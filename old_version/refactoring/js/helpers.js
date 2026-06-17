'use strict';

export function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export function fmtFunding(n) {
  if (!n) return '—';
  if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(0)}M`;
  return `$${n.toLocaleString()}`;
}

export function sectorBadge(s) {
  return s ? `<span class="badge-sector badge-${s}">${s}</span>` : '';
}

const TYPE_LABELS = {
  fund:               'Fund',
  government_agency:  'Gov Agency',
  bank:               'Bank',
  institution:        'Institution',
  company:            'Manufacturer',
};

export function typeBadge(type) {
  const label = TYPE_LABELS[type] || (type ? esc(type) : 'Unknown');
  return `<span class="badge-type badge-type--${type || 'company'}">${label}</span>`;
}

export function typeDot(type) {
  return `<span class="type-dot type-dot--${type || 'company'}" title="${TYPE_LABELS[type] || type}"></span>`;
}

export function dualBadge() {
  return `<span class="badge-dual" title="Also acts as investor">⟲ investor</span>`;
}

export function wdBadge(c) {
  return c.wikidata_id
    ? `<span class="badge-wd">${c.wikidata_id}</span>`
    : `<span class="badge-miss">missing</span>`;
}

export function valBadge(c) {
  const open = (c.validation || []).filter(v => v.status !== 'confirmed');
  if (!open.length) return '<span style="color:var(--text-tertiary);font-size:var(--fs-xs)">✓</span>';
  return open.slice(0, 2).map(v =>
    `<span class="${v.status === 'flagged' ? 'badge-val-flag' : 'badge-val-review'}">${v.status === 'flagged' ? '⛔' : '⚠'}</span>`
  ).join(' ');
}

export function tip(e, name, info, sub = '') {
  document.getElementById('tip-name').textContent = name;
  document.getElementById('tip-info').textContent = info;
  document.getElementById('tip-sub').textContent  = sub;
  const t = document.getElementById('tip');
  t.style.display = 'block';
  t.style.left    = (e.clientX + 14) + 'px';
  t.style.top     = (e.clientY - 6)  + 'px';
}

export function hideTip() {
  document.getElementById('tip').style.display = 'none';
}

export function initSectorFilter(containerSelector, onSelect) {
  document.querySelectorAll(`${containerSelector} .sf-btn`).forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll(`${containerSelector} .sf-btn`).forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      onSelect(btn.dataset.sector);
    });
  });
}
