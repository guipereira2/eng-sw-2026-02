"""O que outros módulos podem pedir ao catálogo.

Outros módulos não podem importar `catalogo.domain` nem `catalogo.adapters` (o import-linter
barra), então a fachada devolve um tipo próprio, só com o que é preciso fora daqui.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from ciclobox.catalogo.adapters.produto_repository import SqlAlchemyProdutoRepository


@dataclass(frozen=True)
class ProdutoResumo:
    id: int
    nome: str
    preco: Decimal
    aceita_programada: bool


def buscar_produtos(session: Session, produto_ids: Iterable[int]) -> dict[int, ProdutoResumo]:
    """Devolve os produtos encontrados, indexados pelo id. Ids inexistentes ficam de fora."""
    produtos = SqlAlchemyProdutoRepository(session).buscar_por_ids(produto_ids)
    return {
        produto.id: ProdutoResumo(
            id=produto.id,
            nome=produto.nome,
            preco=produto.preco,
            aceita_programada=produto.aceita_programada,
        )
        for produto in produtos
        if produto.id is not None
    }
