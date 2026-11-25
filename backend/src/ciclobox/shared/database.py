from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session

from ciclobox.shared.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Dependência do FastAPI: uma sessão por requisição.

    Faz commit se a rota terminar sem erro e rollback se der qualquer exceção.
    """
    with Session(get_engine()) as session, session.begin():
        yield session


def ping_database() -> None:
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
