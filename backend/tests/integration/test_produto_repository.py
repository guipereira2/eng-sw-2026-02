from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ciclobox.catalogo.adapters.models import ProdutoModel
from ciclobox.catalogo.adapters.produto_repository import SqlAlchemyProdutoRepository
from ciclobox.catalogo.domain.produto import Categoria, Pet, Produto

pytestmark = pytest.mark.integration


def test_seed_cria_os_16_produtos_iniciais(session: Session):
    assert session.scalar(select(func.count()).select_from(ProdutoModel)) == 16


def test_salva_e_busca_produto(session: Session):
    repositorio = SqlAlchemyProdutoRepository(session)
    novo = Produto(
        nome="Coleira refletiva",
        pet=Pet.CAO,
        categoria=Categoria.ACESSORIOS,
        preco=Decimal("45.50"),
    )

    salvo = repositorio.salvar(novo)

    assert salvo.id is not None
    assert repositorio.buscar_por_id(salvo.id) == salvo


def test_buscar_produto_inexistente_devolve_none(session: Session):
    assert SqlAlchemyProdutoRepository(session).buscar_por_id(999_999) is None
