# Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova

Controle de contribuição **REAP** para notebook/computador (Windows `.exe`), integrado à **Google Planilha**.

---

## Download rápido (última versão)

| Item | Link |
|------|------|
| **EXE v1.2.0 (recomendado)** | [Baixar artefato `SinapescREAP-Windows`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31858767536) |
| Código-fonte atual | [`sinapesc-desktop/`](./sinapesc-desktop/) |
| Como integrar a API Google | [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md) |
| Histórico completo | [`CHANGELOG.md`](./CHANGELOG.md) |
| Pull Request | [#1](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/pull/1) |

> No GitHub Actions: abra o run → **Artifacts** → **SinapescREAP-Windows** → baixe o ZIP com `SinapescREAP.exe`.

---

## O que o programa faz

- Cadastro de sócios (individual e **em lote**)
- Marcação mês a mês do REAP (clique no nome para abrir)
- Lista pública com CPF mascarado
- QR Code imprimível da lista / comprovante individual
- Botão **Criar link público** (internet/4G via Cloudflare Tunnel)
- Dados na Google Planilha (abas `Pessoas` e `Reap`)

---

## Versões (tags) — links diretos

| Versão | Tag | O que entrou | Bugs resolvidos | EXE |
|--------|-----|--------------|-----------------|-----|
| **v1.2.0** | [`v1.2.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.2.0) | UI premium · nome Casa Nova · link público 1 clique · cadastro em lote | Texto redundante `0/12` · túnel manual confuso | [Actions #31858767536](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31858767536) |
| **v1.1.0** | [`v1.1.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.1.0) | Scroll corrigido · lista accordion · QR + página online | Scroll quebrado · tela poluída com todos os meses abertos | [Actions #31857220864](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31857220864) |
| **v1.0.0** | [`v1.0.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.0.0) | 1º EXE Windows · Google Sheets didático · config ao lado do exe | Build Windows falhava (ícone PNG) · API difícil de configurar | [Actions #31854798304](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31854798304) |

Tags no Git:

```text
git fetch --tags
git checkout v1.2.0   # última
git checkout v1.1.0
git checkout v1.0.0   # primeira estável
```

---

## Bugs registrados e status

| ID | Bug | Versão que resolveu | Status |
|----|-----|---------------------|--------|
| B01 | Scroll da lista não funcionava / “vazava” a roda do mouse | v1.1.0 | Resolvido |
| B02 | Tela cheia demais: todos os anos/meses abertos ao mesmo tempo | v1.1.0 | Resolvido |
| B03 | Build do `.exe` no Windows falhava (ícone `.png` sem Pillow) | v1.0.0 | Resolvido |
| B04 | Integração Google Sheets pouco clara para o usuário final | v1.0.0 | Resolvido (guia + import JSON) |
| B05 | Texto redundante `0/12 pagos` na lista | v1.2.0 | Resolvido |
| B06 | QR só na Wi‑Fi local; fora da rede não abria (4G) | v1.2.0 | Resolvido (botão Criar link público) |
| B07 | Cadastro um a um inviável para muitos sócios | v1.2.0 | Resolvido (lote/CSV) |

---

## Melhorias por versão (resumo)

### v1.0.0 — primeira versão estável
- App desktop no lugar do web Next.js
- Cliente Google Sheets comentado passo a passo
- `google-credentials.json` + `config.json` ao lado do `.exe`
- Login admin local · lista pública · marcar meses

### v1.1.0
- Scroll estável
- Clique no nome → abre anos/REAP (menu rápido)
- Servidor HTTP embutido + QR imprimível

### v1.2.0 — atual
- Marca **Sinapesc Casa Nova**
- Visual mais premium
- **Criar link público** (Cloudflare automático)
- **Cadastro em lote**
- Remoção do contador redundante

---

## Instalação rápida no notebook

1. Baixe o ZIP da [v1.2.0](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31858767536)
2. Extraia numa pasta (ex.: `C:\Sinapesc\`)
3. Coloque na mesma pasta:
   - `google-credentials.json` (Conta de Serviço Google)
   - `config.json` com o ID da planilha (modelo vem no ZIP)
4. Compartilhe a planilha com o e-mail da Conta de Serviço (**Editor**)
5. Execute `SinapescREAP.exe`

Detalhes: [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md)

---

## Estrutura do repositório

```text
├── README.md                 ← você está aqui (visão geral + versões)
├── CHANGELOG.md              ← histórico detalhado
├── sinapesc-desktop/         ← código do programa .exe
│   ├── COMO_INTEGRAR_API.md
│   ├── main.py
│   ├── sheets/               ← API Google Sheets (didática)
│   └── ui/                   ← interface
└── .github/workflows/        ← gera o EXE no Windows automaticamente
```

---

## Próxima ideia de melhoria

**Painel de inadimplência + cobrança rápida** — listar sócios com REAP em atraso, marcar pagos em lote e gerar mensagem pronta (WhatsApp/impressão).

---

## Licença / uso

Sistema interno do Sinapesc — Casa Nova. Uso operacional do sindicato.
