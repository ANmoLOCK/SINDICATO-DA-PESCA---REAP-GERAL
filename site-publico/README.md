# Site público Sinapesc (Opção A — gratuito e estável)

Consulta online **sem depender do notebook ligado**.

## O que é

Páginas estáticas que leem a Google Planilha publicada/compartilhada:

- `consulta.html` — associado digita o CPF
- `lista.html` — lista pública
- `pessoa.html?id=...` — comprovante individual (QR do sócio)

## Como colocar no ar (grátis)

### 1) Liberar a planilha
Na Google Planilha: **Compartilhar** → **Qualquer pessoa com o link** → **Leitor**.

### 2) Configurar
Edite `config.js` e cole o ID da planilha:

```js
spreadsheetId: "COLE_O_ID_AQUI",
```

### 3) Publicar o site
Opções gratuitas:

**GitHub Pages (já preparado neste repo)**  
Pasta `site-publico/` + workflow `.github/workflows/deploy-site.yml`  
URL típica: `https://SEU_USUARIO.github.io/SINDICATO-DA-PESCA---REAP-GERAL/`

**Cloudflare Pages / Netlify**  
Envie a pasta `site-publico` como projeto estático.

### 4) No programa EXE
Em **Configurações**, preencha **URL do site público** com o endereço publicado.  
Os QRs passam a apontar para esse link **fixo** (não muda).

## QR da sede (recomendado)

Imprima o QR de:

```text
https://SEU-SITE/consulta.html
```
