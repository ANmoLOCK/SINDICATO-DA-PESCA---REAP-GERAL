"""Ponte Python ↔ JavaScript (pywebview) para o Sinapesc REAP."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import threading
import webbrowser
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import import_credentials_file, is_sheets_configured, load_config, save_config
from controle.auditoria import combina_busca
from controle.backup import backup_root, gravar_backup, listar_backups
from controle.calendario import meses_para_texto
from controle.pendencias import classificar
from controle.relatorio import itens_para_relatorio, montar_html, nome_arquivo_relatorio, salvar_html
from sheets import MESES, MESES_LABEL, MesKey, SheetsConfigError, SheetsService
from ui.formatters import display_nome, format_cpf, format_nome, only_digits, parse_lote_lines
from ui.public_link import ensure_site_qrs, urls_for
from ui.qr_vault import normalize_public_base, preferred_public_base, qr_dir
from ui.qrutil import make_qr_image
from ui.theme import APP_VERSION, ORG_FULL, ORG_SHORT
from webapp.serialize import err, ok, pessoa_to_dict

try:
    import webview
except ImportError:  # pragma: no cover
    webview = None  # type: ignore[assignment]


class SinapescApi:
    """Métodos expostos ao JS via window.pywebview.api."""

    def __init__(self) -> None:
        self._window: Any = None
        self._busy = False
        self._queue: List[tuple] = []
        self._lock = threading.Lock()
        self._logged_in = False
        self._admin_user = ""
        self._service: Optional[SheetsService] = None

    def bind_window(self, window: Any) -> None:
        self._window = window

    # ---- sync / bootstrap ------------------------------------------------

    def get_bootstrap(self) -> Dict[str, Any]:
        cfg = load_config()
        cred = cfg.get("credentials_json")
        cred_label = (
            f"JSON: {cred.get('client_email')}"
            if isinstance(cred, dict)
            else "Nenhuma credencial carregada."
        )
        site = normalize_public_base(cfg.get("public_site_url") or cfg.get("public_base_url") or "")
        return ok(
            {
                "version": APP_VERSION,
                "org_short": ORG_SHORT,
                "org_full": ORG_FULL,
                "configured": is_sheets_configured(cfg),
                "logged_in": self._logged_in,
                "admin_email": str(cfg.get("admin_email") or ""),
                "admin_user": self._admin_user,
                "spreadsheet_id": str(cfg.get("spreadsheet_id") or ""),
                "public_site_url": site,
                "ultimo_backup_em": str(cfg.get("ultimo_backup_em") or "Nunca"),
                "credentials_label": cred_label,
                "backup_root": str(backup_root()),
                "qr_dir": str(qr_dir()),
                "meses": MESES,
                "meses_label": MESES_LABEL,
            }
        )

    def login(self, email: str, password: str) -> Dict[str, Any]:
        cfg = load_config()
        if email.strip().lower() != str(cfg.get("admin_email", "")).lower():
            return err("E-mail ou senha incorretos.")
        if password != str(cfg.get("admin_password", "")):
            return err("E-mail ou senha incorretos.")
        if not is_sheets_configured(cfg):
            return err("Configure primeiro o Google Sheets.", redirect="settings")
        self._logged_in = True
        self._admin_user = email.strip()
        self._service = None
        return ok(admin_user=self._admin_user)

    def logout(self) -> Dict[str, Any]:
        self._logged_in = False
        self._admin_user = ""
        self._service = None
        return ok()

    def get_settings(self) -> Dict[str, Any]:
        cfg = load_config()
        cred = cfg.get("credentials_json")
        return ok(
            {
                "spreadsheet_id": str(cfg.get("spreadsheet_id") or ""),
                "public_site_url": normalize_public_base(
                    cfg.get("public_site_url") or cfg.get("public_base_url") or ""
                ),
                "admin_email": str(cfg.get("admin_email") or ""),
                "admin_password": str(cfg.get("admin_password") or ""),
                "credentials_label": (
                    f"JSON: {cred.get('client_email')}"
                    if isinstance(cred, dict)
                    else "Nenhuma credencial carregada."
                ),
            }
        )

    def save_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        cfg = load_config()
        if "spreadsheet_id" in payload:
            cfg["spreadsheet_id"] = str(payload.get("spreadsheet_id") or "").strip()
        if "public_site_url" in payload:
            base = normalize_public_base(str(payload.get("public_site_url") or ""))
            cfg["public_site_url"] = base
            cfg["public_base_url"] = base
        if "admin_email" in payload:
            cfg["admin_email"] = str(payload.get("admin_email") or "").strip()
        if "admin_password" in payload:
            cfg["admin_password"] = str(payload.get("admin_password") or "")
        save_config(cfg)
        self._service = None
        self._sync_site_config_js(cfg.get("spreadsheet_id", ""))
        return ok()

    def import_credentials_json(self, raw_json: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            return err("JSON inválido.")
        if not isinstance(data, dict) or data.get("type") != "service_account":
            return err("Arquivo inválido. Use o JSON da Conta de Serviço do Google Cloud.")
        if "client_email" not in data or "private_key" not in data:
            return err("JSON incompleto: faltam client_email ou private_key.")
        cfg = load_config()
        cfg["credentials_json"] = data
        cfg["service_account_email"] = data.get("client_email", "")
        cfg["private_key"] = data.get("private_key", "")
        save_config(cfg)
        self._service = None
        return ok(credentials_label=f"JSON: {data.get('client_email')}")

    def test_connection(self) -> Dict[str, Any]:
        try:
            svc = self._ensure_service(require_login=False)
            n = len(svc.get_all_pessoas())
            return ok(count=n)
        except Exception as exc:  # noqa: BLE001
            return err(str(exc))

    # ---- async helpers ---------------------------------------------------

    def _dispatch(self, event: str, payload: Any) -> None:
        if not self._window:
            return
        body = json.dumps(payload, ensure_ascii=False)
        self._window.evaluate_js(f"window.AppEvents.dispatch({json.dumps(event)}, {body})")

    def _run_async(self, op: str, work, busy: str = "Aguarde…") -> Dict[str, Any]:
        job = (op, work, busy)
        with self._lock:
            if self._busy:
                self._queue.append(job)
                queued = True
            else:
                self._busy = True
                queued = False
        if queued:
            self._dispatch("status", {"msg": busy})
            return ok(pending=True, op=op, queued=True)
        self._start_job(job)
        return ok(pending=True, op=op)

    def _start_job(self, job: tuple) -> None:
        op, work, busy = job
        self._dispatch("status", {"msg": busy})

        def target() -> None:
            try:
                payload = ok(work())
            except Exception as exc:  # noqa: BLE001
                payload = err(str(exc))
            nxt = None
            with self._lock:
                if self._queue:
                    nxt = self._queue.pop(0)
                else:
                    self._busy = False
            # Libera "ocupado" ANTES de avisar o JS, senão o recarregamento
            # da lista é recusado e a tela só muda com Atualizar.
            self._dispatch(op, payload)
            if nxt:
                self._start_job(nxt)
            else:
                self._dispatch("status", {"msg": "Pronto."})

        threading.Thread(target=target, daemon=True).start()

    def _ensure_service(self, *, require_login: bool = True) -> SheetsService:
        if require_login and not self._logged_in:
            raise SheetsConfigError("Faça login como administrador.")
        cfg = load_config()
        if not is_sheets_configured(cfg):
            raise SheetsConfigError("Google Sheets ainda não configurado.")
        if self._service is None:
            self._service = SheetsService.from_config(cfg)
        actor = self._admin_user if self._logged_in else str(cfg.get("admin_email") or "")
        self._service.actor = actor
        return self._service

    def _sync_site_config_js(self, spreadsheet_id: str) -> None:
        sid = (spreadsheet_id or "").strip()
        if not sid:
            return
        from config import app_data_dir, exe_dir

        candidates = [
            Path(__file__).resolve().parents[2] / "site-publico" / "config.js",
            exe_dir().parent / "site-publico" / "config.js",
            exe_dir() / "site-publico" / "config.js",
            app_data_dir() / "site-publico" / "config.js",
        ]
        import re

        for path in candidates:
            if not path.exists():
                continue
            try:
                text = path.read_text(encoding="utf-8")
                updated = re.sub(
                    r'spreadsheetId:\s*"[^"]*"',
                    f'spreadsheetId: "{sid}"',
                    text,
                    count=1,
                )
                if updated != text:
                    path.write_text(updated, encoding="utf-8")
                return
            except OSError:
                continue

    # ---- sócios ----------------------------------------------------------

    def load_pessoas(self) -> Dict[str, Any]:
        def work():
            pessoas = self._ensure_service(require_login=False).get_all_pessoas_com_reap()
            return [pessoa_to_dict(p) for p in pessoas]

        return self._run_async("pessoas", work, "Carregando sócios…")

    def save_pessoa(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        nome = format_nome(str(payload.get("nome") or ""))
        cpf = only_digits(str(payload.get("cpf") or ""))
        person_id = str(payload.get("id") or "").strip()
        if not nome:
            return err("Informe o nome completo.")
        if len(cpf) != 11:
            return err("CPF deve conter 11 dígitos.")

        def work():
            svc = self._ensure_service()
            if person_id:
                svc.update_pessoa(person_id, nome, cpf)
                return person_id
            return svc.add_pessoa(nome, cpf).id

        return self._run_async("pessoa_saved", work, "Salvando…")

    def delete_pessoa(self, person_id: str) -> Dict[str, Any]:
        if not person_id:
            return err("Sócio inválido.")

        def work():
            self._ensure_service().delete_pessoa(person_id)
            return True

        return self._run_async("pessoa_deleted", work, "Excluindo…")

    def toggle_mes(self, person_id: str, ano: int, mes: str, novo: bool) -> Dict[str, Any]:
        if mes not in MESES:
            return err("Mês inválido.")

        def work():
            svc = self._ensure_service()
            pessoa = svc.get_pessoa_com_reap(person_id)
            nome = pessoa.nome if pessoa else ""
            svc.toggle_mes(person_id, int(ano), mes, bool(novo), nome=nome)  # type: ignore[arg-type]
            return {"person_id": person_id, "ano": int(ano), "mes": mes, "on": bool(novo)}

        return self._run_async("mes_toggled", work, f"Atualizando {mes}/{ano}…")

    def add_ano(self, person_id: str, ano: int) -> Dict[str, Any]:
        def work():
            svc = self._ensure_service()
            pessoa = svc.get_pessoa_com_reap(person_id)
            nome = pessoa.nome if pessoa else ""
            svc.add_ano(person_id, int(ano), nome=nome)
            return True

        return self._run_async("ano_added", work, "Adicionando ano…")

    def save_lote(self, raw: str, ano: int, meses_on: List[str]) -> Dict[str, Any]:
        itens = parse_lote_lines(raw)
        if not itens:
            return err("Nenhuma linha válida (Nome + CPF).")

        def work():
            return self._ensure_service().add_pessoas_lote(
                itens,
                ano=int(ano),
                meses_on=meses_on,
            )

        return self._run_async("lote_saved", work, "Importando lote…")

    def save_lote_rows(self, rows: Any, ano: int, meses_on: List[str]) -> Dict[str, Any]:
        try:
            itens = _lote_itens_from_rows(rows)
        except ValueError as exc:
            return err(str(exc))
        if not itens:
            return err("Nenhuma linha válida (Nome + CPF).")
        try:
            ano_i = int(ano)
        except (TypeError, ValueError):
            ano_i = datetime.now().year

        def work():
            return self._ensure_service().add_pessoas_lote(
                itens,
                ano=ano_i,
                meses_on=meses_on or [],
            )

        return self._run_async("lote_saved", work, f"Importando lote ({len(itens)} sócios)…")

    def copiar_ano(
        self,
        ano_origem: int,
        ano_destino: int,
        person_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        def work():
            return self._ensure_service().copiar_reap_ano(
                int(ano_origem),
                int(ano_destino),
                person_ids=person_ids,
            )

        return self._run_async("copia_ok", work, "Copiando ano…")

    def marcar_meses_em_massa(
        self,
        ano: int,
        meses_on: List[str],
        person_ids: Optional[List[str]] = None,
        substituir: bool = False,
    ) -> Dict[str, Any]:
        """Alias JS (nome igual ao SheetsService)."""
        return self.marcar_meses_massa(ano, meses_on, person_ids, substituir)

    def marcar_meses_massa(
        self,
        ano: int,
        meses_on: List[str],
        person_ids: Optional[List[str]] = None,
        substituir: bool = False,
    ) -> Dict[str, Any]:
        if not meses_on:
            return err("Escolha pelo menos um mês.")

        def work():
            svc = self._ensure_service()
            if person_ids:
                return svc.marcar_meses_em_massa(
                    ano=int(ano),
                    meses_on=meses_on,
                    person_ids=person_ids,
                    substituir=bool(substituir),
                )
            return svc.marcar_meses_em_massa(
                ano=int(ano),
                meses_on=meses_on,
                substituir=bool(substituir),
            )

        return self._run_async("massa_ok", work, "Marcando meses…")

    # ---- pendências ------------------------------------------------------

    def load_pendencias(self, ano: int) -> Dict[str, Any]:
        def work():
            svc = self._ensure_service()
            pessoas = svc.get_all_pessoas_com_reap()
            cal = svc.get_calendario(int(ano))
            pend, reg = classificar(pessoas, int(ano), cal)
            return {
                "ano": int(ano),
                "calendario": cal,
                "calendario_texto": meses_para_texto(cal),
                "pendentes": [_situacao_dict(s) for s in pend],
                "regulares_count": len(reg),
            }

        return self._run_async("pendencias", work, "Carregando pendências…")

    def save_calendario(self, ano: int, meses: List[str]) -> Dict[str, Any]:
        def work():
            cal = self._ensure_service().set_calendario(meses, ano=int(ano))
            return {"calendario": cal, "texto": meses_para_texto(cal)}

        return self._run_async("calendario_saved", work, "Salvando calendário…")

    # ---- relatório -------------------------------------------------------

    def generate_relatorio(self, ano: int, modo: str, busca: str = "") -> Dict[str, Any]:
        def work():
            svc = self._ensure_service()
            pessoas = svc.get_all_pessoas_com_reap()
            cal = svc.get_calendario(int(ano))
            pend, reg = classificar(pessoas, int(ano), cal)
            todos = itens_para_relatorio(pend, reg)
            escolhidos = todos
            titulo = f"Relatório de conformidade REAP {ano}"
            nome_arq = nome_arquivo_relatorio(int(ano))
            q = busca.strip().lower()
            digits = only_digits(q)
            if modo == "individual":
                if not q:
                    raise ValueError("Digite o nome ou CPF do sócio para o comprovante individual.")
                match = [
                    s
                    for s in todos
                    if q in s.pessoa.nome.lower() or (digits and digits in s.pessoa.cpf)
                ]
                if not match:
                    raise ValueError("Nenhum sócio encontrado com essa busca.")
                if len(match) > 1:
                    nomes = ", ".join(s.pessoa.nome for s in match[:8])
                    raise ValueError(f"Vários sócios ({len(match)}). Refine a busca.\n{nomes}")
                escolhidos = match
                titulo = f"Comprovante de situação REAP {ano}"
                nome_arq = nome_arquivo_relatorio(int(ano), individual_nome=match[0].pessoa.nome)
            html_txt = montar_html(
                org_short=ORG_SHORT,
                org_full=ORG_FULL,
                ano=int(ano),
                calendario=cal,
                itens=escolhidos,
                titulo=titulo,
                individual=modo == "individual",
            )
            path = salvar_html(html_txt, nome_arquivo=nome_arq)
            svc.registrar_evento("relatorio", f"gerou {path.name}")
            return {"path": str(path), "html": html_txt}

        return self._run_async("relatorio", work, "Gerando relatório…")

    # ---- backup / auditoria ----------------------------------------------

    def run_backup(self) -> Dict[str, Any]:
        def work():
            svc = self._ensure_service()
            dados = svc.exportar_abas()
            pasta = gravar_backup(
                pessoas_rows=dados["pessoas"],
                reap_rows=dados["reap"],
                spreadsheet_id=str(svc.client.spreadsheet_id),
            )
            svc.registrar_evento("backup", f"gerou backup local {pasta.name}")
            cfg = load_config()
            cfg["ultimo_backup_em"] = datetime.now().isoformat(timespec="seconds")
            cfg["backup_adiado_em"] = ""
            save_config(cfg)
            return {"pasta": str(pasta), "ultimo_backup_em": cfg["ultimo_backup_em"]}

        return self._run_async("backup", work, "Gerando backup CSV…")

    def list_backups(self) -> Dict[str, Any]:
        return ok(data=[p.name for p in listar_backups()[:12]])

    def load_auditoria(self) -> Dict[str, Any]:
        def work():
            eventos = self._ensure_service().listar_auditoria(400)
            return [
                {
                    "em": e.em,
                    "usuario": e.usuario,
                    "acao": e.acao,
                    "detalhe": e.detalhe,
                    "nome": e.nome,
                    "ano": e.ano,
                    "meses": e.meses,
                }
                for e in eventos
            ]

        return self._run_async("auditoria", work, "Carregando auditoria…")

    def export_auditoria(self) -> Dict[str, Any]:
        import csv

        def work():
            eventos = self._ensure_service().listar_auditoria(400)
            path = backup_root() / "auditoria-reap.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["em", "usuario", "acao", "detalhe", "nome", "ano", "meses"])
                for e in eventos:
                    writer.writerow([e.em, e.usuario, e.acao, e.detalhe, e.nome, e.ano, e.meses])
            return {"path": str(path), "count": len(eventos)}

        return self._run_async("auditoria_export", work, "Exportando auditoria…")

    def filter_auditoria_local(self, eventos: List[Dict[str, Any]], busca: str) -> Dict[str, Any]:
        from controle.auditoria import EventoAuditoria

        out = []
        for raw in eventos:
            evt = EventoAuditoria(
                id="",
                em=str(raw.get("em") or ""),
                usuario=str(raw.get("usuario") or ""),
                acao=str(raw.get("acao") or ""),
                detalhe=str(raw.get("detalhe") or ""),
                nome=str(raw.get("nome") or ""),
                ano=str(raw.get("ano") or ""),
                meses=str(raw.get("meses") or ""),
            )
            if combina_busca(evt, busca):
                out.append(raw)
        return ok(data=out)

    # ---- site público / QR -----------------------------------------------

    def generate_site_qrs(self, force: bool = True) -> Dict[str, Any]:
        base = preferred_public_base()
        if not base:
            return err("Configure a URL do site público em Configurações.")

        def work():
            cfg = load_config()
            pessoas = []
            try:
                pessoas = self._ensure_service().get_all_pessoas_com_reap()
            except Exception:
                pass
            resolved = ensure_site_qrs(pessoas=pessoas or None, force=force)
            return {"base": resolved, "qr_dir": str(qr_dir())}

        return self._run_async("qrs", work, "Gerando QRs do site público…")

    def qr_preview(self, kind: str, person_id: str = "") -> Dict[str, Any]:
        base = preferred_public_base()
        if not base:
            return err("Site público não configurado.")
        try:
            if kind == "consulta":
                url = urls_for(base)["consulta"]
                subtitle = "Consulta por CPF"
            elif kind == "lista":
                url = urls_for(base)["lista"]
                subtitle = "Lista pública"
            elif kind == "pessoa" and person_id:
                pessoa = self._ensure_service(require_login=False).get_pessoa_com_reap(person_id)
                if not pessoa:
                    return err("Sócio não encontrado.")
                url = urls_for(base, pessoa)["pessoa"]
                subtitle = display_nome(pessoa.nome)
            else:
                return err("Tipo de QR inválido.")
            img = make_qr_image(url, subtitle=subtitle)
            buf = BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return ok(data={"url": url, "image": f"data:image/png;base64,{b64}"})
        except Exception as exc:  # noqa: BLE001
            return err(str(exc))

    def open_path(self, path: str) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return err("Caminho não encontrado.")
        try:
            if os.name == "nt":
                os.startfile(str(p))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(p)])
            return ok()
        except OSError as exc:
            return err(str(exc))

    def open_url(self, url: str) -> Dict[str, Any]:
        try:
            webbrowser.open(url)
            return ok()
        except Exception as exc:  # noqa: BLE001
            return err(str(exc))

    def quit_app(self) -> Dict[str, Any]:
        if webview:
            webview.destroy_window()
        return ok()


def _lote_itens_from_rows(rows: Any) -> List[tuple[str, str]]:
    """Aceita lista de dicts OU JSON string (ponte JS do pywebview)."""
    if isinstance(rows, str):
        text = rows.strip()
        if not text:
            return []
        try:
            rows = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Lista do lote inválida.") from exc
    itens: List[tuple[str, str]] = []
    for row in rows or []:
        if isinstance(row, (list, tuple)) and len(row) >= 2:
            nome = str(row[0] or "").strip()
            cpf = only_digits(str(row[1] or ""))
        elif isinstance(row, dict):
            nome = str(row.get("nome") or "").strip()
            cpf = only_digits(str(row.get("cpf") or ""))
        else:
            continue
        if nome or cpf:
            itens.append((nome, cpf))
    return itens


def _situacao_dict(item) -> Dict[str, Any]:
    p = item.pessoa
    return {
        "person_id": p.id,
        "nome": p.nome,
        "nome_display": display_nome(p.nome),
        "cpf": format_cpf(p.cpf),
        "faltando": list(item.faltando),
        "regular": item.regular,
        "rotulo": item.rotulo_faltando,
        "tem_ano": item.tem_ano,
        "ano": item.ano,
    }
