"""criar tabela weather_daily

Revision ID: 4e5f2211361d
Revises: 
Create Date: 2026-10-15 17:06:56.239204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5f2211361d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Cria a tabela quando esta migration for aplicada.
    # Não usamos IF NOT EXISTS: uma tabela inesperada deve gerar erro, em vez de esconder diferenças na estrutura.
    op.create_table(
        "weather_daily",

        # Identificador inteiro gerado automaticamente.
        # always=True corresponde a GENERATED ALWAYS AS IDENTITY.
        # primary_key=True define a chave primária.
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=True),
            primary_key=True,
            nullable=False,
        ),

        # Texto obrigatório que identifica a localização.
        sa.Column(
            "localidade",
            sa.Text(),
            nullable=False,
        ),

        # Texto obrigatório que identifica a fonte.
        sa.Column(
            "fonte",
            sa.Text(),
            nullable=False,
        ),

        # Data sem horário, com preenchimento obrigatório.
        sa.Column(
            "data",
            sa.Date(),
            nullable=False,
        ),

        # Numeric(5, 1) corresponde ao NUMERIC(5, 1) do SQL.
        # nullable=True permite dados ausentes.
        sa.Column(
            "temperatura_maxima",
            sa.Numeric(5, 1),
            nullable=True,
        ),

        sa.Column(
            "temperatura_minima",
            sa.Numeric(5, 1),
            nullable=True,
        ),

        # Precipitação com duas casas decimais.
        sa.Column(
            "precipitacao",
            sa.Numeric(8, 2),
            nullable=True,
        ),

        # DateTime(timezone=True) corresponde ao TIMESTAMPTZ
        # no PostgreSQL.
        #
        # server_default define um valor calculado pelo banco,
        # inclusive quando a inserção é feita fora do Python.
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),

        # Impede repetir a mesma localidade, fonte e data.
        sa.UniqueConstraint(
            "localidade",
            "fonte",
            "data",
            name="weather_daily_localidade_fonte_data_unique",
        ),

        # Impede precipitação negativa, permitindo NULL.
        sa.CheckConstraint(
            "precipitacao >= 0",
            name="weather_daily_precipitacao_check",
        ),

        # Quando ambas existem, a máxima não pode ser menor.
        sa.CheckConstraint(
            "temperatura_maxima >= temperatura_minima",
            name="weather_daily_temperaturas_check",
        ),

        # Indica explicitamente o schema utilizado.
        schema="public",
    )


def downgrade() -> None:
    # Desfaz a criação removendo a tabela.
    # Executar esse downgrade também apagaria seus registros.
    op.drop_table("weather_daily", schema="public")
