"""Ligações de pedidos com outros módulos, sempre pela fachada deles."""

from collections.abc import Iterable

from sqlalchemy.orm import Session

from ciclobox.catalogo import facade as catalogo
from ciclobox.pedidos.domain.carrinho import ProdutoParaVenda


class CatalogoViaFachada:
    """Implementa `ciclobox.pedidos.ports.CatalogoPort` chamando a fachada do catálogo."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def buscar_produtos(self, produto_ids: Iterable[int]) -> dict[int, ProdutoParaVenda]:
        return {
            produto_id: ProdutoParaVenda(
                id=produto.id,
                nome=produto.nome,
                preco=produto.preco,
                aceita_programada=produto.aceita_programada,
            )
            for produto_id, produto in catalogo.buscar_produtos(self._session, produto_ids).items()
        }


class ClubeProvisorio:
    """Implementa `ciclobox.pedidos.ports.ClubePort` enquanto `assinaturas` não tem `eh_membro`.

    PROVISÓRIO: ninguém é membro, então o desconto de 10% e o frete grátis de membro nunca
    se aplicam pela API. Quando a HU06 publicar `assinaturas.facade.eh_membro`, trocar por
    uma classe que chame a fachada, como o `CatalogoViaFachada`.
    """

    def eh_membro(self, usuario_id: int) -> bool:
        return False
