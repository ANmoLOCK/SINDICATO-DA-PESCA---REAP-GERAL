# Sinapesc REAP — Casa Nova

**Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova**

Sistema de controle da contribuição **REAP**: programa Windows para a secretaria e site público para o associado consultar o CPF no celular, **sem o notebook ligado**.

| | |
|--|--|
| Repositório | https://github.com/ANmoLOCK/sinapesc-casanova-reap |
| Tag desta versão | [**v1.5.0**](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.0) |
| Data | 17 de agosto de 2026 |

---

## 1. Download do programa (EXE v1.5.0)

**Clique neste link** (baixa o ZIP, não precisa entrar no Actions):

**https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP-Windows-v1.5.0.zip**

Ou só o executável:

**https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP.exe**

Página da versão (notas + arquivos):  
https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.0

O ZIP contém `SinapescREAP.exe`, `config.json` e os tutoriais. Extraia numa pasta (ex.: `C:\Sinapesc\`) e coloque o `google-credentials.json` junto.

---

## 2. Site público (já no ar)

O associado **não precisa** do GitHub aberto nem do PC da sede ligado.

| Página | URL |
|--------|-----|
| Consulta por CPF (QR da sede) | https://anmolock.github.io/sinapesc-casanova-reap/consulta.html |
| Lista pública | https://anmolock.github.io/sinapesc-casanova-reap/lista.html |
| Início | https://anmolock.github.io/sinapesc-casanova-reap/ |

**URL para colar no EXE** (Configurações → URL do site público). Sem `/consulta.html` no final:

```text
https://anmolock.github.io/sinapesc-casanova-reap
```

Planilha (modo leitor, a mesma do EXE):  
https://docs.google.com/spreadsheets/d/1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4/edit?usp=sharing

---

## 3. Novidades v1.6.0 (controle REAP)

No Admin, abaixo da lista de sócios:

| Botão | Função |
|-------|--------|
| **Pendências** | Quem ainda não tem os meses obrigatórios do ano (padrão mar–out). Marca só o que falta. |
| **Relatório** | HTML da diretoria ou comprovante de um sócio (**CPF completo**, só o admin gera). Sem R$. |
| **Backup** | Cópia CSV das abas Pessoas + Reap neste computador (lembrete semanal). |
| **Auditoria** | Histórico **na planilha Google** — todos os admins veem as alterações uns dos outros. |

Na primeira conexão o EXE cria as abas **Auditoria** e **Config** (calendário do ano). O site público continua lendo só Pessoas e Reap.

Plano detalhado: [`PLANO_FUNCOES_v16.md`](./PLANO_FUNCOES_v16.md)

---

## 4. Atualizações da v1.5.0 (detalhe)

Esta versão junta o que entrou depois da v1.3.0: site público estável, EXE azul com logo, e o lote visual.

### 3.1 Cadastro em lote (secretaria)

Antes o lote era uma **caixona de texto** (`Nome;CPF`), fácil de errar.

Agora cada sócio é uma **linha visual**:

- Campo **Nome completo**  
- Campo **CPF** (formata enquanto digita: `000.000.000-00`)  
- Botão **lixeira** para apagar a linha  
- **+ Adicionar linha** para incluir mais gente  
- **Importar arquivo** (CSV/TXT) continua: o arquivo vira essas linhas, não some  

Não mistura quantidade nem valor em R$ no lote: o REAP continua sendo **mês pago / não pago**.

### 3.2 Site público gratuito (Opção A)

- Pasta `site-publico/` no GitHub Pages (`gh-pages`)  
- Consulta por CPF, lista e comprovante individual (`pessoa.html?id=`)  
- Lê a Google Planilha em modo **Leitor** (qualquer pessoa com o link)  
- O notebook **não precisa ficar ligado**  
- Repositório público: `sinapesc-casanova-reap`  
- `config.js` já com o ID da planilha `1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4`  
- Leitor da aba `Pessoas` ignora linha de cabeçalho do Google (gviz)

### 3.3 EXE — QR e URL do site

- Campo **URL do site público** em Configurações  
- Se colar com `/consulta.html`, o programa **corta** e usa a raiz  
- **Salvar** grava a URL mesmo sem retestar a API  
- **Gerar QRs do site** / **QR Consulta CPF** apontam para o GitHub Pages  
- QRs ficam na pasta `qr-codes/` ao lado do `.exe` e **não mudam** enquanto a URL for a mesma  
- Tema azul oceano, logo Sinapesc e gráfica de peixe  

### 3.4 O que a secretaria continua fazendo no EXE

- Login administrativo  
- Cadastro individual de sócio  
- Clique no nome → anos → marcar meses do REAP  
- Busca na lista  
- Teste de conexão com a planilha (Conta de Serviço = **Editor**)

### 3.5 O que o associado faz no celular

1. Aponta a câmera no QR da sede  
2. Digita o CPF  
3. Vê só os próprios meses/anos  

---

## 5. Como instalar (resumo)

1. Baixe o ZIP: [SinapescREAP-Windows-v1.5.0.zip](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP-Windows-v1.5.0.zip)  
2. Extraia, por exemplo em `C:\Sinapesc\`  
3. Coloque `google-credentials.json` (JSON da Conta de Serviço) na mesma pasta  
4. Em `config.json`, confira o ID da planilha e:

```json
"public_site_url": "https://anmolock.github.io/sinapesc-casanova-reap"
```

5. Abra o `.exe` → **Configurações** → **Salvar** → **Testar conexão**  
6. **QR Consulta CPF** → salvar PNG → imprimir  

Guia completo: [`TUTORIAL_IMPLEMENTACAO.md`](./TUTORIAL_IMPLEMENTACAO.md)  
API Google passo a passo: [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md)

---

## 6. Duas peças (não misturar)

| Peça | Quem usa | Precisa do PC? | Precisa do GitHub aberto? |
|------|----------|----------------|---------------------------|
| `SinapescREAP.exe` | Secretaria | Sim, na sede | Não |
| Site `consulta.html` | Associado (QR) | Não | Não |

Os dois usam a **mesma planilha**. O EXE grava (Editor). O site só lê (Leitor).

Não é necessário domínio `.com.br`. O endereço gratuito do GitHub Pages já é o oficial desta versão.

---

## 7. Histórico de versões

| Versão | Tag | O que entrou | EXE |
|--------|-----|----------------|-----|
| **v1.6.0** | código nesta branch | Pendências · relatório HTML · backup CSV · auditoria na planilha | após merge / Actions |
| **v1.5.0** | [v1.5.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.0) | Lote visual · site `sinapesc-casanova-reap` · URL/QR sem travar | [ZIP direto](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP-Windows-v1.5.0.zip) |
| v1.4.0 | — (código na main, tag desta linha é a 1.5.0) | Site estático · UI azul · logo/peixe · Pages | [Actions 31863086521](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31863086521) |
| v1.3.0 | [v1.3.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.3.0) | QR estável · consulta CPF · cofre `qr-codes/` | [Actions 31860049095](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31860049095) |
| v1.2.0 | [v1.2.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.2.0) | Nome Casa Nova · lote texto · link público | [Actions 31858767536](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31858767536) |
| v1.1.0 | [v1.1.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.1.0) | Scroll · accordion · QR online | [Actions 31857220864](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31857220864) |
| v1.0.0 | [v1.0.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.0.0) | Primeiro EXE + Google Sheets | [Actions 31854798304](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31854798304) |

Histórico narrado: [`CHANGELOG.md`](./CHANGELOG.md)

---

## 8. Bugs registrados

| ID | Problema | Resolvido em |
|----|----------|----------------|
| B01 | Scroll quebrado | v1.1.0 |
| B02 | Todos os meses sempre abertos | v1.1.0 |
| B03 | Build Windows (ícone PNG) | v1.0.0 |
| B04 | API Google pouco clara | v1.0.0 |
| B05 | Texto `0/12 pagos` na lista do EXE | v1.2.0 |
| B06 | QR só na Wi‑Fi | v1.2.0 |
| B07 | Cadastro um a um inviável | v1.2.0 |
| B08 | `X/12 pagos` nas páginas do QR | v1.3.0 |
| B09 | Frase “CPF parcialmente oculto” | v1.3.0 |
| B10 | QR/túnel mudavam a cada geração | v1.3.0 |
| B11 | Consulta pública dependia do PC/túnel | v1.4.0 / v1.5.0 (site Pages) |
| B12 | QR pedia URL mesmo depois de colar o site | v1.5.0 (normaliza e salva) |
| B13 | Clique duplo na API / lambda de erro no fundo | v1.6.0 |
| B14 | Auditoria só no PC (outro admin não via) | v1.6.0 (aba Auditoria) |

---

## 9. Pastas do repositório

| Pasta / arquivo | Função |
|-----------------|--------|
| `sinapesc-desktop/` | Código do programa Windows (Tkinter + Sheets) |
| `sinapesc-desktop/controle/` | Pendências, relatório, backup (separado da UI) |
| `sinapesc-desktop/ui/tela_*.py` | Telas Pendências / Relatório / Backup / Auditoria |
| `site-publico/` | Site estático de consulta (GitHub Pages) |
| `.github/workflows/build-windows-exe.yml` | Gera o `.exe` a cada push na `main` |
| `.github/workflows/deploy-site.yml` | Publica `site-publico/` na branch `gh-pages` |
| `TUTORIAL_IMPLEMENTACAO.md` | Instalação completa (planilha → EXE → site → QR) |
| `CHANGELOG.md` | Notas de cada versão |

---

## 10. Segurança (quem pode mexer)

- **Código:** só quem tem acesso de escrita no GitHub (sua conta)  
- **Site:** qualquer um **lê** a consulta; não altera a planilha pelo celular  
- **Planilha:** Conta de Serviço = Editor (EXE); “qualquer pessoa com o link” = Leitor (site)  
- A aba **Auditoria** fica na planilha para os admins (Editor). O site público **não** a lê. Quem abrir o Google Sheets no modo leitor vê as abas da planilha — compartilhe a planilha só com a secretaria como Editor, e o site usa o modo leitor já configurado.  
- Não envie `google-credentials.json` nem a senha do admin para terceiros  

O GitHub **não precisa ficar aberto** para o site funcionar.
