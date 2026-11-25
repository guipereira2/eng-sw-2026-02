from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ciclobox.shared.erros import (
    DadoInvalidoError,
    ErroDeDominio,
    NaoEncontradoError,
    RegraDeNegocioError,
)

STATUS_POR_ERRO: dict[type[ErroDeDominio], int] = {
    DadoInvalidoError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    RegraDeNegocioError: status.HTTP_409_CONFLICT,
    NaoEncontradoError: status.HTTP_404_NOT_FOUND,
}


async def tratar_erro_de_dominio(_request: Request, erro: Exception) -> JSONResponse:
    assert isinstance(erro, ErroDeDominio)  # noqa: S101 - o FastAPI só chama para ErroDeDominio
    codigo = next(
        (cod for tipo, cod in STATUS_POR_ERRO.items() if isinstance(erro, tipo)),
        status.HTTP_400_BAD_REQUEST,
    )
    return JSONResponse(status_code=codigo, content={"detail": erro.mensagem})


def registrar_tratamento_de_erros(app: FastAPI) -> None:
    app.add_exception_handler(ErroDeDominio, tratar_erro_de_dominio)
