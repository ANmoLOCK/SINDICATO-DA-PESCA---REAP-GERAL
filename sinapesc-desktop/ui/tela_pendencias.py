"""Tela Admin → Pendências REAP (módulo separado da lista de sócios)."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, List

from controle.calendario import CALENDARIO_PADRAO, meses_para_texto, normalizar_meses
from controle.pendencias import SituacaoReap, classificar
from sheets.models import MESES, MESES_LABEL
from ui.formatters import format_cpf, only_digits
from ui.scroll import ScrollableFrame
from ui.theme import COLORS, FONT_DISPLAY, FONT_FAMILY

if TYPE_CHECKING:
    from ui import SinapescApp


def show_pendencias(app: "SinapescApp") -> None:
    from ui.chrome import page_wrap

    wrap = page_wrap(app)

    top = tk.Frame(wrap, bg=COLORS["content"])
    top.pack(fill="x", pady=(0, 8))
    tk.Label(
        top, text="Pendências REAP", bg=COLORS["content"], fg=COLORS["primary"],
        font=(FONT_DISPLAY, 20, "bold"),
    ).pack(side="left")

    stats = tk.StringVar(value="Carregando…")
    cal_var = tk.StringVar(value="")
    tk.Label(top, textvariable=stats, bg=COLORS["content"], fg=COLORS["muted"], font=(FONT_FAMILY, 10)).pack(
        side="left", padx=12
    )

    tools = tk.Frame(wrap, bg=COLORS["content"])
    tools.pack(fill="x", pady=(0, 8))
    tk.Label(tools, text="Ano", bg=COLORS["content"], fg=COLORS["muted"]).pack(side="left")
    ano_ent = ttk.Entry(tools, width=8)
    ano_ent.insert(0, str(datetime.now().year))
    ano_ent.pack(side="left", padx=8)

    tk.Label(tools, textvariable=cal_var, bg=COLORS["content"], fg=COLORS["accent"], font=(FONT_FAMILY, 9, "bold")).pack(
        side="left", padx=8
    )

    search_var = tk.StringVar()
    tk.Label(tools, text="Buscar", bg=COLORS["content"], fg=COLORS["muted"]).pack(side="left", padx=(16, 4))
    ttk.Entry(tools, textvariable=search_var, width=28).pack(side="left")

    scroll = ScrollableFrame(wrap, bg=COLORS["content"])
    scroll.pack(fill="both", expand=True)
    lista = scroll.inner
    app._scroll = scroll

    state: dict = {"pendentes": [], "regulares": [], "calendario": list(CALENDARIO_PADRAO), "ano": datetime.now().year}

    def ano_atual() -> int | None:
        txt = ano_ent.get().strip()
        if not txt.isdigit():
            return None
        ano = int(txt)
        if ano < 2000 or ano > 2100:
            return None
        return ano

    def filtrar(itens: List[SituacaoReap]) -> List[SituacaoReap]:
        q = search_var.get().strip().lower()
        digits = only_digits(q)
        if not q:
            return itens
        out = []
        for s in itens:
            if q in s.pessoa.nome.lower() or (digits and digits in s.pessoa.cpf):
                out.append(s)
        return out

    def render() -> None:
        for child in lista.winfo_children():
            child.destroy()
        visiveis = filtrar(state["pendentes"])
        n_p, n_r = len(state["pendentes"]), len(state["regulares"])
        n_all = n_p + n_r
        stats.set(f"{n_p} pendente(s) · {n_r} regular(es) · {n_all} sócio(s)")
        cal_var.set("Calendário: " + meses_para_texto(state["calendario"]))
        if not visiveis:
            msg = "Nenhum pendente neste ano." if not search_var.get().strip() else "Nenhum pendente na busca."
            if n_all == 0:
                msg = "Nenhum sócio cadastrado."
            tk.Label(lista, text=msg, bg=COLORS["content"], fg=COLORS["muted"]).pack(anchor="w", pady=20)
            return
        for s in visiveis:
            _card_pendente(app, lista, s, on_marcar=lambda item=s: marcar_um(item))

    def recarregar() -> None:
        ano = ano_atual()
        if ano is None:
            messagebox.showerror("Pendências", "Informe um ano entre 2000 e 2100.")
            return
        try:
            svc = app._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc))
            return

        def work():
            pessoas = svc.get_all_pessoas_com_reap()
            cal = svc.get_calendario(ano)
            return pessoas, cal

        def ok(result) -> None:
            pessoas, cal = result
            app._pessoas = pessoas
            state["ano"] = ano
            state["calendario"] = cal or list(CALENDARIO_PADRAO)
            pend, reg = classificar(pessoas, ano, state["calendario"])
            state["pendentes"], state["regulares"] = pend, reg
            render()

        app._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Carregando pendências…")

    def marcar_um(item: SituacaoReap) -> None:
        if not item.faltando:
            return
        nomes = ", ".join(m.upper() for m in item.faltando)
        if not messagebox.askyesno(
            "Confirmar",
            f"Marcar {nomes} em {item.ano} para {item.pessoa.nome}?\n\n"
            "Só liga o que falta. Não apaga mês já marcado.",
        ):
            return
        _aplicar_marcacao(app, item.ano, item.faltando, [item.pessoa.id], recarregar)

    def marcar_lista() -> None:
        visiveis = filtrar(state["pendentes"])
        if not visiveis:
            messagebox.showwarning("Pendências", "Nenhum pendente nesta lista.")
            return
        if not state["calendario"]:
            messagebox.showwarning("Pendências", "Defina o calendário obrigatório antes.")
            return
        if not messagebox.askyesno(
            "Confirmar",
            f"Marcar os meses que faltam (calendário {meses_para_texto(state['calendario'])}) "
            f"em {len(visiveis)} sócio(s) de {state['ano']}?",
        ):
            return
        ids = [s.pessoa.id for s in visiveis]
        _aplicar_marcacao(app, state["ano"], state["calendario"], ids, recarregar)

    def alterar_cal() -> None:
        ano = ano_atual()
        if ano is None:
            messagebox.showerror("Pendências", "Informe um ano válido.")
            return
        _dialog_calendario(app, ano, state["calendario"], on_saved=recarregar)

    app._btn(tools, "Atualizar", recarregar, kind="ghost").pack(side="right", padx=4)
    app._btn(tools, "Alterar calendário…", alterar_cal, kind="ghost").pack(side="right", padx=4)
    app._btn(tools, "Marcar pendentes desta lista", marcar_lista, kind="accent").pack(side="right", padx=4)

    search_var.trace_add("write", lambda *_: render())
    recarregar()


def _card_pendente(app: "SinapescApp", parent, item: SituacaoReap, *, on_marcar) -> None:
    card = tk.Frame(parent, bg=COLORS["surface"], padx=14, pady=10, highlightbackground=COLORS["border"], highlightthickness=1)
    card.pack(fill="x", pady=5, padx=2)
    head = tk.Frame(card, bg=COLORS["surface"])
    head.pack(fill="x")
    info = tk.Frame(head, bg=COLORS["surface"])
    info.pack(side="left", fill="x", expand=True)
    tk.Label(
        info, text=item.pessoa.nome, bg=COLORS["surface"], fg=COLORS["primary"],
        font=(FONT_DISPLAY, 11, "bold"), anchor="w",
    ).pack(anchor="w")
    tk.Label(
        info, text=f"CPF: {format_cpf(item.pessoa.cpf)} · {item.rotulo_faltando}",
        bg=COLORS["surface"], fg=COLORS["muted"], font=(FONT_FAMILY, 9), anchor="w",
    ).pack(anchor="w")
    grid = tk.Frame(card, bg=COLORS["surface"])
    grid.pack(fill="x", pady=(8, 0))
    obr = set(item.obrigatorio)
    from controle.pendencias import meses_marcados

    marks = meses_marcados(item.pessoa, item.ano)
    for i, mes in enumerate(MESES):
        on = marks.get(mes)
        req = mes in obr
        if on:
            bg, fg, mark = COLORS["month_on"], COLORS["success"], "✓"
        elif req:
            bg, fg, mark = COLORS["danger_bg"], COLORS["danger"], "·"
        else:
            bg, fg, mark = COLORS["month_off"], COLORS["muted"], "·"
        tk.Label(
            grid, text=f"{mes.upper()}\n{mark}", width=5, height=2, bg=bg, fg=fg,
            font=(FONT_FAMILY, 8, "bold"),
        ).grid(row=i // 6, column=i % 6, padx=3, pady=3)
    actions = tk.Frame(head, bg=COLORS["surface"])
    actions.pack(side="right")
    app._btn(actions, "Marcar só os pendentes", on_marcar, padx=8, pady=4, font_size=9).pack(side="left", padx=2)

    def abrir_ficha() -> None:
        app._expanded_ids.add(item.pessoa.id)
        app.show_admin()

    app._btn(actions, "Abrir ficha", abrir_ficha, kind="ghost", padx=8, pady=4, font_size=9, bold=False).pack(
        side="left", padx=2
    )


def _aplicar_marcacao(app: "SinapescApp", ano: int, meses: List[str], person_ids: List[str], on_done) -> None:
    try:
        svc = app._ensure_service()
    except Exception as exc:  # noqa: BLE001
        messagebox.showerror("Sheets", str(exc))
        return

    def work():
        return svc.marcar_meses_em_massa(
            ano=ano,
            meses_on=meses,
            person_ids=person_ids,
            substituir=False,
        )

    def ok(res: dict) -> None:
        messagebox.showinfo(
            "Pendências",
            f"Atualizados: {res.get('atualizados', 0)}\nAnos criados: {res.get('criados', 0)}",
        )
        on_done()

    app._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e)), "Marcando pendentes…")


def _dialog_calendario(app: "SinapescApp", ano: int, atuais: List[str], *, on_saved) -> None:
    win = tk.Toplevel(app)
    win.title("Calendário REAP")
    win.configure(bg=COLORS["surface"])
    win.geometry("520x320")
    win.transient(app)
    win.grab_set()
    tk.Label(
        win,
        text=f"Meses obrigatórios de {ano}",
        bg=COLORS["surface"],
        fg=COLORS["primary"],
        font=(FONT_DISPLAY, 13, "bold"),
    ).pack(anchor="w", padx=16, pady=(14, 4))
    tk.Label(
        win,
        text="Vale para todos os administradores (aba Config da planilha). Não mistura com pagamento.",
        bg=COLORS["surface"],
        fg=COLORS["muted"],
        font=(FONT_FAMILY, 9),
        wraplength=480,
        justify="left",
    ).pack(anchor="w", padx=16)

    vars_mes = {m: tk.BooleanVar(value=m in set(atuais)) for m in MESES}

    def aplicar(meses):
        ligados = set(meses)
        for m, var in vars_mes.items():
            var.set(m in ligados)

    presets = tk.Frame(win, bg=COLORS["surface"])
    presets.pack(fill="x", padx=16, pady=8)
    from sheets.models import meses_no_intervalo

    app._btn(presets, "Mar → Out", lambda: aplicar(meses_no_intervalo("mar", "out")), kind="ghost", padx=8, pady=3, font_size=9).pack(side="left", padx=(0, 4))
    app._btn(presets, "Ano inteiro", lambda: aplicar(list(MESES)), kind="ghost", padx=8, pady=3, font_size=9).pack(side="left", padx=4)
    app._btn(presets, "Limpar", lambda: aplicar([]), kind="ghost", padx=8, pady=3, font_size=9).pack(side="left", padx=4)

    grid = tk.Frame(win, bg=COLORS["surface"])
    grid.pack(fill="x", padx=16)
    for i, mes in enumerate(MESES):
        tk.Checkbutton(
            grid,
            text=MESES_LABEL[mes][:3],
            variable=vars_mes[mes],
            bg=COLORS["surface"],
            fg=COLORS["primary"],
            selectcolor=COLORS["surface_soft"],
            activebackground=COLORS["surface"],
            font=(FONT_FAMILY, 9),
        ).grid(row=i // 6, column=i % 6, sticky="w", padx=4, pady=2)

    def salvar() -> None:
        escolhidos = normalizar_meses([m for m, v in vars_mes.items() if v.get()])
        if not escolhidos:
            messagebox.showwarning("Calendário", "Escolha pelo menos um mês.", parent=win)
            return
        try:
            svc = app._ensure_service()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Sheets", str(exc), parent=win)
            return

        def work():
            return svc.set_calendario(escolhidos, ano=ano)

        def ok(_meses) -> None:
            win.destroy()
            on_saved()

        app._run_bg(work, ok, lambda e: messagebox.showerror("Erro", str(e), parent=win), "Salvando calendário…")

    app._btn(win, "Salvar calendário", salvar).pack(pady=16)
