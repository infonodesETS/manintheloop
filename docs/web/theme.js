const _THEME_KEY   = 'mitl-theme';
const _THEME_PARAM = 'theme';

function _currentTheme() {
  return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
}

function applyTheme(value) {
  if (value === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  syncThemeBtn();
  // Quasi tutto il sito cambia tema da solo, perché i colori arrivano dalle
  // variabili CSS. Non chi disegna via JavaScript (Cytoscape nella Rete): quei
  // colori sono letti una volta sola, quindi va avvisato per rileggerli.
  document.dispatchEvent(new CustomEvent('mitl-theme-change', {
    detail: { theme: _currentTheme() }
  }));
}

function syncThemeBtn() {
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = _currentTheme() === 'light' ? '◑ DARK' : '◑ LIGHT';
}

function _themeUrl(theme) {
  const p = new URLSearchParams(location.search);
  if (theme === 'light') { p.set(_THEME_PARAM, 'light'); } else { p.delete(_THEME_PARAM); }
  const qs = p.toString();
  return qs ? `${location.pathname}?${qs}` : location.pathname;
}

// Returns '&theme=light' or '' — use in dynamic cross-page link builders
function themeParam() {
  return _currentTheme() === 'light' ? `&${_THEME_PARAM}=light` : '';
}

function updateNavLinks(theme) {
  document.querySelectorAll('a.tnav-btn, a.brand').forEach(a => {
    try {
      const u = new URL(a.href, location.origin);
      if (theme === 'light') { u.searchParams.set(_THEME_PARAM, 'light'); } else { u.searchParams.delete(_THEME_PARAM); }
      a.href = u.pathname + (u.search || '');
    } catch (_) {}
  });
}

function toggleTheme() {
  const next = _currentTheme() === 'light' ? 'dark' : 'light';
  applyTheme(next);
  if (next === 'light') { localStorage.setItem(_THEME_KEY, 'light'); } else { localStorage.removeItem(_THEME_KEY); }
  history.pushState({ theme: next }, '', _themeUrl(next));
  updateNavLinks(next);
}

function initTheme() {
  const p = new URLSearchParams(location.search);
  const theme = p.get(_THEME_PARAM) || localStorage.getItem(_THEME_KEY) || 'dark';
  applyTheme(theme);
  history.replaceState(history.state || {}, '', _themeUrl(theme));
  updateNavLinks(theme);
}

window.addEventListener('popstate', () => {
  const p = new URLSearchParams(location.search);
  const theme = p.get(_THEME_PARAM) || 'dark';
  applyTheme(theme);
  updateNavLinks(theme);
});

document.addEventListener('DOMContentLoaded', initTheme);
