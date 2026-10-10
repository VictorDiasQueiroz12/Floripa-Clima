import json
from pathlib import Path

#localiza a pasta onde "analise.py" está
pasta_projeto = Path(__file__).resolve().parent

#monta o caminho para o json salvo pelo "main.py"
caminho_arquivo = pasta_projeto / "dados" / "clima_florianopolis.json"

try:
    #"r" significa que vamos abrir um arquivo existente
    #"with" fecha o arquivo automaticamente ao terminar
    with caminho_arquivo.open("r", encoding="utf-8") as arquivo:
        #"json.load" lê o json e converte o conteudo em uma lista de dicionarios do python
        registros = json.load(arquivo)

    print(f"Registro carregados: {len(registros)}")
    print()

    #percorre os registros lidos do arquivo
    for registro in registros:
        print(
            f"{registro['data']} | "
            f"Máxima: {registro['temperatura_maxima']} °C | "
            f"Chuva: {registro['precipitacao']} mm"
        )

except FileExistsError:
    #acontece quando o arquivo não existe no caminho informado
    print("Arquivo não encontrado. Execute o main.py para gerar os dados.")
