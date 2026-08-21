"""Anexos Defeso — pasta local / sincronizada (Google Drive no PC)."""

from __future__ import annotations

import base64
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from drive.client import ANEXO_NOMES
from ui.formatters import only_digits


def anexos_mode(cfg: Optional[dict] = None) -> str:
    """Modo de anexos: sync (pasta Drive no PC), drive (API Shared Drive) ou local."""
    if cfg is None:
        from config import load_config

        cfg = load_config()
    if str(cfg.get("defeso_anexos_dir") or "").strip().strip('"'):
        return "sync"
    if str(cfg.get("defeso_drive_folder_id") or "").strip():
        return "drive"
    return "local"


def pasta_anexos_root(cfg: Optional[dict] = None) -> Path:
    """Pasta raiz dos anexos: config defeso_anexos_dir ou AppData/backups/defeso_anexos."""
    if cfg is None:
        from config import load_config

        cfg = load_config()
    custom = str(cfg.get("defeso_anexos_dir") or "").strip().strip('"')
    if custom:
        dest = Path(custom).expanduser()
        try:
            dest.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ValueError(
                f"Não foi possível usar a pasta de anexos Defeso:\n{dest}\n{exc}"
            ) from exc
        return dest

    from controle.backup import backup_root

    dest = backup_root() / "defeso_anexos"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def pasta_cpf(cpf: str, cfg: Optional[dict] = None) -> Path:
    digits = only_digits(cpf)
    if len(digits) != 11:
        raise ValueError("CPF inválido para pasta de anexos.")
    dest = pasta_anexos_root(cfg) / digits
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def _decode_b64(data_b64: str) -> bytes:
    payload = (data_b64 or "").strip()
    if "," in payload and payload.lower().startswith("data:"):
        payload = payload.split(",", 1)[1]
    try:
        content = base64.b64decode(payload)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Arquivo inválido (base64).") from exc
    if not content:
        raise ValueError("Arquivo vazio.")
    if len(content) > 12 * 1024 * 1024:
        raise ValueError("Arquivo maior que 12 MB.")
    return content


def _final_name(kind: str, filename: str) -> str:
    key = (kind or "").strip().lower()
    stem = ANEXO_NOMES.get(key)
    if not stem:
        raise ValueError("Tipo de anexo inválido. Use: identidade, pesca, caf.")
    raw_name = (filename or f"{stem}.pdf").strip()
    ext = ""
    if "." in raw_name:
        ext = "." + raw_name.rsplit(".", 1)[-1].lower()
    if ext not in (".pdf", ".jpg", ".jpeg", ".png", ".webp"):
        ext = ".pdf"
    return f"{stem}{ext}"


def salvar_anexo_local(
    *,
    cpf: str,
    kind: str,
    filename: str,
    data_b64: str,
    mime: str = "",
    cfg: Optional[dict] = None,
) -> Dict[str, Any]:
    if cfg is None:
        from config import load_config

        cfg = load_config()
    final_name = _final_name(kind, filename)
    content = _decode_b64(data_b64)
    folder = pasta_cpf(cpf, cfg)
    path = folder / final_name
    path.write_bytes(content)
    guessed = mime or mimetypes.guess_type(final_name)[0] or "application/octet-stream"
    sync = bool(str(cfg.get("defeso_anexos_dir") or "").strip())
    return {
        "id": "",
        "name": final_name,
        "url": "",
        "path": str(path),
        "folder_id": "",
        "kind": (kind or "").strip().lower(),
        "where": "sync" if sync else "local",
        "mime": guessed,
        "modified": datetime.now().isoformat(timespec="seconds"),
        "root": str(pasta_anexos_root(cfg)),
    }


def listar_anexos_local(cpf: str, cfg: Optional[dict] = None) -> List[Dict[str, str]]:
    if cfg is None:
        from config import load_config

        cfg = load_config()
    digits = only_digits(cpf)
    if len(digits) != 11:
        return []
    folder = pasta_anexos_root(cfg) / digits
    if not folder.exists():
        return []
    sync = bool(str(cfg.get("defeso_anexos_dir") or "").strip())
    out: List[Dict[str, str]] = []
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        out.append(
            {
                "id": "",
                "name": path.name,
                "mime": mimetypes.guess_type(path.name)[0] or "",
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(
                    timespec="seconds"
                ),
                "url": "",
                "path": str(path),
                "where": "sync" if sync else "local",
            }
        )
    return out


def is_storage_quota_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return (
        "storagequotaexceeded" in text
        or "storage quota" in text
        or "do not have storage quota" in text
        or "service accounts do not have storage quota" in text
    )
