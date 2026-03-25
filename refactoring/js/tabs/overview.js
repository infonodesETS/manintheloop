'use strict';

import { AppState } from '../state.js';
import { esc } from '../helpers.js';
import { GLOSSARY } from '../glossary.js';
import { openInvestorSidebar } from '../detail-sidebar.js';

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

  // Geographic distribution chart
  const COUNTRY_NORM = {
    'USA': 'United States', 'Cina': 'China', "People's Republic of China": 'China',
    'Giappone': 'Japan', 'EAU (Dubai)': 'United Arab Emirates',
    'Polonia': 'Poland', 'Francia': 'France', 'Norvegia': 'Norway',
    'Belgio': 'Belgium', 'Germania': 'Germany', 'Cile': 'Chile', 'UK': 'United Kingdom',
  };
  const WESTERN = new Set([
    'United States','USA','United Kingdom','UK','Germany','Germania','France','Francia',
    'Italy','Spain','Netherlands','Belgium','Belgio','Norway','Norvegia','Sweden',
    'Finland','Denmark','Poland','Polonia','Czech Republic','Czech Rep.','Czechia',
    'Romania','Estonia','Latvia','Lithuania','Switzerland','Austria','Portugal','Greece',
    'Hungary','Slovakia','Luxembourg','Ireland','Cyprus','Malta','Croatia','Slovenia',
    'Serbia','Bulgaria','North Macedonia','Albania','Canada','Australia','New Zealand',
    'Japan','Giappone','South Korea','Israel','Turkey',
  ]);
  const CHINA_RU = new Set(['China','Cina',"People's Republic of China",'Russia']);

  const countryCounts = {};
  for (const c of companies) {
    const raw = c.sources?.wikidata?.country || c.sources?.infonodes?.country || 'Unknown';
    const ctry = COUNTRY_NORM[raw] || raw;
    countryCounts[ctry] = (countryCounts[ctry] || 0) + 1;
  }
  const geoEntries = Object.entries(countryCounts).sort((a, b) => b[1] - a[1]);
  const geoMax = geoEntries[0]?.[1] || 1;

  const alignColor = (ctry) => {
    if (CHINA_RU.has(ctry)) return '#c0392b';
    if (WESTERN.has(ctry)) return 'var(--accent)';
    return 'var(--grey-mid)';
  };

  const legend = `<div class="ov-geo-legend">
    <span class="ov-geo-dot" style="background:var(--accent)"></span>Western aligned
    <span class="ov-geo-dot" style="background:#c0392b"></span>China / Russia
    <span class="ov-geo-dot" style="background:var(--grey-mid)"></span>Other
  </div>`;

  const geoHtml = geoEntries.map(([ctry, n]) => {
    const pct = Math.round(n / geoMax * 100);
    return `<div class="d-flex align-items-center gap-2 mb-1">
      <span class="ov-geo-lbl">${esc(ctry)}</span>
      <div class="prog-track flex-grow-1"><div class="prog-fill" style="width:${pct}%;background:${alignColor(ctry)}"></div></div>
      <span class="ov-geo-val">${n}</span>
    </div>`;
  }).join('');
  document.getElementById('geo-breakdown').innerHTML = legend + geoHtml;

  const top5 = Object.values(investorMeta).sort((a, b) => b.total - a.total).slice(0, 8);
  const listEl = document.getElementById('top-investors-list');
  listEl.innerHTML = top5.map((im, i) => {
    const pct2 = Math.round(im.total / (top5[0]?.total || 1) * 100);
    return `<div class="d-flex align-items-center gap-2 mb-1 ov-inv-row" data-inv-idx="${i}" style="cursor:pointer" title="Click to view ${esc(im.entity.name)} details">
      <span style="width:130px;font-size:var(--fs-sm);color:#888;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(im.entity.name)}">${esc(im.entity.name)}</span>
      <div class="prog-track flex-grow-1"><div class="prog-fill" style="width:${pct2}%"></div></div>
      <span style="font-family:monospace;font-size:var(--fs-sm);color:var(--accent);width:20px;text-align:right">${im.total}</span>
    </div>`;
  }).join('');
  listEl.querySelectorAll('.ov-inv-row').forEach(row => {
    const im = top5[+row.dataset.invIdx];
    row.addEventListener('click', () => openInvestorSidebar(im));
  });
}
