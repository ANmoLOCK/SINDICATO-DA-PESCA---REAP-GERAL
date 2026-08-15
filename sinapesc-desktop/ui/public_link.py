"""Ativação do link público estável + cofre de QRs."""

from __future__ import annotations

import urllib.error
import urllib.request
from typing import Callable, List, Optional, Tuple

from config import load_config, save_config
from sheets import PessoaComReap
from ui.public_web import public_base_url, start_public_server
from ui.qr_vault import consulta_url, ensure_stable_qrs, lista_url, pessoa_url
from ui.tunnel import current_public_url, is_tunnel_running, start_tunnel


def _url_alive(url: str, timeout: float = 4.0) -> bool:
    try:
        req = urllib.request.Request(url.rstrip("/") + "/consulta", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= getattr(resp, "status", 200) < 500
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return False


def activate_public_link(
    *,
    fetch_pessoas: Callable[[], List[PessoaComReap]],
    force_new: bool = False,
    progress: Optional[Callable[[str], None]] = None,
    pessoas: Optional[List[PessoaComReap]] = None,
) -> Tuple[str, bool]:
    """
    Garante servidor local + túnel + QRs estáveis.
    Retorna (base_url, url_mudou).

    Estratégia eficaz:
    - Se já existe URL salva e ela ainda responde, REUTILIZA (QR impresso ok).
    - Só cria túnel novo se forçado ou se o link antigo morreu.
    """
    cfg = load_config()
    port = int(cfg.get("public_port") or 8765)
    start_public_server(fetch_pessoas, port=port)

    saved = str(cfg.get("public_base_url") or "").strip().rstrip("/")
    url_mudou = False

    if not force_new and saved:
        if progress:
            progress("Verificando link público salvo…")
        if is_tunnel_running() or _url_alive(saved):
            if progress:
                progress(f"Link estável reutilizado: {saved}")
            ensure_stable_qrs(saved, pessoas=pessoas, force=False)
            return saved, False

    # Precisa (re)criar túnel
    url, _created = start_tunnel(
        port,
        progress=progress,
        force_new=True,
    )
    url = url.rstrip("/")
    if url != saved:
        url_mudou = True
    cfg["public_base_url"] = url
    save_config(cfg)

    ensure_stable_qrs(url, pessoas=pessoas, force=True)
    return url, url_mudou or True


def resolve_base() -> str:
    cfg = load_config()
    return public_base_url(str(cfg.get("public_base_url") or current_public_url() or ""))


def urls_for(base: str, pessoa: Optional[PessoaComReap] = None) -> dict:
    out = {
        "consulta": consulta_url(base),
        "lista": lista_url(base),
    }
    if pessoa:
        out["pessoa"] = pessoa_url(base, pessoa.id)
    return out
