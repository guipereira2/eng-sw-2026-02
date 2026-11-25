from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from ciclobox.shared.database import get_engine


@pytest.fixture
def session() -> Iterator[Session]:
    """Sessão de banco que desfaz tudo no fim do teste.

    O que o teste gravar (inclusive com `flush`) some no rollback, então um teste não
    suja o banco para o próximo.
    """
    connection = get_engine().connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
