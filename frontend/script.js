//localiza os elementos do HTML pelo id deles
const formulario = document.getElementById("filtros")
const campoInicio = document.getElementById("inicio")
const campoFim = document.getElementById("fim")
const mensagem = document.getElementById("mensagem")
const tabela = document.getElementById("registros")
const chuvaTotal = document.getElementById("chuva-total")
const coberturaChuva = document.getElementById("cobertura-chuva")

//localiza o botão dentro do formulario
const botao = formulario.querySelector('button[type="submit"]')

function formatarNumero(valor){
    if (valor === null){
        return "Sem dado"
    }

    //"toFixed(1)" transforma coloca uma casa decimal para ele.
    //ex: 27 vira 27.0
    return valor.toFixed(1)
}

//"async" permite usar "await" dentro da função
formulario.addEventListener("submit", async function (evento) {
    //evita que o formulario recarregue a pagina
    evento.preventDefault()
    //remove as linhas da consulta anterior
    tabela.replaceChildren()

    //limpa o indicador para não mostrar valores da consulta anterior
    chuvaTotal.textContent = "—"
    coberturaChuva.textContent = "Sem resultado para esta consulta."

    //".value" recupera o valor preenchido no campo
    const inicio = campoInicio.value
    const fim = campoFim.value

    if(inicio > fim){
        mensagem.textContent = 
        "A data inicial deve ser anterior ou igual à final."
        //encerra esta execução da função, sem consultar a API
        return
    }

    mensagem.textContent = "Carregando dados..."

    //evita novos envios enquanto a consulta esta sendo feita
    botao.disabled = true

    try{
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
        if(!resposta.ok){
            throw new Error(
                dados.detail || "Não foi possível consultar os dados."
            )
        }

        //uma consulta valida também pode não encontrar registros
        if(dados.total === 0){
            mensagem.textContent = 
            "Nenhum registro encontrado nesse período."
            //encerra a função, mas o finally ainda sera executado
            return
        }

        //"let" deixa alterar o valor da variavel durante a soma
        let acumulado = 0
        let diasComChuvaDisponivel = 0

        for(const registro of dados.registros){
            //inclui 0 na soma, mas ignora dados ausentes
            if(registro.precipitacao !== null){
                acumulado += registro.precipitacao
                diasComChuvaDisponivel += 1
            }
        }
        if(diasComChuvaDisponivel > 0){
            chuvaTotal.textContent = `${formatarNumero(acumulado)} mm`

            //informa quantos registros possuem dados de precipitação
            //se houver dados ausentes, a soma representa apenas os disponiveis
            coberturaChuva.textContent = `Dados disponíveis em ${diasComChuvaDisponivel} de ${dados.total} registros.`
        } else{
            chuvaTotal.textContent = "Sem dado"
            coberturaChuva.textContent = "Não há valores de precipitação disponíveis."
        }
        //percorre os elementos de uma lista
        //a cada repetição, "registro" contem os dados de um dia
        for(const registro of dados.registros){
            //cria uma linha na tabela <tr>
            const linha = document.createElement("tr")

            //cria uma lista que a ordem corresponde as quatro colunas do nosso HTML
            const valores = [
                registro.data,
                formatarNumero(registro.temperatura_maxima),
                formatarNumero(registro.temperatura_minima),
                formatarNumero(registro.precipitacao),
            ]

            //percorre os quatro valores para criar as celulas
            for(const valor of valores){
                //cria uma celula <td>
                const celula = document.createElement("td")
                //insere o valor como texto, sem o navegador interpretar como HTML
                celula.textContent = valor
                //adiciona a linha ao corpo da tabela
                linha.appendChild(celula)
            }
            //adiciona a linha completa ao "<tbody id="registros">"
            tabela.appendChild(linha)
        
        } 
        //exibe a quantidade de registros retornada pela API
        mensagem.textContent = `${dados.total} registros encontrados.`

    }catch (erro){
        //recebe falhas de conexão, erros ao interpretar o JSON e erros lançados com throw dentro do try
        //"message" contem a descrição do erro
        mensagem.textContent = `Erro: ${erro.message}`
    } finally{
    //executa ao terminar o try/catch, e tambem um return dentro do try
    //reativa o botão para permitir outra consulta
    botao.disabled = false
}
});