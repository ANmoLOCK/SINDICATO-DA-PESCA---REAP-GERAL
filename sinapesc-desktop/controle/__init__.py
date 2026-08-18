"""
Controle de REAP (pendências, relatório, backup, auditoria).

Pacote separado da UI e da API Google: só regras e arquivos locais.
A planilha (abas Pessoas / Reap / Auditoria / Config) fica em `sheets/`.
"""

from .auditoria import EventoAuditoria, row_to_evento
from .calendario import CALENDARIO_PADRAO, meses_para_texto, normalizar_meses, parse_meses
from .pendencias import SituacaoReap, classificar, reap_do_ano

__all__ = [
    "CALENDARIO_PADRAO",
    "EventoAuditoria",
    "SituacaoReap",
    "classificar",
    "meses_para_texto",
    "normalizar_meses",
    "parse_meses",
    "reap_do_ano",
    "row_to_evento",
]
