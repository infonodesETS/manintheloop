'use strict';

import { AppState } from '../state.js';
import { esc } from '../helpers.js';

export default function initOverview() {
  renderOverview();
}

function renderOverview() {
  const { companies, investors, relationships, derived } = AppState;
  const { investorMeta, raw } = derived;

  const withWd = companies.filter(c => c.wikidata_id).length;
  const pct    = Math.round(withWd / companies.length * 100);
  const sectors = {};
  companies.forEach(c => { const s = c.sector || 'Unknown'; sectors[s] = (sectors[s] || 0) + 1; });

  const stats = [
    { val: companies.length,     lbl: 'Companies'    },
    { val: investors.length,     lbl: 'Investors'     },
    { val: relationships.length, lbl: 'Relationships' },
    { val: raw.filter(d => d[2]).length, lbl: 'Lead inv.' },
    { val: `${pct}%`,            lbl: 'Wikidata cov.' },
    ...Object.entries(sectors).sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ val: v, lbl: k })),
  ];

  document.getElementById('stats-grid').innerHTML = stats.map(s =>
    `<div class="stat-card"><div class="val">${s.val}</div><div class="lbl">${s.lbl}</div></div>`
  ).join('');

  document.getElementById('wd-cov-label').textContent = `${withWd} / ${companies.length} companies`;
  document.getElementById('wd-cov-pct').textContent   = `${pct}%`;
  document.getElementById('wd-cov-bar').style.width   = pct + '%';

  const secHtml = Object.entries(sectors).sort((a, b) => b[1] - a[1]).map(([s, n]) => {
    const sp = Math.round(n / companies.length * 100);
    return `<div class="d-flex align-items-center gap-2 mb-1">
      <span style="width:80px;font-size:.78rem;color:#888">${s}</span>
      <div class="prog-track flex-grow-1"><div class="prog-fill" style="width:${sp}%;background:var(--accent-dim)"></div></div>
      <span style="font-family:monospace;font-size:.75rem;color:#555;width:24px;text-align:right">${n}</span>
    </div>`;
  }).join('');
  document.getElementById('sector-breakdown').innerHTML = secHtml;

  const top5 = Object.values(investorMeta).sort((a, b) => b.total - a.total).slice(0, 8);
  document.getElementById('top-investors-list').innerHTML = top5.map(im => {
    const pct2 = Math.round(im.total / (top5[0]?.total || 1) * 100);
    return `<div class="d-flex align-items-center gap-2 mb-1">
      <span style="width:130px;font-size:.78rem;color:#888;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(im.entity.name)}</span>
      <div class="prog-track flex-grow-1"><div class="prog-fill" style="width:${pct2}%"></div></div>
      <span style="font-family:monospace;font-size:.75rem;color:var(--accent);width:20px;text-align:right">${im.total}</span>
    </div>`;
  }).join('');
}
