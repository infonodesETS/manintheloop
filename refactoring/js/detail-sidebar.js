'use strict';

import { AppState } from './state.js';
import { esc, fmtFunding, sectorBadge, typeBadge, dualBadge } from './helpers.js';
import { getParams, setParams } from './url.js';

// ── Entity detail sidebar — shared across Companies, Investors, Relationships ──

function row(label, value) {
  return `<div class="es-row"><span class="es-lbl">${label}</span><span class="es-val">${value}</span></div>`;
}

function section(content) {
  return `<div class="es-block">${content}</div>`;
}

function lbl(text) {
  return `<div class="sl-section-lbl">${text}</div>`;
}

function _open() {
  document.getElementById('entity-sidebar').classList.add('open');
}

export function closeEntitySidebar() {
  document.getElementById('entity-sidebar').classList.remove('open');
  const p = getParams(); delete p.company; delete p.investor; delete p.name; setParams(p);
}

export function initEntitySidebar() {
  document.getElementById('entity-sidebar-overlay').addEventListener('click', closeEntitySidebar);
  document.getElementById('entity-sidebar-close').addEventListener('click', closeEntitySidebar);
  document.getElementById('entity-sidebar-body').addEventListener('click', e => {
    const btn = e.target.closest('[data-nav-tab]');
    if (!btn) return;
    const tab = btn.dataset.navTab;
    const val = btn.dataset.navValue;
    if (tab === 'map' && val) AppState.ui.map.pendingCountry = val;
    if (tab === 'graph' && val) AppState.ui.graph.search = val;
    closeEntitySidebar();
    AppState.navigate?.('supply-chain', tab);
  });
}

export function openIntroSidebar(title, html) {
  const _estEl = document.getElementById('entity-sidebar-title');
  _estEl.textContent = title; _estEl.title = title;
  document.getElementById('entity-sidebar-body').innerHTML = html;
  _open();
}

function cbSection(cb) {
  const hasAny = cb && (cb.profile_url || cb.stage || cb.headquarters || cb.website ||
    cb.cb_rank || cb.revenue_range || cb.total_funding_usd ||
    cb.founders?.length || cb.primary_industry || cb.industries?.length ||
    cb.industry_groups?.length || cb.patents_granted != null ||
    cb.investor_type || cb.domain || cb.acquired_by);

  let inner = `<div class="es-cb-header">Data from Crunchbase</div>`;

  if (!hasAny) {
    inner += `<div class="es-na">not available</div>`;
    return `<div class="es-block es-cb-block">${inner}</div>`;
  }

  if (cb.description_full && cb.description_full !== cb.description)
    inner += `<div class="es-desc es-cb-desc">${esc(cb.description_full)}</div>`;

  if (cb.profile_url)
    inner += row('Profile', `<a href="${esc(cb.profile_url)}" target="_blank" style="color:var(--cb-accent)">${esc(cb.profile_url)} ↗</a>`);
  if (cb.headquarters)  inner += row('HQ', esc(cb.headquarters));
  if (cb.website)       inner += row('Website', `<a href="${esc(cb.website)}" target="_blank" style="color:var(--cb-accent)">${esc(cb.website)} ↗</a>`);
  if (cb.domain)        inner += row('Domain', esc(cb.domain));
  if (cb.stage)         inner += row('Stage', esc(cb.stage));
  if (cb.revenue_range) inner += row('Revenue', esc(cb.revenue_range));
  if (cb.total_funding_usd)
    inner += row('Total funding', fmtFunding(cb.total_funding_usd));
  if (cb.total_funding_native && cb.total_funding_native.currency !== 'USD' && cb.total_funding_native.amount)
    inner += row(`Funding (${esc(cb.total_funding_native.currency)})`, Number(cb.total_funding_native.amount).toLocaleString());
  if (cb.cb_rank)       inner += row('CB Rank', String(cb.cb_rank));
  if (cb.investor_type) inner += row('Investor type', esc(cb.investor_type));
  if (cb.patents_granted != null && cb.patents_granted !== '')
    inner += row('Patents', String(cb.patents_granted));
  if (cb.acquired_by) {
    const val = cb.acquired_by_url
      ? `<a href="${esc(cb.acquired_by_url)}" target="_blank" style="color:var(--cb-accent)">${esc(cb.acquired_by)} ↗</a>`
      : esc(cb.acquired_by);
    inner += row('Acquired by', val);
  }

  if (cb.founders?.length)
    inner += `${lbl('Founders')}<div class="es-tags" style="margin:.3rem 0 .6rem">${cb.founders.map(f => `<span class="es-tag">${esc(f)}</span>`).join('')}</div>`;

  if (cb.primary_industry)
    inner += row('Primary industry', esc(cb.primary_industry));

  if (cb.industries?.length)
    inner += `${lbl('Industries')}<div class="es-tags" style="margin:.3rem 0 .6rem">${cb.industries.map(i => `<span class="es-tag">${esc(i)}</span>`).join('')}</div>`;

  if (cb.industry_groups?.length)
    inner += `${lbl('Industry groups')}<div class="es-tags" style="margin:.3rem 0 .6rem">${cb.industry_groups.map(g => `<span class="es-tag">${esc(g)}</span>`).join('')}</div>`;

  if (cb.extracted_at)
    inner += `<div class="es-cb-updated">extracted ${esc(cb.extracted_at)}</div>`;

  return `<div class="es-block es-cb-block">${inner}</div>`;
}

function wdSection(wd, wikidata_id) {
  let inner = `<div class="es-wd-header">Data from Wikipedia / Wikidata</div>`;

  if (!wd) {
    inner += `<div class="es-na">not available</div>`;
    return `<div class="es-block es-wd-block">${inner}</div>`;
  }

  if (wd.description) inner += `<div class="es-desc es-wd-desc">${esc(wd.description)}</div>`;

  if (wd.aliases?.length)
    inner += `<div class="es-tags" style="margin:.45rem 0">${wd.aliases.map(a => `<span class="es-tag">${esc(a)}</span>`).join('')}</div>`;

  if (wd.instance_of?.length)
    inner += `${lbl('Type')}<div class="es-tags" style="margin:.3rem 0 .6rem">${wd.instance_of.map(i => `<span class="es-tag">${esc(i)}</span>`).join('')}</div>`;

  if (wd.headquarters)  inner += row('HQ', esc(wd.headquarters));
  if (wd.employees)     inner += row('Employees', Number(wd.employees).toLocaleString());
  if (wd.isin)          inner += row('ISIN', `<span style="font-family:monospace">${esc(wd.isin)}</span>`);
  if (wd.official_website) inner += row('Official site', `<a href="${esc(wd.official_website)}" target="_blank" style="color:var(--accent)">${esc(wd.official_website)} ↗</a>`);
  if (wd.wikipedia_url) inner += row('Wikipedia', `<a href="${esc(wd.wikipedia_url)}" target="_blank" style="color:var(--accent)">en.wikipedia.org ↗</a>`);

  const wdHref = wikidata_id ? `https://www.wikidata.org/wiki/${esc(wikidata_id)}` : null;
  if (wdHref)           inner += row('Wikidata', `<a href="${wdHref}" target="_blank" style="color:var(--accent)">${esc(wikidata_id)} ↗</a>`);

  if (wd.retrieved_at)  inner += `<div class="es-wd-updated">retrieved ${esc(wd.retrieved_at)}</div>`;

  return `<div class="es-block es-wd-block">${inner}</div>`;
}

export function openCompanySidebar(company) {
  const wd  = company.sources?.wikidata;
  const cb  = company.sources?.crunchbase;
  const inf = company.sources?.infonodes;

  const country = wd?.country || inf?.country || '—';
  const founded = wd?.inception ? String(wd.inception).slice(0, 4) : '—';

  const desc = cb?.description || cb?.description_full;

  let html = `
    <div class="es-header-meta">
      ${sectorBadge(company.sector)}
      ${company.roles?.includes('investor') ? dualBadge() : ''}
      <span class="es-id">${esc(company.id)}</span>
    </div>`;

  if (desc) html += section(`<div class="es-desc">${esc(desc)}</div>`);

  html += section(`
    ${row('Country', esc(country))}
    ${row('Founded', esc(founded))}
  `);

  html += cbSection(cb);

  html += wdSection(wd, company.wikidata_id);

  if (inf?.main_focus) {
    html += section(`${lbl('Focus')}<div class="es-desc">${esc(inf.main_focus)}</div>`);
  }

  if (company._investors?.length) {
    html += section(`${lbl(`Investors (${company._investors.length})`)}
      <ul class="es-list">
        ${company._investors.map(({ name, lead }) => {
          const im = AppState.derived.invMap[name];
          return `<li>${im ? typeBadge(im.entity.type) : ''} ${esc(name)} ${lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`;
        }).join('')}
      </ul>`);
  }

  const issues = (company.validation || []).filter(v => v.status !== 'confirmed');
  if (issues.length) {
    html += section(`${lbl('Validation')}
      <ul class="es-list">
        ${issues.map(v =>
          `<li><span style="color:${v.status === 'flagged' ? '#ff4444' : '#ffaa44'}">${esc(v.status)}</span> — ${esc(v.description)}</li>`
        ).join('')}
      </ul>`);
  }

  const navBtns = [
    country !== '—' ? `<button class="es-nav-btn" data-nav-tab="map" data-nav-value="${esc(country)}">Map: ${esc(country)} ↗</button>` : '',
    `<button class="es-nav-btn" data-nav-tab="graph" data-nav-value="${esc(company.name)}">Graph ↗</button>`,
  ].filter(Boolean).join('');
  if (navBtns) html += section(`${lbl('Explore in')}<div>${navBtns}</div>`);

  const _estEl2 = document.getElementById('entity-sidebar-title');
  _estEl2.textContent = company.name; _estEl2.title = company.name;
  document.getElementById('entity-sidebar-body').innerHTML = html;
  setParams({ ...getParams(), company: company.id, name: company.name });
  _open();
}

export function openInvestorSidebar(im) {
  const entity = im.entity;
  const wd  = entity.sources?.wikidata;
  const cb  = entity.sources?.crunchbase;

  const desc = cb?.description || cb?.description_full;

  let html = `
    <div class="es-header-meta">
      ${typeBadge(entity.type)}
      <span class="es-id">${esc(entity.id)}</span>
    </div>`;

  if (desc) html += section(`<div class="es-desc">${esc(desc)}</div>`);

  html += section(`
    ${row('Portfolio', im.total)}
    ${row('Lead investments', im.leads)}
  `);

  html += wdSection(wd, entity.wikidata_id);

  if (im.portfolio.length) {
    html += section(`${lbl(`Companies (${im.portfolio.length})`)}
      <ul class="es-list">
        ${im.portfolio.map(({ company, lead }) =>
          `<li>${sectorBadge(company?.sector)} ${esc(company?.name || '?')} ${lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`
        ).join('')}
      </ul>`);
  }

  html += section(`${lbl('Explore in')}<div><button class="es-nav-btn" data-nav-tab="graph" data-nav-value="${esc(entity.name)}">Graph ↗</button></div>`);

  const _estEl3 = document.getElementById('entity-sidebar-title');
  _estEl3.textContent = entity.name; _estEl3.title = entity.name;
  document.getElementById('entity-sidebar-body').innerHTML = html;
  setParams({ ...getParams(), investor: entity.id, name: entity.name });
  _open();
}
