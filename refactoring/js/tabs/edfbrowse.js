'use strict';

import { setParams, getParams } from '../url.js';
import { loadEdfCalls } from '../edf-data.js';

// ── EDF Participants Browser — local data from data/edf_calls.json ────────────
// Rows = organisations aggregated across their EDF project participations.
// Inspired by edf_country_explorer.html UX: stats bar, country chips, sortable
// table with expandable drawers.

const PAGE_SIZE = 50;

let allOrgs    = [];   // full aggregated org list (built once from raw data)
let filtered   = [];   // after search + country + funded filters
let activeCountry = 'all';
let searchTerm    = '';
let fundedOnly    = true;   // default: on
let sortKey       = 'eu_total';
let sortAsc       = false;
let page          = 0;

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmtEuro(n) {
  if (!n) return '—';
  const v = Math.round(n);
  if (v >= 1e9) return `€${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `€${Math.round(v / 1e6)}M`;
  if (v >= 1e3) return `€${Math.round(v / 1e3)}K`;
  return `€${v.toLocaleString()}`;
}

function fmtDate(s) {
  if (!s) return '—';
  return s.slice(0, 10);
}

function safeId(s) {
  return s.replace(/[^a-z0-9]/gi, '_');
}

// ── Build org map from raw calls data ─────────────────────────────────────────
// Each org entry aggregates all their participations across funded projects.

function buildOrgs(callsMap, funded) {
  const orgMap = {};   // key: pic || `${name}||${country}`

  for (const call of Object.values(callsMap)) {
    const projects = call.projects || [];
    for (const proj of projects) {
      const projEuContrib = parseFloat(proj.eu_contribution) || 0;
      if (funded && projEuContrib === 0) continue;  // funded-only filter

      for (const pt of (proj.participants || [])) {
        const ptEuContrib = parseFloat(pt.eu_contribution) || 0;
        const key = pt.pic || `${pt.organization_name}||${pt.country || ''}`;
        if (!orgMap[key]) {
          orgMap[key] = {
            key,
            name:           pt.organization_name || '—',
            country:        pt.country || '—',
            pic:            pt.pic || null,
            eu_url:         pt.eu_url || null,
            sme:            pt.sme || false,
            activity_type:  pt.activity_type || '',
            type:           pt.type || '',
            participations: 0,
            coordinations:  0,
            eu_total:       0,
            projects_count: 0,
            projects:       [],   // { call_id, call_title, proj_acronym, proj_title, role, eu_contrib, status, proj_url }
          };
        }
        const org = orgMap[key];
        org.participations++;
        if (pt.role === 'coordinator') org.coordinations++;
        org.eu_total += ptEuContrib;
        org.projects_count++;
        org.projects.push({
          call_id:      call.identifier,
          call_title:   call.title || '',
          proj_acronym: proj.acronym || '',
          proj_title:   proj.title || '—',
          role:         pt.role || 'partner',
          eu_contrib:   ptEuContrib,
          status:       proj.status || '',
          proj_url:     proj.url || null,
          start_date:   proj.start_date || '',
          end_date:     proj.end_date   || '',
        });
      }
    }
  }

  return Object.values(orgMap);
}

// ── Stats bar ─────────────────────────────────────────────────────────────────

function renderStats(orgs) {
  const uniqueCountries = new Set(orgs.map(o => o.country)).size;
  const totalParts      = orgs.reduce((s, o) => s + o.participations, 0);
  const totalEU         = orgs.reduce((s, o) => s + o.eu_total, 0);
  const totalProjs      = new Set(
    orgs.flatMap(o => o.projects.map(p => `${p.call_id}|${p.proj_title}`))
  ).size;

  document.getElementById('eb-stats-bar').innerHTML = `
    <div class="eb-stat"><span class="eb-stat-val">${orgs.length.toLocaleString()}</span><span class="eb-stat-lbl">organisations</span></div>
    <div class="eb-stat-sep"></div>
    <div class="eb-stat"><span class="eb-stat-val">${uniqueCountries}</span><span class="eb-stat-lbl">countries</span></div>
    <div class="eb-stat"><span class="eb-stat-val">${totalParts.toLocaleString()}</span><span class="eb-stat-lbl">participations</span></div>
    <div class="eb-stat-sep"></div>
    <div class="eb-stat"><span class="eb-stat-val">${totalProjs.toLocaleString()}</span><span class="eb-stat-lbl">funded projects</span></div>
    <div class="eb-stat"><span class="eb-stat-val">${fmtEuro(totalEU)}</span><span class="eb-stat-lbl">total EU contribution</span></div>
  `;
}

// ── Country select ────────────────────────────────────────────────────────────

function renderCountrySelect(orgs) {
  const counts = {};
  for (const o of orgs) counts[o.country] = (counts[o.country] || 0) + o.participations;
  const countries = Object.keys(counts).sort((a, b) => a.localeCompare(b));

  const sel = document.getElementById('eb-country-select');
  sel.innerHTML = `<option value="all">All countries</option>` +
    countries.map(c => `<option value="${c}"${c === activeCountry ? ' selected' : ''}>${c} (${counts[c]})</option>`).join('');

  sel.addEventListener('change', () => {
    activeCountry = sel.value;
    applyFilters();
  });
}

// ── Filter + sort ─────────────────────────────────────────────────────────────

function applyFilters() {
  const q = searchTerm.toLowerCase();

  filtered = allOrgs.filter(o => {
    if (activeCountry !== 'all' && o.country !== activeCountry) return false;
    if (q && !o.name.toLowerCase().includes(q) && !o.country.toLowerCase().includes(q)) return false;
    return true;
  });

  filtered.sort((a, b) => {
    let va = a[sortKey], vb = b[sortKey];
    if (typeof va === 'string') va = va.toLowerCase();
    if (typeof vb === 'string') vb = vb.toLowerCase();
    if (va < vb) return sortAsc ? -1 : 1;
    if (va > vb) return sortAsc ? 1 : -1;
    return 0;
  });

  page = 0;

  // Sync URL (no-op until setUrlReady() is called)
  const params = { tab: 'edfbrowse' };
  if (searchTerm) params.search = searchTerm;
  if (activeCountry !== 'all') params.country = activeCountry;
  if (!fundedOnly) params.funded = '0';
  if (sortKey !== 'eu_total') params.sort = sortKey;
  if (sortAsc) params.asc = '1';
  setParams(params);

  renderTable();
}

// ── Table ─────────────────────────────────────────────────────────────────────

function renderTable() {
  const start = page * PAGE_SIZE;
  const rows  = filtered.slice(start, start + PAGE_SIZE);

  const tbody = document.getElementById('eb-tbody');
  tbody.innerHTML = rows.map(o => `
    <tr class="eb-row${o.coordinations > 0 ? ' eb-is-coord' : ''}" data-key="${o.key}">
      <td>
        <span class="eb-org-name" title="${o.name}">${o.name}</span>
        ${o.activity_type ? `<span class="eb-org-type" title="${o.activity_type}">${o.activity_type}</span>` : ''}
      </td>
      <td><span class="eb-country-tag">${o.country}</span></td>
      <td class="eb-num eb-bold">${o.participations}</td>
      <td class="eb-num">${o.coordinations > 0
        ? `<span class="eb-coord-badge">${o.coordinations}</span>`
        : '<span class="eb-dim">—</span>'}</td>
      <td class="eb-num eb-bold">${fmtEuro(o.eu_total)}</td>
      <td class="eb-num">${o.projects_count}</td>
      <td>${o.sme ? '<span class="eb-sme-badge">SME</span>' : '<span class="eb-dim">—</span>'}</td>
      <td class="eb-caret-cell">›</td>
    </tr>
  `).join('');

  // Sort arrow indicators
  document.querySelectorAll('#eb-table thead th[data-sort]').forEach(th => {
    const k = th.dataset.sort;
    th.classList.toggle('eb-sorted', k === sortKey);
    const arrow = th.querySelector('.eb-arrow');
    if (arrow) arrow.textContent = k === sortKey ? (sortAsc ? '↑' : '↓') : '↕';
  });

  // Row click → sidebar
  tbody.querySelectorAll('.eb-row').forEach(row => {
    row.addEventListener('click', () => openEdfSidebar(row.dataset.key));
  });

  renderPagination();
}

// ── Sidebar ───────────────────────────────────────────────────────────────────

export function openEdfSidebar(key) {
  const org = allOrgs.find(o => o.key === key);
  if (!org) return;
  const _edfSbEl = document.getElementById('edf-sidebar-title');
  _edfSbEl.textContent = org.name; _edfSbEl.title = org.name;
  document.getElementById('edf-sidebar-body').innerHTML = buildDrawer(org);
  document.getElementById('edf-sidebar').classList.add('open');
  // Sync URL
  const base = { tab: 'edfbrowse' };
  if (searchTerm) base.search = searchTerm;
  if (activeCountry !== 'all') base.country = activeCountry;
  const slug = org.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  setParams({ ...base, entity: encodeURIComponent(key), 'entity-name': slug });
}

function closeEdfSidebar() {
  document.getElementById('edf-sidebar').classList.remove('open');
  // Remove entity from URL, keep other filters
  const p = getParams();
  delete p.entity; delete p['entity-name'];
  setParams(p);
}

function buildDrawer(org) {
  const picLink = org.eu_url
    ? `<a href="${org.eu_url}" target="_blank" class="eb-ext-link" onclick="event.stopPropagation()">↗ EC Portal</a>`
    : '';

  const projsHtml = org.projects
    .sort((a, b) => b.eu_contrib - a.eu_contrib)
    .map(p => {
      const rawCall = rawCallsMap?.[p.call_id] || {};
      const rawProj = (rawCall.projects || []).find(r => r.acronym === p.proj_acronym) || {};
      const objective   = rawProj.objective || '';
      const totalBudget = rawProj.total_budget || rawProj.overall_budget || 0;
      const partCount   = (rawProj.participants || []).length;
      const inlineRows = [
        rawCall.title ? `<div class="eb-det-row"><span class="eb-det-lbl">Call</span><span class="eb-det-val">${rawCall.title}</span></div>` : '',
        totalBudget   ? `<div class="eb-det-row"><span class="eb-det-lbl">Total budget</span><span class="eb-det-val">${fmtEuro(totalBudget)}</span></div>` : '',
        partCount     ? `<div class="eb-det-row"><span class="eb-det-lbl">Participants</span><span class="eb-det-val">${partCount}</span></div>` : '',
      ].filter(Boolean).join('');
      const detailRows = [
        inlineRows ? `<div class="eb-det-rows-inline">${inlineRows}</div>` : '',
        objective  ? `<div class="eb-det-objective">${objective}</div>` : '',
      ].filter(Boolean).join('');
      return `
      <div class="eb-proj-item eb-proj-item--clickable">
        <div class="eb-proj-header">
          <span class="eb-proj-caret">›</span>
          ${p.proj_acronym ? `<span class="eb-proj-acronym">${p.proj_acronym}</span>` : ''}
          <span class="eb-proj-title">${p.proj_title}</span>
          <span class="eb-role-badge ${p.role === 'coordinator' ? 'coord' : 'partner'}">${p.role}</span>
          <span class="eb-proj-status ${p.status === 'Ongoing' ? 'ongoing' : 'closed'}">${p.status}</span>
          ${p.proj_url ? `<a href="${p.proj_url}" target="_blank" class="eb-ext-link" onclick="event.stopPropagation()">↗ EC Portal</a>` : ''}
        </div>
        <div class="eb-proj-meta">
          <span class="eb-meta-call">${p.call_id}</span>
          ${p.eu_contrib ? `<span>EU: <strong>${fmtEuro(p.eu_contrib)}</strong></span>` : ''}
          ${p.start_date ? `<span>${fmtDate(p.start_date)} → ${fmtDate(p.end_date)}</span>` : ''}
        </div>
        ${detailRows ? `<div class="eb-proj-detail">${detailRows}</div>` : ''}
      </div>`;
    }).join('');

  return `
    <div class="eb-drawer-inner">
      <div class="eb-drawer-orgmeta">
        <div class="eb-orgmeta-row">
          ${org.pic ? `<span class="eb-dr-field"><span class="eb-dr-lbl">PIC</span><span class="eb-mono">${org.pic}</span></span>` : ''}
          ${org.activity_type ? `<span class="eb-dr-field"><span class="eb-dr-lbl">Type</span><span>${org.activity_type}</span></span>` : ''}
          ${org.sme ? `<span class="eb-sme-badge">SME</span>` : ''}
          ${picLink}
        </div>
      </div>
      <div class="eb-projects-section">
        <div class="eb-dr-lbl">Projects <span class="eb-proj-count">${org.projects.length}</span></div>
        <div class="eb-proj-list">${projsHtml}</div>
      </div>
    </div>`;
}

// ── Pagination ────────────────────────────────────────────────────────────────

function renderPagination() {
  const total      = filtered.length;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  const countEl = document.getElementById('eb-count');
  if (countEl) countEl.textContent = `${total.toLocaleString()} organisation${total !== 1 ? 's' : ''}`;

  const pgEl = document.getElementById('eb-pagination');
  if (!pgEl) return;
  if (totalPages <= 1) { pgEl.innerHTML = ''; return; }

  pgEl.innerHTML = `
    <button class="eb-pg-btn" id="eb-pg-prev" ${page === 0 ? 'disabled' : ''}>← Prev</button>
    <span class="eb-pg-info">${page + 1} / ${totalPages}</span>
    <button class="eb-pg-btn" id="eb-pg-next" ${page >= totalPages - 1 ? 'disabled' : ''}>Next →</button>
  `;

  document.getElementById('eb-pg-prev')?.addEventListener('click', () => {
    page--; renderTable();
  });
  document.getElementById('eb-pg-next')?.addEventListener('click', () => {
    page++; renderTable();
  });
}

// ── Rebuild from raw (re-runs when funded toggle changes) ─────────────────────

let rawCallsMap = null;

function rebuild() {
  allOrgs = buildOrgs(rawCallsMap, fundedOnly);
  activeCountry = 'all';
  const sel = document.getElementById('eb-country-select');
  if (sel) sel.value = 'all';
  searchTerm = document.getElementById('eb-search')?.value.trim() || '';
  renderStats(allOrgs);
  renderCountrySelect(allOrgs);
  applyFilters();
}

// ── Snapshot for Export-for-AI ────────────────────────────────────────────────

export function buildSnapshot() {
  const filters = [];
  if (activeCountry !== 'all') filters.push(`country: ${activeCountry}`);
  if (searchTerm) filters.push(`search: "${searchTerm}"`);
  if (fundedOnly) filters.push('funded projects only');
  const lines = filtered.slice(0, 100).map(o =>
    `- **${o.name}** | ${o.country || '—'} | ${fmtEuro(o.eu_total)} EU funding | ${o.project_count} project${o.project_count !== 1 ? 's' : ''}`
  ).join('\n');
  const trunc = filtered.length > 100 ? `\n_(showing 100 of ${filtered.length})_` : '';
  return `## EDF Beneficiaries (${filtered.length} organisations)\n\n` +
    (filters.length ? `**Filters:** ${filters.join(' · ')}\n\n` : '') +
    lines + trunc;
}

// ── Init ──────────────────────────────────────────────────────────────────────

/** Restore edfbrowse state from URL params (called after init completes). */
export function restoreEdfbrowseUrl(p) {
  let changed = false;
  if (p.search) {
    searchTerm = p.search;
    const inp = document.getElementById('eb-search');
    if (inp) inp.value = p.search;
    changed = true;
  }
  if (p.country && p.country !== 'all') {
    activeCountry = p.country;
    const sel = document.getElementById('eb-country-select');
    if (sel) sel.value = p.country;
    changed = true;
  }
  if (p.funded === '0') {
    fundedOnly = false;
    const check = document.getElementById('eb-funded-check');
    if (check) check.checked = false;
    // rebuild re-processes the org list with new fundedOnly value
    rebuild();
    return;
  }
  if (p.sort) {
    sortKey = p.sort;
    sortAsc = p.asc === '1';
    changed = true;
  }
  if (changed) applyFilters();
  if (p.entity) {
    const key = decodeURIComponent(p.entity);
    openEdfSidebar(key);
  }
}


export function openEdfBrowseIntro() {
  const total   = allOrgs.length;
  const countries = new Set(allOrgs.map(o => o.country)).size;
  const withFunding = allOrgs.filter(o => o.eu_total > 0).length;
  const calls = new Set(allOrgs.flatMap(o => o.projects.map(p => p.call_id))).size;
  if (!total) return; // data not loaded yet
  document.getElementById('edf-sidebar-title').textContent = 'EDF Beneficiaries';
  document.getElementById('edf-sidebar-body').innerHTML = `
    <p class="map-intro-text">
      Organisations that participated in European Defence Fund projects, browsable by name,
      country, and funding amount.
    </p>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">Dataset</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Organisations</span> ${total}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Countries</span> ${countries}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">With EU funding</span> ${withFunding}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">EDF calls covered</span> ${calls}</div>
    </div>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">How to navigate</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Click a row</span> Open organisation detail with project list and funding breakdown</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Search</span> Filter by organisation name</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Country filter</span> Narrow to a specific country</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Funded only</span> Toggle to show only orgs with EU contribution > 0</div>
    </div>
  `;
  document.getElementById('edf-sidebar').classList.add('open');
}
export default async function initEdfbrowse() {
  try {
    const json = await loadEdfCalls();
    rawCallsMap = json.calls || {};

    // Set checkbox to default state
    const check = document.getElementById('eb-funded-check');
    if (check) {
      check.checked = fundedOnly;
      check.addEventListener('change', () => {
        fundedOnly = check.checked;
        rebuild();
      });
    }

    // Wire search
    const searchEl = document.getElementById('eb-search');
    searchEl?.addEventListener('input', () => {
      searchTerm = searchEl.value.trim();
      applyFilters();
    });

    // Wire sidebar close
    document.getElementById('edf-sidebar-overlay')?.addEventListener('click', closeEdfSidebar);
    document.getElementById('edf-sidebar-close')?.addEventListener('click', closeEdfSidebar);

    // Wire project item expand (delegation on permanent sidebar element)
    document.getElementById('edf-sidebar')?.addEventListener('click', e => {
      const item = e.target.closest('.eb-proj-item--clickable');
      if (!item) return;
      if (e.target.closest('a')) return; // let ↗ links through
      const detail = item.querySelector('.eb-proj-detail');
      if (!detail) return;
      const isOpen = detail.classList.toggle('open');
      item.querySelector('.eb-proj-caret')?.classList.toggle('open', isOpen);
    });

    // Wire sort headers
    document.querySelectorAll('#eb-table thead th[data-sort]').forEach(th => {
      th.addEventListener('click', () => {
        if (sortKey === th.dataset.sort) {
          sortAsc = !sortAsc;
        } else {
          sortKey = th.dataset.sort;
          sortAsc = ['name', 'country'].includes(sortKey);
        }
        applyFilters();
      });
    });

    rebuild();
    openEdfBrowseIntro();

    // If opened directly via URL, restore filter state now (after async init resolves)
    const p = getParams();
    if (p.tab === 'edfbrowse' && (p.search || p.country || p.funded || p.sort)) {
      restoreEdfbrowseUrl(p);
    }

  } catch (err) {
    const tbody = document.getElementById('eb-tbody');
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="7" style="color:var(--error);padding:20px;font-size:var(--fs-base)">
        Error loading EDF data: ${err.message}</td></tr>`;
    }
  }
}
