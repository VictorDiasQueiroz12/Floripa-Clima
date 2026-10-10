import json

#permite acessar configuraçoes nas variaveis de ambiente, como o usuario e a senha do banco 
import os 
from pathlib import Path

#"load_dotenv" le o arquivo ".env" e disponibiliza suas configuraçoes para serem acessadas com "os.getenv()"
from dotenv import load_dotenv

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
