from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from ciclobox.catalogo.adapters.models import ProdutoModel
from ciclobox.main import create_app
from ciclobox.pedidos.adapters.models import CompraProgramadaModel
from ciclobox.shared.database import get_session

pytestmark = pytest.mark.integration

USUARIO = {"X-Usuario-Id": "42"}
OUTRO_USUARIO = {"X-Usuario-Id": "43"}


@pytest.fixture
def client(session: Session) -> TestClient:
    """Cliente da API usando a sessão do teste, que desfaz tudo no fim."""

    def sessao_do_teste() -> Iterator[Session]:
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = sessao_do_teste
    return TestClient(app)


def id_do_produto(session: Session, nome: str) -> int:
    return session.scalars(select(ProdutoModel.id).where(ProdutoModel.nome == nome)).one()


@pytest.fixture
def racao(session: Session) -> int:
    return id_do_produto(session, "Ração cães adultos 10 kg")


@pytest.fixture
def bifinho(session: Session) -> int:
    return id_do_produto(session, "Bifinho de carne 500 g")


def corpo_pedido(*itens: dict) -> dict:
    return {"itens": list(itens), "cep": "37500000", "forma_pagamento": "pix"}


def test_totais_do_carrinho(client: TestClient, racao: int, bifinho: int):
    resposta = client.post(
        "/api/carrinho/totais",
        json={
            "itens": [
                {"produto_id": racao, "quantidade": 1, "frequencia_dias": 30},
                {"produto_id": bifinho, "quantidade": 2, "frequencia_dias": None},
            ]
        },
    )

    assert resposta.status_code == 200
    assert resposta.json() == {
        "subtotal": "255.70",
        "desconto_programada": "9.50",
        "desconto_membro": "0.00",
        "frete": "14.90",
        "total": "261.10",
        "membro": False,
    }


def test_totais_recusa_programada_em_produto_que_nao_aceita(client: TestClient, bifinho: int):
    resposta = client.post(
        "/api/carrinho/totais",
        json={"itens": [{"produto_id": bifinho, "quantidade": 1, "frequencia_dias": 30}]},
    )

    assert resposta.status_code == 422
    assert resposta.json() == {"detail": "Bifinho de carne 500 g não aceita compra programada"}


def test_finalizar_pedido_cria_pedido_pago_e_compra_programada(
    client: TestClient, session: Session, racao: int, bifinho: int
):
    resposta = client.post(
        "/api/pedidos",
        headers=USUARIO,
        json=corpo_pedido(
            {"produto_id": racao, "quantidade": 1, "frequencia_dias": 30},
            {"produto_id": bifinho, "quantidade": 2},
        ),
    )

    assert resposta.status_code == 201
    pedido = resposta.json()
    assert pedido["status"] == "Pago"
    assert pedido["total"] == "261.10"
    assert [item["nome"] for item in pedido["itens"]] == [
        "Ração cães adultos 10 kg",
        "Bifinho de carne 500 g",
    ]

    compras = session.scalars(
        select(CompraProgramadaModel).where(CompraProgramadaModel.pedido_origem_id == pedido["id"])
    ).all()
    assert [(c.produto_id, c.frequencia_dias, c.status) for c in compras] == [(racao, 30, "ativa")]


def test_finalizar_pedido_exige_usuario(client: TestClient, racao: int):
    resposta = client.post(
        "/api/pedidos", json=corpo_pedido({"produto_id": racao, "quantidade": 1})
    )

    assert resposta.status_code == 401


@pytest.mark.parametrize(
    "alteracao",
    [{"itens": []}, {"cep": "3750000"}, {"forma_pagamento": "dinheiro"}],
)
def test_finalizar_pedido_valida_entrada(client: TestClient, racao: int, alteracao: dict):
    corpo = corpo_pedido({"produto_id": racao, "quantidade": 1}) | alteracao

    resposta = client.post("/api/pedidos", headers=USUARIO, json=corpo)

    assert resposta.status_code == 422


def test_listar_mostra_so_os_pedidos_do_usuario_do_mais_novo_para_o_mais_antigo(
    client: TestClient, racao: int, bifinho: int
):
    primeiro = client.post(
        "/api/pedidos", headers=USUARIO, json=corpo_pedido({"produto_id": racao, "quantidade": 1})
    ).json()
    segundo = client.post(
        "/api/pedidos", headers=USUARIO, json=corpo_pedido({"produto_id": bifinho, "quantidade": 1})
    ).json()
    client.post(
        "/api/pedidos",
        headers=OUTRO_USUARIO,
        json=corpo_pedido({"produto_id": racao, "quantidade": 1}),
    )

    resposta = client.get("/api/pedidos", headers=USUARIO)

    assert resposta.status_code == 200
    assert [p["id"] for p in resposta.json()] == [segundo["id"], primeiro["id"]]


def test_avancar_status_ate_entregue_e_depois_409(client: TestClient, racao: int):
    pedido = client.post(
        "/api/pedidos", headers=USUARIO, json=corpo_pedido({"produto_id": racao, "quantidade": 1})
    ).json()
    url = f"/api/pedidos/{pedido['id']}/avancar-status"

    status_vistos = [client.post(url, headers=USUARIO).json()["status"] for _ in range(3)]
    depois_de_entregue = client.post(url, headers=USUARIO)

    assert status_vistos == ["Separando", "Enviado", "Entregue"]
    assert depois_de_entregue.status_code == 409
    assert depois_de_entregue.json() == {"detail": "O pedido já foi entregue"}


def test_avancar_status_de_pedido_de_outro_usuario_responde_404(client: TestClient, racao: int):
    pedido = client.post(
        "/api/pedidos", headers=USUARIO, json=corpo_pedido({"produto_id": racao, "quantidade": 1})
    ).json()

    resposta = client.post(f"/api/pedidos/{pedido['id']}/avancar-status", headers=OUTRO_USUARIO)

    assert resposta.status_code == 404
