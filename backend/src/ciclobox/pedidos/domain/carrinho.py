from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal

from ciclobox.shared.erros import DadoInvalidoError

FREQUENCIAS_PERMITIDAS = (30, 45, 60)


@dataclass(frozen=True)
class ProdutoParaVenda:
    """O que o carrinho precisa saber de um produto do catálogo."""

    id: int
    nome: str
    preco: Decimal
    aceita_programada: bool


@dataclass(frozen=True)
class ItemCarrinho:
    """Um item como o cliente mandou: só ids e quantidades."""

    produto_id: int
    quantidade: int
    frequencia_dias: int | None = None


@dataclass(frozen=True)
class LinhaDoCarrinho:
    """Um item já validado e ligado ao produto, com o preço do banco."""

    produto: ProdutoParaVenda
    quantidade: int
    frequencia_dias: int | None

    @property
    def programada(self) -> bool:
        return self.frequencia_dias is not None

    @property
    def valor(self) -> Decimal:
        return self.produto.preco * self.quantidade


def montar_linhas(
    itens: Iterable[ItemCarrinho], produtos: Mapping[int, ProdutoParaVenda]
) -> list[LinhaDoCarrinho]:
    """Valida os itens do carrinho e liga cada um ao seu produto."""
    linhas: list[LinhaDoCarrinho] = []
    for item in itens:
        produto = produtos.get(item.produto_id)
        if produto is None:
            raise DadoInvalidoError(f"Produto {item.produto_id} não encontrado")
        if item.quantidade < 1:
            raise DadoInvalidoError("A quantidade precisa ser de pelo menos 1")
        if item.frequencia_dias is not None:
            if item.frequencia_dias not in FREQUENCIAS_PERMITIDAS:
                raise DadoInvalidoError("A frequência precisa ser de 30, 45 ou 60 dias")
            if not produto.aceita_programada:
                raise DadoInvalidoError(f"{produto.nome} não aceita compra programada")
        linhas.append(LinhaDoCarrinho(produto, item.quantidade, item.frequencia_dias))

    if not linhas:
        raise DadoInvalidoError("O carrinho está vazio")
    return linhas
