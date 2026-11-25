from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ciclobox.shared.database import Base


class PedidoModel(Base):
    __tablename__ = "pedidos"
    __table_args__ = (
        CheckConstraint(
            "status IN ('Pago', 'Separando', 'Enviado', 'Entregue')", name="ck_pedidos_status"
        ),
        CheckConstraint(
            "forma_pagamento IN ('pix', 'cartao', 'boleto')", name="ck_pedidos_forma_pagamento"
        ),
    )
    # Busca o criado_em gerado pelo banco logo depois do INSERT.
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(20))
    cep: Mapped[str] = mapped_column(String(8))
    forma_pagamento: Mapped[str] = mapped_column(String(10))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    desconto_programada: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    desconto_membro: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    frete: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    itens: Mapped[list["ItemPedidoModel"]] = relationship(
        cascade="all, delete-orphan", order_by="ItemPedidoModel.id", lazy="selectin"
    )


class ItemPedidoModel(Base):
    __tablename__ = "itens_pedido"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_itens_pedido_quantidade"),
        CheckConstraint(
            "frequencia_dias IS NULL OR frequencia_dias IN (30, 45, 60)",
            name="ck_itens_pedido_frequencia",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), index=True)
    produto_id: Mapped[int] = mapped_column(Integer)
    nome_produto: Mapped[str] = mapped_column(String(120))
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantidade: Mapped[int] = mapped_column(Integer)
    frequencia_dias: Mapped[int | None] = mapped_column(Integer)


class CompraProgramadaModel(Base):
    __tablename__ = "compras_programadas"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ativa', 'pausada', 'cancelada')", name="ck_compras_programadas_status"
        ),
        CheckConstraint(
            "frequencia_dias IN (30, 45, 60)", name="ck_compras_programadas_frequencia"
        ),
        CheckConstraint("quantidade > 0", name="ck_compras_programadas_quantidade"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, index=True)
    produto_id: Mapped[int] = mapped_column(Integer)
    pedido_origem_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    nome_produto: Mapped[str] = mapped_column(String(120))
    quantidade: Mapped[int] = mapped_column(Integer)
    frequencia_dias: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(10))
    proxima_entrega: Mapped[date] = mapped_column(Date)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
