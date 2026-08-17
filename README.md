# Sinapesc — Sindicato Dos Aquicultores E Pescadores De Casa Nova

Programa de contribuição **REAP**: Windows `.exe` (secretaria) + site público gratuito (consulta por CPF no celular).

Repositório: [ANmoLOCK/sinapesc-casanova-reap](https://github.com/ANmoLOCK/sinapesc-casanova-reap)

---

## Download (v1.5.0)

| Item | Link |
|------|------|
| **EXE Windows** | [Baixar `SinapescREAP-Windows` (v1.5.0)](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/32050211734) |
| **Consulta pública (CPF)** | https://anmolock.github.io/sinapesc-casanova-reap/consulta.html |
| **Lista pública** | https://anmolock.github.io/sinapesc-casanova-reap/lista.html |
| Tutorial | [`TUTORIAL_IMPLEMENTACAO.md`](./TUTORIAL_IMPLEMENTACAO.md) |
| API Google (planilha) | [`sinapesc-desktop/COMO_INTEGRAR_API.md`](./sinapesc-desktop/COMO_INTEGRAR_API.md) |
| Histórico de versões | [`CHANGELOG.md`](./CHANGELOG.md) |

> No GitHub: [Actions run 32050211734](https://github.com/ANmoLOCK/sinapesc-casanova-reap/actions/runs/32050211734) → **Artifacts** → `SinapescREAP-Windows`.

**URL para colar no EXE** (Configurações → URL do site público), **sem** `/consulta.html`:

```text
https://anmolock.github.io/sinapesc-casanova-reap
```

---

## Comece por aqui

1. Baixe o ZIP do EXE e extraia  
2. Coloque `google-credentials.json` + `config.json` na mesma pasta  
3. No EXE: **Configurações** → cole a URL acima → **Salvar** → **QR Consulta CPF**  
4. Imprima o QR na sede  

Detalhes: [`TUTORIAL_IMPLEMENTACAO.md`](./TUTORIAL_IMPLEMENTACAO.md)

---

## O que o sistema faz

- Cadastro de sócios (um a um e **em lote**, com Nome + CPF lado a lado)  
- Marcação mês a mês do REAP  
- Site público: associado digita o CPF **sem o notebook ligado**  
- QR permanente apontando para o site  
- Interface azul com logo Sinapesc  

---

## Melhorias desta versão (v1.5.0)

- Cadastro em lote com linhas **Nome | CPF | lixeira** (mais fácil de entender)  
- Site público no ar: `anmolock.github.io/sinapesc-casanova-reap`  
- EXE aceita a URL do site mesmo se colar `/consulta.html`  
- Planilha leitora já configurada no `site-publico/config.js`  
- GitHub Pages pela branch `gh-pages`  

Versões anteriores (v1.0–v1.4): site estático, QR estável, UI azul, accordion, scroll — ver [`CHANGELOG.md`](./CHANGELOG.md).

---

## Versões e EXE

| Versão | Destaque |
|--------|----------|
| **v1.5.0** | Lote visual · URL nova do site · QR mais simples de gerar |
| v1.4.0 | Site público + UI azul + logo/peixe |
| v1.3.0 | QR estável · consulta CPF |
| v1.2.0 | Casa Nova · lote · link público |
| v1.1.0 | Scroll · accordion |
| v1.0.0 | Primeiro EXE + Google Sheets |

---

## Pastas do projeto

| Pasta | Função |
|-------|--------|
| `sinapesc-desktop/` | Programa Windows (código do EXE) |
| `site-publico/` | Site de consulta (GitHub Pages) |
| `.github/workflows/` | Build do EXE + publish do site |
