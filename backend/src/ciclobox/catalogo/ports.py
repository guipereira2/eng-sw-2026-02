from collections.abc import Iterable
from typing import Protocol

from ciclobox.catalogo.domain.produto import Produto


class ProdutoRepository(Protocol):
    """O que o catálogo precisa para guardar e buscar produtos.

    A implementação com banco fica em `adapters/`. Nos testes de regra, dá para usar uma
    versão em memória que siga esta mesma interface.
    """

    def buscar_por_id(self, produto_id: int) -> Produto | None: ...

    def buscar_por_ids(self, produto_ids: Iterable[int]) -> list[Produto]: ...

    def salvar(self, produto: Produto) -> Produto: ...
