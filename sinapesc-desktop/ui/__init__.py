"""
Interface gráfica desktop do Sinapesc — Controle de REAP.

Telas:
  - Login do administrador
  - Configuração da API Google Sheets (didática)
  - Painel admin (CRUD associados + marcar meses)
  - Lista pública (consulta com CPF mascarado)
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional

from config import (
    import_credentials_file,
    is_sheets_configured,
    load_config,
    save_config,
)
from sheets import MESES, MESES_LABEL, MesKey, PessoaComReap, SheetsConfigError, SheetsService
from ui.formatters import format_cpf, format_cpf_masked, get_initials, only_digits
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

        self._setup_style()
        self._build_shell()
        self.show_home()

        try:
            self.iconphoto(True, tk.PhotoImage(file=_asset("icon.png")))
        except Exception:
            pass

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
        style.configure("Card.TFrame", background=COLORS["surface"])
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
        style.configure(
            "Card.TLabel",
            background=COLORS["surface"],
            foreground=COLORS["primary"],
            font=(FONT_FAMILY, 11, "bold"),
        )
        style.configure(
            "CardMuted.TLabel",
            background=COLORS["surface"],
            foreground=COLORS["muted"],
            font=(FONT_FAMILY, 9),
        )
        style.configure(
            "Primary.TButton",
            font=(FONT_FAMILY, 10, "bold"),
            padding=(14, 8),
        )
        style.configure("TButton", font=(FONT_FAMILY, 10), padding=(10, 6))
        style.configure("TEntry", padding=6)
        style.configure(
            "Success.TLabel",
            background=COLORS["success_bg"],
            foreground=COLORS["success"],
            font=(FONT_FAMILY, 9, "bold"),
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
        status_bar = tk.Label(
            self,
            textvariable=self.status,
            anchor="w",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
            padx=12,
            pady=6,
        )
        status_bar.pack(fill="x", side="bottom")

    def _clear_body(self) -> None:
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
            except Exception as exc:  # noqa: BLE001 — UI precisa mostrar qualquer falha
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

    # ------------------------------------------------------------------
    # Navegação
    # ------------------------------------------------------------------
    def _nav_button(self, text: str, command: Callable) -> None:
        btn = tk.Button(
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
        )
        btn.pack(side="left", padx=4)

    def show_home(self) -> None:
        self._clear_body()
        self._nav_button("Configurações", self.show_settings)

        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True, padx=40, pady=36)

        ttk.Label(wrap, text="Acompanhamento mensal da contribuição REAP", style="Title.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            wrap,
            text="Programa para notebook: cadastre associados, marque meses pagos e consulte a lista.",
            style="Muted.TLabel",
            wraplength=700,
        ).pack(anchor="w", pady=(8, 28))

        cards = ttk.Frame(wrap)
        cards.pack(fill="x")

        self._home_card(
            cards,
            "Área administrativa",
            "Cadastre associados, informe nome/CPF e marque os meses pagos do REAP.",
            "Entrar como administrador",
            self.show_login,
        ).pack(side="left", fill="both", expand=True, padx=(0, 12))

        self._home_card(
            cards,
            "Lista pública",
            "Consulte a situação do REAP de todos os associados (CPF parcialmente oculto).",
            "Ver lista pública",
            self.show_lista,
        ).pack(side="left", fill="both", expand=True, padx=(12, 0))

        tip = ttk.Label(
            wrap,
            text=(
                "Dica: na primeira vez, abra Configurações e importe o JSON da Conta de Serviço "
                "do Google + o ID da planilha. Veja o guia didático na própria tela de configuração."
            ),
            style="Muted.TLabel",
            wraplength=760,
        )
        tip.pack(anchor="w", pady=(28, 0))

    def _home_card(
        self,
        parent: ttk.Frame,
        title: str,
        desc: str,
        btn_text: str,
        command: Callable,
    ) -> ttk.Frame:
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=COLORS["surface"], padx=18, pady=18)
        inner.pack(fill="both", expand=True)

        tk.Label(
            inner,
            text=title,
            bg=COLORS["surface"],
            fg=COLORS["primary"],
            font=(FONT_FAMILY, 13, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            inner,
            text=desc,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 10),
            wraplength=320,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(8, 16))

        tk.Button(
            inner,
            text=btn_text,
            command=command,
            bg=COLORS["primary"],
            fg=COLORS["primary_fg"],
            activebackground="#142844",
            relief="flat",
            padx=12,
            pady=8,
            font=(FONT_FAMILY, 10, "bold"),
            cursor="hand2",
        ).pack(anchor="w")

        # Substitui o ttk card pelo frame com borda
        return outer

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    def show_login(self) -> None:
        self._clear_body()
        self._nav_button("Início", self.show_home)
        self._nav_button("Configurações", self.show_settings)

        wrap = ttk.Frame(self.body)
        wrap.pack(expand=True)

        box = tk.Frame(wrap, bg=COLORS["surface"], padx=28, pady=24, highlightbackground=COLORS["border"], highlightthickness=1)
        box.pack()

        tk.Label(
            box,
            text="Login do administrador",
            bg=COLORS["surface"],
            fg=COLORS["primary"],
            font=(FONT_FAMILY, 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            box,
            text="Use o e-mail e senha definidos em Configurações.",
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=(FONT_FAMILY, 9),
        ).pack(anchor="w", pady=(4, 16))

        tk.Label(box, text="E-mail", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        email = ttk.Entry(box, width=40)
        email.pack(anchor="w", pady=(2, 10))
        email.insert(0, self.cfg.get("admin_email", ""))

        tk.Label(box, text="Senha", bg=COLORS["surface"], fg=COLORS["muted"]).pack(anchor="w")
        password = ttk.Entry(box, width=40, show="•")
        password.pack(anchor="w", pady=(2, 16))

        def do_login() -> None:
            cfg = load_config()
            if email.get().strip().lower() != str(cfg.get("admin_email", "")).lower():
                messagebox.showerror("Login", "E-mail ou senha incorretos.")
                return
            if password.get() != str(cfg.get("admin_password", "")):
                messagebox.showerror("Login", "E-mail ou senha incorretos.")
                return
            if not is_sheets_configured(cfg):
                messagebox.showwarning(
                    "Configuração",
                    "Configure primeiro a integração com o Google Sheets.",
                )
                self.show_settings()
                return
            self._logged_in = True
            self.show_admin()

        tk.Button(
            box,
            text="Entrar",
            command=do_login,
            bg=COLORS["accent"],
            fg=COLORS["accent_fg"],
            relief="flat",
            padx=16,
            pady=8,
            font=(FONT_FAMILY, 10, "bold"),
            cursor="hand2",
        ).pack(anchor="e")
        password.bind("<Return>", lambda _e: do_login())

    # ------------------------------------------------------------------
    # Configurações (didático)
    # ------------------------------------------------------------------
    def show_settings(self) -> None:
        self._clear_body()
        self._nav_button("Início", self.show_home)

        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True, padx=24, pady=16)

        ttk.Label(wrap, text="Configuração do Google Sheets", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text="Siga os passos abaixo. O programa usa uma Conta de Serviço (sem login Google a cada uso).",
            style="Muted.TLabel",
            wraplength=820,
        ).pack(anchor="w", pady=(4, 12))

        # Painel de passos didáticos
        guide = tk.Text(
            wrap,
            height=10,
            wrap="word",
            bg="#F4FAF8",
            fg=COLORS["primary"],
            font=(FONT_FAMILY, 9),
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=10,
        )
        guide.pack(fill="x", pady=(0, 14))
        guide.insert(
            "1.0",
            "PASSO A PASSO DA API GOOGLE PLANILHAS\n"
            "1) Acesse console.cloud.google.com → crie/selecione um projeto.\n"
            "2) Ative a API: APIs e serviços → Biblioteca → 'Google Sheets API' → Ativar.\n"
            "3) IAM → Contas de serviço → Criar → gere uma chave JSON e baixe o arquivo.\n"
            "4) Abra sua planilha no Google Drive e compartilhe com o e-mail da conta de serviço (Editor).\n"
            "5) O ID da planilha está na URL: docs.google.com/spreadsheets/d/ID_AQUI/edit\n"
            "6) Neste programa: importe o JSON, cole o ID e salve. O app cria as abas Pessoas e Reap sozinho.\n"
            "\n"
            "Estrutura das abas:\n"
            "  Pessoas = id | nome | cpf | criadoEm\n"
            "  Reap    = id | personId | ano | jan…dez | atualizadoEm",
        )
        guide.configure(state="disabled")

        form = tk.Frame(wrap, bg=COLORS["surface"], padx=16, pady=16, highlightbackground=COLORS["border"], highlightthickness=1)
        form.pack(fill="x")

        cfg = load_config()

        tk.Label(form, text="ID da planilha (GOOGLE_SHEET_ID)", bg=COLORS["surface"], fg=COLORS["muted"]).grid(
            row=0, column=0, sticky="w"
        )
        sheet_id = ttk.Entry(form, width=70)
        sheet_id.grid(row=1, column=0, columnspan=2, sticky="we", pady=(2, 10))
        sheet_id.insert(0, cfg.get("spreadsheet_id", ""))

        cred_label = tk.StringVar(
            value=(
                f"JSON carregado: {cfg['credentials_json'].get('client_email')}"
                if isinstance(cfg.get("credentials_json"), dict)
                else (
                    f"E-mail + chave: {cfg.get('service_account_email')}"
                    if cfg.get("service_account_email")
                    else "Nenhuma credencial carregada ainda."
                )
            )
        )
        tk.Label(form, textvariable=cred_label, bg=COLORS["surface"], fg=COLORS["accent"], font=(FONT_FAMILY, 9, "bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )

        credentials_holder: dict = {"json": cfg.get("credentials_json")}

        def pick_json() -> None:
            path = filedialog.askopenfilename(
                title="Selecione o JSON da Conta de Serviço",
                filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            )
            if not path:
                return
            try:
                data = import_credentials_file(path)
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Credenciais", str(exc))
                return
            credentials_holder["json"] = data
            cred_label.set(f"JSON carregado: {data.get('client_email')}")

        tk.Button(
            form,
            text="Importar JSON da Conta de Serviço…",
            command=pick_json,
            bg=COLORS["primary"],
            fg=COLORS["primary_fg"],
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
        ).grid(row=3, column=0, sticky="w", pady=(0, 14))

        tk.Label(form, text="E-mail do administrador (login local)", bg=COLORS["surface"], fg=COLORS["muted"]).grid(
            row=4, column=0, sticky="w"
        )
        admin_email = ttk.Entry(form, width=40)
        admin_email.grid(row=5, column=0, sticky="w", pady=(2, 10))
        admin_email.insert(0, cfg.get("admin_email", "admin@sinapesc.local"))

        tk.Label(form, text="Senha do administrador", bg=COLORS["surface"], fg=COLORS["muted"]).grid(
            row=6, column=0, sticky="w"
        )
        admin_password = ttk.Entry(form, width=40, show="•")
        admin_password.grid(row=7, column=0, sticky="w", pady=(2, 14))
        admin_password.insert(0, cfg.get("admin_password", "sinapesc"))

        def save() -> None:
            new_cfg = load_config()
            new_cfg["spreadsheet_id"] = sheet_id.get().strip()
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

            def ok(n: int) -> None:
                messagebox.showinfo(
                    "Teste",
                    f"Conexão OK!\nAbas verificadas.\nAssociados encontrados: {n}",
                )

            def err(exc: Exception) -> None:
                messagebox.showerror(
                    "Teste",
                    "Falha ao falar com a planilha.\n\n"
                    f"{exc}\n\n"
                    "Confira: API ativada, JSON correto e planilha compartilhada com o e-mail da conta de serviço.",
                )

            self._run_bg(work, ok, err, "Testando conexão com o Google Sheets…")

        actions = tk.Frame(form, bg=COLORS["surface"])
        actions.grid(row=8, column=0, sticky="w")
        tk.Button(
            actions,
            text="Salvar",
            command=save,
            bg=COLORS["accent"],
            fg=COLORS["accent_fg"],
            relief="flat",
            padx=14,
            pady=7,
            font=(FONT_FAMILY, 10, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            actions,
            text="Testar conexão",
            command=test_connection,
            bg=COLORS["primary"],
            fg=COLORS["primary_fg"],
            relief="flat",
            padx=14,
            pady=7,
            cursor="hand2",
        ).pack(side="left")

        form.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------------
    def show_admin(self) -> None:
        if not self._logged_in:
            self.show_login()
            return

        self._clear_body()
        self._nav_button("Início", self.show_home)
        self._nav_button("Lista pública", self.show_lista)
        self._nav_button("Configurações", self.show_settings)
        self._nav_button("Sair", self._logout)

        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True, padx=20, pady=12)

        top = ttk.Frame(wrap)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Associados", style="Title.TLabel").pack(side="left")
        self.admin_count = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.admin_count, style="Muted.TLabel").pack(side="left", padx=12)

        tk.Button(
            top,
            text="+ Novo associado",
            command=self._dialog_pessoa,
            bg=COLORS["accent"],
            fg=COLORS["accent_fg"],
            relief="flat",
            padx=12,
            pady=6,
            font=(FONT_FAMILY, 10, "bold"),
            cursor="hand2",
        ).pack(side="right")
        tk.Button(
            top,
            text="Atualizar",
            command=self._load_admin_data,
            bg=COLORS["primary"],
            fg=COLORS["primary_fg"],
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side="right", padx=8)

        search_row = ttk.Frame(wrap)
        search_row.pack(fill="x", pady=(0, 8))
        ttk.Label(search_row, text="Buscar:", style="Muted.TLabel").pack(side="left")
        self.search_var = tk.StringVar()
        search = ttk.Entry(search_row, textvariable=self.search_var, width=40)
        search.pack(side="left", padx=8)
        self.search_var.trace_add("write", lambda *_: self._render_admin_list())

        # Lista com scroll
        canvas_frame = ttk.Frame(wrap)
        canvas_frame.pack(fill="both", expand=True)
        self.admin_canvas = tk.Canvas(canvas_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.admin_canvas.yview)
        self.admin_list = ttk.Frame(self.admin_canvas)
        self.admin_list.bind(
            "<Configure>",
            lambda e: self.admin_canvas.configure(scrollregion=self.admin_canvas.bbox("all")),
        )
        self.admin_canvas.create_window((0, 0), window=self.admin_list, anchor="nw")
        self.admin_canvas.configure(yscrollcommand=scrollbar.set)
        self.admin_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event: tk.Event) -> None:
            self.admin_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.admin_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.admin_canvas.bind_all("<Button-4>", lambda _e: self.admin_canvas.yview_scroll(-1, "units"))
        self.admin_canvas.bind_all("<Button-5>", lambda _e: self.admin_canvas.yview_scroll(1, "units"))

        self._load_admin_data()

    def _logout(self) -> None:
        self._logged_in = False
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
            self.admin_count.set(f"{len(pessoas)} associado(s)")
            self._render_admin_list()

        def err(exc: Exception) -> None:
            messagebox.showerror("Erro", str(exc))

        self._run_bg(work, ok, err, "Carregando associados da planilha…")

    def _filtered_pessoas(self) -> List[PessoaComReap]:
        q = self.search_var.get().strip().lower()
        digits = only_digits(q)
        if not q:
            return self._pessoas
        out = []
        for p in self._pessoas:
            if q in p.nome.lower() or (digits and digits in p.cpf):
                out.append(p)
        return out

    def _render_admin_list(self) -> None:
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
            self._pessoa_card(self.admin_list, pessoa, editable=True)

    def _pessoa_card(self, parent: ttk.Frame, pessoa: PessoaComReap, *, editable: bool, mask_cpf: bool = False) -> None:
        card = tk.Frame(parent, bg=COLORS["surface"], padx=14, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="x", pady=6, padx=2)

        head = tk.Frame(card, bg=COLORS["surface"])
        head.pack(fill="x")

        avatar = tk.Label(
            head,
            text=get_initials(pessoa.nome),
            bg=COLORS["primary"],
            fg=COLORS["primary_fg"],
            width=3,
            font=(FONT_FAMILY, 11, "bold"),
            padx=6,
            pady=6,
        )
        avatar.pack(side="left", padx=(0, 10))

        info = tk.Frame(head, bg=COLORS["surface"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=pessoa.nome, bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT_FAMILY, 11, "bold")).pack(anchor="w")
        cpf_txt = format_cpf_masked(pessoa.cpf) if mask_cpf else format_cpf(pessoa.cpf)
        tk.Label(info, text=f"CPF: {cpf_txt}", bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9)).pack(anchor="w")

        if editable:
            actions = tk.Frame(head, bg=COLORS["surface"])
            actions.pack(side="right")
            tk.Button(
                actions,
                text="Editar",
                command=lambda p=pessoa: self._dialog_pessoa(p),
                relief="flat",
                bg=COLORS["month_off"],
                cursor="hand2",
            ).pack(side="left", padx=2)
            tk.Button(
                actions,
                text="Excluir",
                command=lambda p=pessoa: self._delete_pessoa(p),
                relief="flat",
                bg=COLORS["danger_bg"],
                fg=COLORS["danger"],
                cursor="hand2",
            ).pack(side="left", padx=2)

        # Anos / meses
        for ano in pessoa.anos:
            ano_frame = tk.Frame(card, bg=COLORS["surface"])
            ano_frame.pack(fill="x", pady=(10, 0))
            tk.Label(
                ano_frame,
                text=str(ano.ano),
                bg=COLORS["surface"],
                fg=COLORS["primary"],
                font=(FONT_FAMILY, 10, "bold"),
            ).pack(anchor="w")
            self._month_grid(ano_frame, pessoa.id, ano.ano, ano.meses, editable=editable)

        if editable:
            add_row = tk.Frame(card, bg=COLORS["surface"])
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

    def _month_grid(
        self,
        parent: tk.Frame,
        person_id: str,
        ano: int,
        meses: dict,
        *,
        editable: bool,
    ) -> None:
        grid = tk.Frame(parent, bg=COLORS["surface"])
        grid.pack(fill="x", pady=4)

        for i, mes in enumerate(MESES):
            pago = bool(meses.get(mes))
            bg = COLORS["month_on"] if pago else COLORS["month_off"]
            fg = COLORS["success"] if pago else COLORS["muted"]
            mark = "✓" if pago else "✗"
            btn = tk.Button(
                grid,
                text=f"{mes.upper()}\n{mark}",
                width=5,
                height=2,
                bg=bg,
                fg=fg,
                relief="flat",
                font=(FONT_FAMILY, 8, "bold"),
                cursor="hand2" if editable else "arrow",
                state="normal" if editable else "disabled",
                disabledforeground=fg,
                command=(
                    (lambda m=mes, p=pago: self._toggle_mes(person_id, ano, m, not p))
                    if editable
                    else None
                ),
            )
            btn.grid(row=i // 6, column=i % 6, padx=3, pady=3, sticky="nsew")
            btn_tip = MESES_LABEL[mes]
            # tooltip simples via title no Windows não existe; usamos bind status
            btn.bind("<Enter>", lambda _e, t=btn_tip: self.status.set(t))

    def _toggle_mes(self, person_id: str, ano: int, mes: MesKey, novo: bool) -> None:
        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return

        def work():
            svc.toggle_mes(person_id, ano, mes, novo)
            return True

        def ok(_: bool) -> None:
            self._load_admin_data()

        def err(exc: Exception) -> None:
            messagebox.showerror("Erro", str(exc))

        self._run_bg(work, ok, err, f"Atualizando {mes}/{ano}…")

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
                else:
                    svc.add_pessoa(n, c)
                return True

            def ok(_: bool) -> None:
                win.destroy()
                self._load_admin_data()

            def err(exc: Exception) -> None:
                messagebox.showerror("Erro", str(exc), parent=win)

            self._run_bg(work, ok, err, "Salvando associado…")

        tk.Button(
            win,
            text="Salvar",
            command=save,
            bg=COLORS["accent"],
            fg=COLORS["accent_fg"],
            relief="flat",
            padx=14,
            pady=7,
            font=(FONT_FAMILY, 10, "bold"),
            cursor="hand2",
        ).pack(pady=16)

    def _delete_pessoa(self, pessoa: PessoaComReap) -> None:
        if not messagebox.askyesno(
            "Remover",
            f"Remover {pessoa.nome} e todo o histórico de REAP?\nEsta ação não pode ser desfeita.",
        ):
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
            self._load_admin_data()

        def err(exc: Exception) -> None:
            messagebox.showerror("Erro", str(exc))

        self._run_bg(work, ok, err, "Removendo associado…")

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

        def work():
            svc.add_ano(pessoa.id, ano)
            return True

        def ok(_: bool) -> None:
            self._load_admin_data()

        def err(exc: Exception) -> None:
            messagebox.showerror("Erro", str(exc))

        self._run_bg(work, ok, err, f"Adicionando ano {ano}…")

    # ------------------------------------------------------------------
    # Lista pública
    # ------------------------------------------------------------------
    def show_lista(self) -> None:
        self._clear_body()
        self._nav_button("Início", self.show_home)
        if self._logged_in:
            self._nav_button("Admin", self.show_admin)
        self._nav_button("Configurações", self.show_settings)

        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True, padx=20, pady=12)

        ttk.Label(wrap, text="Situação do REAP", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            wrap,
            text="Consulta pública. Os documentos (CPF) aparecem parcialmente ocultos.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 10))

        canvas_frame = ttk.Frame(wrap)
        canvas_frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(canvas_frame, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        lista = ttk.Frame(canvas)
        lista.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=lista, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            svc = self._ensure_service()
        except Exception as exc:  # noqa: BLE001
            ttk.Label(lista, text=str(exc), style="Muted.TLabel").pack(anchor="w")
            return

        def work():
            return svc.get_all_pessoas_com_reap()

        def ok(pessoas: List[PessoaComReap]) -> None:
            if not pessoas:
                ttk.Label(lista, text="Nenhum associado cadastrado.", style="Muted.TLabel").pack(anchor="w")
                return
            for p in pessoas:
                self._pessoa_card(lista, p, editable=False, mask_cpf=True)

        def err(exc: Exception) -> None:
            messagebox.showerror("Erro", str(exc))

        self._run_bg(work, ok, err, "Carregando lista pública…")


def _asset(name: str) -> str:
    from pathlib import Path
    import sys

    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return str(base / "assets" / name)
