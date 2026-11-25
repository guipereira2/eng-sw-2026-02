"""Erros que o domínio pode lançar.

Ficam aqui, sem FastAPI, para qualquer `domain/` poder usar. O `shared/http.py` transforma
cada um no status HTTP certo, com o corpo `{"detail": "<mensagem>"}`.
"""


class ErroDeDominio(Exception):
    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class DadoInvalidoError(ErroDeDominio):
    """Dado de entrada que não faz sentido para a regra (vira 422)."""


class RegraDeNegocioError(ErroDeDominio):
    """A regra de negócio impede a ação no estado atual (vira 409)."""


class NaoEncontradoError(ErroDeDominio):
    """O recurso não existe ou não é do usuário (vira 404)."""
