"""Backup CSV local + lembrete semanal (não restaura a planilha sozinho)."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime
from tkinter import messagebox
from typing import TYPE_CHECKING

from config import load_config, save_config
from controle.backup import backup_root, dias_desde, gravar_backup, listar_backups

if TYPE_CHECKING:
    from ui import SinapescApp


DIAS_SEMANA = 7.0


def executar_backup(app: "SinapescApp", *, silencioso: bool = False) -> None:
    try:
        svc = app._ensure_service()
    except Exception as exc:  # noqa: BLE001
        if not silencioso:
            messagebox.showerror("Backup", str(exc))
        return

    def work():
        dados = svc.exportar_abas()
        pasta = gravar_backup(
            pessoas_rows=dados["pessoas"],
            reap_rows=dados["reap"],
            spreadsheet_id=str(svc.client.spreadsheet_id),
        )
        svc.registrar_evento("backup", f"gerou backup local {pasta.name}")
        return str(pasta)

    def ok(pasta: str) -> None:
        cfg = load_config()
        cfg["ultimo_backup_em"] = datetime.now().isoformat(timespec="seconds")
        cfg["backup_adiado_em"] = ""
        save_config(cfg)
        app.cfg = cfg
        if silencioso:
            app.status.set(f"Backup ok: {pasta}")
            return
        abrir = messagebox.askyesno("Backup", f"Cópia salva em:\n{pasta}\n\nAbrir a pasta?")
        if abrir:
            _abrir_pasta(pasta)

    def err(exc: Exception) -> None:
        if not silencioso:
            messagebox.showerror("Backup", str(exc))

    app._run_bg(work, ok, err, "Gerando backup CSV…")


def pedir_backup_agora(app: "SinapescApp") -> None:
    if not messagebox.askyesno("Backup", "Copiar as abas Pessoas e Reap para CSV neste computador?"):
        return
    executar_backup(app, silencioso=False)


def talvez_lembrar_backup(app: "SinapescApp") -> None:
    """Chamado após entrar no Admin. Não bloqueia se já houver operação."""
    if getattr(app, "_bg_busy", False):
        return
    cfg = load_config()
    ultimo = str(cfg.get("ultimo_backup_em") or "")
    adiado = str(cfg.get("backup_adiado_em") or "")
    dias = dias_desde(ultimo)
    if not ultimo:
        existentes = listar_backups()
        if existentes:
            dias = dias_desde(existentes[0].name)
    if dias is not None and dias < DIAS_SEMANA:
        return
    dias_adiado = dias_desde(adiado)
    if dias_adiado is not None and dias_adiado < 1:
        return
    txt = "Ainda não há backup local." if dias is None else f"O último backup foi há {int(dias)} dia(s)."
    if not messagebox.askyesno(
        "Backup semanal",
        txt + "\n\nGerar agora uma cópia CSV das abas Pessoas e Reap neste computador?",
    ):
        cfg["backup_adiado_em"] = datetime.now().isoformat(timespec="seconds")
        save_config(cfg)
        return
    executar_backup(app, silencioso=False)


def _abrir_pasta(path: str) -> None:
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", path])


def abrir_pasta_backups() -> None:
    _abrir_pasta(str(backup_root()))
