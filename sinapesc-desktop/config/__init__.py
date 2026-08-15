"""Persistência local de configuração (credenciais + login admin)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

APP_NAME = "SinapescREAP"


def app_data_dir() -> Path:
    """Pasta de dados do usuário (Windows: %APPDATA%\\SinapescREAP)."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return app_data_dir() / "config.json"


DEFAULT_CONFIG: Dict[str, Any] = {
    "spreadsheet_id": "",
    "service_account_email": "",
    "private_key": "",
    "credentials_json": None,
    "admin_email": "admin@sinapesc.local",
    "admin_password": "sinapesc",
}


def load_config() -> Dict[str, Any]:
    path = config_path()
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        merged = dict(DEFAULT_CONFIG)
        merged.update(data if isinstance(data, dict) else {})
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)


def save_config(cfg: Dict[str, Any]) -> None:
    path = config_path()
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def is_sheets_configured(cfg: Optional[Dict[str, Any]] = None) -> bool:
    cfg = cfg or load_config()
    if not cfg.get("spreadsheet_id"):
        return False
    if isinstance(cfg.get("credentials_json"), dict):
        return True
    return bool(cfg.get("service_account_email") and cfg.get("private_key"))


def import_credentials_file(json_path: str | Path) -> Dict[str, Any]:
    """Lê o arquivo JSON baixado do Google Cloud e devolve o dict."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("type") != "service_account":
        raise ValueError(
            "Arquivo inválido. Selecione o JSON da Conta de Serviço do Google Cloud."
        )
    if "client_email" not in data or "private_key" not in data:
        raise ValueError("JSON incompleto: faltam client_email ou private_key.")
    return data
