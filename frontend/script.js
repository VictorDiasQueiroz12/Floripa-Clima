//localiza os elementos do HTML pelo id deles
const formulario = document.getElementById("filtros")
const campoInicio = document.getElementById("inicio")
const campoFim = document.getElementById("fim")
const mensagem = document.getElementById("mensagem")
const tabela = document.getElementById("registros")
const chuvaTotal = document.getElementById("chuva-total")
const coberturaChuva = document.getElementById("cobertura-chuva")
const temperaturaMaxima = document.getElementById("temperatura-maxima")
const dataMaxima = document.getElementById("data-maxima")
const botaoImportar = document.getElementById("importar")

//localiza o botão dentro do formulario
const botao = formulario.querySelector('button[type="submit"]')

function formatarNumero(valor) {
    if (valor === null) {
        return "Sem dado"
    }

    //"toFixed(1)" transforma coloca uma casa decimal para ele.
    //ex: 27 vira 27.0
    return valor.toFixed(1)
}

const canvasTemperaturas = document.getElementById("grafico-temperaturas")

//vai guardar o objeto para podemos remove depois
//começa com "null" porque ainda não existe um grafico
let graficoTemperaturas = null

function desenharGrafico(registros) {
    //cria 3 listas vazias
    const datas = []
    const maximas = []
    const minimas = []

    //cada posição das tres listas correspondem ao mesmo dia
    for (const registro of registros) {
        //divide a data para exibir como DD/MM/AAAA
        const partes = registro.data.split("-")

        datas.push(`${partes[2]}/${partes[1]}/${partes[0]}`)

        //"push" adiciona um elemento ao final da lista
        //valores null continuam ausentes, sem virar 0, porque mantemos os numeros originais
        maximas.push(registro.temperatura_maxima)
        minimas.push(registro.temperatura_minima)
    }

    //"new Chart" cria um grafico usando a biblioteca carregada no HTML
    //os argumentos são o canvas e um objeto com dados e configs
    graficoTemperaturas = new Chart(canvasTemperaturas, {
        //grafico em linhas
        type: "line",
        data: {
            //na horizontal
            labels: datas,
            //cada dataset representa uma serie de valores
            //tem uma linha para maxima e para minima
            datasets: [
                {
                    label: "Máxima (°C)",
                    data: maximas,
                    borderColor: "#dc2626",
                    backgroundColor: "#dc2626",
                    //tamanho dos pontos de cada dia
                    pointRadius: 3,
                    //usa segmentos retos entre os pontos
                    tension: 0,
                    //interrompe a linha quando houver um dado ausente
                    spanGaps: false,
                },
                {
                    label: "Mínima (°C)",
                    data: minimas,
                    borderColor: "#0369a1",
                    backgroundColor: "#0369a1",
                    pointRadius: 3,
                    tension: 0,
                    spanGaps: false,
                }
            ]
        },
        options: {
            //ajusta o grafico ao tamanho do espaço disponivel
            responsive: true,
            //permite usar a altura definida em ".area-grafico"
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: "Temperatura (°C)",
                    },
                },
                x: {
                    title: {
                        display: true,
                        text: "Data",
                    },
                },
            },
        }
    })
}

//"async" permite usar "await" dentro da função
formulario.addEventListener("submit", async function (evento) {
    //evita que o formulario recarregue a pagina
    evento.preventDefault()
    //remove as linhas da consulta anterior
    tabela.replaceChildren()

    //remove o grafico anterior para não mostrar outro periodo
    if (graficoTemperaturas !== null) {
        //libera o canvas para receber um novo grafico, "destroy()" remove o grafico
        graficoTemperaturas.destroy()
        //indica que não existe mais um grafico ativo
        graficoTemperaturas = null
    }

    //limpa o indicador para não mostrar valores da consulta anterior
    chuvaTotal.textContent = "—"
    coberturaChuva.textContent = "Sem resultado para esta consulta."

    //limpa o cartão para não manter resultados da consulta anterior
    temperaturaMaxima.textContent = "—"
    dataMaxima.textContent = "Sem resultado para esta consulta."

    //".value" recupera o valor preenchido no campo
    const inicio = campoInicio.value
    const fim = campoFim.value

    if (inicio > fim) {
        mensagem.textContent =
            "A data inicial deve ser anterior ou igual à final."
        //encerra esta execução da função, sem consultar a API
        return
    }

    mensagem.textContent = "Carregando dados..."

    //evita novos envios enquanto a consulta esta sendo feita
    botao.disabled = true
    botaoImportar.disabled = true

    try {
        //"URLSearchParams" organiza os parametros de uma URL
        const parametros = new URLSearchParams({
            inicio: inicio,
            fim: fim,
        })

        //"fetch" faz uma requisição HTTP
        //como a pagina e a API estão no mesmo endereço basta informar o caminho "/clima"
        //"await" aguarda a resposta antes de continuar esta função
        const resposta = await fetch(`/clima?${parametros}`)

        //converte o JSON recebido em um objeto
        const dados = await resposta.json()

        //se a resposta não for "ok" o "throw" interrompe a execução e mostra o erro
        if (!resposta.ok) {
            throw new Error(
                dados.detail || "Não foi possível consultar os dados."
            )
        }

        //uma consulta valida também pode não encontrar registros
        if (dados.total === 0) {
            mensagem.textContent =
                "Nenhum registro encontrado nesse período."
            //encerra a função, mas o finally ainda sera executado
            return
        }

        //"let" deixa alterar o valor da variavel durante a soma
        let acumulado = 0
        let diasComChuvaDisponivel = 0

        for (const registro of dados.registros) {
            //inclui 0 na soma, mas ignora dados ausentes
            if (registro.precipitacao !== null) {
                acumulado += registro.precipitacao
                diasComChuvaDisponivel += 1
            }
        }

        if (diasComChuvaDisponivel > 0) {
            chuvaTotal.textContent = `${formatarNumero(acumulado)} mm`

            //informa quantos registros possuem dados de precipitação
            //se houver dados ausentes, a soma representa apenas os disponiveis
            coberturaChuva.textContent =
                `Dados disponíveis em ${diasComChuvaDisponivel} de ${dados.total} registros.`
        } else {
            chuvaTotal.textContent = "Sem dado"
            coberturaChuva.textContent =
                "Não há valores de precipitação disponíveis."
        }

        //"null" fala que ainda não encontramos uma temperatura valida
        let diaMaisQuente = null

        for (const registro of dados.registros) {
            //ignora dias sem informações de temperatura maxima
            if (registro.temperatura_maxima !== null) {
                //o primeiro dia mais quente vira referencia
                if (diaMaisQuente === null) {
                    diaMaisQuente = registro

                //nos proximos registros compara a maxima com a referencia
                //se tiver uma maior guarda o registro inteiro
                //assim mantem tanto a temperatura quanto sua data
                } else if (
                    registro.temperatura_maxima > diaMaisQuente.temperatura_maxima
                ) {
                    diaMaisQuente = registro
                }
            }
        }

        if (diaMaisQuente !== null) {
            //reutiliza a função que exibe uma casa decimal
            temperaturaMaxima.textContent =
                `${formatarNumero(diaMaisQuente.temperatura_maxima)} °C`

            //a API envia data no formato AAAA-MM-DD
            //"split("-")" separa o texto em uma lista
            //ex: ["2025", "01", "03"]
            const partesData = diaMaisQuente.data.split("-")

            //as posições começam em 0
            //[0] é o ano, [1] mes e [2] dia
            dataMaxima.textContent =
                `Registrada em ${partesData[2]}/${partesData[1]}/${partesData[0]}.`
        } else {
            //pode haver registros, mas nenhuma temperatura disponivel
            temperaturaMaxima.textContent = "Sem dado"
            dataMaxima.textContent =
                "Não há temperaturas máximas disponíveis."
        }

        //percorre os elementos de uma lista
        //a cada repetição, "registro" contem os dados de um dia
        for (const registro of dados.registros) {
            //cria uma linha na tabela \<tr>
            const linha = document.createElement("tr")

            //cria uma lista que a ordem corresponde as quatro colunas do nosso HTML
            const valores = [
                registro.data,
                formatarNumero(registro.temperatura_maxima),
                formatarNumero(registro.temperatura_minima),
                formatarNumero(registro.precipitacao),
            ]

            //percorre os quatro valores para criar as celulas
            for (const valor of valores) {
                //cria uma celula \<td>
                const celula = document.createElement("td")
                //insere o valor como texto, sem o navegador interpretar como HTML
                celula.textContent = valor
                //adiciona a linha ao corpo da tabela
                linha.appendChild(celula)
            }

            //adiciona a linha completa ao "\<tbody id="registros">"
            tabela.appendChild(linha)
        }

        //usa os mesmos registros dos cartoes e tabela
        desenharGrafico(dados.registros)

        //exibe a quantidade de registros retornada pela API
        mensagem.textContent = `${dados.total} registros encontrados.`

    } catch (erro) {
        //recebe falhas de conexão, erros ao interpretar o JSON e erros lançados com throw dentro do try
        //"message" contem a descrição do erro
        mensagem.textContent = `Erro: ${erro.message}`
    } finally {
        //executa ao terminar o try/catch, e tambem um return dentro do try
        //reativa o botão para permitir outra consulta
        botao.disabled = false
        botaoImportar.disabled = false
    }
});


botaoImportar.addEventListener("click", async function () {
    //verifica os campos obrigatorios do formulario, se faltar uma data o navegador mostra a indicação no campo
    if (!formulario.reportValidity()) {
        //encerra a funçao sem fazer requisição
        return
    }

    //recupera as datas preenchidas nos inputs
    const inicio = campoInicio.value
    const fim = campoFim.value

    if (inicio > fim) {
        mensagem.textContent = "A data inicial deve ser anterior ou igual à final."
        return
    }

    mensagem.textContent = "Importando dados do Open-Meteo..."

    //desativa os dois botões enquanto o ETL está em andamento
    botaoImportar.disabled = true
    botao.disabled = true

    try {
        const parametros = new URLSearchParams({
            inicio: inicio,
            fim: fim,
        })

        //nessa rota precisa informar o metodo POST
        //o periodo continua sendo enviado nos parametros da URL
        const resposta = await fetch(`/importar?${parametros}`, {
            method: "POST",
        })

        const dados = await resposta.json()

        if (!resposta.ok) {
            throw new Error(
                dados.detail || "Não foi possível importar os dados."
            )
        }

        mensagem.textContent = `Importação concluída: ${dados.registros_processados} registros processados. Clique em Consultar para atualizar o painel.`

    } catch (erro) {
        mensagem.textContent = `Erro: ${erro.message}`

    } finally {
        botaoImportar.disabled = false
        botao.disabled = false
    }
});