# Defeso Fácil — configuração

## O que colocar no `config.json`

Na pasta do EXE (`C:\Sinapesc\config.json`), use (ou complete) assim:

```json
{
  "spreadsheet_id": "ID_DA_PLANILHA_REAP",
  "defeso_spreadsheet_id": "1UxDjb78h7tYUnKXPcLVniuqAfWwrbvyf",
  "defeso_drive_folder_id": "COLE_AQUI_O_ID_DA_PASTA_DRIVE",
  "admin_email": "admin@sinapesc.local",
  "admin_password": "sinapesc",
  "public_site_url": "https://anmolock.github.io/sinapesc-casanova-reap"
}
```

### Campos novos

| Campo | O que é |
|-------|---------|
| `defeso_spreadsheet_id` | Planilha Defeso (já definida): `1UxDjb78h7tYUnKXPcLVniuqAfWwrbvyf` |
| `defeso_drive_folder_id` | ID da pasta `Sinapesc-Defeso` no Drive (anexos). Sem isso, ficha/impressão funcionam; anexos não. |

### Como pegar o ID da pasta Drive

URL da pasta:

```text
https://drive.google.com/drive/folders/ ESTE_E_O_ID
```

### Compartilhar (obrigatório)

1. Planilha Defeso → Compartilhar com o `client_email` do JSON → **Editor**
2. Pasta `Sinapesc-Defeso` → Compartilhar com o mesmo e-mail → **Editor**
3. Google Cloud: **Google Drive API** ativada (além da Sheets)

O EXE cria a aba **Defeso** sozinho na primeira abertura do módulo.

## Fluxo

Home → **Defeso Fácil** → login → lista REAP → Abrir ficha → preencher → Salvar → Gerar declaração / Imprimir → Anexos (Identidade, Carteira pesca, CAF)
