# Changelog — Sinapesc REAP (desktop)

Todas as versões notáveis do programa Windows.

Formato: mais recente primeiro.

---

## [v1.6.5] — 2026-08-18 — Escala compacta + funções restauradas

**Tag:** [`v1.6.5`](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.5)  
**Download:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.5/SinapescREAP-Windows-v1.6.5.zip

### O que entrou
- Escala da UI: fontes legíveis, padding reduzido, conteúdo com largura máxima (não “estica” a 1280px)
- Config.Atalhos como **aba completa**: (1) lote pré-marcado, (2) marcar em massa com busca/substituir, (3) copiar ano
- Presets **Mar → Out / Ano inteiro / Limpar**
- Cadastro em lote visual (linhas Nome + CPF + lixeira)
- Configurações: Gerar QRs, QR Consulta CPF, pasta dos QRs
- Auditoria: exportar CSV
- Modal JS corrigido (botões Salvar/Importar voltaram a funcionar)

---

## [v1.6.4] — 2026-08-18 — UI web pywebview (idêntica ao mockup)

**Tag:** [`v1.6.4`](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.4)  
**Download:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.4/SinapescREAP-Windows-v1.6.4.zip

### O que entrou
- Interface **HTML + CSS** dentro da janela via **pywebview** (WebView2 no Windows)
- Mockup aprovado com fidelidade real: header navy, abas sublinhadas, cartões, pílulas de mês, rodapé limpo
- Ponte `webapp/api.py` reutiliza `sheets/` e `controle/` (login, sócios, REAP, pendências, relatório, backup, auditoria, QRs)
- Tkinter mantido como fallback: `SinapescREAP.exe --tk`
- Correções: nomes CAPS, relatório individual, lista/QR sem login admin, navegação Voltar

---

## [v1.6.2] — 2026-08-18 — UI fiel ao mockup aprovado (Tkinter)

**Tag:** [`v1.6.2`](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.2)  
**Download:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.2/SinapescREAP-Windows-v1.6.2.zip

### O que entrou
- Módulo `ui/widgets.py` (busca com lupa, botões outline/primary, cartões, pills de mês)
- Header: e-mail acima dos botões; abas com sublinhado branco na ativa
- Ordem das abas igual ao mockup (+ Auditoria)
- Cartões: avatar circular, ações com ícones, chevron ▲/▼
- Meses em fila horizontal verde ✓ / vermelho !
- Rodapé: Pronto · Usuário · Conectado

---

## [v1.6.1] — 2026-08-18 — Interface fusionada + rodapé limpo

**Tag:** [`v1.6.1`](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.1)  
**Download:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.1/SinapescREAP-Windows-v1.6.1.zip

### O que entrou
- **UI reorganizada:** header compacto, abas em texto (Pendências · Relatório · Backup · Auditoria · Sócios · Config.Atalhos)
- Botões outline no topo: **Voltar · Lista pública · Configurações · Sair**
- **Voltar** com histórico (não desloga ao voltar)
- Tela Sócios mais limpa: busca + ações no topo, sem segunda fileira de botões coloridos
- Rodapé: usuário, conexão, versão (removido texto “safra”)
- Nova página **Backup** na aba (gerar, abrir pasta, listar recentes)
- Módulo `ui/chrome.py` centraliza shell e navegação

### Inclui tudo da v1.6.0
Pendências, relatório HTML (CPF admin), backup CSV, auditoria na planilha.

---

## [v1.6.0] — 2026-08-18 — Pendências, relatório, backup e auditoria na planilha

**Tag:** [`v1.6.0`](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.6.0)  
**Download direto:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.6.0/SinapescREAP-Windows-v1.6.0.zip  
**Repo:** https://github.com/ANmoLOCK/sinapesc-casanova-reap  
**Consulta:** https://anmolock.github.io/sinapesc-casanova-reap/consulta.html  
**Plano:** [`PLANO_FUNCOES_v16.md`](./PLANO_FUNCOES_v16.md)

### O que entrou
- **Pendências REAP:** lista só quem falta no calendário do ano (padrão mar–out). Marca somente os meses pendentes, em lote, sem apagar o que já está marcado.
- **Calendário compartilhado:** aba **Config** na planilha (`calendario_padrao` / `calendario_2026`). Todos os admins usam a mesma regra.
- **Relatório de conformidade:** HTML com logo Sinapesc, **CPF completo** (somente o admin, pela tela Relatório), grade do ano, carimbo Regular/Pendente. Sem R$. Abrir no navegador → Imprimir → Salvar como PDF. A consulta pública no celular continua com CPF mascarado.
- **Backup CSV local:** cópia das abas Pessoas + Reap em `backups/` ao lado do EXE (ou AppData). Lembrete a cada 7 dias no login admin. Guarda os últimos 12.
- **Auditoria na planilha:** aba **Auditoria**. Cada admin vê o que o outro marcou: “fulano marcou OUT/2026 em Maria”. O site público **não** lê essa aba.

### Organização (código separado)
- Regras em `sinapesc-desktop/controle/`
- Telas em `ui/tela_pendencias.py`, `ui/tela_relatorio.py`, `ui/tela_backup.py`, `ui/tela_auditoria.py`
- Planilha: `sheets/client.py` cria as abas novas na primeira conexão

### Bugs corrigidos nesta leva
- Clique duplo na planilha: `_run_bg` zera o “ocupado” mesmo se o callback falhar (B13)
- Exceção do thread não se perde no `lambda` (Python 3)
- Relatório do admin deixa de mascarar o CPF (B15); site público permanece mascarado
- Auditoria deixa de ser só local (B14)

### O que não mudou
- Consulta pública por CPF
- Cadastro em lote e Config.Atalhos
- Sem pagamento / boleto / valor em R$

---

## [v1.5.1] — 2026-08-17 — Config.Atalhos

**Tag:** [`v1.5.1`](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.1)  
**Download:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.1/SinapescREAP-Windows-v1.5.1.zip  
**Consulta:** https://anmolock.github.io/sinapesc-casanova-reap/consulta.html  
**Sugestões:** [`MELHORIAS.md`](./MELHORIAS.md)

### O que entrou
- Botão **Config.Atalhos** no admin (ao lado de Atualizar)
- **Lote com REAP já marcado** (Mar→Out, um mês ou ano inteiro)
- **Marcar meses em massa** nos sócios existentes (opção de só a busca; não apaga pagos, salvo “substituir”)
- **Copiar REAP** de um ano para outro
- Escritas na planilha em **batch** (`values.batchUpdate` + append), para não estourar cota da API

### O que não mudou
- Site público, QR permanente, lote visual Nome/CPF, tema azul

---

## [v1.5.0] — 2026-08-17 — Lote visual + site no ar + EXE

**Tag:** [`v1.5.0`](https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.0)  
**EXE (download direto):** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/download/v1.5.0/SinapescREAP-Windows-v1.5.0.zip  
**Página da release:** https://github.com/ANmoLOCK/sinapesc-casanova-reap/releases/tag/v1.5.0  
**Repo:** https://github.com/ANmoLOCK/sinapesc-casanova-reap  
**Consulta:** https://anmolock.github.io/sinapesc-casanova-reap/consulta.html

### Download
Actions → [run 32050211734](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/32050211734) → Artifacts → **SinapescREAP-Windows**.

### Melhorias (detalhe)
- **Lote visual:** cada sócio em uma linha com Nome, CPF (máscara) e lixeira; botão + Adicionar linha
- Importar CSV/TXT preenche as linhas (não substitui por caixona de texto)
- Site público no repositório `sinapesc-casanova-reap` (GitHub Pages / `gh-pages`)
- `config.js` com spreadsheetId da planilha leitora
- Parser da aba Pessoas ignora cabeçalho do gviz
- EXE: `normalize_public_base` — aceita URL com `/consulta.html` e grava a raiz
- Configurações: salvar URL do site sem bloquear o QR (B12)
- README da raiz reorganizado (download, atualizações, versões, bugs)

### O que não mudou
- Consulta por CPF no celular sem o PC ligado
- Marcação mês a mês no EXE
- Tema azul, logo Sinapesc, QR permanente em `qr-codes/`

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
