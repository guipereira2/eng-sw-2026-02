from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CodigoPlano(StrEnum):
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"


@dataclass(frozen=True)
class Plano:
    codigo: CodigoPlano
    nome: str
    preco_caixa: Decimal
    caixas_por_cobranca: int
    frete_gratis: bool


PLANOS: dict[CodigoPlano, Plano] = {
    CodigoPlano.MENSAL: Plano(
        codigo=CodigoPlano.MENSAL,
        nome="Mensal",
        preco_caixa=Decimal("89.90"),
        caixas_por_cobranca=1,
        frete_gratis=False,
    ),
    CodigoPlano.TRIMESTRAL: Plano(
        codigo=CodigoPlano.TRIMESTRAL,
        nome="Trimestral",
        preco_caixa=Decimal("79.90"),
        caixas_por_cobranca=3,
        frete_gratis=False,
    ),
    CodigoPlano.ANUAL: Plano(
        codigo=CodigoPlano.ANUAL,
        nome="Anual",
        preco_caixa=Decimal("69.90"),
        caixas_por_cobranca=12,
        frete_gratis=True,
    ),
}
