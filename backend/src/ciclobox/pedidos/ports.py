from collections.abc import Iterable
from typing import Protocol

from ciclobox.pedidos.domain.carrinho import ProdutoParaVenda
from ciclobox.pedidos.domain.compra_programada import CompraProgramada
from ciclobox.pedidos.domain.pedido import Pedido


class CatalogoPort(Protocol):
    """Preço, nome e elegibilidade dos produtos. Quem responde é o módulo catalogo."""

    def buscar_produtos(self, produto_ids: Iterable[int]) -> dict[int, ProdutoParaVenda]: ...


class ClubePort(Protocol):
    """Se o cliente é membro do Clube. Quem responde é o módulo assinaturas."""

    def eh_membro(self, usuario_id: int) -> bool: ...


class PedidoRepository(Protocol):
    def salvar(self, pedido: Pedido) -> Pedido: ...

    def buscar_por_id(self, pedido_id: int) -> Pedido | None: ...

    def listar_do_usuario(self, usuario_id: int) -> list[Pedido]: ...


class CompraProgramadaRepository(Protocol):
    def salvar(self, compra: CompraProgramada) -> CompraProgramada: ...
