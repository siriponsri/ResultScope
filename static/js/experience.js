/* Presentation only. Provider calls and report state remain owned by chat.js. */
(() => {
  const workspace = document.getElementById('workspace');
  const hero = document.querySelector('.hero-content');
  const shell = document.querySelector('.workspace-shell');
  const drawer = document.getElementById('document-drawer');
  const mobile = matchMedia('(max-width: 760px)');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const triggers = [...document.querySelectorAll('[data-open-report]')];
  const background = [document.querySelector('.app-header'), document.querySelector('.landing'), document.querySelector('.workspace-header'), document.querySelector('.demo-notice'), document.getElementById('chat-pane'), document.getElementById('report-context'), document.querySelector('.app-footer')].filter(Boolean);
  let returnFocus = null, timeline = null, scheduled = false, previewURL = null, busy = false;
  const fileInput = document.getElementById('image-input');
  const preview = document.createElement('img');
  preview.className = 'image-preview selected-report-preview';
  preview.alt = 'Selected report preview; values have not been confirmed';
  preview.hidden = true;
  document.getElementById('image-status').after(preview);
  const contextHint = document.createElement('p');
  contextHint.className = 'upload-help';
  contextHint.textContent = 'Start a new analysis to attach a different report.';
  contextHint.hidden = true;
  fileInput.after(contextHint);

  function enterWorkspace() {
    workspace.scrollIntoView({behavior: reduced.matches ? 'auto' : 'smooth', block:'start'});
    workspace.focus({preventScroll:true});
  }
  document.querySelectorAll('[data-enter-workspace]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); history.replaceState(null, '', '#workspace'); enterWorkspace();
  }));
  document.getElementById('hero-example').addEventListener('click', () => {
    enterWorkspace();
    window.dispatchEvent(new Event('resultscope:hero-example'));
  });
  function syncMotion() {
    if (!timeline || scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      const end = Math.max(1, workspace.offsetTop - 50);
      timeline?.progress(Math.max(0, Math.min(1, scrollY / end)));
    });
  }
  function configureMotion() {
    timeline?.kill(); timeline = null;
    hero.style.removeProperty('transform'); hero.style.removeProperty('opacity'); shell.style.removeProperty('transform');
    window.__timelines = window.__timelines || {};
    delete window.__timelines['resultscope-entry'];
    if (window.gsap && !reduced.matches && !mobile.matches) {
      timeline = window.gsap.timeline({paused:true});
      timeline.to(hero, {scale:.88, opacity:0, y:-24, duration:1, ease:'none'}, 0);
      timeline.fromTo(shell, {scale:1.035}, {scale:1, duration:1, ease:'none'}, 0);
      window.__timelines['resultscope-entry'] = timeline;
      syncMotion();
    }
  }
  function syncDialog() {
    const modal = !drawer.hidden && mobile.matches;
    drawer.setAttribute('role', modal ? 'dialog' : 'complementary');
    if (modal) drawer.setAttribute('aria-modal', 'true'); else drawer.removeAttribute('aria-modal');
    background.forEach(node => { node.inert = modal; });
    document.body.classList.toggle('drawer-open', modal);
  }
  function openDrawer(trigger) {
    returnFocus = trigger || document.activeElement;
    drawer.hidden = false;
    triggers.forEach(node => node.setAttribute('aria-expanded', 'true'));
    syncDialog();
    document.getElementById('close-report').focus({preventScroll:mobile.matches});
  }
  function closeDrawer(restore = true) {
    drawer.hidden = true;
    triggers.forEach(node => node.setAttribute('aria-expanded', 'false'));
    syncDialog();
    if (restore && returnFocus?.isConnected && !returnFocus.closest('.hidden')) returnFocus.focus({preventScroll:true});
  }
  triggers.forEach(node => node.addEventListener('click', () => openDrawer(node)));
  document.getElementById('close-report').addEventListener('click', () => closeDrawer());
  document.getElementById('return-to-chat').addEventListener('click', () => {
    closeDrawer(false);
    document.getElementById(document.body.dataset.view === 'analysis' ? 'followup-input' : 'message-input').focus();
  });
  document.addEventListener('keydown', event => {
    if (drawer.hidden) return;
    if (event.key === 'Escape') {event.preventDefault(); event.stopImmediatePropagation(); closeDrawer(); return;}
    if (event.key === 'Tab' && mobile.matches) {
      const focusable = [...drawer.querySelectorAll('button:not(:disabled), input:not(:disabled), a[href], [tabindex="0"]')].filter(el => el.getClientRects().length);
      const first = focusable[0], last = focusable.at(-1);
      if (event.shiftKey && document.activeElement === first) {event.preventDefault(); last?.focus();}
      else if (!event.shiftKey && document.activeElement === last) {event.preventDefault(); first?.focus();}
    }
  }, true);
  function syncContext() {
    const active = document.body.dataset.view === 'analysis';
    fileInput.disabled = busy || active;
    contextHint.hidden = !active;
    const discard = drawer.querySelector('.image-review-actions .secondary-button');
    if (discard) discard.disabled = active || busy;
  }
  window.addEventListener('resultscope:viewchange', syncContext);
  window.addEventListener('resultscope:busy', event => {busy = event.detail.busy; syncContext();});
  window.addEventListener('resultscope:report', event => {
    const {file, state} = event.detail;
    const summary = document.getElementById('file-summary');
    summary.hidden = !file;
    document.getElementById('file-name').textContent = file?.name || '';
    document.getElementById('file-size').textContent = file ? `${(file.size / 1024).toFixed(1)} KB ยท ${file.type === 'image/png' ? 'PNG' : 'JPEG'}` : '';
    document.getElementById('drawer-empty').hidden = Boolean(file);
    document.querySelectorAll('[data-report-label]').forEach(node => {node.textContent = file ? 'Your report' : 'Report';});
    if (previewURL) URL.revokeObjectURL(previewURL);
    previewURL = null; preview.hidden = true; preview.removeAttribute('src');
    if (file && state === 'loading' && ['image/jpeg', 'image/png'].includes(file.type)) {
      previewURL = URL.createObjectURL(file); preview.src = previewURL; preview.hidden = false;
    }
    syncContext();
  });
  window.addEventListener('resultscope:confirmed', () => {if (mobile.matches) closeDrawer(false);});
  window.addEventListener('scroll', syncMotion, {passive:true});
  window.addEventListener('resize', syncMotion, {passive:true});
  mobile.addEventListener('change', () => {syncDialog(); configureMotion();});
  reduced.addEventListener('change', configureMotion);
  configureMotion(); syncContext();
})();
