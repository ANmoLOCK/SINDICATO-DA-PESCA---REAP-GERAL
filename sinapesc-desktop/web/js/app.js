/* Sinapesc REAP — UI web compacta (pywebview) */

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

  const MAR_OUT = ["mar", "abr", "mai", "jun", "jul", "ago", "set", "out"];

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
    connLabel: "",
    sortMode: (typeof localStorage !== "undefined" && localStorage.getItem("sinapesc_sort")) || "recent",
    loteBackdrop: null,
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
    const sep = document.querySelector(".footer-conn-sep");
    if (sep) sep.style.display = state.connLabel ? "" : "none";
    $("#footer-conn").textContent = state.connLabel;
  }

  function setPage(html) {
    content.innerHTML = `<div class="page">${html}</div>`;
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatCpf(value) {
    const d = String(value || "").replace(/\D/g, "").slice(0, 11);
    const p1 = d.slice(0, 3);
    const p2 = d.slice(3, 6);
    const p3 = d.slice(6, 9);
    const p4 = d.slice(9, 11);
    let out = p1;
    if (p2) out += `.${p2}`;
    if (p3) out += `.${p3}`;
    if (p4) out += `-${p4}`;
    return out;
  }

  function formatNome(value) {
    return String(value || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map((word) => word.split("-").map((part) => {
        if (!part) return part;
        return part.charAt(0).toLocaleUpperCase("pt-BR") + part.slice(1).toLocaleLowerCase("pt-BR");
      }).join("-"))
      .join(" ");
  }

  function bindNomeMask(input) {
    if (!input) return;
    const paint = () => { input.value = formatNome(input.value); };
    input.addEventListener("blur", paint);
    input.addEventListener("change", paint);
  }

  function bindCpfMask(input) {
    if (!input) return;
    const paint = () => { input.value = formatCpf(input.value); };
    input.addEventListener("input", paint);
    paint();
  }

  function createModal(html, className = "") {
    const backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop";
    backdrop.innerHTML = `<div class="modal ${className}">${html}</div>`;
    function close(result) {
      backdrop.remove();
      if (backdrop._onClose) backdrop._onClose(result);
    }
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) close(false);
    });
    backdrop.querySelectorAll("[data-modal-close]").forEach((btn) => {
      btn.addEventListener("click", () => close(btn.dataset.modalClose === "ok"));
    });
    backdrop._close = close;
    modalRoot.appendChild(backdrop);
    return backdrop;
  }

  function confirmModal(title, text) {
    return new Promise((resolve) => {
      const backdrop = createModal(`
        <div class="modal-head">${esc(title)}</div>
        <div class="modal-body"><p style="margin:0;white-space:pre-wrap">${esc(text)}</p></div>
        <div class="modal-foot">
          <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
          <button type="button" class="btn btn-primary" data-modal-close="ok">Confirmar</button>
        </div>
      `);
      backdrop._onClose = resolve;
    });
  }

  function mesesKeys() {
    return state.bootstrap?.meses || ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"];
  }

  function monthChecksHtml(className, selected) {
    const sel = new Set(selected || []);
    return mesesKeys().map((m) => `
      <div class="month-check">
        <label><input type="checkbox" class="${className}" value="${m}" ${sel.has(m) ? "checked" : ""} /> ${m.toUpperCase()}</label>
      </div>
    `).join("");
  }

  function applyPreset(root, className, meses) {
    root.querySelectorAll(`.${className}`).forEach((cb) => {
      cb.checked = meses.includes(cb.value);
    });
  }

  function presetButtons(className) {
    return `
      <div class="preset-row" data-preset-for="${className}">
        <button type="button" class="btn btn-ghost btn-sm" data-preset-set="marout">Mar → Out</button>
        <button type="button" class="btn btn-ghost btn-sm" data-preset-set="ano">Ano inteiro</button>
        <button type="button" class="btn btn-ghost btn-sm" data-preset-set="limpar">Limpar</button>
      </div>`;
  }

  function bindPresets(root, className) {
    root.querySelectorAll(`[data-preset-for="${className}"] [data-preset-set]`).forEach((btn) => {
      btn.addEventListener("click", () => {
        const kind = btn.dataset.presetSet;
        const all = mesesKeys();
        if (kind === "marout") applyPreset(root, className, MAR_OUT);
        else if (kind === "ano") applyPreset(root, className, all);
        else applyPreset(root, className, []);
      });
    });
  }

  function selectedMonths(root, className) {
    return [...root.querySelectorAll(`.${className}:checked`)].map((c) => c.value);
  }

  function isSecretariaScreen(screen) {
    return !["home", "login", "settings"].includes(screen || "");
  }

  function navigate(screen, { push = true, tab = null } = {}) {
    const leavingSecretaria =
      state.loggedIn && isSecretariaScreen(state.screen) && !isSecretariaScreen(screen);
    if (push && state.screen && state.screen !== screen) {
      state.navHistory.push(state.screen);
    }
    state.screen = screen;
    renderTabs(tab);
    renderHeader();
    renderScreen();
    // Ao sair da secretaria, puxa a planilha fresca do Google (contador e REAP).
    if (leavingSecretaria) loadPessoas();
  }

  function goBack() {
    const prev = state.navHistory.pop();
    navigate(prev || (state.loggedIn ? "admin" : "home"), { push: false });
  }

  function tabForScreen(screen) {
    const map = {
      admin: "socies",
      pendencias: "pendencias",
      relatorio: "relatorio",
      backup: "backup",
      auditoria: "auditoria",
      atalhos: "atalhos",
      lista: "lista",
    };
    return map[screen] || null;
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
        const tab = TABS.find((x) => x.id === cell.dataset.tab);
        if (tab) navigate(tab.screen, { tab: tab.id });
      });
    });
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
    loadPessoas();
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
      atalhos: renderAtalhos,
      lista: renderLista,
    };
    (fns[state.screen] || renderHome)();
  }

  function renderHome() {
    setPage(`
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
    `);
    $("#go-login").addEventListener("click", () => navigate("login"));
    $("#go-lista").addEventListener("click", () => navigate("lista"));
  }

  function renderLogin() {
    const email = state.bootstrap?.admin_email || "";
    setPage(`
      <div class="form-panel" style="max-width:400px;margin:28px auto">
        <h2 style="margin:0 0 2px;font-size:16px">Acesso administrativo</h2>
        <p class="page-sub">${esc(state.bootstrap?.org_full || "")}</p>
        <label>E-mail</label>
        <input type="email" id="login-email" value="${esc(email)}" />
        <label>Senha</label>
        <input type="password" id="login-pass" />
        <div class="form-actions" style="justify-content:flex-end">
          <button type="button" class="btn btn-primary" id="login-btn">Entrar</button>
        </div>
      </div>
    `);
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
      maybeBackupReminder();
    };
    $("#login-btn").addEventListener("click", tryLogin);
    $("#login-pass").addEventListener("keydown", (e) => { if (e.key === "Enter") tryLogin(); });
  }

  async function maybeBackupReminder() {
    const ultimo = state.bootstrap?.ultimo_backup_em || "";
    if (!ultimo || ultimo === "Nunca") {
      if (await confirmModal("Backup", "Ainda não há backup local. Gerar agora?")) {
        api("run_backup");
      }
    }
  }

  async function renderSettings() {
    const res = await api("get_settings");
    const s = res.ok ? res.data : {};
    setPage(`
      <h1 class="page-title">Configurações</h1>
      <div class="form-panel" style="margin-top:10px">
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
        <button type="button" class="btn btn-primary btn-sm" id="cfg-import">Importar JSON da Conta de Serviço…</button>
        <div class="site-box">
          <h4>Site público online (gratuito)</h4>
          <p>1) Planilha como Leitor · 2) GitHub Pages · 3) Cole a URL acima · 4) Gere os QRs. O notebook não precisa ficar ligado.</p>
          <div class="btn-row">
            <button type="button" class="btn btn-primary btn-sm" id="cfg-qrs">Gerar QRs do site</button>
            <button type="button" class="btn btn-outline-dark btn-sm" id="cfg-qr-consulta">QR Consulta CPF</button>
            <button type="button" class="btn btn-ghost btn-sm" id="cfg-qr-pasta">Pasta dos QRs</button>
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-outline-dark" id="cfg-save">Salvar</button>
          <button type="button" class="btn btn-primary" id="cfg-test">Testar conexão</button>
        </div>
      </div>
    `);

    const persist = () => api("save_settings", {
      spreadsheet_id: $("#cfg-sheet").value,
      public_site_url: $("#cfg-site").value,
      admin_email: $("#cfg-email").value,
      admin_password: $("#cfg-pass").value,
    });

    $("#cfg-import").addEventListener("click", () => $("#cfg-json").click());
    $("#cfg-json").addEventListener("change", async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const r = await api("import_credentials_json", await file.text());
      if (r.ok) { $("#cfg-cred").textContent = r.credentials_label; toast("Credenciais importadas."); }
      else toast(r.error);
    });
    $("#cfg-save").addEventListener("click", async () => {
      const r = await persist();
      toast(r.ok ? "Configurações salvas." : r.error);
      if (r.ok) refreshBootstrap();
    });
    $("#cfg-test").addEventListener("click", async () => {
      await persist();
      const r = await api("test_connection");
      toast(r.ok ? `Conexão OK! Associados: ${r.count}` : r.error);
    });
    $("#cfg-qrs").addEventListener("click", async () => {
      await persist();
      api("generate_site_qrs", true);
    });
    $("#cfg-qr-consulta").addEventListener("click", async () => {
      await persist();
      showQr("consulta");
    });
    $("#cfg-qr-pasta").addEventListener("click", () => api("open_path", state.bootstrap?.qr_dir || ""));
  }

  function renderAdmin() {
    setPage(`
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
          <label class="filter-wrap">Filtro
            <select id="admin-sort">
              <option value="recent">Mais recente</option>
              <option value="30d">Alterados (30 dias)</option>
              <option value="1y">Alterados (1 ano)</option>
              <option value="az">A–Z</option>
            </select>
          </label>
          <button type="button" class="btn btn-outline-dark btn-sm" id="admin-refresh">↻ Atualizar</button>
          <button type="button" class="btn btn-outline-dark btn-sm" id="admin-lote">⇪ Cadastro em lote</button>
          <button type="button" class="btn btn-primary btn-sm" id="admin-new">+ Novo sócio</button>
        </div>
      </div>
      <div id="admin-list"></div>
    `);
    $("#admin-search").addEventListener("input", (e) => {
      state.search = e.target.value;
      renderAdminList();
    });
    const sortSel = $("#admin-sort");
    if (sortSel) {
      const allowed = ["recent", "30d", "1y", "az"];
      if (!allowed.includes(state.sortMode)) state.sortMode = "recent";
      sortSel.value = state.sortMode;
      sortSel.addEventListener("change", () => {
        state.sortMode = sortSel.value;
        try { localStorage.setItem("sinapesc_sort", state.sortMode); } catch (_e) {}
        renderAdminList();
      });
    }
    $("#admin-refresh").addEventListener("click", loadPessoas);
    $("#admin-new").addEventListener("click", () => openPessoaModal());
    $("#admin-lote").addEventListener("click", () => openLoteModal());
    renderAdminList();
    if (!state.pessoas.length) loadPessoas();
  }

  function parseToggleDate(valor) {
    const s = String(valor || "").trim().slice(0, 19);
    if (!s) return null;
    const normalized = s.includes("T") ? s : s.replace(" ", "T");
    const dt = new Date(normalized);
    return Number.isNaN(dt.getTime()) ? null : dt;
  }

  function diasDesdeToggle(p) {
    const dt = parseToggleDate(p.ultimo_toggle_em);
    if (!dt) return null;
    return Math.max(0, (Date.now() - dt.getTime()) / 86400000);
  }

  function filteredPessoas() {
    const q = state.search.trim().toLowerCase();
    const digits = q.replace(/\D/g, "");
    let list = state.pessoas;
    if (q) {
      list = list.filter((p) =>
        p.nome.toLowerCase().includes(q) || (digits && p.cpf_raw.includes(digits))
      );
    }
    if (state.sortMode === "30d") {
      list = list.filter((p) => {
        const d = diasDesdeToggle(p);
        return d !== null && d <= 30;
      });
    } else if (state.sortMode === "1y") {
      list = list.filter((p) => {
        const d = diasDesdeToggle(p);
        return d !== null && d <= 365;
      });
    }
    return sortedPessoas(list);
  }

  function sortedPessoas(list) {
    const copy = list.map((p, i) => ({ p, i: p._idx ?? i }));
    if (state.sortMode === "az") {
      copy.sort((a, b) =>
        String(a.p.nome_display || a.p.nome || "").localeCompare(
          String(b.p.nome_display || b.p.nome || ""),
          "pt-BR",
          { sensitivity: "base" }
        )
      );
    } else {
      // Mais recente / 30d / 1y: prioriza última marca/desmarca REAP
      copy.sort((a, b) => {
        const ta = a.p.ultimo_toggle_em || "";
        const tb = b.p.ultimo_toggle_em || "";
        if (ta && tb && ta !== tb) return tb.localeCompare(ta);
        if (ta && !tb) return -1;
        if (!ta && tb) return 1;
        const ca = a.p.criado_em || "";
        const cb = b.p.criado_em || "";
        if (ca && cb && ca !== cb) return cb.localeCompare(ca);
        return b.i - a.i;
      });
    }
    return copy.map((x) => x.p);
  }

  function renderAdminList() {
    const list = $("#admin-list");
    if (!list) return;
    const pessoas = filteredPessoas();
    const count = $("#admin-count");
    if (count) {
      if (!state.pessoas.length) count.textContent = "";
      else if (pessoas.length === state.pessoas.length) count.textContent = `${state.pessoas.length} cadastrados`;
      else count.textContent = `${pessoas.length} de ${state.pessoas.length}`;
    }
    if (!pessoas.length) {
      const emptyMsg = !state.pessoas.length
        ? "Nenhum sócio cadastrado."
        : (state.sortMode === "30d" || state.sortMode === "1y")
          ? "Nenhum sócio com alteração REAP neste período."
          : "Nenhum sócio encontrado.";
      list.innerHTML = `<div class="empty-msg">${emptyMsg}</div>`;
      return;
    }
    list.innerHTML = pessoas.map((p) => pessoaCardHtml(p, true)).join("");
    bindPessoaCards(list, true);
  }

  function touchBadgeHtml(p) {
    const label = (p.ultimo_toggle_label || "").trim();
    if (!label) return "";
    const tip = p.ultimo_toggle_em
      ? `Última marca/desmarca de mês · ${p.ultimo_toggle_em}`
      : "Última marca/desmarca de mês";
    return `<span class="card-touch" title="${esc(tip)}"> — ${esc(label)}</span>`;
  }

  function pessoaCardHtml(p, editable) {
    const expanded = state.expanded.has(p.id);
    let detail = "";
    if (expanded) {
      const anos = (p.anos || []).map((a) => `
        <div class="year-label">Ano ${a.ano}</div>
        <div class="pills">${renderPills(p.id, a.ano, a.meses, editable)}</div>
      `).join("") || `<div class="empty-msg" style="padding:6px 0">Nenhum ano registrado.</div>`;
      const addAno = editable ? `
        <div class="inline-row" style="margin-top:8px">
          <input type="number" id="ano-new-${p.id}" value="${new Date().getFullYear() + 1}" />
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
            <p class="card-name">${esc(p.nome_display)}${touchBadgeHtml(p)}</p>
            <p class="card-cpf">CPF: ${esc(formatCpf(p.cpf_raw || p.cpf))}</p>
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
    return mesesKeys().map((m) => {
      const on = !!meses[m];
      const cls = on ? "on" : "off";
      const mark = on ? "✓" : "!";
      const ed = editable ? `editable data-pill="${personId}|${ano}|${m}|${on ? 0 : 1}"` : "";
      const title = esc(state.bootstrap?.meses_label?.[m] || m);
      return `<button type="button" class="pill ${cls}" ${ed} title="${title}">${m.toUpperCase()} ${mark}</button>`;
    }).join("");
  }

  function paintPill(btn, on) {
    if (!btn) return;
    btn.classList.toggle("on", on);
    btn.classList.toggle("off", !on);
    const label = (btn.textContent || "").trim().split(/\s+/)[0] || "";
    btn.textContent = `${label} ${on ? "✓" : "!"}`;
    const parts = (btn.dataset.pill || "").split("|");
    if (parts.length >= 3) {
      btn.dataset.pill = `${parts[0]}|${parts[1]}|${parts[2]}|${on ? 0 : 1}`;
    }
  }

  function applyLocalMes(pid, ano, mes, on) {
    const p = state.pessoas.find((x) => x.id === pid);
    if (!p) return;
    const a = (p.anos || []).find((x) => String(x.ano) === String(ano));
    if (a && a.meses) a.meses[mes] = on;
  }

  function bindPessoaCards(root, editable) {
    root.querySelectorAll("[data-toggle]").forEach((el) => {
      el.addEventListener("click", () => {
        const id = el.dataset.toggle;
        if (state.expanded.has(id)) state.expanded.delete(id);
        else state.expanded.add(id);
        if (state.screen === "lista") renderListaCards();
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
      const wantOn = novo === "1";
      paintPill(b, wantOn);
      applyLocalMes(pid, ano, mes, wantOn);
      const pessoa = state.pessoas.find((x) => x.id === pid);
      if (pessoa) {
        pessoa.ultimo_toggle_label = "agora";
        pessoa.ultimo_toggle_em = nowLocalStamp();
        if (state.screen === "admin") renderAdminList();
      }
      api("toggle_mes", pid, parseInt(ano, 10), mes, wantOn).then((r) => {
        if (r && r.ok === false && !r.pending) {
          paintPill(b, !wantOn);
          applyLocalMes(pid, ano, mes, !wantOn);
          toast(r.error || "Não foi possível marcar o mês.");
        }
      }).catch(() => {
        paintPill(b, !wantOn);
        applyLocalMes(pid, ano, mes, !wantOn);
        toast("Não foi possível marcar o mês.");
      });
    }));
    root.querySelectorAll("[data-add-ano]").forEach((b) => b.addEventListener("click", () => {
      const id = b.dataset.addAno;
      const inp = document.getElementById(`ano-new-${id}`);
      if (inp) api("add_ano", id, parseInt(inp.value, 10));
    }));
  }

  function openPessoaModal(pessoa) {
    const isEdit = !!pessoa;
    const backdrop = createModal(`
      <div class="modal-head">${isEdit ? "Editar sócio" : "Novo sócio"}</div>
      <div class="modal-body">
        <label>Nome completo</label>
        <input id="m-nome" value="${esc(formatNome(pessoa?.nome || ""))}" />
        <label>CPF</label>
        <input id="m-cpf" inputmode="numeric" maxlength="14" placeholder="000.000.000-00" value="${esc(formatCpf(pessoa?.cpf_raw || pessoa?.cpf || ""))}" />
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
        <button type="button" class="btn btn-primary" id="m-save">Salvar</button>
      </div>
    `);
    bindNomeMask(backdrop.querySelector("#m-nome"));
    bindCpfMask(backdrop.querySelector("#m-cpf"));
    backdrop.querySelector("#m-save").addEventListener("click", async () => {
      const r = await api("save_pessoa", {
        id: pessoa?.id || "",
        nome: formatNome(backdrop.querySelector("#m-nome").value),
        cpf: backdrop.querySelector("#m-cpf").value,
      });
      if (!r.pending && !r.ok) toast(r.error);
      else backdrop._close(true);
    });
  }

  function parseLoteText(raw) {
    const itens = [];
    String(raw || "").split(/\r?\n/).forEach((line) => {
      const t = line.trim();
      if (!t || /^nome/i.test(t)) return;
      let parts;
      if (t.includes(";")) parts = t.split(";", 2);
      else if (t.includes("\t")) parts = t.split("\t", 2);
      else if (t.includes(",")) {
        const i = t.lastIndexOf(",");
        parts = [t.slice(0, i), t.slice(i + 1)];
      } else {
        parts = t.split(/\s{2,}/, 2);
      }
      if (!parts || parts.length < 2) return;
      const nome = String(parts[0] || "").replace(/^"|"$/g, "").trim();
      const cpf = String(parts[1] || "").replace(/^"|"$/g, "").trim();
      if (nome || cpf) itens.push({ nome, cpf });
    });
    return itens;
  }

  function openLoteModal(opts = {}) {
    const ano = opts.ano || new Date().getFullYear();
    const meses = opts.meses || [];
    const banner = meses.length
      ? `<div class="banner-ok">Atalho: no ano ${ano} já entram marcados: ${meses.map((m) => m.toUpperCase()).join(", ")}</div>`
      : "";
    const backdrop = createModal(`
      <div class="modal-head">Cadastro em lote</div>
      <div class="modal-body">
        <p class="page-sub">Uma linha = um sócio. Os dados ficam guardados se der erro — a janela só fecha depois de importar.</p>
        ${banner}
        <div class="inline-row">
          <label>Ano REAP</label>
          <input type="number" id="l-ano" value="${esc(ano)}" />
        </div>
        ${meses.length ? "" : `
          ${presetButtons("lote-m")}
          <div class="month-grid">${monthChecksHtml("lote-m", [])}</div>
        `}
        <label>Colar lista (Nome;CPF — uma pessoa por linha)</label>
        <textarea id="l-paste" placeholder="Maria Silva;105.205.585-45"></textarea>
        <div class="btn-row" style="margin:6px 0 8px">
          <button type="button" class="btn btn-ghost btn-sm" id="l-paste-btn">Colar nas linhas</button>
          <button type="button" class="btn btn-ghost btn-sm" id="l-add">+ Linha</button>
          <button type="button" class="btn btn-ghost btn-sm" id="l-add-10">+ 10 linhas</button>
        </div>
        <div class="lote-head"><span>Nome completo</span><span>CPF</span><span></span></div>
        <div class="lote-rows" id="l-rows"></div>
        <p class="page-sub" id="l-status"></p>
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
        <button type="button" class="btn btn-primary" id="l-save">Importar</button>
      </div>
    `, "modal-wide");

    bindPresets(backdrop, "lote-m");
    const host = backdrop.querySelector("#l-rows");
    const saveBtn = backdrop.querySelector("#l-save");
    const statusEl = backdrop.querySelector("#l-status");
    state.loteBackdrop = backdrop;

    function collectRows() {
      return [...host.querySelectorAll(".lote-row")].map((r) => ({
        nome: formatNome(r.querySelector(".l-nome").value),
        cpf: r.querySelector(".l-cpf").value,
      })).filter((r) => r.nome.trim() || r.cpf.trim());
    }

    function persistDraft() {
      try {
        localStorage.setItem("sinapesc_lote_draft", JSON.stringify({
          ano: backdrop.querySelector("#l-ano").value,
          rows: collectRows(),
        }));
      } catch (_e) {}
    }

    function addRow(nome = "", cpf = "") {
      const row = document.createElement("div");
      row.className = "lote-row";
      row.innerHTML = `
        <input class="l-nome" value="${esc(formatNome(nome))}" placeholder="Nome completo" />
        <input class="l-cpf" value="${esc(formatCpf(cpf))}" placeholder="000.000.000-00" maxlength="14" />
        <button type="button" class="icon-btn danger l-del">🗑</button>
      `;
      row.querySelector(".l-del").addEventListener("click", () => {
        if (host.children.length <= 1) {
          row.querySelector(".l-nome").value = "";
          row.querySelector(".l-cpf").value = "";
          persistDraft();
          return;
        }
        row.remove();
        persistDraft();
      });
      row.querySelector(".l-nome").addEventListener("input", persistDraft);
      row.querySelector(".l-cpf").addEventListener("input", persistDraft);
      host.appendChild(row);
      bindNomeMask(row.querySelector(".l-nome"));
      bindCpfMask(row.querySelector(".l-cpf"));
    }

    let restored = [];
    try {
      const raw = localStorage.getItem("sinapesc_lote_draft");
      if (raw) restored = JSON.parse(raw).rows || [];
    } catch (_e) { restored = []; }

    if (restored.length) {
      restored.forEach((r) => addRow(r.nome || "", r.cpf || ""));
      statusEl.textContent = `Rascunho restaurado: ${restored.length} linha(s).`;
    } else {
      for (let i = 0; i < 8; i++) addRow();
    }

    backdrop.querySelector("#l-add").addEventListener("click", () => addRow());
    backdrop.querySelector("#l-add-10").addEventListener("click", () => {
      for (let i = 0; i < 10; i++) addRow();
    });
    backdrop.querySelector("#l-paste-btn").addEventListener("click", () => {
      const itens = parseLoteText(backdrop.querySelector("#l-paste").value);
      if (!itens.length) {
        toast("Cole linhas no formato Nome;CPF.");
        return;
      }
      host.innerHTML = "";
      itens.forEach((r) => addRow(r.nome, r.cpf));
      persistDraft();
      statusEl.textContent = `${itens.length} linha(s) coladas.`;
    });
    saveBtn.addEventListener("click", async () => {
      const rows = collectRows();
      if (!rows.length) {
        toast("Preencha pelo menos um Nome e CPF.");
        return;
      }
      persistDraft();
      const anoVal = parseInt(backdrop.querySelector("#l-ano").value, 10) || new Date().getFullYear();
      const mesesOn = meses.length ? meses : selectedMonths(backdrop, "lote-m");
      saveBtn.disabled = true;
      statusEl.textContent = `Enviando ${rows.length} sócio(s)… a janela só fecha se der certo.`;
      try {
        const r = await api("save_lote_rows", JSON.stringify(rows), anoVal, mesesOn);
        if (r && r.ok === false && !r.pending) {
          toast(r.error || "Não foi possível importar o lote.");
          statusEl.textContent = r.error || "Erro ao importar. Seus dados continuam aqui.";
          saveBtn.disabled = false;
        }
      } catch (_e) {
        toast("Erro ao enviar o lote. Seus nomes e CPFs foram guardados.");
        statusEl.textContent = "Erro de envio. Rascunho guardado — pode tentar de novo.";
        saveBtn.disabled = false;
      }
    });
  }

  function nowLocalStamp() {
    const d = new Date();
    const p = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
  }

  function loadPessoas() {
    api("load_pessoas");
  }

  function renderPendencias() {
    const ano = new Date().getFullYear();
    setPage(`
      <div>
        <span class="page-title">Pendências REAP</span>
        <span class="page-meta" id="pend-stats">Carregando…</span>
      </div>
      <div class="toolbar">
        <label>Ano</label>
        <input type="number" id="pend-ano" value="${ano}" style="width:80px" />
        <span id="pend-cal" style="font-size:12px;font-weight:700;color:var(--accent)"></span>
        <div class="search-wrap" style="max-width:240px;margin-left:auto">
          <input type="search" id="pend-search" placeholder="Buscar" />
        </div>
        <button type="button" class="btn btn-outline-dark btn-sm" id="pend-cal-btn">Alterar calendário…</button>
        <button type="button" class="btn btn-primary btn-sm" id="pend-marcar">Marcar pendentes desta lista</button>
        <button type="button" class="btn btn-ghost btn-sm" id="pend-refresh">Atualizar</button>
      </div>
      <div id="pend-list"></div>
    `);
    const reload = () => api("load_pendencias", parseInt($("#pend-ano").value, 10));
    $("#pend-refresh").addEventListener("click", reload);
    $("#pend-ano").addEventListener("change", reload);
    $("#pend-cal-btn").addEventListener("click", openCalendarioModal);
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
    const stats = $("#pend-stats");
    const cal = $("#pend-cal");
    if (stats) stats.textContent = `${nP} pendente(s) · ${nR} regular(es) · ${nP + nR} sócio(s)`;
    if (cal) cal.textContent = "Calendário: " + (data.calendario_texto || "");
    const list = $("#pend-list");
    if (!list) return;
    if (!items.length) {
      list.innerHTML = `<div class="empty-msg">${nP + nR === 0 ? "Nenhum sócio cadastrado." : "Nenhum pendente nesta lista."}</div>`;
      return;
    }
    list.innerHTML = items.map((s) => {
      const pills = (s.faltando || []).map((m) =>
        `<span class="pill warn">${m.toUpperCase()} !</span>`
      ).join(" ");
      return `
      <div class="card">
        <div class="card-head">
          <div class="card-info">
            <p class="card-name">${esc(s.nome_display)}${touchBadgeHtml(s)}</p>
            <p class="card-cpf">${esc(s.rotulo)} · CPF ${esc(formatCpf(s.cpf))}</p>
            <div class="pills" style="margin-top:4px">${pills}</div>
          </div>
          <div class="card-actions">
            <button type="button" class="btn btn-primary btn-sm" data-marcar="${s.person_id}">Marcar só os pendentes</button>
            <button type="button" class="btn btn-ghost btn-sm" data-ficha="${s.person_id}">Abrir ficha</button>
          </div>
        </div>
      </div>`;
    }).join("");
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
    if ($("#pend-search")) $("#pend-search").oninput = () => renderPendenciasList(data);
  }

  function openCalendarioModal() {
    const ano = parseInt($("#pend-ano")?.value || new Date().getFullYear(), 10);
    const cal = state.pendencias?.calendario || [];
    const backdrop = createModal(`
      <div class="modal-head">Calendário REAP ${ano}</div>
      <div class="modal-body">
        <p class="page-sub">Meses obrigatórios (aba Config da planilha).</p>
        ${presetButtons("cal-m")}
        <div class="month-grid">${monthChecksHtml("cal-m", cal)}</div>
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" data-modal-close="">Cancelar</button>
        <button type="button" class="btn btn-primary" id="cal-save">Salvar</button>
      </div>
    `);
    bindPresets(backdrop, "cal-m");
    backdrop.querySelector("#cal-save").addEventListener("click", () => {
      api("save_calendario", ano, selectedMonths(backdrop, "cal-m"));
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
    setPage(`
      <h1 class="page-title">Relatório de conformidade REAP</h1>
      <p class="page-sub">Somente administrador. CPF completo. Imprimir → PDF. Consulta pública continua mascarada.</p>
      <div class="form-panel" style="margin-top:10px">
        <div class="inline-row">
          <label>Ano</label>
          <input type="number" id="rel-ano" value="${ano}" />
          <label><input type="radio" name="rel-modo" value="diretoria" checked /> Diretoria (todos)</label>
          <label><input type="radio" name="rel-modo" value="individual" /> Comprovante individual</label>
        </div>
        <label>Buscar sócio (comprovante individual)</label>
        <input id="rel-busca" />
        <div class="form-actions">
          <button type="button" class="btn btn-primary" id="rel-gerar">Gerar e abrir HTML</button>
        </div>
      </div>
    `);
    $("#rel-gerar").addEventListener("click", () => {
      const modo = document.querySelector('input[name="rel-modo"]:checked')?.value || "diretoria";
      api("generate_relatorio", parseInt($("#rel-ano").value, 10), modo, $("#rel-busca").value);
    });
  }

  function renderBackup() {
    const ultimo = state.bootstrap?.ultimo_backup_em || "Nunca";
    const pasta = state.bootstrap?.backup_root || "";
    setPage(`
      <h1 class="page-title">Backup local</h1>
      <p class="page-sub">Cópia CSV local. Não substitui a planilha na nuvem.</p>
      <div class="form-panel" style="margin-top:10px">
        <p style="margin:0 0 4px"><strong>Último backup:</strong> ${esc(ultimo)}</p>
        <p class="page-sub">Pasta: ${esc(pasta)}</p>
        <div class="form-actions">
          <button type="button" class="btn btn-primary" id="bk-run">Gerar backup agora</button>
          <button type="button" class="btn btn-outline-dark" id="bk-open">Abrir pasta de backups</button>
        </div>
        <div id="bk-list" style="margin-top:12px;font-size:12px"></div>
      </div>
    `);
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
    setPage(`
      <div><span class="page-title">Auditoria</span> <span class="page-meta" id="aud-hint">Carregando…</span></div>
      <div class="toolbar">
        <input type="search" id="aud-search" placeholder="Buscar" style="flex:0 1 260px;padding:6px 8px;border:1px solid var(--border)" />
        <button type="button" class="btn btn-ghost btn-sm" id="aud-refresh">Atualizar</button>
        <button type="button" class="btn btn-outline-dark btn-sm" id="aud-export">Exportar CSV</button>
      </div>
      <div id="aud-list"></div>
    `);
    $("#aud-refresh").addEventListener("click", () => api("load_auditoria"));
    $("#aud-search")?.addEventListener("input", () => renderAuditoriaList(state.auditoria));
    $("#aud-export").addEventListener("click", () => api("export_auditoria"));
    api("load_auditoria");
  }

  function renderAuditoriaList(eventos) {
    state.auditoria = eventos || [];
    const q = $("#aud-search")?.value || "";
    api("filter_auditoria_local", state.auditoria, q).then((r) => {
      const items = r.ok ? r.data : state.auditoria;
      const hint = $("#aud-hint");
      if (hint) hint.textContent = `${items.length} registro(s) · aba Auditoria da planilha`;
      const list = $("#aud-list");
      if (!list) return;
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

  function renderAtalhos() {
    const ano = new Date().getFullYear();
    setPage(`
      <h1 class="page-title">Config.Atalhos</h1>
      <p class="page-sub">Automações em lote — poucas chamadas à planilha, sem marcar mês a mês.</p>

      <div class="atalho-card">
        <h3>1) Lote com REAP já marcado</h3>
        <p class="desc">Cadastra vários sócios de uma vez e já deixa os meses pagos no ano escolhido (ex.: março a outubro).</p>
        <div class="inline-row">
          <label>Ano</label>
          <input type="number" id="at1-ano" value="${ano}" />
        </div>
        ${presetButtons("m1")}
        <div class="month-grid">${monthChecksHtml("m1", MAR_OUT)}</div>
        <button type="button" class="btn btn-primary btn-sm" id="at-lote">Abrir lote com meses marcados…</button>
      </div>

      <div class="atalho-card">
        <h3>2) Marcar meses nos sócios já cadastrados</h3>
        <p class="desc">Liga o intervalo no ano para todos, ou só os da busca atual. Não apaga meses já pagos, a menos que substitua o ano.</p>
        <div class="inline-row">
          <label>Ano</label>
          <input type="number" id="at2-ano" value="${ano}" />
          <label><input type="checkbox" id="at2-busca" /> Só quem aparece na busca da lista</label>
          <label><input type="checkbox" id="at2-sub" /> Substituir o ano</label>
        </div>
        ${presetButtons("m2")}
        <div class="month-grid">${monthChecksHtml("m2", MAR_OUT)}</div>
        <button type="button" class="btn btn-primary btn-sm" id="at-massa">Aplicar marcação em massa</button>
      </div>

      <div class="atalho-card">
        <h3>3) Copiar REAP de um ano para outro</h3>
        <p class="desc">Leva os 12 meses já marcados (ex.: 2025 → 2026). Cria o ano novo se ainda não existir.</p>
        <div class="inline-row">
          <label>De</label>
          <input type="number" id="at3-de" value="${ano - 1}" />
          <label>para</label>
          <input type="number" id="at3-para" value="${ano}" />
          <label><input type="checkbox" id="at3-busca" /> Só a busca da lista</label>
        </div>
        <button type="button" class="btn btn-primary btn-sm" id="at-copiar">Copiar ano</button>
      </div>
      <p class="page-sub">Evite clicar várias vezes enquanto o rodapé disser “Marcando…” ou “Copiando…”.</p>
    `);
    bindPresets(content, "m1");
    bindPresets(content, "m2");

    $("#at-lote").addEventListener("click", () => {
      const meses = selectedMonths(content, "m1");
      if (!meses.length) { toast("Escolha os meses (ex.: Mar → Out) antes de abrir o lote."); return; }
      openLoteModal({ ano: parseInt($("#at1-ano").value, 10), meses });
    });

    $("#at-massa").addEventListener("click", async () => {
      const mesesOn = selectedMonths(content, "m2");
      if (!mesesOn.length) { toast("Escolha pelo menos um mês."); return; }
      const ids = $("#at2-busca").checked ? filteredPessoas().map((p) => p.id) : null;
      const n = ids ? ids.length : state.pessoas.length;
      if (!n) { toast("Nenhum sócio para aplicar."); return; }
      const substituir = $("#at2-sub").checked;
      const anoN = parseInt($("#at2-ano").value, 10);
      if (!(await confirmModal("Confirmar", `Marcar ${mesesOn.map((m) => m.toUpperCase()).join(", ")} em ${anoN} para ${n} sócio(s)?`))) return;
      api("marcar_meses_massa", anoN, mesesOn, ids, substituir);
    });

    $("#at-copiar").addEventListener("click", async () => {
      const a = parseInt($("#at3-de").value, 10);
      const b = parseInt($("#at3-para").value, 10);
      const ids = $("#at3-busca").checked ? filteredPessoas().map((p) => p.id) : null;
      const n = ids ? ids.length : state.pessoas.length;
      if (!n) { toast("Nenhum sócio para copiar."); return; }
      if (!(await confirmModal("Confirmar", `Copiar meses de ${a} para ${b} em ${n} sócio(s)?`))) return;
      api("copiar_ano", a, b, ids);
    });
  }

  function renderLista() {
    setPage(`
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
    `);
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
      list.innerHTML = `<div class="empty-msg">${state.pessoas.length ? "Nenhum sócio encontrado." : "Carregando…"}</div>`;
      if (!state.pessoas.length) loadPessoas();
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
    const backdrop = createModal(`
      <div class="modal-head">QR Code</div>
      <div class="modal-body qr-preview">
        <img id="qr-img" src="${r.data.image}" alt="QR" />
      </div>
      <div class="modal-foot">
        <button type="button" class="btn btn-outline-dark" id="qr-print">Imprimir</button>
        <button type="button" class="btn btn-primary" data-modal-close="ok">Fechar</button>
      </div>
    `);
    backdrop.querySelector("#qr-print").addEventListener("click", async () => {
      const pr = await api("print_qr", kind, personId || "");
      if (pr.ok) toast("QR aberto no navegador para imprimir.");
      else toast(pr.error || "Falha ao abrir impressão do QR.");
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
        // Sempre confia na planilha (evita contador preso em "agora").
        state.pessoas = (r.data || []).map((p, i) => ({ ...p, _idx: i }));
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
      if (r.ok && r.data && r.data.person_id) {
        // Atualiza o contador na hora (sem esperar a planilha).
        const p = state.pessoas.find((x) => x.id === r.data.person_id);
        if (p) {
          p.ultimo_toggle_label = "agora";
          p.ultimo_toggle_em = nowLocalStamp();
          if (state.screen === "admin") renderAdminList();
          if (state.screen === "lista") renderListaCards();
        }
        if (state.screen === "pendencias") {
          const anoEl = $("#pend-ano");
          if (anoEl) api("load_pendencias", parseInt(anoEl.value, 10));
        }
      } else if (!r.ok) {
        toast(r.error || "Não foi possível marcar o mês.");
        loadPessoas();
      }
    });
    AppEvents.on("ano_added", (r) => {
      if (r.ok) loadPessoas();
      else toast(r.error);
    });
    AppEvents.on("lote_saved", (r) => {
      const box = state.loteBackdrop;
      const saveBtn = box && box.querySelector("#l-save");
      const statusEl = box && box.querySelector("#l-status");
      if (r.ok) {
        const d = r.data || {};
        const nOk = d.ok ?? d.criados ?? 0;
        const erros = d.erros || [];
        toast(`Lote: ${nOk} cadastrado(s)${erros.length ? ` · ${erros.length} recusado(s)` : ""}.`);
        if (erros.length) toast(erros.slice(0, 4).join(" "));
        if (nOk > 0) {
          try { localStorage.removeItem("sinapesc_lote_draft"); } catch (_e) {}
          if (box) box._close(true);
          state.loteBackdrop = null;
          loadPessoas();
        } else {
          if (statusEl) statusEl.textContent = erros.slice(0, 6).join(" ") || "Ninguém foi cadastrado. Confira CPF e nomes.";
          if (saveBtn) saveBtn.disabled = false;
        }
      } else {
        toast(r.error || "Erro no lote.");
        if (statusEl) statusEl.textContent = r.error || "Erro. Seus dados continuam nesta janela.";
        if (saveBtn) saveBtn.disabled = false;
      }
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
        toast(`Atualizados: ${r.data?.atualizados ?? "?"} · criados: ${r.data?.criados ?? 0}`);
        if (state.screen === "pendencias") api("load_pendencias", parseInt($("#pend-ano")?.value, 10));
        else loadPessoas();
      } else toast(r.error);
    });
    AppEvents.on("copia_ok", (r) => {
      if (r.ok) {
        toast(`Copiados: ${r.data?.ok ?? 0} · pulados: ${r.data?.pulados ?? 0}`);
        loadPessoas();
      } else toast(r.error);
    });
    AppEvents.on("relatorio", (r) => {
      if (r.ok && r.data?.path) {
        api("open_path", r.data.path);
        toast("Relatório aberto no navegador para imprimir.");
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
    AppEvents.on("auditoria_export", (r) => {
      if (r.ok) {
        toast(`CSV: ${r.data?.path}`);
        api("open_path", r.data.path);
      } else toast(r.error);
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
