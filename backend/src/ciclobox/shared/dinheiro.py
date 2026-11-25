from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal("0.01")


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda para centavos, com meio para cima (0,005 vira 0,01)."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)
