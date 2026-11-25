from sqlalchemy import select
from sqlalchemy.orm import Session

from ciclobox.pedidos.adapters.models import ItemPedidoModel, PedidoModel
from ciclobox.pedidos.domain.pedido import FormaPagamento, ItemPedido, Pedido, StatusPedido
from ciclobox.pedidos.domain.totais import Totais


class SqlAlchemyPedidoRepository:
    """Implementa `ciclobox.pedidos.ports.PedidoRepository` com Postgres."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def salvar(self, pedido: Pedido) -> Pedido:
        if pedido.id is None:
            model = _novo_model(pedido)
            self._session.add(model)
        else:
            # Depois de criado, o pedido só muda de status.
            model = self._session.get_one(PedidoModel, pedido.id)
            model.status = pedido.status.value
        self._session.flush()
        return _para_entidade(model)

    def buscar_por_id(self, pedido_id: int) -> Pedido | None:
        model = self._session.get(PedidoModel, pedido_id)
        return _para_entidade(model) if model else None

    def listar_do_usuario(self, usuario_id: int) -> list[Pedido]:
        consulta = (
            select(PedidoModel)
            .where(PedidoModel.usuario_id == usuario_id)
            .order_by(PedidoModel.criado_em.desc(), PedidoModel.id.desc())
        )
        return [_para_entidade(model) for model in self._session.scalars(consulta)]


def _novo_model(pedido: Pedido) -> PedidoModel:
    return PedidoModel(
        usuario_id=pedido.usuario_id,
        status=pedido.status.value,
        cep=pedido.cep,
        forma_pagamento=pedido.forma_pagamento.value,
        subtotal=pedido.totais.subtotal,
        desconto_programada=pedido.totais.desconto_programada,
        desconto_membro=pedido.totais.desconto_membro,
        frete=pedido.totais.frete,
        total=pedido.totais.total,
        itens=[
            ItemPedidoModel(
                produto_id=item.produto_id,
                nome_produto=item.nome_produto,
                preco_unitario=item.preco_unitario,
                quantidade=item.quantidade,
                frequencia_dias=item.frequencia_dias,
            )
            for item in pedido.itens
        ],
    )


def _para_entidade(model: PedidoModel) -> Pedido:
    return Pedido(
        id=model.id,
        usuario_id=model.usuario_id,
        status=StatusPedido(model.status),
        cep=model.cep,
        forma_pagamento=FormaPagamento(model.forma_pagamento),
        criado_em=model.criado_em,
        totais=Totais(
            subtotal=model.subtotal,
            desconto_programada=model.desconto_programada,
            desconto_membro=model.desconto_membro,
            frete=model.frete,
            total=model.total,
        ),
        itens=[
            ItemPedido(
                id=item.id,
                produto_id=item.produto_id,
                nome_produto=item.nome_produto,
                preco_unitario=item.preco_unitario,
                quantidade=item.quantidade,
                frequencia_dias=item.frequencia_dias,
            )
            for item in model.itens
        ],
    )
