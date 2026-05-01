// fava-quick-entry — Fava extension JS module.
//
// Single handwritten ES module. No build step, no npm. Loaded by Fava when
// has_js_module = True via /<bfile>/extension_js_module/FavaQuickEntry.js.
// Colors come from Fava's own CSS variables (which use `light-dark()`), so
// the form follows the user's theme.

const STYLE_ID = "qe-style";
const STYLES = `
.qe-app { color: var(--text-color); }
.qe-app input, .qe-app textarea, .qe-app button { font: inherit; box-sizing: border-box; }
.qe-app input[type=text], .qe-app input[type=date] {
  width: 100%; min-height: 40px; padding: 8px 12px;
  border: 1px solid var(--border); border-radius: 8px;
  background: var(--background); color: var(--text-color);
}
.qe-app input[type=text]:focus, .qe-app input[type=date]:focus {
  outline: 2px solid var(--button-background); outline-offset: -1px;
}
.qe-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; max-width: 720px; margin: 0 auto; padding: 0 12px 96px; }
.qe-card { background: var(--background); border: 1px solid var(--border); border-radius: 12px; padding: 14px; }
.qe-label { font-size: 12px; color: var(--text-color-lighter); margin-bottom: 6px; display: block; }
.qe-row { margin-bottom: 12px; }
.qe-section { font-size: 13px; font-weight: 600; color: var(--text-color); margin: 14px 0 8px; padding-top: 10px; border-top: 1px solid var(--border-lighter); }
.qe-section:first-child { border-top: none; padding-top: 0; margin-top: 0; }
.qe-posting { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 80px) 36px; gap: 6px 8px; margin-bottom: 10px; align-items: center; }
.qe-posting > :first-child { grid-column: 1 / -1; }
.qe-mono { font-family: var(--font-family-monospaced); }
.qe-amount { text-align: right; }
.qe-rm { height: 40px; width: 40px; padding: 0; line-height: 1; font-size: 18px;
  border: 1px solid var(--border); border-radius: 8px; background: var(--background-darker); color: var(--text-color); cursor: pointer; }
.qe-rm:hover { background: var(--background-darkest); }
.qe-add { font-size: 13px; color: var(--link-color); background: transparent; border: none; padding: 6px 0; cursor: pointer; }
.qe-add:hover { text-decoration: underline; }
.qe-preview { width: 100%; box-sizing: border-box; background: var(--background-darker); color: var(--text-color); border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; font-family: var(--font-family-monospaced); font-size: 13px; line-height: 1.7; white-space: pre; overflow-x: auto; min-height: 140px; margin: 0; resize: vertical; }
.qe-preview:focus { outline: 2px solid var(--button-background); outline-offset: -1px; }
.qe-preview.is-edited { border-color: var(--link-color); }
.qe-preview-note { font-size: 11px; color: var(--text-color-lightest); margin-top: 6px; line-height: 1.5; }
.qe-preview-note .qe-reset { background: transparent; border: none; padding: 0; color: var(--link-color); cursor: pointer; font: inherit; text-decoration: underline; }
.qe-target-row { display: flex; align-items: center; gap: 8px; margin-top: 14px; flex-wrap: wrap; }
.qe-target-row > span:first-child { font-size: 13px; color: var(--text-color-lighter); }
.qe-pill { font-family: var(--font-family-monospaced); font-size: 12px; padding: 6px 10px; background: var(--background-darker); color: var(--text-color); border-radius: 6px; border: 1px solid var(--border); }
.qe-chip { font-size: 12px; padding: 6px 10px; background: transparent; color: var(--link-color); border: 1px solid var(--border); border-radius: 6px; cursor: pointer; min-height: 32px; }
.qe-chip:hover { background: var(--background-darker); }
.qe-status { font-size: 12px; padding: 8px 12px; border-radius: 6px; margin: 14px 0; min-height: 18px; border: 1px solid var(--border); background: var(--background-darker); color: var(--text-color); }
.qe-status.is-err { color: var(--diff-red); border-color: var(--diff-red); }
.qe-actions { display: flex; gap: 8px; margin-top: 4px; }
.qe-save { flex: 1; min-height: 44px; background: var(--button-background); color: var(--button-color); border: none; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; }
.qe-save:disabled { opacity: 0.5; cursor: not-allowed; }
.qe-save.is-saved { background: var(--diff-green); }
.qe-modal-bg { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: none; align-items: center; justify-content: center; z-index: 1000; }
.qe-modal-bg.show { display: flex; }
.qe-modal { background: var(--background); border: 1px solid var(--border); border-radius: 12px; padding: 16px; width: 90%; max-width: 380px; }
.qe-modal-title { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text-color); }
.qe-modal-help { font-size: 12px; color: var(--text-color-lightest); margin-bottom: 8px; }
.qe-modal-error { font-size: 12px; color: var(--diff-red); margin-bottom: 8px; min-height: 16px; }
.qe-file-row { padding: 10px 12px; text-align: left; font-family: var(--font-family-monospaced); font-size: 13px; border: 1px solid var(--border); border-radius: 8px; width: 100%; background: var(--background); color: var(--text-color); cursor: pointer; min-height: 40px; }
.qe-file-row:hover { background: var(--background-darker); }
.qe-modal-actions { display: flex; gap: 8px; margin-top: 12px; }
.qe-secondary { flex: 1; min-height: 40px; background: var(--background-darker); border: 1px solid var(--border); color: var(--text-color); border-radius: 8px; cursor: pointer; }
.qe-secondary:hover { background: var(--background-darkest); }
.qe-ac-wrap { position: relative; min-width: 0; }
.qe-ac-popup {
  display: none; position: absolute; top: 100%; left: 0; right: 0; z-index: 50;
  margin-top: 4px; background: var(--background); border: 1px solid var(--border); border-radius: 8px;
  max-height: 240px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
.qe-ac-popup.show { display: block; }
.qe-ac-row { padding: 8px 12px; cursor: pointer; font-family: var(--font-family-monospaced); font-size: 13px; color: var(--text-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.qe-ac-row.is-sel, .qe-ac-row:hover { background: var(--background-darker); }
`;

function injectStyles() {
  if (document.getElementById(STYLE_ID)) return;
  const s = document.createElement("style");
  s.id = STYLE_ID;
  s.textContent = STYLES;
  document.head.appendChild(s);
}

const LAST_TARGET_KEY = "fava-quick-entry:last-target";
function loadLastTarget() {
  try { return localStorage.getItem(LAST_TARGET_KEY) || ""; } catch { return ""; }
}
function saveLastTarget(t) {
  try { localStorage.setItem(LAST_TARGET_KEY, t || ""); } catch {}
}

function todayISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function emptyState() {
  return {
    date: todayISO(),
    payee: "",
    narration: "",
    postings: [
      { account: "", amount: "", currency: "USD" },
      { account: "", amount: "", currency: "USD" },
    ],
    target: "",
    files: [],
    accounts: [],
    payees: [],
  };
}

// Subsequence-aware fuzzy match. Returns score (lower = better) or null if no
// match. Prefix < substring < subsequence; ties broken by candidate length.
function fuzzyScore(query, candidate) {
  if (!query) return 0;
  const q = query.toLowerCase();
  const c = candidate.toLowerCase();
  if (c.startsWith(q)) return 0;
  if (c.includes(q)) return 1;
  let i = 0;
  for (let j = 0; j < c.length && i < q.length; j++) {
    if (c[j] === q[i]) i++;
  }
  return i === q.length ? 2 : null;
}

function fuzzyFilter(query, candidates, max = 12) {
  const scored = [];
  for (const cand of candidates) {
    const s = fuzzyScore(query, cand);
    if (s !== null) scored.push([s, cand]);
  }
  scored.sort((a, b) => a[0] - b[0] || a[1].length - b[1].length || a[1].localeCompare(b[1]));
  return scored.slice(0, max).map(x => x[1]);
}

function attachAutocomplete(input, popup, getCandidates) {
  let items = [];
  let selected = -1;
  let open = false;

  function render() {
    popup.innerHTML = "";
    items.forEach((it, idx) => {
      const row = document.createElement("div");
      row.className = "qe-ac-row" + (idx === selected ? " is-sel" : "");
      row.textContent = it;
      row.addEventListener("mousedown", (ev) => { ev.preventDefault(); commit(it); });
      row.addEventListener("mouseenter", () => {
        selected = idx;
        Array.from(popup.children).forEach((c, i) => c.classList.toggle("is-sel", i === idx));
      });
      popup.append(row);
    });
    popup.classList.toggle("show", open && items.length > 0);
  }

  function update() {
    items = fuzzyFilter(input.value, getCandidates());
    selected = items.length > 0 ? 0 : -1;
    open = true;
    render();
  }

  function commit(value) {
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    open = false;
    render();
  }

  input.addEventListener("focus", update);
  input.addEventListener("input", update);
  input.addEventListener("blur", () => { setTimeout(() => { open = false; render(); }, 100); });
  input.addEventListener("keydown", (ev) => {
    if (!open || items.length === 0) return;
    if (ev.key === "ArrowDown") { ev.preventDefault(); selected = (selected + 1) % items.length; render(); }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); selected = (selected - 1 + items.length) % items.length; render(); }
    else if (ev.key === "Enter" && selected >= 0) { ev.preventDefault(); commit(items[selected]); }
    else if (ev.key === "Escape") { open = false; render(); }
    else if (ev.key === "Tab" && selected >= 0) { commit(items[selected]); }
  });
}

function makeAutocomplete(inputProps, getCandidates) {
  const input = el("input", inputProps);
  const popup = el("div", { class: "qe-ac-popup" });
  const wrap = el("div", { class: "qe-ac-wrap" }, input, popup);
  attachAutocomplete(input, popup, getCandidates);
  return { input, wrap };
}

function el(tag, props, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (k === "class") node.className = v;
    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2).toLowerCase(), v);
    else if (v === true) node.setAttribute(k, "");
    else if (v != null && v !== false) node.setAttribute(k, v);
  }
  for (const c of children) {
    if (c == null || c === false) continue;
    node.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return node;
}

function mount(host, ctx) {
  const api = ctx.api;
  const state = emptyState();
  let previewTimer = null;

  function buildTx() {
    return {
      date: state.date,
      flag: "*",
      payee: state.payee,
      narration: state.narration,
      postings: state.postings.filter(p => p.account.trim()).map(p => ({
        account: p.account.trim(),
        amount: p.amount,
        currency: p.currency,
      })),
    };
  }

  function schedulePreview() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(updatePreview, 200);
  }

  async function updatePreview() {
    try {
      const r = await api.post("preview", buildTx());
      previewAuto = r.text || "";
      if (!previewEdited) previewEl.value = previewAuto;
      setStatus(r.ok, r.ok ? "bean-check: ok (preview)" : (r.error || "preview failed"));
    } catch (e) {
      setStatus(false, e.message);
    }
  }

  function setStatus(ok, msg) {
    statusEl.textContent = msg;
    statusEl.className = "qe-status" + (ok ? "" : " is-err");
    saveBtn.disabled = !ok;
  }

  // ---- form fields ----
  const dateInput = el("input", { type: "date", value: state.date });
  const payeeAuto = makeAutocomplete(
    { type: "text", placeholder: "who you paid (or who paid you)" },
    () => state.payees.map(p => p.name),
  );
  const payeeInput = payeeAuto.input;
  const narrationInput = el("input", { type: "text", placeholder: "optional" });

  const postingsList = el("div");
  const addPostingBtn = el("button", { class: "qe-add", type: "button" }, "+ posting");

  const previewEl = el("textarea", { class: "qe-preview qe-mono", spellcheck: "false", rows: "8" });
  let previewAuto = "";  // last auto-generated text; lets us detect manual edits
  let previewEdited = false;
  const resetBtn = el("button", { class: "qe-reset", type: "button" }, "reset to auto");
  const previewNote = el("div", { class: "qe-preview-note" },
    "You can edit this preview directly — saving will write exactly what's here. ",
    "Edits won't update the Basic fields above. ",
    resetBtn);

  function markEdited(edited) {
    previewEdited = edited;
    previewEl.classList.toggle("is-edited", edited);
    resetBtn.style.display = edited ? "" : "none";
  }
  markEdited(false);

  previewEl.addEventListener("input", () => {
    markEdited(previewEl.value !== previewAuto);
  });
  resetBtn.addEventListener("click", () => {
    previewEl.value = previewAuto;
    markEdited(false);
  });
  const targetPill = el("span", { class: "qe-pill" }, "—");
  const changeTargetBtn = el("button", { class: "qe-chip", type: "button" }, "change");
  const newFileBtn = el("button", { class: "qe-chip", type: "button" }, "new file");
  const statusEl = el("div", { class: "qe-status" }, "loading…");
  const saveBtn = el("button", { class: "qe-save", type: "button" }, "Save");

  const formCard = el("div", { class: "qe-card" },
    el("div", { class: "qe-section" }, "Basic"),
    el("div", { class: "qe-row" },
      el("label", { class: "qe-label" }, "Date"),
      dateInput),
    el("div", { class: "qe-row" },
      el("label", { class: "qe-label" }, "Payee"),
      payeeAuto.wrap),
    el("div", { class: "qe-row" },
      el("label", { class: "qe-label" }, "Narration"),
      narrationInput),
    el("div", { class: "qe-section" }, "Postings"),
    postingsList,
    addPostingBtn,
  );

  const previewCard = el("div", { class: "qe-card qe-preview-card" },
    el("div", { class: "qe-section" }, "Preview"),
    previewEl,
    previewNote,
    el("div", { class: "qe-target-row" },
      el("span", null, "→ writes to"),
      targetPill,
      changeTargetBtn,
      newFileBtn,
    ),
    statusEl,
    el("div", { class: "qe-actions" }, saveBtn),
  );

  // ---- modals ----
  const fileListEl = el("div", { style: "display: flex; flex-direction: column; gap: 6px; max-height: 280px; overflow-y: auto;" });
  const targetCancel = el("button", { class: "qe-secondary", type: "button" }, "Cancel");
  const targetModal = el("div", { class: "qe-modal-bg" },
    el("div", { class: "qe-modal" },
      el("div", { class: "qe-modal-title" }, "Choose target file"),
      fileListEl,
      el("div", { class: "qe-modal-actions" }, targetCancel),
    ));

  const newFilePath = el("input", { type: "text", placeholder: "e.g. 2025/06.beancount" });
  const newFileError = el("div", { class: "qe-modal-error" });
  const newFileCancel = el("button", { class: "qe-secondary", type: "button" }, "Cancel");
  const newFileCreate = el("button", { class: "qe-save", type: "button" }, "Create & use");
  const newFileModal = el("div", { class: "qe-modal-bg" },
    el("div", { class: "qe-modal" },
      el("div", { class: "qe-modal-title" }, "Create new file"),
      el("div", { class: "qe-row" }, newFilePath),
      el("div", { class: "qe-modal-help" }, "Will auto-add `include` to main.beancount"),
      newFileError,
      el("div", { class: "qe-modal-actions" }, newFileCancel, newFileCreate),
    ));

  // ---- mount ----
  host.innerHTML = "";
  host.classList.add("qe-app");
  host.append(
    el("div", { class: "qe-grid" }, formCard, previewCard),
    targetModal,
    newFileModal,
  );

  // ---- wire ----
  dateInput.addEventListener("input", async () => {
    state.date = dateInput.value;
    try {
      const sug = await api.get("suggest_target", { date: state.date });
      // Only auto-update target when a template is actually configured;
      // otherwise leave whatever the user picked alone.
      if (sug.ok && sug.template_configured && sug.target_file) {
        state.target = sug.target_file;
        targetPill.textContent = sug.target_file;
      }
    } catch {}
    schedulePreview();
  });
  payeeInput.addEventListener("input", () => { state.payee = payeeInput.value; schedulePreview(); });
  narrationInput.addEventListener("input", () => { state.narration = narrationInput.value; schedulePreview(); });

  addPostingBtn.addEventListener("click", () => {
    state.postings.push({ account: "", amount: "", currency: "USD" });
    renderPostings();
    schedulePreview();
  });

  changeTargetBtn.addEventListener("click", () => {
    fileListEl.innerHTML = "";
    for (const f of state.files) {
      const b = el("button", { class: "qe-file-row", type: "button" },
        f + (f === state.target ? "  ✓" : ""));
      b.addEventListener("click", () => {
        state.target = f;
        targetPill.textContent = f;
        saveLastTarget(f);
        targetModal.classList.remove("show");
      });
      fileListEl.append(b);
    }
    targetModal.classList.add("show");
  });
  targetCancel.addEventListener("click", () => targetModal.classList.remove("show"));

  newFileBtn.addEventListener("click", () => {
    newFilePath.value = "";
    newFileError.textContent = "";
    newFileModal.classList.add("show");
    setTimeout(() => newFilePath.focus(), 0);
  });
  newFileCancel.addEventListener("click", () => newFileModal.classList.remove("show"));
  newFileCreate.addEventListener("click", async () => {
    const path = newFilePath.value.trim();
    if (!path) return;
    try {
      const r = await api.post("files_create", { path });
      if (!r.ok) { newFileError.textContent = r.error || "create failed"; return; }
      const f = await api.get("files", {});
      state.files = f.files;
      state.target = path;
      targetPill.textContent = path;
      saveLastTarget(path);
      newFileModal.classList.remove("show");
    } catch (e) {
      newFileError.textContent = e.message;
    }
  });

  saveBtn.addEventListener("click", async () => {
    saveBtn.disabled = true;
    const original = saveBtn.textContent;
    try {
      const payload = { transaction: buildTx(), target_file: state.target };
      if (previewEdited) payload.raw_text = previewEl.value;
      const r = await api.post("save", payload);
      if (r.ok) {
        saveBtn.textContent = "Saved ✓";
        saveBtn.classList.add("is-saved");
        Object.assign(state, emptyState(), {
          files: state.files, accounts: state.accounts, payees: state.payees,
          target: state.target,
        });
        markEdited(false);
        syncDom();
        try {
          const p = await api.get("payees", {});
          state.payees = p.payees;
        } catch {}
        setTimeout(() => {
          saveBtn.textContent = original;
          saveBtn.classList.remove("is-saved");
          schedulePreview();
        }, 1500);
      } else {
        setStatus(false, r.error || "save failed");
        saveBtn.textContent = original;
        saveBtn.disabled = false;
      }
    } catch (e) {
      setStatus(false, e.message);
      saveBtn.textContent = original;
      saveBtn.disabled = false;
    }
  });

  function renderPostings() {
    postingsList.innerHTML = "";
    state.postings.forEach((p, i) => {
      const acctAuto = makeAutocomplete(
        { type: "text", value: p.account, placeholder: "Account", class: "qe-acct" },
        () => state.accounts,
      );
      const acct = acctAuto.input;
      acct.addEventListener("input", () => { state.postings[i].account = acct.value; schedulePreview(); });
      const amt = el("input", { type: "text", inputmode: "decimal", value: p.amount, placeholder: "0.00", class: "qe-mono qe-amount" });
      amt.addEventListener("input", () => { state.postings[i].amount = amt.value; schedulePreview(); });
      const cur = el("input", { type: "text", value: p.currency, placeholder: "USD", class: "qe-mono" });
      cur.addEventListener("input", () => { state.postings[i].currency = cur.value.toUpperCase(); schedulePreview(); });
      const rm = el("button", { class: "qe-rm", type: "button", title: "Remove posting" }, "×");
      rm.addEventListener("click", () => {
        state.postings.splice(i, 1);
        renderPostings();
        schedulePreview();
      });
      postingsList.append(el("div", { class: "qe-posting" }, acctAuto.wrap, amt, cur, rm));
    });
  }

  function syncDom() {
    dateInput.value = state.date;
    payeeInput.value = state.payee;
    narrationInput.value = state.narration;
    targetPill.textContent = state.target || "—";
    renderPostings();
  }

  // ---- bootstrap ----
  renderPostings();
  setStatus(true, "loading…");

  return (async () => {
    try {
      const [filesR, accountsR, payeesR] = await Promise.all([
        api.get("files", {}),
        api.get("accounts", {}),
        api.get("payees", {}),
      ]);
      state.files = filesR.files || [];
      state.accounts = accountsR.accounts || [];
      state.payees = payeesR.payees || [];
      state.target = filesR.default || "";
      let templateConfigured = false;
      try {
        const sug = await api.get("suggest_target", { date: state.date });
        if (sug.ok && sug.target_file) {
          state.target = sug.target_file;
          templateConfigured = !!sug.template_configured;
        }
      } catch {}
      // No template? fall back to whatever the user picked last.
      if (!templateConfigured) {
        const last = loadLastTarget();
        if (last && state.files.includes(last)) state.target = last;
      }
      targetPill.textContent = state.target || "—";
      schedulePreview();
    } catch (e) {
      setStatus(false, `setup failed: ${e.message}`);
    }
  })();
}

export default {
  onExtensionPageLoad(ctx) {
    const host = document.getElementById("qe-app");
    if (!host) return;
    injectStyles();
    mount(host, ctx);
  },
};
