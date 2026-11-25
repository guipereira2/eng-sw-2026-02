from decimal import Decimal

import pytest

from ciclobox.shared.dinheiro import arredondar


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("9.495"), Decimal("9.50")),
        (Decimal("9.494"), Decimal("9.49")),
        (Decimal("8.49"), Decimal("8.49")),
        (Decimal("10"), Decimal("10.00")),
        (Decimal("0.005"), Decimal("0.01")),
    ],
)
def test_arredonda_para_centavos_com_meio_para_cima(valor: Decimal, esperado: Decimal):
    assert arredondar(valor) == esperado
    assert arredondar(valor).as_tuple().exponent == -2
