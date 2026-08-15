"""
Serviço de negócio: Pessoas + REAP sobre a planilha Google.

Tradução didática do antigo `lib/sheets.ts` (Next.js) para desktop Python.
Cada função pública corresponde a uma ação da interface.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .client import (
    PESSOAS_TAB,
    REAP_TAB,
    GoogleSheetsClient,
    SheetsConfigError,
)
from .models import MESES, MesKey, Pessoa, PessoaComReap, ReapAno, meses_vazios

# Reexport para a UI
__all__ = ["SheetsService", "SheetsConfigError"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_pessoa(row: List[str]) -> Pessoa:
    return Pessoa(
        id=row[0] if len(row) > 0 else "",
        nome=row[1] if len(row) > 1 else "",
        cpf=row[2] if len(row) > 2 else "",
        criado_em=row[3] if len(row) > 3 else "",
    )


def _cell_bool(value: str) -> bool:
    return str(value).strip().upper() == "TRUE"


def _row_to_reap(row: List[str]) -> ReapAno:
    meses: Dict[MesKey, bool] = {}
    for idx, mes in enumerate(MESES):
        cell = row[3 + idx] if len(row) > 3 + idx else "FALSE"
        meses[mes] = _cell_bool(cell)
    return ReapAno(
        id=row[0] if len(row) > 0 else "",
        person_id=row[1] if len(row) > 1 else "",
        ano=int(row[2]) if len(row) > 2 and str(row[2]).strip().isdigit() else 0,
        meses=meses,
        atualizado_em=row[3 + len(MESES)] if len(row) > 3 + len(MESES) else "",
    )


def _col_letter(index_zero_based: int) -> str:
    """Converte 0->A, 1->B, ... (suficiente para as ~16 colunas do REAP)."""
    return chr(ord("A") + index_zero_based)


class SheetsService:
    """Fachada usada pela interface gráfica."""

    def __init__(self, client: GoogleSheetsClient) -> None:
        self.client = client

    @classmethod
    def from_config(cls, cfg: dict) -> "SheetsService":
        """
        Monta o serviço a partir do dicionário salvo em config.json.

        Campos aceitos:
          - spreadsheet_id (obrigatório)
          - credentials_json (dict completo da chave Google)  OU
          - service_account_email + private_key
        """
        credentials_json = cfg.get("credentials_json")
        client = GoogleSheetsClient(
            service_account_email=cfg.get("service_account_email", ""),
            private_key=cfg.get("private_key", ""),
            spreadsheet_id=cfg.get("spreadsheet_id", ""),
            credentials_info=credentials_json if isinstance(credentials_json, dict) else None,
        )
        return cls(client)

    # ---- leituras -----------------------------------------------------

    def _pessoas_rows(self) -> tuple[List[List[str]], int]:
        self.client.ensure_tabs()
        rows = self.client.get_values(f"{PESSOAS_TAB}!A2:D")
        return rows, 2  # dados começam na linha 2 (1 = cabeçalho)

    def _reap_rows(self) -> tuple[List[List[str]], int]:
        self.client.ensure_tabs()
        last_col = _col_letter(3 + len(MESES))  # coluna de atualizadoEm
        rows = self.client.get_values(f"{REAP_TAB}!A2:{last_col}")
        return rows, 2

    def get_all_pessoas(self) -> List[Pessoa]:
        rows, _ = self._pessoas_rows()
        return [_row_to_pessoa(r) for r in rows if r and r[0]]

    def get_all_reap(self) -> List[ReapAno]:
        rows, _ = self._reap_rows()
        return [_row_to_reap(r) for r in rows if r and r[0]]

    def get_all_pessoas_com_reap(self) -> List[PessoaComReap]:
        pessoas = self.get_all_pessoas()
        reap = self.get_all_reap()
        resultado: List[PessoaComReap] = []
        for p in pessoas:
            anos = sorted(
                [r for r in reap if r.person_id == p.id],
                key=lambda x: x.ano,
                reverse=True,
            )
            resultado.append(
                PessoaComReap(
                    id=p.id,
                    nome=p.nome,
                    cpf=p.cpf,
                    criado_em=p.criado_em,
                    anos=anos,
                )
            )
        return resultado

    def get_pessoa_com_reap(self, person_id: str) -> Optional[PessoaComReap]:
        for p in self.get_all_pessoas_com_reap():
            if p.id == person_id:
                return p
        return None

    # ---- escritas -----------------------------------------------------

    def add_pessoa(self, nome: str, cpf: str) -> PessoaComReap:
        self.client.ensure_tabs()
        person_id = str(uuid.uuid4())
        now = _now_iso()
        ano_atual = datetime.now().year

        self.client.append_values(
            f"{PESSOAS_TAB}!A2",
            [[person_id, nome, cpf, now]],
        )

        reap_id = str(uuid.uuid4())
        meses_row = ["FALSE"] * len(MESES)
        self.client.append_values(
            f"{REAP_TAB}!A2",
            [[reap_id, person_id, ano_atual, *meses_row, now]],
        )

        return PessoaComReap(
            id=person_id,
            nome=nome,
            cpf=cpf,
            criado_em=now,
            anos=[
                ReapAno(
                    id=reap_id,
                    person_id=person_id,
                    ano=ano_atual,
                    meses=meses_vazios(),
                    atualizado_em=now,
                )
            ],
        )

    def add_pessoas_lote(self, itens: List[tuple[str, str]]) -> dict:
        """
        Cadastra vários sócios de uma vez.
        itens = [(nome, cpf), ...]
        Retorna {ok: int, erros: list[str], ids: list[str]}.
        """
        self.client.ensure_tabs()
        existentes = {p.cpf for p in self.get_all_pessoas()}
        now = _now_iso()
        ano_atual = datetime.now().year

        pessoas_rows: List[list] = []
        reap_rows: List[list] = []
        ids: List[str] = []
        erros: List[str] = []
        vistos: set[str] = set()

        for i, (nome, cpf) in enumerate(itens, start=1):
            nome = (nome or "").strip()
            cpf = "".join(ch for ch in (cpf or "") if ch.isdigit())[:11]
            if not nome:
                erros.append(f"Linha {i}: nome vazio.")
                continue
            if len(cpf) != 11:
                erros.append(f"Linha {i} ({nome}): CPF deve ter 11 dígitos.")
                continue
            if cpf in existentes or cpf in vistos:
                erros.append(f"Linha {i} ({nome}): CPF já cadastrado ou duplicado no lote.")
                continue
            vistos.add(cpf)
            person_id = str(uuid.uuid4())
            reap_id = str(uuid.uuid4())
            pessoas_rows.append([person_id, nome, cpf, now])
            reap_rows.append([reap_id, person_id, ano_atual, *(["FALSE"] * len(MESES)), now])
            ids.append(person_id)

        if pessoas_rows:
            self.client.append_values(f"{PESSOAS_TAB}!A2", pessoas_rows)
            self.client.append_values(f"{REAP_TAB}!A2", reap_rows)

        return {"ok": len(ids), "erros": erros, "ids": ids}

    def update_pessoa(self, person_id: str, nome: str, cpf: str) -> None:
        rows, start = self._pessoas_rows()
        idx = next((i for i, r in enumerate(rows) if r and r[0] == person_id), -1)
        if idx < 0:
            raise ValueError("Pessoa não encontrada.")
        row_number = start + idx
        self.client.update_values(
            f"{PESSOAS_TAB}!B{row_number}:C{row_number}",
            [[nome, cpf]],
        )

    def delete_pessoa(self, person_id: str) -> None:
        self.client.ensure_tabs()
        sheet_ids = self.client.get_sheet_ids_by_title()
        pessoas_sheet_id = sheet_ids.get(PESSOAS_TAB)
        reap_sheet_id = sheet_ids.get(REAP_TAB)

        pessoas_rows, pessoas_start = self._pessoas_rows()
        reap_rows, reap_start = self._reap_rows()

        requests: List[dict] = []

        p_idx = next((i for i, r in enumerate(pessoas_rows) if r and r[0] == person_id), -1)
        if p_idx >= 0 and pessoas_sheet_id is not None:
            # deleteDimension usa índice 0-based (linha 1 da planilha = índice 0)
            row_index = pessoas_start + p_idx - 1
            requests.append(
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": pessoas_sheet_id,
                            "dimension": "ROWS",
                            "startIndex": row_index,
                            "endIndex": row_index + 1,
                        }
                    }
                }
            )

        # Apagar de baixo para cima para não deslocar índices
        reap_indexes = sorted(
            [
                reap_start + i - 1
                for i, r in enumerate(reap_rows)
                if len(r) > 1 and r[1] == person_id
            ],
            reverse=True,
        )
        if reap_sheet_id is not None:
            for row_index in reap_indexes:
                requests.append(
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": reap_sheet_id,
                                "dimension": "ROWS",
                                "startIndex": row_index,
                                "endIndex": row_index + 1,
                            }
                        }
                    }
                )

        self.client.batch_update(requests)

    def toggle_mes(
        self,
        person_id: str,
        ano: int,
        mes: MesKey,
        novo_status: bool,
    ) -> None:
        rows, start = self._reap_rows()
        idx = next(
            (
                i
                for i, r in enumerate(rows)
                if len(r) > 2 and r[1] == person_id and str(r[2]).strip() == str(ano)
            ),
            -1,
        )
        if idx < 0:
            raise ValueError("Ano não encontrado para esta pessoa.")

        row_number = start + idx
        mes_idx = MESES.index(mes)
        col = _col_letter(3 + mes_idx)
        now = _now_iso()

        self.client.update_values(
            f"{REAP_TAB}!{col}{row_number}",
            [["TRUE" if novo_status else "FALSE"]],
        )
        atualizado_col = _col_letter(3 + len(MESES))
        self.client.update_values(
            f"{REAP_TAB}!{atualizado_col}{row_number}",
            [[now]],
        )

    def add_ano(self, person_id: str, ano: int) -> ReapAno:
        rows, _ = self._reap_rows()
        ja_existe = any(
            len(r) > 2 and r[1] == person_id and str(r[2]).strip() == str(ano)
            for r in rows
        )
        if ja_existe:
            raise ValueError("Este ano já existe para esta pessoa.")

        reap_id = str(uuid.uuid4())
        now = _now_iso()
        meses_row = ["FALSE"] * len(MESES)
        self.client.append_values(
            f"{REAP_TAB}!A2",
            [[reap_id, person_id, ano, *meses_row, now]],
        )
        return ReapAno(
            id=reap_id,
            person_id=person_id,
            ano=ano,
            meses=meses_vazios(),
            atualizado_em=now,
        )
