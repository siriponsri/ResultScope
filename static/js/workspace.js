'use strict';
/* ResultScope workspace: customer (/app) and service desk (/staff).
   Every control here calls a server endpoint; the server owns identity, prices,
   capacity, payment state and permissions. The browser only renders and asks. */
(() => {
  const $ = id => document.getElementById(id);
  const STAFF_MODE = document.body.dataset.staff === 'true';
  const STAFF_ROLES = ['staff', 'manager', 'clinical'];
  let csrf = '', user = null, state = null, accessCode = '', busy = false, controller = null;
  let view = STAFF_MODE ? 'staff' : 'chat', lastMessages = '', activeTicket = '', ticketFilter = 'open', opsFilter = 'requested';
  let modes = null, catalogCache = null, branchCache = null;

  /* ------------------------------------------------------------ helpers */
  const money = n => '฿' + new Intl.NumberFormat('en-US').format(n);
  const when = t => new Date(t * 1000).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' });
  const el = (tag, text, cls) => { const e = document.createElement(tag); if (text !== undefined && text !== null) e.textContent = text; if (cls) e.className = cls; return e; };
  const isStaff = () => STAFF_ROLES.includes(user?.role);
  const isManager = () => user?.role === 'manager';
  function notice(text, tone) { const n = $('notice'); n.textContent = text; n.className = 'toast' + (tone === 'bad' ? ' bad' : ''); n.hidden = false; clearTimeout(notice.t); notice.t = setTimeout(() => { n.hidden = true; }, 7000); }
  async function api(path, options = {}) {
    const headers = { 'X-Business-CSRF': csrf, ...(accessCode ? { 'X-ResultScope-Access': accessCode } : {}), ...options.headers };
    if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
    let r;
    try { r = await fetch('/api/business' + path, { credentials: 'same-origin', ...options, headers }); }
    catch (e) { if (e.name === 'AbortError') throw e; throw Object.assign(Error('You appear to be offline. Check your connection and try again.'), { code: 'network' }); }
    let d; try { d = await r.json(); } catch { throw Error('The server response could not be read.'); }
    if (!r.ok) {
      let message = d.message || 'The request could not be completed.';
      if (Array.isArray(d.detail)) message = 'Please check: ' + d.detail.map(x => (x.loc || []).slice(-1)[0]).filter(Boolean).join(', ') + '.';
      throw Object.assign(Error(message), { code: d.code, status: r.status });
    }
    return d;
  }
  const post = (path, data = {}) => api(path, { method: 'POST', body: JSON.stringify(data) });
  function button(text, run, cls = 'btn sm') {
    const b = el('button', text, cls); b.type = 'button';
    b.addEventListener('click', async () => {
      if (b.disabled) return;
      b.disabled = true; b.setAttribute('aria-busy', 'true');
      try { await run(b); } catch (e) { if (e.name !== 'AbortError') notice(e.message, 'bad'); }
      finally { b.disabled = false; b.removeAttribute('aria-busy'); }
    });
    return b;
  }
  function link(text, href, cls = 'btn sm') { const a = el('a', text, cls); a.href = href; return a; }
  function modal(title, node) { $('modal-title').textContent = title; $('modal-content').replaceChildren(node); if (!$('modal').open) $('modal').showModal(); }
  const closeModal = () => { if ($('modal').open) $('modal').close(); };
  $('modal-close').onclick = closeModal;
  $('modal').addEventListener('click', e => { if (e.target === $('modal')) { const r = $('modal').getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) closeModal(); } });
  function intro(title, copy) { const d = el('div', null, 'view-intro'); d.append(el('h2', title)); if (copy) d.append(el('p', copy)); return d; }
  function empty(title, copy, ...actions) { const d = el('div', null, 'state-box'); d.append(el('h3', title)); if (copy) d.append(el('p', copy, 'small muted')); if (actions.length) { const r = el('div', null, 'row'); r.append(...actions); d.append(r); } return d; }
  let fieldSeq = 0;
  function field(label, type = 'text', value = '', hint = '') {
    // Label names the control; the hint is linked with aria-describedby so it is not part of the name.
    const id = 'f' + (++fieldSeq), wrap = el('div', null, 'field'), lab = el('label', label); lab.htmlFor = id; wrap.append(lab);
    const input = type === 'textarea' ? el('textarea', null, 'input') : type === 'select' ? el('select', null, 'input') : el('input', null, 'input');
    input.id = id; if (type !== 'textarea' && type !== 'select') input.type = type;
    if (hint) { const h = el('span', hint, 'hint'); h.id = id + '-hint'; input.setAttribute('aria-describedby', h.id); wrap.append(h); }
    if (value !== '' && value !== null && value !== undefined) input.value = value;
    wrap.append(input); return { wrap, input };
  }
  function badge(text, tone = '') { return el('span', text, 'badge' + (tone ? ' ' + tone : '')); }
  const BOOKING_STATE = { requested: ['Awaiting confirmation', 'warn'], confirmed: ['Confirmed', 'ok'], declined: ['Declined', 'bad'], cancelled: ['Cancelled', 'neutral'] };
  const PAYMENT_STATE = { pending: ['Unpaid', 'neutral'], paid: ['Paid (simulation)', 'ok'], refunded: ['Refunded', 'neutral'], refund_pending: ['Refund pending', 'warn'], expired: ['Checkout expired', 'neutral'] };
  function bookingBadges(b) {
    const [s, st] = BOOKING_STATE[b.state] || [b.state, 'neutral'];
    const [p, pt] = PAYMENT_STATE[b.data.payment_status] || [b.data.payment_status, 'neutral'];
    return [badge(s, st), badge(p, pt)];
  }
  const branchName = id => (branchCache?.branches || []).find(b => b.id === id)?.name || id;
  async function loadBusiness() {
    if (!catalogCache) catalogCache = await api('/catalog');
    if (!branchCache) branchCache = await api('/branches');
  }
  function requireAccount(reason) {
    const box = el('div', null, 'stack');
    box.append(el('p', reason), button('Sign in or create an account', account, 'btn primary'));
    modal('Account needed', box);
  }

  /* ------------------------------------------------------------ account */
  function updateUser(u) {
    user = u;
    $('account-label').textContent = u.registered ? u.email : 'Guest';
    $('account-sub').textContent = isStaff() ? u.role + (u.branch ? ' · ' + u.branch : '') : u.registered ? 'Your personal workspace' : 'Sign in to keep your history';
    if ($('staff-nav')) $('staff-nav').hidden = !isStaff();
    document.querySelectorAll('[data-manager-only]').forEach(n => { n.hidden = !isManager(); });
  }
  function account() {
    const box = el('div', null, 'stack');
    if (user?.registered) {
      box.append(el('p', 'Signed in as ' + user.email + (isStaff() ? ' (' + user.role + ')' : '')),
        el('p', 'Your reports and conversations are private to this account. Email verification and password recovery are not available in this coursework release.', 'small muted'));
      const row = el('div', null, 'row');
      row.append(button('Sign out', async () => { await post('/logout'); location.href = STAFF_MODE ? '/staff' : '/app'; }, 'btn'));
      if (!STAFF_MODE) row.append(button('Unlink LINE', async () => { await post('/account/line/unlink'); notice('LINE unlinked. Pending LINE deliveries were cancelled.'); }, 'btn ghost'));
      box.append(row);
    } else {
      const form = el('form', null, 'form-grid'), email = field('Email address', 'email'), pass = field('Password', 'password', '', 'At least 12 characters. Use a demonstration password.');
      email.input.required = true; email.input.autocomplete = 'email'; pass.input.minLength = 12; pass.input.required = true; pass.input.autocomplete = 'current-password';
      const err = el('p', '', 'field-error'); err.setAttribute('role', 'alert'); err.hidden = true;
      async function auth(kind) {
        err.hidden = true;
        if (!form.reportValidity()) return;
        try {
          const r = await post('/' + kind, { email: email.input.value, password: pass.input.value });
          csrf = r.csrf; updateUser(r.user); closeModal(); lastMessages = '';
          await refresh(); notice(kind === 'login' ? 'Signed in.' : 'Account created.');
          await navigate(STAFF_MODE ? 'staff' : view, false); await checkLink();
        } catch (e) { err.textContent = e.message; err.hidden = false; }
      }
      const actions = el('div', null, 'form-actions');
      actions.append(button('Sign in', () => auth('login'), 'btn primary'));
      if (!STAFF_MODE) actions.append(button('Create account', () => auth('register'), 'btn'));
      form.addEventListener('submit', e => { e.preventDefault(); auth('login'); });
      form.append(email.wrap, pass.wrap, err, actions);
      if (STAFF_MODE) form.append(el('p', 'Staff accounts are created by the deployment owner with scripts/create_staff.py.', 'tiny muted'));
      box.append(form);
    }
    modal(user?.registered ? 'Your account' : (STAFF_MODE ? 'Staff sign-in' : 'Sign in or create an account'), box);
  }
  $('account-open').onclick = account;

  /* ------------------------------------------------------------ chat */
  function markdown(text) {
    const d = el('div', null, 'message-body');
    d.innerHTML = DOMPurify.sanitize(marked.parse(text || ''), { ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre', 'blockquote', 'h2', 'h3', 'table', 'thead', 'tbody', 'tr', 'th', 'td'], ALLOWED_ATTR: [] });
    return d;
  }
  function safeHref(url) { try { const u = new URL(url, location.origin); return ['http:', 'https:'].includes(u.protocol) ? u.href : null; } catch { return null; } }
  function actionCard(m) {
    const a = m.action, c = el('div', null, 'action-card');
    const titles = { book: 'Appointment request preview', quote: 'Package preview', pay: 'Payment preview', handoff: 'Continue with our team', link: 'Link your LINE conversation' };
    c.append(el('strong', titles[a.type] || 'Preview'));
    if (a.quote) c.append(el('p', a.quote.items.map(x => x.name).join(' + ') + ' · ' + money(a.quote.total_thb), 'small'));
    if (a.type === 'book') c.append(el('p', branchName(a.branch_id) + ' · ' + a.date + ' · ' + a.time + ' (Bangkok time)', 'small'));
    if (a.summary) c.append(el('p', a.summary, 'small muted'));
    if (a.type === 'book') c.append(el('p', 'Sending this creates a request. Our team confirms it before payment opens.', 'tiny muted'));
    if (a.type === 'link') c.append(el('p', 'Open the invitation from your LINE chat while signed in here to link accounts.', 'tiny muted'));
    if (m.action_id && ['book', 'quote', 'handoff', 'pay'].includes(a.type)) {
      const label = { book: 'Send appointment request', quote: 'Keep this selection', handoff: 'Request our team', pay: 'Open test payment' }[a.type];
      c.append(button(label, async () => {
        try {
          const r = await post('/confirm', { action_id: m.action_id });
          if (r.simulator_url) { location.assign(r.simulator_url); return; }
          if (r.url) { location.assign(r.url); return; }
          notice(a.type === 'book' ? 'Appointment request sent. Our team will confirm it.' : a.type === 'handoff' ? 'Your request is with our team.' : r.message || 'Done.');
          await refresh();
        } catch (e) {
          if (e.code === 'account_required') requireAccount('Create an account or sign in before sending an appointment request, so you can follow it.');
          else if (['preview_expired', 'quote_changed'].includes(e.code)) notice(e.message + ' Ask the assistant for a fresh preview.', 'bad');
          else throw e;
        }
      }, 'btn primary sm'));
    }
    return c;
  }
  function messageNode(m, interactive = true) {
    const a = el('article', null, 'chat-message ' + m.role + (m.failed ? ' failed' : ''));
    if (m.role === 'user') {
      a.append(document.createTextNode(m.content));
      if (m.failed) {
        const row = el('div', null, 'failed-row');
        row.append(el('span', m.retryable ? 'Not answered. You can retry without retyping.' : 'Not answered. ' + (m.error === 'safety_blocked' ? 'This request was blocked by the safety check.' : 'Try rephrasing, or contact our team.')));
        if (interactive && m.retryable) row.append(button('Retry', () => retry(m.id), 'btn sm'));
        a.append(row);
      }
      return a;
    }
    a.append(el('div', m.role === 'staff' ? 'ResultScope team' : 'ResultScope assistant', 'message-label'), markdown(m.content));
    if (m.sources?.length) {
      const s = el('div', null, 'source-chips'); s.setAttribute('aria-label', 'Sources');
      m.sources.forEach(x => { const href = safeHref(x.url); const l = el(href ? 'a' : 'span', x.title); if (href) { l.href = href; l.target = '_blank'; l.rel = 'noopener noreferrer'; } s.append(l); });
      a.append(s);
    }
    if (interactive && m.action) a.append(actionCard(m));
    if (interactive && m.followups?.length) {
      const f = el('div', null, 'followups');
      m.followups.slice(0, 3).forEach(q => { const b = el('button', q, 'chip'); b.type = 'button'; b.dataset.prompt = q; f.append(b); });
      a.append(f);
    }
    return a;
  }
  function renderMessages(c) {
    if (STAFF_MODE) return;
    const key = JSON.stringify(c.messages);
    if (key === lastMessages) return;
    lastMessages = key;
    if (!c.messages.length) {
      if (!$('messages').querySelector('.welcome')) $('messages').replaceChildren(empty('A fresh conversation', 'Ask about a health check, a report or an appointment.'));
      return;
    }
    $('messages').replaceChildren(...c.messages.map(m => messageNode(m)));
    $('messages').scrollTop = $('messages').scrollHeight;
  }
  function renderContext() {
    if (STAFF_MODE || !state) return;
    const mode = state.conversation.mode;
    $('handoff-state').textContent = mode === 'waiting' ? 'Your request is queued for our team; the assistant is paused.' : mode === 'staff' ? 'A team member is replying; the assistant is paused.' : '';
    const r = state.reports.find(x => x.id === state.conversation.report_id);
    $('context-report').textContent = r ? 'Report in use: ' + r.label + (r.date ? ' · ' + r.date : '') : 'No report selected';
    const next = $('context-next'); next.replaceChildren();
    const open = state.bookings.filter(b => ['requested', 'confirmed'].includes(b.state));
    if (open.length) { const b = open[open.length - 1]; next.append(el('p', 'Next appointment: ' + b.data.date + ' ' + b.data.time, 'small'), ...bookingBadges(b)); }
    const chips = $('context-chips'); chips.replaceChildren();
    if (r) { const c = el('button', null, 'chip active'); c.type = 'button'; c.append(document.createTextNode('Report: ' + r.label + ' '), el('span', '×', 'x')); c.setAttribute('aria-label', 'Stop using report ' + r.label); c.onclick = async () => { await post('/reports/select', { report_id: '' }); await refresh(); notice('The report is no longer used in this conversation.'); }; chips.append(c); }
  }
  async function refresh() {
    state = await api('/workspace');
    updateUser(state.user);
    renderMessages(state.conversation);
    renderContext();
    setBell(state.unread_notifications);
  }
  async function send(text) {
    if (busy || !text.trim()) return;
    if (view !== 'chat') await navigate('chat');
    busy = true; $('send').disabled = true; $('stop').hidden = false;
    $('chat-status').textContent = state?.conversation.mode === 'bot' ? 'Checking your request, sources and safety before replying…' : 'Sending to our team…';
    controller = new AbortController(); $('message').value = '';
    try { await api('/chat', { method: 'POST', body: JSON.stringify({ message: text }), signal: controller.signal }); }
    catch (e) { if (e.name !== 'AbortError') notice(e.message, 'bad'); }
    finally { busy = false; $('send').disabled = false; $('stop').hidden = true; $('chat-status').textContent = ''; controller = null; await refresh().catch(() => {}); $('message').focus(); }
  }
  async function retry(id) {
    if (busy) return;
    busy = true; $('chat-status').textContent = 'Retrying your last message…'; $('stop').hidden = false; controller = new AbortController();
    try { await api('/chat/retry', { method: 'POST', body: JSON.stringify({ message_id: id }), signal: controller.signal }); }
    catch (e) { if (e.name !== 'AbortError') notice(e.message, 'bad'); }
    finally { busy = false; $('chat-status').textContent = ''; $('stop').hidden = true; controller = null; lastMessages = ''; await refresh().catch(() => {}); }
  }
  if (!STAFF_MODE) {
    $('chat-form').addEventListener('submit', e => { e.preventDefault(); send($('message').value); });
    $('message').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); $('chat-form').requestSubmit(); } });
    $('stop').onclick = async () => { controller?.abort(); try { await post('/stop'); notice('Stopped. A late answer will not be added.'); } catch (e) { notice(e.message, 'bad'); } };
    $('new-chat').onclick = async () => {
      try { await post('/new-chat'); lastMessages = ''; await refresh(); await navigate('chat'); notice('Previous conversation saved in Past conversations.'); }
      catch (e) { notice(e.message, 'bad'); }
    };
    $('staff-request').onclick = requestStaff; $('context-staff').onclick = requestStaff;
  }
  document.addEventListener('click', e => { const b = e.target.closest('[data-prompt]'); if (b) send(b.dataset.prompt); });
  function requestStaff(prefill = '') {
    const form = el('form', null, 'form-grid'), f = field('How can our team help?', 'textarea', typeof prefill === 'string' ? prefill : '');
    f.input.required = true; f.input.maxLength = 1000;
    form.append(f.wrap, el('p', 'Your conversation is shared with the service team and the assistant pauses until they reply or hand it back. Urgent health concerns should not wait in this queue.', 'small muted'),
      button('Send to our team', async () => { if (!form.reportValidity()) return; await post('/handoffs', { summary: f.input.value }); closeModal(); await refresh(); notice('Your request is queued for our team.'); }, 'btn primary'));
    form.onsubmit = e => e.preventDefault();
    modal('Talk to our team', form);
  }

  /* ------------------------------------------------------------ health checks */
  function packageCard(p) {
    const c = el('article', null, 'pkg');
    const head = el('div', null, 'pkg-head'), h = el('h3'), a = el('a', p.name); a.href = '/packages/' + p.id; h.append(a);
    head.append(h, p.segment === 'organization' ? badge('Organizations', 'neutral') : p.staff_review_required ? badge('Staff review', 'warn') : badge('Book directly'));
    const ul = el('ul', null, 'pkg-tests'); p.services.forEach(s => ul.append(el('li', s)));
    const price = el('div', null, 'pkg-price'); price.append(el('strong', money(p.price_thb)), el('span', p.price_unit));
    const foot = el('div', null, 'pkg-foot');
    if (p.segment === 'organization') foot.append(link('Request a quotation', '/organizations?package=' + p.id, 'btn sm primary'));
    else if (!p.staff_review_required) foot.append(button('Request appointment', () => navigate('book', true, { package: p.id }), 'btn sm primary'));
    foot.append(button('Ask about it', () => send(`Tell me about ${p.name} (${p.id}). Is it suitable for my goals?`), 'btn sm'));
    c.append(head, ul, price, foot); return c;
  }
  async function packages() {
    const box = el('div'); box.append(intro('Health checks', 'Search and filter the same catalog the assistant uses. Simulated prices.'));
    const bar = el('form', null, 'toolbar'); bar.setAttribute('role', 'search');
    const q = el('input', null, 'input'); q.type = 'search'; q.placeholder = 'Search tests, e.g. lipid'; q.setAttribute('aria-label', 'Search health checks'); q.maxLength = 80;
    const seg = el('select', null, 'input'); seg.setAttribute('aria-label', 'Who it is for');
    [['', 'Everyone'], ['individual', 'Individuals'], ['organization', 'Organizations']].forEach(([v, t]) => { const o = el('option', t); o.value = v; seg.append(o); });
    const sort = el('select', null, 'input'); sort.setAttribute('aria-label', 'Sort');
    [['featured', 'Recommended'], ['price_asc', 'Price: low to high'], ['price_desc', 'Price: high to low'], ['name', 'Name']].forEach(([v, t]) => { const o = el('option', t); o.value = v; sort.append(o); });
    const reset = el('button', 'Reset', 'btn ghost sm'); reset.type = 'button';
    const count = el('p', '', 'small muted'); count.setAttribute('aria-live', 'polite');
    bar.append(q, seg, sort, reset);
    const grid = el('div', null, 'pkg-grid');
    async function load() {
      grid.setAttribute('aria-busy', 'true');
      const p = new URLSearchParams({ q: q.value, segment: seg.value, sort: sort.value });
      try {
        const d = await api('/catalog/search?' + p);
        grid.replaceChildren(...d.packages.map(packageCard));
        count.textContent = d.total + ' result' + (d.total !== 1 ? 's' : '') + ' · catalog ' + d.catalog_version;
        if (!d.total) grid.replaceChildren(empty('No matches', 'Try another test name or clear the filters.', button('Clear filters', () => { q.value = ''; seg.value = ''; sort.value = 'featured'; load(); }), button('Ask the assistant', () => send('I am looking for a health check that includes ' + (q.value || 'specific tests') + '.'), 'btn sm primary')));
      } catch (e) { grid.replaceChildren(empty('Health checks could not be loaded', e.message, button('Try again', load))); }
      finally { grid.removeAttribute('aria-busy'); }
    }
    let t; q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(load, 300); });
    seg.onchange = load; sort.onchange = load; bar.onsubmit = e => { e.preventDefault(); load(); };
    reset.onclick = () => { q.value = ''; seg.value = ''; sort.value = 'featured'; load(); };
    box.append(bar, count, grid); await load(); return box;
  }

  /* ------------------------------------------------------------ booking */
  function slotPicker(branchSel, dateInput, onPick) {
    const wrap = el('div', null, 'stack-sm'), grid = el('div', null, 'slot-grid'), msg = el('p', 'Choose a center and date to see available times.', 'small muted');
    grid.setAttribute('role', 'group'); grid.setAttribute('aria-label', 'Available times'); msg.setAttribute('aria-live', 'polite');
    let chosen = '';
    async function load() {
      chosen = ''; onPick('');
      if (!branchSel.value || !dateInput.value) { grid.replaceChildren(); msg.textContent = 'Choose a center and date to see available times.'; return; }
      msg.textContent = 'Loading times…'; grid.replaceChildren();
      try {
        const d = await api('/slots?' + new URLSearchParams({ branch_id: branchSel.value, date: dateInput.value }));
        if (!d.slots.length) { msg.textContent = new Date(dateInput.value + 'T00:00:00').getDay() === 0 ? 'Centers are closed on Sundays. Choose Monday to Saturday.' : 'No times are open on this date (past, or more than 30 days ahead). Choose another date.'; return; }
        const open = d.slots.filter(s => s.available > 0).length;
        msg.textContent = open ? open + ' of ' + d.slots.length + ' times available.' : 'This date is fully booked. Try another date or center.';
        d.slots.forEach(s => {
          const b = el('button', null, 'slot'); b.type = 'button'; b.disabled = s.available < 1; b.setAttribute('aria-pressed', 'false');
          b.append(el('span', s.time), el('small', s.available < 1 ? 'Full' : s.available + ' left'));
          b.setAttribute('aria-label', s.time + (s.available < 1 ? ', full' : ', ' + s.available + ' places left'));
          b.onclick = () => { grid.querySelectorAll('.slot').forEach(x => x.setAttribute('aria-pressed', String(x === b))); chosen = s.time; onPick(s.time); };
          grid.append(b);
        });
      } catch (e) { msg.textContent = e.message; grid.replaceChildren(button('Try again', load)); }
    }
    branchSel.addEventListener('change', load); dateInput.addEventListener('change', load);
    wrap.append(msg, grid); return { wrap, load, get value() { return chosen; } };
  }
  function bangkokDate(offsetDays = 0) { const d = new Date(Date.now() + 7 * 3600e3 + offsetDays * 86400e3); return d.toISOString().slice(0, 10); }
  async function bookView(params = {}) {
    await loadBusiness();
    const box = el('div'); box.append(intro('Request an appointment', 'Choose a package, center and time. Your request holds the slot until our team confirms it; payment opens after confirmation.'));
    const bookable = catalogCache.packages.filter(p => p.segment === 'individual' && !p.staff_review_required && p.active !== false);
    const grid = el('div', null, 'book-grid'), form = el('form', null, 'card form-grid'), summary = el('aside', null, 'card summary');
    const pkg = field('Health check', 'select'); bookable.forEach(p => { const o = el('option', p.name + ' · ' + money(p.price_thb)); o.value = p.id; pkg.input.append(o); });
    if (params.package && bookable.some(p => p.id === params.package)) pkg.input.value = params.package;
    const branch = field('Center', 'select'); const date = field('Date', 'date', '', 'Monday to Saturday, up to 30 days ahead');
    date.input.min = bangkokDate(0); date.input.max = bangkokDate(30); date.input.required = true;
    function fillBranches() {
      const p = bookable.find(x => x.id === pkg.input.value); const prev = branch.input.value || params.branch || '';
      branch.input.replaceChildren(); const o0 = el('option', 'Choose a center'); o0.value = ''; branch.input.append(o0);
      branchCache.branches.filter(b => !p || p.branch_ids.includes(b.id)).forEach(b => { const o = el('option', b.name); o.value = b.id; branch.input.append(o); });
      branch.input.value = [...branch.input.options].some(o => o.value === prev) ? prev : '';
    }
    fillBranches();
    let time = ''; let key = crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2);
    const picker = slotPicker(branch.input, date.input, t => { time = t; renderSummary(); });
    const err = el('p', '', 'field-error'); err.hidden = true; err.setAttribute('role', 'alert');
    const submit = button('Send appointment request', async () => {
      err.hidden = true;
      if (!pkg.input.value || !branch.input.value || !date.input.value || !time) { err.textContent = 'Choose a package, a center, a date and an available time.'; err.hidden = false; return; }
      if (!user?.registered) { requireAccount('Create an account or sign in so you can follow your appointment request.'); return; }
      try {
        const r = await post('/bookings', { package_ids: [pkg.input.value], branch_id: branch.input.value, date: date.input.value, time, idempotency_key: key });
        key = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
        notice('Request sent for ' + r.data.date + ' at ' + r.data.time + '. We will notify you when it is confirmed.');
        await navigate('bookings');
      } catch (e) {
        err.textContent = e.message; err.hidden = false;
        if (e.code === 'slot_full') picker.load();
      }
    }, 'btn primary');
    pkg.input.addEventListener('change', () => { fillBranches(); picker.load(); renderSummary(); });
    branch.input.addEventListener('change', renderSummary); date.input.addEventListener('change', renderSummary);
    function renderSummary() {
      const p = bookable.find(x => x.id === pkg.input.value);
      summary.replaceChildren(el('h3', 'Summary'));
      const dl = el('dl'); const row = (k, v) => { const d = el('div'); d.append(el('dt', k), el('dd', v || '—')); dl.append(d); };
      row('Package', p?.name); row('Center', branch.input.value ? branchName(branch.input.value) : ''); row('Date', date.input.value); row('Time', time ? time + ' Bangkok' : '');
      summary.append(dl, el('p', p ? money(p.price_thb) : '—', 'total'), el('p', 'Simulated price from the current catalog. The server rechecks price and capacity when you send.', 'tiny muted'), submit);
    }
    form.onsubmit = e => e.preventDefault();
    form.append(pkg.wrap, branch.wrap, date.wrap, el('h3', 'Time', 'h4'), picker.wrap, err);
    if (!bookable.length) form.replaceChildren(empty('No packages can be booked directly right now', 'Ask our team for help.', button('Talk to our team', requestStaff)));
    renderSummary(); grid.append(form, summary); box.append(grid);
    if (branch.input.value && params.date) { date.input.value = params.date; picker.load(); }
    return box;
  }
  function rescheduleDialog(b) {
    const f = el('div', null, 'form-grid');
    const branch = el('select', null, 'input'); const o = el('option', branchName(b.branch)); o.value = b.branch; branch.append(o); branch.disabled = true;
    const date = field('New date', 'date'); date.input.min = bangkokDate(0); date.input.max = bangkokDate(30);
    let time = ''; const picker = slotPicker(branch, date.input, t => { time = t; });
    f.append(el('p', 'Changing the time sends the appointment back to our team for confirmation. ' + (b.state === 'confirmed' ? 'Changes less than 24 hours before the slot go to staff review.' : ''), 'small muted'), date.wrap, picker.wrap,
      button('Request new time', async () => {
        if (!date.input.value || !time) { notice('Choose a date and an available time.', 'bad'); return; }
        const r = await post('/bookings/' + b.id + '/change', { operation: 'reschedule', date: date.input.value, time });
        closeModal(); notice(r.kind === 'ticket' ? 'Within 24 hours, so our team will review the change.' : 'New time requested. Awaiting confirmation.'); await navigate('bookings', false);
      }, 'btn primary'));
    modal('Change appointment time', f);
  }
  async function pay(b, method) {
    const r = await post('/payments/checkout', { booking_id: b.id, method });
    if (r.simulator_url) { location.assign(r.simulator_url); return; }
    if (r.url) { location.assign(r.url); return; }
    notice(r.message || 'Payment method recorded.'); await navigate('bookings', false);
  }
  async function bookings() {
    await refresh(); await loadBusiness();
    const box = el('div'); box.append(intro('My appointments', 'Requests, confirmed visits, payments and organization quotations. A confirmed appointment and a paid order are separate states.'));
    const toolbar = el('div', null, 'toolbar'); toolbar.append(button('Request an appointment', () => navigate('book'), 'btn primary sm'), button('Refresh', () => navigate('bookings', false), 'btn ghost sm'));
    box.append(toolbar);
    // Quotations grouped by case, newest version first.
    const quotes = (state.quotes || []).slice().sort((a, b) => (b.data.version || 1) - (a.data.version || 1));
    if (quotes.length || (state.inquiries || []).length) {
      const t = el('div', null, 'section-title'); t.append(el('h2', 'Organization quotations')); box.append(t);
      const list = el('div', null, 'record-list');
      (state.inquiries || []).filter(i => !quotes.some(q => q.data.ticket_id === i.data.ticket_id)).forEach(i => {
        const r = el('article', null, 'record'); const h = el('div', null, 'record-head');
        h.append(el('h3', i.data.organization), badge('Waiting for quotation', 'warn')); r.append(h, el('p', i.data.headcount + ' people · ' + (i.data.service_mode === 'onsite' ? 'onsite' : 'at center') + ' · requested ' + when(i.data.at), 'small muted')); list.append(r);
      });
      quotes.forEach(q => {
        const d = q.data, r = el('article', null, 'record'), h = el('div', null, 'record-head');
        const tone = { offered: ['Ready to review', 'warn'], accepted: ['Accepted', 'ok'], superseded: ['Superseded by a newer version', 'neutral'] }[q.state] || [q.state, 'neutral'];
        h.append(el('h3', d.items[0].name + ' · version ' + (d.version || 1)), badge(...tone)); r.append(h);
        const meta = el('div', null, 'record-meta'); meta.append(el('span', 'Total ' + money(d.total_thb)), el('span', d.date + ' ' + d.time), el('span', d.venue), el('span', 'Valid until ' + new Date(d.expires * 1000).toLocaleDateString('en-GB')));
        r.append(meta); if (d.note) r.append(el('p', 'Note: ' + d.note, 'small'));
        const act = el('div', null, 'record-actions');
        act.append(link('Download quotation (PDF)', '/api/business/quotes/' + encodeURIComponent(q.id) + '/document.pdf', 'btn sm'));
        if (q.state === 'offered') act.append(button('Review and accept', () => {
          const n = el('div', null, 'stack');
          n.append(el('p', `Accept version ${d.version || 1}: ${d.people} people, ${money(d.total_thb)} in total. Accepting creates the service appointment; payment is arranged with our team. This is not a tax invoice.`),
            button('Accept quotation', async () => { try { await post('/quotes/accept', { quote_id: q.id }); closeModal(); notice('Quotation accepted.'); await navigate('bookings', false); } catch (e) { closeModal(); notice(e.message, 'bad'); await navigate('bookings', false); } }, 'btn primary'));
          modal('Accept organization quotation', n);
        }, 'btn sm primary'));
        r.append(act); list.append(r);
      });
      box.append(list);
    }
    const t2 = el('div', null, 'section-title'); t2.append(el('h2', 'Appointments')); box.append(t2);
    if (!state.bookings.length) { box.append(empty('No appointments yet', 'Request a time directly, or ask the assistant to help you choose.', button('Request an appointment', () => navigate('book'), 'btn primary sm'), button('Ask the assistant', () => send('Help me choose a package and book a visit.'), 'btn sm'))); return box; }
    const list = el('div', null, 'record-list');
    state.bookings.slice().reverse().forEach(b => {
      const d = b.data, r = el('article', null, 'record'), h = el('div', null, 'record-head');
      h.append(el('h3', d.items.map(i => i.name).join(' + ')), ...bookingBadges(b));
      const meta = el('div', null, 'record-meta');
      meta.append(el('span', d.date + ' · ' + d.time + ' Bangkok'), el('span', d.organization ? (d.venue || 'Organization service') : branchName(b.branch)), el('span', money(d.total_thb)), el('span', 'Ref ' + b.id.slice(-8)));
      r.append(h, meta);
      if (b.state === 'declined' && d.decision_note) r.append(el('p', 'From our team: ' + d.decision_note, 'small'));
      const txn = (state.payments || []).find(t => t.booking_id === b.id && t.state === 'pending');
      if (d.last_payment_outcome && d.payment_status === 'pending' && !txn) r.append(el('p', 'Last test payment: ' + d.last_payment_outcome + '. You can try again or pay at the center.', 'small muted'));
      const act = el('div', null, 'record-actions');
      if (b.state === 'requested') {
        r.append(el('p', 'Our team will confirm or decline this request. You will get a notification.', 'small muted'));
        act.append(button('Change time', () => rescheduleDialog(b)), button('Withdraw request', () => {
          const n = el('div', null, 'stack'); n.append(el('p', 'Withdraw this appointment request? The time slot is released.'), button('Withdraw request', async () => { await post('/bookings/' + b.id + '/change', { operation: 'cancel' }); closeModal(); notice('Request withdrawn.'); await navigate('bookings', false); }, 'btn danger'));
          modal('Withdraw request', n);
        }, 'btn sm danger'));
      }
      if (b.state === 'confirmed') {
        if (!d.organization) act.append(link('Add to calendar (.ics)', '/api/business/bookings/' + encodeURIComponent(b.id) + '/calendar.ics', 'btn sm'));
        if (d.payment_status === 'pending') {
          if (txn) act.append(link('Continue test payment', '/pay/sim/' + encodeURIComponent(txn.id), 'btn sm primary'));
          else if (!d.organization) act.append(button('Pay with test PromptPay', () => pay(b, 'promptpay'), 'btn sm primary'), button('Pay with test card', () => pay(b, 'card')), d.payment_method === 'center' ? badge('Paying at the center', 'neutral') : button('Pay at the center', () => pay(b, 'center')));
        }
        if (!d.organization) act.append(button('Change time', () => rescheduleDialog(b)));
        act.append(button(d.payment_status === 'paid' ? 'Request refund' : 'Cancel appointment', () => {
          const n = el('div', null, 'stack');
          n.append(el('p', d.payment_status === 'paid' ? 'Refunds are reviewed by our team; approval is not guaranteed.' : 'Cancelling 24 hours or more before the slot is immediate. Closer to the time, our team reviews it.', 'small'),
            button('Confirm', async () => { const res = await post('/bookings/' + b.id + '/change', { operation: d.payment_status === 'paid' ? 'refund_request' : 'cancel' }); closeModal(); notice(res.kind === 'ticket' ? 'Sent to our team for review.' : 'Appointment cancelled.'); await navigate('bookings', false); }, 'btn danger'));
          modal(d.payment_status === 'paid' ? 'Request a refund' : 'Cancel appointment', n);
        }, 'btn sm danger'));
      }
      if (act.children.length) r.append(act);
      list.append(r);
    });
    box.append(list); return box;
  }

  /* ------------------------------------------------------------ reports */
  async function reports() {
    await refresh();
    const box = el('div'); box.append(intro('My reports', 'Check every extracted value before it is used. Choose a previous report for comparison only when it belongs to the same person.'));
    const actions = el('div', null, 'toolbar');
    actions.append(button('Add a report', () => $('report-file').click(), 'btn primary sm'), button('Try a synthetic sample', demoPicker),
      button('Clear report context', async () => { await post('/reports/select', { report_id: '' }); await post('/reports/compare', { report_id: '' }); await refresh(); notice('Report context cleared.'); }, 'btn ghost sm'));
    box.append(actions);
    if (!state.reports.length) { box.append(empty('No reports yet', 'Upload a JPEG, PNG or PDF up to 3 MB, or read one of the synthetic samples.')); return box; }
    const list = el('div', null, 'record-list');
    state.reports.slice().reverse().forEach(r => {
      const c = el('article', null, 'record'), h = el('div', null, 'record-head');
      h.append(el('h3', r.label), r.confirmed ? badge('Confirmed', 'ok') : badge('Needs review', 'warn'));
      if (state.conversation.report_id === r.id) h.append(badge('In use'));
      if (state.conversation.compare_report_id === r.id) h.append(badge('Previous report', 'neutral'));
      c.append(h, el('p', r.date || 'Collection date not entered', 'small muted'));
      const a = el('div', null, 'record-actions');
      a.append(button(r.confirmed ? 'View fields' : 'Review fields', async () => reviewReport(await api('/reports/' + r.id))));
      if (r.confirmed) a.append(button('Use in conversation', async () => { await post('/reports/select', { report_id: r.id }); await refresh(); await navigate('chat'); notice('Report selected. Ask about it now.'); }),
        button('Use as previous report', async () => { await post('/reports/compare', { report_id: r.id }); await navigate('reports', false); notice('Previous report selected for comparison.'); }));
      a.append(button('Delete', () => {
        const n = el('div', null, 'stack'); n.append(el('p', 'This removes the report and clears conversation history so its values cannot reappear. This cannot be undone.'),
          button('Delete report and history', async () => { await api('/reports/' + r.id, { method: 'DELETE' }); closeModal(); lastMessages = ''; notice('Report deleted.'); await navigate('reports', false); }, 'btn danger'));
        modal('Delete report', n);
      }, 'btn sm danger'));
      c.append(a); list.append(c);
    });
    box.append(list); return box;
  }
  function reviewReport(r) {
    const d = r.data, form = el('form', null, 'form-grid'), label = field('Report label', 'text', d.label || 'My report'), date = field('Collection date if known', 'date', d.collected_date || '');
    form.append(el('p', 'Compare every value with the source image. Leave missing values empty. Synthetic samples are not patient records.', 'small muted'), label.wrap, date.wrap);
    if (d.warnings?.length) form.append(el('p', d.warnings.join(' · '), 'callout warn small'));
    const preview = el('img', null, 'report-preview'); preview.src = '/api/business/reports/' + encodeURIComponent(r.id) + '/source'; preview.alt = 'Source report first page for comparison';
    form.append(preview);
    const wrap = el('div', null, 'table-wrap'), table = el('table', null, 'data report-table'), head = el('tr');
    ['Test', 'Result', 'Unit', 'Reference', 'Flag'].forEach(x => head.append(el('th', x))); table.append(head);
    const fields = [];
    d.fields.forEach((row, i) => {
      const tr = el('tr'), cells = {};
      ['name', 'value', 'unit', 'reference', 'printed_flag'].forEach(k => { const td = el('td'), input = el('input'); input.type = 'text'; input.value = row[k] || ''; input.setAttribute('aria-label', (k === 'printed_flag' ? 'flag' : k) + ' for row ' + (i + 1)); input.maxLength = k === 'name' ? 120 : 160; td.append(input); tr.append(td); cells[k] = input; });
      fields.push(cells); table.append(tr);
    });
    if (!d.fields.length) form.append(el('p', 'No values could be read. Delete this report or try a clearer image.', 'callout warn small'));
    wrap.append(table);
    const check = el('label', null, 'check'), cb = el('input'); cb.type = 'checkbox'; cb.required = true;
    check.append(cb, document.createTextNode('I checked the extracted values and confirm this report belongs to the person being discussed.'));
    form.append(wrap, check, button('Confirm and use report', async () => {
      if (!form.reportValidity()) return;
      await post('/reports/confirm', { report_id: r.id, fields: fields.map(c => Object.fromEntries(Object.entries(c).map(([k, v]) => [k, v.value]))), label: label.input.value, collected_date: date.input.value, same_person_confirmed: cb.checked });
      closeModal(); await refresh(); await navigate('chat'); notice('Report confirmed. You can ask about it now.');
    }, 'btn primary'));
    form.onsubmit = e => e.preventDefault();
    modal('Review report fields', form);
  }
  async function demoPicker() {
    const d = await api('/demos'), box = el('div', null, 'stack');
    box.append(el('p', 'Six synthetic laboratory documents for testing the reader. Their values and printed ranges are not medical reference knowledge.', 'small muted'));
    d.demos.forEach(x => {
      const row = el('div', null, 'record'); row.append(el('h3', x.title), el('p', x.description, 'small muted'));
      const a = el('a', 'View source image', 'small'); a.href = '/api/v2/demos/' + x.id + '/png'; a.target = '_blank'; a.rel = 'noopener';
      row.append(a, button('Read this sample', async () => { notice('Reading the document. This uses the configured OCR provider.'); reviewReport(await post('/demos/' + x.id + '/read')); }, 'btn sm'));
      box.append(row);
    });
    modal('Try a sample report', box);
  }
  if (!STAFF_MODE) {
    $('add-report').onclick = () => $('report-file').click();
    $('demo-open').onclick = () => demoPicker().catch(e => notice(e.message, 'bad'));
  }
  $('report-file').onchange = async () => {
    const file = $('report-file').files[0]; if (!file) return;
    try {
      if (file.size > 3 * 1024 * 1024) throw Error('Choose a file under 3 MB.');
      if (!/\.(pdf|png|jpe?g)$/i.test(file.name)) throw Error('Use a PDF, PNG or JPEG file.');
      const form = new FormData(); form.append('file', file);
      notice('Reading your document. Please wait…');
      reviewReport(await api('/reports/read', { method: 'POST', body: form }));
    } catch (e) { notice(e.message, 'bad'); } finally { $('report-file').value = ''; }
  };

  /* ------------------------------------------------------------ history and notifications */
  async function historyView() {
    const d = await api('/history'), box = el('div'); box.append(intro('Past conversations', 'Saved when you start a new conversation. Deleting a report also clears these to avoid keeping its values.'));
    if (!d.conversations.length) { box.append(empty('No past conversations', 'Start a new conversation to save the current one here.')); return box; }
    const list = el('div', null, 'record-list');
    d.conversations.slice().reverse().forEach(c => {
      const n = el('article', null, 'record'), first = c.data.messages.find(m => m.role === 'user');
      n.append(el('h3', when(c.created)), el('p', first ? first.content.slice(0, 140) : 'No messages', 'small muted'),
        button('Read conversation', () => { const b = el('div', null, 'stack'); c.data.messages.forEach(m => b.append(messageNode({ ...m, action: null }, false))); modal('Past conversation', b); }));
      list.append(n);
    });
    box.append(list); return box;
  }
  function setBell(n) { const c = $('bell-count'); c.textContent = n > 99 ? '99+' : String(n || 0); c.hidden = !n; $('bell').setAttribute('aria-label', n ? `Notifications, ${n} unread` : 'Notifications'); }
  const noticePath = () => STAFF_MODE ? '/staff/notifications' : '/notifications';
  async function pollBell() { if (!csrf || (STAFF_MODE && !isStaff())) return; try { setBell((await api(noticePath())).unread); } catch { /* keep last count */ } }
  async function notifications() {
    const box = el('div'); box.append(intro('Notifications', 'Updates created by real events in your account: requests, confirmations, payments, quotations and replies.'));
    if (STAFF_MODE && !isStaff()) return staffSignIn(box);
    const d = await api(noticePath());
    const bar = el('div', null, 'toolbar'); bar.append(button('Mark all as read', async () => { await post(noticePath() + '/read', {}); await navigate('notifications', false); setBell(0); }, 'btn sm'));
    box.append(bar);
    if (!d.notifications.length) { box.append(empty('No notifications yet', 'You will see updates here when something changes.')); return box; }
    const list = el('div', null, 'record-list');
    d.notifications.forEach(n => {
      const item = el('article', null, 'notice-item' + (n.state === 'unread' ? ' unread' : ''));
      item.append(el('strong', n.title), el('span', n.body, 'small'), el('time', when(n.at)));
      if (n.link) { const go = el('button', 'Open', 'link-btn small'); go.type = 'button'; go.onclick = async () => { await post(noticePath() + '/read', { ids: [n.id] }); const u = new URL(n.link, location.origin); if (u.pathname === location.pathname) navigate(u.searchParams.get('view') || (STAFF_MODE ? 'staff' : 'chat')); else location.href = u.href; }; item.append(go); }
      list.append(item);
    });
    box.append(list); setBell(d.unread); return box;
  }
  $('bell').onclick = () => navigate('notifications');

  /* ------------------------------------------------------------ staff: inbox */
  function staffSignIn(box) { box.append(empty('Staff sign-in required', 'Use an account created by the deployment owner.', button('Sign in', account, 'btn primary sm'))); return box; }
  function ticketButton(t) {
    const b = el('button', null, 'ticket-btn'); b.type = 'button'; b.dataset.ticket = t.id; b.setAttribute('aria-current', String(t.id === activeTicket));
    const top = el('span', null, 'row'); top.append(el('strong', t.data.summary.slice(0, 90)));
    const tone = { waiting: 'warn', staff: '', bot: 'neutral', closed: 'neutral' }[t.state];
    b.append(top, el('small', ({ waiting: 'Waiting', staff: 'With staff', bot: 'Back with assistant', closed: 'Closed' }[t.state] || t.state) + ' · ' + (t.branch || 'any center') + ' · ' + when(t.created)));
    if (t.data.topic === 'organization') b.append(badge('Organization', 'neutral'));
    b.onclick = () => openTicket(t.id); b.classList.toggle('closed', t.state === 'closed'); void tone; return b;
  }
  async function staffView() {
    const box = el('div'); box.append(intro('Inbox', 'Customer requests from the website and LINE. Take over a case before replying; the assistant pauses while you do.'));
    if (!isStaff()) return staffSignIn(box);
    const [d, ops] = await Promise.all([api('/staff/inbox'), api('/staff/operations')]);
    const metrics = el('div', null, 'metric-grid');
    [['Open requests', d.metrics.open], ['Waiting for a person', d.tickets.filter(t => t.state === 'waiting').length], ['My cases', d.tickets.filter(t => t.data.assigned_to === user.id && t.state === 'staff').length], ['Appointments to confirm', ops.bookings.filter(b => b.state === 'requested').length]]
      .forEach(([name, count]) => { const m = el('div', null, 'metric'); m.append(el('strong', String(count)), el('span', name)); metrics.append(m); });
    const filters = el('div', null, 'toolbar');
    [['open', 'Open'], ['all', 'All']].forEach(([v, t]) => { const c = el('button', t, 'chip'); c.type = 'button'; c.setAttribute('aria-pressed', String(ticketFilter === v)); c.onclick = () => { ticketFilter = v; navigate('staff', false); }; filters.append(c); });
    filters.append(button('Refresh', () => navigate('staff', false), 'btn ghost sm'));
    const grid = el('div', null, 'staff-grid'), list = el('div', null, 'staff-list'), thread = el('div', null, 'staff-thread');
    list.id = 'staff-list'; thread.id = 'staff-thread'; list.setAttribute('aria-label', 'Requests');
    thread.append(empty('Select a request', 'Its conversation, related appointments and organization details appear here.'));
    const shown = d.tickets.filter(t => ticketFilter === 'all' || t.state !== 'closed').reverse();
    shown.forEach(t => list.append(ticketButton(t)));
    if (!shown.length) list.append(empty('The queue is clear', ticketFilter === 'open' ? 'No open requests.' : 'No requests yet.'));
    grid.append(list, thread); box.append(metrics, filters, grid);
    if (activeTicket && shown.some(t => t.id === activeTicket)) setTimeout(() => openTicket(activeTicket), 0);
    return box;
  }
  async function openTicket(id) {
    activeTicket = id;
    document.querySelectorAll('.ticket-btn').forEach(b => b.setAttribute('aria-current', String(b.dataset.ticket === id)));
    const thread = $('staff-thread'); if (!thread) return;
    let d, inq;
    try { [d, inq] = await Promise.all([api('/staff/tickets/' + id), api('/staff/tickets/' + id + '/inquiry')]); }
    catch (e) { thread.replaceChildren(empty('This case cannot be opened', e.message)); return; }
    const t = d.ticket, mine = t.data.assigned_to === user.id;
    const head = el('div', null, 'record-head'); head.append(el('h3', t.data.summary), badge({ waiting: 'Waiting', staff: mine ? 'You are replying' : 'With another staff member', bot: 'With assistant', closed: 'Closed' }[t.state] || t.state, t.state === 'waiting' ? 'warn' : 'neutral'));
    thread.replaceChildren(head);
    const controls = el('div', null, 'record-actions');
    const setState = (label, s, cls) => button(label, async () => { await post('/staff/tickets/' + id + '/state', { state: s }); notice(s === 'staff' ? 'You took over. The assistant is paused for this customer.' : s === 'bot' ? 'Returned to the assistant.' : 'Case closed.'); await openTicket(id); pollList(); }, cls);
    if (!(t.state === 'staff' && mine)) controls.append(setState('Take over', 'staff', 'btn sm primary'));
    if (t.state !== 'bot') controls.append(setState('Return to assistant', 'bot'));
    if (t.state !== 'closed') controls.append(setState('Close case', 'closed', 'btn sm ghost'));
    thread.append(controls);
    if (inq.inquiry) {
      const i = inq.inquiry.data, box = el('section', null, 'card stack-sm'); box.append(el('h4', 'Organization request'));
      const kv = el('dl', null, 'kv'); const row = (k, v) => kv.append(el('dt', k), el('dd', v || '—'));
      row('Organization', i.organization); row('Contact', i.contact_name + ' · ' + i.email); row('People', String(i.headcount)); row('Where', i.service_mode === 'onsite' ? 'Onsite at their workplace' : 'At a center'); row('Center', branchName(i.branch_id)); row('Preferred date', i.preferred_date); row('Interested in', (i.package_ids || []).join(', ')); row('Notes', i.notes);
      box.append(kv); thread.append(box);
    }
    if (inq.quotes.length || inq.inquiry || t.data.topic === 'organization') {
      const qs = el('section', null, 'stack-sm'); qs.append(el('h4', 'Quotations'));
      inq.quotes.slice().sort((a, b) => b.data.version - a.data.version).forEach(q => {
        const r = el('div', null, 'row small'); r.append(el('strong', 'v' + q.data.version), el('span', money(q.data.total_thb) + ' · ' + q.data.people + ' people · ' + q.data.date), badge(q.state, q.state === 'accepted' ? 'ok' : q.state === 'offered' ? 'warn' : 'neutral'), link('PDF', '/api/business/quotes/' + encodeURIComponent(q.id) + '/document.pdf', 'btn ghost sm'));
        qs.append(r);
      });
      if (!inq.quotes.some(q => q.state === 'accepted')) qs.append(button(inq.quotes.length ? 'Revise quotation (new version)' : 'Prepare quotation', () => quoteForm(id, inq), mine ? 'btn sm primary' : 'btn sm'));
      thread.append(qs);
    }
    const messages = el('div', null, 'staff-messages'); messages.setAttribute('aria-label', 'Conversation'); messages.setAttribute('aria-live', 'polite');
    d.conversation.messages.forEach(m => messages.append(messageNode({ ...m, action: null }, false)));
    if (!d.conversation.messages.length) messages.append(el('p', 'No chat messages. This case came from a form or appointment change.', 'small muted'));
    messages.dataset.version = JSON.stringify(d.conversation.messages);
    thread.append(messages);
    const form = el('form', null, 'form-grid'), text = el('textarea', null, 'input');
    text.setAttribute('aria-label', 'Staff reply'); text.required = true; text.maxLength = 4000; text.rows = 3;
    const canReply = t.state === 'staff' && mine; text.disabled = !canReply;
    text.placeholder = canReply ? 'Write to the customer…' : 'Take over the case to reply.';
    form.append(text, button('Send reply', async () => { if (!form.reportValidity()) return; await post('/staff/tickets/' + id + '/messages', { message: text.value }); text.value = ''; await openTicket(id); }, 'btn primary sm'));
    form.onsubmit = e => e.preventDefault();
    thread.append(form);
    if (d.bookings.length) {
      const bx = el('section', null, 'stack-sm'); bx.append(el('h4', 'This customer’s appointments'));
      d.bookings.slice().reverse().forEach(b => bx.append(staffBookingRow(b, () => openTicket(id))));
      thread.append(bx);
    }
  }
  async function quoteForm(ticketId, inq) {
    await loadBusiness();
    const latest = inq.quotes.slice().sort((a, b) => b.data.version - a.data.version)[0]?.data, i = inq.inquiry?.data || {};
    const f = el('form', null, 'form-grid'), pkg = field('Organization package', 'select');
    catalogCache.packages.filter(p => p.segment === 'organization' && p.active !== false).forEach(p => { const o = el('option', p.name + ' · ' + money(p.price_thb) + ' per person'); o.value = p.id; pkg.input.append(o); });
    pkg.input.value = latest?.package_id || (i.package_ids || [])[0] || pkg.input.value;
    const people = field('Number of people', 'number', latest?.people || i.headcount || 20); people.input.min = 20; people.input.max = 10000; people.input.required = true;
    const date = field('Service date', 'date', latest?.date || i.preferred_date || ''); date.input.required = true; date.input.min = bangkokDate(1);
    const tm = field('Start time', 'time', latest?.time || '09:00'); tm.input.required = true;
    const venue = field('Venue', 'text', latest?.venue || (i.service_mode === 'center' ? branchName(i.branch_id) : '')); venue.input.required = true; venue.input.maxLength = 250;
    const travel = field('Travel fee (THB)', 'number', latest?.travel_fee_thb ?? 0, 'Onsite only'); travel.input.min = 0; travel.input.max = 20000;
    const branch = field('Coordinating center', 'select'); branchCache.branches.forEach(b => { const o = el('option', b.name); o.value = b.id; branch.input.append(o); }); branch.input.value = latest?.branch_id || i.branch_id || user.branch || 'BKK01';
    const note = field('Note to customer', 'textarea', '', 'Optional, shown on the quotation'); note.input.maxLength = 500;
    const total = el('p', '', 'total');
    const calc = () => { const p = catalogCache.packages.find(x => x.id === pkg.input.value); total.textContent = p ? 'Total ' + money(p.price_thb * Number(people.input.value || 0) + Number(travel.input.value || 0)) : ''; };
    [pkg.input, people.input, travel.input].forEach(x => x.addEventListener('input', calc)); calc();
    const err = el('p', '', 'field-error'); err.hidden = true; err.setAttribute('role', 'alert');
    f.append(pkg.wrap, el('div', null, 'form-grid two'), venue.wrap, branch.wrap, note.wrap, total, err);
    f.children[1].append(people.wrap, travel.wrap, date.wrap, tm.wrap);
    f.append(el('p', inq.quotes.length ? 'Issuing creates a new version and supersedes the open one. The customer is notified.' : 'The customer is notified and can download and accept it.', 'small muted'),
      button('Issue quotation', async () => {
        err.hidden = true; if (!f.reportValidity()) return;
        try {
          await post('/staff/quotes', { ticket_id: ticketId, package_id: pkg.input.value, people: Number(people.input.value), date: date.input.value, time: tm.input.value, venue: venue.input.value, travel_fee_thb: Number(travel.input.value || 0), branch_id: branch.input.value, note: note.input.value });
          closeModal(); notice('Quotation issued to the customer.'); await openTicket(ticketId);
        } catch (e) { err.textContent = e.message; err.hidden = false; }
      }, 'btn primary'));
    f.onsubmit = e => e.preventDefault();
    modal(inq.quotes.length ? 'Revise quotation' : 'Prepare quotation', f);
  }

  /* ------------------------------------------------------------ staff: appointments */
  function staffBookingRow(b, after) {
    const d = b.data, r = el('article', null, 'record'), h = el('div', null, 'record-head');
    h.append(el('h3', d.items.map(i => i.name).join(' + ')), ...bookingBadges(b));
    const meta = el('div', null, 'record-meta'); meta.append(el('span', d.date + ' ' + d.time), el('span', branchName(b.branch)), el('span', money(d.total_thb)), el('span', d.organization ? 'Organization' : 'Pay: ' + (d.payment_method || 'center')), el('span', 'Ref ' + b.id.slice(-8)));
    r.append(h, meta);
    const act = el('div', null, 'record-actions');
    if (b.state === 'requested') {
      act.append(button('Confirm appointment', async () => { await post('/staff/bookings/' + b.id + '/decision', { decision: 'confirm' }); notice('Confirmed. The customer was notified.'); await after(); }, 'btn sm primary'),
        button('Decline', () => {
          const n = el('form', null, 'form-grid'), why = field('Reason shown to the customer', 'textarea'); why.input.required = true; why.input.maxLength = 500;
          n.append(why.wrap, button('Decline request', async () => { if (!n.reportValidity()) return; await post('/staff/bookings/' + b.id + '/decision', { decision: 'decline', note: why.input.value }); closeModal(); notice('Declined. The customer was notified.'); await after(); }, 'btn danger'));
          n.onsubmit = e => e.preventDefault(); modal('Decline appointment request', n);
        }, 'btn sm danger'));
    }
    if (b.state === 'confirmed' && d.payment_status === 'pending' && d.payment_method === 'center' && !d.active_txn)
      act.append(button('Record payment at center', () => {
        const n = el('div', null, 'stack'); n.append(el('p', `Confirm you received ${money(d.total_thb)} for this simulated appointment. This creates an auditable demo receipt.`),
          button('Confirm receipt', async () => { await post('/staff/bookings/' + b.id + '/settle'); closeModal(); notice('Payment recorded.'); await after(); }, 'btn primary'));
        modal('Record center payment', n);
      }));
    if (isManager() && d.payment_status === 'paid')
      act.append(button('Approve full refund', () => {
        const n = el('form', null, 'form-grid'), why = field('Reason'); why.input.required = true; why.input.minLength = 3;
        n.append(why.wrap, el('p', `Refund ${money(d.total_thb)}. Test payments are refunded through the simulator or provider test mode; center payments create a demo refund record.`, 'small muted'),
          button('Confirm refund', async () => { if (!n.reportValidity()) return; const res = await post('/staff/bookings/' + b.id + '/refund', { reason: why.input.value }); closeModal(); notice('Refund status: ' + res.status); await after(); }, 'btn danger'));
        n.onsubmit = e => e.preventDefault(); modal('Approve refund', n);
      }, 'btn sm danger'));
    if (act.children.length) r.append(act);
    return r;
  }
  async function operationsView() {
    const box = el('div'); box.append(intro('Appointments', 'Confirm or decline requests, record center payments and approve refunds. Capacity and prices are checked on the server.'));
    if (!isStaff()) return staffSignIn(box);
    await loadBusiness();
    const d = await api('/staff/operations');
    const bar = el('div', null, 'toolbar');
    [['requested', 'Awaiting confirmation'], ['confirmed', 'Confirmed'], ['closed', 'Declined or cancelled'], ['all', 'All']].forEach(([v, t]) => {
      const n = v === 'all' ? d.bookings.length : v === 'closed' ? d.bookings.filter(b => ['declined', 'cancelled'].includes(b.state)).length : d.bookings.filter(b => b.state === v).length;
      const c = el('button', t + ' (' + n + ')', 'chip'); c.type = 'button'; c.setAttribute('aria-pressed', String(opsFilter === v)); c.onclick = () => { opsFilter = v; navigate('operations', false); }; bar.append(c);
    });
    bar.append(button('Refresh', () => navigate('operations', false), 'btn ghost sm'));
    box.append(bar);
    const rows = d.bookings.filter(b => opsFilter === 'all' || (opsFilter === 'closed' ? ['declined', 'cancelled'].includes(b.state) : b.state === opsFilter))
      .sort((a, b) => (a.data.date + a.data.time).localeCompare(b.data.date + b.data.time));
    if (!rows.length) { box.append(empty('Nothing here', opsFilter === 'requested' ? 'No requests are waiting for confirmation.' : 'No appointments in this group.')); return box; }
    const list = el('div', null, 'record-list'); rows.forEach(b => list.append(staffBookingRow(b, () => navigate('operations', false)))); box.append(list);
    return box;
  }
  async function catalogAdmin() {
    const box = el('div'); box.append(intro('Catalog', 'Manager-only. Changes apply immediately to the website, the assistant and new previews. Confirmed appointments keep their agreed price.'));
    if (!isManager()) { box.append(empty('Manager access required', 'Ask a manager to change prices or availability.')); return box; }
    const d = await api('/staff/operations'); catalogCache = null;
    box.append(el('p', 'Catalog version ' + d.catalog.version, 'small muted'));
    const wrap = el('div', null, 'table-wrap'), table = el('table', null, 'data'), head = el('tr');
    ['Package', 'Segment', 'Price (THB)', 'Available', ''].forEach(h => head.append(el('th', h))); table.append(head);
    d.catalog.packages.forEach(p => {
      const tr = el('tr'), price = el('input', null, 'input'); price.type = 'number'; price.min = 1; price.max = 1000000; price.value = p.price_thb; price.setAttribute('aria-label', p.name + ' price in THB');
      const active = el('input'); active.type = 'checkbox'; active.checked = p.active !== false; active.setAttribute('aria-label', p.name + ' available');
      const status = el('span', '', 'tiny muted'); status.setAttribute('aria-live', 'polite');
      const save = button('Save package', async () => {
        if (!price.checkValidity()) { status.textContent = 'Enter 1–1,000,000.'; return; }
        const r = await api('/staff/catalog/' + p.id, { method: 'PUT', body: JSON.stringify({ price_thb: Number(price.value), active: active.checked }) });
        const fresh = await api('/catalog/search?segment=' + p.segment); const back = fresh.packages.find(x => x.id === p.id);
        status.textContent = back ? 'Saved · now ' + money(back.price_thb) + ' · ' + r.version : 'Saved · hidden from customers · ' + r.version;
      });
      const tdName = el('td'); tdName.append(el('strong', p.name), el('div', p.id, 'tiny muted'));
      const tdP = el('td'); tdP.append(price); const tdA = el('td'); tdA.append(active); const tdS = el('td'); tdS.append(save, status);
      tr.append(tdName, el('td', p.segment), tdP, tdA, tdS); table.append(tr);
    });
    wrap.append(table); box.append(wrap); return box;
  }
  async function channels() {
    const box = el('div'); box.append(intro('Channels and budget', 'Integration modes are decided by the server. Simulated channels run through the same adapters, queues and storage as real ones.'));
    if (!isManager()) { box.append(empty('Manager access required', '')); return box; }
    const [m, budget, out] = await Promise.all([api('/modes'), api('/staff/budget').catch(e => ({ error: e.message })), api('/staff/line-simulator/outbox')]);
    const t = el('div', null, 'table-wrap'), table = el('table', null, 'data'); const h = el('tr'); ['Integration', 'Mode'].forEach(x => h.append(el('th', x))); table.append(h);
    Object.values(m.modes).forEach(x => { const tr = el('tr'), td = el('td'); td.append(badge(x.mode.replaceAll('_', ' ').toLowerCase(), x.mode === 'LIVE_MODEL' || x.mode === 'PROVIDER_SANDBOX' ? 'ok' : x.mode === 'UNAVAILABLE' ? 'warn' : 'neutral')); tr.append(el('td', x.label), td); table.append(tr); });
    t.append(table);
    const b = el('section', null, 'card stack-sm'); b.append(el('h3', 'AI budget (project total)'));
    if (budget.error) b.append(el('p', budget.error, 'small'));
    else {
      const c = budget.cost, kv = el('dl', null, 'kv'); const row = (k, v) => kv.append(el('dt', k), el('dd', v));
      row('Cap', money(c.cap_thb) + ' for the whole project, not monthly'); row('Spent before this ledger', c.prior_spend_thb === null || c.prior_spend_thb === undefined ? 'Not set — paid AI calls are blocked' : money(c.prior_spend_thb));
      row('Settled in ledger', c.available ? c.settled_thb.toFixed(4) + ' THB' : 'Unavailable'); row('Reserved now', c.available ? c.reserved_thb.toFixed(4) + ' THB' : '—'); row('Remaining', c.remaining_thb === null || c.remaining_thb === undefined ? 'Unknown' : c.remaining_thb.toFixed(2) + ' THB');
      row('Calls', String(c.calls ?? 0)); row('Priced models', (c.priced_models || []).join(', ') || 'None configured'); row('Provider network', budget.network_enabled ? 'Enabled' : 'Disabled');
      b.append(kv);
    }
    const sim = el('section', null, 'card stack'); sim.append(el('h3', 'LINE channel simulator'), el('p', 'Sends a LINE-shaped, signed webhook event through the real verification, queue and worker. Replies are stored as simulated deliveries; nothing is sent to LINE.', 'small muted'));
    const f = el('form', null, 'form-grid'), uid = field('Simulated LINE user ID', 'text', 'Usim' + Math.random().toString(16).slice(2, 12)), text = field('Message', 'textarea');
    uid.input.pattern = 'Usim[0-9a-f]{8,32}'; text.input.required = true; text.input.maxLength = 2000;
    f.append(uid.wrap, text.wrap);
    const row = el('div', null, 'form-actions');
    row.append(button('Send as LINE user', async () => { if (!f.reportValidity()) return; const r = await post('/staff/line-simulator/events', { line_user_id: uid.input.value, text: text.input.value }); notice('Queued event ' + r.event_id.slice(-6) + '. Run the worker to process it.'); text.input.value = ''; await navigate('channels', false); }, 'btn primary sm'),
      button('Run worker once', async () => { const r = await post('/staff/line-simulator/run'); notice(r.processed ? 'Processed one job.' : r.failed ? 'The job failed; see its error code below.' : 'No pending jobs.'); await navigate('channels', false); }, 'btn sm'));
    f.append(row); f.onsubmit = e => e.preventDefault(); sim.append(f);
    const jt = el('div', null, 'table-wrap'), jtable = el('table', null, 'data'); const jh = el('tr'); ['Job', 'State', 'Error', 'Created'].forEach(x => jh.append(el('th', x))); jtable.append(jh);
    out.jobs.slice().reverse().forEach(j => { const tr = el('tr'); tr.append(el('td', j.kind + ' …' + j.id.slice(-6)), el('td', j.state), el('td', j.error_code || '—'), el('td', when(j.created))); jtable.append(tr); });
    if (!out.jobs.length) { const tr = el('tr'); const td = el('td', 'No LINE jobs yet.'); td.colSpan = 4; tr.append(td); jtable.append(tr); }
    jt.append(jtable);
    const dl = el('div', null, 'record-list'); out.deliveries.slice().reverse().forEach(x => { const r = el('article', null, 'notice-item'); r.append(el('strong', 'To ' + x.to), el('span', x.text, 'small'), el('time', when(x.at))); dl.append(r); });
    if (!out.deliveries.length) dl.append(el('p', 'No simulated deliveries yet.', 'small muted'));
    sim.append(el('h4', 'Jobs'), jt, el('h4', 'Simulated deliveries'), dl);
    box.append(t, b, sim); return box;
  }

  /* ------------------------------------------------------------ navigation */
  const TITLES = { chat: 'Conversation', packages: 'Health checks', book: 'Request an appointment', bookings: 'My appointments', reports: 'My reports', history: 'Past conversations', notifications: 'Notifications', staff: 'Inbox', operations: 'Appointments', 'catalog-admin': 'Catalog', channels: 'Channels and budget' };
  const FACTORIES = { packages, book: bookView, bookings, reports, history: historyView, notifications, staff: staffView, operations: operationsView, 'catalog-admin': catalogAdmin, channels };
  const mobile = matchMedia('(max-width:800px)');
  function setMenu(open) { $('sidebar').classList.toggle('open', open); $('sidebar').inert = mobile.matches && !open; $('menu-toggle').setAttribute('aria-expanded', String(open)); $('menu-toggle').setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation'); }
  async function navigate(next, push = true, params = {}) {
    if (!TITLES[next] || (STAFF_MODE && next === 'chat') || (!STAFF_MODE && ['operations', 'catalog-admin', 'channels'].includes(next))) next = STAFF_MODE ? 'staff' : 'chat';
    view = next; $('view-title').textContent = TITLES[next]; document.title = TITLES[next] + ' — ResultScope';
    document.querySelectorAll('.nav-item').forEach(b => { const on = b.dataset.view === next; b.classList.toggle('active', on); if (on) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
    setMenu(false);
    if (push) { const u = new URL(location.href); u.search = ''; if (next !== (STAFF_MODE ? 'staff' : 'chat')) u.searchParams.set('view', next); Object.entries(params).forEach(([k, v]) => u.searchParams.set(k, v)); window.history.pushState({ view: next }, '', u); }
    if ($('chat-view')) $('chat-view').hidden = next !== 'chat';
    $('content-view').hidden = next === 'chat';
    if (next === 'chat') { $('message').focus({ preventScroll: true }); return; }
    const content = $('content'); content.replaceChildren(el('div', null, 'skeleton')); content.setAttribute('aria-busy', 'true');
    try { content.replaceChildren(await FACTORIES[next](params)); }
    catch (e) { content.replaceChildren(empty('This view could not be loaded', e.message, button('Try again', () => navigate(next, false, params), 'btn sm'))); }
    finally { content.removeAttribute('aria-busy'); }
  }
  document.querySelectorAll('.nav-item[data-view]').forEach(b => { b.onclick = () => navigate(b.dataset.view); });
  $('menu-toggle').onclick = () => setMenu(!$('sidebar').classList.contains('open'));
  mobile.addEventListener('change', () => setMenu(false));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && $('sidebar').classList.contains('open')) { setMenu(false); $('menu-toggle').focus(); } });
  window.addEventListener('popstate', () => { const p = new URLSearchParams(location.search); navigate(p.get('view') || (STAFF_MODE ? 'staff' : 'chat'), false, Object.fromEntries(p)); });

  /* ------------------------------------------------------------ connection and linking */
  async function connection() {
    try {
      modes = (await api('/modes')).modes;
      const online = modes.assistant.mode === 'LIVE_MODEL';
      $('connection-state').textContent = online ? 'Assistant online' : 'Assistant offline';
      $('connection-state').className = 'status-pill ' + (online ? 'ok' : 'off');
    } catch { $('connection-state').textContent = 'Status unavailable'; }
  }
  $('connection-state').onclick = () => {
    const n = el('div', null, 'stack');
    n.append(el('p', modes?.assistant.mode === 'LIVE_MODEL' ? 'The conversation model is connected. Replies pass safety and evidence checks before they appear.' : 'The conversation model is not connected or is paused. Browsing, booking, payments, reports review and our team still work; AI replies will show a clear error instead of an invented answer.', 'small'));
    if (modes) { const ul = el('ul', null, 'plain small'); Object.values(modes).forEach(x => { const li = el('li'); li.append(el('span', x.label + ': '), badge(x.mode.replaceAll('_', ' ').toLowerCase(), 'neutral')); ul.append(li); }); n.append(ul); }
    const f = field('Demo access code for this tab', 'password', '', 'Only if the deployment owner gave you one');
    n.append(f.wrap, button('Use access code', () => { accessCode = f.input.value; f.input.value = ''; closeModal(); notice('Access code set for this tab only.'); }, 'btn sm'), link('Connection settings', '/settings', 'small'));
    modal('Assistant and integrations', n);
  };
  async function checkLink() {
    const token = new URLSearchParams(location.search).get('link'); if (!token || STAFF_MODE) return;
    if (!user?.registered) { requireAccount('Sign in or create an account first, then open the link from your LINE chat again.'); return; }
    const n = el('div', null, 'stack');
    n.append(el('p', 'Link this LINE identity to your account and import its reports, appointments and conversation. Continue only if you requested this invitation from your own LINE chat.'),
      button('Confirm account linking', async () => { await post('/account/line/link', { token, consent: true }); window.history.replaceState({}, '', '/app'); closeModal(); notice('Your LINE conversation is linked.'); await refresh(); }, 'btn primary'));
    modal('Link your LINE conversation', n);
  }
  async function applyDeepLinks(p) {
    if (STAFF_MODE) return;
    const pkgName = id => catalogCache?.packages.find(x => x.id === id)?.name || id;
    if (p.has('package') && !p.get('view')) { await loadBusiness(); $('message').value = `Tell me about ${pkgName(p.get('package'))} (${p.get('package')}). Is it suitable for me?`; }
    if (p.has('ask')) { await loadBusiness(); $('message').value = `I am interested in ${pkgName(p.get('ask'))} (${p.get('ask')}). Can your team review whether it is suitable for me?`; }
    if (p.has('compare')) { await loadBusiness(); const ids = p.get('compare').split(',').slice(0, 3); $('message').value = `Please compare ${ids.map(i => `${pkgName(i)} (${i})`).join(' and ')} for me. What is different and which fits a general check-up?`; }
    if (p.get('topic') === 'organization') $('message').value = 'I would like to arrange health checks for my organization.';
    if (p.get('team') === '1') requestStaff();
    if (p.get('payment') === 'return') notice('Returned from checkout. Payment status updates when the provider confirms it.');
    if (p.has('q') && p.get('q').trim()) {
      const q = p.get('q').slice(0, 2000); window.history.replaceState({}, '', '/app'); // a reload must not resend
      if (state?.conversation.mode === 'bot') send(q); else $('message').value = q;
    }
    if (['package', 'ask', 'compare', 'topic'].some(k => p.has(k)) && !p.get('view')) { window.history.replaceState({}, '', '/app'); $('message').focus(); }
  }
  async function init() {
    setMenu(false);
    const p = new URLSearchParams(location.search);
    try {
      const s = await api('/session'); csrf = s.csrf; updateUser(s.user);
      if (!STAFF_MODE) await refresh(); else setBell(0);
      await navigate(p.get('view') || view, false, Object.fromEntries(p));
      await checkLink(); await applyDeepLinks(p);
      if (STAFF_MODE && !isStaff()) account();
    } catch (e) { notice(e.message, 'bad'); if ($('chat-status')) $('chat-status').textContent = e.message; }
    connection(); pollBell();
  }
  async function pollList() {
    const list = $('staff-list'); if (!list || !isStaff()) return;
    const d = await api('/staff/inbox');
    const shown = d.tickets.filter(t => ticketFilter === 'all' || t.state !== 'closed').reverse();
    if (shown.length) list.replaceChildren(...shown.map(ticketButton));
  }
  async function pollStaff() {
    if (!isStaff() || $('modal').open) return;
    await pollList();
    if (activeTicket && $('staff-thread')) {
      const t = await api('/staff/tickets/' + activeTicket), messages = $('staff-thread').querySelector('.staff-messages');
      const content = JSON.stringify(t.conversation.messages);
      if (messages && messages.dataset.version !== content) { messages.replaceChildren(...t.conversation.messages.map(m => messageNode({ ...m, action: null }, false))); messages.dataset.version = content; messages.scrollTop = messages.scrollHeight; }
    }
  }
  init();
  setInterval(() => {
    if (document.hidden || busy || !csrf) return;
    if (view === 'chat' && !STAFF_MODE) refresh().catch(() => {});
    if (view === 'staff') pollStaff().catch(() => {});
  }, 4000);
  setInterval(() => { if (!document.hidden && csrf) pollBell(); }, 20000);
})();
