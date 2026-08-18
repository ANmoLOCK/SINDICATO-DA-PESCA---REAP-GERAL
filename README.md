# Sinapesc REAP — Casa Nova

**Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova**

Controle de **REAP** (não é pagamento): a secretaria usa o EXE no Windows; o associado consulta o CPF no celular **sem o notebook ligado**.

| | |
|--|--|
| Repositório | https://github.com/ANmoLOCK/sinapesc-casanova-reap |
| Versão atual | [**v1.6.2**](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.2) |
| Site (consulta) | https://anmolock.github.io/sinapesc-casanova-reap/consulta.html |
| Planilha (leitor) | https://docs.google.com/spreadsheets/d/1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4/edit?usp=sharing |

---

## Download do EXE (v1.6.2)

**Link direto (ZIP):**

https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.2/SinapescREAP-Windows-v1.6.2.zip

Página da release: https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.2

Versão anterior: [v1.6.1](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.1) · [v1.6.0](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.0)

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

## O que há na v1.6.2

### Interface fiel ao mockup aprovado
- Header: logo, e-mail acima dos botões, **← Voltar · Lista pública · ⚙ Configurações · Sair**
- Abas com sublinhado: **Sócios · Pendências · Relatório · Backup · Auditoria · Config.Atalhos · Lista pública**
- Busca larga com lupa, botões outline e **+ Novo sócio** azul
- Cartões com avatar, **▦ QR · ✎ Editar · 🗑 Excluir**, chevron ▲/▼
- Meses em fila horizontal: verde ✓ (regular) · vermelho ! (pendente)
- Rodapé: **Pronto · Usuário · Conectado** | **Sinapesc REAP**

### v1.6.1 / v1.6.0 (mantidos)
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
| **v1.6.2** | UI fiel ao mockup (cartões, meses, abas, busca) | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.2/SinapescREAP-Windows-v1.6.2.zip) |
| v1.6.1 | UI fusionada, Voltar, abas, rodapé limpo | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.1/SinapescREAP-Windows-v1.6.1.zip) |
| v1.6.0 | Pendências, relatório, backup, auditoria na planilha | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.0/SinapescREAP-Windows-v1.6.0.zip) |
| v1.5.1 | Config.Atalhos (lote, massa, copiar ano) | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.1/SinapescREAP-Windows-v1.5.1.zip) |
| v1.5.0 | Lote visual, site Pages, QR permanente | [ZIP](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP-Windows-v1.5.0.zip) |

Versões antigas: [`CHANGELOG.md`](./CHANGELOG.md)

---

## Pastas do repositório

| Pasta | Função |
|-------|--------|
| `sinapesc-desktop/` | Programa Windows (Tkinter + Sheets) |
| `sinapesc-desktop/controle/` | Pendências, relatório, backup, auditoria |
| `sinapesc-desktop/ui/` | Interface + `chrome.py` (header/abas/rodapé) |
| `site-publico/` | Site estático (GitHub Pages) |
| `.github/workflows/` | Build EXE + deploy site |

---

## Segurança

- Relatório admin: **CPF completo** · consulta pública: **CPF mascarado**
- Aba **Auditoria**: só no EXE/planilha; o site não lê
- Não compartilhe `google-credentials.json` nem senha do admin
