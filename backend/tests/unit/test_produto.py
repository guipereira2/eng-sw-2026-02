from decimal import Decimal

import pytest

from ciclobox.catalogo.domain.produto import Categoria, Pet, Produto


def criar_produto(**campos) -> Produto:
    padrao = {
        "nome": "Ração cães adultos 10 kg",
        "pet": Pet.CAO,
        "categoria": Categoria.ALIMENTACAO,
        "preco": Decimal("189.90"),
        "aceita_programada": True,
    }
    return Produto(**(padrao | campos))


def test_produto_novo_ainda_nao_tem_id():
    assert criar_produto().id is None


def test_nome_vazio_nao_e_aceito():
    with pytest.raises(ValueError, match="nome"):
        criar_produto(nome="   ")


@pytest.mark.parametrize("preco", [Decimal("0"), Decimal("-1.00")])
def test_preco_precisa_ser_positivo(preco: Decimal):
    with pytest.raises(ValueError, match="preço"):
        criar_produto(preco=preco)
