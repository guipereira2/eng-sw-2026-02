from sqlalchemy.orm import Session

from ciclobox.pedidos.adapters.models import CompraProgramadaModel
from ciclobox.pedidos.domain.compra_programada import CompraProgramada, StatusCompraProgramada


class SqlAlchemyCompraProgramadaRepository:
    """Implementa `ciclobox.pedidos.ports.CompraProgramadaRepository` com Postgres.

    Por enquanto só cria. Buscar, listar e alterar entram com as HU16 a HU18.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def salvar(self, compra: CompraProgramada) -> CompraProgramada:
        model = CompraProgramadaModel(
            id=compra.id,
            usuario_id=compra.usuario_id,
            produto_id=compra.produto_id,
            pedido_origem_id=compra.pedido_origem_id,
            nome_produto=compra.nome_produto,
            quantidade=compra.quantidade,
            frequencia_dias=compra.frequencia_dias,
            status=compra.status.value,
            proxima_entrega=compra.proxima_entrega,
        )
        model = self._session.merge(model)
        self._session.flush()
        return _para_entidade(model)


def _para_entidade(model: CompraProgramadaModel) -> CompraProgramada:
    return CompraProgramada(
        id=model.id,
        usuario_id=model.usuario_id,
        produto_id=model.produto_id,
        pedido_origem_id=model.pedido_origem_id,
        nome_produto=model.nome_produto,
        quantidade=model.quantidade,
        frequencia_dias=model.frequencia_dias,
        status=StatusCompraProgramada(model.status),
        proxima_entrega=model.proxima_entrega,
    )
