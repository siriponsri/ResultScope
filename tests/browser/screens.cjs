/* Design-approval screenshot bundle.
   Drives the real UI against tests/browser/screens_server.py (real routes, storage, permissions and
   state machines; scripted assistant/OCR doubles). Screens are produced by real clicks and API calls
   in the order a customer and the staff would make them.
   MOCKED_TEST_ONLY: assistant text and OCR values are scripted for layout review, not quality evidence.
   Usage: TEST_PYTHON=/path/to/python node tests/browser/screens.cjs   (SCREENS_OUT to change the folder;
          SCREENS_BASE=http://127.0.0.1:8098 to reuse a server that is already running) */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { spawn } = require('child_process'), fs = require('fs'), path = require('path'), os = require('os');
const root = path.resolve(__dirname, '../..');
const out = path.resolve(root, process.env.SCREENS_OUT || 'docs/evidence/cowork-20261006/screens'); fs.mkdirSync(out, { recursive: true });
const port = Number(process.env.UI_TEST_PORT || 8099); let base = process.env.SCREENS_BASE || 'http://127.0.0.1:' + port;
const py = process.env.TEST_PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const wait = ms => new Promise(r => setTimeout(r, ms));
const shots = [], problems = []; let server = null;
const PASSWORD = 'ui-test-only-password';

async function shot(page, id, title, note = '', full = false) {
  await wait(250); await page.evaluate(() => { const t = document.getElementById('notice'); if (t) t.hidden = true; }); // toasts are real but cover content
  const file = id + '.png'; await page.screenshot({ path: path.join(out, file), fullPage: full });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
  shots.push({ id, file, title, note, width: page.viewportSize().width, overflow });
  if (overflow) problems.push(id + ': horizontal overflow');
}
let debugPages = [];
async function step(name, fn) { try { await fn(); } catch (e) { problems.push(name + ': ' + e.message.split('\n')[0]); console.error('STEP FAILED', name, e.message.split('\n')[0]); if (process.env.SCREENS_DEBUG) for (const [i, p] of debugPages.entries()) await p.screenshot({ path: path.join(out, 'fail-' + name + '-' + i + '.png') }).catch(() => {}); } }
function watch(page, label) { page.on('pageerror', e => problems.push(label + ' pageerror: ' + e.message)); page.on('console', m => { if (m.type() === 'error' && !/status of (4\d\d|502)|net::ERR/.test(m.text())) problems.push(label + ' console: ' + m.text()); }); }
async function api(page, p, body, method) {
  return page.evaluate(async ([p, body, method]) => {
    const s = await (await fetch('/api/business/session', { credentials: 'same-origin' })).json();
    const r = await fetch('/api/business' + p, { method: method || (body ? 'POST' : 'GET'), credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-Business-CSRF': s.csrf }, body: body ? JSON.stringify(body) : undefined });
    const d = await r.json(); if (!r.ok) throw Error(p + ' ' + r.status + ' ' + JSON.stringify(d)); return d;
  }, [p, body, method]);
}
function openDay(days) { const d = new Date(Date.now() + 7 * 3600e3 + days * 86400e3); while (d.getUTCDay() === 0) d.setUTCDate(d.getUTCDate() + 1); return d.toISOString().slice(0, 10); }
async function signUp(page, email) {
  await page.locator('#account-open').click();
  await page.getByLabel('Email address').fill(email); await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
  await page.getByRole('button', { name: 'Create account', exact: true }).click(); await page.locator('#modal').waitFor({ state: 'hidden' });
}
async function signIn(page, email) {
  await page.getByLabel('Email address').fill(email); await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
  await page.locator('#modal').getByRole('button', { name: 'Sign in', exact: true }).click(); await page.locator('#modal').waitFor({ state: 'hidden' });
}
async function ask(page, text) {
  const before = await page.locator('#messages .turn.ai').count();
  await page.locator('#message').fill(text); await page.locator('#send').click();
  await page.waitForFunction(n => document.querySelectorAll('#messages .turn.ai').length > n || document.querySelector('#messages .turn.user .callout.bad'), before, { timeout: 15000 });
  await wait(300);
}
async function view(page, v) { const nav = page.locator(`.nav-item[data-view="${v}"]`); if (await nav.count()) await nav.first().evaluate(b => b.click()); else if (v === 'notifications') await page.locator('#bell').click(); else await page.goto(base + (page.url().includes('/staff') ? '/staff' : '/app') + '?view=' + v, { waitUntil: 'networkidle' }); await page.locator('#content [aria-busy]').waitFor({ state: 'detached' }).catch(() => {}); await wait(400); }

(async () => {
  let tmp;
  if (!process.env.SCREENS_BASE) {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'resultscope-screens-'));
    server = spawn(py, ['tests/browser/screens_server.py'], { cwd: root, env: { ...process.env, UI_TEST_PORT: String(port), APP_ENV: 'test', PROVIDER_NETWORK_ENABLED: 'false', BUSINESS_DB_PATH: path.join(tmp, 'db.sqlite'), BUSINESS_KEY_PATH: path.join(tmp, 'key'), BUSINESS_DATA_KEY: '', DATABASE_URL: '', VERCEL: '', RENDER: '', BUSINESS_EXTERNAL_ENABLED: '', STRIPE_SECRET_KEY: '', LINE_CHANNEL_SECRET: '', LINE_CHANNEL_ACCESS_TOKEN: '' }, stdio: ['ignore', 'ignore', 'pipe'] });
    let log = ''; server.stderr.on('data', x => { log += x; });
    for (let i = 0; i < 80; i++) { try { if ((await fetch(base + '/health')).ok) break; } catch { } await wait(250); if (i === 79) throw Error('server unavailable ' + log.slice(-800)); }
  }
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const desk = { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 };
  const phone = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true };
  const C = await (await browser.newContext(desk)).newPage(); watch(C, 'customer');
  const S = await (await browser.newContext(desk)).newPage(); watch(S, 'staff');
  debugPages = [C, S];
  const day1 = openDay(3), day2 = openDay(4), day3 = openDay(6);

  /* ---------------- public website */
  await step('public', async () => {
    for (const [id, p, title, full] of [['01-home', '/', 'Home', true], ['02-catalog', '/packages', 'Health checks catalog', true], ['04-package', '/packages/P02', 'Package detail', true],
      ['05-compare', '/compare?ids=P01,P02,P03', 'Compare three packages', true], ['06-centers', '/centers', 'Centers', true], ['07-organizations', '/organizations', 'Organizations and quotation request', true],
      ['08-help', '/help', 'Help and policies', true], ['09-sources', '/sources', 'Medical sources the assistant may cite', false], ['10-privacy', '/privacy', 'Privacy', false], ['11-not-found', '/no-such-page', 'Page not found', false]]) {
      await C.goto(base + p, { waitUntil: 'networkidle' }); await shot(C, id, title, '', full);
    }
    await C.goto(base + '/packages?q=zzz', { waitUntil: 'networkidle' }); await shot(C, '03-catalog-empty', 'Catalog: no results state', 'Search with no match keeps filters and offers reset and the assistant.');
    await C.goto(base + '/packages', { waitUntil: 'networkidle' });
    for (const id of ['P01', 'P02']) await C.locator(`[data-compare="${id}"]`).check();
    await shot(C, '02b-compare-tray', 'Catalog: compare tray after choosing two packages');
  });
  await step('dock', async () => {
    await C.goto(base + '/packages/P02', { waitUntil: 'networkidle' });
    await C.locator('.dock-launch').click(); await C.locator('.dock textarea').fill('Which check fits about ฿1,500?'); await C.locator('.dock .send-btn').click();
    await C.locator('.dock .turn.ai').first().waitFor({ timeout: 15000 }); await wait(400);
    await shot(C, '12-dock-answer', 'Assistant dock on a package page', 'Answer cites catalog records; shortcuts open compare or prefill a booking. Scripted reply.');
  });

  /* ---------------- customer workspace */
  await step('workspace-welcome', async () => {
    await C.goto(base + '/app', { waitUntil: 'networkidle' }); await api(C, '/new-chat', {});
    await C.goto(base + '/app', { waitUntil: 'networkidle' });
    await shot(C, '20-app-welcome', 'Conversation: first visit', 'Guest session; suggestions are real prompts; links skip the chat entirely.');
    await C.locator('#account-open').click(); await C.locator('#modal').waitFor(); await shot(C, '21-account-dialog', 'Sign in or create an account');
    await C.locator('#modal-close').click(); await signUp(C, 'malee@example.invalid');
  });
  await step('chat-advisor', async () => {
    await ask(C, 'Which check fits about ฿1,500?');
    await C.locator('#messages .act', { hasText: 'How this was checked' }).last().click();
    await shot(C, '22-chat-advisor', 'Answer with sources, shortcuts and the verification receipt', 'Receipt lists the checks that ran before the answer was shown. Scripted reply.');
    await C.locator('#messages .act', { hasText: 'Compare packages' }).last().click(); await C.locator('#canvas table').waitFor();
    await shot(C, '23-chat-compare', 'Comparison panel opened from the answer', 'Highlighted column is the package the user asked about, not a popularity badge.');
    await C.keyboard.press('Escape');
    await ask(C, 'What does a lipid profile measure?');
    await C.locator('#messages .act', { hasText: /View \d+ sources/ }).last().click();
    await shot(C, '24-chat-explainer', 'Report Explainer answer with numbered references', 'Inline numbers match the source list. Scripted reply.');
  });
  await step('report', async () => {
    await view(C, 'reports'); await shot(C, '25-reports-empty', 'My reports: empty state');
    await C.getByRole('button', { name: 'Try a synthetic sample' }).click(); await C.locator('#modal .record').first().waitFor();
    await shot(C, '26-sample-picker', 'Synthetic sample reports');
    await C.locator('#modal').getByRole('button', { name: 'Read this sample' }).first().click(); await C.locator('#modal-title', { hasText: 'Review report fields' }).waitFor();
    await C.getByLabel('Report label').fill('Annual check, September 2026');
    await shot(C, '27-report-review', 'Review every extracted value before use', 'OCR values here come from a scripted double.');
    await C.locator('#modal input[type=checkbox]').check(); await C.locator('#modal').getByRole('button', { name: 'Confirm and use report' }).click();
    await C.locator('#modal').waitFor({ state: 'hidden' }); await C.locator('#chat-view').waitFor({ state: 'visible' });
    await ask(C, 'ช่วยอธิบายค่าน้ำตาลและ LDL ในรายงานของฉัน');
    await C.locator('#messages .turn.ai').last().scrollIntoViewIfNeeded();
    await shot(C, '28-chat-report-values', 'Report values drawn on the range printed on the user\'s own report', 'Thai reply; values were matched exactly to the confirmed report. Scripted reply.');
    await C.locator('#attach').click(); await shot(C, '29-attach-menu', 'Add a report from the composer'); await C.keyboard.press('Escape');
  });
  await step('booking', async () => {
    await C.goto(base + '/app?view=book&package=P01', { waitUntil: 'networkidle' }); await wait(500);
    await C.getByLabel('Center').selectOption('BKK01'); await C.getByLabel('Date').fill(day1); await C.getByLabel('Date').dispatchEvent('change');
    await C.locator('.slot:not([disabled])').first().waitFor(); await C.locator('.slot:not([disabled])').nth(3).click();
    await shot(C, '30-book', 'Request a time', 'Live capacity per half-hour; the server rechecks price and capacity on submit.');
    await C.getByRole('button', { name: 'Send appointment request' }).click(); await C.locator('#content .record').first().waitFor();
    await api(C, '/bookings', { package_ids: ['P02'], branch_id: 'BKK01', date: day2, time: '10:00', idempotency_key: 'screens-booking-0002' });
    await api(C, '/bookings', { package_ids: ['P03'], branch_id: 'BKK01', date: day3, time: '08:30', idempotency_key: 'screens-booking-0003' });
    await C.goto(base + '/app?view=bookings', { waitUntil: 'networkidle' }); await wait(500);
    await shot(C, '31-bookings-requested', 'My appointments: three requests awaiting confirmation');
  });
  await step('second-customer', async () => {
    const D = await (await browser.newContext(desk)).newPage(); watch(D, 'customer2');
    await D.goto(base + '/app', { waitUntil: 'networkidle' }); await signUp(D, 'hr@northwind.example.invalid');
    await api(D, '/bookings', { package_ids: ['P01'], branch_id: 'BKK01', date: day2, time: '13:00', idempotency_key: 'screens-booking-d001' });
    await api(D, '/organizations/inquiries', { organization: 'Northwind Trading', contact_name: 'Anong P.', headcount: 45, service_mode: 'onsite', branch_id: 'BKK01', preferred_date: openDay(14), package_ids: ['P17'], notes: 'Two shifts; morning and afternoon.' });
    await api(D, '/handoffs', { summary: 'Can your team bring the onsite unit for a night shift?' });
    await D.context().close();
  });

  /* ---------------- staff */
  await step('staff-overview', async () => {
    await S.goto(base + '/staff', { waitUntil: 'networkidle' }); await S.locator('#modal').waitFor();
    await shot(S, '40-staff-signin', 'Staff sign-in');
    await signIn(S, 'staff@example.invalid'); await wait(600);
    await shot(S, '41-staff-overview', 'Overview: requests that wait for a person come first', 'Confirm and decline are the real actions; numbers are computed from stored records.', true);
    const rows = S.locator('.decide .record');
    await rows.first().getByRole('button', { name: 'Confirm appointment' }).click(); await wait(800);
    await S.locator('.decide .record').first().getByRole('button', { name: 'Confirm appointment' }).click(); await wait(800);
    await S.locator('.decide .record').first().getByRole('button', { name: 'Decline' }).click();
    await S.getByLabel('Reason shown to the customer').fill('The Ari center is fully staffed for onsite work that morning. Please choose another time.');
    await shot(S, '42-staff-decline', 'Declining a request asks for a reason the customer will see');
    await S.locator('#modal').getByRole('button', { name: 'Decline request' }).click(); await S.locator('#modal').waitFor({ state: 'hidden' });
  });
  await step('customer-pay', async () => {
    await C.goto(base + '/app?view=bookings', { waitUntil: 'networkidle' }); await wait(500);
    await shot(C, '32-bookings-confirmed', 'My appointments after staff decisions', 'Confirmed, declined with the reason, and payment options that open only after confirmation.', true);
    await C.getByRole('button', { name: 'Pay with test PromptPay' }).first().click(); await C.waitForURL(/\/pay\/sim\//); await C.locator('.qr-sim').waitFor();
    await shot(C, '33-pay-sim', 'Payment simulator (signed test events, no real money)');
    await C.getByRole('button', { name: 'Simulate successful payment' }).click(); await C.locator('.badge.ok').first().waitFor();
    await shot(C, '34-pay-sim-done', 'Payment simulator after a successful signed event');
    await C.goto(base + '/app?view=bookings', { waitUntil: 'networkidle' }); await wait(400);
    const pc = C.getByRole('button', { name: 'Pay at the center' }); if (await pc.count()) { await pc.first().click(); await wait(600); }
  });
  await step('handoff', async () => {
    await C.goto(base + '/app', { waitUntil: 'networkidle' });
    await C.locator('#staff-request').click(); await C.getByLabel('How can our team help?').fill('Can I bring my previous report from another lab to the visit?');
    await shot(C, '35-handoff-dialog', 'Talk to our team');
    await C.locator('#modal').getByRole('button', { name: 'Send to our team' }).click(); await C.locator('#modal').waitFor({ state: 'hidden' }); await wait(500);
  });
  await step('staff-inbox', async () => {
    await S.goto(base + '/staff?view=staff', { waitUntil: 'networkidle' }); await wait(700);
    await S.locator('.ticket-btn', { hasText: 'previous report' }).click(); await S.locator('.staff-thread > .record-head').waitFor();
    await S.getByRole('button', { name: 'Take over' }).click(); await wait(600);
    await S.getByLabel('Staff reply').fill('Yes, please bring it. The nurse will note it at check-in; we do not combine results from different labs.');
    await S.getByRole('button', { name: 'Send reply' }).click(); await wait(700);
    await S.evaluate(() => scrollTo(0, 0)); await shot(S, '43-staff-inbox', 'Inbox: a case taken over by staff, the assistant paused for this customer');
    await S.locator('.ticket-btn', { hasText: 'Northwind' }).first().click(); await S.locator('.staff-thread h4', { hasText: 'Organization request' }).waitFor();
    await S.getByRole('button', { name: 'Take over' }).click(); await wait(500);
    await S.getByRole('button', { name: /Prepare quotation/ }).click(); await S.locator('#modal-title', { hasText: 'quotation' }).waitFor();
    await S.getByLabel('Travel fee (THB)').fill('1500'); await S.getByLabel('Venue').fill('Northwind Trading, Silom Road office, 12th floor');
    await shot(S, '44-staff-quote', 'Preparing a versioned quotation for an organization');
    await S.locator('#modal').getByRole('button', { name: 'Issue quotation' }).click(); await S.locator('#modal').waitFor({ state: 'hidden' }); await wait(500);
  });
  await step('customer-after', async () => {
    await C.goto(base + '/app', { waitUntil: 'networkidle' }); await wait(500);
    await shot(C, '36-chat-staff-reply', 'The staff reply in the customer conversation');
    await view(C, 'notifications'); await shot(C, '37-notifications', 'Notifications created by real events');
    await view(C, 'packages'); await shot(C, '38-app-packages', 'Health checks inside the workspace');
  });
  await step('staff-views', async () => {
    for (const [v, id, title, full] of [['overview', '45-staff-overview-after', 'Overview after the day\'s decisions', true], ['operations', '46-staff-appointments', 'Appointments', false], ['customers', '47-staff-customers', 'Customers', false], ['payments', '49-staff-payments', 'Payments', false],
      ['catalog-admin', '50-staff-catalog', 'Catalog and prices (manager)', false], ['centers', '51-staff-centers', 'Centers and capacity (manager)', false], ['roles', '52-staff-roles', 'Assistant roles (manager)', false], ['channels', '53-staff-channels', 'Channels, LINE simulator and AI budget (manager)', true], ['audit', '54-staff-audit', 'Audit log (manager)', false]]) {
      await view(S, v);
      if (v === 'operations') { await S.locator('#content').getByRole('button', { name: /^All \(/ }).click(); await wait(700); }
      await shot(S, id, title, '', full);
      if (v === 'customers') { await S.locator('table.data .link-btn', { hasText: 'malee' }).click(); await S.locator('#modal .history-block').first().waitFor(); await shot(S, '48-staff-customer', 'Customer history', 'Report values and chat text are not shown here.'); await S.locator('#modal-close').click(); }
    }
  });

  /* ---------------- phone */
  await step('phone', async () => {
    const P = await (await browser.newContext(phone)).newPage(); watch(P, 'phone');
    for (const [id, p, title] of [['60-m-home', '/', 'Home'], ['61-m-catalog', '/packages', 'Catalog'], ['62-m-package', '/packages/P02', 'Package detail']]) { await P.goto(base + p, { waitUntil: 'networkidle' }); await shot(P, id, 'Phone: ' + title); }
    await P.locator('.nav-toggle').click(); await shot(P, '63-m-menu', 'Phone: menu'); await P.locator('.nav-toggle').click();
    await P.locator('.dock-launch').click(); await P.locator('.dock textarea').fill('What does a lipid profile measure?'); await P.locator('.dock .send-btn').click();
    await P.locator('.dock .turn.ai').first().waitFor({ timeout: 15000 }); await shot(P, '64-m-dock', 'Phone: assistant dock');
    await P.goto(base + '/app', { waitUntil: 'networkidle' }); await signUp(P, 'phone@example.invalid');
    await ask(P, 'Which check fits about ฿1,500?'); await shot(P, '65-m-chat', 'Phone: conversation');
    await P.locator('#messages .act', { hasText: 'Compare packages' }).last().click(); await P.locator('#canvas table').waitFor(); await shot(P, '66-m-compare', 'Phone: comparison panel'); await P.keyboard.press('Escape');
    await ask(P, 'UI_TEST_FAIL_ONCE'); await shot(P, '67-m-retry', 'Phone: a failed turn keeps the message and offers Retry');
    await P.goto(base + '/app?view=book&package=P02', { waitUntil: 'networkidle' }); await wait(500);
    await P.getByLabel('Center').selectOption('BKK01'); await P.getByLabel('Date').fill(day1); await P.getByLabel('Date').dispatchEvent('change'); await P.locator('.slot:not([disabled])').first().waitFor();
    await P.locator('.slot:not([disabled])').nth(5).click(); await shot(P, '68-m-book', 'Phone: request a time', '', true);
    const PS = await (await browser.newContext(phone)).newPage(); watch(PS, 'phone-staff');
    await PS.goto(base + '/staff', { waitUntil: 'networkidle' }); await PS.locator('#modal').waitFor(); await signIn(PS, 'staff@example.invalid'); await wait(600);
    await shot(PS, '69-m-staff-overview', 'Phone: staff overview', '', true);
    await PS.locator('#menu-toggle').click(); await wait(300); await shot(PS, '70-m-staff-menu', 'Phone: staff navigation');
  });

  fs.writeFileSync(path.join(out, 'screens.json'), JSON.stringify({ generated_at: new Date().toISOString(), label: 'MOCKED_TEST_ONLY: real UI and server; scripted assistant/OCR text', shots, problems }, null, 2));
  console.log(JSON.stringify({ shots: shots.length, problems }, null, 2));
  await browser.close(); if (server) server.kill();
})().catch(e => { console.error(e); if (server) server.kill(); process.exit(1); });
