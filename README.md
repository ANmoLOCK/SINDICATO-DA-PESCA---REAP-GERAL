# Sinapesc REAP — Casa Nova

**Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova**

Controle de **REAP** (não é pagamento): a secretaria usa o EXE no Windows; o associado consulta o CPF no celular **sem o notebook ligado**.

| | |
|--|--|
| Repositório | https://github.com/ANmoLOCK/sinapesc-casanova-reap |
| Versão atual | [**v1.6.6**](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.6) |
| Site (consulta) | https://anmolock.github.io/sinapesc-casanova-reap/consulta.html |
| Planilha (leitor) | https://docs.google.com/spreadsheets/d/1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4/edit?usp=sharing |

---

## Download do EXE (v1.6.6)

**Link direto (ZIP):**

https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.6/SinapescREAP-Windows-v1.6.6.zip

Página da release: https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.6

Versão anterior: [v1.6.5](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.5) · [v1.6.4](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.4)

O ZIP traz `SinapescREAP.exe`, `config.json`, `LEIA-ME.txt` e tutoriais. Extraia numa pasta (ex.: `C:\Sinapesc\`) e coloque o `google-credentials.json` junto.

---

## Site público

| Página | URL |
|--------|-----|
| Consulta por CPF (QR da sede) | https://anmolock.github.io/sinapesc-casanova-reap/consulta.html |
| Lista pública | https://anmolock.github.io/sinapesc-casanova-reap/lista.html |

**URL para colar no EXE** (Configurações — sem `/consulta.html`):

```text
https://anmolock.github.io/sinapesc-casanova-reap
```

O site lê só as abas **Pessoas** e **Reap**. CPF no celular fica **mascarado**.

---

## O que há na v1.6.6

- Sócios novos no **topo** (mais recente → mais antigo)
- **Filtro** na toolbar: Mais recente | A–Z · Atualizar · Lote · + Novo sócio
- QR: botão **Imprimir**
- Logo selo SINAPESC no programa e nos relatórios HTML

### Interface web (pywebview)

- Escala compacta (fontes 13–16px, cartões e pílulas juntos — sem “vazio” na tela)
- **Config.Atalhos** completo na aba: lote pré-marcado, marcar em massa, **copiar ano**, presets Mar→Out
- Cadastro em lote visual (Nome | CPF | lixeira)
- Configurações: Gerar QRs, QR Consulta, pasta dos QRs
- Auditoria: exportar CSV

### Interface web (pywebview)
- **HTML + CSS real** dentro da janela (WebView2 no Windows) — avatares circulares, pílulas, abas sublinhadas
- Header: logo, e-mail acima dos botões, **← Voltar · Lista pública · ⚙ Configurações · Sair**
- Abas: **Sócios · Pendências · Relatório · Backup · Auditoria · Config.Atalhos · Lista pública**
- Cartões com avatar, **▦ QR · ✎ Editar · 🗑 Excluir**, chevron ▲/▼
- Meses em pílulas: verde ✓ (regular) · vermelho ! (pendente)
- Rodapé: **Pronto · Usuário · Conectado** | **Sinapesc REAP**
- Tkinter legado ainda disponível: `SinapescREAP.exe --tk`

### v1.6.2 / v1.6.1 / v1.6.0 (mantidos)
- Header compacto: logo, e-mail logado, botões **Voltar · Lista pública · Configurações · Sair**
- Abas da secretaria: **Pendências · Relatório · Backup · Auditoria · Sócios · Config.Atalhos**
- Tela **Sócios** mais limpa (busca + ações no topo, sem fileira extra de botões)
- **Voltar** com histórico — volta à tela anterior sem deslogar
- Rodapé com usuário, conexão e versão

### Funções v1.6.0 (mantidas)

| Aba / botão | Função |
|-------------|--------|
| **Pendências** | Quem falta no calendário do ano (padrão **mar–out**). Marca só o que falta. |
| **Relatório** | HTML com **CPF completo** (só admin). Imprimir → PDF. Sem R$. |
| **Backup** | CSV local das abas Pessoas + Reap (`backups/`). Lembrete a cada 7 dias. |
| **Auditoria** | Histórico na aba **Auditoria** da planilha (todos os admins veem). |
| **Config.Atalhos** | Lote pré-marcado, marcar em massa, copiar ano. |

Na primeira conexão o EXE cria as abas **Auditoria** e **Config**.

Código: `sinapesc-desktop/controle/` (regras) · `sinapesc-desktop/ui/` (telas + `chrome.py`)

---

## Instalação rápida

1. Extraia o ZIP do EXE  
2. Coloque `google-credentials.json` na mesma pasta  
3. Em `config.json`:

```json
"public_site_url": "https://anmolock.github.io/sinapesc-casanova-reap"
```

4. Abra o `.exe` → **Configurações** → **Salvar** → **Testar conexão**  
5. **QR Consulta CPF** → imprimir na sede  
6. Login admin → use as abas da secretaria  

Guia completo: [`TUTORIAL_IMPLEMENTACAO.md`](./TUTORIAL_IMPLEMENTACAO.md)  
API Google: [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md)  
Histórico: [`CHANGELOG.md`](./CHANGELOG.md)

---

## Duas peças

| Peça | Quem usa | PC ligado? |
|------|----------|------------|
| `SinapescREAP.exe` | Secretaria | Sim, na sede |
| Site `consulta.html` | Associado (QR) | Não |

Mesma planilha: EXE grava (Editor); site só lê (Leitor).

---

## Histórico de versões

| Versão | O que entrou | EXE |
|--------|----------------|-----|
| **v1.6.6** | Filtro sócios, imprimir QR, logo selo SINAPESC | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.6/SinapescREAP-Windows-v1.6.6.zip) |
| v1.6.5 | Escala compacta + atalhos completos (lote visual, copiar ano) | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.5/SinapescREAP-Windows-v1.6.5.zip) |
| v1.6.4 | UI web pywebview — idêntica ao mockup (HTML/CSS no EXE) | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.4/SinapescREAP-Windows-v1.6.4.zip) |
| v1.6.2 | UI Tkinter refinada (cartões, meses, abas, busca) | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.2/SinapescREAP-Windows-v1.6.2.zip) |
| v1.6.1 | UI fusionada, Voltar, abas, rodapé limpo | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.1/SinapescREAP-Windows-v1.6.1.zip) |
| v1.6.0 | Pendências, relatório, backup, auditoria na planilha | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.0/SinapescREAP-Windows-v1.6.0.zip) |
| v1.5.1 | Config.Atalhos (lote, massa, copiar ano) | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.1/SinapescREAP-Windows-v1.5.1.zip) |
| v1.5.0 | Lote visual, site Pages, QR permanente | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP-Windows-v1.5.0.zip) |

Versões antigas: [`CHANGELOG.md`](./CHANGELOG.md)

---

## Pastas do repositório

| Pasta | Função |
|-------|--------|
| `sinapesc-desktop/` | Programa Windows (pywebview + Google Sheets) |
| `sinapesc-desktop/web/` | Interface HTML/CSS (mockup aprovado) |
| `sinapesc-desktop/webapp/` | Ponte Python ↔ JavaScript |
| `sinapesc-desktop/controle/` | Pendências, relatório, backup, auditoria |
| `site-publico/` | Site estático (GitHub Pages) |
| `.github/workflows/` | Build EXE + deploy site |

---

## Segurança

- Relatório admin: **CPF completo** · consulta pública: **CPF mascarado**
- Aba **Auditoria**: só no EXE/planilha; o site não lê
- Não compartilhe `google-credentials.json` nem senha do admin
