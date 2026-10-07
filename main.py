import requests #biblioteca que faz consultas pela internet

url = "https://archive-api.open-meteo.com/v1/archive"

parametros = { #Dicionario que organiza as informações por nome e valor
    "latitude": -27.5954,
    "longitude": -48.5480,
    "start_date": "2025-01-01",
    "end_date": "2025-01-10",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
    "timezone": "America/Sao_Paulo",
}

#Primeiro vai tentar fazer oque está aqui dentro, caso de errado vai para o except
try:
    #Faz a consulta e diz que o tempo limite de espera é de 30 segundos. 
    resposta = requests.get(url, params=parametros, timeout=30)

    #Gera um erro caso a API responda com uma falha HTTP
    resposta.raise_for_status()

    #Converte o json recebido em estrutura do Python
    dados = resposta.json()

    # print(dados) -> mostraria os dados que estou pegando
    diarios = dados["daily"]

    registros = []

    for indice, data in enumerate(diarios["time"]):
        maxima = diarios["temperature_2m_max"][indice]
        minima = diarios["temperature_2m_min"][indice]
        chuva = diarios["precipitation_sum"][indice]


        #Diz que amplitude tem um valor nulo ou indefinido
        amplitude = None

        #Calcula a amplitude apenas se tiver as duas temperaturas
        if maxima is not None and minima is not None:
            amplitude = round(maxima - minima, 1) #round arredonda o valor e o 1 fala o numero de casas decimais após a virgula

        #Dicionario que tem as informações de um unico dia
        registro = {
            "data": data,
            "temperatura_maxima": maxima,
            "temperatura_minima": minima,
            "precipitacao": chuva,
            "amplitude_termica": amplitude,
        }


        #append adiciona um elemento ao final de uma lista
        #A cada repetição adiciona mais um dia em "registros" que está vazio
        registros.append(registro)



    print("Dados meteorológicos de Florianópolis")

    #o "f" permite passar os valores no texto usando chaves{}
    print(f"Período:{parametros['start_date']}"
      f"a {parametros['end_date']}"
      )

    #o len retorna a quantidade de elementos dentro da lista
    print(f"Total de registros: {len(registros)}")
    print()    #é só uma linha em branco mesmo



    #Percorendo a lista criada
    #Em cada repetição, "registro" representa o dicionario de um dia
    #Logica: Para cada registro dentro de Registros, exiba as infos
    for registro in registros:

        #Pega a info de cada valor registrado e printa ela
        print(f"Data: {registro['data']}")
        print(f"Temperatura máxima: {registro['temperatura_maxima']} °C")
        print(f"Temperatura miníma: {registro['temperatura_minima']} °C")
        print(f"Precipitação: {registro['precipitacao']} mm")
        print(f"Amplitude térmica: {registro['amplitude_termica']} °C")
        print()

#Trata exceções de requisições da biblioteca, como falhas de coneção, erros HTTP e timeout
except requests.exceptions.RequestException as erro: #"as erro": ta guardando a exceção na variavel erro
    print(f"Não foi possível consultar a API: {erro}")

    #.\.venv\Scripts\python.exe main.py