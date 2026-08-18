"""Utilitários de formatação (CPF, iniciais, nome na tela)."""

from __future__ import annotations


def only_digits(value: str, max_len: int = 11) -> str:
    return "".join(ch for ch in value if ch.isdigit())[:max_len]


def format_cpf(digits: str) -> str:
    clean = only_digits(digits)
    part1, part2, part3, part4 = clean[:3], clean[3:6], clean[6:9], clean[9:11]
    result = part1
    if part2:
        result += f".{part2}"
    if part3:
        result += f".{part3}"
    if part4:
        result += f"-{part4}"
    return result


def format_cpf_masked(digits: str) -> str:
    clean = only_digits(digits)
    if len(clean) != 11:
        return format_cpf(clean)
    return f"***.***.{clean[6:9]}-**"


def get_initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def display_nome(name: str) -> str:
    """Nome para a tela: se veio TODO EM CAPS da planilha, vira título."""
    txt = (name or "").strip()
    if not txt:
        return txt
    letters = [c for c in txt if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        return txt.title()
    return txt


def parse_lote_lines(raw: str) -> list[tuple[str, str]]:
    """Lê Nome + CPF de texto/CSV (uma pessoa por linha)."""
    import re

    itens: list[tuple[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("nome"):
            continue
        if ";" in line:
            parts = line.split(";", 1)
        elif "\t" in line:
            parts = line.split("\t", 1)
        elif "," in line:
            parts = line.rsplit(",", 1)
        else:
            parts = re.split(r"\s{2,}", line, maxsplit=1)
        if len(parts) < 2:
            continue
        itens.append((parts[0].strip().strip('"'), parts[1].strip().strip('"')))
    return itens
