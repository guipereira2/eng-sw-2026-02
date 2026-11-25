from collections.abc import Sequence
from dataclasses import dataclass

from ciclobox.pedidos.domain.carrinho import ItemCarrinho, montar_linhas
from ciclobox.pedidos.domain.totais import Totais, calcular_totais
from ciclobox.pedidos.ports import CatalogoPort, ClubePort


@dataclass(frozen=True)
class ResumoDoCarrinho:
    totais: Totais
    membro: bool


def calcular_totais_do_carrinho(
    itens: Sequence[ItemCarrinho],
    usuario_id: int | None,
    catalogo: CatalogoPort,
    clube: ClubePort,
) -> ResumoDoCarrinho:
    """HU12. Sem usuário logado, o cliente não é membro."""
    produtos = catalogo.buscar_produtos({item.produto_id for item in itens})
    linhas = montar_linhas(itens, produtos)
    membro = usuario_id is not None and clube.eh_membro(usuario_id)
    return ResumoDoCarrinho(totais=calcular_totais(linhas, membro), membro=membro)
