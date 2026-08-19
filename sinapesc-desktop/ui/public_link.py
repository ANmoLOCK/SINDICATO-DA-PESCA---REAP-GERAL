"""Helpers de URL pública — prioriza site estático gratuito (Opção A)."""

from __future__ import annotations

from typing import Optional

from config import load_config, save_config
from sheets import PessoaComReap
from ui.qr_vault import (
    consulta_url,
    ensure_stable_qrs,
    lista_url,
    pessoa_url,
    preferred_public_base,
)
from ui.tunnel import current_public_url


def resolve_base() -> str:
    base = preferred_public_base()
    if base:
        return base
    return (current_public_url() or "").rstrip("/")


def ensure_site_qrs(pessoas=None, force: bool = False) -> str:
    """Gera/atualiza QRs para o site público configurado. Retorna a base."""
    base = resolve_base()
    if not base:
        raise ValueError(
            "Configure a URL do site público em Configurações "
            "(ex.: https://seuusuario.github.io/SINDICATO-DA-PESCA---REAP-GERAL)."
        )
    ensure_stable_qrs(base, pessoas=pessoas, force=force)
    cfg = load_config()
    # Mantém public_base_url alinhada ao site quando site estiver definido
    if cfg.get("public_site_url"):
        cfg["public_base_url"] = str(cfg["public_site_url"]).rstrip("/")
        save_config(cfg)
    return base


def urls_for(base: str, pessoa: Optional[PessoaComReap] = None) -> dict:
    out = {
        "consulta": consulta_url(base),
        "lista": lista_url(base),
    }
    if pessoa:
        out["pessoa"] = pessoa_url(base, pessoa.id)
    return out
