"""Backup CSV local + lembrete semanal (não restaura a planilha sozinho)."""

from __future__ import annotations

import os
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from typing import TYPE_CHECKING

from config import load_config, save_config
from controle.backup import backup_root, dias_desde, gravar_backup, listar_backups

from ui.theme import COLORS, FONT_DISPLAY, FONT_FAMILY

if TYPE_CHECKING:
    from ui import SinapescApp


def render_backup(app: "SinapescApp") -> None:
    from ui.chrome import page_wrap

    wrap = page_wrap(app)
    tk.Label(
        wrap, text="Backup local", bg=COLORS["content"], fg=COLORS["primary"],
        font=(FONT_DISPLAY, 20, "bold"),
    ).pack(anchor="w")
    tk.Label(
        wrap,
        text="Cópia CSV das abas Pessoas e Reap neste computador. Não substitui a planilha na nuvem.",
        bg=COLORS["content"],
        fg=COLORS["muted"],
        font=(FONT_FAMILY, 10),
        wraplength=720,
        justify="left",
    ).pack(anchor="w", pady=(4, 16))

    cfg = load_config()
    ultimo = str(cfg.get("ultimo_backup_em") or "Nunca")
    info = tk.Frame(wrap, bg=COLORS["surface"], padx=16, pady=14, highlightbackground=COLORS["border"], highlightthickness=1)
    info.pack(fill="x", pady=(0, 12))
    tk.Label(info, text=f"Último backup: {ultimo}", bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_FAMILY, 10)).pack(anchor="w")
    pasta = str(backup_root())
    tk.Label(info, text=f"Pasta: {pasta}", bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(4, 0))

    btns = tk.Frame(wrap, bg=COLORS["content"])
    btns.pack(anchor="w")
    app._btn(btns, "Gerar backup agora", lambda: pedir_backup_agora(app), kind="primary").pack(side="left", padx=(0, 8))
    app._btn(btns, "Abrir pasta de backups", lambda: abrir_pasta_backups(), kind="outline").pack(side="left")

    recentes = listar_backups()
    if recentes:
        tk.Label(wrap, text="Backups recentes", bg=COLORS["content"], fg=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(16, 6))
        for path in recentes[:8]:
            tk.Label(wrap, text=path.name, bg=COLORS["content"], fg=COLORS["primary"], font=(FONT_FAMILY, 9)).pack(anchor="w")


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
        if getattr(app, "_current_screen", None) == "backup":
            from ui.chrome import navigate

            app.after(50, lambda: navigate(app, "backup", push=False))
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
