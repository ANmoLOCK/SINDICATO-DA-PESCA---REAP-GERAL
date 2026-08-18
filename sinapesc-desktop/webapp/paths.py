"""Caminhos para assets web (dev e PyInstaller)."""

from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def web_dir() -> Path:
    return app_root() / "web"


def web_index_url() -> str:
    index = web_dir() / "index.html"
    return index.resolve().as_uri()
