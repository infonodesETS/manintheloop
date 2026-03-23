'use strict';

import { AppState } from '../state.js';
import { esc, fmtFunding, sectorBadge, dualBadge, wdBadge, valBadge } from '../helpers.js';
import { setParams } from '../url.js';
import { openCompanySidebar, openIntroSidebar } from '../detail-sidebar.js';

export default function initCompanies() {
  document.getElementById('co-search').addEventListener('input', renderCoTable);
  document.getElementById('co-tbody').addEventListener('click', e => {
    const tr = e.target.closest('tr[data-id]');
    if (!tr) return;
    const company = AppState.derived.entityMap[tr.dataset.id];
    if (company) openCompanySidebar(company);
  });
  renderCoTable();
}

export function openCompaniesIntro() {
  const { companies } = AppState;
  const total = companies.length;
  const bySector = {};
  for (const c of companies) bySector[c.sector] = (bySector[c.sector] || 0) + 1;
  const withInvestors = companies.filter(c => c._investors?.length).length;

  const sectorRows = Object.entries(bySector)
    .filter(([s]) => s && s !== 'null' && s !== 'undefined')
    .sort((a, b) => b[1] - a[1])
    .map(([s, n]) => `<div class="map-sector-row"><span class="map-sector-lbl">${s}</span> ${n}</div>`)
    .join('');

  openIntroSidebar('Companies', `
    <p class="map-intro-text">
      Manufacturers, tech firms, startups, and mining companies with documented defence exposure,
      tracked in the info.nodes research database.
    </p>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">Dataset</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Total companies</span> ${total}</div>
      ${sectorRows}
      <div class="map-sector-row"><span class="map-sector-lbl">With investors</span> ${withInvestors}</div>
    </div>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">How to navigate</div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Click a row</span>
        Open company detail: sector, founding, funding, investors, Crunchbase and Wikidata data
      </div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Filter by sector</span>
        Use the toolbar buttons — Defence / Mining / Tech / Startup
      </div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Sort columns</span>
        Click any column header to sort by name, country, founded, funding, or investor count
      </div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Search</span>
        Type in the search bar to filter by company name
      </div>
    </div>
  `);
}

export function setCoSector(s) {
  AppState.ui.companies.sector = s;
  renderCoTable();
}

export function sortCo(key) {
  const sort = AppState.ui.companies.sort;
  AppState.ui.companies.sort = { key, asc: sort.key === key ? !sort.asc : key === 'name' };
  renderCoTable();
}

export function renderCoTable() {
  const { companies } = AppState;
  const { sector, sort } = AppState.ui.companies;
  const q = (document.getElementById('co-search')?.value || '').toLowerCase();

  let list = sector === 'all' ? companies : companies.filter(c => c.sector === sector);
  if (q) list = list.filter(c => c.name.toLowerCase().includes(q));

  list = [...list].sort((a, b) => {
    const { key, asc } = sort;
    let av, bv;
    if (key === 'name')      { av = a.name; bv = b.name; }
    if (key === 'country')   { av = a.sources?.wikidata?.country || 'zzz'; bv = b.sources?.wikidata?.country || 'zzz'; }
    if (key === 'inception') { av = a.sources?.wikidata?.inception || 'zzz'; bv = b.sources?.wikidata?.inception || 'zzz'; }
    if (key === 'funding')   { av = a.sources?.crunchbase?.total_funding_usd || 0; bv = b.sources?.crunchbase?.total_funding_usd || 0; }
    if (key === 'investors') { av = a._investors?.length || 0; bv = b._investors?.length || 0; }
    if (av < bv) return asc ? -1 : 1;
    if (av > bv) return asc ? 1 : -1;
    return 0;
  });

  document.getElementById('co-count').textContent = `${list.length} / ${companies.length}`;
  document.getElementById('co-tbody').innerHTML = list.map(c => {
    const wd = c.sources?.wikidata, cb = c.sources?.crunchbase;
    const country    = wd?.country || '—';
    const inception  = wd?.inception ? String(wd.inception).slice(0, 4) : '—';
    const industries = (Array.isArray(cb?.industries) ? cb.industries : []).slice(0, 2).join(', ') || '—';
    return `<tr data-id="${esc(c.id)}">
      <td><strong>${esc(c.name)}</strong><br><span style="font-size:var(--fs-xs);color:var(--text-faint)">${esc(c.id)}</span></td>
      <td>${sectorBadge(c.sector)} ${c.roles?.includes('investor') ? dualBadge() : ''}</td>
      <td style="font-size:var(--fs-sm)">${esc(country)}</td>
      <td style="font-size:var(--fs-sm);font-family:monospace">${inception}</td>
      <td style="font-size:var(--fs-sm);font-family:monospace">${fmtFunding(cb?.total_funding_usd)}</td>
      <td style="font-size:var(--fs-sm);color:var(--text-muted)">${esc(industries)}</td>
      <td style="text-align:center;font-family:monospace;color:${c._investors?.length ? 'var(--text-tertiary)' : 'var(--grey-dark)'}">${c._investors?.length || 0}</td>
      <td>${wdBadge(c)}</td>
      <td>${valBadge(c)}</td>
    </tr>`;
  }).join('');

  // Sync URL (no-op until setUrlReady() is called)
  const params = { tab: 'companies' };
  if (q) params.search = q;
  if (sector !== 'all') params.sector = sector;
  if (sort.key !== 'name' || !sort.asc) { params.sort = sort.key; params.asc = sort.asc ? '1' : '0'; }
  setParams(params);
}

/** Restore companies state from URL params (called on page load / popstate). */
export function restoreCoUrl(p) {
  if (p.search) {
    const inp = document.getElementById('co-search');
    if (inp) inp.value = p.search;
  }
  if (p.sector && p.sector !== 'all') {
    AppState.ui.companies.sector = p.sector;
    document.querySelectorAll('#tab-companies .sf-btn').forEach(b =>
      b.classList.toggle('active', b.dataset.sector === p.sector));
  }
  if (p.sort) {
    AppState.ui.companies.sort = { key: p.sort, asc: p.asc === '1' };
  }
  renderCoTable();
}
