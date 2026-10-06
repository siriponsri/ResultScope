'use strict';
/* Light and dark theme. Loaded in <head> without defer so the chosen theme applies before first paint.
   No stored choice = follow the system setting. Storage can be blocked; the page still works. */
(() => {
  const KEY = 'rs-theme', root = document.documentElement;
  let saved = null; try { saved = localStorage.getItem(KEY); } catch { /* storage blocked */ }
  if (saved === 'light' || saved === 'dark') root.dataset.theme = saved;
  const current = () => root.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  function label(btn) { const next = current() === 'dark' ? 'light' : 'dark'; btn.setAttribute('aria-label', 'Switch to ' + next + ' theme'); btn.title = 'Switch to ' + next + ' theme'; }
  function bind() {
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      label(btn);
      btn.addEventListener('click', () => {
        const next = current() === 'dark' ? 'light' : 'dark'; root.dataset.theme = next;
        try { localStorage.setItem(KEY, next); } catch { /* the choice lasts for this page only */ }
        document.querySelectorAll('[data-theme-toggle]').forEach(label);
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind); else bind();
  window.RSTheme = { current };
})();
