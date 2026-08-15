"""Utilitários de formatação (CPF, iniciais)."""

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
