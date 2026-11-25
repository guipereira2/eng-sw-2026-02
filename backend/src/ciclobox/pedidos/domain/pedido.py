from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from ciclobox.pedidos.domain.carrinho import LinhaDoCarrinho
from ciclobox.pedidos.domain.totais import Totais, calcular_totais
from ciclobox.shared.erros import DadoInvalidoError, RegraDeNegocioError


class StatusPedido(StrEnum):
    PAGO = "Pago"
    SEPARANDO = "Separando"
    ENVIADO = "Enviado"
    ENTREGUE = "Entregue"


SEQUENCIA_DE_STATUS = list(StatusPedido)


class FormaPagamento(StrEnum):
    PIX = "pix"
    CARTAO = "cartao"
    BOLETO = "boleto"


@dataclass
class ItemPedido:
    """Guarda nome e preço do produto no momento da compra."""

    produto_id: int
    nome_produto: str
    preco_unitario: Decimal
    quantidade: int
    frequencia_dias: int | None = None
    id: int | None = None


@dataclass
class Pedido:
    usuario_id: int
    cep: str
    forma_pagamento: FormaPagamento
    itens: list[ItemPedido]
    totais: Totais
    status: StatusPedido = StatusPedido.PAGO
    id: int | None = None
    criado_em: datetime | None = field(default=None)
    """Preenchido pelo banco ao salvar."""

    @classmethod
    def criar(
        cls,
        usuario_id: int,
        linhas: Sequence[LinhaDoCarrinho],
        cep: str,
        forma_pagamento: FormaPagamento,
        membro: bool,
    ) -> "Pedido":
        if len(cep) != 8 or not cep.isdigit():
            raise DadoInvalidoError("O CEP precisa ter 8 dígitos")
        if not linhas:
            raise DadoInvalidoError("O carrinho está vazio")

        itens = [
            ItemPedido(
                produto_id=linha.produto.id,
                nome_produto=linha.produto.nome,
                preco_unitario=linha.produto.preco,
                quantidade=linha.quantidade,
                frequencia_dias=linha.frequencia_dias,
            )
            for linha in linhas
        ]
        return cls(
            usuario_id=usuario_id,
            cep=cep,
            forma_pagamento=forma_pagamento,
            itens=itens,
            totais=calcular_totais(linhas, membro),
        )

    def avancar_status(self) -> None:
        """Pago → Separando → Enviado → Entregue, sem pular nem voltar."""
        if self.status is StatusPedido.ENTREGUE:
            raise RegraDeNegocioError("O pedido já foi entregue")
        posicao = SEQUENCIA_DE_STATUS.index(self.status)
        self.status = SEQUENCIA_DE_STATUS[posicao + 1]
