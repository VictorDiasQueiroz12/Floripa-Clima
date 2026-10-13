# Floripa Clima

Dashboard meteorológico de Florianópolis com um processo ETL executado pelo site. A aplicação consulta dados públicos do Open-Meteo, organiza os registros diários, salva no PostgreSQL e apresenta filtros, indicadores, tabela e gráfico.

Projeto desenvolvido para aprender na prática a integração entre Python, APIs, SQL, Docker e desenvolvimento web.

## Funcionalidades

- Importação de dados históricos por intervalo de datas.
- ETL iniciado pelo botão **Importar dados**.
- Consulta dos registros armazenados por período.
- Indicador de precipitação acumulada com cobertura dos dados disponíveis.
- Indicador de maior temperatura máxima e sua data.
- Gráfico de temperaturas máximas e mínimas por dia.
- Tabela dos registros consultados.
- Atualização de registros existentes sem duplicar a mesma localidade, fonte e data.
- Validação de datas e tratamento de falhas da API externa e do banco.
- Documentação interativa das rotas em `/docs`.

## Imagens da aplicação

### Dashboard com dados consultados

Consulta de 01/01/2025 a 04/01/2025, com indicadores, gráfico de temperaturas e tabela diária.

![Dashboard do Floripa Clima com quatro registros, indicadores, gráfico e tabela](docs/dashboard.png)

### Página antes da consulta

Tela inicial com os filtros e os botões de consulta e importação, antes de carregar os registros.

![Página inicial do Floripa Clima antes de consultar os dados](docs/tela-inicial.png)

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python | Extração, transformação, carga e backend |
| FastAPI | Rotas HTTP e documentação interativa |
| Uvicorn | Execução do servidor da aplicação |
| Requests | Consulta à API do Open-Meteo |
| Psycopg | Comunicação com o PostgreSQL |
| python-dotenv | Leitura das configurações do `.env` |
| PostgreSQL | Armazenamento dos registros meteorológicos |
| Docker Compose | Execução do PostgreSQL com volume persistente |
| HTML e CSS | Estrutura e apresentação do dashboard |
| JavaScript | Requisições, filtros e atualização da interface |
| Chart.js | Gráfico de temperaturas |

O PostgreSQL roda em um container. Nesta versão, o backend Python é executado no computador e serve também os arquivos do frontend.

## Como o ETL funciona

1. **Extração:** `extrair_dados(inicio, fim)` consulta o Open-Meteo para um ponto representativo do centro de Florianópolis.
2. **Transformação:** `transformar_dados(dados)` combina as listas recebidas em registros por dia e calcula a amplitude térmica quando existem as duas temperaturas.
3. **Carga:** `salvar_registros(registros)` grava no PostgreSQL. O `ON CONFLICT` atualiza os dados caso a combinação de localidade, fonte e data já exista.

O botão **Importar dados** chama `POST /importar`, que aguarda o término do ETL antes de responder. O botão **Consultar** chama `GET /clima` e atualiza os indicadores, a tabela e o gráfico.

O fluxo do site passa diretamente da API externa para o banco, sem depender do JSON local. Os scripts de terminal continuam permitindo salvar e analisar um arquivo JSON.

## Organização dos arquivos

| Caminho | Responsabilidade |
|---|---|
| `api.py` | Rotas de consulta, importação e entrega do frontend |
| `main.py` | Funções de extração e transformação; coleta pelo terminal |
| `carregar_dados.py` | Função de carga; importação do JSON pelo terminal |
| `analise.py` | Leitura e análise do JSON pelo terminal |
| `schema.sql` | Criação da tabela e suas restrições |
| `compose.yaml` | Configuração do PostgreSQL no Docker |
| `requirements.txt` | Dependências Python com versões |
| `.env` | Credenciais locais; não deve ser enviado ao GitHub |
| `.gitignore` | Arquivos e pastas ignorados pelo Git |
| `frontend/index.html` | Estrutura da página |
| `frontend/style.css` | Estilos da página |
| `frontend/script.js` | Interação com a API e construção do gráfico |
| `dados/clima_florianopolis.json` | Arquivo gerado pela coleta de terminal |
| `docs/images/` | Prints usados neste README |

## Pré-requisitos

- Python 3.10 ou superior, devido à sintaxe `date | None`.
- Docker Desktop funcionando com containers Linux e Docker Compose.
- Git, se for clonar pelo terminal.
- Internet para baixar dependências, consultar o Open-Meteo e carregar o Chart.js pelo CDN.
- pgAdmin 4, opcional, para visualizar e administrar o banco.

As instruções a seguir usam o PowerShell no Windows. As versões das bibliotecas estão registradas em `requirements.txt`.

## Instalação e primeira execução

### 1. Obter o projeto

Na página deste repositório, clique em **Code** e copie a URL HTTPS. Execute `git clone` seguido dessa URL e entre na pasta criada:

```powershell
git clone <URL-HTTPS-DESTE-REPOSITORIO>
cd floripa-clima
```

Substitua `<URL-HTTPS-DESTE-REPOSITORIO>` pela URL real, sem os sinais `<` e `>`. Também é possível baixar o ZIP pelo GitHub e abrir a pasta extraída no VS Code.

### 2. Criar o ambiente virtual e instalar as dependências

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos usam diretamente o Python da `.venv`; sua ativação no PowerShell não é obrigatória.

### 3. Configurar o `.env`

Crie um arquivo chamado `.env` na pasta principal e copie este exemplo:

```dotenv
POSTGRES_USER=floripa
POSTGRES_PASSWORD=troque_por_uma_senha_local
POSTGRES_DB=floripa_clima
```

Escolha uma senha local antes de iniciar o banco. O Docker e o Python leem essas mesmas configurações.

O `.gitignore` deve conter:

```gitignore
.venv/
__pycache__/
.env
```

O exemplo das variáveis fica neste README; não é necessário um `.env.example` separado.

### 4. Iniciar o PostgreSQL

Abra o Docker Desktop e aguarde sua inicialização. Na pasta do projeto, execute:

```powershell
docker compose up -d
docker compose ps
```

O serviço `db` deve aparecer como `Up`. Confira os logs, se necessário:

```powershell
docker compose logs db
```

Espere a mensagem `database system is ready to accept connections`.

O PostgreSQL é acessado pelo computador em `127.0.0.1:5433`. Dentro do container, ele usa a porta `5432`. O volume `postgres_data` mantém os arquivos do banco entre recriações do container.

### 5. Criar a tabela

A configuração atual não executa `schema.sql` automaticamente. Faça isso na primeira instalação.

Pelo terminal PowerShell, envie o arquivo para o PostgreSQL:

```powershell
Get-Content -Raw -Encoding UTF8 .\schema.sql | docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Como alternativa, conecte pelo pgAdmin:

| Campo | Valor |
|---|---|
| Name | Floripa Clima Local |
| Host name/address | `127.0.0.1` |
| Port | `5433` |
| Maintenance database | Valor de `POSTGRES_DB` |
| Username | Valor de `POSTGRES_USER` |
| Password | Senha definida em `POSTGRES_PASSWORD` |

Abra o **Query Tool** do banco, cole todo o conteúdo de `schema.sql` e execute. Confira:

```sql
SELECT * FROM public.weather_daily;
```

A tabela estará vazia até a primeira importação.

### 6. Iniciar a aplicação

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

Mantenha o terminal aberto. Quando aparecer `Application startup complete`, acesse:

| Endereço | Uso |
|---|---|
| [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Dashboard |
| [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Documentação e testes das rotas |
| [http://127.0.0.1:8000/saude](http://127.0.0.1:8000/saude) | Verificação de resposta da API |
| [http://127.0.0.1:8000/clima](http://127.0.0.1:8000/clima) | Registros armazenados |

## Usando o dashboard

1. Selecione as datas inicial e final, por exemplo **01/01/2025 a 10/01/2025**.
2. Clique em **Importar dados** e aguarde a mensagem de conclusão.
3. Clique em **Consultar** para exibir o período na tabela, nos cartões e no gráfico.
4. Altere o período e consulte novamente para explorar os dados já armazenados.

A importação não atualiza automaticamente o painel. Durante o ETL, ele mantém a consulta anterior. Um período ainda não importado pode retornar zero registros.

## Rotas

| Método | Rota | Função |
|---|---|---|
| GET | `/` | Entrega a página HTML |
| GET | `/saude` | Indica que a API está respondendo; não testa o banco |
| GET | `/clima` | Consulta os registros; aceita `inicio` e `fim` opcionais |
| POST | `/importar` | Executa o ETL; exige `inicio` e `fim` |
| GET | `/docs` | Documentação interativa |
| GET | `/static/...` | Entrega os arquivos da pasta `frontend` |

Exemplo de consulta:

```text
http://127.0.0.1:8000/clima?inicio=2025-01-03&fim=2025-01-07
```

Para testar a importação, use `POST /importar` em `/docs`. Abrir a URL na barra do navegador envia GET e não executa a importação.

### Validações da importação

- Data inicial anterior ou igual à final.
- Data final anterior ao dia atual do ambiente do servidor.
- Máximo de 366 dias por execução.
- Validação de formato de data pelo FastAPI.

Datas históricas muito recentes podem ainda não estar disponíveis na fonte.

## Modelo de dados e indicadores

A tabela `weather_daily` armazena identificador, localidade, fonte, data, temperaturas máxima e mínima, precipitação e instante de criação.

| Regra | Comportamento |
|---|---|
| Chave única | Uma linha por localidade, fonte e data |
| Valores ausentes | Permanecem `NULL` no banco e `null` no JSON |
| Precipitação | Não permite valores negativos |
| Temperaturas | Quando ambas existem, máxima não pode ser menor que mínima |
| Reimportação | Atualiza os valores existentes com `ON CONFLICT` |

A amplitude térmica é calculada como **máxima − mínima**. A consulta do banco calcula esse campo sem armazená-lo na tabela.

O cartão de precipitação soma apenas valores disponíveis e informa sua cobertura entre os registros retornados. Essa contagem não garante que todos os dias do intervalo solicitado estejam armazenados. O gráfico mantém valores ausentes como lacunas.

Em caso de empate na maior máxima, o painel mantém o primeiro registro encontrado, que é o mais antigo na ordenação por data.

## Scripts de terminal

```powershell
# Consulta o período definido em executar_coleta() e salva o JSON.
.\.venv\Scripts\python.exe .\main.py

# Analisa os registros do JSON local.
.\.venv\Scripts\python.exe .\analise.py

# Importa o JSON local para o PostgreSQL.
.\.venv\Scripts\python.exe .\carregar_dados.py
```

O JSON é substituído a cada coleta pelo terminal. Ele não é atualizado pela importação iniciada no site; por isso, `analise.py` pode analisar um período diferente do painel.

## Reiniciar e encerrar

Depois de fechar tudo, abra o Docker Desktop e execute na pasta do projeto:

```powershell
docker compose up -d
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

Não é necessário recriar a tabela ou importar os dados novamente enquanto o volume persistente existir.

Para encerrar a API, pressione **Ctrl + C** no terminal. Para parar o banco:

```powershell
docker compose stop
```

Esse comando preserva os dados. `docker compose down -v` remove os volumes e pode apagar o banco; não é o comando de encerramento comum do projeto.

As variáveis de inicialização do PostgreSQL são aplicadas quando o volume está vazio. Alterar a senha no `.env` não altera automaticamente a senha de um banco já existente.

## Verificações manuais

| Teste | Resultado esperado |
|---|---|
| Importar 01/01 a 10/01/2025 e consultar | Dez registros nesse intervalo |
| Reimportar o mesmo período | Quantidade de linhas permanece igual |
| Consultar 03/01 a 07/01/2025 | Cinco registros e 3,4 mm acumulados |
| Consultar 01/01 a 10/01/2025 | 13,6 mm e maior máxima de 34,3 °C em 03/01/2025, conforme os dados usados no desenvolvimento |
| Consultar com datas invertidas | Mensagem de validação |
| Consultar período sem registros armazenados | Mensagem de nenhum registro encontrado |
| Trocar o período após uma consulta | Tabela, cartões e gráfico acompanham o filtro |

Os exemplos numéricos refletem a resposta da fonte usada no desenvolvimento e podem mudar se ela revisar os dados.

## Solução de problemas

| Problema | O que conferir |
|---|---|
| Docker não conecta | Docker Desktop aberto e inicializado |
| `relation weather_daily does not exist` | Executar `schema.sql` no banco correto |
| Consulta retorna 503 | Banco ativo, credenciais e mensagem detalhada no terminal |
| `0 placeholders but 2 parameters` | Usar `%s`, não `$s`, nas condições do SQL |
| Página inicial retorna 404 | Rota `/` definida fora das demais funções |
| CSS ou JavaScript retorna 404 | Configuração de `/static` e nomes dos arquivos |
| Gráfico não aparece | CDN acessível, Chart.js antes de `script.js` e id `grafico-temperaturas` |
| Alterações não aparecem | Salvar os arquivos e atualizar com Ctrl + F5 |
| Importação retorna 502 | Falha da fonte externa, período indisponível ou resposta inesperada; verificar terminal |

## Fonte e limitações

Fonte: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

Localização consultada: latitude **-27.5954**, longitude **-48.5480**. Fuso solicitado: **America/Sao_Paulo**.

Os dados históricos são de **reanálise**, combinando modelos meteorológicos e observações. Não devem ser apresentados como medições diretas de uma estação instalada nesse ponto ou como valores específicos para cada bairro da cidade.

Dados disponibilizados pelo Open-Meteo sob [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Consulte também os [termos do serviço](https://open-meteo.com/en/terms) para uso da API. A licença dos dados não define a licença do código deste repositório.

A aplicação atual é voltada ao uso local e educacional. Não possui autenticação, agendamento de importações, fila de tarefas ou histórico persistente de execuções do ETL. A consulta sem filtros retorna todos os registros e ainda não possui paginação.

## Próximas melhorias

- Histórico de execuções do ETL com status e quantidade de registros.
- Gráfico diário de precipitação.
- Exportação de dados em CSV.
- Validação da cobertura de todos os dias do intervalo solicitado.
- Backend também executado pelo Docker Compose.
- Testes automatizados de transformação e importação.

## Autor

Desenvolvido por **Victor Dias Queiroz** como projeto de aprendizagem em programação, integração de sistemas e análise de dados.
