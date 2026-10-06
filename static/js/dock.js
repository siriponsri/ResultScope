'use strict';
/* Assistant dock on every public page. Same conversation as /app; the page the visitor is
   viewing is sent as context. Shortcuts only navigate or prefill — the visitor confirms. */
(() => {
  if (document.body.dataset.noDock === 'true') return;
  const make = (tag, text, cls) => { const e = document.createElement(tag); if (text != null) e.textContent = text; if (cls) e.className = cls; return e; };
  const money = n => '฿' + new Intl.NumberFormat('en-US').format(n);
  let roles = [], online = null, open = false, busy = false, controller = null, loaded = false, launcher, panel, body, input, status, lastKey = '';

  function pageContext() {
    const ctx = { path: location.pathname.replace(/[^A-Za-z0-9/_-]/g, '').slice(0, 120) };
    const m = location.pathname.match(/^\/packages\/(P\d{2})$/); if (m) ctx.package_id = m[1];
    const ids = new URLSearchParams(location.search).get('ids'); if (location.pathname === '/compare' && ids) ctx.compare_ids = ids.split(',').filter(x => /^P\d{2}$/.test(x)).slice(0, 3);
    return ctx;
  }
  function contextLabel() {
    const c = pageContext();
    if (c.package_id) return 'Knows you are viewing ' + (document.querySelector('h1')?.textContent || c.package_id) + '.';
    if (c.compare_ids) return 'Knows you are comparing ' + c.compare_ids.length + ' packages.';
    if (c.path === '/packages') return 'Knows you are browsing health checks.';
    if (c.path === '/organizations') return 'Knows you are planning for an organization.';
    return 'Replies in your language. Not a diagnosis.';
  }
  function mark(id, name) { const m = make('span', (name || '?')[0], 'dot-mark ' + (id || '')); m.setAttribute('aria-hidden', 'true'); return m; }

  async function loadRoles() {
    try { roles = (await fetch('/api/business/dots').then(r => r.json())).dots.filter(d => d.enabled); } catch { roles = []; }
    try { online = (await fetch('/api/business/modes').then(r => r.json())).modes.assistant.mode === 'LIVE_MODEL'; } catch { online = null; }
    document.querySelectorAll('[data-dot-status]').forEach(n => { n.textContent = online ? 'Online' : 'Offline right now'; });
  }
  function buildLauncher() {
    launcher = make('button', null, 'dock-launch'); launcher.type = 'button'; launcher.setAttribute('aria-haspopup', 'dialog'); launcher.setAttribute('aria-expanded', 'false');
    const marks = make('span', null, 'marks'); (roles.length ? roles : [{ id: 'advisor', name: 'A' }]).forEach(r => marks.append(mark(r.id, r.name)));
    launcher.append(marks, make('span', 'Ask ResultScope'));
    launcher.addEventListener('click', () => toggle(true));
    document.body.append(launcher);
  }
  function buildPanel() {
    panel = make('section', null, 'dock'); panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'false'); panel.setAttribute('aria-labelledby', 'dock-title'); panel.hidden = true;
    const head = make('div', null, 'dock-head'), top = make('div', null, 'row'), h = make('h2', 'Ask ResultScope'); h.id = 'dock-title';
    const tools = make('div', null, 'row'); const full = make('a', 'Open workspace', 'small'); full.href = '/app'; full.style.color = '#d9c9ff';
    const close = make('button', '×', 'icon-btn'); close.type = 'button'; close.setAttribute('aria-label', 'Close assistant'); close.onclick = () => toggle(false);
    tools.append(full, close); top.append(h, tools);
    const rs = make('div', null, 'dock-roles');
    roles.forEach(r => { const c = make('span', null, 'role-chip on-night'), t = make('span'); t.append(document.createTextNode(r.name), make('small', r.role)); c.append(mark(r.id, r.name), t); rs.append(c); });
    head.append(top, rs, make('p', contextLabel(), 'dock-context'));
    body = make('div', null, 'dock-body'); body.setAttribute('aria-live', 'polite');
    const foot = make('div', null, 'dock-foot'), form = make('form');
    input = make('textarea', null, 'input'); input.rows = 1; input.maxLength = 4000; input.placeholder = 'Ask about a package, a report or a booking…'; input.setAttribute('aria-label', 'Message');
    const send = make('button', 'Send', 'btn primary sm'); send.type = 'submit';
    const stop = make('button', 'Stop', 'btn sm'); stop.type = 'button'; stop.hidden = true; stop.onclick = async () => { controller?.abort(); try { await RS.post('/stop'); } catch { } };
    form.append(input, stop, send);
    status = make('p', '', 'tiny muted'); status.setAttribute('role', 'status');
    foot.append(status, form);
    form.addEventListener('submit', e => { e.preventDefault(); ask(input.value, send, stop); });
    input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); } });
    panel.append(head, body, foot); document.body.append(panel);
    panel.addEventListener('keydown', e => { if (e.key === 'Escape') toggle(false); });
  }
  async function toggle(want) {
    open = want; panel.hidden = !want; launcher.hidden = want; launcher.setAttribute('aria-expanded', String(want));
    if (want) {
      input.focus();
      if (!loaded) { loaded = true; await refresh(true); }
    } else launcher.focus();
  }
  function empty() {
    const box = make('div', null, 'dock-empty');
    if (online === false) box.append(make('p', 'AI replies are switched off right now. You can still browse, book and send a message to our team.', 'callout warn small'));
    box.append(make('p', 'Try one of these, or type your own question.', 'small muted'));
    const c = pageContext(), prompts = c.package_id ? ['What does this package test for?', 'Is this suitable for a yearly check-up?', 'Which centers offer it?'] :
      c.compare_ids ? ['What is the real difference between these?', 'Which one fits a general check-up?'] :
        ['Which check fits a ฿1,500 budget?', 'What does a lipid profile include?', 'I need health checks for 40 employees'];
    prompts.forEach(p => { const b = make('button', p, 'chip'); b.type = 'button'; b.onclick = () => { input.value = p; panel.querySelector('form').requestSubmit(); }; box.append(b); });
    return box;
  }
  function shortcut(cmd) {
    const a = cmd.args || {}; let label = '', href = '';
    if (cmd.type === 'open_package') { label = 'Open ' + (a.name || a.package_id); href = '/packages/' + encodeURIComponent(a.package_id); }
    else if (cmd.type === 'open_compare') { label = 'Compare ' + a.package_ids.length + ' packages'; href = '/compare?ids=' + a.package_ids.map(encodeURIComponent).join(','); }
    else if (cmd.type === 'filter_catalog') { const p = new URLSearchParams(); ['q', 'segment', 'max_price'].forEach(k => { if (a[k]) p.set(k, a[k]); }); label = 'Show matching packages'; href = '/packages?' + p; }
    else if (cmd.type === 'prefill_booking') { const p = new URLSearchParams({ view: 'book', package: a.package_id }); if (a.branch_id) p.set('branch', a.branch_id); if (a.date) p.set('date', a.date); label = 'Book ' + (a.name || a.package_id) + (a.date ? ' on ' + a.date : ''); href = '/app?' + p; }
    else if (cmd.type === 'open_org_form') { label = 'Open the organization form'; href = '/organizations#inq-title'; }
    else if (cmd.type === 'open_view') { label = { packages: 'Browse packages', book: 'Request an appointment', bookings: 'My appointments', reports: 'My reports', notifications: 'Notifications' }[a.view] || 'Open'; href = a.view === 'packages' ? '/packages' : '/app?view=' + encodeURIComponent(a.view); }
    else if (cmd.type === 'highlight_report_field') { label = 'Show this value on my report'; href = '/app?view=reports'; }
    if (!href) return null;
    const l = make('a', label, 'btn sm'); l.href = href; return l;
  }
  function render(m) {
    if (m.role === 'user') {
      const n = make('div', null, 'msg user'); n.append(document.createTextNode(m.content));
      if (m.failed) { const r = make('div', null, 'small'); r.style.marginTop = '6px'; r.append(document.createTextNode(m.retryable ? 'Not answered. ' : 'Not answered.'));
        if (m.retryable) { const b = make('button', 'Retry', 'link-btn'); b.type = 'button'; b.style.color = '#fff'; b.onclick = () => retry(m.id); r.append(b); } n.append(r); }
      return n;
    }
    const n = make('div', null, 'msg ' + (m.role === 'staff' ? 'staff' : 'ai')), by = make('div', null, 'msg-by');
    if (m.role === 'staff') by.append(mark('team', 'T'), document.createTextNode('ResultScope team (a person)'));
    else by.append(mark(m.dot?.id || 'advisor', m.dot?.name || 'Assistant'), document.createTextNode((m.dot?.name || 'Assistant') + ' · AI'));
    const text = make('div', null, 'message-body');
    if (window.DOMPurify && window.marked) text.innerHTML = DOMPurify.sanitize(marked.parse(m.content || ''), { ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code'], ALLOWED_ATTR: [] }); else text.textContent = m.content;
    n.append(by, text);
    if (m.sources?.length) { const s = make('div', null, 'sources'); m.sources.forEach((x, i) => { const a = make('a', (i + 1) + '. ' + x.title); try { const u = new URL(x.url, location.origin); if (['http:', 'https:'].includes(u.protocol)) a.href = u.href; } catch { } if (/^https?:/.test(x.url || '')) { a.target = '_blank'; a.rel = 'noopener noreferrer'; } s.append(a); }); n.append(s); }
    const cuts = make('div', null, 'shortcuts');
    (m.ui || []).forEach(c => { const x = shortcut(c); if (x) cuts.append(x); });
    if (m.action && m.action_id && ['book', 'quote', 'handoff', 'pay'].includes(m.action.type)) {
      const a = m.action;
      const label = { book: 'Send appointment request', quote: 'Keep this selection', handoff: 'Ask our team', pay: 'Open test payment' }[a.type];
      const summary = a.quote ? a.quote.items.map(x => x.name).join(' + ') + ' · ' + money(a.quote.total_thb) + (a.type === 'book' ? ' · ' + a.date + ' ' + a.time : '') : (a.summary || '');
      if (summary) n.append(make('p', summary, 'small'));
      const b = make('button', label, 'btn primary sm'); b.type = 'button';
      b.onclick = async () => {
        b.disabled = true;
        try { const r = await RS.post('/confirm', { action_id: m.action_id }); if (r.simulator_url || r.url) { location.assign(r.simulator_url || r.url); return; } status.textContent = a.type === 'book' ? 'Request sent. Our team will confirm it; see My appointments.' : 'Done.'; await refresh(); }
        catch (e) { status.textContent = e.code === 'account_required' ? 'Sign in or create an account in your workspace first.' : e.message; if (e.code === 'account_required') { const l = make('a', 'Open workspace to sign in', 'btn sm'); l.href = '/app'; cuts.append(l); } }
        finally { b.disabled = false; }
      };
      cuts.prepend(b);
    }
    if (m.followups?.length) m.followups.slice(0, 2).forEach(q => { const c = make('button', q, 'chip'); c.type = 'button'; c.onclick = () => { input.value = q; panel.querySelector('form').requestSubmit(); }; cuts.append(c); });
    if (cuts.children.length) n.append(cuts);
    return n;
  }
  async function refresh(scroll) {
    try {
      if (!RS.user) await RS.session();
      const w = await RS.call('/workspace'); const msgs = w.conversation.messages.slice(-12);
      const key = JSON.stringify(msgs); if (key === lastKey) return; lastKey = key;
      body.replaceChildren(...(msgs.length ? msgs.map(render) : [empty()]));
      if (w.conversation.mode !== 'bot') body.append(make('p', w.conversation.mode === 'waiting' ? 'Your request is with our team; the AI is paused.' : 'A person from our team is replying; the AI is paused.', 'callout small'));
      if (scroll) body.scrollTop = body.scrollHeight;
    } catch (e) { body.replaceChildren(make('p', e.message, 'callout bad small')); }
  }
  async function ask(text, send, stop) {
    if (busy || !text.trim()) return;
    busy = true; send.disabled = true; stop.hidden = false; input.value = '';
    body.append(render({ role: 'user', content: text })); body.scrollTop = body.scrollHeight;
    status.textContent = 'Checking sources and safety before replying…';
    controller = new AbortController();
    try { if (!RS.user) await RS.session(); await RS.call('/chat', { method: 'POST', body: JSON.stringify({ message: text, page: pageContext() }), signal: controller.signal }); status.textContent = ''; }
    catch (e) { status.textContent = e.name === 'AbortError' ? 'Stopped.' : e.message; }
    finally { busy = false; send.disabled = false; stop.hidden = true; controller = null; lastKey = ''; await refresh(true); input.focus(); }
  }
  async function retry(id) {
    if (busy) return; busy = true; status.textContent = 'Retrying…';
    try { await RS.post('/chat/retry', { message_id: id }); status.textContent = ''; } catch (e) { status.textContent = e.message; }
    finally { busy = false; lastKey = ''; await refresh(true); }
  }
  loadRoles().then(() => { buildLauncher(); buildPanel(); document.querySelectorAll('[data-open-dock]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); toggle(true); })); });
  setInterval(() => { if (open && !busy && !document.hidden && RS.user) refresh(true); }, 5000);
})();
