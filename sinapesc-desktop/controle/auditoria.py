"""Formato da aba Auditoria (sem chamar a API)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence


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


def parse_em(valor: str) -> Optional[datetime]:
    s = (valor or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:19], fmt)
        except ValueError:
            continue
    return None


def format_tempo_desde(valor: str, *, agora: Optional[datetime] = None) -> str:
    """Ex.: 1min atrás · 4h atrás · 14d · 1ano15d"""
    dt = parse_em(valor)
    if not dt:
        return ""
    agora = agora or datetime.now()
    secs = max(0, int((agora - dt).total_seconds()))
    if secs < 45:
        return "agora"
    mins = secs // 60
    if mins < 60:
        return f"{mins}min atrás"
    horas = secs // 3600
    if horas < 24:
        return f"{horas}h atrás"
    dias = secs // 86400
    if dias < 365:
        return f"{dias}d"
    anos = dias // 365
    resto = dias % 365
    if resto:
        return f"{anos}ano{resto}d"
    return f"{anos}ano"


def ultimo_toggle_por_pessoa(eventos: Iterable[EventoAuditoria]) -> Dict[str, Dict[str, str]]:
    """Mapa person_id → último toggle_mes (eventos já do mais recente ao mais antigo)."""
    out: Dict[str, Dict[str, str]] = {}
    for evt in eventos:
        if evt.acao != "toggle_mes":
            continue
        pid = (evt.person_id or "").strip()
        if not pid or pid in out:
            continue
        out[pid] = {
            "em": evt.em,
            "label": format_tempo_desde(evt.em),
        }
    return out
