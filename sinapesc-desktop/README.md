# Sinapesc Desktop

Programa Windows (Tkinter + Google Sheets) para controle REAP da secretaria.

| Documento | Link |
|-----------|------|
| README principal (download, site, versões) | [../README.md](../README.md) |
| Changelog | [../CHANGELOG.md](../CHANGELOG.md) |
| API Google | [COMO_INTEGRAR_API.md](./COMO_INTEGRAR_API.md) |
| Site público | [../site-publico/](../site-publico/) |

## Versão

**v1.6.1** — UI fusionada (header, abas, Voltar) + pendências, relatório, backup e auditoria.

## Desenvolvimento

```bash
pip install -r requirements.txt
python main.py
```

## Build EXE (Windows)

```bash
build_exe.bat
```

Ou dispare o workflow [build-windows-exe.yml](../.github/workflows/build-windows-exe.yml) (branch `main` ou tag `v*`).

## Estrutura

| Pasta / arquivo | Função |
|-----------------|--------|
| `controle/` | Regras: calendário, pendências, relatório, backup, auditoria |
| `ui/chrome.py` | Header, abas da secretaria, rodapé, navegação Voltar |
| `ui/tela_*.py` | Telas Pendências, Relatório, Backup, Auditoria |
| `sheets/` | Cliente e serviço Google Sheets |
| `build_exe.spec` | PyInstaller |
