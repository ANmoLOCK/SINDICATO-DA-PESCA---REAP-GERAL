/* Sinapesc REAP — UI web (pywebview) */

(function () {
  "use strict";

  const TABS = [
    { id: "socies", label: "Sócios", screen: "admin" },
    { id: "pendencias", label: "Pendências", screen: "pendencias" },
    { id: "relatorio", label: "Relatório", screen: "relatorio" },
    { id: "backup", label: "Backup", screen: "backup" },
    { id: "auditoria", label: "Auditoria", screen: "auditoria" },
    { id: "atalhos", label: "Config.Atalhos", screen: "atalhos" },
    { id: "lista", label: "Lista pública", screen: "lista" },
  ];

  const state = {
    bootstrap: null,
    screen: "home",
    navHistory: [],
    loggedIn: false,
    adminUser: "",
    pessoas: [],
    expanded: new Set(),
    search: "",
    pendencias: null,
    auditoria: [],
    busy: false,
    connLabel: "",
  };

  const $ = (sel) => document.querySelector(sel);
  const content = $("#content");
  const tabBar = $("#tab-bar");
  const tabInner = $("#tab-inner");
  const headerActions = $("#header-actions");
  const headerEmail = $("#header-email");
  const modalRoot = $("#modal-root");

  window.AppEvents = {
    _handlers: {},
    on(event, fn) {
      (this._handlers[event] = this._handlers[event] || []).push(fn);
    },
    dispatch(event, payload) {
      (this._handlers[event] || []).forEach((fn) => {
        try { fn(payload); } catch (e) { console.error(e); }
      });
    },
  };

  function api(method, ...args) {
    if (!window.pywebview || !window.pywebview.api) {
      return Promise.reject(new Error("API Python indisponível"));
    }
    return window.pywebview.api[method](...args);
  }

  function toast(msg, ms = 3200) {
    const el = document.createElement("div");
    el.className = "toast";
    el.textContent = msg;
    $("#toast-root").appendChild(el);
    setTimeout(() => el.remove(), ms);
  }

  function setStatus(msg) {
    $("#status-text").textContent = msg || "Pronto.";
  }

  function setFooter() {
    $("#footer-user").textContent = state.loggedIn ? state.adminUser : "";
    document.querySelector(".footer-conn-sep").style.display = state.connLabel ? "" : "none";
    $("#footer-conn").textContent = state.connLabel;
  }

  function showModal(html, className = "") {
    return new Promise((resolve) => {
      const backdrop = document.createElement("div");
      backdrop.className = "modal-backdrop";
      backdrop.innerHTML = `<div class="modal ${className}">${html}</div>`;
      backdrop.addEventListener("click", (e) => {
        if (e.target === backdrop) close(false);
      });
      modalRoot.appendChild(backdrop);

      function close(result) {
        backdrop.remove();
        resolve(result);
      }

      backdrop.querySelectorAll("[data-modal-close]").forEach((btn) => {
        btn.addEventListener("click", () => close(btn.dataset.modalClose === "ok" ? true : false));
      });

      backdrop._close = close;
      return backdrop;
    });
  }

  function confirmModal(title, text) {
    return showModal(`
      <div class="modal-head">${esc(title)}</div>
      <div class="modal-body"><p style="margin:0;white-space:pre-wrap">${esc(text)}</p></div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
        <button type="button" class="btn btn-primary" data-modal-close="ok">Confirmar</button>
      </div>
    `);
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function navigate(screen, { push = true, tab = null } = {}) {
    if (push && state.screen && state.screen !== screen) {
      state.navHistory.push(state.screen);
    }
    state.screen = screen;
    renderTabs(tab);
    renderHeader();
    renderScreen();
  }

  function goBack() {
    const prev = state.navHistory.pop();
    navigate(prev || (state.loggedIn ? "admin" : "home"), { push: false });
  }

  function renderTabs(activeTab) {
    const secretaria = state.loggedIn && !["home", "login", "settings"].includes(state.screen);
    tabBar.hidden = !secretaria;
    if (!secretaria) return;

    const tabId = activeTab || tabForScreen(state.screen) || "socies";
    tabInner.innerHTML = TABS.map((t) => `
      <div class="tab-cell ${t.id === tabId ? "active" : ""}" data-tab="${t.id}">
        <div class="tab-label">${esc(t.label)}</div>
        <div class="tab-underline"></div>
      </div>
    `).join("");

    tabInner.querySelectorAll(".tab-cell").forEach((cell) => {
      cell.addEventListener("click", () => {
        const id = cell.dataset.tab;
        if (id === "atalhos") {
          openAtalhosModal();
          return;
        }
        const tab = TABS.find((x) => x.id === id);
        if (tab) navigate(tab.screen, { tab: id });
      });
    });
  }

  function tabForScreen(screen) {
    const map = {
      admin: "socies",
      pendencias: "pendencias",
      relatorio: "relatorio",
      backup: "backup",
      auditoria: "auditoria",
      lista: "lista",
    };
    return map[screen] || null;
  }

  function renderHeader() {
    headerEmail.textContent = state.loggedIn ? state.adminUser : "";
    headerActions.innerHTML = "";

    const mkBtn = (label, cls, fn) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = `btn btn-sm ${cls}`;
      b.textContent = label;
      b.addEventListener("click", fn);
      return b;
    };

    if (state.screen === "home") {
      headerActions.appendChild(mkBtn("⚙ Configurações", "btn-outline", () => navigate("settings")));
      return;
    }

    if (state.loggedIn) {
      if (state.navHistory.length) {
        headerActions.appendChild(mkBtn("← Voltar", "btn-outline", goBack));
      }
      headerActions.appendChild(mkBtn("Lista pública", "btn-outline", () => navigate("lista", { tab: "lista" })));
      headerActions.appendChild(mkBtn("⚙ Configurações", "btn-outline", () => navigate("settings")));
      headerActions.appendChild(mkBtn("Sair", "btn-outline", doLogout));
      return;
    }

    headerActions.appendChild(mkBtn("← Voltar", "btn-outline", goBack));
    headerActions.appendChild(mkBtn("⚙ Configurações", "btn-outline", () => navigate("settings")));
  }

  async function doLogout() {
    await api("logout");
    state.loggedIn = false;
    state.adminUser = "";
    state.navHistory = [];
    state.expanded.clear();
    state.connLabel = "";
    setFooter();
    navigate("home", { push: false });
  }

  function renderScreen() {
    const fns = {
      home: renderHome,
      login: renderLogin,
      settings: renderSettings,
      admin: renderAdmin,
      pendencias: renderPendencias,
      relatorio: renderRelatorio,
      backup: renderBackup,
      auditoria: renderAuditoria,
      lista: renderLista,
    };
    (fns[state.screen] || renderHome)();
  }

  function renderHome() {
    content.innerHTML = `
      <div class="hero">
        <div class="hero-title">${esc(state.bootstrap?.org_short || "Sinapesc")}</div>
        <div class="hero-sub">${esc(state.bootstrap?.org_full || "")}</div>
        <div class="hero-tag">Controle REAP · consulta online · QR permanente</div>
      </div>
      <div class="home-cards">
        <div class="home-card">
          <h3>Secretaria</h3>
          <p>Cadastre sócios, marque REAPs e importe lotes na planilha Google.</p>
          <button type="button" class="btn btn-primary" id="go-login">Entrar como administrador</button>
        </div>
        <div class="home-card">
          <h3>Consulta &amp; QR</h3>
          <p>Site público online (CPF) e QRs permanentes para imprimir na sede.</p>
          <button type="button" class="btn btn-primary" id="go-lista">Abrir lista e QRs</button>
        </div>
      </div>
      <div class="tip-box">Site gratuito: compartilhe a planilha como Leitor, publique site-publico/, cole a URL em Configurações e gere o QR Consulta.</div>
    `;
    $("#go-login").addEventListener("click", () => navigate("login"));
    $("#go-lista").addEventListener("click", () => navigate("lista"));
  }

  function renderLogin() {
    const email = state.bootstrap?.admin_email || "";
    content.innerHTML = `
      <div class="form-panel" style="max-width:420px;margin:40px auto">
        <h2 style="margin:0 0 4px;font-size:15px">Acesso administrativo</h2>
        <p style="margin:0 0 16px;font-size:9px;color:var(--muted)">${esc(state.bootstrap?.org_full || "")}</p>
        <label>E-mail</label>
        <input type="email" id="login-email" value="${esc(email)}" />
        <label>Senha</label>
        <input type="password" id="login-pass" />
        <div class="form-actions" style="justify-content:flex-end">
          <button type="button" class="btn btn-primary" id="login-btn">Entrar</button>
        </div>
      </div>
    `;
    const tryLogin = async () => {
      const res = await api("login", $("#login-email").value, $("#login-pass").value);
      if (!res.ok) {
        toast(res.error || "Erro no login");
        if (res.redirect === "settings") navigate("settings");
        return;
      }
      state.loggedIn = true;
      state.adminUser = res.admin_user || $("#login-email").value;
      state.connLabel = "Conectado";
      setFooter();
      state.navHistory = [];
      navigate("admin", { push: false, tab: "socies" });
      loadPessoas();
    };
    $("#login-btn").addEventListener("click", tryLogin);
    $("#login-pass").addEventListener("keydown", (e) => { if (e.key === "Enter") tryLogin(); });
  }

  async function renderSettings() {
    const res = await api("get_settings");
    const s = res.ok ? res.data : {};
    content.innerHTML = `
      <h1 class="page-title">Configurações</h1>
      <div class="form-panel" style="margin-top:12px">
        <label>ID da planilha Google (admin / API)</label>
        <input id="cfg-sheet" value="${esc(s.spreadsheet_id || "")}" />
        <label>URL do site público (sem /consulta.html)</label>
        <input id="cfg-site" value="${esc(s.public_site_url || "")}" placeholder="https://anmolock.github.io/sinapesc-casanova-reap" />
        <label>E-mail do administrador</label>
        <input id="cfg-email" value="${esc(s.admin_email || "")}" />
        <label>Senha do administrador</label>
        <input id="cfg-pass" type="password" value="${esc(s.admin_password || "")}" />
        <div class="cred-label" id="cfg-cred">${esc(s.credentials_label || "")}</div>
        <input type="file" id="cfg-json" accept=".json,application/json" hidden />
        <button type="button" class="btn btn-primary" id="cfg-import">Importar JSON da Conta de Serviço…</button>
        <div class="form-actions">
          <button type="button" class="btn btn-outline-dark" id="cfg-save">Salvar</button>
          <button type="button" class="btn btn-primary" id="cfg-test">Testar conexão</button>
          <button type="button" class="btn btn-outline-dark" id="cfg-qrs">Gerar QRs do site</button>
        </div>
      </div>
    `;

    $("#cfg-import").addEventListener("click", () => $("#cfg-json").click());
    $("#cfg-json").addEventListener("change", async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const text = await file.text();
      const r = await api("import_credentials_json", text);
      if (r.ok) {
        $("#cfg-cred").textContent = r.credentials_label;
        toast("Credenciais importadas.");
      } else toast(r.error);
    });

    $("#cfg-save").addEventListener("click", async () => {
      const r = await api("save_settings", {
        spreadsheet_id: $("#cfg-sheet").value,
        public_site_url: $("#cfg-site").value,
        admin_email: $("#cfg-email").value,
        admin_password: $("#cfg-pass").value,
      });
      toast(r.ok ? "Configurações salvas." : r.error);
      if (r.ok) refreshBootstrap();
    });

    $("#cfg-test").addEventListener("click", async () => {
      await api("save_settings", {
        spreadsheet_id: $("#cfg-sheet").value,
        public_site_url: $("#cfg-site").value,
        admin_email: $("#cfg-email").value,
        admin_password: $("#cfg-pass").value,
      });
      const r = await api("test_connection");
      toast(r.ok ? `Conexão OK! Associados: ${r.count}` : r.error);
    });

    $("#cfg-qrs").addEventListener("click", async () => {
      await api("save_settings", { public_site_url: $("#cfg-site").value, spreadsheet_id: $("#cfg-sheet").value });
      api("generate_site_qrs", true);
    });
  }

  function renderAdmin() {
    content.innerHTML = `
      <div>
        <span class="page-title">Sócios</span>
        <span class="page-meta" id="admin-count"></span>
        <p class="page-sub">Clique no nome para abrir o REAP</p>
      </div>
      <div class="toolbar">
        <div class="search-wrap">
          <span class="search-icon">⌕</span>
          <input type="search" id="admin-search" placeholder="Buscar por nome ou CPF" value="${esc(state.search)}" />
        </div>
        <div class="btn-row">
          <button type="button" class="btn btn-outline-dark btn-sm" id="admin-refresh">↻ Atualizar</button>
          <button type="button" class="btn btn-outline-dark btn-sm" id="admin-lote">⇪ Cadastro em lote</button>
          <button type="button" class="btn btn-primary btn-sm" id="admin-new">+ Novo sócio</button>
        </div>
      </div>
      <div id="admin-list"></div>
    `;
    $("#admin-search").addEventListener("input", (e) => {
      state.search = e.target.value;
      renderAdminList();
    });
    $("#admin-refresh").addEventListener("click", loadPessoas);
    $("#admin-new").addEventListener("click", () => openPessoaModal());
    $("#admin-lote").addEventListener("click", openLoteModal);
    renderAdminList();
    if (!state.pessoas.length) loadPessoas();
  }

  function filteredPessoas() {
    const q = state.search.trim().toLowerCase();
    const digits = q.replace(/\D/g, "");
    if (!q) return state.pessoas;
    return state.pessoas.filter((p) =>
      p.nome.toLowerCase().includes(q) || (digits && p.cpf_raw.includes(digits))
    );
  }

  function renderAdminList() {
    const list = $("#admin-list");
    if (!list) return;
    const pessoas = filteredPessoas();
    $("#admin-count").textContent = state.pessoas.length ? `${state.pessoas.length} cadastrados` : "";
    if (!pessoas.length) {
      list.innerHTML = `<div class="empty-msg">${state.pessoas.length ? "Nenhum sócio encontrado." : "Nenhum sócio cadastrado."}</div>`;
      return;
    }
    list.innerHTML = pessoas.map((p) => pessoaCardHtml(p, true)).join("");
    bindPessoaCards(list, true);
  }

  function pessoaCardHtml(p, editable) {
    const expanded = state.expanded.has(p.id);
    let detail = "";
    if (expanded) {
      const anos = (p.anos || []).map((a) => `
        <div class="year-label">Ano ${a.ano}</div>
        <div class="pills">${renderPills(p.id, a.ano, a.meses, editable)}</div>
      `).join("") || `<div class="empty-msg" style="padding:8px 0">Nenhum ano registrado.</div>`;
      const addAno = editable ? `
        <div style="margin-top:14px;display:flex;gap:8px;align-items:center">
          <input type="number" id="ano-new-${p.id}" value="${new Date().getFullYear() + 1}" style="width:80px;padding:6px" />
          <button type="button" class="btn btn-outline-dark btn-sm" data-add-ano="${p.id}">Adicionar ano</button>
        </div>` : "";
      detail = `<div class="card-detail">${anos}${addAno}</div>`;
    }
    const actions = editable ? `
      <button type="button" class="icon-btn" data-qr="${p.id}">▦ QR</button>
      <button type="button" class="icon-btn" data-edit="${p.id}">✎ Editar</button>
      <button type="button" class="icon-btn danger" data-del="${p.id}">🗑 Excluir</button>
    ` : "";
    return `
      <div class="card" data-id="${p.id}">
        <div class="card-head">
          <div class="avatar">${esc(p.iniciais)}</div>
          <div class="card-info" data-toggle="${p.id}">
            <p class="card-name">${esc(p.nome_display)}</p>
            <p class="card-cpf">CPF: ${esc(p.cpf)}</p>
          </div>
          <div class="card-actions">
            ${actions}
            <button type="button" class="chevron" data-toggle="${p.id}">${expanded ? "▴" : "▾"}</button>
          </div>
        </div>
        ${detail}
      </div>`;
  }

  function renderPills(personId, ano, meses, editable) {
    const mesesKeys = state.bootstrap?.meses || [];
    return mesesKeys.map((m) => {
      const on = !!meses[m];
      const cls = on ? "on" : "off";
      const mark = on ? "✓" : "!";
      const ed = editable ? `editable data-pill="${personId}|${ano}|${m}|${on ? 0 : 1}"` : "";
      return `<button type="button" class="pill ${cls}" ${ed} title="${esc(state.bootstrap?.meses_label?.[m] || m)}">${m.toUpperCase()} ${mark}</button>`;
    }).join("");
  }

  function bindPessoaCards(root, editable) {
    root.querySelectorAll("[data-toggle]").forEach((el) => {
      el.addEventListener("click", () => {
        const id = el.dataset.toggle;
        if (state.expanded.has(id)) state.expanded.delete(id);
        else state.expanded.add(id);
        if (state.screen === "lista") renderLista();
        else renderAdminList();
      });
    });
    if (!editable) return;
    root.querySelectorAll("[data-qr]").forEach((b) => b.addEventListener("click", () => showQr("pessoa", b.dataset.qr)));
    root.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () => {
      const p = state.pessoas.find((x) => x.id === b.dataset.edit);
      if (p) openPessoaModal(p);
    }));
    root.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", async () => {
      const p = state.pessoas.find((x) => x.id === b.dataset.del);
      if (!p) return;
      if (!(await confirmModal("Excluir sócio", `Remover ${p.nome_display} e todo o histórico REAP?`))) return;
      api("delete_pessoa", p.id);
    }));
    root.querySelectorAll("[data-pill]").forEach((b) => b.addEventListener("click", () => {
      const [pid, ano, mes, novo] = b.dataset.pill.split("|");
      api("toggle_mes", pid, parseInt(ano, 10), mes, novo === "1");
    }));
    root.querySelectorAll("[data-add-ano]").forEach((b) => b.addEventListener("click", () => {
      const id = b.dataset.addAno;
      const inp = document.getElementById(`ano-new-${id}`);
      if (inp) api("add_ano", id, parseInt(inp.value, 10));
    }));
  }

  async function openPessoaModal(pessoa) {
    const isEdit = !!pessoa;
    const backdrop = await showModal(`
      <div class="modal-head">${isEdit ? "Editar sócio" : "Novo sócio"}</div>
      <div class="modal-body">
        <label>Nome completo</label>
        <input id="m-nome" value="${esc(pessoa?.nome || "")}" />
        <label>CPF (11 dígitos)</label>
        <input id="m-cpf" value="${esc(pessoa?.cpf_raw || "")}" />
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
        <button type="button" class="btn btn-primary" id="m-save">Salvar</button>
      </div>
    `);
    backdrop.querySelector("#m-save").addEventListener("click", async () => {
      const payload = {
        id: pessoa?.id || "",
        nome: backdrop.querySelector("#m-nome").value,
        cpf: backdrop.querySelector("#m-cpf").value,
      };
      const r = await api("save_pessoa", payload);
      if (!r.pending && !r.ok) toast(r.error);
      else backdrop._close(true);
    });
  }

  async function openLoteModal() {
    const ano = new Date().getFullYear();
    const backdrop = await showModal(`
      <div class="modal-head">Cadastro em lote</div>
      <div class="modal-body">
        <label>Ano REAP</label>
        <input type="number" id="l-ano" value="${ano}" style="width:100px" />
        <label>Linhas (Nome + CPF por linha)</label>
        <textarea id="l-raw" placeholder="João Silva;12345678901"></textarea>
        <div id="l-months" class="month-grid"></div>
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
        <button type="button" class="btn btn-primary" id="l-save">Importar</button>
      </div>
    `, "modal-wide");
    const grid = backdrop.querySelector("#l-months");
    const meses = state.bootstrap?.meses || [];
    grid.innerHTML = meses.map((m) => `
      <div class="month-check"><label><input type="checkbox" value="${m}" /> ${m.toUpperCase()}</label></div>
    `).join("");
    backdrop.querySelector("#l-save").addEventListener("click", () => {
      const mesesOn = [...grid.querySelectorAll("input:checked")].map((c) => c.value);
      api("save_lote", backdrop.querySelector("#l-raw").value, parseInt(backdrop.querySelector("#l-ano").value, 10), mesesOn);
      backdrop._close(true);
    });
  }

  function loadPessoas() {
    api("load_pessoas");
  }

  function renderPendencias() {
    const ano = new Date().getFullYear();
    content.innerHTML = `
      <div><span class="page-title">Pendências REAP</span> <span class="page-meta" id="pend-stats">Carregando…</span></div>
      <div class="toolbar">
        <label>Ano</label>
        <input type="number" id="pend-ano" value="${ano}" style="width:80px;padding:6px;margin-right:12px" />
        <span id="pend-cal" style="font-size:9px;font-weight:700;color:var(--accent)"></span>
        <div class="search-wrap" style="max-width:280px;margin-left:auto">
          <input type="search" id="pend-search" placeholder="Buscar" />
        </div>
        <button type="button" class="btn btn-outline-dark btn-sm" id="pend-cal-btn">Alterar calendário…</button>
        <button type="button" class="btn btn-primary btn-sm" id="pend-marcar">Marcar pendentes desta lista</button>
        <button type="button" class="btn btn-ghost btn-sm" id="pend-refresh">Atualizar</button>
      </div>
      <div id="pend-list"></div>
    `;
    const reload = () => api("load_pendencias", parseInt($("#pend-ano").value, 10));
    $("#pend-refresh").addEventListener("click", reload);
    $("#pend-ano").addEventListener("change", reload);
    $("#pend-cal-btn").addEventListener("click", () => openCalendarioModal());
    $("#pend-marcar").addEventListener("click", marcarPendentesLista);
    reload();
  }

  function renderPendenciasList(data) {
    state.pendencias = data;
    const q = ($("#pend-search")?.value || "").trim().toLowerCase();
    const digits = q.replace(/\D/g, "");
    let items = data.pendentes || [];
    if (q) {
      items = items.filter((s) =>
        s.nome.toLowerCase().includes(q) || (digits && s.cpf.replace(/\D/g, "").includes(digits))
      );
    }
    const nP = (data.pendentes || []).length;
    const nR = data.regulares_count || 0;
    $("#pend-stats").textContent = `${nP} pendente(s) · ${nR} regular(es) · ${nP + nR} sócio(s)`;
    $("#pend-cal").textContent = "Calendário: " + (data.calendario_texto || "");
    const list = $("#pend-list");
    if (!items.length) {
      list.innerHTML = `<div class="empty-msg">${nP + nR === 0 ? "Nenhum sócio cadastrado." : "Nenhum pendente nesta lista."}</div>`;
      return;
    }
    list.innerHTML = items.map((s) => `
      <div class="card">
        <div class="card-head">
          <div class="card-info">
            <p class="card-name">${esc(s.nome_display)}</p>
            <p class="card-cpf">${esc(s.rotulo)} · CPF ${esc(s.cpf)}</p>
          </div>
          <div class="card-actions">
            <button type="button" class="btn btn-primary btn-sm" data-marcar="${s.person_id}">Marcar só os pendentes</button>
            <button type="button" class="btn btn-ghost btn-sm" data-ficha="${s.person_id}">Abrir ficha</button>
          </div>
        </div>
      </div>
    `).join("");
    list.querySelectorAll("[data-marcar]").forEach((b) => b.addEventListener("click", async () => {
      const s = items.find((x) => x.person_id === b.dataset.marcar);
      if (!s || !s.faltando.length) return;
      const nomes = s.faltando.map((m) => m.toUpperCase()).join(", ");
      if (!(await confirmModal("Confirmar", `Marcar ${nomes} em ${s.ano} para ${s.nome_display}?`))) return;
      api("marcar_meses_massa", s.ano, s.faltando, [s.person_id], false);
    }));
    list.querySelectorAll("[data-ficha]").forEach((b) => b.addEventListener("click", () => {
      state.expanded.add(b.dataset.ficha);
      navigate("admin", { tab: "socies" });
    }));
    if ($("#pend-search")) {
      $("#pend-search").oninput = () => renderPendenciasList(data);
    }
  }

  async function openCalendarioModal() {
    const ano = parseInt($("#pend-ano")?.value || new Date().getFullYear(), 10);
    const cal = state.pendencias?.calendario || [];
    const meses = state.bootstrap?.meses || [];
    const backdrop = await showModal(`
      <div class="modal-head">Calendário REAP ${ano}</div>
      <div class="modal-body">
        <p style="font-size:9px;color:var(--muted)">Meses obrigatórios (aba Config da planilha).</p>
        <div class="month-grid" id="cal-grid"></div>
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
        <button type="button" class="btn btn-primary" id="cal-save">Salvar</button>
      </div>
    `);
    const grid = backdrop.querySelector("#cal-grid");
    grid.innerHTML = meses.map((m) => `
      <div class="month-check"><label><input type="checkbox" value="${m}" ${cal.includes(m) ? "checked" : ""} /> ${m.toUpperCase()}</label></div>
    `).join("");
    backdrop.querySelector("#cal-save").addEventListener("click", () => {
      const sel = [...grid.querySelectorAll("input:checked")].map((c) => c.value);
      api("save_calendario", ano, sel);
      backdrop._close(true);
    });
  }

  async function marcarPendentesLista() {
    const data = state.pendencias;
    if (!data || !data.pendentes?.length) {
      toast("Nenhum pendente nesta lista.");
      return;
    }
    const ids = data.pendentes.map((s) => s.person_id);
    if (!(await confirmModal("Confirmar", `Marcar calendário ${data.calendario_texto} em ${ids.length} sócio(s)?`))) return;
    api("marcar_meses_massa", data.ano, data.calendario, ids, false);
  }

  function renderRelatorio() {
    const ano = new Date().getFullYear();
    content.innerHTML = `
      <h1 class="page-title">Relatório de conformidade REAP</h1>
      <p class="page-sub" style="max-width:880px">Somente administrador. CPF completo. Imprimir → PDF. Consulta pública continua mascarada.</p>
      <div class="form-panel" style="margin-top:12px">
        <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center">
          <label>Ano</label>
          <input type="number" id="rel-ano" value="${ano}" style="width:80px;padding:6px" />
          <label><input type="radio" name="rel-modo" value="diretoria" checked /> Diretoria (todos)</label>
          <label><input type="radio" name="rel-modo" value="individual" /> Comprovante individual</label>
        </div>
        <label style="margin-top:12px">Buscar sócio (comprovante individual)</label>
        <input id="rel-busca" />
        <div class="form-actions">
          <button type="button" class="btn btn-primary" id="rel-gerar">Gerar HTML</button>
        </div>
      </div>
    `;
    $("#rel-gerar").addEventListener("click", () => {
      const modo = document.querySelector('input[name="rel-modo"]:checked')?.value || "diretoria";
      api("generate_relatorio", parseInt($("#rel-ano").value, 10), modo, $("#rel-busca").value);
    });
  }

  function renderBackup() {
    const ultimo = state.bootstrap?.ultimo_backup_em || "Nunca";
    const pasta = state.bootstrap?.backup_root || "";
    content.innerHTML = `
      <h1 class="page-title">Backup local</h1>
      <p class="page-sub">Cópia CSV local. Não substitui a planilha na nuvem.</p>
      <div class="form-panel" style="margin-top:12px">
        <p><strong>Último backup:</strong> ${esc(ultimo)}</p>
        <p style="font-size:9px;color:var(--muted)">Pasta: ${esc(pasta)}</p>
        <div class="form-actions">
          <button type="button" class="btn btn-primary" id="bk-run">Gerar backup agora</button>
          <button type="button" class="btn btn-outline-dark" id="bk-open">Abrir pasta de backups</button>
        </div>
        <div id="bk-list" style="margin-top:16px;font-size:9px"></div>
      </div>
    `;
    $("#bk-run").addEventListener("click", async () => {
      if (await confirmModal("Backup", "Copiar abas Pessoas e Reap para CSV neste computador?")) {
        api("run_backup");
      }
    });
    $("#bk-open").addEventListener("click", () => api("open_path", pasta));
    refreshBackupList();
  }

  async function refreshBackupList() {
    const r = await api("list_backups");
    const el = $("#bk-list");
    if (!el || !r.ok) return;
    el.innerHTML = r.data?.length
      ? `<strong>Backups recentes</strong><br>${r.data.map(esc).join("<br>")}`
      : "";
  }

  function renderAuditoria() {
    content.innerHTML = `
      <div><span class="page-title">Auditoria</span> <span class="page-meta" id="aud-hint">Carregando…</span></div>
      <div class="toolbar">
        <input type="search" id="aud-search" placeholder="Buscar" style="flex:0 1 280px;padding:8px;border:1px solid var(--border)" />
        <button type="button" class="btn btn-ghost btn-sm" id="aud-refresh">Atualizar</button>
      </div>
      <div id="aud-list"></div>
    `;
    $("#aud-refresh").addEventListener("click", () => api("load_auditoria"));
    $("#aud-search")?.addEventListener("input", () => renderAuditoriaList(state.auditoria));
    api("load_auditoria");
  }

  function renderAuditoriaList(eventos) {
    state.auditoria = eventos || [];
    const q = $("#aud-search")?.value || "";
    api("filter_auditoria_local", state.auditoria, q).then((r) => {
      const items = r.ok ? r.data : state.auditoria;
      $("#aud-hint").textContent = `${items.length} registro(s) · aba Auditoria da planilha`;
      const list = $("#aud-list");
      if (!items.length) {
        list.innerHTML = `<div class="empty-msg">Nenhum registro ainda.</div>`;
        return;
      }
      list.innerHTML = items.map((e) => `
        <div class="audit-card">
          <div class="audit-meta">${esc(e.em)} · ${esc(e.usuario || "(sem usuário)")}</div>
          <div class="audit-text">${esc(e.detalhe || e.acao)}</div>
        </div>
      `).join("");
    });
  }

  function renderLista() {
    content.innerHTML = `
      <div class="toolbar" style="margin-top:0">
        <span class="page-title">Lista pública</span>
        <div class="btn-row" style="margin-left:auto">
          <button type="button" class="btn btn-outline-dark btn-sm" id="qr-consulta">QR Consulta CPF</button>
          <button type="button" class="btn btn-primary btn-sm" id="qr-lista">QR Lista</button>
          <button type="button" class="btn btn-outline-dark btn-sm" id="qr-pasta">Pasta QRs</button>
        </div>
      </div>
      <p class="page-sub">Consulta online — CPF mascarado no celular.</p>
      <div class="toolbar">
        <div class="search-wrap">
          <span class="search-icon">⌕</span>
          <input type="search" id="lista-search" placeholder="Buscar por nome ou CPF" value="${esc(state.search)}" />
        </div>
      </div>
      <div id="lista-cards"></div>
    `;
    $("#qr-consulta").addEventListener("click", () => showQr("consulta"));
    $("#qr-lista").addEventListener("click", () => showQr("lista"));
    $("#qr-pasta").addEventListener("click", () => api("open_path", state.bootstrap?.qr_dir || ""));
    $("#lista-search").addEventListener("input", (e) => {
      state.search = e.target.value;
      renderListaCards();
    });
    if (!state.pessoas.length) loadPessoas();
    else renderListaCards();
  }

  function renderListaCards() {
    const list = $("#lista-cards");
    if (!list) return;
    const pessoas = filteredPessoas();
    if (!pessoas.length) {
      list.innerHTML = `<div class="empty-msg">Carregando…</div>`;
      loadPessoas();
      return;
    }
    list.innerHTML = pessoas.map((p) => pessoaCardHtml({ ...p, cpf: maskCpf(p.cpf_raw) }, false)).join("");
    bindPessoaCards(list, false);
  }

  function maskCpf(raw) {
    const d = String(raw || "").replace(/\D/g, "");
    if (d.length !== 11) return d;
    return `***.***.${d.slice(6, 9)}-**`;
  }

  async function showQr(kind, personId) {
    const r = await api("qr_preview", kind, personId || "");
    if (!r.ok) { toast(r.error); return; }
    await showModal(`
      <div class="modal-head">QR Code</div>
      <div class="modal-body qr-preview">
        <img src="${r.data.image}" alt="QR" />
        <div class="qr-url">${esc(r.data.url)}</div>
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-primary" data-modal-close="ok">Fechar</button>
      </div>
    `);
  }

  async function openAtalhosModal() {
    const ano = new Date().getFullYear();
    const meses = state.bootstrap?.meses || [];
    const monthBlock = (id) => meses.map((m) => `
      <div class="month-check"><label><input type="checkbox" class="${id}" value="${m}" /> ${m.toUpperCase()}</label></div>
    `).join("");
    const backdrop = await showModal(`
      <div class="modal-head">Config.Atalhos</div>
      <div class="modal-body">
        <div class="card" style="margin-bottom:12px">
          <strong>1) Lote com REAP já marcado</strong>
          <div class="month-grid">${monthBlock("m1")}</div>
          <button type="button" class="btn btn-primary btn-sm" id="at-lote">Abrir lote com meses…</button>
        </div>
        <div class="card">
          <strong>2) Marcar meses nos sócios cadastrados</strong>
          <input type="number" id="at-ano" value="${ano}" style="width:80px;margin:8px 0" />
          <div class="month-grid">${monthBlock("m2")}</div>
          <button type="button" class="btn btn-primary btn-sm" id="at-massa">Marcar em todos</button>
        </div>
      </div>
      <div class="modal-foot"><button type="button" class="btn btn-outline-dark" data-modal-close="ok">Fechar</button></div>
    `, "modal-wide");
    backdrop.querySelector("#at-lote").addEventListener("click", () => {
      backdrop._close(true);
      openLoteModal();
    });
    backdrop.querySelector("#at-massa").addEventListener("click", async () => {
      const mesesOn = [...backdrop.querySelectorAll(".m2:checked")].map((c) => c.value);
      if (!mesesOn.length) { toast("Escolha pelo menos um mês."); return; }
      if (!(await confirmModal("Atalhos", `Marcar ${mesesOn.join(", ").toUpperCase()} em todos os sócios?`))) return;
      api("marcar_meses_em_massa", parseInt(backdrop.querySelector("#at-ano").value, 10), mesesOn, null, false);
      backdrop._close(true);
    });
  }

  async function refreshBootstrap() {
    const r = await api("get_bootstrap");
    if (r.ok) {
      state.bootstrap = r.data;
      $("#org-short").textContent = r.data.org_short;
      $("#org-full").textContent = r.data.org_full;
    }
  }

  function wireEvents() {
    AppEvents.on("status", (p) => setStatus(p.msg));
    AppEvents.on("pessoas", (r) => {
      if (r.ok) {
        state.pessoas = r.data || [];
        state.connLabel = "Conectado";
        setFooter();
        if (state.screen === "admin") renderAdminList();
        if (state.screen === "lista") renderListaCards();
      } else toast(r.error);
    });
    AppEvents.on("pessoa_saved", (r) => {
      if (r.ok) { toast("Salvo."); loadPessoas(); }
      else toast(r.error);
    });
    AppEvents.on("pessoa_deleted", (r) => {
      if (r.ok) { toast("Excluído."); loadPessoas(); }
      else toast(r.error);
    });
    AppEvents.on("mes_toggled", (r) => {
      if (r.ok) loadPessoas();
      else toast(r.error);
    });
    AppEvents.on("ano_added", (r) => {
      if (r.ok) loadPessoas();
      else toast(r.error);
    });
    AppEvents.on("lote_saved", (r) => {
      if (r.ok) { toast("Lote importado."); loadPessoas(); }
      else toast(r.error);
    });
    AppEvents.on("pendencias", (r) => {
      if (r.ok) renderPendenciasList(r.data);
      else toast(r.error);
    });
    AppEvents.on("calendario_saved", (r) => {
      if (r.ok) {
        toast("Calendário salvo.");
        api("load_pendencias", parseInt($("#pend-ano")?.value || new Date().getFullYear(), 10));
      } else toast(r.error);
    });
    AppEvents.on("massa_ok", (r) => {
      if (r.ok) {
        toast(`Atualizados: ${r.data?.atualizados ?? "?"}`);
        if (state.screen === "pendencias") api("load_pendencias", parseInt($("#pend-ano")?.value, 10));
        else loadPessoas();
      } else toast(r.error);
    });
    AppEvents.on("relatorio", (r) => {
      if (r.ok && r.data?.html) {
        const w = window.open("");
        if (w) { w.document.write(r.data.html); w.document.close(); }
        toast("Relatório aberto.");
      } else toast(r.error);
    });
    AppEvents.on("backup", (r) => {
      if (r.ok) {
        toast(`Backup: ${r.data?.pasta || "ok"}`);
        refreshBootstrap();
        refreshBackupList();
      } else toast(r.error);
    });
    AppEvents.on("auditoria", (r) => {
      if (r.ok) renderAuditoriaList(r.data);
      else toast(r.error);
    });
    AppEvents.on("qrs", (r) => {
      toast(r.ok ? `QRs → ${r.data?.base}` : r.error);
    });
  }

  async function init() {
    wireEvents();
    await refreshBootstrap();
    $("#app").classList.remove("hidden");
    navigate("home", { push: false });
  }

  window.addEventListener("pywebviewready", init);
  if (window.pywebview) init();
})();
