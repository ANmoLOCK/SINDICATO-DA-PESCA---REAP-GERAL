# Site público Sinapesc (GitHub Pages)

Consulta online **sem o notebook ligado**.

## Link publicado

Depois do deploy automático:

- Site: https://anmolock.github.io/sinapesc-casanova-reap/consulta.html
- Consulta CPF: https://anmolock.github.io/SINDICATO-DA-PESCA---REAP-GERAL/consulta.html
- Lista: https://anmolock.github.io/SINDICATO-DA-PESCA---REAP-GERAL/lista.html

Planilha (modo leitor):  
https://docs.google.com/spreadsheets/d/1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4/edit?usp=sharing

## Deploy automático

O workflow `.github/workflows/deploy-site.yml` publica esta pasta no GitHub Pages a cada push na `main`.

Se for a primeira vez no repositório, o passo `configure-pages` com `enablement: true` ativa o Pages sozinho.

## No EXE

Em **Configurações**, cole:

```text
https://anmolock.github.io/sinapesc-casanova-reap/consulta.html
```

Depois: **Gerar QRs do site** → **QR Consulta CPF** → imprimir.
