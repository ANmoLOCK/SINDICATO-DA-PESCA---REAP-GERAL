"""Carrega logo e artes do Sinapesc para a UI."""

from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk
from typing import Optional

_cache: dict[tuple[str, int], tk.PhotoImage] = {}


def _base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def asset_path(name: str) -> Path:
    return _base() / "assets" / name


def load_png(master: tk.Misc, name: str, size: int = 48) -> Optional[tk.PhotoImage]:
    """Carrega PNG do assets/ com redimensionamento aproximado."""
    key = (name, size)
    if key in _cache:
        return _cache[key]
    path = asset_path(name)
    if not path.exists():
        return None
    try:
        img = tk.PhotoImage(file=str(path), master=master)
        w = max(img.width(), 1)
        factor = max(1, round(w / max(size, 1)))
        if factor > 1:
            img = img.subsample(factor, factor)
        _cache[key] = img
        return img
    except tk.TclError:
        return None


def load_logo(master: tk.Misc, size: int = 48) -> Optional[tk.PhotoImage]:
    img = load_png(master, "logo.png", size=size)
    if img is None:
        img = load_png(master, "icon.png", size=size)
    return img


def load_fish(master: tk.Misc, size: int = 64) -> Optional[tk.PhotoImage]:
    return load_png(master, "fish.png", size=size)


def load_school(master: tk.Misc, width: int = 320) -> Optional[tk.PhotoImage]:
    return load_png(master, "school.png", size=width)
