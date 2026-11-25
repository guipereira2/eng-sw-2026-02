from decimal import Decimal

import pytest

from ciclobox.pedidos.domain.carrinho import (
    ItemCarrinho,
    LinhaDoCarrinho,
    ProdutoParaVenda,
    montar_linhas,
)
from ciclobox.pedidos.domain.totais import calcular_totais
from ciclobox.shared.erros import DadoInvalidoError

RACAO = ProdutoParaVenda(1, "Ração cães adultos 10 kg", Decimal("189.90"), aceita_programada=True)
BIFINHO = ProdutoParaVenda(7, "Bifinho de carne 500 g", Decimal("19.90"), aceita_programada=False)
CAMINHA = ProdutoParaVenda(12, "Caminha redonda", Decimal("119.90"), aceita_programada=False)
PRODUTOS = {p.id: p for p in (RACAO, BIFINHO, CAMINHA)}


def linhas(*itens: ItemCarrinho) -> list[LinhaDoCarrinho]:
    return montar_linhas(itens, PRODUTOS)


def test_exemplo_do_backlog_com_programada_e_membro():
    totais = calcular_totais(
        linhas(ItemCarrinho(1, 1, 30), ItemCarrinho(7, 2)),
        membro=True,
    )

    assert totais.subtotal == Decimal("229.70")
    assert totais.desconto_programada == Decimal("9.50")  # 5% de 189,90 = 9,495
    assert totais.desconto_membro == Decimal("22.02")  # 10% de 220,20
    assert totais.frete == Decimal("0.00")
    assert totais.total == Decimal("198.18")


def test_sem_desconto_paga_frete():
    totais = calcular_totais(linhas(ItemCarrinho(7, 1)), membro=False)

    assert totais.desconto_programada == Decimal("0.00")
    assert totais.desconto_membro == Decimal("0.00")
    assert totais.frete == Decimal("14.90")
    assert totais.total == Decimal("34.80")


def test_so_programada():
    totais = calcular_totais(linhas(ItemCarrinho(1, 1, 45)), membro=False)

    assert totais.desconto_programada == Decimal("9.50")
    assert totais.desconto_membro == Decimal("0.00")
    assert totais.total == Decimal("195.30")  # 189,90 - 9,50 + 14,90


def test_nao_membro_paga_frete_mesmo_acima_de_150():
    totais = calcular_totais(linhas(ItemCarrinho(12, 2)), membro=False)

    assert totais.frete == Decimal("14.90")


def test_membro_abaixo_de_150_paga_frete():
    totais = calcular_totais(linhas(ItemCarrinho(12, 1)), membro=True)

    assert totais.desconto_membro == Decimal("11.99")  # 10% de 119,90
    assert totais.frete == Decimal("14.90")
    assert totais.total == Decimal("122.81")


def test_membro_com_exatamente_150_tem_frete_gratis():
    produto = ProdutoParaVenda(99, "Produto teste", Decimal("166.67"), aceita_programada=False)
    totais = calcular_totais(
        montar_linhas([ItemCarrinho(99, 1)], {99: produto}),
        membro=True,
    )

    # 166,67 - 16,67 = 150,00
    assert totais.desconto_membro == Decimal("16.67")
    assert totais.frete == Decimal("0.00")
    assert totais.total == Decimal("150.00")


def test_carrinho_vazio_nao_e_aceito():
    with pytest.raises(DadoInvalidoError, match="vazio"):
        linhas()


def test_produto_inexistente_nao_e_aceito():
    with pytest.raises(DadoInvalidoError, match="não encontrado"):
        linhas(ItemCarrinho(404, 1))


def test_frequencia_em_produto_que_nao_aceita_programada():
    with pytest.raises(DadoInvalidoError, match="não aceita compra programada"):
        linhas(ItemCarrinho(7, 1, 30))


@pytest.mark.parametrize("frequencia", [0, 15, 90])
def test_frequencia_fora_das_permitidas(frequencia: int):
    with pytest.raises(DadoInvalidoError, match="30, 45 ou 60"):
        linhas(ItemCarrinho(1, 1, frequencia))


def test_quantidade_zero_nao_e_aceita():
    with pytest.raises(DadoInvalidoError, match="quantidade"):
        linhas(ItemCarrinho(1, 0))
