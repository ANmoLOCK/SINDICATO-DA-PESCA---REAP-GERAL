"""Área com scroll confiável (Windows + Linux)."""

from __future__ import annotations

import platform
import tkinter as tk
from tkinter import ttk
from typing import ClassVar, Optional


class ScrollableFrame(ttk.Frame):
    """
    Canvas + frame interno.
    Mousewheel só age na área sob o ponteiro (sem vazar bind_all).
    """

    _active: ClassVar[Optional["ScrollableFrame"]] = None
    _global_bound: ClassVar[bool] = False

    def __init__(self, master, *, bg: str = "#E8F0F4", **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._bg = bg
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)

        self._window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        for widget in (self.canvas, self.inner):
            widget.bind("<Enter>", self._activate, add="+")
            widget.bind("<Leave>", self._maybe_deactivate, add="+")

        ScrollableFrame._ensure_global_bindings(self.canvas)

    @classmethod
    def _ensure_global_bindings(cls, canvas: tk.Canvas) -> None:
        if cls._global_bound:
            return
        cls._global_bound = True
        system = platform.system()
        root = canvas.winfo_toplevel()
        if system == "Windows":
            root.bind_all("<MouseWheel>", cls._dispatch_windows, add="+")
        elif system == "Darwin":
            root.bind_all("<MouseWheel>", cls._dispatch_mac, add="+")
        else:
            root.bind_all("<Button-4>", cls._dispatch_linux_up, add="+")
            root.bind_all("<Button-5>", cls._dispatch_linux_down, add="+")

    def _on_inner_configure(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self._window_id, width=max(event.width, 1))

    def _activate(self, _event=None) -> None:
        ScrollableFrame._active = self

    def _maybe_deactivate(self, _event=None) -> None:
        # Mantém ativo se o ponteiro ainda está em algum filho
        try:
            x, y = self.winfo_pointerxy()
            w = self.winfo_containing(x, y)
            while w is not None:
                if w == self or w == self.canvas or w == self.inner:
                    return
                w = getattr(w, "master", None)
        except tk.TclError:
            pass
        if ScrollableFrame._active is self:
            ScrollableFrame._active = None

    @classmethod
    def _dispatch_windows(cls, event: tk.Event):
        if cls._active is None:
            return None
        cls._active.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    @classmethod
    def _dispatch_mac(cls, event: tk.Event):
        if cls._active is None:
            return None
        cls._active.canvas.yview_scroll(int(-1 * event.delta), "units")
        return "break"

    @classmethod
    def _dispatch_linux_up(cls, _event: tk.Event):
        if cls._active is None:
            return None
        cls._active.canvas.yview_scroll(-1, "units")
        return "break"

    @classmethod
    def _dispatch_linux_down(cls, _event: tk.Event):
        if cls._active is None:
            return None
        cls._active.canvas.yview_scroll(1, "units")
        return "break"

    def clear(self) -> None:
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)

    def destroy(self) -> None:
        if ScrollableFrame._active is self:
            ScrollableFrame._active = None
        super().destroy()
