# Define a imagem que serve de base ao container.
# Ela já contém Python e um sistema Linux reduzido.
FROM python:3.14-slim

# Copia o executável do uv de sua imagem oficial.
# Não precisamos instalar uv com pip.
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv

# Impede a criação de arquivos .pyc.
ENV PYTHONDONTWRITEBYTECODE=1

# Faz os prints aparecerem imediatamente nos logs do container.
ENV PYTHONUNBUFFERED=1

# Define onde o uv criará o ambiente virtual dentro da imagem.
# Ele fica separado da pasta que contém nosso código.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Coloca os executáveis desse ambiente no caminho de comandos.
# Assim, podemos executar python, uvicorn e alembic diretamente.
ENV PATH="/opt/venv/bin:$PATH"

# Define a pasta de trabalho dentro do container.
WORKDIR /app

# Copia primeiro apenas os arquivos das dependências.
# Os caminhos de origem serão relativos à raiz do projeto,
# conforme configuraremos no Compose.
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Instala as dependências com uv.
# --locked exige que o uv.lock esteja atualizado.
# --no-dev deixa de fora dependências de desenvolvimento.
# --no-install-project instala as bibliotecas sem instalar
# nosso próprio código como um pacote distribuível.
RUN uv sync --project backend --locked --no-dev --no-install-project

# Copia os arquivos Python e as migrations.
COPY backend/ ./backend/


# Documenta a porta utilizada pela aplicação.
# EXPOSE não publica a porta no Windows; o Compose fará isso.
EXPOSE 8000

# A configuração do servidor fica no módulo de inicialização da aplicação.
CMD ["python", "-m", "backend.app"]