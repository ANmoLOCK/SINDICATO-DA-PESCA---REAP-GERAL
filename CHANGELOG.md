# Changelog — Sinapesc REAP (desktop)

Todas as versões notáveis do programa Windows.

Formato: mais recente primeiro.

---

## [v1.5.0] — 2026-08-17 — Lote visual + site no ar

**Tag:** `v1.5.0`  
**EXE:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/32050211734  
**Repo:** https://github.com/ANmoLOCK/sinapesc-casanova-reap  
**Site:** https://anmolock.github.io/sinapesc-casanova-reap/consulta.html

### Melhorias
- Cadastro em lote com campos lado a lado: **Nome**, **CPF** e **lixeira**
- Botão **+ Adicionar linha**; importar CSV continua preenchendo as linhas
- URL pública atualizada para o repositório `sinapesc-casanova-reap`
- EXE normaliza a URL do site (aceita colar com `/consulta.html`)
- Salvamento da URL do site sem travar o QR
- Planilha em modo leitor já no `config.js`

### O que não mudou
- Consulta por CPF no celular (sem PC ligado)
- Marcação mês a mês no EXE
- Cores azuis, logo e QR permanente

---

## [v1.4.0] — 2026-08-15 — Site público gratuito + UI azul Sinapesc

**Tag:** `v1.4.0`  
**EXE:** https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31863086521  
**Tutorial:** [`TUTORIAL_IMPLEMENTACAO.md`](./TUTORIAL_IMPLEMENTACAO.md)

### Melhorias
- **Opção A:** pasta `site-publico/` (consulta/lista/pessoa) lendo a planilha sem o notebook ligado
- Deploy GitHub Pages via `.github/workflows/deploy-site.yml`
- EXE: tema premium **azul oceano**, logo Sinapesc e gráfica de peixe
- QRs permanentes apontam para `public_site_url` (URL fixa do site)
- Configurações: campo **URL do site público** + gerar QRs do site
- Poster do QR com cores institucionais azuis + dourado
- Tutorial passo a passo de implementação (`TUTORIAL_IMPLEMENTACAO.md`)

### Bugs / ajustes
- Consulta pública deixa de depender de túnel/PC ligado (B11)
- Salvamento de configurações alinhado ao fluxo do site (sem campos órfãos do túnel)

---

## [v1.3.0] — 2026-08-15 — QR estável + consulta CPF + UI premium

**Tag:** [`v1.3.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.3.0)

### Melhorias
- UI pública/desktop mais premium
- Página **/consulta** — associado digita CPF e vê só o próprio REAP
- QR com padrão visual único (selo Sinapesc + moldura)
- Cofre `qr-codes/` — QRs permanentes (consulta, lista, individual)
- Link público **reutilizado** (não gera URL nova à toa)
- Túnel pode permanecer ativo ao fechar o app

### Bugs / ajustes
- Removido texto `X/12 pagos` das páginas do QR
- Removida frase “CPF parcialmente oculto” da lista pública online
- QR individual/`lista` não mudam a cada geração enquanto o link estiver válido

---


## [v1.2.0] — 2026-08-15 — Casa Nova + link público + lote

**Tag:** [`v1.2.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.2.0)  
**Commit:** `0372e20`  
**EXE:** https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31858767536

### Melhorias
- Nome oficial: **Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova**
- Interface visual mais premium (faixa dourada, tipografia, botões)
- Botão **Criar link público** (Cloudflare Tunnel automático; preenche a URL)
- **Cadastro em lote** (colar linhas ou importar CSV `Nome;CPF`)
- Botão de link público também no diálogo do QR

### Bugs resolvidos
- Removido texto redundante `0/12 pagos` na lista
- QR inacessível fora da Wi‑Fi (agora há link https com 1 clique)
- Cadastro em massa inviável (agora há lote)

---

## [v1.1.0] — 2026-08-15 — Scroll, accordion e QR online

**Tag:** [`v1.1.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.1.0)  
**Commit:** `6e1035a`  
**EXE:** https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31857220864

### Melhorias
- Lista compacta: clique no nome abre anos/REAP
- QR da lista pública e comprovante individual (PNG imprimível)
- Página web embutida (porta 8765) com atualização automática

### Bugs resolvidos
- Scroll quebrado / mousewheel inconsistente (B01)
- Interface poluída com todos os meses sempre visíveis (B02)

---

## [v1.0.0] — 2026-08-15 — Primeira versão estável (.exe)

**Tag:** [`v1.0.0`](https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/releases/tag/v1.0.0)  
**Commit:** `3cad999`  
**EXE:** https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/runs/31854798304

### Melhorias
- Reformulação do app web Next.js em programa desktop
- Integração Google Sheets didática (`sheets/client.py` + guia)
- Configuração por arquivos ao lado do `.exe`
- CI GitHub Actions gerando artefato Windows

### Bugs resolvidos
- Build Windows falhava por ícone PNG sem conversão ICO/Pillow (B03)
- Falta de fluxo claro para API Google (B04 — guia + import JSON)

---

## Origem (antes das tags)

- App web original (ZIP Next.js) → base da lógica Pessoas/Reap
- Branch de desenvolvimento: `cursor/sinapesc-desktop-exe-46d6`
- PR: https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/pull/1
