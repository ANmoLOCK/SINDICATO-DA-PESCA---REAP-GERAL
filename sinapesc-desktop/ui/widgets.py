"""Componentes visuais alinhados ao mockup Sinapesc REAP v1.6."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ui.theme import COLORS, FONT_DISPLAY, FONT_FAMILY


def header_outline_btn(parent, text: str, command: Callable) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLORS["primary"],
        fg=COLORS["primary_fg"],
        activebackground=COLORS["primary_mid"],
        activeforeground=COLORS["primary_fg"],
        relief="solid",
        bd=1,
        highlightbackground="#C8D8E8",
        highlightcolor="#C8D8E8",
        highlightthickness=1,
        padx=12,
        pady=5,
        font=(FONT_FAMILY, 9),
        cursor="hand2",
    )


def content_outline_btn(
    parent,
    text: str,
    command: Callable,
    *,
    padx: int = 14,
    pady: int = 7,
    font_size: int = 9,
) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLORS["content"],
        fg=COLORS["primary"],
        activebackground=COLORS["surface_soft"],
        activeforeground=COLORS["primary"],
        relief="solid",
        bd=1,
        highlightbackground=COLORS["primary"],
        highlightcolor=COLORS["primary"],
        highlightthickness=1,
        padx=padx,
        pady=pady,
        font=(FONT_FAMILY, font_size),
        cursor="hand2",
    )


def content_primary_btn(
    parent,
    text: str,
    command: Callable,
    *,
    padx: int = 16,
    pady: int = 7,
    font_size: int = 9,
) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLORS["primary"],
        fg=COLORS["primary_fg"],
        activebackground=COLORS["primary_mid"],
        activeforeground=COLORS["primary_fg"],
        relief="flat",
        bd=0,
        padx=padx,
        pady=pady,
        font=(FONT_DISPLAY, font_size, "bold"),
        cursor="hand2",
    )


def search_field(parent, textvariable: tk.StringVar, *, width: int = 44) -> tk.Frame:
    """Campo de busca com borda arredondada visual e lupa à direita."""
    outer = tk.Frame(
        parent,
        bg=COLORS["content"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
    )
    inner = tk.Frame(outer, bg=COLORS["content"])
    inner.pack(fill="x", padx=10, pady=6)
    ent = ttk.Entry(inner, textvariable=textvariable, width=width, style="Search.TEntry")
    ent.pack(side="left", fill="x", expand=True)
    tk.Label(inner, text="🔍", bg=COLORS["content"], fg=COLORS["muted"], font=(FONT_FAMILY, 10)).pack(
        side="right", padx=(8, 0)
    )
    return outer


def card_shell(parent) -> tk.Frame:
    return tk.Frame(
        parent,
        bg=COLORS["surface"],
        padx=16,
        pady=12,
        highlightbackground=COLORS["border_soft"],
        highlightthickness=1,
    )


def circular_avatar(parent, initials: str) -> tk.Frame:
    wrap = tk.Frame(parent, bg=COLORS["surface"], width=44, height=44)
    wrap.pack_propagate(False)
    lbl = tk.Label(
        wrap,
        text=initials,
        bg=COLORS["primary"],
        fg=COLORS["primary_fg"],
        font=(FONT_DISPLAY, 11, "bold"),
        width=2,
        height=1,
    )
    lbl.place(relx=0.5, rely=0.5, anchor="center")
    return wrap


def icon_btn(
    parent,
    text: str,
    command: Callable,
    *,
    danger: bool = False,
) -> tk.Button:
    if danger:
        bg, fg, hover = COLORS["danger_bg"], COLORS["danger"], "#EFD0CC"
    else:
        bg, fg, hover = COLORS["content"], COLORS["muted"], COLORS["surface_soft"]
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=8,
        pady=4,
        font=(FONT_FAMILY, 9),
        cursor="hand2",
    )


def chevron_btn(parent, expanded: bool, command: Callable) -> tk.Button:
    sym = "▲" if expanded else "▼"
    return tk.Button(
        parent,
        text=sym,
        command=command,
        bg=COLORS["surface"],
        fg=COLORS["muted"],
        activebackground=COLORS["surface_soft"],
        relief="flat",
        bd=0,
        padx=6,
        pady=2,
        font=(FONT_FAMILY, 9),
        cursor="hand2",
    )


def month_pill(
    parent,
    mes: str,
    *,
    pago: bool,
    editable: bool,
    command: Optional[Callable] = None,
) -> tk.Widget:
    if pago:
        bg, fg, mark = COLORS["success_bg"], COLORS["success"], "✓"
    else:
        bg, fg, mark = COLORS["danger_bg"], COLORS["danger"], "!"
    text = f"{mes.lower()}\n{mark}"
    if editable and command:
        w = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            width=5,
            height=2,
            font=(FONT_FAMILY, 8, "bold"),
            cursor="hand2",
            bd=0,
            padx=4,
            pady=2,
        )
    else:
        w = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            width=5,
            height=2,
            font=(FONT_FAMILY, 8, "bold"),
        )
    return w


def setup_widget_styles(root: tk.Misc) -> None:
    style = ttk.Style(root)
    style.configure(
        "Search.TEntry",
        fieldbackground=COLORS["content"],
        borderwidth=0,
        padding=(2, 4),
    )
