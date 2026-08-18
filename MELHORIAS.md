# Melhorias sugeridas — Sinapesc REAP

Última revisão: **v1.6.0** (18/08/2026)

---

## Já no programa (não refazer)

| Recurso | Onde | Desde |
|---------|------|-------|
| Cadastro individual e em lote (Nome + CPF + lixeira) | Admin | v1.5.0 |
| Lote com meses já marcados / marcar em massa / copiar ano | Config.Atalhos | v1.5.1 |
| Painel Pendências REAP (calendário mar–out) | Admin → Pendências | v1.6.0 |
| Relatório HTML (CPF completo só no admin) | Admin → Relatório | v1.6.0 |
| Backup CSV local semanal | Admin → Backup | v1.6.0 |
| Auditoria na planilha (todos os admins) | Aba Auditoria + tela | v1.6.0 |
| Consulta por CPF no celular (PC desligado) | Site público | v1.4.0 |
| QR permanente | Configurações / qr-codes/ | v1.3.0 |

---

## Próximas (ainda não fazer)

### 1) Dois níveis de acesso
Secretaria (cadastra/marca) vs consulta na sede (só vê). Evita exclusão acidental.

### 2) Carteirinha do associado
QR individual + nome para imprimir. Sem foto obrigatória nesta etapa.

### 3) Texto pronto de WhatsApp (só copiar)
Lista “faltam X meses” + mensagem para a secretaria colar. O programa **não envia** sozinho.

### 4) Valor do REAP (opcional, separado)
Tabela ano → valor, só para relatório interno. **Não** misturar R$ no cadastro em lote.

---

## O que **não** fazer

- Não voltar a depender de túnel/PC ligado para o QR
- Não inventar domínio `.com.br` sem comprar o DNS
- Não gravar a API mês a mês em loop (atalhos e pendências já usam lote)
- Não colocar R$ no cadastro em lote
- Não mascarar o CPF no Relatório do admin (pedido da secretaria)
- Não mostrar CPF completo no site público

Quando for a próxima leva, abrir **v1.7.0** e anotar no `CHANGELOG.md`.
