'use strict';

import { AppState } from '../state.js';
import { esc, typeBadge } from '../helpers.js';
import { setParams } from '../url.js';
import { openInvestorSidebar, openIntroSidebar } from '../detail-sidebar.js';

export default function initInvestors() {
  document.getElementById('inv-search').addEventListener('input', renderInvTable);
  document.getElementById('inv-tbody').addEventListener('click', e => {
    const tr = e.target.closest('tr[data-id]');
    if (!tr) return;
    const im = AppState.derived.investorMeta[tr.dataset.id];
    if (im) openInvestorSidebar(im);
  });
  renderInvTable();
}

export function openInvestorsIntro() {
  const { investors, derived } = AppState;
  const total = investors.length;
  const byType = {};
  for (const inv of investors) byType[inv.type] = (byType[inv.type] || 0) + 1;

  const meta = Object.values(derived.investorMeta);
  const totalPortfolio = meta.reduce((s, im) => s + im.total, 0);
  const leadCount = meta.reduce((s, im) => s + im.leads, 0);

  const typeRows = Object.entries(byType)
    .filter(([t]) => t && t !== 'null' && t !== 'undefined')
    .sort((a, b) => b[1] - a[1])
    .map(([t, n]) => `<div class="map-sector-row"><span class="map-sector-lbl">${t}</span> ${n}</div>`)
    .join('');

  openIntroSidebar('Investors', `
    <p class="map-intro-text">
      Funds, banks, and government agencies with documented investment relationships
      to defence-exposed companies in the info.nodes database.
    </p>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">Dataset</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Total investors</span> ${total}</div>
      ${typeRows}
      <div class="map-sector-row"><span class="map-sector-lbl">Total relationships</span> ${totalPortfolio}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Lead investments</span> ${leadCount}</div>
    </div>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">How to navigate</div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Click a row</span>
        Open investor detail: type, portfolio companies, lead investments, Crunchbase and Wikidata data
      </div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Sort columns</span>
        Click Portfolio or Lead to rank investors by investment activity
      </div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Search</span>
        Type in the search bar to filter by investor name
      </div>
    </div>
  `);
}

export function sortInv(key) {
  const sort = AppState.ui.investors.sort;
  AppState.ui.investors.sort = { key, asc: sort.key === key ? !sort.asc : false };
  renderInvTable();
}

export function renderInvTable() {
  const { investors, derived } = AppState;
  const { investorMeta } = derived;
  const { sort } = AppState.ui.investors;
  const q = (document.getElementById('inv-search')?.value || '').toLowerCase();

  let list = Object.values(investorMeta);
  if (q) list = list.filter(im => im.entity.name.toLowerCase().includes(q));

  list = [...list].sort((a, b) => {
    const { key, asc } = sort;
    let av = key === 'leads' ? a.leads : a.total;
    let bv = key === 'leads' ? b.leads : b.total;
    if (av < bv) return asc ? -1 : 1;
    if (av > bv) return asc ? 1 : -1;
    return 0;
  });

  document.getElementById('inv-count').textContent = `${list.length} / ${investors.length}`;
  document.getElementById('inv-tbody').innerHTML = list.map(im => {
    const names = im.portfolio.slice(0, 4).map(p => p.company?.name || '?').join(', ');
    const more  = im.portfolio.length > 4 ? ` +${im.portfolio.length - 4}` : '';
    return `<tr data-id="${esc(im.entity.id)}">
      <td><strong>${esc(im.entity.name)}</strong><br><span style="font-size:var(--fs-xs);color:var(--text-faint)">${esc(im.entity.id)}</span></td>
      <td>${typeBadge(im.entity.type)}</td>
      <td style="text-align:center;font-family:monospace;color:var(--text-tertiary)">${im.total}</td>
      <td style="text-align:center;font-family:monospace;color:var(--accent)">${im.leads}</td>
      <td style="font-size:var(--fs-sm);color:var(--text-muted)">${esc(names)}${more ? `<span style="color:var(--text-faint)">${more}</span>` : ''}</td>
    </tr>`;
  }).join('');

  // Sync URL
  const params = { tab: 'investors' };
  if (q) params.search = q;
  if (sort.key !== 'total' || sort.asc) { params.sort = sort.key; params.asc = sort.asc ? '1' : '0'; }
  setParams(params);
}

/** Restore investors state from URL params. */
export function restoreInvUrl(p) {
  if (p.search) {
    const inp = document.getElementById('inv-search');
    if (inp) inp.value = p.search;
  }
  if (p.sort) {
    AppState.ui.investors.sort = { key: p.sort, asc: p.asc === '1' };
  }
  renderInvTable();
}
