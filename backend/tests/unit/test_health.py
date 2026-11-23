from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from ciclobox.main import create_app
from ciclobox.shared.health import get_database_check


def client_with_database_check(check) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_database_check] = lambda: check
    return TestClient(app)


def test_health_is_ok_when_database_responds():
    response = client_with_database_check(lambda: None).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_is_unavailable_when_database_fails():
    def failing_check() -> None:
        raise OperationalError("SELECT 1", {}, Exception("sem conexão"))

    response = client_with_database_check(failing_check).get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "indisponivel", "database": "erro"}


def test_root_serves_frontend():
    response = client_with_database_check(lambda: None).get("/")

    assert response.status_code == 200
    assert "Ciclo Box" in response.text
