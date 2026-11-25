from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ciclobox.pedidos.adapters.rotas import router as pedidos_router
from ciclobox.shared.health import router as health_router
from ciclobox.shared.http import registrar_tratamento_de_erros

FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"


def create_app() -> FastAPI:
    app = FastAPI(title="Ciclo Box API", docs_url="/api/docs", openapi_url="/api/openapi.json")
    registrar_tratamento_de_erros(app)
    app.include_router(health_router)
    app.include_router(pedidos_router)
    # Precisa ficar por último: o mount em "/" captura o que as rotas da API não trataram.
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app


app = create_app()
