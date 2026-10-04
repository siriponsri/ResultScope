(() => {
  const loginForm = document.getElementById("admin-login-form");
  const loginError = document.getElementById("admin-login-error");
  const providerList = document.getElementById("provider-list");
  const status = document.getElementById("admin-status");
  let csrfToken = "";

  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  const request = async (url, options = {}) => {
    const headers = { ...(options.headers || {}) };
    if (csrfToken) headers["X-CSRF-Token"] = csrfToken;
    const response = await fetch(url, { credentials: "same-origin", ...options, headers });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.message || "The request failed.");
    return body;
  };

  loginForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    loginError.textContent = "Checking credentials...";
    const form = new FormData(loginForm);
    try {
      const result = await request("/api/v1/admin/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: form.get("username"), password: form.get("password") }) });
      csrfToken = result.csrf_token;
      window.location.assign("/admin/settings");
    } catch (error) { loginError.textContent = error.message; }
  });

  const providerCard = (slot, row, catalog) => {
    const options = Object.entries(catalog).filter(([, item]) => item.kind === (slot === "ocr" ? "ocr" : slot === "systemone" ? "systemone" : "llm")).map(([id, item]) => `<option value="${escape(id)}" ${id === row.provider_id ? "selected" : ""}>${escape(item.label)} (${escape(id)})</option>`).join("");
    return `<article class="provider-card" data-slot="${escape(slot)}"><div><h2>${escape(row.label)}</h2><small>${escape(row.note)} Endpoint: ${escape(row.endpoint)}. Key: ${row.configured ? "configured" : "not configured"}. ${row.shadow_mode ? "shadow-only" : ""}</small></div><div class="provider-grid"><label>Provider<select data-field="provider_id">${options}</select></label><label>Model<input data-field="model" value="${escape(row.model)}" autocomplete="off"></label><label>Timeout (seconds)<input data-field="timeout_seconds" type="number" min="1" max="300" value="${escape(row.timeout_seconds)}"></label><label>Replace key<input data-field="api_key" type="password" placeholder="Leave blank to keep the current key" autocomplete="new-password"></label></div><div class="provider-actions"><label><input data-field="enabled" type="checkbox" ${row.enabled ? "checked" : ""}> enabled</label><button type="button" class="secondary-button" data-action="test">Test with mock</button><button type="button" class="secondary-button" data-action="clear">Delete key</button></div></article>`;
  };

  const load = async () => {
    if (!providerList) return;
    const token = await request("/api/v1/admin/csrf"); csrfToken = token.csrf_token;
    const data = await request("/api/v1/admin/config");
    providerList.innerHTML = Object.entries(data.providers).map(([slot, row]) => providerCard(slot, row, data.catalog)).join("");
    providerList.querySelectorAll("[data-action='test']").forEach((button) => button.addEventListener("click", async () => {
      const slot = button.closest("[data-slot]").dataset.slot; button.disabled = true;
      try { const result = await request(`/api/v1/admin/providers/${slot}/test`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ live: false }) }); status.textContent = result.message; } catch (error) { status.textContent = error.message; } finally { button.disabled = false; }
    }));
    providerList.querySelectorAll("[data-action='clear']").forEach((button) => button.addEventListener("click", () => { button.closest("[data-slot]").querySelector("[data-field='api_key']").value = ""; button.closest("[data-slot]").dataset.clear = "true"; status.textContent = "Save settings to confirm key deletion."; }));
  };

  document.getElementById("admin-logout")?.addEventListener("click", async () => { try { await request("/api/v1/admin/logout", { method: "POST" }); } finally { window.location.assign("/admin/login"); } });
  document.getElementById("admin-save")?.addEventListener("click", async () => {
    const providers = {};
    providerList?.querySelectorAll("[data-slot]").forEach((card) => {
      const value = (field) => card.querySelector(`[data-field='${field}']`);
      providers[card.dataset.slot] = {
        provider_id: value("provider_id").value,
        enabled: value("enabled").checked,
        model: value("model").value,
        timeout_seconds: Number(value("timeout_seconds").value),
        api_key: value("api_key").value || null,
        clear_api_key: card.dataset.clear === "true",
      };
    });
    try {
      const result = await request("/api/v1/admin/config", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ providers }) });
      status.textContent = result.saved ? "Saved — no provider was called." : "The settings could not be saved.";
      await load();
    } catch (error) { status.textContent = error.message; }
  });
  if (providerList) load().catch((error) => { status.textContent = error.message; });
})();
