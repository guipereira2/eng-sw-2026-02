from ciclobox.pedidos.domain.pedido import Pedido
from ciclobox.pedidos.ports import PedidoRepository


def listar_pedidos(usuario_id: int, pedidos: PedidoRepository) -> list[Pedido]:
    """HU14. Do mais novo para o mais antigo."""
    return pedidos.listar_do_usuario(usuario_id)
