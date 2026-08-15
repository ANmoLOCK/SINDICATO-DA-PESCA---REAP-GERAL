"""
Interface Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova.
"""

from __future__ import annotations

import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional, Set

from config import (
    app_data_dir,
    exe_dir,
    import_credentials_file,
    is_sheets_configured,
    load_config,
    save_config,
)
from sheets import MESES, MESES_LABEL, MesKey, PessoaComReap, SheetsConfigError, SheetsService
from ui.brand import load_fish, load_logo, load_school
from ui.formatters import format_cpf, format_cpf_masked, get_initials, only_digits
from ui.public_link import ensure_site_qrs, resolve_base, urls_for
from ui.public_web import start_public_server
from ui.qr_vault import (
    ensure_stable_qrs,
    path_for_consulta,
    path_for_lista,
    path_for_pessoa,
    preferred_public_base,
    qr_dir,
)
from ui.qrutil import make_qr_image, pil_to_tk, save_qr_png
from ui.scroll import ScrollableFrame
from ui.theme import (
    APP_TAGLINE,
    COLORS,
    FONT_DISPLAY,
    FONT_FAMILY,
    ORG_FULL,
    ORG_SHORT,
    ORG_TITLE,
)
from ui.tunnel import stop_tunnel


class SinapescApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(ORG_TITLE)
        self.geometry("1040x720")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg"])

        self.cfg = load_config()
        self.service: Optional[SheetsService] = None
        self._logged_in = False
        self._lista_mode = False
        self._pessoas: List[PessoaComReap] = []
        self._expanded_ids: Set[str] = set()
        self._scroll: Optional[ScrollableFrame] = None
        self._qr_photo = None
        self._public_url_var = tk.StringVar(value=str(self.cfg.get("public_base_url") or ""))

        self._setup_style()
        self._build_shell()
        self.show_home()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        try:
            self.iconphoto(True, tk.PhotoImage(file=_asset("icon.png")))
        except Exception:
            pass

    def _on_close(self) -> None:
        cfg = load_config()
        if not cfg.get("keep_tunnel_alive", True):
            stop_tunnel()
        if self._scroll is not None:
            try:
                self._scroll.destroy()
            except tk.TclError:
                pass
        self.destroy()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", font=(FONT_FAMILY, 10), background=COLORS["bg"])
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Header.TFrame", background=COLORS["primary"])
        style.configure("Header.TLabel", background=COLORS["primary"], foreground=COLORS["primary_fg"], font=(FONT_DISPLAY, 15, "bold"))
        style.configure("HeaderSub.TLabel", background=COLORS["primary"], foreground="#A9C0D4", font=(FONT_FAMILY, 9))
        style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["primary"], font=(FONT_DISPLAY, 20, "bold"))
        style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=(FONT_FAMILY, 10))

    def _build_shell(self) -> None:
        self.header = tk.Frame(self, bg=COLORS["primary"])
        self.header.pack(fill="x")
        tk.Frame(self.header, bg=COLORS["gold"], height=3).pack(fill="x")

        inner = tk.Frame(self.header, bg=COLORS["primary"])
        inner.pack(fill="x", padx=18, pady=12)

        left = tk.Frame(inner, bg=COLORS["primary"])
        left.pack(side="left", fill="x", expand=True)

        brand = tk.Frame(left, bg=COLORS["primary"])
        brand.pack(anchor="w")
        self._logo_img = load_logo(self, size=52)
        if self._logo_img is not None:
            tk.Label(brand, image=self._logo_img, bg=COLORS["primary"]).pack(side="left", padx=(0, 12))
        titles = tk.Frame(brand, bg=COLORS["primary"])
        titles.pack(side="left")
        tk.Label(titles, text=ORG_SHORT, bg=COLORS["primary"], fg=COLORS["primary_fg"], font=(FONT_DISPLAY, 17, "bold")).pack(anchor="w")
        tk.Label(titles, text=ORG_FULL, bg=COLORS["primary"], fg="#9CB8D0", font=(FONT_FAMILY, 9)).pack(anchor="w")
        tk.Label(titles, text=APP_TAGLINE, bg=COLORS["primary"], fg="#7E9BB3", font=(FONT_FAMILY, 8)).pack(anchor="w", pady=(2, 0))

        self.nav = tk.Frame(inner, bg=COLORS["primary"])
        self.nav.pack(side="right")

        self._school_img = load_school(self, width=220)
        if self._school_img is not None:
            tk.Label(inner, image=self._school_img, bg=COLORS["primary"]).pack(side="right", padx=(8, 10))

        tk.Frame(self.header, bg=COLORS["accent"], height=4).pack(fill="x")

        self.body = tk.Frame(self, bg=COLORS["bg"])
        self.body.pack(fill="both", expand=True)

        self.status = tk.StringVar(value="Pronto.")
        tk.Label(
            self, textvariable=self.status, anchor="w", bg=COLORS["surface"], fg=COLORS["muted"],
            font=(FONT_FAMILY, 9), padx=14, pady=7,
        ).pack(fill="x", side="bottom")

    def _clear_body(self) -> None:
        if self._scroll is not None:
            try:
                self._scroll.destroy()
            except tk.TclError:
                pass
            self._scroll = None
        for child in self.body.winfo_children():
            child.destroy()
        for child in self.nav.winfo_children():
            child.destroy()

    def _btn(self, parent, text, command, *, kind="accent", padx=12, pady=7, font_size=10, bold=True):
        styles = {
            "accent": (COLORS["accent"], COLORS["accent_fg"], COLORS["accent_hover"]),
            "primary": (COLORS["primary"], COLORS["primary_fg"], COLORS["primary_mid"]),
            "ghost": (COLORS["surface_soft"], COLORS["primary"], COLORS["border_soft"]),
            "danger": (COLORS["danger_bg"], COLORS["danger"], "#EFD0CC"),
            "nav": (COLORS["accent"], COLORS["accent_fg"], COLORS["accent_hover"]),
        }
        bg, fg, hover = styles.get(kind, styles["accent"])
        btn = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg, activebackground=hover,
            activeforeground=fg, relief="flat", padx=padx, pady=pady,
            font=(FONT_FAMILY, font_size, "bold" if bold else "normal"), cursor="hand2", bd=0,
        )
        return btn

    def _nav_button(self, text: str, command: Callable) -> None:
        self._btn(self.nav, text, command, kind="nav", padx=10, pady=5, font_size=9).pack(side="left", padx=3)

    def _set_busy(self, message: str) -> None:
        self.status.set(message)
        self.configure(cursor="watch")
        self.update_idletasks()

    def _set_idle(self, message: str = "Pronto.") -> None:
        self.status.set(message)
        self.configure(cursor="")

    def _run_bg(self, work: Callable, on_ok: Callable, on_err: Callable, busy_msg: str) -> None:
        self._set_busy(busy_msg)

        def target() -> None:
            try:
                result = work()
                self.after(0, lambda: (self._set_idle(), on_ok(result)))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: (self._set_idle("Erro."), on_err(exc)))

        threading.Thread(target=target, daemon=True).start()

    def _ensure_service(self) -> SheetsService:
        self.cfg = load_config()
        if not is_sheets_configured(self.cfg):
            raise SheetsConfigError("Google Sheets ainda não configurado. Abra Configurações.")
        self.service = SheetsService.from_config(self.cfg)
        return self.service

    def _ensure_public_server(self) -> str:
        """Servidor local só como fallback; site público é o canal principal."""
        self.cfg = load_config()
        if self.cfg.get("public_site_url"):
            return resolve_base()
        svc = self._ensure_service()

        def fetch():
            return svc.get_all_pessoas_com_reap()

        port = int(self.cfg.get("public_port") or 8765)
        start_public_server(fetch, port=port)
        return resolve_base()

    def _activate_link(self, *, force_new: bool = False, on_done=None) -> None:
        """Gera QRs para o site público configurado (URL fixa)."""
        if not preferred_public_base():
            messagebox.showwarning(
                "Site público",
                "Configure a URL do site público em Configurações "
                "(GitHub Pages / Cloudflare / Netlify).",
            )
            self.show_settings()
            return

        def work():
            pessoas = []
            try:
                svc = self._ensure_service()
                pessoas = svc.get_all_pessoas_com_reap()
            except Exception:
                pass
            base = ensure_site_qrs(pessoas=pessoas or None, force=force_new)
            return base, force_new, pessoas

        def ok(result):
            base, mudou, _pessoas = result
            self.cfg = load_config()
            if on_done:
                on_done(base, mudou)
            else:
                messagebox.showinfo(
                    "QRs do site público",
                    f"QRs apontando para:\n{base}\n\n"
                    f"Pasta:\n{qr_dir()}\n\n"
                    "Este endereço é fixo — não precisa gerar QR novo depois.",
                )

        self._run_bg(
            work,
            ok,
            lambda e: messagebox.showerror("Site público", str(e)),
            "Gerando QRs do site público…",
        )

    def _sync_site_config_js(self, spreadsheet_id: str) -> None:
        """Atualiza spreadsheetId em site-publico/config.js quando existir no disco."""
        sid = (spreadsheet_id or "").strip()
        if not sid:
            return
        candidates = [
            Path(__file__).resolve().parents[2] / "site-publico" / "config.js",
            exe_dir().parent / "site-publico" / "config.js",
            exe_dir() / "site-publico" / "config.js",
            app_data_dir() / "site-publico" / "config.js",
        ]
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
                    self.status.set(f"config.js atualizado: {path}")
                return
            except OSError:
                continue

    # ------------------------------------------------------------------
    # Home / Login
    # ------------------------------------------------------------------
    def show_home(self) -> None:
        self._lista_mode = False
        self._clear_body()
        self._nav_button("Configurações", self.show_settings)

        wrap = tk.Frame(self.body, bg=COLORS["bg"])
        wrap.pack(fill="both", expand=True, padx=40, pady=28)

        hero = tk.Frame(wrap, bg=COLORS["primary"], padx=22, pady=20)
        hero.pack(fill="x", pady=(0, 18))
        tk.Frame(hero, bg=COLORS["gold"], height=3).pack(fill="x", pady=(0, 12))
        row = tk.Frame(hero, bg=COLORS["primary"])
        row.pack(fill="x")
        if getattr(self, "_logo_img", None) is not None:
            tk.Label(row, image=self._logo_img, bg=COLORS["primary"]).pack(side="left", padx=(0, 14))
        col = tk.Frame(row, bg=COLORS["primary"])
        col.pack(side="left", fill="x", expand=True)
        tk.Label(col, text=ORG_SHORT, bg=COLORS["primary"], fg=COLORS["foam"], font=(FONT_DISPLAY, 26, "bold")).pack(anchor="w")
        tk.Label(col, text=ORG_FULL, bg=COLORS["primary"], fg="#B7D3E8", font=(FONT_FAMILY, 11)).pack(anchor="w", pady=(2, 6))
        tk.Label(
            col,
            text="Sistema profissional de REAP · consulta online gratuita · QR permanente",
            bg=COLORS["primary"], fg="#8EB0C9", font=(FONT_FAMILY, 9),
        ).pack(anchor="w")
        self._fish_hero = load_fish(self, size=96)
        if self._fish_hero is not None:
            tk.Label(row, image=self._fish_hero, bg=COLORS["primary"]).pack(side="right", padx=(8, 0))

        cards = tk.Frame(wrap, bg=COLORS["bg"])
        cards.pack(fill="x")
        self._home_card(
            cards,
            "Secretaria",
            "Cadastre sócios, marque REAPs e importe lotes na planilha Google.",
            "Entrar como administrador",
            self.show_login,
        ).pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._home_card(
            cards,
            "Consulta & QR",
            "Site público online (CPF) e QRs permanentes para imprimir na sede.",
            "Abrir lista e QRs",
            self.show_lista,
        ).pack(side="left", fill="both", expand=True, padx=(10, 0))

        tip = tk.Frame(wrap, bg=COLORS["surface_soft"], padx=16, pady=12)
        tip.pack(fill="x", pady=(18, 0))
        tip.configure(highlightbackground=COLORS["border"], highlightthickness=1)
        tk.Label(
            tip,
            text="Opção A — site gratuito: compartilhe a planilha como Leitor, publique site-publico/, cole a URL em Configurações e gere o QR Consulta.",
            bg=COLORS["surface_soft"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
            wraplength=880,
            justify="left",
        ).pack(anchor="w")

    def _home_card(self, parent, title, desc, btn_text, command) -> tk.Frame:
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=COLORS["surface"], padx=22, pady=22)
        inner.pack(fill="both", expand=True)
        tk.Frame(inner, bg=COLORS["gold"], height=2).pack(fill="x", pady=(0, 14))
        tk.Label(inner, text=title, bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_DISPLAY, 14, "bold"), anchor="w").pack(fill="x")
        tk.Label(inner, text=desc, bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 10), wraplength=340, justify="left", anchor="w").pack(fill="x", pady=(8, 18))
        self._btn(inner, btn_text, command, kind="primary").pack(anchor="w")
        return outer

    def show_login(self) -> None:
        self._clear_body()
        self._nav_button("Início", self.show_home)
        self._nav_button("Configurações", self.show_settings)

        wrap = tk.Frame(self.body, bg=COLORS["bg"])
        wrap.pack(expand=True)
        box = tk.Frame(wrap, bg=COLORS["surface"], padx=32, pady=28, highlightbackground=COLORS["border"], highlightthickness=1)
        box.pack()
        tk.Frame(box, bg=COLORS["gold"], height=2).pack(fill="x", pady=(0, 14))
        tk.Label(box, text="Acesso administrativo", bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_DISPLAY, 15, "bold")).pack(anchor="w")
        tk.Label(box, text=ORG_FULL, bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(2, 16))

        tk.Label(box, text="E-mail", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        email = ttk.Entry(box, width=42)
        email.pack(anchor="w", pady=(2, 10))
        email.insert(0, self.cfg.get("admin_email", ""))

        tk.Label(box, text="Senha", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        password = ttk.Entry(box, width=42, show="•")
        password.pack(anchor="w", pady=(2, 16))

        def do_login() -> None:
            cfg = load_config()
            if email.get().strip().lower() != str(cfg.get("admin_email", "")).lower() or password.get() != str(cfg.get("admin_password", "")):
                messagebox.showerror("Login", "E-mail ou senha incorretos.")
                return
            if not is_sheets_configured(cfg):
                messagebox.showwarning("Configuração", "Configure primeiro o Google Sheets.")
                self.show_settings()
                return
            self._logged_in = True
            self.show_admin()

        self._btn(box, "Entrar", do_login).pack(anchor="e")
        password.bind("<Return>", lambda _e: do_login())

    # ------------------------------------------------------------------
    # Configurações + site público
    # ------------------------------------------------------------------
    def show_settings(self) -> None:
        self._clear_body()
        self._nav_button("Início", self.show_home)

        outer = tk.Frame(self.body, bg=COLORS["bg"])
        outer.pack(fill="both", expand=True, padx=24, pady=16)
        tk.Label(outer, text="Configurações", bg=COLORS["bg"], fg=COLORS["primary"], font=(FONT_DISPLAY, 20, "bold")).pack(anchor="w")

        scroll = ScrollableFrame(outer, bg=COLORS["bg"])
        scroll.pack(fill="both", expand=True, pady=(8, 0))
        self._scroll = scroll
        wrap = scroll.inner
        cfg = load_config()

        form = tk.Frame(wrap, bg=COLORS["surface"], padx=18, pady=18, highlightbackground=COLORS["border"], highlightthickness=1)
        form.pack(fill="x", padx=2, pady=(0, 16))

        def labeled(row, label, width=72, show=None, value=""):
            tk.Label(form, text=label, bg=COLORS["surface"], fg=COLORS["muted"]).grid(row=row, column=0, sticky="w")
            ent = ttk.Entry(form, width=width, show=show)
            ent.grid(row=row + 1, column=0, sticky="we", pady=(2, 10))
            ent.insert(0, value)
            return ent

        sheet_id = labeled(0, "ID da planilha Google (admin / API)", value=cfg.get("spreadsheet_id", ""))
        site_url = labeled(
            2,
            "URL do site público (GitHub Pages / Cloudflare / Netlify) — QR fixo",
            value=cfg.get("public_site_url", "") or cfg.get("public_base_url", ""),
        )
        admin_email = labeled(4, "E-mail do administrador", width=40, value=cfg.get("admin_email", "admin@sinapesc.local"))
        admin_password = labeled(6, "Senha do administrador", width=40, show="•", value=cfg.get("admin_password", "sinapesc"))

        cred_label = tk.StringVar(
            value=(
                f"JSON: {cfg['credentials_json'].get('client_email')}"
                if isinstance(cfg.get("credentials_json"), dict)
                else "Nenhuma credencial carregada."
            )
        )
        tk.Label(form, textvariable=cred_label, bg=COLORS["surface"], fg=COLORS["accent"], font=(FONT_FAMILY, 9, "bold")).grid(row=8, column=0, sticky="w", pady=(0, 8))
        credentials_holder = {"json": cfg.get("credentials_json")}

        def pick_json() -> None:
            path = filedialog.askopenfilename(title="JSON da Conta de Serviço", filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
            if not path:
                return
            try:
                data = import_credentials_file(path)
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Credenciais", str(exc))
                return
            credentials_holder["json"] = data
            cred_label.set(f"JSON: {data.get('client_email')}")

        self._btn(form, "Importar JSON da Conta de Serviço…", pick_json, kind="primary").grid(row=9, column=0, sticky="w", pady=(0, 12))

        site_box = tk.Frame(form, bg=COLORS["surface_soft"], padx=14, pady=14)
        site_box.grid(row=10, column=0, sticky="we", pady=(0, 14))
        tk.Label(site_box, text="Site público online (Opção A — gratuito)", bg=COLORS["surface_soft"], fg=COLORS["primary"], font=(FONT_DISPLAY, 11, "bold")).pack(anchor="w")
        tk.Label(
            site_box,
            text=(
                "1) Compartilhe a planilha como Leitor (qualquer pessoa com o link)\n"
                "2) Publique a pasta site-publico/ (GitHub Pages)\n"
                "3) Cole a URL do site acima · 4) Gere os QRs permanentes\n"
                "O notebook NÃO precisa ficar ligado para a consulta no celular."
            ),
            bg=COLORS["surface_soft"], fg=COLORS["muted"], font=(FONT_FAMILY, 9), justify="left",
        ).pack(anchor="w", pady=(4, 10))
        site_status = tk.StringVar(
            value=(f"Site: {cfg.get('public_site_url')}" if cfg.get("public_site_url") else "Site ainda não configurado.")
        )
        tk.Label(site_box, textvariable=site_status, bg=COLORS["surface_soft"], fg=COLORS["accent"], font=(FONT_FAMILY, 9, "bold")).pack(anchor="w", pady=(0, 8))

        def gerar_qrs_site() -> None:
            # salva URL antes
            new_cfg = load_config()
            new_cfg["public_site_url"] = site_url.get().strip().rstrip("/")
            new_cfg["public_base_url"] = new_cfg["public_site_url"]
            if sheet_id.get().strip():
                new_cfg["spreadsheet_id"] = sheet_id.get().strip()
            save_config(new_cfg)
            self.cfg = new_cfg
            # sync config.js hint
            self._sync_site_config_js(new_cfg.get("spreadsheet_id", ""))

            def done(base, _mudou):
                site_status.set(f"QRs prontos → {base}")

            self._activate_link(force_new=True, on_done=done)

        def abrir_pasta_qr() -> None:
            import os
            import subprocess

            path = str(qr_dir())
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", path])

        row = tk.Frame(site_box, bg=COLORS["surface_soft"])
        row.pack(anchor="w")
        self._btn(row, "Gerar QRs do site", gerar_qrs_site).pack(side="left", padx=(0, 6))
        self._btn(row, "QR Consulta CPF", self._show_qr_consulta, kind="primary").pack(side="left", padx=(0, 6))
        self._btn(row, "Pasta dos QRs", abrir_pasta_qr, kind="ghost").pack(side="left")

        def save() -> None:
            new_cfg = load_config()
            new_cfg["spreadsheet_id"] = sheet_id.get().strip()
            new_cfg["public_site_url"] = site_url.get().strip().rstrip("/")
            if new_cfg["public_site_url"]:
                new_cfg["public_base_url"] = new_cfg["public_site_url"]
            new_cfg["admin_email"] = admin_email.get().strip()
            new_cfg["admin_password"] = admin_password.get()
            if credentials_holder["json"]:
                new_cfg["credentials_json"] = credentials_holder["json"]
                new_cfg["service_account_email"] = credentials_holder["json"].get("client_email", "")
                new_cfg["private_key"] = credentials_holder["json"].get("private_key", "")
            if not new_cfg["spreadsheet_id"]:
                messagebox.showerror("Configuração", "Informe o ID da planilha.")
                return
            if not is_sheets_configured(new_cfg):
                messagebox.showerror("Configuração", "Importe o JSON da Conta de Serviço.")
                return
            save_config(new_cfg)
            self.cfg = new_cfg
            self.service = None
            self._sync_site_config_js(new_cfg.get("spreadsheet_id", ""))
            site_status.set(
                f"Site: {new_cfg['public_site_url']}" if new_cfg.get("public_site_url") else "Site ainda não configurado."
            )
            messagebox.showinfo("Configuração", "Salvo com sucesso.")

        def test_connection() -> None:
            save()
            try:
                svc = self._ensure_service()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Teste", str(exc))
                return

            def work():
                svc.client.ensure_tabs()
                return len(svc.get_all_pessoas())

            self._run_bg(
                work,
                lambda n: messagebox.showinfo("Teste", f"Conexão OK!\nAssociados: {n}"),
                lambda e: messagebox.showerror("Teste", str(e)),
                "Testando…",
            )

        actions = tk.Frame(form, bg=COLORS["surface"])
        actions.grid(row=13, column=0, sticky="w")
        self._btn(actions, "Salvar", save).pack(side="left", padx=(0, 8))
        self._btn(actions, "Testar conexão", test_connection, kind="primary").pack(side="left")
        form.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------------
    def show_admin(self) -> None:
        self._lista_mode = False
        if not self._logged_in:
            self.show_login()
            return

        self._clear_body()
        self._nav_button("Início", self.show_home)
        self._nav_button("Lista pública", self.show_lista)
        self._nav_button("QR Consulta", self._show_qr_consulta)
        self._nav_button("Configurações", self.show_settings)
        self._nav_button("Sair", self._logout)

        wrap = tk.Frame(self.body, bg=COLORS["bg"])
        wrap.pack(fill="both", expand=True, padx=22, pady=14)

        top = tk.Frame(wrap, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="Sócios", bg=COLORS["bg"], fg=COLORS["primary"], font=(FONT_DISPLAY, 20, "bold")).pack(side="left")
        self.admin_count = tk.StringVar(value="")
        tk.Label(top, textvariable=self.admin_count, bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT_FAMILY, 10)).pack(side="left", padx=12)
        tk.Label(top, text="Clique no nome para abrir o REAP", bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(side="left")

        self._btn(top, "+ Novo sócio", lambda: self._dialog_pessoa(), kind="accent").pack(side="right")
        self._btn(top, "Cadastro em lote", self._dialog_lote, kind="primary").pack(side="right", padx=8)
        self._btn(top, "Atualizar", self._load_admin_data, kind="ghost").pack(side="right", padx=4)

        search_row = tk.Frame(wrap, bg=COLORS["bg"])
        search_row.pack(fill="x", pady=(0, 8))
        tk.Label(search_row, text="Buscar", bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.search_var, width=42).pack(side="left", padx=8)
        self.search_var.trace_add("write", lambda *_: self._render_admin_list())

        self._scroll = ScrollableFrame(wrap, bg=COLORS["bg"])
        self._scroll.pack(fill="both", expand=True)
        self.admin_list = self._scroll.inner
        self._load_admin_data()

    def _logout(self) -> None:
        self._logged_in = False
        self._expanded_ids.clear()
        self.show_home()

    def _load_admin_data(self) -> None:
        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            self.show_settings()
            return

        def work():
            return svc.get_all_pessoas_com_reap()

        def ok(pessoas: List[PessoaComReap]) -> None:
            self._pessoas = pessoas
            if hasattr(self, "admin_count"):
                self.admin_count.set(f"{len(pessoas)} cadastrado(s)")
            self._render_admin_list()

        self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Carregando sócios…")

    def _filtered_pessoas(self) -> List[PessoaComReap]:
        if not hasattr(self, "search_var"):
            return self._pessoas
        q = self.search_var.get().strip().lower()
        digits = only_digits(q)
        if not q:
            return self._pessoas
        return [p for p in self._pessoas if q in p.nome.lower() or (digits and digits in p.cpf)]

    def _render_admin_list(self) -> None:
        if not hasattr(self, "admin_list") or not self.admin_list.winfo_exists():
            return
        for child in self.admin_list.winfo_children():
            child.destroy()
        pessoas = self._filtered_pessoas()
        if not pessoas:
            tk.Label(
                self.admin_list,
                text="Nenhum sócio encontrado." if self._pessoas else "Nenhum sócio cadastrado.",
                bg=COLORS["bg"], fg=COLORS["muted"],
            ).pack(anchor="w", pady=20)
            return
        for pessoa in pessoas:
            self._pessoa_row(self.admin_list, pessoa, editable=True)

    def _toggle_expand(self, person_id: str) -> None:
        if person_id in self._expanded_ids:
            self._expanded_ids.discard(person_id)
        else:
            self._expanded_ids.add(person_id)
        y = 0.0
        if self._scroll is not None:
            try:
                y = self._scroll.canvas.yview()[0]
            except tk.TclError:
                y = 0.0
        if self._lista_mode:
            self._render_lista_rows()
        else:
            self._render_admin_list()
        if self._scroll is not None:
            self.after(10, lambda: self._scroll.canvas.yview_moveto(y))

    def _pessoa_row(self, parent, pessoa: PessoaComReap, *, editable: bool, mask_cpf: bool = False) -> None:
        expanded = pessoa.id in self._expanded_ids
        card = tk.Frame(parent, bg=COLORS["surface"], padx=14, pady=10, highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=5, padx=2)

        head = tk.Frame(card, bg=COLORS["surface"])
        head.pack(fill="x")

        avatar = tk.Label(
            head, text=get_initials(pessoa.nome), bg=COLORS["primary"], fg=COLORS["primary_fg"],
            width=3, font=(FONT_FAMILY, 11, "bold"), padx=8, pady=8,
        )
        avatar.pack(side="left", padx=(0, 12))

        info = tk.Frame(head, bg=COLORS["surface"], cursor="hand2")
        info.pack(side="left", fill="x", expand=True)

        chevron = "▾" if expanded else "▸"
        name_lbl = tk.Label(
            info, text=f"{chevron}  {pessoa.nome}", bg=COLORS["surface"], fg=COLORS["primary"],
            font=(FONT_DISPLAY, 11, "bold"), anchor="w", cursor="hand2",
        )
        name_lbl.pack(anchor="w")
        cpf_txt = format_cpf_masked(pessoa.cpf) if mask_cpf else format_cpf(pessoa.cpf)
        sub = tk.Label(info, text=f"CPF: {cpf_txt}", bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9), anchor="w", cursor="hand2")
        sub.pack(anchor="w")

        def toggle(_e=None, pid=pessoa.id):
            self._toggle_expand(pid)

        for w in (info, name_lbl, sub, avatar):
            w.bind("<Button-1>", toggle)

        if editable:
            actions = tk.Frame(head, bg=COLORS["surface"])
            actions.pack(side="right")
            self._btn(actions, "QR", lambda p=pessoa: self._show_qr_pessoa(p), kind="ghost", padx=8, pady=4, font_size=9, bold=False).pack(side="left", padx=2)
            self._btn(actions, "Editar", lambda p=pessoa: self._dialog_pessoa(p), kind="ghost", padx=8, pady=4, font_size=9, bold=False).pack(side="left", padx=2)
            self._btn(actions, "Excluir", lambda p=pessoa: self._delete_pessoa(p), kind="danger", padx=8, pady=4, font_size=9, bold=False).pack(side="left", padx=2)

        if not expanded:
            return

        detail = tk.Frame(card, bg=COLORS["surface"])
        detail.pack(fill="x", pady=(12, 0))
        tk.Frame(detail, bg=COLORS["border_soft"], height=1).pack(fill="x", pady=(0, 10))

        if not pessoa.anos:
            tk.Label(detail, text="Nenhum ano registrado.", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        for ano in pessoa.anos:
            ano_frame = tk.Frame(detail, bg=COLORS["surface"])
            ano_frame.pack(fill="x", pady=(6, 0))
            tk.Label(ano_frame, text=f"Ano {ano.ano}", bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_DISPLAY, 10, "bold")).pack(anchor="w")
            self._month_grid(ano_frame, pessoa.id, ano.ano, ano.meses, editable=editable)

        if editable:
            add_row = tk.Frame(detail, bg=COLORS["surface"])
            add_row.pack(fill="x", pady=(12, 0))
            year_var = tk.StringVar(value=str(__import__("datetime").datetime.now().year + 1))
            ttk.Entry(add_row, textvariable=year_var, width=8).pack(side="left")
            self._btn(add_row, "Adicionar ano", lambda p=pessoa, y=year_var: self._add_ano(p, y.get()), kind="ghost", padx=10, pady=4, font_size=9).pack(side="left", padx=8)

    def _month_grid(self, parent, person_id: str, ano: int, meses: dict, *, editable: bool) -> None:
        grid = tk.Frame(parent, bg=COLORS["surface"])
        grid.pack(fill="x", pady=4)
        for i, mes in enumerate(MESES):
            pago = bool(meses.get(mes))
            bg = COLORS["month_on"] if pago else COLORS["month_off"]
            fg = COLORS["success"] if pago else COLORS["muted"]
            mark = "✓" if pago else "·"
            if editable:
                btn = tk.Button(
                    grid, text=f"{mes.upper()}\n{mark}", width=5, height=2, bg=bg, fg=fg, relief="flat",
                    font=(FONT_FAMILY, 8, "bold"), cursor="hand2",
                    command=lambda m=mes, p=pago: self._toggle_mes(person_id, ano, m, not p),
                )
            else:
                btn = tk.Label(grid, text=f"{mes.upper()}\n{mark}", width=5, height=2, bg=bg, fg=fg, font=(FONT_FAMILY, 8, "bold"))
            btn.grid(row=i // 6, column=i % 6, padx=3, pady=3, sticky="nsew")
            btn.bind("<Enter>", lambda _e, t=MESES_LABEL[mes]: self.status.set(t))

    def _toggle_mes(self, person_id: str, ano: int, mes: MesKey, novo: bool) -> None:
        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return
        self._expanded_ids.add(person_id)

        def work():
            svc.toggle_mes(person_id, ano, mes, novo)
            return True

        self._run_bg(work, lambda _: self._load_admin_data(), lambda e: messagebox.showerror("Erro", str(e)), f"Atualizando {mes}/{ano}…")

    def _dialog_pessoa(self, pessoa: Optional[PessoaComReap] = None) -> None:
        win = tk.Toplevel(self)
        win.title("Editar sócio" if pessoa else "Novo sócio")
        win.configure(bg=COLORS["surface"])
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Nome completo", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=16, pady=(16, 2))
        nome = ttk.Entry(win, width=44)
        nome.pack(padx=16)
        if pessoa:
            nome.insert(0, pessoa.nome)

        tk.Label(win, text="CPF (11 dígitos)", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=16, pady=(10, 2))
        cpf = ttk.Entry(win, width=44)
        cpf.pack(padx=16)
        if pessoa:
            cpf.insert(0, pessoa.cpf)

        def save() -> None:
            n = nome.get().strip()
            c = only_digits(cpf.get())
            if not n:
                messagebox.showerror("Validação", "Informe o nome completo.", parent=win)
                return
            if len(c) != 11:
                messagebox.showerror("Validação", "CPF deve conter 11 dígitos.", parent=win)
                return
            try:
                svc = self._ensure_service()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Sheets", str(exc), parent=win)
                return

            def work():
                if pessoa:
                    svc.update_pessoa(pessoa.id, n, c)
                    return pessoa.id
                return svc.add_pessoa(n, c).id

            def ok(pid: str) -> None:
                win.destroy()
                self._expanded_ids.add(pid)
                self._load_admin_data()

            self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e), parent=win), "Salvando…")

        self._btn(win, "Salvar", save).pack(pady=16)

    def _dialog_lote(self) -> None:
        win = tk.Toplevel(self)
        win.title("Cadastro em lote")
        win.configure(bg=COLORS["surface"])
        win.geometry("620x480")
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Cadastro de sócios em lote", bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_DISPLAY, 14, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(
            win,
            text="Uma pessoa por linha. Formatos: Nome;CPF   ou   Nome,CPF   ou   Nome[TAB]CPF",
            bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9),
        ).pack(anchor="w", padx=16)

        text = tk.Text(win, height=16, wrap="none", font=(FONT_FAMILY, 10), bg=COLORS["surface_soft"], relief="solid", borderwidth=1)
        text.pack(fill="both", expand=True, padx=16, pady=10)

        def load_file() -> None:
            path = filedialog.askopenfilename(
                parent=win,
                title="Importar CSV/TXT",
                filetypes=[("Texto/CSV", "*.csv *.txt"), ("Todos", "*.*")],
            )
            if not path:
                return
            raw = open(path, encoding="utf-8-sig", errors="replace").read()
            text.delete("1.0", "end")
            text.insert("1.0", raw)

        def parse_lines(raw: str) -> List[tuple[str, str]]:
            itens: List[tuple[str, str]] = []
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.lower().startswith("nome"):
                    continue
                if ";" in line:
                    parts = line.split(";", 1)
                elif "\t" in line:
                    parts = line.split("\t", 1)
                elif "," in line:
                    # última vírgula separa CPF se houver várias no nome
                    parts = line.rsplit(",", 1)
                else:
                    parts = re.split(r"\s{2,}", line, maxsplit=1)
                if len(parts) < 2:
                    continue
                itens.append((parts[0].strip().strip('"'), parts[1].strip().strip('"')))
            return itens

        def salvar() -> None:
            itens = parse_lines(text.get("1.0", "end"))
            if not itens:
                messagebox.showerror("Lote", "Nenhuma linha válida encontrada.", parent=win)
                return
            try:
                svc = self._ensure_service()
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Sheets", str(exc), parent=win)
                return

            def work():
                return svc.add_pessoas_lote(itens)

            def ok(result: dict) -> None:
                for pid in result.get("ids", []):
                    self._expanded_ids.add(pid)
                msg = f"Cadastrados: {result.get('ok', 0)}"
                erros = result.get("erros") or []
                if erros:
                    msg += "\n\nAvisos:\n" + "\n".join(erros[:12])
                    if len(erros) > 12:
                        msg += f"\n… e mais {len(erros) - 12}."
                messagebox.showinfo("Lote", msg, parent=win)
                win.destroy()
                self._load_admin_data()

            self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e), parent=win), "Cadastrando lote…")

        bar = tk.Frame(win, bg=COLORS["surface"])
        bar.pack(fill="x", padx=16, pady=(0, 16))
        self._btn(bar, "Importar arquivo…", load_file, kind="ghost").pack(side="left")
        self._btn(bar, "Cadastrar lote", salvar).pack(side="right")

    def _delete_pessoa(self, pessoa: PessoaComReap) -> None:
        if not messagebox.askyesno("Remover", f"Remover {pessoa.nome} e todo o histórico de REAP?"):
            return
        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return

        def work():
            svc.delete_pessoa(pessoa.id)
            return True

        def ok(_: bool) -> None:
            self._expanded_ids.discard(pessoa.id)
            self._load_admin_data()

        self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Removendo…")

    def _add_ano(self, pessoa: PessoaComReap, ano_txt: str) -> None:
        try:
            ano = int(ano_txt)
        except ValueError:
            messagebox.showerror("Ano", "Informe um ano válido.")
            return
        if ano < 2000 or ano > 2100:
            messagebox.showerror("Ano", "Informe um ano entre 2000 e 2100.")
            return
        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return
        self._expanded_ids.add(pessoa.id)

        def work():
            svc.add_ano(pessoa.id, ano)
            return True

        self._run_bg(work, lambda _: self._load_admin_data(), lambda e: messagebox.showerror("Erro", str(e)), f"Adicionando {ano}…")

    # ------------------------------------------------------------------
    # Lista + QR
    # ------------------------------------------------------------------
    def show_lista(self) -> None:
        self._clear_body()
        self._lista_mode = True
        self._nav_button("Início", self.show_home)
        if self._logged_in:
            self._nav_button("Admin", self.show_admin)
        self._nav_button("QR Consulta CPF", self._show_qr_consulta)
        self._nav_button("QR Lista", self._show_qr_lista)
        self._nav_button("Configurações", self.show_settings)

        wrap = tk.Frame(self.body, bg=COLORS["bg"])
        wrap.pack(fill="both", expand=True, padx=22, pady=14)

        top = tk.Frame(wrap, bg=COLORS["bg"])
        top.pack(fill="x")
        tk.Label(top, text="Lista pública de REAP", bg=COLORS["bg"], fg=COLORS["primary"], font=(FONT_DISPLAY, 20, "bold")).pack(side="left")
        self._btn(top, "QR Consulta CPF", self._show_qr_consulta).pack(side="right", padx=(6, 0))
        self._btn(top, "QR Lista", self._show_qr_lista, kind="primary").pack(side="right")

        tk.Label(
            wrap,
            text="Clique no nome para ver os meses. O QR de Consulta por CPF é o ideal para imprimir na sede.",
            bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT_FAMILY, 10),
        ).pack(anchor="w", pady=(4, 10))

        self._scroll = ScrollableFrame(wrap, bg=COLORS["bg"])
        self._scroll.pack(fill="both", expand=True)
        self.lista_frame = self._scroll.inner

        try:
            self._ensure_public_server()
        except Exception:
            pass

        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            tk.Label(self.lista_frame, text=str(exc), bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")
            return

        def work():
            return svc.get_all_pessoas_com_reap()

        def ok(pessoas: List[PessoaComReap]) -> None:
            self._pessoas = pessoas
            self._render_lista_rows()

        self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Carregando lista…")

    def _render_lista_rows(self) -> None:
        if not hasattr(self, "lista_frame") or not self.lista_frame.winfo_exists():
            return
        for child in self.lista_frame.winfo_children():
            child.destroy()
        if not self._pessoas:
            tk.Label(self.lista_frame, text="Nenhum sócio cadastrado.", bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")
            return
        for p in self._pessoas:
            self._pessoa_row(self.lista_frame, p, editable=False, mask_cpf=True)

    def _show_qr_consulta(self) -> None:
        base = preferred_public_base()
        if not base:
            messagebox.showwarning(
                "Site público",
                "Configure a URL do site público em Configurações antes de gerar o QR.",
            )
            self.show_settings()
            return
        ensure_stable_qrs(base, force=False)
        self._qr_dialog(
            urls_for(base)["consulta"],
            title=f"{ORG_SHORT} — Consulta por CPF",
            subtitle="QR permanente do site público. O associado digita o CPF e vê só os próprios REAPs.",
            kind="consulta",
        )

    def _show_qr_lista(self) -> None:
        base = preferred_public_base()
        if not base:
            messagebox.showwarning(
                "Site público",
                "Configure a URL do site público em Configurações antes de gerar o QR.",
            )
            self.show_settings()
            return
        ensure_stable_qrs(base, force=False)
        self._qr_dialog(
            urls_for(base)["lista"],
            title=f"{ORG_SHORT} — Lista pública",
            subtitle="Lista geral no site público. Mesmo QR enquanto a URL do site não mudar.",
            kind="lista",
        )

    def _show_qr_pessoa(self, pessoa: PessoaComReap) -> None:
        base = preferred_public_base()
        if not base:
            messagebox.showwarning(
                "Site público",
                "Configure a URL do site público em Configurações antes de gerar o QR.",
            )
            self.show_settings()
            return
        ensure_stable_qrs(base, pessoas=[pessoa], force=False)
        self._qr_dialog(
            urls_for(base, pessoa)["pessoa"],
            title=f"{ORG_SHORT} — {pessoa.nome}",
            subtitle="Comprovante individual no site público · QR permanente.",
            kind="pessoa",
            person_id=pessoa.id,
        )

    def _qr_dialog(
        self,
        url: str,
        *,
        title: str,
        subtitle: str,
        kind: str = "lista",
        person_id: str = "",
    ) -> None:
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=COLORS["surface"])
        win.transient(self)
        win.grab_set()

        state = {"url": url}

        tk.Frame(win, bg=COLORS["gold"], height=3).pack(fill="x")
        head = tk.Frame(win, bg=COLORS["primary"], padx=16, pady=12)
        head.pack(fill="x")
        fish = load_fish(win, size=56)
        if fish is not None:
            win._fish = fish  # keep ref
            tk.Label(head, image=fish, bg=COLORS["primary"]).pack(side="right")
        tk.Label(head, text=title, bg=COLORS["primary"], fg=COLORS["foam"], font=(FONT_DISPLAY, 13, "bold")).pack(anchor="w")
        tk.Label(win, text=subtitle, bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9), wraplength=400).pack(padx=16, pady=(12, 0))
        qr_label = tk.Label(win, bg=COLORS["surface"])
        qr_label.pack(pady=12)
        url_lbl = tk.Label(win, text=url, bg=COLORS["surface"], fg=COLORS["accent"], font=(FONT_FAMILY, 8), wraplength=420)
        url_lbl.pack(padx=16)
        tk.Label(
            win,
            text=f"Arquivos permanentes em: {qr_dir()}",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 8),
            wraplength=420,
        ).pack(padx=16, pady=(4, 0))

        def render(u: str) -> None:
            state["url"] = u
            url_lbl.configure(text=u)
            try:
                poster = make_qr_image(u, title=title, subtitle=subtitle)
                photo = pil_to_tk(poster, max_size=(300, 340))
                self._qr_photo = photo
                qr_label.configure(image=photo)
            except Exception as exc:  # noqa: BLE001
                qr_label.configure(text=f"Falha ao gerar QR: {exc}", image="")

        render(url)

        def save() -> None:
            default = {
                "consulta": "sinapesc-consulta-cpf-qr.png",
                "lista": "sinapesc-lista-qr.png",
                "pessoa": f"sinapesc-pessoa-{person_id[:8] or 'socio'}-qr.png",
            }.get(kind, "sinapesc-qr.png")
            vault_map = {
                "consulta": path_for_consulta(),
                "lista": path_for_lista(),
                "pessoa": path_for_pessoa(person_id) if person_id else None,
            }
            suggested = vault_map.get(kind)
            path = filedialog.asksaveasfilename(
                parent=win,
                title="Salvar QR permanente",
                defaultextension=".png",
                filetypes=[("PNG", "*.png")],
                initialfile=default,
            )
            if not path:
                return
            if suggested and suggested.exists():
                from shutil import copyfile

                copyfile(suggested, path)
            else:
                save_qr_png(state["url"], path, title=title, subtitle=subtitle)
            messagebox.showinfo("QR", f"Salvo em:\n{path}\n\nEste QR permanece válido com a URL do site público.", parent=win)

        def copy_url() -> None:
            win.clipboard_clear()
            win.clipboard_append(state["url"])
            self.status.set("URL copiada.")

        btns = tk.Frame(win, bg=COLORS["surface"])
        btns.pack(pady=14)
        self._btn(btns, "Salvar PNG", save).pack(side="left", padx=5)
        self._btn(btns, "Copiar link", copy_url, kind="primary").pack(side="left", padx=5)
        self._btn(btns, "Fechar", win.destroy, kind="ghost").pack(side="left", padx=5)


def _asset(name: str) -> str:
    from pathlib import Path
    import sys

    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return str(base / "assets" / name)
