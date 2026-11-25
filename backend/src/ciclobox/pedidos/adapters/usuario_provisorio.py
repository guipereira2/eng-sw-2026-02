"""PROVISÓRIO: identifica o usuário pelo header `X-Usuario-Id`.

Existe só enquanto o login (HU02) não fica pronto. Quando a dependência `usuario_logado`
existir, as rotas trocam `UsuarioId` e `UsuarioIdOpcional` por ela, e este arquivo some.
Não tem segurança nenhuma: qualquer um manda o id que quiser.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status


def _usuario_id_opcional(
    x_usuario_id: Annotated[
        int | None, Header(description="Provisório até o login existir")
    ] = None,
) -> int | None:
    return x_usuario_id


def _usuario_id_obrigatorio(
    usuario_id: Annotated[int | None, Depends(_usuario_id_opcional)],
) -> int:
    if usuario_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Faça login para continuar")
    return usuario_id


UsuarioIdOpcional = Annotated[int | None, Depends(_usuario_id_opcional)]
UsuarioId = Annotated[int, Depends(_usuario_id_obrigatorio)]
