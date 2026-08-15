# Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova

Controle de contribuição **REAP** para notebook/computador (Windows `.exe`), integrado à **Google Planilha**, com **site público gratuito** (consulta por CPF sem o PC ligado).

---

## Download rápido (última versão)

| Item | Link |
|------|------|
| **EXE v1.4.0 (recomendado)** | Após o build Actions: artefato `SinapescREAP-Windows` |
| Release | [v1.4.0](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.4.0) (quando publicada) |
| Código-fonte EXE | [`sinapesc-desktop/`](./sinapesc-desktop/) |
| Site público (Opção A) | [`site-publico/`](./site-publico/) |
| Como integrar a API Google | [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md) |
| Histórico | [`CHANGELOG.md`](./CHANGELOG.md) |

> Actions → **Artifacts** → **SinapescREAP-Windows** → ZIP com `SinapescREAP.exe`.

---

## O que o programa faz

- Cadastro de sócios (individual e **em lote**)
- Marcação mês a mês do REAP (clique no nome para abrir)
- **Site público gratuito** (`site-publico/`) — consulta por CPF online **sem notebook ligado**
- QR Code **permanente** apontando para o site (consulta, lista e individual)
- Interface premium azul com logo Sinapesc e gráfica de peixe
- Dados na Google Planilha (abas `Pessoas` e `Reap`)

---

## Site público (Opção A) — passo a passo

1. Na planilha: **Compartilhar** → **Qualquer pessoa com o link** → **Leitor**
2. Edite `site-publico/config.js` e cole o `spreadsheetId`
3. Publique a pasta `site-publico/` (GitHub Pages já tem workflow `deploy-site.yml`)
4. No EXE → **Configurações** → cole a **URL do site público** → **Gerar QRs do site**
5. Imprima o **QR Consulta CPF** na sede

Detalhes: [`site-publico/README.md`](./site-publico/README.md)

---

## Versões (tags)

| Versão | Tag | O que entrou |
|--------|-----|--------------|
| **v1.4.0** | `v1.4.0` | Site público estático · UI azul + logo + peixe · QR fixo no site |
| **v1.3.0** | [`v1.3.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.3.0) | QR estável · consulta CPF · UI premium |
| **v1.2.0** | [`v1.2.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.2.0) | Casa Nova · link público · lote |
| **v1.1.0** | [`v1.1.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.1.0) | Scroll · accordion · QR online |
| **v1.0.0** | [`v1.0.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.0.0) | 1º EXE · Sheets didático |

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
| B10 | QR/túnel mudavam a cada geração | v1.3.0 | Resolvido |
| B11 | Consulta pública dependia do notebook/túnel | v1.4.0 | Resolvido (site estático) |

---

## Instalação rápida

1. Baixe o ZIP do artefato Windows (Actions)
2. Extraia · coloque `google-credentials.json` + `config.json`
3. Compartilhe a planilha com o e-mail da Conta de Serviço (**Editor**)
4. Publique o site (`site-publico/`) e configure a URL no EXE
5. Gere o **QR Consulta CPF** e imprima

Detalhes: [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md)
