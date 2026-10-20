// ServiceOps Portal UI — vanilla JS SPA, hash-routed.

const API_BASE = "http://localhost:8000";
const TOKEN_KEY = "serviceops_token";
const REQUEST_TYPES = ["FIREWALL", "SSL", "SFTP", "SERVER_ACCESS", "DNS"];
const REQUEST_STATUSES = ["SUBMITTED", "APPROVED", "REJECTED", "COMPLETED"];
const ROLES = ["ADMIN", "APPROVER", "OPERATOR", "USER"];

// ---------- helpers ----------

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }

function decodeJwt(token) {
  try {
    const payload = token.split(".")[1];
    const b64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = b64 + "==".slice(0, (4 - (b64.length % 4)) % 4);
    return JSON.parse(atob(padded));
  } catch (e) { return null; }
}

function currentRole() {
  const t = getToken();
  if (!t) return null;
  const p = decodeJwt(t);
  return p ? p.role : null;
}

function toast(msg, isError) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.style.background = isError ? "#b91c1c" : "#1f2937";
  el.hidden = false;
  setTimeout(() => { el.hidden = true; }, 2500);
}

async function apiFetch(path, opts = {}) {
  const headers = opts.headers ? { ...opts.headers } : {};
  const token = getToken();
  if (token && !headers.Authorization) headers.Authorization = "Bearer " + token;

  let body = opts.body;
  if (body && opts.form) {
    const p = new URLSearchParams();
    for (const k of Object.keys(body)) p.append(k, body[k]);
    body = p.toString();
    headers["Content-Type"] = "application/x-www-form-urlencoded";
  } else if (body && typeof body === "object") {
    body = JSON.stringify(body);
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(API_BASE + path, {
    method: opts.method || "GET",
    headers,
    body: body || undefined,
  });

  if (res.status === 401) {
    clearToken();
    if (location.hash !== "#/login") location.hash = "#/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    let detail = res.statusText;
    try { const j = await res.json(); detail = j.detail || JSON.stringify(j); } catch (e) {}
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  if (res.status === 204) return null;
  return res.json();
}

function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  if (attrs) {
    for (const k of Object.keys(attrs)) {
      if (k === "class") node.className = attrs[k];
      else if (k === "html") node.innerHTML = attrs[k];
      else if (k.startsWith("on") && typeof attrs[k] === "function") {
        node.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
      } else if (k === "hidden" && attrs[k]) {
        node.hidden = true;
      } else {
        node.setAttribute(k, attrs[k]);
      }
    }
  }
  for (const c of children) {
    if (c == null || c === false) continue;
    node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  }
  return node;
}

function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

// ---------- header / auth ----------

function updateHeader() {
  const token = getToken();
  const header = document.getElementById("app-header");
  const userLabel = document.getElementById("user-label");
  const navUsers = document.getElementById("nav-users");
  if (!token) { header.hidden = true; return; }
  header.hidden = false;
  const p = decodeJwt(token) || {};
  userLabel.textContent = (p.sub || "") + " (" + (p.role || "") + ")";
  navUsers.hidden = p.role !== "ADMIN";
}

async function doLogout() {
  try { await apiFetch("/logout", { method: "POST" }); } catch (e) {}
  clearToken();
  location.hash = "#/login";
}

// ---------- screens ----------

function renderLogin(view) {
  clear(view);
  const card = el("div", { class: "card" });
  card.appendChild(el("h2", null, "Sign in"));
  const err = el("div", { class: "error", id: "login-err", hidden: true });
  card.appendChild(err);
  const form = el("form", { onsubmit: onSubmit });
  form.appendChild(el("label", null, "Username", el("input", { name: "username", required: true, autocomplete: "username" })));
  form.appendChild(el("label", null, "Password", el("input", { name: "password", type: "password", required: true, autocomplete: "current-password" })));
  form.appendChild(el("button", { type: "submit" }, "Sign in"));
  card.appendChild(form);
  card.appendChild(el("div", { class: "muted", style: "margin-top:12px;" },
    el("a", { href: "#/signup" }, "Create an account")));
  view.appendChild(card);

  async function onSubmit(ev) {
    ev.preventDefault();
    const fd = new FormData(form);
    err.hidden = true;
    try {
      const data = await apiFetch("/login", {
        method: "POST",
        form: true,
        body: { username: fd.get("username"), password: fd.get("password") },
      });
      setToken(data.access_token);
      location.hash = "#/dashboard";
    } catch (e) {
      err.textContent = e.message;
      err.hidden = false;
    }
  }
}

function renderSignup(view) {
  clear(view);
  const card = el("div", { class: "card" });
  card.appendChild(el("h2", null, "Create account"));
  const err = el("div", { class: "error", id: "signup-err", hidden: true });
  card.appendChild(err);
  const form = el("form", { onsubmit: onSubmit });
  form.appendChild(el("label", null, "Username", el("input", { name: "username", required: true, autocomplete: "username", minlength: "3" })));
  form.appendChild(el("label", null, "Password", el("input", { name: "password", type: "password", required: true, autocomplete: "new-password", minlength: "6" })));
  form.appendChild(el("button", { type: "submit" }, "Sign up"));
  card.appendChild(form);
  card.appendChild(el("div", { class: "muted", style: "margin-top:12px;" },
    el("a", { href: "#/login" }, "Back to sign in")));
  view.appendChild(card);

  async function onSubmit(ev) {
    ev.preventDefault();
    const fd = new FormData(form);
    err.hidden = true;
    try {
      await apiFetch("/signup", {
        method: "POST",
        body: { username: fd.get("username"), password: fd.get("password") },
      });
      toast("Account created — please sign in");
      location.hash = "#/login";
    } catch (e) {
      err.textContent = e.message;
      err.hidden = false;
    }
  }
}

async function renderDashboard(view) {
  clear(view);
  view.appendChild(el("h1", null, "Dashboard"));
  let data;
  try { data = await apiFetch("/dashboard"); }
  catch (e) { view.appendChild(el("div", { class: "error" }, e.message)); return; }

  const tiles = el("div", { class: "tiles" });
  for (const k of ["total_requests", "submitted_requests", "approved_requests", "rejected_requests", "completed_requests"]) {
    const label = k.replace("_requests", "").replace("_", " ");
    tiles.appendChild(el("div", { class: "tile" },
      el("div", { class: "num" }, String(data[k] ?? 0)),
      el("div", { class: "lbl" }, label),
    ));
  }
  view.appendChild(tiles);

  const card = el("div", { class: "card" });
  card.appendChild(el("h2", null, "Requests by type"));
  const tbl = el("table");
  tbl.appendChild(el("thead", null, el("tr", null, el("th", null, "Type"), el("th", null, "Count"))));
  const tbody = el("tbody");
  if (!data.requests_by_type || data.requests_by_type.length === 0) {
    tbody.appendChild(el("tr", null, el("td", { colspan: "2", class: "muted" }, "No data")));
  } else {
    for (const r of data.requests_by_type) {
      tbody.appendChild(el("tr", null, el("td", null, r.request_type), el("td", null, String(r.count))));
    }
  }
  tbl.appendChild(tbody);
  card.appendChild(tbl);
  view.appendChild(card);
}

async function renderRequestsList(view) {
  clear(view);
  view.appendChild(el("h1", null, "Requests"));

  const toolbar = el("div", { class: "toolbar" });
  const statusSel = el("select", { id: "f-status" },
    el("option", { value: "" }, "All statuses"),
    ...REQUEST_STATUSES.map(s => el("option", { value: s }, s)),
  );
  const typeSel = el("select", { id: "f-type" },
    el("option", { value: "" }, "All types"),
    ...REQUEST_TYPES.map(t => el("option", { value: t }, t)),
  );
  const refresh = el("button", { class: "secondary", onclick: load }, "Apply");
  const newBtn = el("a", { href: "#/requests/new", class: "btn" }, "+ New Request");
  toolbar.appendChild(el("label", null, "Status", statusSel));
  toolbar.appendChild(el("label", null, "Type", typeSel));
  toolbar.appendChild(refresh);
  toolbar.appendChild(newBtn);
  view.appendChild(toolbar);

  const card = el("div", { class: "card" });
  const tbl = el("table");
  tbl.appendChild(el("thead", null, el("tr", null,
    el("th", null, "ID"), el("th", null, "Title"), el("th", null, "Type"),
    el("th", null, "Status"), el("th", null, "Created"),
  )));
  const tbody = el("tbody");
  tbl.appendChild(tbody);
  card.appendChild(tbl);
  view.appendChild(card);

  async function load() {
    clear(tbody);
    const q = new URLSearchParams();
    if (statusSel.value) q.set("status", statusSel.value);
    if (typeSel.value) q.set("request_type", typeSel.value);
    const qs = q.toString();
    let data;
    try { data = await apiFetch("/requests" + (qs ? "?" + qs : "")); }
    catch (e) { tbody.appendChild(el("tr", null, el("td", { colspan: "5", class: "error" }, e.message))); return; }
    if (!data.items || data.items.length === 0) {
      tbody.appendChild(el("tr", null, el("td", { colspan: "5", class: "muted" }, "No requests")));
      return;
    }
    for (const r of data.items) {
      tbody.appendChild(el("tr", null,
        el("td", null, String(r.id)),
        el("td", null, el("a", { href: "#/requests/" + r.id }, r.title)),
        el("td", null, r.request_type),
        el("td", null, el("span", { class: "badge badge-" + r.status }, r.status)),
        el("td", null, (r.created_date || "").slice(0, 19).replace("T", " ")),
      ));
    }
  }
  load();
}

async function renderRequestNew(view) {
  clear(view);
  view.appendChild(el("h1", null, "New Request"));
  const card = el("div", { class: "card" });
  const err = el("div", { class: "error", hidden: true });
  card.appendChild(err);
  const form = el("form", { onsubmit: onSubmit });
  form.appendChild(el("label", null, "Title", el("input", { name: "title", required: true, maxlength: "255" })));
  form.appendChild(el("label", null, "Description", el("textarea", { name: "description" })));
  const typeSel = el("select", { name: "request_type", required: true },
    ...REQUEST_TYPES.map(t => el("option", { value: t }, t)),
  );
  form.appendChild(el("label", null, "Type", typeSel));
  form.appendChild(el("div", { class: "actions" },
    el("button", { type: "submit" }, "Create"),
    el("a", { href: "#/requests", class: "btn secondary" }, "Cancel"),
  ));
  card.appendChild(form);
  view.appendChild(card);

  async function onSubmit(ev) {
    ev.preventDefault();
    const fd = new FormData(form);
    err.hidden = true;
    try {
      const r = await apiFetch("/requests", {
        method: "POST",
        body: {
          title: fd.get("title"),
          description: fd.get("description") || null,
          request_type: fd.get("request_type"),
        },
      });
      location.hash = "#/requests/" + r.id;
    } catch (e) {
      err.textContent = e.message; err.hidden = false;
    }
  }
}

async function renderRequestDetail(view, id) {
  clear(view);
  view.appendChild(el("h1", null, "Request #" + id));
  const card = el("div", { class: "card" });
  view.appendChild(card);

  let r;
  try { r = await apiFetch("/requests/" + id); }
  catch (e) { card.appendChild(el("div", { class: "error" }, e.message)); return; }

  const role = currentRole();
  const canApprove = role === "ADMIN" || role === "APPROVER";
  const canDelete = role === "ADMIN" || role === "OPERATOR";

  const meta = el("table");
  meta.appendChild(el("tbody", null,
    row("Title", r.title),
    row("Type", r.request_type),
    row("Status", el("span", { class: "badge badge-" + r.status }, r.status)),
    row("Description", r.description || el("span", { class: "muted" }, "(none)")),
    row("Created by", "user #" + r.created_by),
    row("Created", (r.created_date || "").slice(0, 19).replace("T", " ")),
    row("Updated", (r.updated_date || "").slice(0, 19).replace("T", " ")),
  ));
  card.appendChild(meta);

  const actions = el("div", { class: "actions", style: "margin-top:16px;" });

  if (canApprove && r.status === "SUBMITTED") {
    actions.appendChild(el("button", { class: "success", onclick: () => doApprove(r.id) }, "Approve"));
    actions.appendChild(el("button", { class: "danger", onclick: () => doReject(r.id) }, "Reject"));
  }
  if (canDelete) {
    actions.appendChild(el("button", { class: "secondary", onclick: () => doDelete(r.id) }, "Delete"));
  }
  actions.appendChild(el("a", { href: "#/requests", class: "btn secondary" }, "Back"));
  card.appendChild(actions);

  function row(k, v) {
    return el("tr", null, el("th", { style: "width:160px;" }, k), el("td", null, v));
  }

  async function doApprove(rid) {
    const comments = prompt("Approval comments (optional):") || "";
    try { await apiFetch("/requests/" + rid + "/approve", { method: "POST", body: { comments } }); toast("Approved"); renderRequestDetail(view, id); }
    catch (e) { toast(e.message, true); }
  }
  async function doReject(rid) {
    const comments = prompt("Rejection comments (optional):") || "";
    try { await apiFetch("/requests/" + rid + "/reject", { method: "POST", body: { comments } }); toast("Rejected"); renderRequestDetail(view, id); }
    catch (e) { toast(e.message, true); }
  }
  async function doDelete(rid) {
    if (!confirm("Delete request #" + rid + "?")) return;
    try { await apiFetch("/requests/" + rid, { method: "DELETE" }); toast("Deleted"); location.hash = "#/requests"; }
    catch (e) { toast(e.message, true); }
  }
}

async function renderUsers(view) {
  clear(view);
  if (currentRole() !== "ADMIN") {
    view.appendChild(el("div", { class: "error" }, "Admin only."));
    return;
  }
  view.appendChild(el("h1", null, "Users"));

  const card = el("div", { class: "card" });
  card.appendChild(el("h2", null, "Create user"));
  const err = el("div", { class: "error", hidden: true });
  card.appendChild(err);
  const form = el("form", { class: "row-form", onsubmit: onCreate });
  form.appendChild(el("label", null, "Username", el("input", { name: "username", required: true })));
  form.appendChild(el("label", null, "Password", el("input", { name: "password", type: "password", required: true })));
  const roleSel = el("select", { name: "role", required: true },
    ...ROLES.map(r => el("option", { value: r }, r)),
  );
  form.appendChild(el("label", null, "Role", roleSel));
  form.appendChild(el("button", { type: "submit" }, "Create"));
  card.appendChild(form);
  view.appendChild(card);

  const listCard = el("div", { class: "card" });
  const tbl = el("table");
  tbl.appendChild(el("thead", null, el("tr", null,
    el("th", null, "ID"), el("th", null, "Username"), el("th", null, "Role"),
    el("th", null, "Created"), el("th", null, ""),
  )));
  const tbody = el("tbody");
  tbl.appendChild(tbody);
  listCard.appendChild(tbl);
  view.appendChild(listCard);

  async function load() {
    clear(tbody);
    let data;
    try { data = await apiFetch("/users"); }
    catch (e) { tbody.appendChild(el("tr", null, el("td", { colspan: "5", class: "error" }, e.message))); return; }
    if (!data || data.length === 0) {
      tbody.appendChild(el("tr", null, el("td", { colspan: "5", class: "muted" }, "No users")));
      return;
    }
    for (const u of data) {
      tbody.appendChild(el("tr", null,
        el("td", null, String(u.id)),
        el("td", null, u.username),
        el("td", null, u.role),
        el("td", null, (u.created_date || "").slice(0, 19).replace("T", " ")),
        el("td", null, el("button", { class: "danger", onclick: () => doDelete(u.id, u.username) }, "Delete")),
      ));
    }
  }

  async function onCreate(ev) {
    ev.preventDefault();
    const fd = new FormData(form);
    err.hidden = true;
    try {
      await apiFetch("/users", {
        method: "POST",
        body: {
          username: fd.get("username"),
          password: fd.get("password"),
          role: fd.get("role"),
        },
      });
      form.reset();
      toast("User created");
      load();
    } catch (e) { err.textContent = e.message; err.hidden = false; }
  }

  async function doDelete(uid, uname) {
    if (!confirm("Delete user " + uname + "?")) return;
    try { await apiFetch("/users/" + uid, { method: "DELETE" }); toast("Deleted"); load(); }
    catch (e) { toast(e.message, true); }
  }

  load();
}

// ---------- router ----------

async function route() {
  updateHeader();
  const view = document.getElementById("view");
  const hash = location.hash || "#/dashboard";
  if (!getToken() && hash !== "#/login" && hash !== "#/signup") { location.hash = "#/login"; return; }
  if (getToken() && (hash === "#/login" || hash === "#/signup")) { location.hash = "#/dashboard"; return; }

  if (hash === "#/login") return renderLogin(view);
  if (hash === "#/signup") return renderSignup(view);
  if (hash === "#/dashboard" || hash === "" || hash === "#") return renderDashboard(view);
  if (hash === "#/requests") return renderRequestsList(view);
  if (hash === "#/requests/new") return renderRequestNew(view);
  if (hash.startsWith("#/requests/")) return renderRequestDetail(view, hash.slice("#/requests/".length));
  if (hash === "#/users") return renderUsers(view);
  view.appendChild(el("div", { class: "error" }, "Unknown route: " + hash));
}

window.addEventListener("hashchange", route);
window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("logout-btn").addEventListener("click", doLogout);
  route();
});
