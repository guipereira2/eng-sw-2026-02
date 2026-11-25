from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ciclobox.catalogo.adapters.models import ProdutoModel
from ciclobox.catalogo.domain.produto import Categoria, Pet, Produto


class SqlAlchemyProdutoRepository:
    """Implementa `ciclobox.catalogo.ports.ProdutoRepository` com Postgres.

    Converte entre a linha do banco (`ProdutoModel`) e a entidade (`Produto`), para o
    resto do módulo nunca lidar com SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar_por_id(self, produto_id: int) -> Produto | None:
        model = self._session.get(ProdutoModel, produto_id)
        return _para_entidade(model) if model else None

    def buscar_por_ids(self, produto_ids: Iterable[int]) -> list[Produto]:
        ids = list(produto_ids)
        if not ids:
            return []
        models = self._session.scalars(select(ProdutoModel).where(ProdutoModel.id.in_(ids)))
        return [_para_entidade(model) for model in models]

    def salvar(self, produto: Produto) -> Produto:
        model = ProdutoModel(
            id=produto.id,
            nome=produto.nome,
            pet=produto.pet.value,
            categoria=produto.categoria.value,
            preco=produto.preco,
            aceita_programada=produto.aceita_programada,
        )
        model = self._session.merge(model)
        self._session.flush()
        return _para_entidade(model)


def _para_entidade(model: ProdutoModel) -> Produto:
    return Produto(
        id=model.id,
        nome=model.nome,
        pet=Pet(model.pet),
        categoria=Categoria(model.categoria),
        preco=model.preco,
        aceita_programada=model.aceita_programada,
    )
