from fastapi import FastAPI, HTTPException #importa a classe usada para criar a aplicação | "HTTPException" permite devolver uma resposta HTTP de erro
import os #acessar infos carregadas no ".env"
from pathlib import Path #ajuda a localizar o ".env"
import psycopg #conecxão com postgreSQL
from psycopg.rows import dict_row #faz cada linha consultada virar um dicionario, com os nomes das colunas chaves
from dotenv import load_dotenv #carrega as configs do ".env"

pasta_projeto = Path(__file__).resolve().parent
load_dotenv(pasta_projeto / ".env")


#cria a aplicação e guarda na variavel "app"
#titulo aparece automatico na documentação
app = FastAPI(title="Floripa Clima")


#get é usado para consultar informações
@app.get("/saude")
#"def"define uma função
def verificar_saude():
    return{
        "status": "ok",
        "mensagem": "API do Floripa Clima funcionando",
    }

#ROTA GET /CLIMA
@app.get("/clima")
def listar_clima():
    try:
        #abre conecxão usando as mesmas configs que foi usada na importação dos dados
        #"row_factory=dict_row" faz os resultados serem dicionarios
        #ex: {"data": ..., "temperatura_maxima": ...}
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
                #seleciona os campos para ser devolvidos
                #"ORDER BY" organiza os resultados por data

                #"AS" da um nome ao resultado da subtração: calcula a amplitude sem armazenar ela na tabela
                cursor.execute("""
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
                    ORDER BY data;
                """)
                #"fetchall()" recupera todas as linhas da consulta e guarda em uma lista
                registros = cursor.fetchall()

        #a conexão ja esta fechada aqui
        #o FastAPI converte o dicionario e seus registros em json
        return{
            "total": len(registros),
            "registros": registros,
        }
    except psycopg.Error as erro:
        #mostra detalhes no terminal para ajudar no diagnostico
        print(f"Erro ao consultar o banco: {erro}")

        #devolve uma respota de erro ao cliente
        #"503" significa que o serviço esta indisponivel
        #os detalhes internos do banco ficam no terminal
        raise HTTPException(
            status_code=503,
            datail="Não foi possível consultar os dados metereológicos."
        ) from erro