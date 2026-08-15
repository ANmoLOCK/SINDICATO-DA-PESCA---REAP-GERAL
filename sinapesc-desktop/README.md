# Sinapesc Desktop — Controle de REAP

Programa para **notebook/computador** (Windows `.exe`) que substitui a versão web Next.js.
Os dados continuam na **Google Planilha**, com a implementação da API explicada de forma didática.

## O que o programa faz

- Login de administrador (local)
- Cadastro de associados (nome + CPF)
- Marcação mês a mês do REAP (jan–dez por ano)
- Lista pública com CPF mascarado
- Configuração visual da Conta de Serviço Google Sheets

## Como gerar o `.exe` no Windows

1. Instale [Python 3.10+](https://www.python.org/downloads/) (marque “Add Python to PATH”).
2. Abra a pasta `sinapesc-desktop`.
3. Dê dois cliques em `build_exe.bat` (ou rode no Prompt).
4. O instalável/executável sai em `dist\SinapescREAP.exe`.
5. Copie `SinapescREAP.exe` para o notebook e execute.

Não precisa instalar Python no notebook de destino — o `.exe` já leva as dependências.

## Como usar (primeira vez)

1. Abra o programa → **Configurações**.
2. Siga o guia na tela (ativar Google Sheets API, criar Conta de Serviço, baixar JSON).
3. **Importar JSON** da Conta de Serviço.
4. Colar o **ID da planilha** (parte da URL entre `/d/` e `/edit`).
5. Compartilhar a planilha com o e-mail da Conta de Serviço (Editor).
6. **Testar conexão** → **Salvar**.
7. Voltar ao início → **Entrar como administrador** (padrão: `admin@sinapesc.local` / `sinapesc` — altere em Configurações).

## Rodar em modo desenvolvimento (Python)

```bash
cd sinapesc-desktop
python -m pip install -r requirements.txt
python main.py
```

## Onde está a API Google Sheets (didática)

| Arquivo | Papel |
|---------|--------|
| `sheets/client.py` | Autenticação JWT + operações da API v4 (com comentários passo a passo) |
| `sheets/service.py` | Regras de negócio (Pessoas / REAP) — equivalente ao antigo `lib/sheets.ts` |
| `sheets/models.py` | Tipos de dados |
| `docs/GOOGLE_SHEETS.md` | Tutorial completo da integração |

## Estrutura da planilha (criada automaticamente)

**Pessoas:** `id | nome | cpf | criadoEm`  
**Reap:** `id | personId | ano | jan…dez | atualizadoEm`

## Relação com o ZIP original

O ZIP continha um app **Next.js (web)**. Este projeto reformula a mesma lógica em **aplicação desktop** instalável no notebook, mantendo a planilha Google como banco de dados.
