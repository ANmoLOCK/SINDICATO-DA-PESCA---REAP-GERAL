# Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova

Controle de contribuição **REAP** para notebook/computador (Windows `.exe`), integrado à **Google Planilha**.

---

## Download rápido (última versão)

| Item | Link |
|------|------|
| **EXE v1.3.0 (recomendado)** | [Baixar artefato `SinapescREAP-Windows`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31860049095) |
| Release | [v1.3.0](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.3.0) |
| Código-fonte | [`sinapesc-desktop/`](./sinapesc-desktop/) |
| Como integrar a API Google | [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md) |
| Histórico completo | [`CHANGELOG.md`](./CHANGELOG.md) |

> Actions → **Artifacts** → **SinapescREAP-Windows** → ZIP com `SinapescREAP.exe`.

---

## O que o programa faz

- Cadastro de sócios (individual e **em lote**)
- Marcação mês a mês do REAP (clique no nome para abrir)
- **Consulta por CPF** no celular (`/consulta`) — sócio vê só o próprio REAP
- QR Code **permanente** (consulta, lista e individual) com padrão visual único
- Link público estável (reutiliza a mesma URL; não troca QR à toa)
- Dados na Google Planilha (abas `Pessoas` e `Reap`)

---

## Versões (tags) — links diretos

| Versão | Tag | O que entrou | Bugs resolvidos | EXE |
|--------|-----|--------------|-----------------|-----|
| **v1.3.0** | [`v1.3.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.3.0) | QR estável · consulta CPF · UI premium · cofre `qr-codes/` | `X/12 pagos` no QR · frase CPF oculto · QR mudava sempre | [Actions](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31860049095) |
| **v1.2.0** | [`v1.2.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.2.0) | Casa Nova · link público · lote | `0/12` na lista desktop · túnel manual | [Actions](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31858767536) |
| **v1.1.0** | [`v1.1.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.1.0) | Scroll · accordion · QR online | Scroll quebrado · tela poluída | [Actions](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31857220864) |
| **v1.0.0** | [`v1.0.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.0.0) | 1º EXE · Sheets didático | Build ícone PNG · API confusa | [Actions](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31854798304) |

```text
git fetch --tags
git checkout v1.3.0   # última
```

---

## Bugs registrados e status

| ID | Bug | Versão | Status |
|----|-----|--------|--------|
| B01 | Scroll quebrado | v1.1.0 | Resolvido |
| B02 | Todos os meses sempre abertos | v1.1.0 | Resolvido |
| B03 | Build Windows (ícone PNG) | v1.0.0 | Resolvido |
| B04 | API Google pouco clara | v1.0.0 | Resolvido |
| B05 | Texto `0/12 pagos` na lista desktop | v1.2.0 | Resolvido |
| B06 | QR só na Wi‑Fi | v1.2.0 | Resolvido |
| B07 | Cadastro um a um inviável | v1.2.0 | Resolvido |
| B08 | Texto `X/12 pagos` nas páginas do QR online | v1.3.0 | Resolvido |
| B09 | Frase “CPF parcialmente oculto” no QR/lista online | v1.3.0 | Resolvido |
| B10 | QR/túnel mudavam a cada geração (precisava reimprimir) | v1.3.0 | Resolvido |

---

## Melhorias por versão (resumo)

### v1.3.0 — atual
- Consulta por CPF online
- QR permanente com padrão Sinapesc + pasta `qr-codes/`
- Link público reutilizado (só renova se você pedir ou se o antigo morrer)
- UI mais premium

### v1.2.0
- Marca Casa Nova · cadastro em lote · link público 1 clique

### v1.1.0
- Scroll · accordion · QR online

### v1.0.0
- Primeiro EXE estável + Google Sheets

---

## Instalação rápida

1. Baixe o ZIP da [v1.3.0](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31860049095)
2. Extraia · coloque `google-credentials.json` + `config.json`
3. Compartilhe a planilha com o e-mail da Conta de Serviço (**Editor**)
4. Abra o `.exe` → **Ativar link estável** → **QR Consulta CPF** → imprima

Detalhes: [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md)

---

## Próxima ideia

**Painel de inadimplência + cobrança rápida** (atrasados do ano, marcar em lote, mensagem WhatsApp pronta).
