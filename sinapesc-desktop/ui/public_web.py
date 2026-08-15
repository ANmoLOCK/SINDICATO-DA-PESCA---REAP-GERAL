"""
Servidor HTTP embutido da lista pública (consulta online pelo celular).

Qualquer pessoa na mesma rede (ou na URL pública configurada) abre o link
do QR e vê os REAPs atualizados direto da planilha Google.
"""

from __future__ import annotations

import html
import json
import socket
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, List, Optional
from urllib.parse import urlparse

from sheets.models import MESES, MESES_LABEL, PessoaComReap
from ui.formatters import format_cpf_masked

_server: Optional[ThreadingHTTPServer] = None
_thread: Optional[threading.Thread] = None
_port: int = 8765
_fetch: Optional[Callable[[], List[PessoaComReap]]] = None


def get_lan_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "127.0.0.1"


def public_base_url(configured: str = "") -> str:
    configured = (configured or "").strip().rstrip("/")
    if configured:
        return configured
    return f"http://{get_lan_ip()}:{_port}"


def is_running() -> bool:
    return _server is not None


def start_public_server(fetch_pessoas: Callable[[], List[PessoaComReap]], port: int = 8765) -> str:
    """Inicia (ou reinicia) o servidor. Retorna a URL local."""
    global _server, _thread, _port, _fetch
    _fetch = fetch_pessoas
    _port = port

    if _server is not None:
        return f"http://{get_lan_ip()}:{_port}"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:  # silencioso
            return

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                pessoas = _fetch() if _fetch else []
            except Exception as exc:  # noqa: BLE001
                self._send(500, "text/plain; charset=utf-8", f"Erro ao ler planilha: {exc}".encode("utf-8"))
                return

            if path in ("/", "/lista", "/lista/"):
                body = render_lista_html(pessoas).encode("utf-8")
                self._send(200, "text/html; charset=utf-8", body)
                return

            if path.startswith("/pessoa/"):
                pid = path.split("/pessoa/", 1)[1].strip("/")
                pessoa = next((p for p in pessoas if p.id == pid), None)
                if not pessoa:
                    self._send(404, "text/plain; charset=utf-8", b"Associado nao encontrado")
                    return
                body = render_pessoa_html(pessoa).encode("utf-8")
                self._send(200, "text/html; charset=utf-8", body)
                return

            if path == "/api/lista":
                payload = [
                    {
                        "id": p.id,
                        "nome": p.nome,
                        "cpf_mascarado": format_cpf_masked(p.cpf),
                        "anos": [
                            {
                                "ano": a.ano,
                                "meses": a.meses,
                                "pagos": sum(1 for v in a.meses.values() if v),
                            }
                            for a in p.anos
                        ],
                    }
                    for p in pessoas
                ]
                raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self._send(200, "application/json; charset=utf-8", raw)
                return

            self._send(404, "text/plain; charset=utf-8", b"Nao encontrado")

        def _send(self, code: int, content_type: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    _server = ThreadingHTTPServer(("0.0.0.0", _port), Handler)
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    return f"http://{get_lan_ip()}:{_port}"


def stop_public_server() -> None:
    global _server, _thread
    if _server is not None:
        _server.shutdown()
        _server.server_close()
        _server = None
        _thread = None


def _css() -> str:
    return """
    :root { --bg:#e8f0f4; --card:#fff; --primary:#1a3358; --accent:#1f8a7a; --muted:#5a6b7a; --ok:#2e8b57; --off:#eef2f5; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Segoe UI, system-ui, sans-serif; background:var(--bg); color:var(--primary); }
    header { background:var(--primary); color:#f5fafc; padding:18px 20px; }
    header h1 { margin:0; font-size:1.25rem; }
    header p { margin:4px 0 0; opacity:.75; font-size:.85rem; }
    main { max-width:720px; margin:0 auto; padding:20px 16px 40px; }
    .meta { color:var(--muted); font-size:.9rem; margin-bottom:16px; }
    details.card { background:var(--card); border:1px solid #c5d4de; border-radius:10px; margin-bottom:12px; padding:0 14px; }
    details.card summary { cursor:pointer; list-style:none; padding:14px 0; font-weight:700; display:flex; justify-content:space-between; gap:12px; align-items:center; }
    details.card summary::-webkit-details-marker { display:none; }
    .cpf { color:var(--muted); font-weight:500; font-size:.85rem; }
    .year { margin:8px 0 14px; }
    .year h3 { margin:0 0 8px; font-size:1rem; }
    .months { display:grid; grid-template-columns:repeat(6,1fr); gap:6px; }
    .m { text-align:center; padding:8px 4px; border-radius:8px; font-size:.75rem; font-weight:700; text-transform:uppercase; background:var(--off); color:var(--muted); }
    .m.on { background:#d8f0e4; color:var(--ok); }
    footer { text-align:center; color:var(--muted); font-size:.75rem; padding:12px; }
    @media (max-width:520px){ .months{grid-template-columns:repeat(4,1fr);} }
    """


def _months_html(meses: dict) -> str:
    cells = []
    for mes in MESES:
        pago = bool(meses.get(mes))
        cls = "m on" if pago else "m"
        mark = "✓" if pago else "✗"
        label = MESES_LABEL[mes][:3]
        cells.append(f'<div class="{cls}" title="{html.escape(MESES_LABEL[mes])}">{mes}<br>{mark}</div>')
    return f'<div class="months">{"".join(cells)}</div>'


def render_lista_html(pessoas: List[PessoaComReap]) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    cards = []
    for p in pessoas:
        years = []
        for a in p.anos:
            pagos = sum(1 for v in a.meses.values() if v)
            years.append(
                f'<div class="year"><h3>{a.ano} · {pagos}/12 pagos</h3>{_months_html(a.meses)}</div>'
            )
        body = "".join(years) if years else "<p class='cpf'>Nenhum ano registrado.</p>"
        cards.append(
            f"""<details class="card">
            <summary><span>{html.escape(p.nome)}</span><span class="cpf">{html.escape(format_cpf_masked(p.cpf))}</span></summary>
            {body}
            </details>"""
        )
    content = "".join(cards) if cards else "<p class='meta'>Nenhum associado cadastrado.</p>"
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta http-equiv="refresh" content="60"/>
<title>Sinapesc — Lista REAP</title>
<style>{_css()}</style>
</head><body>
<header><h1>Sinapesc</h1><p>Lista pública de REAP · atualiza a cada 60s</p></header>
<main>
<p class="meta">Consulta pública · CPF parcialmente oculto · Atualizado em {agora}</p>
{content}
</main>
<footer>Sinapesc — Sindicato Nacional dos Pescadores</footer>
</body></html>"""


def render_pessoa_html(pessoa: PessoaComReap) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    years = []
    for a in pessoa.anos:
        pagos = sum(1 for v in a.meses.values() if v)
        years.append(
            f'<div class="year"><h3>{a.ano} · {pagos}/12 pagos</h3>{_months_html(a.meses)}</div>'
        )
    body = "".join(years) if years else "<p class='cpf'>Nenhum ano registrado.</p>"
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta http-equiv="refresh" content="60"/>
<title>{html.escape(pessoa.nome)} — REAP</title>
<style>{_css()}</style>
</head><body>
<header><h1>{html.escape(pessoa.nome)}</h1><p>Comprovante individual · CPF {html.escape(format_cpf_masked(pessoa.cpf))}</p></header>
<main>
<p class="meta">Documento intransferível · Atualizado em {agora}</p>
{body}
</main>
<footer>Sinapesc — válido apenas para {html.escape(pessoa.nome)}</footer>
</body></html>"""
