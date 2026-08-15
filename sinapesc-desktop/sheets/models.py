"""Modelos de dados do Sinapesc (equivalente ao lib/types.ts da versão web)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

MesKey = Literal[
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
]

MESES: List[MesKey] = [
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
]

MESES_LABEL: Dict[MesKey, str] = {
    "jan": "Janeiro",
    "fev": "Fevereiro",
    "mar": "Março",
    "abr": "Abril",
    "mai": "Maio",
    "jun": "Junho",
    "jul": "Julho",
    "ago": "Agosto",
    "set": "Setembro",
    "out": "Outubro",
    "nov": "Novembro",
    "dez": "Dezembro",
}


@dataclass
class Pessoa:
    id: str
    nome: str
    cpf: str
    criado_em: str


@dataclass
class ReapAno:
    id: str
    person_id: str
    ano: int
    meses: Dict[MesKey, bool]
    atualizado_em: str


@dataclass
class PessoaComReap(Pessoa):
    anos: List[ReapAno] = field(default_factory=list)


def meses_vazios() -> Dict[MesKey, bool]:
    return {mes: False for mes in MESES}
