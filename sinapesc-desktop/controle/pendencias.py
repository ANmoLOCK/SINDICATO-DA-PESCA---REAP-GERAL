"""Quem está regular / pendente no ano, segundo o calendário obrigatório."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from sheets.models import MESES, PessoaComReap, ReapAno

from .calendario import normalizar_meses


@dataclass(frozen=True)
class SituacaoReap:
    pessoa: PessoaComReap
    ano: int
    obrigatorio: List[str]
    faltando: List[str]
    tem_ano: bool

    @property
    def regular(self) -> bool:
        return not self.faltando

    @property
    def rotulo_faltando(self) -> str:
        if not self.faltando:
            return "Regular"
        if not self.tem_ano:
            return "Ano ainda não criado · falta " + " ".join(m.upper() for m in self.faltando)
        return "Falta: " + " ".join(m.upper() for m in self.faltando)


def reap_do_ano(pessoa: PessoaComReap, ano: int) -> Optional[ReapAno]:
    alvo = int(ano)
    for item in pessoa.anos or []:
        if int(item.ano) == alvo:
            return item
    return None


def meses_marcados(pessoa: PessoaComReap, ano: int) -> Dict[str, bool]:
    item = reap_do_ano(pessoa, ano)
    if item is None:
        return {m: False for m in MESES}
    return {m: bool(item.meses.get(m)) for m in MESES}


def situacao_de(
    pessoa: PessoaComReap,
    ano: int,
    obrigatorio: Sequence[str],
) -> SituacaoReap:
    obr = normalizar_meses(obrigatorio)
    item = reap_do_ano(pessoa, int(ano))
    if item is None:
        faltando = list(obr)
        tem_ano = False
    else:
        faltando = [m for m in obr if not item.meses.get(m)]
        tem_ano = True
    return SituacaoReap(
        pessoa=pessoa,
        ano=int(ano),
        obrigatorio=obr,
        faltando=faltando,
        tem_ano=tem_ano,
    )


def classificar(
    pessoas: Iterable[PessoaComReap],
    ano: int,
    obrigatorio: Sequence[str],
) -> Tuple[List[SituacaoReap], List[SituacaoReap]]:
    """Retorna (pendentes, regulares), ambos ordenados por nome."""
    pendentes: List[SituacaoReap] = []
    regulares: List[SituacaoReap] = []
    for pessoa in pessoas:
        item = situacao_de(pessoa, ano, obrigatorio)
        if item.regular:
            regulares.append(item)
        else:
            pendentes.append(item)
    pendentes.sort(key=lambda s: s.pessoa.nome.lower())
    regulares.sort(key=lambda s: s.pessoa.nome.lower())
    return pendentes, regulares
