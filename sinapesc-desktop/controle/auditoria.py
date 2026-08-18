"""Formato da aba Auditoria (sem chamar a API)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


AUDITORIA_COLUNAS = [
    "id",
    "em",
    "usuario",
    "acao",
    "detalhe",
    "personId",
    "nome",
    "ano",
    "meses",
]


@dataclass(frozen=True)
class EventoAuditoria:
    id: str
    em: str
    usuario: str
    acao: str
    detalhe: str
    person_id: str = ""
    nome: str = ""
    ano: str = ""
    meses: str = ""


def row_to_evento(row: Sequence[str] | None) -> EventoAuditoria | None:
    if not row:
        return None
    cells = [str(c) if c is not None else "" for c in row]
    while len(cells) < 9:
        cells.append("")
    eid = cells[0].strip()
    if not eid or eid.lower() == "id":
        return None
    return EventoAuditoria(
        id=eid,
        em=cells[1].strip(),
        usuario=cells[2].strip(),
        acao=cells[3].strip(),
        detalhe=cells[4].strip(),
        person_id=cells[5].strip(),
        nome=cells[6].strip(),
        ano=cells[7].strip(),
        meses=cells[8].strip(),
    )


def evento_para_row(evt: EventoAuditoria) -> List[str]:
    return [
        evt.id,
        evt.em,
        evt.usuario,
        evt.acao,
        evt.detalhe,
        evt.person_id,
        evt.nome,
        evt.ano,
        evt.meses,
    ]


def combina_busca(evt: EventoAuditoria, query: str) -> bool:
    q = (query or "").strip().lower()
    if not q:
        return True
    blob = " ".join(
        [evt.em, evt.usuario, evt.acao, evt.detalhe, evt.nome, evt.ano, evt.meses]
    ).lower()
    return q in blob
