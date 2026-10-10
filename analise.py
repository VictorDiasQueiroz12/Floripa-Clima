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

    #comeca a soma em zero
    chuva_total = 0 

    #conta quantos dias possuem informaçao de precipitacao
    dias_com_dado_chuva = 0

    #ainda não foi escolhido o dia com maior temperatura
    dias_mais_quente = None

    for registro in registros:
        #recupera os valores do dia que estamos analisando
        chuva = registro["precipitacao"]
        maxima = registro["temperatura_maxima"]

        #zero pode ser valido aqui, indicando que não houve precipitacao
        #"None" siginifica dado ausente, por isso nao entra na soma
        if chuva is not None:
            #"+=" soma o valor a variavel. 
            #ex: chuva_total = chuva_total + chuva
            chuva_total += chuva
            dias_com_dado_chuva += 1

        #so compara temperaturas disponiveis
        if maxima is not None:
            #o primeiro dia com temperaturas valida vira referencia
            if dias_mais_quente is None:
                dias_mais_quente = registro

            #nos proximos dias, substitui a referencia somente se encontrar uma maxima maior
            elif maxima > dias_mais_quente["temperatura_maxima"]:
                dias_mais_quente = registro

    print()
    print("Análise do período")

    if dias_com_dado_chuva > 0:
        #".1f" exibe um numero depois da virgula
        print(f"Precipitação acumulada disponível: {chuva_total:.1f} mm")

        #mostra a cobertura para nao confundir dados ausentes com dias secos
        print(
            f"Dias com dados de precipitação: "
            f"{dias_com_dado_chuva} de {len(registros)}"
        )
    else:
        print("Não há dados de precipitação disponíveis.")


    if dias_mais_quente is not None:
        print(f"Dias com maior máxima: {dias_mais_quente['data']}")
        print(
            f"Temperatura máxima: "
            f"{dias_mais_quente['temperatura_maxima']} °C"
        )
    else:
        print("Não há temperaturas máximas disponíveis.")


except FileExistsError:
    #acontece quando o arquivo não existe no caminho informado
    print("Arquivo não encontrado. Execute o main.py para gerar os dados.")

except json.JSONDecodeError:
    #acontece quando o conteudo do arquivo não é um json valido
    print("O arquivo contém um JSON inválido.")

except OSError as erro:
    #trata outras falhas de acesso ao arquivo
    print(f"Não foi possível ler o arquivo: {erro}")