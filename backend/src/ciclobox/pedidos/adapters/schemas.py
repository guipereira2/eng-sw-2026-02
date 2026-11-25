"""Formato do JSON de entrada e saída das rotas de pedidos (ver docs/backlog.md)."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from ciclobox.pedidos.domain.pedido import Pedido


class ItemCarrinhoEntrada(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)
    frequencia_dias: Literal[30, 45, 60] | None = None


class CarrinhoEntrada(BaseModel):
    itens: list[ItemCarrinhoEntrada] = Field(min_length=1)


class FinalizarPedidoEntrada(CarrinhoEntrada):
    cep: str = Field(pattern=r"^\d{8}$", description="Só os 8 dígitos, sem traço")
    forma_pagamento: Literal["pix", "cartao", "boleto"]


class TotaisResposta(BaseModel):
    subtotal: Decimal
    desconto_programada: Decimal
    desconto_membro: Decimal
    frete: Decimal
    total: Decimal
    membro: bool


class ItemPedidoResposta(BaseModel):
    produto_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal
    frequencia_dias: int | None


class PedidoResposta(BaseModel):
    id: int
    status: str
    criado_em: datetime
    itens: list[ItemPedidoResposta]
    subtotal: Decimal
    desconto_programada: Decimal
    desconto_membro: Decimal
    frete: Decimal
    total: Decimal

    @classmethod
    def de(cls, pedido: Pedido) -> "PedidoResposta":
        assert pedido.id is not None and pedido.criado_em is not None  # noqa: S101 - já salvo
        return cls(
            id=pedido.id,
            status=pedido.status.value,
            criado_em=pedido.criado_em,
            itens=[
                ItemPedidoResposta(
                    produto_id=item.produto_id,
                    nome=item.nome_produto,
                    quantidade=item.quantidade,
                    preco_unitario=item.preco_unitario,
                    frequencia_dias=item.frequencia_dias,
                )
                for item in pedido.itens
            ],
            subtotal=pedido.totais.subtotal,
            desconto_programada=pedido.totais.desconto_programada,
            desconto_membro=pedido.totais.desconto_membro,
            frete=pedido.totais.frete,
            total=pedido.totais.total,
        )
