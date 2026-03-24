'use strict';

import { AppState } from '../state.js';
import { esc, fmtFunding, sectorBadge, typeBadge, typeDot, dualBadge, tip, hideTip } from '../helpers.js';

export default function initMatrix() {
  renderMatrix();
}

export function setMatrixSector(s) {
  AppState.ui.matrix.sector = s;
  AppState.COMPANIES = s === 'all' ? [...AppState.ALL_COMPANIES] : AppState.ALL_COMPANIES.filter(c => c.sector === s);
  renderMatrix();
}

export function renderMatrix() {
  const { COMPANIES, INVESTORS, derived } = AppState;
  const { raw, invMap } = derived;
  const maxTotal = INVESTORS[0]?.total || 1;
  const filtered = INVESTORS.filter(im => im.portfolio.some(p => COMPANIES.some(c => c.name === p.company?.name)));

  document.getElementById('mx-info').textContent =
    `${COMPANIES.length} companies · ${filtered.length} investors · ${raw.filter(([c]) => COMPANIES.some(x => x.name === c)).length} investments`;

  let html = '<table>';
  html += '<thead><tr><th style="min-width:210px;padding:0 12px;vertical-align:bottom;padding-bottom:10px"><span style="font-size:var(--fs-xs);color:#555;letter-spacing:.5px">INVESTOR</span></th>';
  COMPANIES.forEach(c => {
    const short = c.name.length > 14 ? c.name.slice(0, 13) + '…' : c.name;
    const cb = c.sources?.crunchbase || {};
    const loc = cb.headquarters || '';
    html += `<th class="col-hdr" data-company="${esc(c.name)}" data-action="mxShowCompany">
      <span class="col-inner"><abbr title="${esc(c.name)} · ${esc(loc)}">${esc(short)}</abbr></span>
    </th>`;
  });
  html += '<th style="min-width:90px;padding:0 10px;vertical-align:bottom;padding-bottom:10px;border-left:2px solid var(--border)"><span style="font-size:var(--fs-xs);color:#555">TOTAL</span></th></tr></thead>';

  html += '<tbody>';
  filtered.forEach((im, idx) => {
    const pf = {};
    im.portfolio.forEach(p => { if (p.company) pf[p.company.name] = p.lead; });

    const cc = im.total >= 3 ? 'c3' : im.total === 2 ? 'c2' : 'c1';
    const leadLbl = im.leads > 0 ? `<span class="cnt-lead" title="${im.leads} lead">↑${im.leads}</span>` : '';

    html += `<tr data-investor="${esc(im.entity.name)}">
      <td><div class="inv-cell" data-action="mxShowInvestor" data-name="${esc(im.entity.name)}">
        ${typeDot(im.entity.type)}
        <span class="inv-rank">${idx + 1}</span>
        <span class="inv-name">${esc(im.entity.name)}</span>
        ${leadLbl}
        <span class="cnt-pill ${cc}">${im.total}</span>
      </div></td>`;

    COMPANIES.forEach(c => {
      if (c.name in pf) {
        const isLead = pf[c.name];
        const cls = isLead ? 'dot-lead' : 'dot-follow';
        const title = `${im.entity.name} → ${c.name} (${isLead ? 'LEAD' : 'follow'})`;
        html += `<td class="inv-td" data-company="${esc(c.name)}">
          <span class="${cls}" title="${esc(title)}"
            data-tip-name="${esc(im.entity.name)} → ${esc(c.name)}"
            data-tip-info="${isLead ? 'Lead investment' : 'Follow investment'}"
            data-tip-sub="${esc(c.sector || '')}"
            data-action="tip"></span></td>`;
      } else {
        html += `<td class="inv-td" data-company="${esc(c.name)}"><span class="dot-none"></span></td>`;
      }
    });

    const pct = (im.total / maxTotal * 100).toFixed(0);
    const bc  = im.total >= 3 ? 'var(--accent)' : im.total === 2 ? 'var(--accent-dim)' : 'rgba(255,255,255,0.35)';
    html += `<td class="bar-cell">
      <span class="bar-track"><span class="bar-fill" style="width:${pct}%;background:${bc}"></span></span>
      <span style="font-size:var(--fs-sm);color:${bc};margin-left:6px;font-weight:600">${im.total}</span>
    </td></tr>`;
  });
  html += '</tbody></table>';
  document.getElementById('matrix-scroll').innerHTML = html;

  // Attach event handlers
  document.getElementById('matrix-scroll').querySelectorAll('[data-action="mxShowInvestor"]').forEach(el => {
    el.addEventListener('click', () => mxShowInvestor(el.dataset.name));
  });
  document.getElementById('matrix-scroll').querySelectorAll('[data-action="mxShowCompany"]').forEach(el => {
    el.addEventListener('click', () => mxShowCompany(el.dataset.company));
  });
  document.getElementById('matrix-scroll').querySelectorAll('[data-action="tip"]').forEach(el => {
    el.addEventListener('mouseenter', e => tip(e, el.dataset.tipName, el.dataset.tipInfo, el.dataset.tipSub));
    el.addEventListener('mouseleave', hideTip);
  });
}

export function mxShowInvestor(name) {
  const { COMPANIES, derived } = AppState;
  const { invMap } = derived;
  const im = invMap[name];
  if (!im) return;
  const panel = document.getElementById('mx-detail');
  const portfolioFiltered = im.portfolio.filter(p => COMPANIES.some(c => c.name === p.company?.name));

  document.getElementById('mx-detail-title').textContent = name;
  let html = typeBadge(im.entity.type);
  html += `<div class="dp-inv-meta">${im.total} investments · ${im.leads} lead</div>`;
  html += `<div class="sl-section-lbl">Portfolio (${portfolioFiltered.length})</div><ul class="es-list">`;
  [...portfolioFiltered].sort((a, b) => (b.lead ? 1 : 0) - (a.lead ? 1 : 0)).forEach(p => {
    html += `<li><span>${esc(p.company?.name)}</span>${p.lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`;
  });
  html += '</ul>';

  const coSet = {};
  im.portfolio.forEach(p => {
    (p.company?._investors || []).filter(x => x.name !== name).forEach(o => {
      coSet[o.name] = (coSet[o.name] || 0) + 1;
    });
  });
  const coList = Object.entries(coSet).sort((a, b) => b[1] - a[1]).slice(0, 6);
  if (coList.length) {
    html += '<div class="sl-section-lbl">Co-investors</div><ul class="es-list">';
    coList.forEach(([n, cnt]) => {
      html += `<li><span>${esc(n)}</span><span class="dp-co-count">${cnt > 1 ? cnt + '×' : ''}</span></li>`;
    });
    html += '</ul>';
  }

  document.getElementById('mx-inner').innerHTML = html;
  panel.classList.add('open');
}

export function mxShowCompany(name) {
  const { derived } = AppState;
  const { companyMap } = derived;
  const c = companyMap[name];
  if (!c) return;
  const wd = c.sources?.wikidata;
  const cb = c.sources?.crunchbase;
  document.getElementById('mx-detail-title').textContent = name;
  let html = '';
  if (c.sector) html += `${sectorBadge(c.sector)} `;
  html += `<span class="badge-type badge-type--company">Manufacturer</span>`;
  if (c.roles?.includes('investor')) html += ` ${dualBadge()}`;

  const country   = wd?.country || '';
  const inception = wd?.inception ? String(wd.inception).slice(0, 4) : '';
  const meta = [country, inception ? `est. ${inception}` : ''].filter(Boolean).join(' · ');
  if (meta) html += `<div class="dp-co-meta">${esc(meta)}</div>`;

  const funding = cb?.total_funding_usd;
  if (funding) html += `<div class="dp-funding">Funding: <span>${fmtFunding(funding)}</span></div>`;

  const desc = cb?.description || wd?.description;
  if (desc) html += `<div class="dp-desc">${esc(desc.slice(0, 200))}${desc.length > 200 ? '…' : ''}</div>`;

  const links = [];
  if (cb?.website) links.push(`<a href="${esc(cb.website)}" target="_blank" class="dp-link">Website ↗</a>`);
  if (wd?.wikipedia_url) links.push(`<a href="${esc(wd.wikipedia_url)}" target="_blank" class="dp-link">Wikipedia ↗</a>`);
  if (links.length) html += `<div class="dp-links">${links.join('')}</div>`;

  if (c._investors?.length) {
    html += `<div class="sl-section-lbl">Investors (${c._investors.length})</div><ul class="es-list">`;
    [...c._investors].sort((a, b) => (b.lead ? 1 : 0) - (a.lead ? 1 : 0)).forEach(x => {
      html += `<li><span>${esc(x.name)}</span>${x.lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`;
    });
    html += '</ul>';
  }

  document.getElementById('mx-inner').innerHTML = html;
  document.getElementById('mx-detail').classList.add('open');
}

export function closeMxDetail() {
  document.getElementById('mx-detail').classList.remove('open');
}
