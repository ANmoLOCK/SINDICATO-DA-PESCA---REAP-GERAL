"""
Interface gráfica desktop do Sinapesc — Controle de REAP.

Melhorias:
  - Scroll estável (sem bind_all vazando)
  - Lista compacta: toque/clique no nome abre anos + REAPs
  - Lista pública com QR imprimível + página online (celular)
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional, Set

from config import (
    import_credentials_file,
    is_sheets_configured,
    load_config,
    save_config,
)
from sheets import MESES, MESES_LABEL, MesKey, PessoaComReap, SheetsConfigError, SheetsService
from ui.formatters import format_cpf, format_cpf_masked, get_initials, only_digits
from ui.public_web import public_base_url, start_public_server
from ui.qrutil import make_qr_image, pil_to_tk, save_qr_png
from ui.scroll import ScrollableFrame
from ui.theme import COLORS, FONT_FAMILY


class SinapescApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sinapesc — Controle de REAP")
        self.geometry("980x680")
        self.minsize(840, 560)
        self.configure(bg=COLORS["bg"])

        self.cfg = load_config()
        self.service: Optional[SheetsService] = None
        self._logged_in = False
        self._pessoas: List[PessoaComReap] = []
        self._expanded_ids: Set[str] = set()
        self._scroll: Optional[ScrollableFrame] = None
        self._qr_photo = None  # evita GC do PhotoImage

        self._setup_style()
        self._build_shell()
        self.show_home()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        try:
            self.iconphoto(True, tk.PhotoImage(file=_asset("icon.png")))
        except Exception:
            pass

    def _on_close(self) -> None:
        if self._scroll is not None:
            try:
                self._scroll.destroy()
            except tk.TclError:
                pass
        self.destroy()

    # ------------------------------------------------------------------
    # Estilo
    # ------------------------------------------------------------------
    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", font=(FONT_FAMILY, 10), background=COLORS["bg"])
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Header.TFrame", background=COLORS["primary"])
        style.configure(
            "Header.TLabel",
            background=COLORS["primary"],
            foreground=COLORS["primary_fg"],
            font=(FONT_FAMILY, 14, "bold"),
        )
        style.configure(
            "HeaderSub.TLabel",
            background=COLORS["primary"],
            foreground="#B8C9D8",
            font=(FONT_FAMILY, 9),
        )
        style.configure(
            "Title.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["primary"],
            font=(FONT_FAMILY, 18, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
            font=(FONT_FAMILY, 10),
        )

    def _build_shell(self) -> None:
        self.header = ttk.Frame(self, style="Header.TFrame")
        self.header.pack(fill="x")

        inner = ttk.Frame(self.header, style="Header.TFrame")
        inner.pack(fill="x", padx=20, pady=14)

        left = ttk.Frame(inner, style="Header.TFrame")
        left.pack(side="left")
        ttk.Label(left, text="Sinapesc", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            left,
            text="Sindicato Nacional dos Pescadores — Controle de REAP",
            style="HeaderSub.TLabel",
        ).pack(anchor="w")

        self.nav = ttk.Frame(inner, style="Header.TFrame")
        self.nav.pack(side="right")

        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)

        self.status = tk.StringVar(value="Pronto.")
        tk.Label(
            self,
            textvariable=self.status,
            anchor="w",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
            padx=12,
            pady=6,
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
            raise SheetsConfigError(
                "Google Sheets ainda não configurado. Abra Configurações e informe as credenciais."
            )
        self.service = SheetsService.from_config(self.cfg)
        return self.service

    def _ensure_public_server(self) -> str:
        """Sobe o servidor local e devolve a URL que deve ir no QR."""
        self.cfg = load_config()
        svc = self._ensure_service()

        def fetch():
            return svc.get_all_pessoas_com_reap()

        port = int(self.cfg.get("public_port") or 8765)
        start_public_server(fetch, port=port)
        configured = str(self.cfg.get("public_base_url") or "").strip()
        return public_base_url(configured)

    def _nav_button(self, text: str, command: Callable) -> None:
        tk.Button(
            self.nav,
            text=text,
            command=command,
            bg=COLORS["accent"],
            fg=COLORS["accent_fg"],
            activebackground="#187567",
            activeforeground=COLORS["accent_fg"],
            relief="flat",
            padx=10,
            pady=4,
            font=(FONT_FAMILY, 9, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=4)

    # ------------------------------------------------------------------
    # Home / Login
    # ------------------------------------------------------------------
    def show_home(self) -> None:
        self._lista_mode = False
        self._clear_body()
        self._nav_button("Configurações", self.show_settings)

        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True, padx=40, pady=36)

        ttk.Label(wrap, text="Acompanhamento mensal da contribuição REAP", style="Title.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            wrap,
            text="Cadastre associados, marque meses pagos e compartilhe a lista pública por QR Code.",
            style="Muted.TLabel",
            wraplength=700,
        ).pack(anchor="w", pady=(8, 28))

        cards = ttk.Frame(wrap)
        cards.pack(fill="x")
        self._home_card(
            cards,
            "Área administrativa",
            "Cadastre associados e marque os meses pagos do REAP.",
            "Entrar como administrador",
            self.show_login,
        ).pack(side="left", fill="both", expand=True, padx=(0, 12))
        self._home_card(
            cards,
            "Lista pública + QR",
            "Consulte REAPs e imprima o QR para qualquer pessoa escanear no celular.",
            "Ver lista pública",
            self.show_lista,
        ).pack(side="left", fill="both", expand=True, padx=(12, 0))

    def _home_card(self, parent, title, desc, btn_text, command) -> tk.Frame:
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=COLORS["surface"], padx=18, pady=18)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=title, bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_FAMILY, 13, "bold"), anchor="w").pack(fill="x")
        tk.Label(inner, text=desc, bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 10), wraplength=320, justify="left", anchor="w").pack(fill="x", pady=(8, 16))
        tk.Button(
            inner, text=btn_text, command=command, bg=COLORS["primary"], fg=COLORS["primary_fg"],
            activebackground="#142844", relief="flat", padx=12, pady=8, font=(FONT_FAMILY, 10, "bold"), cursor="hand2",
        ).pack(anchor="w")
        return outer

    def show_login(self) -> None:
        self._clear_body()
        self._nav_button("Início", self.show_home)
        self._nav_button("Configurações", self.show_settings)

        wrap = ttk.Frame(self.body)
        wrap.pack(expand=True)
        box = tk.Frame(wrap, bg=COLORS["surface"], padx=28, pady=24, highlightbackground=COLORS["border"], highlightthickness=1)
        box.pack()

        tk.Label(box, text="Login do administrador", bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_FAMILY, 14, "bold")).pack(anchor="w")
        tk.Label(box, text="Use o e-mail e senha definidos em Configurações.", bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(anchor="w", pady=(4, 16))

        tk.Label(box, text="E-mail", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        email = ttk.Entry(box, width=40)
        email.pack(anchor="w", pady=(2, 10))
        email.insert(0, self.cfg.get("admin_email", ""))

        tk.Label(box, text="Senha", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        password = ttk.Entry(box, width=40, show="•")
        password.pack(anchor="w", pady=(2, 16))

        def do_login() -> None:
            cfg = load_config()
            if email.get().strip().lower() != str(cfg.get("admin_email", "")).lower() or password.get() != str(cfg.get("admin_password", "")):
                messagebox.showerror("Login", "E-mail ou senha incorretos.")
                return
            if not is_sheets_configured(cfg):
                messagebox.showwarning("Configuração", "Configure primeiro a integração com o Google Sheets.")
                self.show_settings()
                return
            self._logged_in = True
            self.show_admin()

        tk.Button(box, text="Entrar", command=do_login, bg=COLORS["accent"], fg=COLORS["accent_fg"], relief="flat", padx=16, pady=8, font=(FONT_FAMILY, 10, "bold"), cursor="hand2").pack(anchor="e")
        password.bind("<Return>", lambda _e: do_login())

    # ------------------------------------------------------------------
    # Configurações
    # ------------------------------------------------------------------
    def show_settings(self) -> None:
        self._clear_body()
        self._nav_button("Início", self.show_home)

        outer = ttk.Frame(self.body)
        outer.pack(fill="both", expand=True, padx=24, pady=16)
        ttk.Label(outer, text="Configuração", style="Title.TLabel").pack(anchor="w")

        scroll = ScrollableFrame(outer, bg=COLORS["bg"])
        scroll.pack(fill="both", expand=True, pady=(8, 0))
        self._scroll = scroll
        wrap = scroll.inner

        guide = tk.Text(wrap, height=8, wrap="word", bg="#F4FAF8", fg=COLORS["primary"], font=(FONT_FAMILY, 9), relief="solid", borderwidth=1, padx=12, pady=10)
        guide.pack(fill="x", pady=(0, 14), padx=2)
        guide.insert(
            "1.0",
            "GOOGLE SHEETS\n"
            "1) Ative Google Sheets API no Cloud Console\n"
            "2) Crie Conta de Serviço e baixe o JSON\n"
            "3) Compartilhe a planilha com o client_email (Editor)\n"
            "4) Cole o ID da planilha e importe o JSON\n\n"
            "QR / LISTA ONLINE\n"
            "O programa sobe uma página em http://SEU-IP:8765 — o celular na mesma rede lê os REAPs ao vivo.\n"
            "Se tiver URL pública (túnel/host), informe em 'URL pública do QR'.",
        )
        guide.configure(state="disabled")

        form = tk.Frame(wrap, bg=COLORS["surface"], padx=16, pady=16, highlightbackground=COLORS["border"], highlightthickness=1)
        form.pack(fill="x", padx=2, pady=(0, 20))
        cfg = load_config()

        def labeled_entry(row, label, width=70, show=None, value=""):
            tk.Label(form, text=label, bg=COLORS["surface"], fg=COLORS["muted"]).grid(row=row, column=0, sticky="w")
            ent = ttk.Entry(form, width=width, show=show)
            ent.grid(row=row + 1, column=0, sticky="we", pady=(2, 10))
            ent.insert(0, value)
            return ent

        sheet_id = labeled_entry(0, "ID da planilha", value=cfg.get("spreadsheet_id", ""))
        public_url = labeled_entry(2, "URL pública do QR (opcional, ex.: https://meu-tunel.exemplo)", value=cfg.get("public_base_url", ""))
        public_port = labeled_entry(4, "Porta do servidor local da lista", width=12, value=str(cfg.get("public_port") or 8765))
        admin_email = labeled_entry(6, "E-mail do administrador", width=40, value=cfg.get("admin_email", "admin@sinapesc.local"))
        admin_password = labeled_entry(8, "Senha do administrador", width=40, show="•", value=cfg.get("admin_password", "sinapesc"))

        cred_label = tk.StringVar(
            value=(
                f"JSON carregado: {cfg['credentials_json'].get('client_email')}"
                if isinstance(cfg.get("credentials_json"), dict)
                else "Nenhuma credencial carregada ainda."
            )
        )
        tk.Label(form, textvariable=cred_label, bg=COLORS["surface"], fg=COLORS["accent"], font=(FONT_FAMILY, 9, "bold")).grid(row=10, column=0, sticky="w", pady=(0, 8))
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
            cred_label.set(f"JSON carregado: {data.get('client_email')}")

        tk.Button(form, text="Importar JSON da Conta de Serviço…", command=pick_json, bg=COLORS["primary"], fg=COLORS["primary_fg"], relief="flat", padx=10, pady=6, cursor="hand2").grid(row=11, column=0, sticky="w", pady=(0, 14))

        def save() -> None:
            new_cfg = load_config()
            new_cfg["spreadsheet_id"] = sheet_id.get().strip()
            new_cfg["public_base_url"] = public_url.get().strip()
            try:
                new_cfg["public_port"] = int(public_port.get().strip() or "8765")
            except ValueError:
                messagebox.showerror("Configuração", "Porta inválida.")
                return
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
                lambda exc: messagebox.showerror("Teste", str(exc)),
                "Testando conexão…",
            )

        actions = tk.Frame(form, bg=COLORS["surface"])
        actions.grid(row=12, column=0, sticky="w")
        tk.Button(actions, text="Salvar", command=save, bg=COLORS["accent"], fg=COLORS["accent_fg"], relief="flat", padx=14, pady=7, font=(FONT_FAMILY, 10, "bold"), cursor="hand2").pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Testar conexão", command=test_connection, bg=COLORS["primary"], fg=COLORS["primary_fg"], relief="flat", padx=14, pady=7, cursor="hand2").pack(side="left")
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
        self._nav_button("QR lista", self._show_qr_lista)
        self._nav_button("Configurações", self.show_settings)
        self._nav_button("Sair", self._logout)

        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True, padx=20, pady=12)

        top = ttk.Frame(wrap)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Associados", style="Title.TLabel").pack(side="left")
        self.admin_count = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.admin_count, style="Muted.TLabel").pack(side="left", padx=12)
        ttk.Label(top, text="Clique no nome para abrir anos/REAP", style="Muted.TLabel").pack(side="left", padx=8)

        tk.Button(top, text="+ Novo associado", command=lambda: self._dialog_pessoa(), bg=COLORS["accent"], fg=COLORS["accent_fg"], relief="flat", padx=12, pady=6, font=(FONT_FAMILY, 10, "bold"), cursor="hand2").pack(side="right")
        tk.Button(top, text="Atualizar", command=self._load_admin_data, bg=COLORS["primary"], fg=COLORS["primary_fg"], relief="flat", padx=10, pady=6, cursor="hand2").pack(side="right", padx=8)

        search_row = ttk.Frame(wrap)
        search_row.pack(fill="x", pady=(0, 8))
        ttk.Label(search_row, text="Buscar:", style="Muted.TLabel").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.search_var, width=40).pack(side="left", padx=8)
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
                self.admin_count.set(f"{len(pessoas)} associado(s)")
            self._render_admin_list()

        self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Carregando associados…")

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
            ttk.Label(
                self.admin_list,
                text="Nenhum associado encontrado." if self._pessoas else "Nenhum associado cadastrado. Clique em Novo associado.",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=20)
            return

        for pessoa in pessoas:
            self._pessoa_row(self.admin_list, pessoa, editable=True)

    def _toggle_expand(self, person_id: str) -> None:
        if person_id in self._expanded_ids:
            self._expanded_ids.discard(person_id)
        else:
            self._expanded_ids.add(person_id)
        # re-render mantendo posição relativa
        y = 0.0
        if self._scroll is not None:
            try:
                y = self._scroll.canvas.yview()[0]
            except tk.TclError:
                y = 0.0
        if hasattr(self, "_lista_mode") and self._lista_mode:
            self._render_lista_rows()
        elif hasattr(self, "admin_list"):
            self._render_admin_list()
        if self._scroll is not None:
            self.after(10, lambda: self._scroll.canvas.yview_moveto(y))

    def _pessoa_row(self, parent, pessoa: PessoaComReap, *, editable: bool, mask_cpf: bool = False) -> None:
        expanded = pessoa.id in self._expanded_ids
        card = tk.Frame(parent, bg=COLORS["surface"], padx=12, pady=8, highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=4, padx=2)

        head = tk.Frame(card, bg=COLORS["surface"])
        head.pack(fill="x")

        avatar = tk.Label(head, text=get_initials(pessoa.nome), bg=COLORS["primary"], fg=COLORS["primary_fg"], width=3, font=(FONT_FAMILY, 11, "bold"), padx=6, pady=6)
        avatar.pack(side="left", padx=(0, 10))

        info = tk.Frame(head, bg=COLORS["surface"], cursor="hand2")
        info.pack(side="left", fill="x", expand=True)

        pagos_ano = 0
        ano_atual = __import__("datetime").datetime.now().year
        for a in pessoa.anos:
            if a.ano == ano_atual:
                pagos_ano = sum(1 for v in a.meses.values() if v)
        chevron = "▼" if expanded else "▶"
        name_lbl = tk.Label(
            info,
            text=f"{chevron}  {pessoa.nome}",
            bg=COLORS["surface"],
            fg=COLORS["primary"],
            font=(FONT_FAMILY, 11, "bold"),
            anchor="w",
            cursor="hand2",
        )
        name_lbl.pack(anchor="w")
        cpf_txt = format_cpf_masked(pessoa.cpf) if mask_cpf else format_cpf(pessoa.cpf)
        sub = tk.Label(
            info,
            text=f"CPF: {cpf_txt}  ·  {ano_atual}: {pagos_ano}/12 REAPs",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
            anchor="w",
            cursor="hand2",
        )
        sub.pack(anchor="w")

        def toggle(_e=None, pid=pessoa.id):
            self._toggle_expand(pid)

        for w in (info, name_lbl, sub, avatar):
            w.bind("<Button-1>", toggle)

        if editable:
            actions = tk.Frame(head, bg=COLORS["surface"])
            actions.pack(side="right")
            tk.Button(actions, text="QR", command=lambda p=pessoa: self._show_qr_pessoa(p), relief="flat", bg=COLORS["month_off"], cursor="hand2").pack(side="left", padx=2)
            tk.Button(actions, text="Editar", command=lambda p=pessoa: self._dialog_pessoa(p), relief="flat", bg=COLORS["month_off"], cursor="hand2").pack(side="left", padx=2)
            tk.Button(actions, text="Excluir", command=lambda p=pessoa: self._delete_pessoa(p), relief="flat", bg=COLORS["danger_bg"], fg=COLORS["danger"], cursor="hand2").pack(side="left", padx=2)

        if not expanded:
            return

        # Menu rápido expandido: anos + REAPs
        detail = tk.Frame(card, bg=COLORS["surface"])
        detail.pack(fill="x", pady=(10, 0))

        if not pessoa.anos:
            tk.Label(detail, text="Nenhum ano registrado.", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        for ano in pessoa.anos:
            pagos = sum(1 for v in ano.meses.values() if v)
            ano_frame = tk.Frame(detail, bg=COLORS["surface"])
            ano_frame.pack(fill="x", pady=(8, 0))
            tk.Label(
                ano_frame,
                text=f"Ano {ano.ano}  ·  {pagos}/12 pagos",
                bg=COLORS["surface"],
                fg=COLORS["primary"],
                font=(FONT_FAMILY, 10, "bold"),
            ).pack(anchor="w")
            self._month_grid(ano_frame, pessoa.id, ano.ano, ano.meses, editable=editable)

        if editable:
            add_row = tk.Frame(detail, bg=COLORS["surface"])
            add_row.pack(fill="x", pady=(10, 0))
            year_var = tk.StringVar(value=str(__import__("datetime").datetime.now().year + 1))
            ttk.Entry(add_row, textvariable=year_var, width=8).pack(side="left")
            tk.Button(
                add_row,
                text="Adicionar ano",
                command=lambda p=pessoa, y=year_var: self._add_ano(p, y.get()),
                relief="flat",
                bg=COLORS["month_off"],
                cursor="hand2",
            ).pack(side="left", padx=8)

    def _month_grid(self, parent, person_id: str, ano: int, meses: dict, *, editable: bool) -> None:
        grid = tk.Frame(parent, bg=COLORS["surface"])
        grid.pack(fill="x", pady=4)
        for i, mes in enumerate(MESES):
            pago = bool(meses.get(mes))
            bg = COLORS["month_on"] if pago else COLORS["month_off"]
            fg = COLORS["success"] if pago else COLORS["muted"]
            mark = "✓" if pago else "✗"
            if editable:
                btn = tk.Button(
                    grid,
                    text=f"{mes.upper()}\n{mark}",
                    width=5,
                    height=2,
                    bg=bg,
                    fg=fg,
                    relief="flat",
                    font=(FONT_FAMILY, 8, "bold"),
                    cursor="hand2",
                    command=lambda m=mes, p=pago: self._toggle_mes(person_id, ano, m, not p),
                )
            else:
                btn = tk.Label(
                    grid,
                    text=f"{mes.upper()}\n{mark}",
                    width=5,
                    height=2,
                    bg=bg,
                    fg=fg,
                    font=(FONT_FAMILY, 8, "bold"),
                )
            btn.grid(row=i // 6, column=i % 6, padx=3, pady=3, sticky="nsew")
            btn.bind("<Enter>", lambda _e, t=MESES_LABEL[mes]: self.status.set(t))

    def _toggle_mes(self, person_id: str, ano: int, mes: MesKey, novo: bool) -> None:
        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return

        # Otimista: mantém expandido e recarrega
        self._expanded_ids.add(person_id)

        def work():
            svc.toggle_mes(person_id, ano, mes, novo)
            return True

        self._run_bg(work, lambda _: self._load_admin_data(), lambda e: messagebox.showerror("Erro", str(e)), f"Atualizando {mes}/{ano}…")

    def _dialog_pessoa(self, pessoa: Optional[PessoaComReap] = None) -> None:
        win = tk.Toplevel(self)
        win.title("Editar associado" if pessoa else "Novo associado")
        win.configure(bg=COLORS["surface"])
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Nome completo", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=16, pady=(16, 2))
        nome = ttk.Entry(win, width=42)
        nome.pack(padx=16)
        if pessoa:
            nome.insert(0, pessoa.nome)

        tk.Label(win, text="CPF (11 dígitos)", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w", padx=16, pady=(10, 2))
        cpf = ttk.Entry(win, width=42)
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
                created = svc.add_pessoa(n, c)
                return created.id

            def ok(pid: str) -> None:
                win.destroy()
                self._expanded_ids.add(pid)  # abre menu rápido da pessoa nova
                self._load_admin_data()

            self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e), parent=win), "Salvando associado…")

        tk.Button(win, text="Salvar", command=save, bg=COLORS["accent"], fg=COLORS["accent_fg"], relief="flat", padx=14, pady=7, font=(FONT_FAMILY, 10, "bold"), cursor="hand2").pack(pady=16)

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

        self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Removendo associado…")

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

        self._run_bg(work, lambda _: self._load_admin_data(), lambda e: messagebox.showerror("Erro", str(e)), f"Adicionando ano {ano}…")

    # ------------------------------------------------------------------
    # Lista pública + QR
    # ------------------------------------------------------------------
    def show_lista(self) -> None:
        self._clear_body()
        self._lista_mode = True
        self._nav_button("Início", self.show_home)
        if self._logged_in:
            self._nav_button("Admin", self.show_admin)
        self._nav_button("Gerar / imprimir QR", self._show_qr_lista)
        self._nav_button("Configurações", self.show_settings)

        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True, padx=20, pady=12)

        top = ttk.Frame(wrap)
        top.pack(fill="x")
        ttk.Label(top, text="Situação do REAP", style="Title.TLabel").pack(side="left")
        tk.Button(
            top,
            text="QR da lista (imprimir)",
            command=self._show_qr_lista,
            bg=COLORS["accent"],
            fg=COLORS["accent_fg"],
            relief="flat",
            padx=12,
            pady=6,
            font=(FONT_FAMILY, 10, "bold"),
            cursor="hand2",
        ).pack(side="right")

        ttk.Label(
            wrap,
            text="Clique no nome para ver os meses. Use o QR para o celular abrir a lista online atualizada.",
            style="Muted.TLabel",
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
            ttk.Label(self.lista_frame, text=str(exc), style="Muted.TLabel").pack(anchor="w")
            return

        def work():
            return svc.get_all_pessoas_com_reap()

        def ok(pessoas: List[PessoaComReap]) -> None:
            self._pessoas = pessoas
            self._render_lista_rows()

        self._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Carregando lista pública…")

    def _render_lista_rows(self) -> None:
        if not hasattr(self, "lista_frame") or not self.lista_frame.winfo_exists():
            return
        for child in self.lista_frame.winfo_children():
            child.destroy()
        if not self._pessoas:
            ttk.Label(self.lista_frame, text="Nenhum associado cadastrado.", style="Muted.TLabel").pack(anchor="w")
            return
        for p in self._pessoas:
            self._pessoa_row(self.lista_frame, p, editable=False, mask_cpf=True)

    def _show_qr_lista(self) -> None:
        try:
            url = self._ensure_public_server().rstrip("/") + "/lista"
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("QR", f"Não foi possível iniciar a lista online.\n{exc}")
            return
        self._qr_dialog(url, title="QR — Lista pública REAP", subtitle="Qualquer pessoa aponta a câmera e vê os REAPs atualizados.")

    def _show_qr_pessoa(self, pessoa: PessoaComReap) -> None:
        try:
            url = self._ensure_public_server().rstrip("/") + f"/pessoa/{pessoa.id}"
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("QR", str(exc))
            return
        self._qr_dialog(url, title=f"QR — {pessoa.nome}", subtitle="Comprovante individual (REAP online).")

    def _qr_dialog(self, url: str, *, title: str, subtitle: str) -> None:
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=COLORS["surface"])
        win.transient(self)
        win.grab_set()

        tk.Label(win, text=title, bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_FAMILY, 13, "bold")).pack(padx=16, pady=(16, 4))
        tk.Label(win, text=subtitle, bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9), wraplength=360).pack(padx=16)

        try:
            poster = make_qr_image(url, title=title)
            photo = pil_to_tk(poster, max_size=(320, 360))
            self._qr_photo = photo
            tk.Label(win, image=photo, bg=COLORS["surface"]).pack(pady=12)
        except Exception as exc:  # noqa: BLE001
            tk.Label(win, text=f"Falha ao gerar QR: {exc}", bg=COLORS["surface"], fg=COLORS["danger"]).pack()

        tk.Label(win, text=url, bg=COLORS["surface"], fg=COLORS["accent"], font=(FONT_FAMILY, 8), wraplength=380).pack(padx=16)

        def save() -> None:
            path = filedialog.asksaveasfilename(
                parent=win,
                title="Salvar QR para impressão",
                defaultextension=".png",
                filetypes=[("PNG", "*.png")],
                initialfile="sinapesc-lista-reap-qr.png",
            )
            if not path:
                return
            save_qr_png(url, path, title=title)
            messagebox.showinfo("QR", f"Salvo em:\n{path}\n\nImprima e cole onde quiser.", parent=win)

        def copy_url() -> None:
            win.clipboard_clear()
            win.clipboard_append(url)
            self.status.set("URL copiada.")

        btns = tk.Frame(win, bg=COLORS["surface"])
        btns.pack(pady=14)
        tk.Button(btns, text="Salvar PNG / imprimir", command=save, bg=COLORS["accent"], fg=COLORS["accent_fg"], relief="flat", padx=12, pady=7, font=(FONT_FAMILY, 10, "bold"), cursor="hand2").pack(side="left", padx=6)
        tk.Button(btns, text="Copiar link", command=copy_url, bg=COLORS["primary"], fg=COLORS["primary_fg"], relief="flat", padx=12, pady=7, cursor="hand2").pack(side="left", padx=6)
        tk.Button(btns, text="Fechar", command=win.destroy, relief="flat", padx=12, pady=7, cursor="hand2").pack(side="left", padx=6)


def _asset(name: str) -> str:
    from pathlib import Path
    import sys

    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return str(base / "assets" / name)
