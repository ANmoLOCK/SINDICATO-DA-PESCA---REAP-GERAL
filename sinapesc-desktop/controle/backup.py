"""Cópia local CSV das abas Pessoas + Reap (não restaura sozinho na planilha)."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Sequence

from config import app_data_dir, exe_dir

KEEP_LAST = 12
STAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{4}$")


def backup_root() -> Path:
    """Pasta backups/ ao lado do EXE; se não der, AppData."""
    try:
        path = exe_dir() / "backups"
        path.mkdir(parents=True, exist_ok=True)
        (path / ".ok").write_text("1", encoding="utf-8")
        return path
    except OSError:
        path = app_data_dir() / "backups"
        path.mkdir(parents=True, exist_ok=True)
        return path


def novo_stamp(agora: datetime | None = None) -> str:
    agora = agora or datetime.now()
    return agora.strftime("%Y-%m-%d_%H%M")


def _escrever_csv(path: Path, rows: Sequence[Sequence[object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        for row in rows:
            writer.writerow(["" if c is None else str(c) for c in row])


def gravar_backup(
    *,
    pessoas_rows: Sequence[Sequence[object]],
    reap_rows: Sequence[Sequence[object]],
    spreadsheet_id: str = "",
    stamp: str | None = None,
    root: Path | None = None,
) -> Path:
    """
    Cria backups/<stamp>/Pessoas.csv + Reap.csv + meta.json.
    Devolve a pasta criada.
    """
    stamp = stamp or novo_stamp()
    dest = (root or backup_root()) / stamp
    dest.mkdir(parents=True, exist_ok=True)
    _escrever_csv(dest / "Pessoas.csv", pessoas_rows)
    _escrever_csv(dest / "Reap.csv", reap_rows)
    meta = {
        "em": datetime.now().isoformat(timespec="seconds"),
        "stamp": stamp,
        "spreadsheet_id": spreadsheet_id,
        "pessoas_linhas": len(pessoas_rows),
        "reap_linhas": len(reap_rows),
    }
    (dest / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    prune_old_backups(root=root or dest.parent)
    return dest


def listar_backups(root: Path | None = None) -> List[Path]:
    base = root or backup_root()
    if not base.exists():
        return []
    dirs = [p for p in base.iterdir() if p.is_dir() and STAMP_RE.match(p.name)]
    dirs.sort(key=lambda p: p.name, reverse=True)
    return dirs


def prune_old_backups(keep: int = KEEP_LAST, root: Path | None = None) -> None:
    import shutil

    extras = listar_backups(root)[max(keep, 1) :]
    for folder in extras:
        shutil.rmtree(folder, ignore_errors=True)


def dias_desde(iso_ou_stamp: str) -> float | None:
    """Dias desde último backup (config ISO ou nome da pasta)."""
    raw = (iso_ou_stamp or "").strip()
    if not raw:
        return None
    agora = datetime.now()
    if STAMP_RE.match(raw):
        try:
            dt = datetime.strptime(raw, "%Y-%m-%d_%H%M")
            return (agora - dt).total_seconds() / 86400.0
        except ValueError:
            return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return (agora - dt).total_seconds() / 86400.0
    except ValueError:
        return None
