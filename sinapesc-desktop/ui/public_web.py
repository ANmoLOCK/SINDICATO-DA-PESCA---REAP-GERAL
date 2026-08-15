"""
Servidor HTTP público — lista, comprovante e consulta por CPF.

Rotas estáveis (não mudam):
  /consulta     → associado digita o CPF e vê só o próprio REAP
  /lista        → lista geral
  /p/{id}       → comprovante individual (QR único por sócio)
  /pessoa/{id}  → alias
"""

from __future__ import annotations

import html
import json
import socket
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, List, Optional
from urllib.parse import parse_qs, urlparse

from sheets.models import MESES, MESES_LABEL, PessoaComReap
from ui.formatters import format_cpf_masked, only_digits
from ui.theme import ORG_FULL, ORG_SHORT

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
    global _server, _thread, _port, _fetch
    _fetch = fetch_pessoas
    _port = port

    if _server is not None:
        return f"http://{get_lan_ip()}:{_port}"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            return

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)

            try:
                pessoas = _fetch() if _fetch else []
            except Exception as exc:  # noqa: BLE001
                self._send(500, "text/plain; charset=utf-8", f"Erro ao ler planilha: {exc}".encode("utf-8"))
                return

            if path in ("/", "/consulta", "/consulta/"):
                cpf = only_digits((qs.get("cpf") or [""])[0])
                body = render_consulta_html(pessoas, cpf_query=cpf).encode("utf-8")
                self._send(200, "text/html; charset=utf-8", body)
                return

            if path in ("/lista", "/lista/"):
                body = render_lista_html(pessoas).encode("utf-8")
                self._send(200, "text/html; charset=utf-8", body)
                return

            if path.startswith("/p/") or path.startswith("/pessoa/"):
                pid = path.split("/", 2)[-1].strip("/")
                pessoa = next((p for p in pessoas if p.id == pid), None)
                if not pessoa:
                    self._send(404, "text/html; charset=utf-8", render_not_found().encode("utf-8"))
                    return
                body = render_pessoa_html(pessoa).encode("utf-8")
                self._send(200, "text/html; charset=utf-8", body)
                return

            if path == "/api/lista":
                payload = [
                    {
                        "id": p.id,
                        "nome": p.nome,
                        "anos": [{"ano": a.ano, "meses": a.meses} for a in p.anos],
                    }
                    for p in pessoas
                ]
                raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self._send(200, "application/json; charset=utf-8", raw)
                return

            self._send(404, "text/html; charset=utf-8", render_not_found().encode("utf-8"))

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path not in ("/consulta", "/consulta/"):
                self._send(404, "text/plain; charset=utf-8", b"Nao encontrado")
                return
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            form = parse_qs(raw)
            cpf = only_digits((form.get("cpf") or [""])[0])
            try:
                pessoas = _fetch() if _fetch else []
            except Exception as exc:  # noqa: BLE001
                self._send(500, "text/plain; charset=utf-8", str(exc).encode("utf-8"))
                return
            body = render_consulta_html(pessoas, cpf_query=cpf).encode("utf-8")
            self._send(200, "text/html; charset=utf-8", body)

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
    :root {
      --bg:#e4edf2; --card:#fff; --primary:#0b243f; --accent:#0c7f72;
      --muted:#5a6b78; --ok:#1b8458; --off:#ecf1f5; --gold:#b8923e; --line:#b9ccd8;
    }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Segoe UI, system-ui, sans-serif; background:linear-gradient(180deg,#d5e3ea 0%, var(--bg) 40%, #eef4f7 100%); color:var(--primary); min-height:100vh; }
    header { background:linear-gradient(135deg, var(--primary), #163a5c); color:#f3fafc; padding:22px 20px 18px; border-bottom:3px solid var(--gold); }
    header h1 { margin:0; font-size:1.35rem; letter-spacing:.02em; }
    header p { margin:6px 0 0; opacity:.8; font-size:.86rem; max-width:42rem; }
    main { max-width:720px; margin:0 auto; padding:22px 16px 48px; }
    .meta { color:var(--muted); font-size:.9rem; margin-bottom:16px; }
    .panel { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; box-shadow:0 8px 24px rgba(11,36,63,.06); }
    label { display:block; font-size:.85rem; color:var(--muted); margin-bottom:6px; }
    input[type=text] { width:100%; padding:12px 14px; border:1px solid var(--line); border-radius:10px; font-size:1.05rem; letter-spacing:.04em; }
    button, .btn { display:inline-block; margin-top:12px; background:var(--accent); color:#fff; border:0; border-radius:10px; padding:12px 18px; font-weight:700; cursor:pointer; text-decoration:none; }
    button:hover { filter:brightness(.95); }
    details.card { background:var(--card); border:1px solid var(--line); border-radius:12px; margin-bottom:12px; padding:0 14px; }
    details.card summary { cursor:pointer; list-style:none; padding:14px 0; font-weight:700; display:flex; justify-content:space-between; gap:12px; align-items:center; }
    details.card summary::-webkit-details-marker { display:none; }
    .cpf { color:var(--muted); font-weight:500; font-size:.85rem; }
    .year { margin:8px 0 14px; }
    .year h3 { margin:0 0 8px; font-size:1rem; }
    .months { display:grid; grid-template-columns:repeat(6,1fr); gap:6px; }
    .m { text-align:center; padding:8px 4px; border-radius:8px; font-size:.75rem; font-weight:700; text-transform:uppercase; background:var(--off); color:var(--muted); }
    .m.on { background:#d4efe3; color:var(--ok); }
    .empty { color:var(--muted); }
    .err { color:#a82e26; margin-top:12px; }
    footer { text-align:center; color:var(--muted); font-size:.75rem; padding:16px; }
    @media (max-width:520px){ .months{grid-template-columns:repeat(4,1fr);} }
    """


def _months_html(meses: dict) -> str:
    cells = []
    for mes in MESES:
        pago = bool(meses.get(mes))
        cls = "m on" if pago else "m"
        mark = "✓" if pago else "·"
        cells.append(f'<div class="{cls}" title="{html.escape(MESES_LABEL[mes])}">{mes}<br>{mark}</div>')
    return f'<div class="months">{"".join(cells)}</div>'


def _years_html(pessoa: PessoaComReap) -> str:
    if not pessoa.anos:
        return "<p class='empty'>Nenhum ano registrado.</p>"
    parts = []
    for a in pessoa.anos:
        parts.append(f'<div class="year"><h3>{a.ano}</h3>{_months_html(a.meses)}</div>')
    return "".join(parts)


def _shell(title: str, subtitle: str, content: str) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta http-equiv="refresh" content="120"/>
<title>{html.escape(title)}</title>
<style>{_css()}</style>
</head><body>
<header>
  <h1>{html.escape(ORG_SHORT)}</h1>
  <p>{html.escape(ORG_FULL)}</p>
</header>
<main>
<p class="meta">{html.escape(subtitle)} · Atualizado em {agora}</p>
{content}
</main>
<footer>{html.escape(ORG_SHORT)} · {html.escape(ORG_FULL)}</footer>
</body></html>"""


def render_consulta_html(pessoas: List[PessoaComReap], *, cpf_query: str = "") -> str:
    form = f"""
    <div class="panel">
      <form method="POST" action="/consulta">
        <label for="cpf">Digite seu CPF para ver seus REAPs</label>
        <input id="cpf" name="cpf" type="text" inputmode="numeric" maxlength="14"
               placeholder="000.000.000-00" value="{html.escape(cpf_query)}" autofocus />
        <button type="submit">Consultar</button>
      </form>
    """
    result = ""
    if cpf_query:
        if len(cpf_query) != 11:
            result = "<p class='err'>Informe um CPF com 11 dígitos.</p>"
        else:
            pessoa = next((p for p in pessoas if only_digits(p.cpf) == cpf_query), None)
            if not pessoa:
                result = "<p class='err'>CPF não encontrado. Confira os números ou fale com a secretaria.</p>"
            else:
                result = f"""
                <div style="margin-top:18px">
                  <h2 style="margin:0 0 6px;font-size:1.15rem">{html.escape(pessoa.nome)}</h2>
                  <p class="cpf">CPF: {html.escape(format_cpf_masked(pessoa.cpf))}</p>
                  {_years_html(pessoa)}
                </div>
                """
    form += result + "</div>"
    return _shell(
        f"{ORG_SHORT} — Consulta REAP",
        "Consulta individual por CPF",
        form,
    )


def render_lista_html(pessoas: List[PessoaComReap]) -> str:
    cards = []
    for p in pessoas:
        cards.append(
            f"""<details class="card">
            <summary><span>{html.escape(p.nome)}</span><span class="cpf">{html.escape(format_cpf_masked(p.cpf))}</span></summary>
            {_years_html(p)}
            </details>"""
        )
    content = "".join(cards) if cards else "<p class='empty'>Nenhum associado cadastrado.</p>"
    nav = '<p><a class="btn" href="/consulta">Consultar meu CPF</a></p>'
    return _shell(
        f"{ORG_SHORT} — Lista REAP",
        "Lista pública de associados",
        nav + content,
    )


def render_pessoa_html(pessoa: PessoaComReap) -> str:
    body = f"""
    <div class="panel">
      <h2 style="margin:0 0 6px">{html.escape(pessoa.nome)}</h2>
      <p class="cpf">CPF: {html.escape(format_cpf_masked(pessoa.cpf))}</p>
      {_years_html(pessoa)}
      <p style="margin-top:16px"><a class="btn" href="/consulta">Outra consulta por CPF</a></p>
    </div>
    """
    return _shell(
        f"{pessoa.nome} — REAP",
        "Comprovante individual",
        body,
    )


def render_not_found() -> str:
    return _shell("Não encontrado", "Página indisponível", "<div class='panel'><p class='empty'>Conteúdo não encontrado.</p><a class='btn' href='/consulta'>Ir para consulta</a></div>")
