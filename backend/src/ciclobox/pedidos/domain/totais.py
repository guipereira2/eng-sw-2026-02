from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from ciclobox.pedidos.domain.carrinho import LinhaDoCarrinho
from ciclobox.shared.dinheiro import arredondar

DESCONTO_PROGRAMADA = Decimal("0.05")
DESCONTO_MEMBRO = Decimal("0.10")
FRETE_LOJA = Decimal("14.90")
FRETE_GRATIS_A_PARTIR_DE = Decimal("150.00")
ZERO = Decimal("0.00")


@dataclass(frozen=True)
class Totais:
    subtotal: Decimal
    desconto_programada: Decimal
    desconto_membro: Decimal
    frete: Decimal
    total: Decimal


def calcular_totais(linhas: Sequence[LinhaDoCarrinho], membro: bool) -> Totais:
    """Aplica os descontos na ordem certa e decide o frete.

    1. Compra programada: 5% sobre a soma dos itens programados.
    2. Membro do Clube: 10% sobre o subtotal já com o desconto de compra programada.
    3. Frete de R$ 14,90, grátis para membro com valor (já com descontos) de pelo menos R$ 150.

    Cada valor é arredondado logo depois da conta, e a conta seguinte usa o valor arredondado.
    """
    subtotal = arredondar(sum((linha.valor for linha in linhas), ZERO))
    base_programada = sum((linha.valor for linha in linhas if linha.programada), ZERO)
    desconto_programada = arredondar(base_programada * DESCONTO_PROGRAMADA)

    desconto_membro = ZERO
    if membro:
        desconto_membro = arredondar((subtotal - desconto_programada) * DESCONTO_MEMBRO)

    liquido = subtotal - desconto_programada - desconto_membro
    frete_gratis = membro and liquido >= FRETE_GRATIS_A_PARTIR_DE
    frete = ZERO if frete_gratis else FRETE_LOJA

    return Totais(
        subtotal=subtotal,
        desconto_programada=desconto_programada,
        desconto_membro=desconto_membro,
        frete=frete,
        total=arredondar(liquido + frete),
    )
