from fastapi import FastAPI, HTTPException  #importa a classe usada para criar a aplicação | HTTPException permite devolver uma resposta HTTP de erro
import os  #acessa informações carregadas no ".env"
from pathlib import Path  #ajuda a localizar o ".env"
import psycopg  #conexão com PostgreSQL
from psycopg.rows import dict_row  #faz cada linha consultada virar um dicionario, com os nomes das colunas como chaves
from dotenv import load_dotenv  #carrega as configurações do ".env"
from datetime import date  #representa datas sem horários
from fastapi.responses import FileResponse #permite devolver um arquivo como resposta de uma rota
from fastapi.staticfiles import StaticFiles #permite servir arquivos estaticos como JS e CSS
import requests #permite tratar falhas ao consultar o Open-Meteo
from .main import extrair_dados, transformar_dados
from .carregar_dados import salvar_registros

#o primeiro "parent" chega na pasta backend e o segundo chega na raiz
pasta_projeto = Path(__file__).resolve().parent.parent
load_dotenv(pasta_projeto / ".env")


#cria a aplicação e guarda na variável "app"
#o titulo aparece automaticamente na documentação
app = FastAPI(title="Floripa Clima")

#liga o endereço "/static" a pasta frontend
#uma requisição para "/static/script.js" entrega frontend/script.js
app.mount(
    "/static",
    StaticFiles(directory=pasta_projeto / "frontend"),
    name="static",
)

#"GET" é usado para consultar informações
@app.get("/saude")
#"def" define uma função
def verificar_saude():
    return {
        "status": "ok",
        "mensagem": "API do Floripa Clima funcionando",
    }


#ROTA GET /CLIMA
@app.get("/clima")
def listar_clima(
    #esses parametros são recebidos pela URL
    #"date" informa que espera uma data válida
    #"| None" permite que o parâmetro fique ausente
    #"= None" define o valor padrão quando ele não é informado
    inicio: date | None = None,
    fim: date | None = None,
):
    #se as duas datas foram informadas, verifica sua ordem
    if inicio is not None and fim is not None:
        if inicio > fim:
            #"400" indica que a solicitação contém um problema
            raise HTTPException(
                status_code=400,
                detail="A data inicial deve ser anterior ou igual à final.",
            )

    #começamos com a consulta sem filtros
    #"WHERE TRUE" permite acrescentar condições usando "AND"
    consulta = """
        SELECT
            data,
            localidade,
            fonte,
            temperatura_maxima,
            temperatura_minima,
            precipitacao,
            temperatura_maxima - temperatura_minima
                AS amplitude_termica
        FROM public.weather_daily
        WHERE TRUE
    """

    #guarda os valores que serão enviados separadamente do SQL
    valores = []

    if inicio is not None:
        #"+=" acrescenta texto ao final da consulta
        #">=" inclui também o próprio dia inicial
        #"%s" reserva o lugar do parametro
        consulta += " AND data >= %s"

        #acrescenta a data a lista de parametros
        valores.append(inicio)

    if fim is not None:
        #"<=" inclui também o próprio dia final
        consulta += " AND data <= %s"
        valores.append(fim)

    #a ordenação precisa ficar depois das condições
    consulta += " ORDER BY data;"

    try:
        #abre conexão usando as mesmas configurações utilizadas na importação dos dados
        #"row_factory=dict_row" faz os resultados serem dicionários
        #exemplo: {"data": ..., "temperatura_maxima": ...}
        with psycopg.connect(
            host="127.0.0.1",
            port=5433,
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            connect_timeout=10,
            row_factory=dict_row,
        ) as conexao:

            #abre o cursor para executar a consulta SQL
            with conexao.cursor() as cursor:

                #os valores são associados aos espaços reservados %s
                #as datas não foram colocadas diretamente no texto SQL
                cursor.execute(consulta, valores)

                #"fetchall()" recupera todas as linhas da consulta e guarda em uma lista
                registros = cursor.fetchall()

        #a conexão já está fechada aqui
        #o FastAPI converte o dicionário e seus registros em JSON
        return {
            "total": len(registros),
            "registros": registros,
        }

    except psycopg.Error as erro:
        #mostra detalhes no terminal para ajudar no diagnóstico
        print(f"Erro ao consultar o banco: {erro}")

        #devolve uma resposta de erro ao cliente
        #"503" significa que o serviço está indisponível
        #os detalhes internos do banco ficam no terminal
        raise HTTPException(
            status_code=503,
            detail="Não foi possível consultar os dados meteorológicos.",
        ) from erro


#a rota "("/")" representa a pagina inicial da aplicação
@app.get("/", response_class=FileResponse)
def pagina():
    #localiza o HTML dentro da pasta frontend
    caminho_html = pasta_projeto / "frontend" / "index.html"
    #envia o arquivo para o navegador, que interpreta o HTML
    return FileResponse(caminho_html)

#POST é usado porque esta operaçao grava dados no banco
@app.post("/importar")
def importar_clima(inicio: date, fim: date):
    #as duas datas são obrigatorias, sao recebidas como parametros da URL
    if inicio > fim:
        raise HTTPException(
            status_code=400,
            detail="A data inicial deve ser maior ou igual à final."
        )
    if fim >= date.today():
        raise HTTPException(
            status_code=400,
            detail="Escolha uma data final anterior ao dia de hoje."
        )
    #subtrai duas datas da um intervalo
    #".days" recupera a quantidade de dias desse intervalo
    #"+ 1" soma, porque inclui as duas datas na importação
    quantidade_dias = (fim - inicio).days + 1

    if quantidade_dias > 366:
        raise HTTPException(
            status_code=400,
            detail="Importe no máximo 366 dias por execução."
        )

    try:
        #EXTRAÇÃO
        #"isoformat()" transforma date em texto no formato AAAA-MM-DD
        dados = extrair_dados(
            inicio.isoformat(),
            fim.isoformat(),
        )

        #TRANSFORMAÇÃO
        #converte as listas da API em registros por dia
        registros = transformar_dados(dados)

        #CARREGAR
        #salva no PostgreSQL e atualiza dias que ja existem
        quantidade = salvar_registros(registros)

        #so anuncia o sucesso depois da confirmação no banco
        return{
            "mensagem": "importação concluída.",
            "inicio": inicio,
            "fim": fim,
            "registros_processados": quantidade,
        }

    except requests.exceptions.RequestException as erro:
        print(f"Erro ao consultar o Open-Meteo: {erro}")

        raise HTTPException(
            status_code=502,
            detail="Não foi possivel obter os dados do Open-Meteo.",
        ) from erro

    except (KeyError, IndexError, TypeError, ValueError) as erro:
        print(f"Erro ao transformar os dados: {erro}")

        raise HTTPException(
            status_code=502,
            detail="Os dados recebidos não puderam ser processados.",
        ) from erro

    except psycopg.Error as erro:
        print(f"Erro ao salvar no banco: {erro}")

        raise HTTPException(
            status_code=503,
            detail="Não foi possível salvar os dados no banco.",
        ) from erro