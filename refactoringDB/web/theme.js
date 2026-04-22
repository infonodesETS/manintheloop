function toggleTheme() {
  const html = document.documentElement;
  const isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) {
    html.removeAttribute('data-theme');
    localStorage.removeItem('mitl-theme');
  } else {
    html.setAttribute('data-theme', 'light');
    localStorage.setItem('mitl-theme', 'light');
  }
  syncThemeBtn();
}

function syncThemeBtn() {
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = document.documentElement.getAttribute('data-theme') === 'light' ? '◑ DARK' : '◑ LIGHT';
}

document.addEventListener('DOMContentLoaded', syncThemeBtn);
