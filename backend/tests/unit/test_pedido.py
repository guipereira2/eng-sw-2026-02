from datetime import date
from decimal import Decimal

import pytest

from ciclobox.pedidos.domain.carrinho import ItemCarrinho, ProdutoParaVenda, montar_linhas
from ciclobox.pedidos.domain.compra_programada import CompraProgramada, StatusCompraProgramada
from ciclobox.pedidos.domain.pedido import FormaPagamento, Pedido, StatusPedido
from ciclobox.shared.erros import DadoInvalidoError, RegraDeNegocioError

RACAO = ProdutoParaVenda(1, "Ração cães adultos 10 kg", Decimal("189.90"), aceita_programada=True)


def criar_pedido(cep: str = "37500000", frequencia: int | None = 30) -> Pedido:
    linhas = montar_linhas([ItemCarrinho(1, 2, frequencia)], {1: RACAO})
    return Pedido.criar(
        usuario_id=5, linhas=linhas, cep=cep, forma_pagamento=FormaPagamento.PIX, membro=False
    )


def test_pedido_nasce_pago_com_nome_e_preco_do_produto():
    pedido = criar_pedido()

    assert pedido.status is StatusPedido.PAGO
    assert pedido.itens[0].nome_produto == "Ração cães adultos 10 kg"
    assert pedido.itens[0].preco_unitario == Decimal("189.90")
    assert pedido.totais.subtotal == Decimal("379.80")


@pytest.mark.parametrize("cep", ["3750000", "375000000", "37500-00", ""])
def test_cep_precisa_ter_8_digitos(cep: str):
    with pytest.raises(DadoInvalidoError, match="CEP"):
        criar_pedido(cep=cep)


def test_status_avanca_um_passo_por_vez_ate_entregue():
    pedido = criar_pedido()
    vistos = []
    for _ in range(3):
        pedido.avancar_status()
        vistos.append(pedido.status)

    assert vistos == [StatusPedido.SEPARANDO, StatusPedido.ENVIADO, StatusPedido.ENTREGUE]


def test_pedido_entregue_nao_avanca():
    pedido = criar_pedido()
    pedido.status = StatusPedido.ENTREGUE

    with pytest.raises(RegraDeNegocioError, match="já foi entregue"):
        pedido.avancar_status()


def test_compra_programada_comeca_ativa_com_entrega_daqui_a_frequencia():
    item = criar_pedido(frequencia=45).itens[0]

    compra = CompraProgramada.a_partir_do_item(5, pedido_id=10, item=item, hoje=date(2026, 11, 30))

    assert compra.status is StatusCompraProgramada.ATIVA
    assert compra.proxima_entrega == date(2027, 1, 14)
    assert compra.quantidade == 2
    assert compra.pedido_origem_id == 10


def test_item_sem_frequencia_nao_vira_compra_programada():
    item = criar_pedido(frequencia=None).itens[0]

    with pytest.raises(DadoInvalidoError):
        CompraProgramada.a_partir_do_item(5, pedido_id=10, item=item, hoje=date(2026, 11, 30))
