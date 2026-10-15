from logging.config import fileConfig #configura os logs, que são as mensagem de diagnostico exibidas no terminal

from sqlalchemy import create_engine #cria o objeto que gerencia o acesso ao banco
from sqlalchemy import pool #fornence opções de gerenciamento das conexões

from alembic import context #representa o contexto de execução do alembic, ele informa congigurações, modo de execução e conecxão utilizada

import os #permite acessar variaveis de ambiente, como usuario e senha

from pathlib import Path #ajuda a localizar arquivos e pastas

from dotenv import load_dotenv #le os aquivos .env e disponibiliza suas configurações nas variaveis de ambiente

from sqlalchemy.engine import URL #URL permite montar o endereço de conexão usando campos separados

#Recupera a configuração carregada pelo alembic, incluindo as informações do "alembic.ini"
config = context.config

#verifica se um arquivo de configuração foi atualizado
#"is not None" significa que existe um valor disponivel
if config.config_file_name is not None:
    #le as seções de logging do "alembic.ini"
    fileConfig(config.config_file_name)

#para localizar a raiz do projeto
pasta_projeto = Path(__file__).resolve().parents[2]

#carrega a env que ta na raiz do projeto
load_dotenv(pasta_projeto / ".env")

#cria um objeto que representa a conexão com o banco 
#ex: "postgresql+psycopg://usuario:senha@localhost:5433/nome_do_banco"
url_banco = URL.create(
    #tipo de banco + drive usado para conversar com ele
    drivername="postgresql+psycopg",
    #[""] puxa a variavel da env, se não existir gera um KeyError e interrompe a execução
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    #usando "os.getenv" para caso altere o host não quebre o codigo dando um KeyError.
    #se POSTGRES_HOST não existir ele usa o 127.0.0.1
    host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
    #as variaveis de ambiente são textos, e é preciso que seja numeros inteiros no sqlalchemy, por isso usar o int() para converter isso.
    #se POSTGRES_PORT não existir ele usa 5433
    port=int(os.getenv("POSTGRES_PORT", "5433")),
    #nome do banco ao qual vai conectar
    database=os.environ["POSTGRES_DB"]
)

#não defini ainda qual modelos sqlalchemy para gerar a migration automaticamente, ent vai ser manual a primeira 
target_metadata = None

#gera comandos SQL sem conectar ao PostgresSQL
def run_migrations_offline():
    #configura o contexto do alembic para gerar SQL
    context.configure(
        #informa qual banco e drive é utilizado
        url=url_banco,
        #não tem metadata para comparação automatica
        target_metadata=target_metadata,
        #quando da, escreve valores diretamente no SQL gerado em vez de deixar parametros que exigiram um drive
        literal_binds=True,
        #define o estilo de parametros usado na geração do SQL
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

#o alembic aqui abre conexão com o PostgreSQL
def run_migrations_online():
    #"engine" é o objeto que gerencia o acesso ao banco
    engine = create_engine(
        url=url_banco,
        #"NullPool" evita guardar conexões abertar para reutilizar, cada conexão é encerrada ao ser devolvida
        poolclass=pool.NullPool,
        #passa configurações ao drive psycopg e limita a espera para estabelecer conexão a 10 segundos
        connect_args={"connect_timeout": 10},
    )

    #garante que o finnally será executado ao terminar o bloco
    try:
        #abre a conexão e o "with" fecha automaticamente ao sair do bloco
        with engine.connect() as conexao:
            #configura o Alembic para utilizar essa conexão
            context.configure(
                connection=conexao,
                target_metadata=target_metadata,
            )

            #coordena a transação usada pelo Alembic
            with context.begin_transaction():
                #entrega o controle ao comando atual do Alembic
                context.run_migrations()

    finally:
        #libera os recursos associados ao engine, isso não apaga tabelas nem registros
        engine.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
