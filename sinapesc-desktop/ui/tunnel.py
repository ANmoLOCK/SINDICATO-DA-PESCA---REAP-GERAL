"""
Túnel público via Cloudflare (trycloudflare.com).

Importante para QR estável:
- Se o túnel JÁ estiver rodando, reutiliza a mesma URL (não gera outra).
- Ao fechar o app, o túnel pode continuar ativo (keep alive) para o QR impresso
  continuar funcionando.
- Só gera URL nova com force_new=True ("Renovar link").
"""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Tuple
from urllib.request import urlretrieve

from config import app_data_dir

_URL_RE = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
_process: Optional[subprocess.Popen] = None
_public_url: str = ""
_lock = threading.Lock()

_CLOUDFLARED_WIN = (
    "https://github.com/cloudflare/cloudflared/releases/latest/download/"
    "cloudflared-windows-amd64.exe"
)


def current_public_url() -> str:
    return _public_url


def is_tunnel_running() -> bool:
    return _process is not None and _process.poll() is None


def stop_tunnel() -> None:
    global _process, _public_url
    with _lock:
        if _process is not None and _process.poll() is None:
            try:
                _process.terminate()
                _process.wait(timeout=5)
            except Exception:
                try:
                    _process.kill()
                except Exception:
                    pass
        _process = None
        # Mantém _public_url em memória só se quiser — limpamos ao encerrar de fato
        _public_url = ""


def _cloudflared_path() -> Path:
    folder = app_data_dir() / "bin"
    folder.mkdir(parents=True, exist_ok=True)
    name = "cloudflared.exe" if platform.system() == "Windows" else "cloudflared"
    return folder / name


def ensure_cloudflared(progress: Optional[Callable[[str], None]] = None) -> Path:
    path = _cloudflared_path()
    if path.exists() and path.stat().st_size > 1_000_000:
        return path

    if platform.system() == "Windows":
        if progress:
            progress("Baixando Cloudflare Tunnel (primeira vez)…")
        urlretrieve(_CLOUDFLARED_WIN, str(path))
        return path

    which = shutil.which("cloudflared")
    if which:
        return Path(which)

    if progress:
        progress("Baixando Cloudflare Tunnel (Linux)…")
    linux_url = (
        "https://github.com/cloudflare/cloudflared/releases/latest/download/"
        "cloudflared-linux-amd64"
    )
    urlretrieve(linux_url, str(path))
    path.chmod(0o755)
    return path


def start_tunnel(
    local_port: int = 8765,
    *,
    timeout_sec: float = 45.0,
    progress: Optional[Callable[[str], None]] = None,
    force_new: bool = False,
) -> Tuple[str, bool]:
    """
    Retorna (url, created_new).
    created_new=False quando reutilizou túnel já ativo (QR continua válido).
    """
    global _process, _public_url

    if not force_new and is_tunnel_running() and _public_url:
        if progress:
            progress(f"Link público já ativo: {_public_url}")
        return _public_url, False

    if force_new or not is_tunnel_running():
        # Encerra só se vamos criar outro
        if is_tunnel_running():
            stop_tunnel()

    binary = ensure_cloudflared(progress)
    if progress:
        progress("Abrindo túnel público…")

    cmd = [
        str(binary),
        "tunnel",
        "--url",
        f"http://127.0.0.1:{local_port}",
        "--no-autoupdate",
    ]

    creationflags = 0
    if platform.system() == "Windows":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
    )

    found = {"url": ""}

    def reader() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            match = _URL_RE.search(line)
            if match and not found["url"]:
                found["url"] = match.group(0).rstrip("/")

    threading.Thread(target=reader, daemon=True).start()

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if found["url"]:
            break
        if proc.poll() is not None:
            raise RuntimeError(
                "O túnel Cloudflare encerrou cedo. Verifique a conexão com a internet."
            )
        time.sleep(0.25)

    if not found["url"]:
        try:
            proc.terminate()
        except Exception:
            pass
        raise TimeoutError("Não foi possível obter o link público a tempo. Tente novamente.")

    with _lock:
        _process = proc
        _public_url = found["url"]

    if progress:
        progress(f"Link público pronto: {_public_url}")
    return _public_url, True
