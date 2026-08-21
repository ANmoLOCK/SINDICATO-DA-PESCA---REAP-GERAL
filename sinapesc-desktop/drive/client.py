"""Google Drive — anexos do Defeso Fácil (pasta por CPF)."""

from __future__ import annotations

import base64
import mimetypes
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

from sheets.client import DRIVE_SCOPES, SheetsConfigError
from ui.formatters import only_digits


ANEXO_NOMES = {
    "identidade": "identidade",
    "pesca": "carteira-pesca",
    "carteira_pesca": "carteira-pesca",
    "caf": "caf",
}


class DriveDefesoClient:
    def __init__(self, credentials_info: dict, *, parent_folder_id: str) -> None:
        folder = normalize_folder_id(parent_folder_id)
        if not folder:
            raise SheetsConfigError(
                "Configure defeso_drive_folder_id no config.json (pasta Sinapesc-Defeso)."
            )
        if not isinstance(credentials_info, dict):
            raise SheetsConfigError("Credenciais Google não configuradas.")
        creds = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=DRIVE_SCOPES
        )
        self._drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        self.parent_folder_id = folder

    @classmethod
    def from_config(cls, cfg: dict) -> "DriveDefesoClient":
        folder = str(cfg.get("defeso_drive_folder_id") or "").strip()
        creds = cfg.get("credentials_json")
        return cls(creds if isinstance(creds, dict) else {}, parent_folder_id=folder)


def normalize_folder_id(value: str) -> str:
    from sheets.client import normalize_sheet_id

    return normalize_sheet_id(value)

    def _find_child_folder(self, parent_id: str, name: str) -> Optional[str]:
        safe = name.replace("'", "\\'")
        q = (
            f"'{parent_id}' in parents and name = '{safe}' "
            f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        res = (
            self._drive.files()
            .list(q=q, spaces="drive", fields="files(id, name)", pageSize=5)
            .execute()
        )
        files = res.get("files") or []
        return files[0]["id"] if files else None

    def ensure_cpf_folder(self, cpf: str) -> str:
        digits = only_digits(cpf)
        if len(digits) != 11:
            raise ValueError("CPF inválido para pasta no Drive.")
        found = self._find_child_folder(self.parent_folder_id, digits)
        if found:
            return found
        meta = {
            "name": digits,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [self.parent_folder_id],
        }
        created = self._drive.files().create(body=meta, fields="id").execute()
        return created["id"]

    def listar_anexos(self, cpf: str) -> List[Dict[str, str]]:
        folder_id = self._find_child_folder(self.parent_folder_id, only_digits(cpf))
        if not folder_id:
            return []
        res = (
            self._drive.files()
            .list(
                q=f"'{folder_id}' in parents and trashed = false",
                spaces="drive",
                fields="files(id, name, mimeType, modifiedTime, webViewLink)",
                pageSize=50,
            )
            .execute()
        )
        out = []
        for f in res.get("files") or []:
            out.append(
                {
                    "id": f.get("id") or "",
                    "name": f.get("name") or "",
                    "mime": f.get("mimeType") or "",
                    "modified": f.get("modifiedTime") or "",
                    "url": f.get("webViewLink") or "",
                }
            )
        return out

    def upload_base64(
        self,
        *,
        cpf: str,
        kind: str,
        filename: str,
        data_b64: str,
        mime: str = "",
    ) -> Dict[str, Any]:
        key = (kind or "").strip().lower()
        stem = ANEXO_NOMES.get(key)
        if not stem:
            raise ValueError("Tipo de anexo inválido. Use: identidade, pesca, caf.")
        raw_name = (filename or f"{stem}.pdf").strip()
        ext = ""
        if "." in raw_name:
            ext = "." + raw_name.rsplit(".", 1)[-1].lower()
        if ext not in (".pdf", ".jpg", ".jpeg", ".png", ".webp"):
            ext = ".pdf"
        final_name = f"{stem}{ext}"
        mime = (mime or mimetypes.guess_type(final_name)[0] or "application/octet-stream").strip()

        payload = data_b64.strip()
        if "," in payload and payload.lower().startswith("data:"):
            payload = payload.split(",", 1)[1]
        try:
            content = base64.b64decode(payload)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("Arquivo inválido (base64).") from exc
        if not content:
            raise ValueError("Arquivo vazio.")
        if len(content) > 12 * 1024 * 1024:
            raise ValueError("Arquivo maior que 12 MB.")

        folder_id = self.ensure_cpf_folder(cpf)
        q = f"'{folder_id}' in parents and name = '{final_name}' and trashed = false"
        old = (
            self._drive.files()
            .list(q=q, spaces="drive", fields="files(id)", pageSize=10)
            .execute()
            .get("files")
            or []
        )
        for item in old:
            self._drive.files().delete(fileId=item["id"]).execute()

        media = MediaInMemoryUpload(content, mimetype=mime, resumable=False)
        created = (
            self._drive.files()
            .create(
                body={"name": final_name, "parents": [folder_id]},
                media_body=media,
                fields="id, name, webViewLink",
            )
            .execute()
        )
        return {
            "id": created.get("id") or "",
            "name": created.get("name") or final_name,
            "url": created.get("webViewLink") or "",
            "folder_id": folder_id,
            "kind": key,
        }
