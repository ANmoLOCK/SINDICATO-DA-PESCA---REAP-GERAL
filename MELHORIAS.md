# Melhorias sugeridas — Sinapesc REAP

Lista organizada do que **já existe** e do que vale fazer depois, sem misturar com o código atual.

Última revisão: **v1.5.1** (17/08/2026)

---

## Já no programa (não refazer)

| Recurso | Onde |
|---------|------|
| Cadastro individual e em lote (Nome + CPF + lixeira) | Admin |
| Lote com meses já marcados (mar–out, um mês, ano) | Config.Atalhos |
| Marcar meses em massa nos sócios existentes | Config.Atalhos |
| Copiar REAP de um ano para outro | Config.Atalhos |
| Consulta por CPF no celular (PC desligado) | Site público |
| QR permanente | Configurações / qr-codes/ |
| Planilha Google (Pessoas + Reap) | API |

---

## Próximas melhorias (prioridade)

### 1) Painel de inadimplência (mais útil no dia a dia)
Tela “quem está atrasado neste ano”: nome, meses faltando, botão para marcar em lote só os atrasados.  
A secretaria para de abrir sócio por sócio.

### 2) Recibo / comprovante em PDF
Gerar PDF com logo Sinapesc, nome, CPF mascarado, meses pagos do ano — para imprimir ou mandar no WhatsApp.

### 3) Backup automático da planilha
Uma vez por semana, o EXE salva uma cópia CSV/XLSX na pasta do programa. Se a planilha sumir, o sindicato não perde o histórico.

### 4) Aviso de aniversário de atraso
Lista “não pagam há X meses” + texto pronto de WhatsApp (sem enviar sozinho — só copiar).

### 5) Dois níveis de acesso
- **Secretaria:** cadastra e marca REAP  
- **Consulta na sede:** só busca e vê, sem poder apagar sócio  

Evita acidente na hora do movimento.

### 6) Valor do REAP (opcional, separado do lote)
Tabela “ano → valor mensal” (ex.: 2026 = R$ 15). O cadastro de sócio **não** mistura com preço. Relatório de arrecadação = meses pagos × valor.

### 7) Foto / carteirinha
QR individual + nome para imprimir carteirinha do associado.

### 8) Logs de alteração
“Fulano marcou julho de 2026 em Maria às 14h” — para auditoria da diretoria.

---

## O que **não** fazer agora

- Não voltar a depender de túnel/PC ligado para o QR  
- Não inventar domínio `.com.br` sem comprar o DNS  
- Não gravar a API mês a mês em loop (os atalhos já usam lote)  
- Não colocar R$ no cadastro em lote (confunde com quantidade de pessoas)

---

Quando for implementar, abrir uma versão nova (ex.: **v1.6.0**) e anotar no `CHANGELOG.md`.
