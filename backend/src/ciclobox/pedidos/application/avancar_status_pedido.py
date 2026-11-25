from ciclobox.pedidos.domain.pedido import Pedido
from ciclobox.pedidos.ports import PedidoRepository
from ciclobox.shared.erros import NaoEncontradoError


def avancar_status_pedido(usuario_id: int, pedido_id: int, pedidos: PedidoRepository) -> Pedido:
    """HU15. Pedido de outro usuário responde como se não existisse."""
    pedido = pedidos.buscar_por_id(pedido_id)
    if pedido is None or pedido.usuario_id != usuario_id:
        raise NaoEncontradoError("Pedido não encontrado")
    pedido.avancar_status()
    return pedidos.salvar(pedido)
