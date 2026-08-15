# Como publicar o site (GitHub Pages)

## Situação atual

O código do site já está pronto na pasta `site-publico/` com a planilha configurada:

- **ID:** `1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4`
- **Planilha (leitor):** https://docs.google.com/spreadsheets/d/1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4/edit?usp=sharing
- **Workflow:** `.github/workflows/deploy-site.yml` (já no `main`)

O deploy automático **falhou** porque o repositório está **PRIVADO**.  
No plano gratuito do GitHub, **Pages só funciona em repositório público**.

---

## O que você precisa fazer (2 cliques — só você pode)

### 1) Deixar o repositório público

1. Abra: https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/settings  
2. Role até **Danger Zone**  
3. Clique **Change repository visibility** → **Make public** → confirme  

(A planilha continua protegida no Google; o site só lê o que já está em modo leitor.)

### 2) Ligar o Pages

1. Ainda em Settings → **Pages**  
2. Em **Source**, escolha **GitHub Actions**  
3. Abra: https://github.com/ANmoLOCK/SINDICATO-DA-PESCA---REAP-GERAL/actions/workflows/deploy-site.yml  
4. Clique **Run workflow** → branch `main` → **Run workflow**  

Quando ficar **verde**, o site estará em:

```text
https://anmolock.github.io/SINDICATO-DA-PESCA---REAP-GERAL/consulta.html
```

### 3) Colar no EXE

Em **Configurações** do programa:

```text
https://anmolock.github.io/SINDICATO-DA-PESCA---REAP-GERAL
```

Depois: **Gerar QRs** → **QR Consulta CPF** → imprimir.

---

## Alternativa sem tornar o repo público

Use **Netlify Drop** (arrastar pasta):

1. Baixe a pasta `site-publico` do GitHub  
2. Abra https://app.netlify.com/drop  
3. Arraste a pasta  
4. Use o link que o Netlify der no EXE  

---

## Já configurado por mim no código

- `site-publico/config.js` com o ID da planilha  
- Correção do leitor da aba Pessoas  
- Workflow com ativação automática do Pages (quando o repo for público)  
- Planilha testada: leitura pública OK  
