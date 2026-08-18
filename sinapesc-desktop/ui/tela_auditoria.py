"""Tela Admin → Auditoria (lê a aba Auditoria da planilha, visível a todos os admins)."""

from __future__ import annotations

import csv
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
from typing import TYPE_CHECKING, List

from controle.auditoria import EventoAuditoria, combina_busca
from ui.scroll import ScrollableFrame
from ui.theme import COLORS, FONT_DISPLAY, FONT_FAMILY

if TYPE_CHECKING:
    from ui import SinapescApp


def show_auditoria(app: "SinapescApp") -> None:
    if not app._logged_in:
        app.show_login()
        return

    app._lista_mode = False
    app._clear_body()
    app._nav_button("Início", app.show_home)
    app._nav_button("Sócios", app.show_admin)
    app._nav_button("Sair", app._logout)

    wrap = tk.Frame(app.body, bg=COLORS["bg"])
    wrap.pack(fill="both", expand=True, padx=22, pady=14)

    top = tk.Frame(wrap, bg=COLORS["bg"])
    top.pack(fill="x", pady=(0, 8))
    tk.Label(
        top, text="Auditoria", bg=COLORS["bg"], fg=COLORS["primary"],
        font=(FONT_DISPLAY, 20, "bold"),
    ).pack(side="left")
    hint = tk.StringVar(value="Registro compartilhado na aba Auditoria da planilha.")
    tk.Label(top, textvariable=hint, bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(
        side="left", padx=12
    )

    tools = tk.Frame(wrap, bg=COLORS["bg"])
    tools.pack(fill="x", pady=(0, 8))
    tk.Label(tools, text="Buscar", bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="left")
    search_var = tk.StringVar()
    ttk.Entry(tools, textvariable=search_var, width=36).pack(side="left", padx=8)

    scroll = ScrollableFrame(wrap, bg=COLORS["bg"])
    scroll.pack(fill="both", expand=True)
    lista = scroll.inner
    app._scroll = scroll

    state: dict = {"eventos": []}

    def visiveis() -> List[EventoAuditoria]:
        return [e for e in state["eventos"] if combina_busca(e, search_var.get())]

    def render() -> None:
        for child in lista.winfo_children():
            child.destroy()
        itens = visiveis()
        hint.set(f"{len(itens)} registro(s) · aba Auditoria da planilha (todos os admins veem)")
        if not itens:
            tk.Label(lista, text="Nenhum registro ainda.", bg=COLORS["bg"], fg=COLORS["muted"]).pack(
                anchor="w", pady=20
            )
            return
        for evt in itens:
            card = tk.Frame(
                lista, bg=COLORS["surface"], padx=12, pady=8,
                highlightbackground=COLORS["border"], highlightthickness=1,
            )
            card.pack(fill="x", pady=4, padx=2)
            tk.Label(
                card,
                text=f"{evt.em}  ·  {evt.usuario or '(sem usuário)'}",
                bg=COLORS["surface"],
                fg=COLORS["accent"],
                font=(FONT_FAMILY, 8, "bold"),
                anchor="w",
            ).pack(anchor="w")
            tk.Label(
                card,
                text=evt.detalhe or evt.acao,
                bg=COLORS["surface"],
                fg=COLORS["primary"],
                font=(FONT_FAMILY, 10),
                wraplength=860,
                justify="left",
                anchor="w",
            ).pack(anchor="w")

    def recarregar() -> None:
        try:
            svc = app._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return

        def work():
            return svc.listar_auditoria(400)

        def ok(eventos) -> None:
            state["eventos"] = eventos
            render()

        app._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Carregando auditoria…")

    def exportar() -> None:
        itens = visiveis()
        if not itens:
            messagebox.showwarning("Auditoria", "Nada para exportar.")
            return
        path = filedialog.asksaveasfilename(
            title="Exportar auditoria",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="auditoria-reap.csv",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["em", "usuario", "acao", "detalhe", "nome", "ano", "meses"])
            for e in itens:
                w.writerow([e.em, e.usuario, e.acao, e.detalhe, e.nome, e.ano, e.meses])
        messagebox.showinfo("Auditoria", f"Salvo em:\n{path}")

    app._btn(tools, "Atualizar", recarregar, kind="ghost").pack(side="right", padx=4)
    app._btn(tools, "Exportar CSV desta busca", exportar, kind="ghost").pack(side="right", padx=4)

    search_var.trace_add("write", lambda *_: render())
    recarregar()
