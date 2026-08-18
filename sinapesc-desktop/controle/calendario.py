"""Calendário REAP do ano: quais meses são obrigatórios (ex.: mar–out)."""

from __future__ import annotations

from typing import Iterable, List, Sequence

from sheets.models import MESES, meses_no_intervalo

# Safra típica do sindicato — usado se a aba Config ainda não tiver valor.
CALENDARIO_PADRAO: List[str] = list(meses_no_intervalo("mar", "out"))


def normalizar_meses(meses: Iterable[str] | None) -> List[str]:
    """Mantém só chaves válidas, na ordem jan…dez, sem repetir."""
    ligados = {str(m).strip().lower()[:3] for m in (meses or [])}
    return [m for m in MESES if m in ligados]


def parse_meses(raw: str | Sequence[str] | None) -> List[str]:
    """Aceita 'mar,abr,mai' ou lista ['mar','abr']."""
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return normalizar_meses(raw)
    parts = str(raw).replace(";", ",").replace(" ", ",").split(",")
    return normalizar_meses(parts)


def meses_para_texto(meses: Iterable[str] | None) -> str:
    nomes = normalizar_meses(meses)
    if not nomes:
        return "(nenhum mês)"
    if nomes == list(MESES):
        return "ano inteiro (jan–dez)"
    if nomes == CALENDARIO_PADRAO:
        return "MAR → OUT"
    return " ".join(m.upper() for m in nomes)


def chave_calendario(ano: int | None = None) -> str:
    if ano is None:
        return "calendario_padrao"
    return f"calendario_{int(ano)}"
