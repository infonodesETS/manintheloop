'use strict';

import { AppState } from '../state.js';
import { esc, sectorBadge } from '../helpers.js';
import { setParams } from '../url.js';
import { openInvestorSidebar, openCompanySidebar } from '../detail-sidebar.js';

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

/** Restore relationships state from URL params. */
export function restoreRelUrl(p) {
  if (p.search) {
    const inp = document.getElementById('rel-search');
    if (inp) inp.value = p.search;
  }
  renderRelTable();
}
