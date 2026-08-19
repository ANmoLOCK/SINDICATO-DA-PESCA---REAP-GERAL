# Tutorial de implementação — Sinapesc REAP v1.6.17

Guia para o **programa Windows** e o **site público** (consulta por CPF sem o notebook ligado).

**Download do EXE:** [SinapescREAP-Windows-v1.6.17.zip](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.17/SinapescREAP-Windows-v1.6.17.zip)  
**Página da release:** [v1.6.17](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.17)

> v1.6.17: ao lado do nome do sócio aparece há quanto tempo foi a última marca/desmarca de mês REAP (`1min atrás`, `4h atrás`, …), lido da aba **Auditoria** — todos os admins veem o mesmo contador.

Site: https://anmolock.github.io/sinapesc-casanova-reap/consulta.html

---

## Visão geral (2 peças)

| Peça | Para quem | Precisa do PC ligado? |
|------|-----------|------------------------|
| **SinapescREAP.exe** | Secretaria (cadastro, marcar REAP) | Sim, só na sede |
| **Site público** (`consulta.html`) | Associados no celular (QR) | **Não** |

Os dois usam a **mesma Google Planilha**.

---

## Parte 1 — Google Planilha + API (uma vez)

### 1.1 Conta de Serviço (robô do Google)

1. Abra https://console.cloud.google.com  
2. Crie/escolha um projeto (ex.: `Sinapesc-REAP`)  
3. **APIs e serviços → Biblioteca** → ative **Google Sheets API**  
4. **IAM → Contas de serviço → Criar** (nome: `sinapesc-reap`)  
5. Na conta → **Chaves → Criar chave → JSON** → baixe o arquivo  

### 1.2 Planilha

1. Crie (ou use) uma planilha no Google Drive  
2. Copie o **ID** da URL:

```text
https://docs.google.com/spreadsheets/d/ ESTE_ID_AQUI /edit
```

3. **Compartilhar** com o e-mail do JSON (`client_email`, termina com `iam.gserviceaccount.com`)  
   → permissão **Editor** (para o EXE gravar)  
4. **Também** compartilhe como **Qualquer pessoa com o link → Leitor**  
   (para o site público ler no celular)

Na primeira conexão o EXE cria as abas `Pessoas`, `Reap`, `Auditoria` e `Config`.

---

## Parte 2 — Instalar o EXE no notebook

1. Baixe o artefato no link do topo desta página  
2. Extraia numa pasta, por exemplo `C:\Sinapesc\`  
3. Renomeie o JSON do Google Cloud para:

```text
google-credentials.json
```

4. Edite `config.json` (já vem no ZIP):

```json
{
  "spreadsheet_id": "COLE_O_ID_DA_PLANILHA",
  "admin_email": "admin@sinapesc.local",
  "admin_password": "sinapesc",
  "public_site_url": ""
}
```

5. Pasta final:

```text
C:\Sinapesc\
  SinapescREAP.exe
  google-credentials.json
  config.json
```

6. Abra o `.exe` → **Configurações** → **Testar conexão**  
7. Login admin (e-mail/senha do `config.json`) → cadastre sócios e marque REAPs

Troque a senha padrão em Configurações.

---

## Parte 3 — Site público gratuito (Opção A)

Assim o associado consulta pelo celular **mesmo com o PC desligado**.

### 3.1 Configurar o site

No repositório, abra `site-publico/config.js` e cole o ID:

```js
window.SINAPESC_CONFIG = {
  orgShort: "Sinapesc",
  orgFull: "Sindicato Dos Aquicultores E Pescadores De Casa Nova",
  spreadsheetId: "COLE_O_MESMO_ID_DA_PLANILHA",
  pessoasCsvUrl: "",
  reapCsvUrl: "",
};
```

### 3.2 Publicar (GitHub Pages — recomendado)

1. Faça merge do código com a pasta `site-publico/` na branch `main`  
2. No GitHub do repositório: **Settings → Pages → Source: GitHub Actions**  
3. O workflow `Deploy site público` publica automaticamente  
4. URL típica:

```text
https://anmolock.github.io/sinapesc-casanova-reap/
```

Página de consulta:

```text
https://anmolock.github.io/sinapesc-casanova-reap/consulta.html
```

**Alternativa:** Cloudflare Pages / Netlify → envie só a pasta `site-publico`.

### 3.3 Ligar o EXE ao site

1. No EXE → **Configurações**  
2. Cole a **URL do site público** (sem `/consulta.html` no final)  
3. Clique **Salvar**  
4. Clique **Gerar QRs do site**  
5. Clique **QR Consulta CPF** → **Salvar PNG** → imprima e fixe na sede  

Os QRs ficam em `qr-codes/` ao lado do `.exe` e **não mudam** enquanto a URL do site for a mesma.

---

## Parte 4 — Uso no dia a dia

### Secretaria (EXE)
- Entrar como administrador  
- Cadastrar sócio (um a um, **lote**, ou Config.Atalhos)  
- **Pendências:** quem falta no calendário do ano; marcar só o que falta  
- **Relatório:** HTML da diretoria ou de um sócio (**CPF completo**, só nesta tela)  
- **Backup:** CSV local das abas Pessoas + Reap  
- **Auditoria:** o que cada admin alterou (aba na planilha, todos veem)  
- Clicar no nome → marcar meses do REAP  

### Associado (celular)
1. Apontar a câmera no QR da sede  
2. Digitar o CPF  
3. Ver só os próprios meses/anos (CPF **mascarado**)  

---

## Checklist se der erro

| Problema | Solução |
|----------|---------|
| EXE: permission / 403 | Compartilhar planilha com o `client_email` como **Editor** |
| Site: não carrega / timeout | Planilha como **Qualquer pessoa → Leitor** + `spreadsheetId` em `config.js` |
| API not enabled | Ativar Google Sheets API no Cloud Console |
| Spreadsheet not found | Conferir o ID (trecho entre `/d/` e `/edit`) |
| QR abre página errada | URL do site em Configurações deve ser a raiz do Pages, sem typo |
| Pages 404 | Ativar Pages (Actions) e esperar o deploy verde |

---

## Links úteis

| Item | Link |
|------|------|
| **EXE v1.6.15 (ZIP)** | https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.15/SinapescREAP-Windows-v1.6.15.zip |
| **Release v1.6.15** | https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.15 |
| Código | https://github.com/ANmoLOCK/sinapesc-casanova-reap |
| API detalhada | [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md) |
| Site público | [`site-publico/README.md`](./site-publico/README.md) |
| Changelog | [`CHANGELOG.md`](./CHANGELOG.md) |

---

*Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova*
