import json

import psycopg  #permite conectar ao PostgreSQL e executar SQL.

import os #permite acessar configuraçoes nas variaveis de ambiente, como o usuario e a senha do banco 

from pathlib import Path

from dotenv import load_dotenv #"load_dotenv" le o arquivo ".env" e disponibiliza suas configuraçoes para serem acessadas com "os.getenv()"

#localiza a pasta onde esse arquivo esta
pasta_projeto = Path(__file__).resolve().parent

#carrega as configuraçoes do .env nas variaveis de ambiente
load_dotenv(pasta_projeto / ".env")

#localiza o json gerado pelo "main.py"
caminho_json = pasta_projeto / "dados" / "clima_florianopolis.json"

#define o comando SQL que sera executado para cada dia 
#"$s" sao espaços reservados para valores

#a biblioteca envia esses valores separadamente do SQL

#"ON CONFLICT" trata a chave unica definida no "schema.sql": localizaçao + fonte + data

#se o dia ja existir, atualizamos os valores em vez de duplicalo
sql = """
    INSERT INTO public.weather_daily (
        localidade,
        fonte,
        data,
        temperatura_maxima,
        temperatura_minima,
        precipitacao
    )
    VALUES (%s, %s, %s, %s, %s, %s)

    ON CONFLICT (localidade, fonte, data)
    DO UPDATE SET
        temperatura_maxima = EXCLUDED.temperatura_maxima,
        temperatura_minima = EXCLUDED.temperatura_minima,
        precipitacao = EXCLUDED.precipitacao;
"""
try:
    #abre o arquivo e recupera a lista de registros
    with caminho_json.open("r", encoding="utf-8") as arquivo:
        registros = json.load(arquivo)

    #conecta ao PostgreSQL executado pelo Docker
    #o Python está no Windows, então usa a porta externa 5433.
    #"os.getenv" busca o valor de uma variável de ambiente.
    with psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        connect_timeout=10,
    ) as conexao:

        #um cursor permite executar comandos SQL pela conexão.
        with conexao.cursor() as cursor:

            for registro in registros:
                #uma tupla reúne os valores na mesma ordem dos %s.
                valores = (
                    "Florianópolis - Centro",
                    "Open-Meteo",
                    registro["data"],
                    registro["temperatura_maxima"],
                    registro["temperatura_minima"],
                    registro["precipitacao"],
                )

                #executa o INSERT com os valores deste dia.
                cursor.execute(sql, valores)

        #ao sair do bloco "with conexao" sem erro, as alterações são confirmadas automaticamente.
        #se ocorrer um erro dentro dele, são desfeitas.

    print(f"Importação concluída: {len(registros)} registros processados.")

except FileNotFoundError:
    print("JSON não encontrado. Execute o main.py primeiro.")

except json.JSONDecodeError:
    print("O arquivo contém um JSON inválido.")

except psycopg.Error as erro:
    print(f"Erro ao acessar o PostgreSQL: {erro}")

except OSError as erro:
    print(f"Erro ao ler o arquivo: {erro}")