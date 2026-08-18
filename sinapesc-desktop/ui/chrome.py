"""Chrome compartilhado — header, abas da secretaria, rodapé e navegação Voltar."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Optional

import tkinter as tk

from config import is_sheets_configured, load_config
from ui.brand import load_logo
from ui.theme import APP_VERSION, COLORS, FONT_DISPLAY, FONT_FAMILY, ORG_FULL, ORG_SHORT
from ui.widgets import header_outline_btn

if TYPE_CHECKING:
    from ui import SinapescApp

# Ordem exata do mockup aprovado (+ Auditoria após Backup)
SECRETARIA_TABS: List[tuple[str, str, str]] = [
    ("socies", "Sócios", "show_admin"),
    ("pendencias", "Pendências", "show_pendencias"),
    ("relatorio", "Relatório", "show_relatorio"),
    ("backup", "Backup", "show_backup"),
    ("auditoria", "Auditoria", "show_auditoria"),
    ("atalhos", "Config.Atalhos", "_open_atalhos_tab"),
    ("lista", "Lista pública", "show_lista"),
]

SCREEN_MODES: Dict[str, str] = {
    "home": "public",
    "login": "public",
    "settings": "public",
    "lista": "public",
    "admin": "secretaria",
    "pendencias": "secretaria",
    "relatorio": "secretaria",
    "backup": "secretaria",
    "auditoria": "secretaria",
}

TAB_FOR_SCREEN: Dict[str, str] = {
    "admin": "socies",
    "pendencias": "pendencias",
    "relatorio": "relatorio",
    "backup": "backup",
    "auditoria": "auditoria",
    "lista": "lista",
}


def build_shell(app: "SinapescApp") -> None:
    app._nav_history: List[str] = []
    app._current_screen: Optional[str] = None
    app._active_tab: Optional[str] = None
    app._tab_labels: Dict[str, tk.Label] = {}
    app._tab_underlines: Dict[str, tk.Frame] = {}

    app.header = tk.Frame(app, bg=COLORS["primary"])
    app.header.pack(fill="x")

    top = tk.Frame(app.header, bg=COLORS["primary"])
    top.pack(fill="x", padx=18, pady=(10, 8))

    brand = tk.Frame(top, bg=COLORS["primary"])
    brand.pack(side="left", fill="x", expand=True)
    app._logo_img = load_logo(app, size=56)
    if app._logo_img is not None:
        logo_wrap = tk.Frame(brand, bg=COLORS["primary"], highlightbackground="#C8D8E8", highlightthickness=1)
        logo_wrap.pack(side="left", padx=(0, 12))
        tk.Label(logo_wrap, image=app._logo_img, bg=COLORS["primary"]).pack(padx=2, pady=2)
    titles = tk.Frame(brand, bg=COLORS["primary"])
    titles.pack(side="left")
    tk.Label(
        titles, text=ORG_SHORT, bg=COLORS["primary"], fg=COLORS["primary_fg"],
        font=(FONT_DISPLAY, 15, "bold"),
    ).pack(anchor="w")
    tk.Label(
        titles, text=ORG_FULL, bg=COLORS["primary"], fg="#9CB8D0",
        font=(FONT_FAMILY, 8), wraplength=480, justify="left",
    ).pack(anchor="w", pady=(1, 0))

    app._header_right = tk.Frame(top, bg=COLORS["primary"])
    app._header_right.pack(side="right", anchor="ne")

    app._email_lbl = tk.Label(
        app._header_right, text="", bg=COLORS["primary"], fg="#9CB8D0",
        font=(FONT_FAMILY, 8), anchor="e",
    )
    app._email_lbl.pack(anchor="e", pady=(0, 6))

    app._header_actions = tk.Frame(app._header_right, bg=COLORS["primary"])
    app._header_actions.pack(anchor="e")

    app.tab_bar = tk.Frame(app.header, bg=COLORS["nav_mid"])
    app.tab_bar.pack(fill="x")
    app._tab_inner = tk.Frame(app.tab_bar, bg=COLORS["nav_mid"])
    app._tab_inner.pack(fill="x", padx=16, pady=(0, 0))

    for tab_id, label, _method in SECRETARIA_TABS:
        cell = tk.Frame(app._tab_inner, bg=COLORS["nav_mid"])
        cell.pack(side="left")
        lbl = tk.Label(
            cell, text=label, bg=COLORS["nav_mid"], fg="#9CB8D0",
            font=(FONT_FAMILY, 9), cursor="hand2", padx=10, pady=8,
        )
        lbl.pack()
        line = tk.Frame(cell, bg=COLORS["nav_mid"], height=2)
        line.pack(fill="x")
        lbl.bind("<Button-1>", lambda _e, tid=tab_id: _on_tab(app, tid))
        lbl.bind("<Enter>", lambda _e, w=lbl, tid=tab_id: _hover_tab(w, tid, app._active_tab, True))
        lbl.bind("<Leave>", lambda _e, w=lbl, tid=tab_id: _hover_tab(w, tid, app._active_tab, False))
        app._tab_labels[tab_id] = lbl
        app._tab_underlines[tab_id] = line

    app.body = tk.Frame(app, bg=COLORS["content"])
    app.body.pack(fill="both", expand=True)

    app.footer = tk.Frame(
        app, bg=COLORS["surface"],
        highlightbackground=COLORS["border_soft"], highlightthickness=1,
    )
    app.footer.pack(fill="x", side="bottom")

    foot_left = tk.Frame(app.footer, bg=COLORS["surface"])
    foot_left.pack(side="left", fill="x", expand=True, padx=16, pady=7)
    app.status = tk.StringVar(value="Pronto.")
    tk.Label(
        foot_left, textvariable=app.status, bg=COLORS["surface"], fg=COLORS["muted"],
        font=(FONT_FAMILY, 9),
    ).pack(side="left")
    app._footer_user = tk.StringVar(value="")
    tk.Label(
        foot_left, text="·", bg=COLORS["surface"], fg=COLORS["border"], font=(FONT_FAMILY, 9),
    ).pack(side="left", padx=6)
    tk.Label(
        foot_left, textvariable=app._footer_user, bg=COLORS["surface"], fg=COLORS["muted"],
        font=(FONT_FAMILY, 9),
    ).pack(side="left")
    app._footer_conn = tk.StringVar(value="")
    tk.Label(
        foot_left, text="·", bg=COLORS["surface"], fg=COLORS["border"], font=(FONT_FAMILY, 9),
    ).pack(side="left", padx=6)
    tk.Label(
        foot_left, textvariable=app._footer_conn, bg=COLORS["surface"], fg=COLORS["muted"],
        font=(FONT_FAMILY, 9),
    ).pack(side="left")

    foot_right = tk.Frame(app.footer, bg=COLORS["surface"])
    foot_right.pack(side="right", padx=16, pady=7)
    tk.Label(
        foot_right, text="Sinapesc REAP", bg=COLORS["surface"], fg=COLORS["primary"],
        font=(FONT_DISPLAY, 9, "bold"),
    ).pack(side="left")

    sync_chrome(app, "public")


def _hover_tab(lbl: tk.Label, tab_id: str, active: Optional[str], entering: bool) -> None:
    if tab_id == active:
        return
    lbl.configure(fg=COLORS["primary_fg"] if entering else "#9CB8D0")


def _clear_header_actions(app: "SinapescApp") -> None:
    for child in app._header_actions.winfo_children():
        child.destroy()


def _paint_tab(app: "SinapescApp", tab_id: str, active: bool) -> None:
    lbl = app._tab_labels[tab_id]
    line = app._tab_underlines[tab_id]
    if active:
        lbl.configure(fg=COLORS["primary_fg"], font=(FONT_FAMILY, 9, "bold"))
        line.configure(bg=COLORS["primary_fg"])
    else:
        lbl.configure(fg="#9CB8D0", font=(FONT_FAMILY, 9))
        line.configure(bg=COLORS["nav_mid"])


def _highlight_tab(app: "SinapescApp", tab_id: Optional[str]) -> None:
    app._active_tab = tab_id
    for tid in app._tab_labels:
        _paint_tab(app, tid, tid == tab_id)


def _on_tab(app: "SinapescApp", tab_id: str) -> None:
    for tid, _label, method in SECRETARIA_TABS:
        if tid != tab_id:
            continue
        if method == "_open_atalhos_tab":
            prev = app._active_tab
            _highlight_tab(app, "atalhos")
            app._dialog_atalhos()
            _highlight_tab(app, prev or "socies")
            return
        if method == "show_lista":
            navigate(app, "lista")
            return
        navigate(app, _screen_for_tab(tab_id))
        return


def _screen_for_tab(tab_id: str) -> str:
    return {
        "socies": "admin",
        "pendencias": "pendencias",
        "relatorio": "relatorio",
        "backup": "backup",
        "auditoria": "auditoria",
    }[tab_id]


def _dispatch(app: "SinapescApp", screen_id: str) -> None:
    routes = {
        "home": app._render_home,
        "login": app._render_login,
        "settings": app._render_settings,
        "lista": app._render_lista,
        "admin": app._render_admin,
        "pendencias": app._render_pendencias,
        "relatorio": app._render_relatorio,
        "backup": app._render_backup,
        "auditoria": app._render_auditoria,
    }
    fn = routes.get(screen_id)
    if fn is None:
        raise ValueError(f"Tela desconhecida: {screen_id}")
    fn()


def clear_body(app: "SinapescApp") -> None:
    if app._scroll is not None:
        try:
            app._scroll.destroy()
        except tk.TclError:
            pass
        app._scroll = None
    for child in app.body.winfo_children():
        child.destroy()


def sync_chrome(app: "SinapescApp", mode: str, *, active_tab: Optional[str] = None) -> None:
    if app._current_screen == "lista" and app._logged_in:
        mode = "secretaria"
        active_tab = active_tab or "lista"

    _clear_header_actions(app)

    if app._logged_in and app._admin_user:
        app._email_lbl.configure(text=app._admin_user)
    else:
        app._email_lbl.configure(text="")

    cfg = load_config()
    if app._logged_in:
        user = app._admin_user or str(cfg.get("admin_email") or "admin")
        app._footer_user.set(f"Usuário: {user}")
        conn = "Conectado" if is_sheets_configured(cfg) else "Desconectado"
        app._footer_conn.set(conn)
    else:
        app._footer_user.set("")
        app._footer_conn.set("")

    if mode == "secretaria":
        app.tab_bar.pack(fill="x")
        tab = active_tab or app._active_tab or "socies"
        _highlight_tab(app, tab)
        header_outline_btn(app._header_actions, "← Voltar", lambda: go_back(app)).pack(side="left", padx=(0, 5))
        header_outline_btn(app._header_actions, "Lista pública", lambda: navigate(app, "lista")).pack(side="left", padx=3)
        header_outline_btn(app._header_actions, "⚙ Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)
        header_outline_btn(app._header_actions, "Sair", app._logout).pack(side="left", padx=3)
    elif mode == "public":
        app.tab_bar.pack_forget()
        _highlight_tab(app, None)
        header_outline_btn(app._header_actions, "← Voltar", lambda: go_back(app)).pack(side="left", padx=(0, 5))
        header_outline_btn(app._header_actions, "Lista pública", lambda: navigate(app, "lista")).pack(side="left", padx=3)
        if not app._logged_in:
            header_outline_btn(app._header_actions, "⚙ Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)
        else:
            header_outline_btn(app._header_actions, "Secretaria", lambda: navigate(app, "admin")).pack(side="left", padx=3)
            header_outline_btn(app._header_actions, "⚙ Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)
            header_outline_btn(app._header_actions, "Sair", app._logout).pack(side="left", padx=3)
    else:
        app.tab_bar.pack_forget()
        _highlight_tab(app, None)
        header_outline_btn(app._header_actions, "⚙ Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)


def navigate(app: "SinapescApp", screen_id: str, *, push: bool = True) -> None:
    if screen_id in ("admin", "pendencias", "relatorio", "backup", "auditoria") and not app._logged_in:
        navigate(app, "login", push=push)
        return

    cur = app._current_screen
    if cur == screen_id:
        sync_chrome(app, SCREEN_MODES.get(screen_id, "public"), active_tab=TAB_FOR_SCREEN.get(screen_id))
        return

    if push and cur:
        app._nav_history.append(cur)

    app._current_screen = screen_id
    clear_body(app)
    mode = SCREEN_MODES.get(screen_id, "public")
    sync_chrome(app, mode, active_tab=TAB_FOR_SCREEN.get(screen_id))
    _dispatch(app, screen_id)


def go_back(app: "SinapescApp") -> None:
    if app._nav_history:
        prev = app._nav_history.pop()
        app._current_screen = None
        navigate(app, prev, push=False)
        return
    if app._logged_in:
        navigate(app, "admin", push=False)
    else:
        navigate(app, "home", push=False)


def page_wrap(app: "SinapescApp", *, padx: int = 28, pady: int = 18) -> tk.Frame:
    wrap = tk.Frame(app.body, bg=COLORS["content"])
    wrap.pack(fill="both", expand=True, padx=padx, pady=pady)
    return wrap
