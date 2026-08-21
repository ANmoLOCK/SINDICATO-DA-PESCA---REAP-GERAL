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

1. Planilha **REAP** (`spreadsheet_id`) → Compartilhar com o `client_email` → **Editor**
2. Planilha **Defeso** `1UxDjb78h7tYUnKXPcLVniuqAfWwrbvyf` → mesmo `client_email` → **Editor**
3. Pasta `Sinapesc-Defeso` → mesmo e-mail → **Editor**
4. Google Cloud: **Sheets API** + **Drive API** ativadas

Use só o ID limpo (sem `?hl=pt-br`):

```text
1UxDjb78h7tYUnKXPcLVniuqAfWwrbvyf
```

O EXE cria a aba **Defeso** sozinho na primeira abertura do módulo.

Se a planilha Defeso não estiver compartilhada, a partir da **v1.7.1** a lista de CPFs do REAP ainda abre (com aviso).

## Fluxo

Home → **Defeso Fácil** → login → lista REAP → Abrir ficha → preencher → Salvar → Gerar declaração / Imprimir → Anexos (Identidade, Carteira pesca, CAF)
