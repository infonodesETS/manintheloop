'use strict';

import { AppState } from '../state.js';
import { esc } from '../helpers.js';
import { GLOSSARY } from '../glossary.js';

export default function initOverview() {
  renderOverview();
}

function renderOverview() {
  const { companies, investors, relationships, derived } = AppState;
  const { investorMeta, raw } = derived;

  const sectors = {};
  companies.forEach(c => { const s = c.sector || 'Unknown'; sectors[s] = (sectors[s] || 0) + 1; });

  const entityStats = [
    { val: companies.length,     lbl: 'Companies',     gl: 'company'      },
    { val: investors.length,     lbl: 'Investors',     gl: 'investor'     },
    { val: relationships.length, lbl: 'Relationships', gl: 'relationship' },
  ];
  const sectorStats = Object.entries(sectors).sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ val: v, lbl: k, gl: k.toLowerCase() }));

  const makeCards = (arr) => arr.map(s => {
    const title = s.gl && GLOSSARY[s.gl] ? ` title="${esc(GLOSSARY[s.gl])}"` : '';
    return `<div class="stat-card"${title}><div class="val">${s.val}</div><div class="lbl">${s.lbl}</div></div>`;
  }).join('');

  document.getElementById('stats-grid').innerHTML =
    `<div class="ov-stats-group">
       <div class="ov-stats-group-lbl">Unique entities</div>
       <div class="overview-grid ov-stats-inner">${makeCards(entityStats)}</div>
     </div>
     <div class="ov-stats-group">
       <div class="ov-stats-group-lbl">Companies by sector</div>
       <div class="overview-grid ov-stats-inner">${makeCards(sectorStats)}</div>
     </div>`;

  const secHtml = Object.entries(sectors).sort((a, b) => b[1] - a[1]).map(([s, n]) => {
    const sp = Math.round(n / companies.length * 100);
    return `<div class="d-flex align-items-center gap-2 mb-1">
      <span style="width:80px;font-size:var(--fs-sm);color:#888">${s}</span>
      <div class="prog-track flex-grow-1"><div class="prog-fill" style="width:${sp}%;background:var(--accent-dim)"></div></div>
      <span style="font-family:monospace;font-size:var(--fs-sm);color:#555;width:24px;text-align:right">${n}</span>
    </div>`;
  }).join('');
  document.getElementById('sector-breakdown').innerHTML = secHtml;

  const top5 = Object.values(investorMeta).sort((a, b) => b.total - a.total).slice(0, 8);
  document.getElementById('top-investors-list').innerHTML = top5.map(im => {
    const pct2 = Math.round(im.total / (top5[0]?.total || 1) * 100);
    return `<div class="d-flex align-items-center gap-2 mb-1">
      <span style="width:130px;font-size:var(--fs-sm);color:#888;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(im.entity.name)}</span>
      <div class="prog-track flex-grow-1"><div class="prog-fill" style="width:${pct2}%"></div></div>
      <span style="font-family:monospace;font-size:var(--fs-sm);color:var(--accent);width:20px;text-align:right">${im.total}</span>
    </div>`;
  }).join('');
}
