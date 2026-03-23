'use strict';

import { AppState } from '../state.js';
import { esc, sectorBadge } from '../helpers.js';
import { setParams } from '../url.js';
import { openInvestorSidebar, openCompanySidebar, openIntroSidebar } from '../detail-sidebar.js';

export default function initRelationships() {
  document.getElementById('rel-search').addEventListener('input', renderRelTable);
  document.getElementById('rel-tbody').addEventListener('click', e => {
    const cell = e.target.closest('[data-open]');
    if (!cell) return;
    const { open: type, id } = cell.dataset;
    const { entityMap, investorMeta } = AppState.derived;
    if (type === 'investor') {
      const im = investorMeta[id];
      if (im) openInvestorSidebar(im);
    } else if (type === 'company') {
      const company = entityMap[id];
      if (company) openCompanySidebar(company);
    }
  });
  renderRelTable();
}

export function renderRelTable() {
  const { relationships, derived } = AppState;
  const { entityMap } = derived;
  const q = (document.getElementById('rel-search')?.value || '').toLowerCase();

  let list = relationships;
  if (q) list = list.filter(rel => {
    return (entityMap[rel.source]?.name || '').toLowerCase().includes(q) ||
           (entityMap[rel.target]?.name || '').toLowerCase().includes(q);
  });

  document.getElementById('rel-count').textContent = `${list.length} / ${relationships.length}`;
  document.getElementById('rel-tbody').innerHTML = list.map(rel => {
    const inv  = entityMap[rel.source], comp = entityMap[rel.target];
    const isLead = rel.details?.lead;
    return `<tr>
      <td style="font-size:var(--fs-xs);color:var(--text-faint);font-family:monospace">${esc(rel.id)}</td>
      <td class="es-click-cell" data-open="investor" data-id="${esc(rel.source)}" style="font-size:var(--fs-base)"><strong>${esc(inv?.name || rel.source)}</strong></td>
      <td class="es-click-cell" data-open="company" data-id="${esc(rel.target)}" style="font-size:var(--fs-base)"><strong>${esc(comp?.name || rel.target)}</strong></td>
      <td>${sectorBadge(comp?.sector)}</td>
      <td>${isLead ? '<span class="badge-lead">LEAD</span>' : '<span class="badge-follow">follow</span>'}</td>
    </tr>`;
  }).join('');

  // Sync URL
  const params = { tab: 'relationships' };
  if (q) params.search = q;
  setParams(params);
}

export function openRelationshipsIntro() {
  const { relationships, derived } = AppState;
  const total   = relationships.length;
  const leads   = relationships.filter(r => r.details?.lead).length;
  const follows = total - leads;
  const uniqueInv  = new Set(relationships.map(r => r.source)).size;
  const uniqueCo   = new Set(relationships.map(r => r.target)).size;

  openIntroSidebar('Relationships', `
    <p class="map-intro-text">
      Documented investment links between investors and defence-exposed companies
      in the info.nodes database.
    </p>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">Dataset</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Total relationships</span> ${total}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Lead investments</span> ${leads}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Follow investments</span> ${follows}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Unique investors</span> ${uniqueInv}</div>
      <div class="map-sector-row"><span class="map-sector-lbl">Unique companies</span> ${uniqueCo}</div>
    </div>
    <div class="sl-panel-section">
      <div class="sl-section-lbl" style="margin-bottom:6px">How to navigate</div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Click an investor</span>
        Open investor detail sidebar with full portfolio
      </div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Click a company</span>
        Open company detail sidebar with investors and data sources
      </div>
      <div class="map-sector-row">
        <span class="map-sector-lbl">Search</span>
        Filter by investor or company name
      </div>
    </div>
  `);
}

/** Restore relationships state from URL params. */
export function restoreRelUrl(p) {
  if (p.search) {
    const inp = document.getElementById('rel-search');
    if (inp) inp.value = p.search;
  }
  renderRelTable();
}
