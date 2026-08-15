"""
Cofre de QRs estáveis.

Os QRs são gerados UMA vez a partir da URL pública salva e ficam na pasta
`qr-codes/` (ao lado do .exe). Só regeneram se o usuário renovar o link.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from config import app_data_dir, exe_dir
from ui.qrutil import save_qr_png
from ui.theme import ORG_SHORT


def qr_dir() -> Path:
    path = exe_dir() / "qr-codes"
    try:
        path.mkdir(parents=True, exist_ok=True)
        # teste de escrita
        probe = path / ".ok"
        probe.write_text("1", encoding="utf-8")
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


def consulta_url(base: str) -> str:
    return base.rstrip("/") + "/consulta"


def lista_url(base: str) -> str:
    return base.rstrip("/") + "/lista"


def pessoa_url(base: str, person_id: str) -> str:
    return base.rstrip("/") + f"/p/{person_id}"


def ensure_stable_qrs(
    base_url: str,
    *,
    pessoas: Optional[Iterable] = None,
    force: bool = False,
) -> dict:
    """
    Garante QRs estáveis para consulta (principal), lista e cada sócio.
    Retorna o manifesto.
    """
    base = base_url.rstrip("/")
    manifest = load_manifest()
    same_base = manifest.get("base_url") == base

    if same_base and not force and (qr_dir() / "consulta.png").exists():
        # Atualiza sócios novos sem mudar QRs existentes
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

    # Regenera pacote completo (primeira vez ou base mudou / force)
    save_qr_png(
        consulta_url(base),
        qr_dir() / "consulta.png",
        title=f"{ORG_SHORT} — Consulta por CPF",
        subtitle="Sócio digita o CPF e vê só o próprio REAP",
    )
    save_qr_png(
        lista_url(base),
        qr_dir() / "lista.png",
        title=f"{ORG_SHORT} — Lista pública",
        subtitle="Lista geral de associados · QR permanente",
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
