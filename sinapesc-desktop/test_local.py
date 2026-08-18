"""Testes locais sem chamar a API Google."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sheets.service import _row_to_pessoa, _row_to_reap  # noqa: E402
from sheets.models import meses_no_intervalo, meses_para_flags  # noqa: E402
from ui.formatters import format_cpf, format_cpf_masked, only_digits, parse_lote_lines  # noqa: E402


def test_meses_intervalo() -> None:
    assert meses_no_intervalo("mar", "out") == ["mar", "abr", "mai", "jun", "jul", "ago", "set", "out"]
    flags = meses_para_flags(["mar", "out"])
    assert flags[2] == "TRUE" and flags[9] == "TRUE" and flags[0] == "FALSE"



def test_formatters() -> None:
    assert only_digits("123.456.789-01") == "12345678901"
    assert format_cpf("12345678901") == "123.456.789-01"
    assert format_cpf_masked("12345678901") == "***.***.789-**"


def test_display_nome() -> None:
    from ui.formatters import display_nome

    assert display_nome("JOAO SILVA") == "Joao Silva"
    assert display_nome("Maria Pereira") == "Maria Pereira"


def test_parse_lote() -> None:
    itens = parse_lote_lines("Maria Silva;12345678901\nJoao,98765432100\n")
    assert itens[0] == ("Maria Silva", "12345678901")
    assert itens[1][0] == "Joao"


def test_row_parsers() -> None:
    p = _row_to_pessoa(["id1", "Maria", "12345678901", "2024-01-01"])
    assert p.nome == "Maria"
    r = _row_to_reap(
        ["rid", "id1", "2024", "TRUE", "FALSE", "FALSE", "FALSE", "FALSE", "FALSE",
         "FALSE", "FALSE", "FALSE", "FALSE", "FALSE", "FALSE", "now"]
    )
    assert r.ano == 2024
    assert r.meses["jan"] is True
    assert r.meses["fev"] is False


def test_controle_pendencias() -> None:
    from sheets.models import PessoaComReap, ReapAno, meses_vazios
    from controle.calendario import CALENDARIO_PADRAO, parse_meses
    from controle.pendencias import classificar

    assert parse_meses("mar, out, XYZ") == ["mar", "out"]
    meses = meses_vazios()
    for m in ("mar", "abr", "mai", "jun", "jul", "ago", "set"):
        meses[m] = True
    maria = PessoaComReap(
        id="1",
        nome="Maria",
        cpf="12345678901",
        criado_em="",
        anos=[ReapAno(id="r", person_id="1", ano=2026, meses=meses, atualizado_em="")],
    )
    joao = PessoaComReap(id="2", nome="Joao", cpf="98765432100", criado_em="", anos=[])
    pend, reg = classificar([maria, joao], 2026, CALENDARIO_PADRAO)
    assert [p.pessoa.nome for p in pend] == ["Joao", "Maria"]
    assert pend[1].faltando == ["out"]
    assert not reg


def test_auditoria_parse() -> None:
    from controle.auditoria import combina_busca, row_to_evento

    assert row_to_evento(["id", "em", "usuario"]) is None
    evt = row_to_evento(
        ["abc", "2026-08-18 09:00:00", "admin@x", "toggle_mes", "marcou OUT/2026 em Maria", "pid", "Maria", "2026", "out"]
    )
    assert evt is not None and evt.nome == "Maria"
    assert combina_busca(evt, "maria")
    assert not combina_busca(evt, "inexistente")


def test_relatorio_mostra_cpf_completo() -> None:
    from sheets.models import PessoaComReap, ReapAno, meses_vazios
    from controle.calendario import CALENDARIO_PADRAO
    from controle.pendencias import situacao_de
    from controle.relatorio import montar_html

    meses = meses_vazios()
    for m in CALENDARIO_PADRAO:
        meses[m] = True
    p = PessoaComReap(
        id="1", nome="Maria Silva", cpf="12345678901", criado_em="",
        anos=[ReapAno(id="r", person_id="1", ano=2026, meses=meses, atualizado_em="")],
    )
    item = situacao_de(p, 2026, CALENDARIO_PADRAO)
    html_txt = montar_html(
        org_short="Sinapesc",
        org_full="Sindicato",
        ano=2026,
        calendario=CALENDARIO_PADRAO,
        itens=[item],
        titulo="Teste",
        individual=True,
    )
    assert "123.456.789-01" in html_txt
    assert "***" not in html_txt
    assert "uso interno" in html_txt.lower()
    assert "não é comprovante de pagamento" in html_txt


def test_backup_rotacao() -> None:
    import tempfile
    from controle.backup import dias_desde, gravar_backup, listar_backups

    assert dias_desde("") is None
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for i in range(14):
            gravar_backup(
                pessoas_rows=[["id", "nome"], ["1", "A"]],
                reap_rows=[["id"]],
                stamp=f"2026-01-{i + 1:02d}_1000",
                root=root,
            )
        assert len(listar_backups(root)) == 12


def test_chrome_routes() -> None:
    from ui.chrome import SCREEN_MODES, TAB_FOR_SCREEN

    assert SCREEN_MODES["admin"] == "secretaria"
    assert SCREEN_MODES["settings"] == "public"
    assert TAB_FOR_SCREEN["pendencias"] == "pendencias"


def test_brand_assets() -> None:
    from ui.brand import asset_path

    logo = asset_path("logo.png")
    icon = asset_path("icon.png")
    ico = asset_path("icon.ico")
    mark = asset_path("watermark.png")
    assert logo.exists() and logo.stat().st_size > 10_000
    assert icon.exists() and icon.stat().st_size > 10_000
    assert ico.exists() and ico.stat().st_size > 10_000
    assert mark.exists() and mark.stat().st_size > 10_000
    from PIL import Image

    im = Image.open(logo)
    assert im.size[0] >= 256 and im.size[1] >= 256
    assert Image.open(mark).mode == "RGBA"


def test_qr_selo_usa_logo() -> None:
    from ui.qrutil import make_qr_image

    img = make_qr_image("https://example.com/consulta")
    assert img.size[0] >= 200 and img.size[1] >= 200


if __name__ == "__main__":
    test_formatters()
    test_display_nome()
    test_row_parsers()
    test_parse_lote()
    test_meses_intervalo()
    test_controle_pendencias()
    test_auditoria_parse()
    test_relatorio_mostra_cpf_completo()
    test_backup_rotacao()
    test_chrome_routes()
    test_brand_assets()
    test_qr_selo_usa_logo()
    print("OK — testes locais passaram.")
