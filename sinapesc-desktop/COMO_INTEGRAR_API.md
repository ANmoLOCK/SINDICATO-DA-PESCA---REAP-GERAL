# Como colocar a API do Google Planilhas (já integrado)

Faça isso **uma vez**. Depois o programa abre e já fala com a planilha.

---

## 1) Criar a Conta de Serviço (o “robô” do Google)

1. Abra: https://console.cloud.google.com  
2. Crie um projeto (ou escolha um existente), ex.: `Sinapesc-REAP`  
3. Menu **APIs e serviços → Biblioteca**  
4. Procure **Google Sheets API** → clique → **Ativar**  
5. Menu **IAM e administrador → Contas de serviço → Criar conta de serviço**  
   - Nome: `sinapesc-reap`  
   - Criar e continuar (papéis podem ficar em branco)  
6. Abra a conta criada → aba **Chaves** → **Adicionar chave → Criar nova chave → JSON**  
7. Baixe o arquivo (algo como `projeto-xxxxx.json`)

Esse JSON é a API “pronta” do seu lado. **Não publique na internet.**

---

## 2) Preparar a planilha

1. Crie uma planilha no Google Drive (ou use uma existente)  
2. Copie o **ID** da URL:

```text
https://docs.google.com/spreadsheets/d/ COLE_ESTE_ID_AQUI /edit
```

3. Em **Compartilhar**, cole o e-mail que está dentro do JSON (`client_email`, termina com `iam.gserviceaccount.com`)  
4. Permissão: **Editor** → Enviar  

O programa cria sozinho as abas `Pessoas` e `Reap` na primeira conexão.

---

## 3) Deixar tudo integrado no notebook (junto do .exe)

Na **mesma pasta** do `SinapescREAP.exe`, coloque estes 2 arquivos:

### A) `google-credentials.json`
Renomeie o JSON baixado do Google Cloud para exatamente:

```text
google-credentials.json
```

### B) `config.json`
Crie um arquivo de texto com este conteúdo (troque o ID):

```json
{
  "spreadsheet_id": "COLE_AQUI_O_ID_DA_PLANILHA",
  "admin_email": "admin@sinapesc.local",
  "admin_password": "sinapesc"
}
```

Pasta final:

```text
C:\Sinapesc\
  SinapescREAP.exe
  google-credentials.json
  config.json
```

Abra o `.exe` → já deve estar integrado.  
Use **Configurações → Testar conexão** se quiser confirmar.

---

## Login do programa (não é login do Google)

- E-mail / senha do admin ficam no `config.json` (ou na tela Configurações)  
- Padrão: `admin@sinapesc.local` / `sinapesc`  
- Altere depois do primeiro acesso  

---

## Checklist rápido se der erro

| Erro | O que fazer |
|------|-------------|
| permission / 403 | Compartilhar a planilha com o `client_email` do JSON |
| API not enabled | Ativar Google Sheets API no Cloud Console |
| Spreadsheet not found | Conferir o `spreadsheet_id` no `config.json` |
| Credencial inválida | Usar o JSON de Conta de Serviço (não OAuth de usuário) |
