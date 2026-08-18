# API Google Planilhas — guia didático (Sinapesc)

Este documento explica **como** o programa desktop fala com a planilha, sem assumir conhecimento prévio da API.

## Ideia central

```
[Programa Sinapesc.exe]
        │
        │ 1. Autentica com Conta de Serviço (e-mail + chave privada)
        ▼
[Google Sheets API v4]
        │
        │ 2. Lê / escreve células
        ▼
[Sua planilha no Google Drive]
   aba Pessoas  +  aba Reap  +  aba Auditoria  +  aba Config
```

Não usamos login interativo do usuário no Google. Usamos uma **Conta de Serviço** (“robô”) criada no Google Cloud. Isso é ideal para um programa interno no notebook.

## Passo 1 — Ativar a API

1. https://console.cloud.google.com
2. Crie ou selecione um projeto
3. **APIs e serviços → Biblioteca**
4. Busque **Google Sheets API** → **Ativar**

## Passo 2 — Criar Conta de Serviço e baixar JSON

1. **IAM e administrador → Contas de serviço → Criar**
2. Dê um nome (ex.: `sinapesc-reap`)
3. Em **Chaves → Adicionar chave → JSON** e baixe o arquivo
4. Guarde esse JSON com cuidado (é a “senha” do robô)

O JSON contém, entre outros:

- `client_email` — e-mail da conta de serviço
- `private_key` — chave PEM usada para assinar o acesso (JWT)

No código isso acontece em `sheets/client.py`:

```python
creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)
```

## Passo 3 — Compartilhar a planilha

A Conta de Serviço **não vê** planilhas privadas automaticamente.

1. Abra a planilha no navegador
2. **Compartilhar**
3. Cole o `client_email` do JSON
4. Permissão: **Editor**

## Passo 4 — ID da planilha

URL típica:

```
https://docs.google.com/spreadsheets/d/1AbCDefGHiJkLmNOpQ/edit
                                      └────── ID ──────┘
```

Esse ID é o `spreadsheet_id` salvo em Configurações.

## Passo 5 — Operações que o programa usa

| Operação | Método da API | Uso no Sinapesc |
|----------|---------------|-----------------|
| Listar abas / criar aba | `spreadsheets.get` + `batchUpdate` | `ensure_tabs()` |
| Ler células | `spreadsheets.values.get` | listar associados / REAP |
| Escrever células | `spreadsheets.values.update` | editar nome/CPF, marcar mês |
| Acrescentar linha | `spreadsheets.values.append` | novo associado / novo ano / **auditoria** |
| Apagar linha | `batchUpdate` → `deleteDimension` | remover associado |
| Várias células | `values.batchUpdate` | marcar REAP em massa / pendências |

Abas criadas automaticamente na primeira conexão:

| Aba | Colunas | Quem vê |
|-----|---------|---------|
| Pessoas | id, nome, cpf, criadoEm | EXE + site público |
| Reap | id, personId, ano, jan…dez, atualizadoEm | EXE + site público |
| Auditoria | id, em, usuario, acao, detalhe, personId, nome, ano, meses | **só o EXE e quem abre a planilha como Editor** |
| Config | chave, valor (calendário REAP do ano) | EXE (compartilhado entre admins) |

O site público (`site-publico/js/sheets.js`) lê **somente** Pessoas e Reap. A aba Auditoria não aparece na consulta por CPF.

## Escopo OAuth

Pedimos apenas:

```
https://www.googleapis.com/auth/spreadsheets
```

Assim o robô só acessa planilhas, não o Drive inteiro além do necessário pela Sheets API.

## Mapa do código

1. **`GoogleSheetsClient`** (`sheets/client.py`)  
   Camada fina: autentica e fala com a API.

2. **`SheetsService`** (`sheets/service.py`)  
   Camada de negócio: “adicionar pessoa”, “toggle mês”, etc.

3. **Módulo `controle/`**  
   Pendências, relatório HTML, backup CSV — sem falar com a API.

4. **Telas** (`ui/tela_pendencias.py`, `ui/tela_auditoria.py`, `ui/tela_relatorio.py`, `ui/tela_backup.py`)  
   Separadas da lista de sócios para não misturar bugs.

Essa separação deixa o aprendizado mais claro: primeiro entenda o cliente, depois as regras.

## Erros comuns

| Sintoma | Causa provável |
|---------|----------------|
| 403 / permission denied | Planilha não compartilhada com o e-mail da Conta de Serviço |
| API not enabled | Sheets API não ativada no projeto Cloud |
| Invalid credentials | JSON errado ou chave corrompida |
| Spreadsheet not found | ID da planilha incorreto |

Use o botão **Testar conexão** na tela de Configurações para validar esses pontos.
