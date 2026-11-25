from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from ciclobox.pedidos.domain.pedido import ItemPedido
from ciclobox.shared.erros import DadoInvalidoError


class StatusCompraProgramada(StrEnum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    CANCELADA = "cancelada"


@dataclass
class CompraProgramada:
    """Entrega recorrente de um item comprado na loja.

    Aqui só existe a criação, que acontece ao finalizar o pedido (HU13). Pausar, retomar,
    pular, cancelar e trocar frequência são do fluxo de compra programada (HU17 e HU18).
    """

    usuario_id: int
    produto_id: int
    pedido_origem_id: int
    nome_produto: str
    quantidade: int
    frequencia_dias: int
    proxima_entrega: date
    status: StatusCompraProgramada = StatusCompraProgramada.ATIVA
    id: int | None = None

    @classmethod
    def a_partir_do_item(
        cls, usuario_id: int, pedido_id: int, item: ItemPedido, hoje: date
    ) -> "CompraProgramada":
        if item.frequencia_dias is None:
            raise DadoInvalidoError("O item não é de compra programada")
        return cls(
            usuario_id=usuario_id,
            produto_id=item.produto_id,
            pedido_origem_id=pedido_id,
            nome_produto=item.nome_produto,
            quantidade=item.quantidade,
            frequencia_dias=item.frequencia_dias,
            proxima_entrega=hoje + timedelta(days=item.frequencia_dias),
        )
