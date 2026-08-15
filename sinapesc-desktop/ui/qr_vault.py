"""
Cofre de QRs estáveis apontando para o site público (Opção A).

Prioridade da URL base:
1) public_site_url  → site gratuito fixo (GitHub Pages / Cloudflare)
2) public_base_url  → túnel (legado)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from config import app_data_dir, exe_dir, load_config
from ui.qrutil import save_qr_png
from ui.theme import ORG_SHORT


def qr_dir() -> Path:
    path = exe_dir() / "qr-codes"
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / ".ok").write_text("1", encoding="utf-8")
        return path
    except OSError:
        path = app_data_dir() / "qr-codes"
        path.mkdir(parents=True, exist_ok=True)
        return path


def meta_path() -> Path:
    return qr_dir() / "manifest.json"


def load_manifest() -> dict:
    p = meta_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_manifest(data: dict) -> None:
    meta_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_public_base(url: str) -> str:
    """
    Aceita a raiz do site OU links colados com /consulta.html etc.
    Ex.: https://anmolock.github.io/sinapesc-casanova-reap/consulta.html
      → https://anmolock.github.io/sinapesc-casanova-reap
    """
    base = (url or "").strip()
    if not base:
        return ""
    # remove query/fragment acidentais
    base = base.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    for suffix in (
        "/consulta.html",
        "/lista.html",
        "/pessoa.html",
        "/index.html",
        "/consulta",
        "/lista",
    ):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)].rstrip("/")
            break
    return base


def preferred_public_base() -> str:
    cfg = load_config()
    site = normalize_public_base(str(cfg.get("public_site_url") or ""))
    if site:
        return site
    return normalize_public_base(str(cfg.get("public_base_url") or ""))


def _is_static_site(base: str) -> bool:
    """Site estático (Opção A) usa *.html; servidor local do EXE usa rotas /consulta."""
    base = normalize_public_base(base)
    cfg = load_config()
    site = preferred_public_base()
    if site and base == site:
        return True
    markers = ("github.io", "pages.dev", "netlify.app", "site-publico", "cloudflare")
    return any(m in base for m in markers)


def consulta_url(base: str) -> str:
    base = normalize_public_base(base)
    if base.endswith(".html"):
        return base
    if _is_static_site(base):
        return base + "/consulta.html"
    return base + "/consulta"


def lista_url(base: str) -> str:
    base = normalize_public_base(base)
    if _is_static_site(base):
        return base + "/lista.html"
    return base + "/lista"


def pessoa_url(base: str, person_id: str) -> str:
    base = normalize_public_base(base)
    if _is_static_site(base):
        return base + f"/pessoa.html?id={person_id}"
    return base + f"/p/{person_id}"


def ensure_stable_qrs(
    base_url: str,
    *,
    pessoas: Optional[Iterable] = None,
    force: bool = False,
) -> dict:
    base = base_url.rstrip("/")
    manifest = load_manifest()
    same_base = manifest.get("base_url") == base

    if same_base and not force and (qr_dir() / "consulta.png").exists():
        if pessoas:
            files = dict(manifest.get("pessoas") or {})
            changed = False
            for p in pessoas:
                pid = getattr(p, "id", None) or p.get("id")
                nome = getattr(p, "nome", None) or p.get("nome", "")
                if not pid:
                    continue
                fname = f"pessoa-{pid}.png"
                if fname not in files or not (qr_dir() / fname).exists():
                    save_qr_png(
                        pessoa_url(base, pid),
                        qr_dir() / fname,
                        title=f"{ORG_SHORT} — {nome}",
                        subtitle="Comprovante individual · QR permanente",
                    )
                    files[fname] = {"id": pid, "nome": nome, "url": pessoa_url(base, pid)}
                    changed = True
            if changed:
                manifest["pessoas"] = files
                save_manifest(manifest)
        return manifest

    save_qr_png(
        consulta_url(base),
        qr_dir() / "consulta.png",
        title=f"{ORG_SHORT} — Consulta por CPF",
        subtitle="Site público online · digite o CPF",
    )
    save_qr_png(
        lista_url(base),
        qr_dir() / "lista.png",
        title=f"{ORG_SHORT} — Lista pública",
        subtitle="Lista geral online · QR permanente",
    )

    files = {}
    if pessoas:
        for p in pessoas:
            pid = getattr(p, "id", None) or p.get("id")
            nome = getattr(p, "nome", None) or p.get("nome", "")
            if not pid:
                continue
            fname = f"pessoa-{pid}.png"
            save_qr_png(
                pessoa_url(base, pid),
                qr_dir() / fname,
                title=f"{ORG_SHORT} — {nome}",
                subtitle="Comprovante individual · QR permanente",
            )
            files[fname] = {"id": pid, "nome": nome, "url": pessoa_url(base, pid)}

    manifest = {
        "base_url": base,
        "consulta": {"file": "consulta.png", "url": consulta_url(base)},
        "lista": {"file": "lista.png", "url": lista_url(base)},
        "pessoas": files,
    }
    save_manifest(manifest)
    return manifest


def path_for_consulta() -> Path:
    return qr_dir() / "consulta.png"


def path_for_lista() -> Path:
    return qr_dir() / "lista.png"


def path_for_pessoa(person_id: str) -> Path:
    return qr_dir() / f"pessoa-{person_id}.png"
