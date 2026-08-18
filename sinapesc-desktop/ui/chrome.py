"""Chrome compartilhado — header, abas da secretaria, rodapé e navegação Voltar."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Optional

import tkinter as tk

from config import is_sheets_configured, load_config
from ui.brand import load_logo
from ui.theme import APP_VERSION, COLORS, FONT_DISPLAY, FONT_FAMILY, ORG_FULL, ORG_SHORT

if TYPE_CHECKING:
    from ui import SinapescApp

# Ordem das abas conforme mockup aprovado
SECRETARIA_TABS: List[tuple[str, str, str]] = [
    ("pendencias", "Pendências", "show_pendencias"),
    ("relatorio", "Relatório", "show_relatorio"),
    ("backup", "Backup", "show_backup"),
    ("auditoria", "Auditoria", "show_auditoria"),
    ("socies", "Sócios", "show_admin"),
    ("atalhos", "Config.Atalhos", "_open_atalhos_tab"),
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
}


def build_shell(app: "SinapescApp") -> None:
    """Monta header, faixa de abas, corpo e rodapé (chamado uma vez no __init__)."""
    app._nav_history: List[str] = []
    app._current_screen: Optional[str] = None
    app._active_tab: Optional[str] = None
    app._tab_labels: Dict[str, tk.Label] = {}

    app.header = tk.Frame(app, bg=COLORS["primary"])
    app.header.pack(fill="x")

    top = tk.Frame(app.header, bg=COLORS["primary"])
    top.pack(fill="x", padx=16, pady=(8, 6))

    brand = tk.Frame(top, bg=COLORS["primary"])
    brand.pack(side="left", fill="x", expand=True)
    app._logo_img = load_logo(app, size=40)
    if app._logo_img is not None:
        tk.Label(brand, image=app._logo_img, bg=COLORS["primary"]).pack(side="left", padx=(0, 10))
    titles = tk.Frame(brand, bg=COLORS["primary"])
    titles.pack(side="left")
    tk.Label(
        titles, text=ORG_SHORT, bg=COLORS["primary"], fg=COLORS["primary_fg"],
        font=(FONT_DISPLAY, 14, "bold"),
    ).pack(anchor="w")
    tk.Label(
        titles, text=ORG_FULL, bg=COLORS["primary"], fg="#9CB8D0",
        font=(FONT_FAMILY, 8), wraplength=520, justify="left",
    ).pack(anchor="w")

    app._header_right = tk.Frame(top, bg=COLORS["primary"])
    app._header_right.pack(side="right")

    app._email_lbl = tk.Label(
        app._header_right, text="", bg=COLORS["primary"], fg="#9CB8D0",
        font=(FONT_FAMILY, 8),
    )
    app._email_lbl.pack(side="left", padx=(0, 10))

    app._header_actions = tk.Frame(app._header_right, bg=COLORS["primary"])
    app._header_actions.pack(side="left")

    app.tab_bar = tk.Frame(app.header, bg=COLORS["nav_mid"])
    app.tab_bar.pack(fill="x")
    app._tab_inner = tk.Frame(app.tab_bar, bg=COLORS["nav_mid"])
    app._tab_inner.pack(fill="x", padx=12, pady=6)

    for tab_id, label, _method in SECRETARIA_TABS:
        lbl = tk.Label(
            app._tab_inner, text=label, bg=COLORS["nav_mid"], fg="#9CB8D0",
            font=(FONT_FAMILY, 9), cursor="hand2", padx=8, pady=2,
        )
        lbl.pack(side="left")
        lbl.bind("<Button-1>", lambda _e, tid=tab_id: _on_tab(app, tid))
        lbl.bind("<Enter>", lambda _e, w=lbl: w.configure(fg=COLORS["primary_fg"]))
        lbl.bind("<Leave>", lambda _e, w=lbl, tid=tab_id: _paint_tab(w, tid == app._active_tab))
        app._tab_labels[tab_id] = lbl

    app.body = tk.Frame(app, bg=COLORS["content"])
    app.body.pack(fill="both", expand=True)

    app.footer = tk.Frame(app, bg=COLORS["surface"], highlightbackground=COLORS["border_soft"], highlightthickness=1)
    app.footer.pack(fill="x", side="bottom")

    foot_left = tk.Frame(app.footer, bg=COLORS["surface"])
    foot_left.pack(side="left", fill="x", expand=True, padx=14, pady=6)
    app.status = tk.StringVar(value="Pronto.")
    tk.Label(
        foot_left, textvariable=app.status, bg=COLORS["surface"], fg=COLORS["muted"],
        font=(FONT_FAMILY, 9), anchor="w",
    ).pack(side="left")
    app._footer_user = tk.StringVar(value="")
    tk.Label(
        foot_left, textvariable=app._footer_user, bg=COLORS["surface"], fg=COLORS["muted"],
        font=(FONT_FAMILY, 9), anchor="w",
    ).pack(side="left", padx=(12, 0))

    foot_right = tk.Frame(app.footer, bg=COLORS["surface"])
    foot_right.pack(side="right", padx=14, pady=6)
    tk.Label(
        foot_right, text="Sinapesc REAP", bg=COLORS["surface"], fg=COLORS["muted"],
        font=(FONT_FAMILY, 9),
    ).pack(side="left")

    sync_chrome(app, "public")


def _header_outline_btn(parent, text: str, command: Callable) -> tk.Button:
    return tk.Button(
        parent, text=text, command=command,
        bg=COLORS["primary"], fg=COLORS["primary_fg"],
        activebackground=COLORS["primary_mid"], activeforeground=COLORS["primary_fg"],
        relief="solid", bd=1, highlightbackground="#C8D8E8", highlightcolor="#C8D8E8",
        highlightthickness=1, padx=10, pady=4,
        font=(FONT_FAMILY, 9), cursor="hand2",
    )


def _clear_header_actions(app: "SinapescApp") -> None:
    for child in app._header_actions.winfo_children():
        child.destroy()


def _paint_tab(lbl: tk.Label, active: bool) -> None:
    if active:
        lbl.configure(fg=COLORS["primary_fg"], font=(FONT_FAMILY, 9, "bold"))
    else:
        lbl.configure(fg="#9CB8D0", font=(FONT_FAMILY, 9))


def _highlight_tab(app: "SinapescApp", tab_id: Optional[str]) -> None:
    app._active_tab = tab_id
    for tid, lbl in app._tab_labels.items():
        _paint_tab(lbl, tid == tab_id)


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
        navigate(app, _screen_for_tab(tab_id))
        return


def _screen_for_tab(tab_id: str) -> str:
    mapping = {
        "socies": "admin",
        "pendencias": "pendencias",
        "relatorio": "relatorio",
        "backup": "backup",
        "auditoria": "auditoria",
    }
    return mapping[tab_id]


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
    """Atualiza header, abas e rodapé conforme o modo da tela."""
    _clear_header_actions(app)

    if app._logged_in and app._admin_user:
        app._email_lbl.configure(text=app._admin_user)
    else:
        app._email_lbl.configure(text="")

    cfg = load_config()

    if app._logged_in:
        user = app._admin_user or str(cfg.get("admin_email") or "admin")
        conn = "Conectado" if is_sheets_configured(cfg) else "Desconectado"
        app._footer_user.set(f"Usuário: {user} · {conn} · v{APP_VERSION}")
    else:
        app._footer_user.set("")

    if mode == "secretaria":
        app.tab_bar.pack(fill="x")
        tab = active_tab or app._active_tab or "socies"
        _highlight_tab(app, tab)
        _header_outline_btn(app._header_actions, "← Voltar", lambda: go_back(app)).pack(side="left", padx=(0, 6))
        _header_outline_btn(app._header_actions, "Lista pública", lambda: navigate(app, "lista")).pack(side="left", padx=3)
        _header_outline_btn(app._header_actions, "Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)
        _header_outline_btn(app._header_actions, "Sair", app._logout).pack(side="left", padx=3)
    elif mode == "public":
        app.tab_bar.pack_forget()
        _highlight_tab(app, None)
        _header_outline_btn(app._header_actions, "← Voltar", lambda: go_back(app)).pack(side="left", padx=(0, 6))
        _header_outline_btn(app._header_actions, "Lista pública", lambda: navigate(app, "lista")).pack(side="left", padx=3)
        if not app._logged_in:
            _header_outline_btn(app._header_actions, "Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)
        else:
            _header_outline_btn(app._header_actions, "Secretaria", lambda: navigate(app, "admin")).pack(side="left", padx=3)
            _header_outline_btn(app._header_actions, "Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)
            _header_outline_btn(app._header_actions, "Sair", app._logout).pack(side="left", padx=3)
    else:
        app.tab_bar.pack_forget()
        _highlight_tab(app, None)
        _header_outline_btn(app._header_actions, "Configurações", lambda: navigate(app, "settings")).pack(side="left", padx=3)


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


def page_wrap(app: "SinapescApp", *, padx: int = 24, pady: int = 16) -> tk.Frame:
    wrap = tk.Frame(app.body, bg=COLORS["content"])
    wrap.pack(fill="both", expand=True, padx=padx, pady=pady)
    return wrap


def page_title_row(
    parent,
    title: str,
    *,
    subtitle: str = "",
    helper: str = "",
) -> tk.Frame:
    row = tk.Frame(parent, bg=COLORS["content"])
    row.pack(fill="x", pady=(0, 10))
    left = tk.Frame(row, bg=COLORS["content"])
    left.pack(side="left", fill="x", expand=True)
    title_row = tk.Frame(left, bg=COLORS["content"])
    title_row.pack(anchor="w")
    tk.Label(
        title_row, text=title, bg=COLORS["content"], fg=COLORS["primary"],
        font=(FONT_DISPLAY, 20, "bold"),
    ).pack(side="left")
    if subtitle:
        tk.Label(
            title_row, text=subtitle, bg=COLORS["content"], fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        ).pack(side="left", padx=(10, 0))
    if helper:
        tk.Label(
            left, text=helper, bg=COLORS["content"], fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
        ).pack(anchor="w", pady=(2, 0))
    return row
