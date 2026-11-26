from fastapi.testclient import TestClient

from ciclobox.main import create_app


def test_lista_os_tres_planos_na_ordem():
    response = TestClient(create_app()).get("/api/planos")

    assert response.status_code == 200
    assert [plano["codigo"] for plano in response.json()] == ["mensal", "trimestral", "anual"]


def test_plano_mensal_vem_no_formato_combinado():
    response = TestClient(create_app()).get("/api/planos")

    assert response.json()[0] == {
        "codigo": "mensal",
        "nome": "Mensal",
        "preco_caixa": "89.90",
        "caixas_por_cobranca": 1,
        "frete_gratis": False,
    }


def test_so_o_anual_tem_frete_gratis():
    response = TestClient(create_app()).get("/api/planos")

    frete_gratis = {plano["codigo"]: plano["frete_gratis"] for plano in response.json()}
    assert frete_gratis == {"mensal": False, "trimestral": False, "anual": True}
