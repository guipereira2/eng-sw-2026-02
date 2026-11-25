from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from ciclobox.shared.database import Base


class ProdutoModel(Base):
    __tablename__ = "produtos"
    __table_args__ = (
        CheckConstraint("pet IN ('cao', 'gato', 'ambos')", name="ck_produtos_pet"),
        CheckConstraint(
            "categoria IN ('Alimentação', 'Petiscos', 'Brinquedos', 'Higiene', 'Acessórios')",
            name="ck_produtos_categoria",
        ),
        CheckConstraint("preco > 0", name="ck_produtos_preco_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    pet: Mapped[str] = mapped_column(String(10))
    categoria: Mapped[str] = mapped_column(String(30))
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    aceita_programada: Mapped[bool] = mapped_column(Boolean, default=False)
