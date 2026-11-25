from collections.abc import Sequence
from datetime import date

from ciclobox.pedidos.domain.carrinho import ItemCarrinho, montar_linhas
from ciclobox.pedidos.domain.compra_programada import CompraProgramada
from ciclobox.pedidos.domain.pedido import FormaPagamento, Pedido
from ciclobox.pedidos.ports import (
    CatalogoPort,
    ClubePort,
    CompraProgramadaRepository,
    PedidoRepository,
)


def finalizar_pedido(
    *,
    usuario_id: int,
    itens: Sequence[ItemCarrinho],
    cep: str,
    forma_pagamento: FormaPagamento,
    hoje: date,
    catalogo: CatalogoPort,
    clube: ClubePort,
    pedidos: PedidoRepository,
    compras_programadas: CompraProgramadaRepository,
) -> Pedido:
    """HU13. Cria o pedido já pago e uma compra programada para cada item com frequência."""
    produtos = catalogo.buscar_produtos({item.produto_id for item in itens})
    linhas = montar_linhas(itens, produtos)
    pedido = Pedido.criar(
        usuario_id=usuario_id,
        linhas=linhas,
        cep=cep,
        forma_pagamento=forma_pagamento,
        membro=clube.eh_membro(usuario_id),
    )
    pedido = pedidos.salvar(pedido)
    assert pedido.id is not None  # noqa: S101 - o repositório sempre devolve com id

    for item in pedido.itens:
        if item.frequencia_dias is not None:
            compras_programadas.salvar(
                CompraProgramada.a_partir_do_item(usuario_id, pedido.id, item, hoje)
            )
    return pedido
