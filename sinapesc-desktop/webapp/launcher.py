"""Inicia a janela pywebview com a UI web."""

from __future__ import annotations

import sys

from ui.theme import APP_TAGLINE, ORG_SHORT
from webapp.api import SinapescApi
from webapp.paths import web_index_url


def run_web_app() -> None:
    try:
        import webview
    except ImportError as exc:
        print("pywebview não instalado. Use: pip install pywebview", file=sys.stderr)
        print("Ou execute com --tk para a interface Tkinter.", file=sys.stderr)
        raise SystemExit(1) from exc

    api = SinapescApi()
    title = f"{ORG_SHORT} REAP — {APP_TAGLINE.split('·')[0].strip()}"

    window = webview.create_window(
        title,
        url=web_index_url(),
        js_api=api,
        width=1180,
        height=760,
        min_size=(900, 600),
        background_color="#0A2F52",
    )
    api.bind_window(window)

    # Edge WebView2 no Windows; no Linux usa GTK/WebKit automaticamente.
    gui = None
    if sys.platform == "win32":
        try:
            gui = "edgechromium"
        except Exception:  # noqa: BLE001
            gui = None

    webview.start(gui=gui, debug=False)
