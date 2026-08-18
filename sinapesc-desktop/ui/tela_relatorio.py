"""Tela Admin → Relatório anual de conformidade (HTML)."""

from __future__ import annotations

import webbrowser
from datetime import datetime
from tkinter import messagebox, ttk
import tkinter as tk
from typing import TYPE_CHECKING, Optional

from controle.calendario import meses_para_texto
from controle.pendencias import classificar
from controle.relatorio import (
    itens_para_relatorio,
    montar_html,
    nome_arquivo_relatorio,
    salvar_html,
)
from ui.formatters import only_digits
from ui.theme import COLORS, FONT_DISPLAY, FONT_FAMILY, ORG_FULL, ORG_SHORT

if TYPE_CHECKING:
    from ui import SinapescApp


def show_relatorio(app: "SinapescApp") -> None:
    from ui.chrome import page_wrap

    wrap = page_wrap(app)

    tk.Label(
        wrap, text="Relatório de conformidade REAP", bg=COLORS["content"], fg=COLORS["primary"],
        font=(FONT_DISPLAY, 20, "bold"),
    ).pack(anchor="w")
    tk.Label(
        wrap,
        text="Somente administrador. Mostra o CPF completo. Abra no navegador e use Imprimir → Salvar como PDF. Sem valor em R$. A consulta pública no celular continua com CPF mascarado.",
        bg=COLORS["content"],
        fg=COLORS["muted"],
        font=(FONT_FAMILY, 9),
        wraplength=880,
        justify="left",
    ).pack(anchor="w", pady=(4, 16))

    box = tk.Frame(wrap, bg=COLORS["surface"], padx=18, pady=16, highlightbackground=COLORS["border"], highlightthickness=1)
    box.pack(fill="x")

    row = tk.Frame(box, bg=COLORS["surface"])
    row.pack(fill="x")
    tk.Label(row, text="Ano", bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")
    ano_ent = ttk.Entry(row, width=8)
    ano_ent.insert(0, str(datetime.now().year))
    ano_ent.pack(side="left", padx=8)

    modo = tk.StringVar(value="diretoria")
    tk.Radiobutton(
        row, text="Diretoria (todos os sócios)", variable=modo, value="diretoria",
        bg=COLORS["surface"], fg=COLORS["primary"], selectcolor=COLORS["surface_soft"],
    ).pack(side="left", padx=12)
    tk.Radiobutton(
        row, text="Comprovante de um sócio", variable=modo, value="individual",
        bg=COLORS["surface"], fg=COLORS["primary"], selectcolor=COLORS["surface_soft"],
    ).pack(side="left")

    tk.Label(box, text="Buscar sócio (só no comprovante individual)", bg=COLORS["surface"], fg=COLORS["muted"]).pack(
        anchor="w", pady=(12, 2)
    )
    busca = ttk.Entry(box, width=48)
    busca.pack(anchor="w")

    cal_lbl = tk.StringVar(value="")
    tk.Label(box, textvariable=cal_lbl, bg=COLORS["surface"], fg=COLORS["accent"], font=(FONT_FAMILY, 9, "bold")).pack(
        anchor="w", pady=(10, 0)
    )

    def ano_ok() -> Optional[int]:
        txt = ano_ent.get().strip()
        if not txt.isdigit():
            messagebox.showerror("Relatório", "Ano inválido.")
            return None
        ano = int(txt)
        if ano < 2000 or ano > 2100:
            messagebox.showerror("Relatório", "Ano entre 2000 e 2100.")
            return None
        return ano

    def gerar() -> None:
        ano = ano_ok()
        if ano is None:
            return
        try:
            svc = app._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return

        q = busca.get().strip().lower()
        digits = only_digits(q)
        individual = modo.get() == "individual"

        def work():
            pessoas = svc.get_all_pessoas_com_reap()
            cal = svc.get_calendario(ano)
            pend, reg = classificar(pessoas, ano, cal)
            todos = itens_para_relatorio(pend, reg)
            escolhidos = todos
            titulo = f"Relatório de conformidade REAP {ano}"
            nome_arq = nome_arquivo_relatorio(ano)
            if individual:
                if not q:
                    raise ValueError("Digite o nome ou CPF do sócio para o comprovante individual.")
                match = [
                    s for s in todos
                    if q in s.pessoa.nome.lower() or (digits and digits in s.pessoa.cpf)
                ]
                if not match:
                    raise ValueError("Nenhum sócio encontrado com essa busca.")
                if len(match) > 1:
                    nomes = ", ".join(s.pessoa.nome for s in match[:8])
                    raise ValueError(f"Vários sócios ({len(match)}). Refine a busca.\n{nomes}")
                escolhidos = match
                titulo = f"Comprovante de situação REAP {ano}"
                nome_arq = nome_arquivo_relatorio(ano, individual_nome=match[0].pessoa.nome)
            html_txt = montar_html(
                org_short=ORG_SHORT,
                org_full=ORG_FULL,
                ano=ano,
                calendario=cal,
                itens=escolhidos,
                titulo=titulo,
                individual=individual,
            )
            path = salvar_html(html_txt, nome_arquivo=nome_arq)
            svc.registrar_evento(
                "relatorio",
                f"gerou {'comprovante de ' + escolhidos[0].pessoa.nome if individual else 'relatório da diretoria'} {ano}",
                nome=escolhidos[0].pessoa.nome if individual else "",
                ano=ano,
            )
            return str(path), meses_para_texto(cal)

        def ok(result) -> None:
            path, cal_txt = result
            cal_lbl.set("Calendário usado: " + cal_txt)
            webbrowser.open(path)
            messagebox.showinfo("Relatório", f"Aberto no navegador.\nCópia salva em:\n{path}")

        app._run_bg(work, ok, lambda e: messagebox.showerror("Relatório", str(e)), "Gerando relatório…")

    app._btn(box, "Gerar e abrir", gerar).pack(anchor="w", pady=(16, 0))
