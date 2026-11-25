from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ciclobox.pedidos.adapters.compra_programada_repository import (
    SqlAlchemyCompraProgramadaRepository,
)
from ciclobox.pedidos.adapters.integracoes import CatalogoViaFachada, ClubeProvisorio
from ciclobox.pedidos.adapters.pedido_repository import SqlAlchemyPedidoRepository
from ciclobox.pedidos.adapters.schemas import (
    CarrinhoEntrada,
    FinalizarPedidoEntrada,
    PedidoResposta,
    TotaisResposta,
)
from ciclobox.pedidos.adapters.usuario_provisorio import UsuarioId, UsuarioIdOpcional
from ciclobox.pedidos.application.avancar_status_pedido import avancar_status_pedido
from ciclobox.pedidos.application.calcular_totais import calcular_totais_do_carrinho
from ciclobox.pedidos.application.finalizar_pedido import finalizar_pedido
from ciclobox.pedidos.application.listar_pedidos import listar_pedidos
from ciclobox.pedidos.domain.carrinho import ItemCarrinho
from ciclobox.pedidos.domain.pedido import FormaPagamento
from ciclobox.shared.database import get_session

router = APIRouter(prefix="/api", tags=["pedidos"])

Sessao = Annotated[Session, Depends(get_session)]


def _itens(corpo: CarrinhoEntrada) -> list[ItemCarrinho]:
    return [
        ItemCarrinho(item.produto_id, item.quantidade, item.frequencia_dias) for item in corpo.itens
    ]


@router.post("/carrinho/totais")
def calcular_totais(
    corpo: CarrinhoEntrada, session: Sessao, usuario_id: UsuarioIdOpcional
) -> TotaisResposta:
    resumo = calcular_totais_do_carrinho(
        _itens(corpo), usuario_id, CatalogoViaFachada(session), ClubeProvisorio()
    )
    totais = resumo.totais
    return TotaisResposta(
        subtotal=totais.subtotal,
        desconto_programada=totais.desconto_programada,
        desconto_membro=totais.desconto_membro,
        frete=totais.frete,
        total=totais.total,
        membro=resumo.membro,
    )


@router.post("/pedidos", status_code=status.HTTP_201_CREATED)
def criar_pedido(
    corpo: FinalizarPedidoEntrada, session: Sessao, usuario_id: UsuarioId
) -> PedidoResposta:
    pedido = finalizar_pedido(
        usuario_id=usuario_id,
        itens=_itens(corpo),
        cep=corpo.cep,
        forma_pagamento=FormaPagamento(corpo.forma_pagamento),
        hoje=date.today(),
        catalogo=CatalogoViaFachada(session),
        clube=ClubeProvisorio(),
        pedidos=SqlAlchemyPedidoRepository(session),
        compras_programadas=SqlAlchemyCompraProgramadaRepository(session),
    )
    return PedidoResposta.de(pedido)


@router.get("/pedidos")
def listar_meus_pedidos(session: Sessao, usuario_id: UsuarioId) -> list[PedidoResposta]:
    pedidos = listar_pedidos(usuario_id, SqlAlchemyPedidoRepository(session))
    return [PedidoResposta.de(pedido) for pedido in pedidos]


@router.post("/pedidos/{pedido_id}/avancar-status")
def avancar_status(pedido_id: int, session: Sessao, usuario_id: UsuarioId) -> PedidoResposta:
    pedido = avancar_status_pedido(usuario_id, pedido_id, SqlAlchemyPedidoRepository(session))
    return PedidoResposta.de(pedido)
