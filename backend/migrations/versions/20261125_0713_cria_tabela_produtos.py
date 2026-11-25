"""cria tabela produtos

Revision ID: fbaa12362835
Revises:
"""

from collections.abc import Sequence
from decimal import Decimal

import sqlalchemy as sa
from alembic import op

revision: str = "fbaa12362835"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Lista inicial, tirada do protótipo (frontend/index.html). O grupo pode mudar à vontade.
PRODUTOS_INICIAIS = [
    ("Ração cães adultos 10 kg", "cao", "Alimentação", "189.90", True),
    ("Ração gatos castrados 3 kg", "gato", "Alimentação", "99.90", True),
    ("Areia sanitária 4 kg", "gato", "Higiene", "29.90", True),
    ("Tapete higiênico 30 un.", "cao", "Higiene", "54.90", True),
    ("Ossinho de frango 200 g", "cao", "Petiscos", "24.90", True),
    ("Bifinho de carne 500 g", "cao", "Petiscos", "32.90", False),
    ("Snack de salmão 80 g", "gato", "Petiscos", "18.90", True),
    ("Kit com 3 bolinhas", "cao", "Brinquedos", "29.90", False),
    ("Ratinho com catnip", "gato", "Brinquedos", "15.90", False),
    ("Varinha de penas", "gato", "Brinquedos", "22.90", False),
    ("Shampoo neutro 500 ml", "ambos", "Higiene", "34.90", False),
    ("Escova de silicone", "ambos", "Higiene", "27.90", False),
    ("Comedouro de inox", "ambos", "Acessórios", "39.90", False),
    ("Guia retrátil 5 m", "cao", "Acessórios", "69.90", False),
    ("Arranhador de papelão", "gato", "Acessórios", "49.90", False),
    ("Caminha redonda", "ambos", "Acessórios", "119.90", False),
]


def upgrade() -> None:
    produtos = op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("pet", sa.String(length=10), nullable=False),
        sa.Column("categoria", sa.String(length=30), nullable=False),
        sa.Column("preco", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("aceita_programada", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "categoria IN ('Alimentação', 'Petiscos', 'Brinquedos', 'Higiene', 'Acessórios')",
            name="ck_produtos_categoria",
        ),
        sa.CheckConstraint("pet IN ('cao', 'gato', 'ambos')", name="ck_produtos_pet"),
        sa.CheckConstraint("preco > 0", name="ck_produtos_preco_positivo"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        produtos,
        [
            {
                "nome": nome,
                "pet": pet,
                "categoria": categoria,
                "preco": Decimal(preco),
                "aceita_programada": aceita_programada,
            }
            for nome, pet, categoria, preco, aceita_programada in PRODUTOS_INICIAIS
        ],
    )


def downgrade() -> None:
    op.drop_table("produtos")
