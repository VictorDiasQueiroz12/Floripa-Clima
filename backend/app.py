"""Inicialização da API: python -m backend.app, a partir da raiz."""

import os
from pathlib import Path

from dotenv import load_dotenv
import uvicorn


def main():
    # Variáveis fornecidas pelo ambiente prevalecem sobre o .env local.
    pasta_projeto = Path(__file__).resolve().parent.parent
    load_dotenv(pasta_projeto / ".env", override=False)

    # O acesso externo deve ser habilitado explicitamente no container.
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    if not 1 <= port <= 65535:
        raise ValueError("API_PORT deve estar entre 1 e 65535.")

    uvicorn.run("backend.api:app", host=host, port=port)


# Importar este módulo não inicia o servidor.
if __name__ == "__main__":
    main()
