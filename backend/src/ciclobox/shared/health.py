from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.exc import SQLAlchemyError

from ciclobox.shared.database import ping_database

router = APIRouter(prefix="/api", tags=["health"])


def get_database_check() -> Callable[[], None]:
    return ping_database


@router.get("/health")
def health(
    response: Response,
    check_database: Annotated[Callable[[], None], Depends(get_database_check)],
) -> dict[str, str]:
    try:
        check_database()
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "indisponivel", "database": "erro"}
    return {"status": "ok", "database": "ok"}
