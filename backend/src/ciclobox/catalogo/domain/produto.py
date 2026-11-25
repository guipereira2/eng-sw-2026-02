from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class Pet(StrEnum):
    CAO = "cao"
    GATO = "gato"
    AMBOS = "ambos"


class Categoria(StrEnum):
    ALIMENTACAO = "Alimentação"
    PETISCOS = "Petiscos"
    BRINQUEDOS = "Brinquedos"
    HIGIENE = "Higiene"
    ACESSORIOS = "Acessórios"


@dataclass
class Produto:
    nome: str
    pet: Pet
    categoria: Categoria
    preco: Decimal
    aceita_programada: bool = False
    id: int | None = None
    """Fica `None` até o produto ser salvo no banco."""

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise ValueError("O nome do produto é obrigatório")
        if self.preco <= 0:
            raise ValueError("O preço do produto deve ser maior que zero")
