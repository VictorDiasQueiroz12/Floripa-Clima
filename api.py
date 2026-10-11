from fastapi import FastAPI, HTTPException  #importa a classe usada para criar a aplicação | HTTPException permite devolver uma resposta HTTP de erro
import os  #acessa informações carregadas no ".env"
from pathlib import Path  #ajuda a localizar o ".env"
import psycopg  #conexão com PostgreSQL
from psycopg.rows import dict_row  #faz cada linha consultada virar um dicionario, com os nomes das colunas como chaves
from dotenv import load_dotenv  #carrega as configurações do ".env"
from datetime import date  #representa datas sem horários

pasta_projeto = Path(__file__).resolve().parent
load_dotenv(pasta_projeto / ".env")


#cria a aplicação e guarda na variável "app"
#o titulo aparece automaticamente na documentação
app = FastAPI(title="Floripa Clima")


#"GET" é usado para consultar informações
@app.get("/saude")
#"def" define uma função
def verificar_saude():
    return {
        "status": "ok",
        "mensagem": "API do Floripa Clima funcionando",
    }


# ROTA GET /CLIMA.
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