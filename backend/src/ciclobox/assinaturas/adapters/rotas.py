from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel

from ciclobox.assinaturas.domain.plano import PLANOS

router = APIRouter(prefix="/api", tags=["assinaturas"])


class PlanoResposta(BaseModel):
    codigo: str
    nome: str
    preco_caixa: Decimal
    caixas_por_cobranca: int
    frete_gratis: bool


@router.get("/planos")
def listar_planos() -> list[PlanoResposta]:
    return [
        PlanoResposta(
            codigo=plano.codigo,
            nome=plano.nome,
            preco_caixa=plano.preco_caixa,
            caixas_por_cobranca=plano.caixas_por_cobranca,
            frete_gratis=plano.frete_gratis,
        )
        for plano in PLANOS.values()
    ]
