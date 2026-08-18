# Sinapesc REAP — Casa Nova

**Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova**

Sistema de **controle de REAP** (não é programa de pagamento): o EXE da secretaria grava a planilha Google; o associado consulta o CPF no celular **sem o notebook ligado**.

| | |
|--|--|
| Repositório | https://github.com/ANmoLOCK/sinapesc-casanova-reap |
| Tag desta versão | [**v1.6.0**](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.0) |
| Data | 18 de agosto de 2026 |
| Site (consulta) | https://anmolock.github.io/sinapesc-casanova-reap/consulta.html |

---

## 1. Download

### Código desta versão (tag v1.6.0)

Página da tag (notas + fonte):  
https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.0

O GitHub Actions gera o EXE quando a tag `v*` é enviada: **Actions → Build Sinapesc Windows EXE → artifact `SinapescREAP-Windows`**.

### Último ZIP público (v1.5.1 — Config.Atalhos)

Enquanto o artefato da v1.6.0 não estiver na release, use o ZIP que já baixa sem login:

**https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.1/SinapescREAP-Windows-v1.5.1.zip**

Extraia numa pasta (ex.: `C:\Sinapesc\`) e coloque o `google-credentials.json` junto.

---

## 2. Site público (já no ar)

O associado **não precisa** do GitHub aberto nem do PC da sede ligado.

| Página | URL |
|--------|-----|
| Consulta por CPF (QR da sede) | https://anmolock.github.io/sinapesc-casanova-reap/consulta.html |
| Lista pública | https://anmolock.github.io/sinapesc-casanova-reap/lista.html |
| Início | https://anmolock.github.io/sinapesc-casanova-reap/ |

**URL para colar no EXE** (Configurações). Sem `/consulta.html` no final:

```text
https://anmolock.github.io/sinapesc-casanova-reap
```

Planilha (modo leitor, a mesma do EXE):  
https://docs.google.com/spreadsheets/d/1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4/edit?usp=sharing

O site lê **somente** as abas Pessoas e Reap. CPF no celular fica **mascarado**.

---

## 3. O que há na v1.6.0

No Admin, faixa extra: **Pendências · Relatório · Backup · Auditoria**.

| Botão | O que faz |
|-------|-----------|
| **Pendências** | Lista só quem falta no calendário do ano (padrão **mar–out**). Marca só o que falta, sem apagar mês já marcado. |
| **Relatório** | HTML da diretoria ou de um sócio, com logo. **CPF completo** — só o admin nesta tela. Imprimir → Salvar como PDF. Sem R$. |
| **Backup** | Cópia CSV das abas Pessoas + Reap na pasta `backups/` (lembrete a cada 7 dias). |
| **Auditoria** | Histórico **na planilha Google** (aba Auditoria). Todos os admins veem o que o outro alterou. |

Na primeira conexão o EXE cria as abas **Auditoria** e **Config** (calendário compartilhado).

Código separado do Admin antigo:

- Regras: `sinapesc-desktop/controle/`
- Telas: `ui/tela_pendencias.py`, `tela_relatorio.py`, `tela_backup.py`, `tela_auditoria.py`

Plano: [`PLANO_FUNCOES_v16.md`](./PLANO_FUNCOES_v16.md) · Notas: [`CHANGELOG.md`](./CHANGELOG.md)

---

## 4. O que já existia (v1.5.1 e v1.5.0)

### Config.Atalhos (v1.5.1)

Ao lado de **Atualizar**: lote com REAP já marcado (Mar→Out), marcar meses em massa, copiar um ano para outro. Escritas em lote na API.

### Cadastro em lote (v1.5.0)

Cada sócio numa linha: Nome, CPF (máscara ao digitar), lixeira. Importar CSV/TXT vira essas linhas. Sem R$ no lote.

### Site + QR

URL do site em Configurações; se colar com `/consulta.html`, o programa usa a raiz. QRs permanentes em `qr-codes/`.

---

## 5. Como instalar (resumo)

1. Extraia o ZIP do EXE  
2. Coloque `google-credentials.json` (Conta de Serviço) na mesma pasta  
3. Em `config.json`, confira o ID da planilha e:

```json
"public_site_url": "https://anmolock.github.io/sinapesc-casanova-reap"
```

4. Abra o `.exe` → **Configurações** → **Salvar** → **Testar conexão**  
5. **QR Consulta CPF** → salvar PNG → imprimir  
6. Login admin → Pendências / Relatório / Backup / Auditoria (v1.6.0)

Guia completo: [`TUTORIAL_IMPLEMENTACAO.md`](./TUTORIAL_IMPLEMENTACAO.md)  
API: [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md)

---

## 6. Duas peças (não misturar)

| Peça | Quem usa | Precisa do PC? | Precisa do GitHub aberto? |
|------|----------|----------------|---------------------------|
| `SinapescREAP.exe` | Secretaria | Sim, na sede | Não |
| Site `consulta.html` | Associado (QR) | Não | Não |

Os dois usam a **mesma planilha**. O EXE grava (Editor). O site só lê (Leitor).

Não é necessário domínio `.com.br`. O GitHub Pages já é o endereço oficial.

---

## 7. Histórico de versões

| Versão | Tag | O que entrou | EXE |
|--------|-----|----------------|-----|
| **v1.6.0** | [v1.6.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.0) | Pendências · relatório HTML (CPF admin) · backup CSV · auditoria na planilha | Actions (tag) |
| **v1.5.1** | [v1.5.1](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.1) | Config.Atalhos: lote pré-marcado · massa · copiar ano | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.1/SinapescREAP-Windows-v1.5.1.zip) |
| v1.5.0 | [v1.5.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.0) | Lote visual · site Pages · URL/QR | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP-Windows-v1.5.0.zip) |
| v1.4.0 | — | Site estático · UI azul · logo/peixe | [Actions 31863086521](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31863086521) |
| v1.3.0 | [v1.3.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.3.0) | QR estável · consulta CPF | [Actions 31860049095](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31860049095) |
| v1.2.0 | [v1.2.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.2.0) | Casa Nova · lote texto | [Actions 31858767536](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31858767536) |
| v1.1.0 | [v1.1.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.1.0) | Scroll · accordion · QR | [Actions 31857220864](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31857220864) |
| v1.0.0 | [v1.0.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.0.0) | Primeiro EXE + Sheets | [Actions 31854798304](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/31854798304) |

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
| B12 | QR pedia URL mesmo depois de colar o site | v1.5.0 |
| B13 | Clique duplo na API / erro perdido no thread | v1.6.0 |
| B14 | Auditoria só no PC (outro admin não via) | v1.6.0 (aba Auditoria) |
| B15 | Relatório mascarava CPF do admin | v1.6.0 (CPF completo só no Relatório) |

---

## 9. Pastas do repositório

| Pasta / arquivo | Função |
|-----------------|--------|
| `sinapesc-desktop/` | Programa Windows (Tkinter + Sheets) |
| `sinapesc-desktop/controle/` | Pendências, relatório, backup (separado da UI) |
| `sinapesc-desktop/ui/tela_*.py` | Telas Pendências / Relatório / Backup / Auditoria |
| `site-publico/` | Site estático (GitHub Pages) |
| `.github/workflows/build-windows-exe.yml` | Gera o `.exe` (main + tags `v*`) |
| `.github/workflows/deploy-site.yml` | Publica o site em `gh-pages` |
| `TUTORIAL_IMPLEMENTACAO.md` | Instalação completa |
| `CHANGELOG.md` | Notas de cada versão |
| `PLANO_FUNCOES_v16.md` | Plano das funções v1.6.0 |
| `MELHORIAS.md` | O que já entrou e o que fica para depois |

---

## 10. Segurança

- **Código:** só quem tem escrita no GitHub  
- **Site:** qualquer um lê a consulta; não grava a planilha  
- **Planilha:** Conta de Serviço = Editor (EXE); “qualquer pessoa com o link” = Leitor (site)  
- Aba **Auditoria**: para admins no EXE e na planilha. O site **não** a lê  
- Relatório com CPF completo: **somente login admin**  
- Consulta no celular: CPF **mascarado**  
- Não envie `google-credentials.json` nem a senha do admin

O GitHub **não precisa ficar aberto** para o site funcionar.
