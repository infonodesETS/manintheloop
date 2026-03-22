'use strict';

import { AppState } from '../state.js';
import { esc, sectorBadge } from '../helpers.js';

export default function initQuality() {
  renderQuality();
}

function renderQuality() {
  const { companies } = AppState;

  const withWd  = companies.filter(c => c.wikidata_id).length;
  const pct     = Math.round(withWd / companies.length * 100);
  const withEnr = companies.filter(c => c.sources?.wikidata?.label).length;

  document.getElementById('q-wd-stats').innerHTML =
    `<div style="font-size:.85rem"><span style="color:var(--accent);font-family:monospace">${withWd}</span> <span style="color:#555">with QID</span></div>
     <div style="font-size:.85rem"><span style="color:#ff4444;font-family:monospace">${companies.length - withWd}</span> <span style="color:#555">missing</span></div>`;
  document.getElementById('q-wd-bar').style.width = pct + '%';

  const valCounts = {};
  companies.forEach(c => { (c.validation || []).forEach(v => { valCounts[v.status] = (valCounts[v.status] || 0) + 1; }); });
  const statusColors = { confirmed: 'var(--accent)', needs_review: '#ffaa44', flagged: '#ff4444' };
  document.getElementById('q-val-stats').innerHTML = Object.entries(valCounts).map(([s, n]) =>
    `<div style="font-size:.85rem"><span style="color:${statusColors[s] || '#aaa'};font-family:monospace">${n}</span> <span style="color:#555">${s}</span></div>`
  ).join('');

  document.getElementById('q-enrich-stats').innerHTML =
    `<div style="font-size:.85rem"><span style="color:var(--accent);font-family:monospace">${withEnr}</span> <span style="color:#555">Wikidata enriched</span></div>
     <div style="font-size:.85rem"><span style="color:#555;font-family:monospace">${companies.length - withEnr}</span> <span style="color:#555">not enriched</span></div>`;

  const missing = companies.filter(c => !c.wikidata_id);
  document.getElementById('q-missing').innerHTML = missing.map(c =>
    `<span style="font-size:.72rem;padding:2px 8px;border-radius:50px;background:var(--surface);border:1px solid var(--border);color:#666">${esc(c.name)}</span>`
  ).join('');

  const openIssues = [];
  companies.forEach(c => { (c.validation || []).filter(v => v.status !== 'confirmed').forEach(v => { openIssues.push({ c, v }); }); });
  document.getElementById('q-val-tbody').innerHTML = openIssues.slice(0, 100).map(({ c, v }) => `
    <tr>
      <td style="font-size:.82rem"><strong>${esc(c.name)}</strong></td>
      <td>${sectorBadge(c.sector)}</td>
      <td><span style="color:${v.status === 'flagged' ? '#ff4444' : '#ffaa44'};font-size:.75rem">${v.status}</span></td>
      <td style="font-size:.75rem;color:#555">${esc((v.description || '').slice(0, 100))}</td>
      <td style="font-size:.68rem;color:#444;font-family:monospace">${v.datestamp || '—'}</td>
    </tr>`).join('');
}
