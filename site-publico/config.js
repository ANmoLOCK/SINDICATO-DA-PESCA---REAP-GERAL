/**
 * Configuração do site público Sinapesc.
 * Preencha após publicar/compartilhar a planilha no Google.
 *
 * Como obter:
 * 1) Planilha → Compartilhar → "Qualquer pessoa com o link" (Leitor)
 *    OU Arquivo → Compartilhar → Publicar na Web (CSV das abas Pessoas e Reap)
 * 2) Cole o ID da planilha (parte entre /d/ e /edit na URL)
 * 3) Faça deploy desta pasta (GitHub Pages / Cloudflare Pages / Netlify)
 */
window.SINAPESC_CONFIG = {
  orgShort: "Sinapesc",
  orgFull: "Sindicato Dos Aquicultores E Pescadores De Casa Nova",
  // ID da planilha Google (obrigatório)
  spreadsheetId: "1ydaWGF53VTkXyIyhf5XKJek5PKMDZO1_cD3CrRePft4",
  // Opcional: URLs CSV publicadas (se preencher, têm prioridade sobre spreadsheetId)
  pessoasCsvUrl: "",
  reapCsvUrl: "",
};
