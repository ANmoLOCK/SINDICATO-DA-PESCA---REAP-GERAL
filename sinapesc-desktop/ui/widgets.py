"""Componentes desenhados em Canvas — o mais próximo do mockup que o Tkinter permite.

Tkinter nativo (Button/Label/Frame) é sempre retângulo. Cantos redondos e círculo
de verdade só existem se a gente desenhar no Canvas.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable, Optional

from ui.theme import COLORS, FONT_DISPLAY, FONT_FAMILY


def _round_rect(canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, r: int, **kwargs):
    r = max(0, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    return canvas.create_polygon(
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        smooth=True, **kwargs,
    )


class CanvasButton(tk.Canvas):
    """Botão com cantos arredondados (Canvas, não tk.Button)."""

    def __init__(
        self,
        parent,
        text: str,
        command: Callable,
        *,
        bg: str,
        fg: str,
        hover: str,
        outline: str = "",
        padx: int = 14,
        pady: int = 7,
        radius: int = 8,
        font=None,
        min_width: int = 0,
    ) -> None:
        font = font or (FONT_FAMILY, 9)
        fnt = tkfont.Font(root=parent.winfo_toplevel(), font=font)
        tw = fnt.measure(text) + 4
        th = fnt.metrics("linespace") + 2
        w = max(min_width, tw + padx * 2)
        h = th + pady * 2
        super().__init__(
            parent, width=w, height=h, bg=parent.cget("bg"),
            highlightthickness=0, bd=0, cursor="hand2",
        )
        self._command = command
        self._bg = bg
        self._hover = hover
        self._fg = fg
        self._outline = outline or bg
        self._radius = radius
        self._text = text
        self._font = font
        self._w = w
        self._h = h
        self._draw(bg)
        self.bind("<Button-1>", lambda _e: self._command())
        self.bind("<Enter>", lambda _e: self._draw(self._hover))
        self.bind("<Leave>", lambda _e: self._draw(self._bg))

    def _draw(self, fill: str) -> None:
        self.delete("all")
        _round_rect(
            self, 1, 1, self._w - 1, self._h - 1, self._radius,
            fill=fill, outline=self._outline,
        )
        self.create_text(
            self._w / 2, self._h / 2, text=self._text, fill=self._fg, font=self._font,
        )


def header_outline_btn(parent, text: str, command: Callable) -> CanvasButton:
    return CanvasButton(
        parent, text, command,
        bg=COLORS["primary"], fg=COLORS["primary_fg"], hover=COLORS["primary_mid"],
        outline="#C8D8E8", padx=12, pady=6, radius=8, font=(FONT_FAMILY, 9),
    )


def content_outline_btn(
    parent,
    text: str,
    command: Callable,
    *,
    padx: int = 14,
    pady: int = 7,
    font_size: int = 9,
) -> CanvasButton:
    return CanvasButton(
        parent, text, command,
        bg=COLORS["content"], fg=COLORS["primary"], hover=COLORS["surface_soft"],
        outline=COLORS["primary"], padx=padx, pady=pady, radius=8,
        font=(FONT_FAMILY, font_size),
    )


def content_primary_btn(
    parent,
    text: str,
    command: Callable,
    *,
    padx: int = 16,
    pady: int = 7,
    font_size: int = 9,
) -> CanvasButton:
    return CanvasButton(
        parent, text, command,
        bg=COLORS["primary"], fg=COLORS["primary_fg"], hover=COLORS["primary_mid"],
        outline=COLORS["primary"], padx=padx, pady=pady, radius=8,
        font=(FONT_DISPLAY, font_size, "bold"),
    )


def search_field(parent, textvariable: tk.StringVar, *, width: int = 44) -> tk.Frame:
    """Campo de busca com placeholder e lupa — borda suave."""
    outer = tk.Frame(parent, bg=COLORS["content"])
    canvas = tk.Canvas(outer, height=38, bg=COLORS["content"], highlightthickness=0, bd=0)
    canvas.pack(fill="x")
    inner = tk.Frame(canvas, bg=COLORS["content"])

    placeholder = "Buscar por nome ou CPF"
    hint = tk.Label(inner, text=placeholder, bg=COLORS["content"], fg=COLORS["muted"], font=(FONT_FAMILY, 9))
    hint.place(x=6, y=3)
    ent = ttk.Entry(inner, textvariable=textvariable, width=width, style="Search.TEntry")
    ent.pack(side="left", fill="x", expand=True, padx=(4, 0))
    tk.Label(inner, text="🔍", bg=COLORS["content"], fg=COLORS["muted"], font=(FONT_FAMILY, 11)).pack(
        side="right", padx=(6, 2)
    )

    def redraw(_e=None) -> None:
        canvas.delete("bg")
        w = max(canvas.winfo_width(), 120)
        _round_rect(canvas, 1, 2, w - 1, 36, 10, fill=COLORS["content"], outline=COLORS["border"], tags="bg")
        canvas.tag_lower("bg")

    def place(_e=None) -> None:
        canvas.coords(win, 12, 6)
        canvas.itemconfigure(win, width=max(canvas.winfo_width() - 24, 80))
        redraw()

    win = canvas.create_window(12, 6, window=inner, anchor="nw")
    canvas.bind("<Configure>", place)

    def sync_hint(*_a) -> None:
        if textvariable.get().strip() or str(ent.focus_get()) == str(ent):
            hint.place_forget()
        else:
            hint.place(x=6, y=3)

    def on_focus_in(_e=None) -> None:
        hint.place_forget()

    def on_focus_out(_e=None) -> None:
        sync_hint()

    ent.bind("<FocusIn>", on_focus_in)
    ent.bind("<FocusOut>", on_focus_out)
    hint.bind("<Button-1>", lambda _e: ent.focus_set())
    textvariable.trace_add("write", lambda *_: sync_hint())
    return outer


def card_shell(parent) -> tk.Frame:
    """Cartão com borda clara. Cantos 100% redondos exigem Canvas; o Frame segura o conteúdo."""
    return tk.Frame(
        parent,
        bg=COLORS["surface"],
        padx=16,
        pady=14,
        highlightbackground=COLORS["border_soft"],
        highlightthickness=1,
    )


def circular_avatar(parent, initials: str) -> tk.Canvas:
    """Círculo de verdade (Canvas oval) — Label do Tkinter sempre vira quadrado."""
    size = 44
    c = tk.Canvas(
        parent, width=size, height=size, bg=COLORS["surface"],
        highlightthickness=0, bd=0,
    )
    c.create_oval(2, 2, size - 2, size - 2, fill=COLORS["primary"], outline=COLORS["primary"])
    c.create_text(
        size / 2, size / 2, text=initials, fill=COLORS["primary_fg"],
        font=(FONT_DISPLAY, 11, "bold"),
    )
    return c


def icon_btn(
    parent,
    text: str,
    command: Callable,
    *,
    danger: bool = False,
) -> CanvasButton:
    if danger:
        return CanvasButton(
            parent, text, command,
            bg=COLORS["danger_bg"], fg=COLORS["danger"], hover="#EFD0CC",
            outline=COLORS["danger_bg"], padx=8, pady=4, radius=7,
            font=(FONT_FAMILY, 9),
        )
    return CanvasButton(
        parent, text, command,
        bg=COLORS["content"], fg=COLORS["muted"], hover=COLORS["surface_soft"],
        outline=COLORS["border_soft"], padx=8, pady=4, radius=7,
        font=(FONT_FAMILY, 9),
    )


def chevron_btn(parent, expanded: bool, command: Callable) -> CanvasButton:
    return CanvasButton(
        parent, "▲" if expanded else "▼", command,
        bg=COLORS["surface"], fg=COLORS["muted"], hover=COLORS["surface_soft"],
        outline=COLORS["surface"], padx=8, pady=4, radius=8,
        font=(FONT_FAMILY, 9), min_width=28,
    )


def month_pill(
    parent,
    mes: str,
    *,
    pago: bool,
    editable: bool,
    command: Optional[Callable] = None,
) -> tk.Canvas:
    """Pílula arredondada com ✓ ou ! — igual ao mockup, não um retângulo de Button."""
    fill = COLORS["success_bg"] if pago else COLORS["danger_bg"]
    ink = COLORS["success"] if pago else COLORS["danger"]
    mark = "✓" if pago else "!"
    w, h = 52, 38
    c = tk.Canvas(
        parent, width=w, height=h, bg=COLORS["surface"],
        highlightthickness=0, bd=0, cursor="hand2" if editable else "",
    )
    _round_rect(c, 1, 1, w - 1, h - 1, 8, fill=fill, outline=fill)
    c.create_text(w / 2, 12, text=mes.lower(), fill=ink, font=(FONT_FAMILY, 8, "bold"))
    c.create_text(w / 2, 26, text=mark, fill=ink, font=(FONT_FAMILY, 10, "bold"))
    if editable and command:
        c.bind("<Button-1>", lambda _e: command())
    return c


def setup_widget_styles(root: tk.Misc) -> None:
    style = ttk.Style(root)
    style.configure(
        "Search.TEntry",
        fieldbackground=COLORS["content"],
        borderwidth=0,
        padding=(2, 4),
        foreground=COLORS["primary"],
    )
