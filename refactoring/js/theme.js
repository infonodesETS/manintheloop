'use strict';

// ── Theme toggle (dark ↔ light) ──────────────────────────────────────────────
// Dark is the default. Preference is persisted in localStorage.

const STORAGE_KEY = 'mitl-theme';
const LIGHT = 'light';

function applyTheme(theme) {
  if (theme === LIGHT) {
    document.documentElement.setAttribute('data-theme', LIGHT);
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
}

function updateButton(btn, theme) {
  btn.textContent = theme === LIGHT ? '◑ DARK' : '◑ LIGHT';
  btn.title = theme === LIGHT ? 'Switch to dark mode' : 'Switch to light mode';
}

export function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY);
  const initial = saved === LIGHT ? LIGHT : 'dark';
  applyTheme(initial);

  const btn = document.getElementById('theme-toggle');
  if (!btn) return;

  updateButton(btn, initial);

  btn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') === LIGHT ? LIGHT : 'dark';
    const next = current === LIGHT ? 'dark' : LIGHT;
    applyTheme(next);
    updateButton(btn, next);
    localStorage.setItem(STORAGE_KEY, next);
  });
}
