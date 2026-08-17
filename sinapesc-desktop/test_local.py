"""Testes locais sem chamar a API Google."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sheets.service import _row_to_pessoa, _row_to_reap  # noqa: E402
from ui.formatters import format_cpf, format_cpf_masked, get_initials, only_digits, parse_lote_lines  # noqa: E402


def test_formatters() -> None:
    assert only_digits("123.456.789-01") == "12345678901"
    assert format_cpf("12345678901") == "123.456.789-01"
    assert format_cpf_masked("12345678901") == "***.***.789-**"


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


if __name__ == "__main__":
    test_formatters()
    test_row_parsers()
    test_parse_lote()
    print("OK — testes locais passaram.")
