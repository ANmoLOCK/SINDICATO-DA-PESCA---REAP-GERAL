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

### Campos

| Campo | O que é |
|-------|---------|
| `defeso_spreadsheet_id` | Planilha Defeso (dados da ficha) |
| `defeso_drive_folder_id` | Pasta no Drive para anexos (opcional). Sem isso, anexos vão para pasta **local** do EXE |

---

## Por que o Drive deu erro 403 (storage quota)?

A Conta de Serviço (**robô**) **não tem espaço** no “Meu Drive” pessoal.

Compartilhar uma pasta do Meu Drive com o robô **não resolve** upload de arquivo — o Google ainda usa a cota do robô (zero).

### Opções

**A) Usar pasta local (já funciona na v1.7.3)**  
Anexos ficam em:

```text
%APPDATA%\SinapescREAP\backups\defeso_anexos\{CPF}\
```

**B) Subir na nuvem de verdade**  
1. Crie um **Drive compartilhado** (Shared Drive) no Google Workspace  
2. Coloque a pasta Defeso **dentro** desse Drive compartilhado  
3. Adicione o `client_email` como membro (**Gerenciador de conteúdo**)  
4. Cole o ID dessa pasta em `defeso_drive_folder_id`

Conta Gmail gratuita (só Meu Drive) **não** consegue dar cota ao robô.

---

### Compartilhar planilha Defeso

1. Planilha REAP → `client_email` → Editor  
2. Planilha Defeso `1UxDjb78h7tYUnKXPcLVniuqAfWwrbvyf` → mesmo e-mail → Editor  

ID limpo (sem `?hl=pt-br`):

```text
1UxDjb78h7tYUnKXPcLVniuqAfWwrbvyf
```

## Fluxo

Home → **Defeso Fácil** → login → Abrir ficha → Salvar → Imprimir declaração → Anexar docs
