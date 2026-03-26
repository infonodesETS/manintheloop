'use strict';

import { AppState } from '../state.js';
import { esc, fmtFunding, sectorBadge, typeBadge, dualBadge } from '../helpers.js';
import { setParams, getParams } from '../url.js';

// ── Local helpers ──────────────────────────────────────────────────────────
function initials(name) {
  return name.split(/\s+/).map(w => w[0] || '').join('').slice(0, 2).toUpperCase() || '?';
}
function highlight(text, q) {
  if (!q) return esc(text);
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return esc(text).replace(re, '<mark>$1</mark>');
}
function entityLink(other, fallback) {
  if (!other) return esc(fallback);
  return `<button class="cs-elist-link" data-entity-id="${esc(other.id)}">${esc(other.name)}</button>`;
}
function row(lbl, val) {
  return `<div class="cs-row">
    <span class="cs-row-lbl">${lbl}</span>
    <span class="cs-row-val">${val}</span>
  </div>`;
}

// ── Searchable entity list (built once on first use) ───────────────────────
let SEARCH_ENTITIES = null;
function getSearchEntities() {
  if (SEARCH_ENTITIES) return SEARCH_ENTITIES;
  SEARCH_ENTITIES = Object.values(AppState.derived.entityMap).map(e => ({
    e,
    _key: [
      e.name,
      e.sources?.crunchbase?.headquarters,
      e.sources?.infonodes?.country,
      e.sources?.wikidata?.country,
      e.sources?.crunchbase?.domain,
    ].filter(Boolean).join(' ').toLowerCase(),
  }));
  return SEARCH_ENTITIES;
}

// ── Autocomplete state ─────────────────────────────────────────────────────
let searchEl, acEl;
let acFlatList = [], acKbd = -1;

function closeAc() {
  acEl.classList.remove('open');
  acEl.innerHTML = '';
  acKbd = -1;
  acFlatList = [];
}

function renderAc(raw) {
  const q = raw.trim().toLowerCase();
  if (!q) { closeAc(); return; }

  const scored = getSearchEntities().map(({ e, _key }) => {
    const n = e.name.toLowerCase();
    let s = 0;
    if (n === q)               s = 200;
    else if (n.startsWith(q))  s = 100;
    else if (n.includes(q))    s = 60;
    else if (_key.includes(q)) s = 20;
    return { e, s };
  }).filter(x => x.s > 0).sort((a, b) => b.s - a.s || a.e.name.localeCompare(b.e.name));

  if (!scored.length) {
    acEl.innerHTML = `<div class="cs-ac-empty">No results for "<strong>${esc(raw)}</strong>"</div>`;
    acEl.classList.add('open');
    acFlatList = [];
    return;
  }

  const companies = scored.filter(x => x.e.id.startsWith('IN-'));
  const investors = scored.filter(x => x.e.id.startsWith('IV-'));
  acFlatList = [];
  let html = '';

  function renderGroup(label, items, limit) {
    if (!items.length) return;
    html += `<div class="cs-ac-group">${label}</div>`;
    for (const { e } of items.slice(0, limit)) {
      const country = e.sources?.infonodes?.country || e.sources?.wikidata?.country || '';
      const badge = e.sector ? sectorBadge(e.sector) : typeBadge(e.type);
      html += `<div class="cs-ac-item" role="option" data-idx="${acFlatList.length}">
        ${badge}
        <span class="cs-ac-name">${highlight(e.name, raw)}</span>
        ${country ? `<span class="cs-ac-country">${esc(country)}</span>` : ''}
        <span class="cs-ac-id">${esc(e.id)}</span>
      </div>`;
      acFlatList.push(e);
    }
  }

  renderGroup('Companies', companies, 14);
  renderGroup('Investors', investors, 10);

  acEl.innerHTML = html;
  acEl.classList.add('open');

  acEl.querySelectorAll('.cs-ac-item').forEach(el => {
    el.addEventListener('mousedown', ev => {
      ev.preventDefault();
      const idx = Number(el.dataset.idx);
      if (acFlatList[idx]) selectEntity(acFlatList[idx]);
    });
  });
}

function moveAcKbd(delta) {
  const items = acEl.querySelectorAll('.cs-ac-item');
  if (!items.length) return;
  items[acKbd]?.classList.remove('kbd');
  acKbd = Math.max(-1, Math.min(items.length - 1, acKbd + delta));
  if (acKbd >= 0) {
    items[acKbd].classList.add('kbd');
    items[acKbd].scrollIntoView({ block: 'nearest' });
    if (acFlatList[acKbd]) searchEl.value = acFlatList[acKbd].name;
  }
}

// ── Selection / clear ──────────────────────────────────────────────────────
function selectEntity(entity) {
  closeAc();
  searchEl.value = entity.name;
  AppState.ui.companysearch.entityId = entity.id;
  setParams({ research: 'company-search', entity: entity.id }, true);
  document.getElementById('cs-hero').classList.add('compact');
  document.getElementById('cs-showing').textContent = entity.name;
  renderProfile(entity);
}

function clearSelection() {
  AppState.ui.companysearch.entityId = null;
  setParams({ research: 'company-search' }, true);
  searchEl.value = '';
  document.getElementById('cs-hero').classList.remove('compact');
  document.getElementById('cs-showing').textContent = '';
  document.getElementById('cs-profile').classList.remove('visible');
  searchEl.focus();
}

// ── Render profile ─────────────────────────────────────────────────────────
function renderProfile(entity) {
  const profile = document.getElementById('cs-profile');
  profile.classList.remove('visible');
  void profile.offsetWidth; // force re-animation
  profile.classList.add('visible');

  const cb  = entity.sources?.crunchbase;
  const wd  = entity.sources?.wikidata;
  const inf = entity.sources?.infonodes;

  const isCompany  = entity.type === 'company';
  const isDual     = isCompany && entity.roles?.includes('investor');
  const rels       = AppState.derived.relMap[entity.id] || [];
  const asInvestor = rels.filter(r => r.role === 'investor');
  const asTarget   = rels.filter(r => r.role === 'target');

  /* Logo */
  document.getElementById('cs-logo').textContent = initials(entity.name);

  /* Name */
  document.getElementById('cs-name').textContent = entity.name;

  /* Badges */
  let badges = '';
  if (entity.sector) badges += sectorBadge(entity.sector);
  if (!isCompany || !entity.sector) badges += typeBadge(entity.type);
  if (isDual) badges += dualBadge();
  badges += `<span class="cs-hdr-id">${esc(entity.id)}</span>`;
  document.getElementById('cs-badges').innerHTML = badges;

  /* Short description */
  const shortDesc = cb?.description || wd?.description;
  const descEl = document.getElementById('cs-desc');
  descEl.textContent = shortDesc || '';
  descEl.style.display = shortDesc ? '' : 'none';

  /* External links */
  let links = '';
  if (cb?.profile_url)
    links += `<a class="cs-ext-link cs-cb" href="${esc(cb.profile_url)}" target="_blank">Crunchbase ↗</a>`;
  if (cb?.website)
    links += `<a class="cs-ext-link" href="${esc(cb.website)}" target="_blank">${esc(cb.website.replace(/^https?:\/\/(www\.)?/, '').replace(/\/.*$/, ''))} ↗</a>`;
  if (wd?.official_website && wd.official_website !== cb?.website)
    links += `<a class="cs-ext-link" href="${esc(wd.official_website)}" target="_blank">Official site ↗</a>`;
  if (wd?.wikipedia_url)
    links += `<a class="cs-ext-link cs-wd" href="${esc(wd.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`;
  if (inf?.wikipedia_url && inf.wikipedia_url !== wd?.wikipedia_url)
    links += `<a class="cs-ext-link cs-wd" href="${esc(inf.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`;
  if (entity.wikidata_id)
    links += `<a class="cs-ext-link cs-wd" href="https://www.wikidata.org/wiki/${esc(entity.wikidata_id)}" target="_blank">${esc(entity.wikidata_id)} ↗</a>`;
  document.getElementById('cs-links').innerHTML = links;

  /* Stat bar */
  const statsEl = document.getElementById('cs-stats');
  const stats = [];
  const founded = wd?.inception ? String(wd.inception).slice(0, 4) : null;
  if (cb?.total_funding_usd)  stats.push({ v: fmtFunding(cb.total_funding_usd), l: 'Total Funding' });
  if (wd?.employees)          stats.push({ v: Number(wd.employees).toLocaleString(), l: 'Employees' });
  if (founded)                stats.push({ v: founded,                              l: 'Founded' });
  if (cb?.cb_rank)            stats.push({ v: `#${cb.cb_rank}`,                     l: 'CB Rank' });
  if (cb?.revenue_range)      stats.push({ v: esc(cb.revenue_range),                l: 'Revenue' });
  if (cb?.patents_granted != null && cb.patents_granted !== '')
                              stats.push({ v: cb.patents_granted,                   l: 'Patents' });
  if (isCompany && asTarget.length) stats.push({ v: asTarget.length,               l: 'Investors' });
  if (asInvestor.length)      stats.push({ v: asInvestor.length,                   l: 'Portfolio' });
  statsEl.innerHTML = stats.map(s =>
    `<div class="cs-stat"><div class="cs-stat-val">${s.v}</div><div class="cs-stat-lbl">${s.l}</div></div>`
  ).join('');
  statsEl.style.display = stats.length ? '' : 'none';

  /* Key facts */
  const country = wd?.country || inf?.country;
  let factsHtml = '';
  if (country)           factsHtml += row('Country',       esc(country));
  if (founded)           factsHtml += row('Founded',       esc(founded));
  if (cb?.headquarters)  factsHtml += row('Headquarters',  esc(cb.headquarters));
  if (cb?.stage)         factsHtml += row('Stage',         esc(cb.stage));
  if (cb?.domain)        factsHtml += row('Domain',        `<a href="https://${esc(cb.domain)}" target="_blank">${esc(cb.domain)} ↗</a>`);
  if (wd?.isin)          factsHtml += row('ISIN',          `<code>${esc(wd.isin)}</code>`);
  if (cb?.investor_type) factsHtml += row('Investor type', esc(cb.investor_type));
  if (inf?.tax_id)       factsHtml += row('Tax ID',        `<code>${esc(inf.tax_id)}</code>`);
  if (entity.roles?.length) factsHtml += row('Roles',      entity.roles.map(esc).join(', '));
  if (cb?.acquired_by) {
    const v = cb.acquired_by_url
      ? `<a href="${esc(cb.acquired_by_url)}" target="_blank">${esc(cb.acquired_by)} ↗</a>`
      : esc(cb.acquired_by);
    factsHtml += row('Acquired by', v);
  }
  document.getElementById('cs-facts-body').innerHTML =
    factsHtml || `<div class="cs-na">No key facts recorded.</div>`;

  /* Full description */
  const aboutCard = document.getElementById('cs-about-card');
  const fullDesc  = cb?.description_full;
  if (fullDesc && fullDesc !== shortDesc) {
    document.getElementById('cs-about-body').innerHTML =
      `<p class="cs-about-text">${esc(fullDesc)}</p>`;
    aboutCard.style.display = '';
  } else {
    aboutCard.style.display = 'none';
  }

  /* Founders */
  const foundersCard = document.getElementById('cs-founders-card');
  if (cb?.founders?.length) {
    document.getElementById('cs-founders-body').innerHTML =
      `<div class="cs-founders">${cb.founders.map(f => `<span class="cs-founder">${esc(f)}</span>`).join('')}</div>`;
    foundersCard.style.display = '';
  } else {
    foundersCard.style.display = 'none';
  }

  /* Industries & Focus */
  const indCard = document.getElementById('cs-ind-card');
  let indHtml = '';
  if (inf?.main_focus)
    indHtml += `<p class="cs-src-desc">${esc(inf.main_focus)}</p>`;
  if (cb?.primary_industry) {
    const val = cb.primary_industry_url
      ? `<a href="${esc(cb.primary_industry_url)}" target="_blank">${esc(cb.primary_industry)} ↗</a>`
      : esc(cb.primary_industry);
    indHtml += row('Primary', val);
  }
  if (cb?.industries?.length)
    indHtml += `<div class="cs-row"><span class="cs-row-lbl">Industries</span><span class="cs-row-val"><div class="cs-tags">${cb.industries.map(i => `<span class="cs-tag">${esc(i)}</span>`).join('')}</div></span></div>`;
  if (cb?.industry_groups?.length)
    indHtml += `<div class="cs-row"><span class="cs-row-lbl">Groups</span><span class="cs-row-val"><div class="cs-tags">${cb.industry_groups.map(g => `<span class="cs-tag">${esc(g)}</span>`).join('')}</div></span></div>`;
  if (indHtml) { document.getElementById('cs-ind-body').innerHTML = indHtml; indCard.style.display = ''; }
  else indCard.style.display = 'none';

  /* Tags */
  const tagsCard = document.getElementById('cs-tags-card');
  if (entity.tags?.length) {
    document.getElementById('cs-tags-body').innerHTML =
      `<div class="cs-tags">${entity.tags.map(t => `<span class="cs-tag">${esc(t)}</span>`).join('')}</div>`;
    tagsCard.style.display = '';
  } else {
    tagsCard.style.display = 'none';
  }

  /* Relationships */
  const relHdrLbl   = document.getElementById('cs-rel-hdr-lbl');
  const relHdrCount = document.getElementById('cs-rel-hdr-count');
  const relBody     = document.getElementById('cs-rel-body');
  let relHtml = '', relTotal = 0;

  if (isCompany && asTarget.length) {
    relTotal += asTarget.length;
    if (isDual && asInvestor.length)
      relHtml += `<div class="cs-rel-group-lbl">Investors (${asTarget.length})</div>`;
    relHtml += `<ul class="cs-elist">` + asTarget.map(r => {
      const lead  = r.rel.details?.lead;
      const badge = r.other ? typeBadge(r.other.type) : '';
      const name  = entityLink(r.other, r.rel.source);
      const meta  = [r.rel.id, r.rel.added_at, r.rel.sources?.join(', ')].filter(Boolean).join(' · ');
      return `<li>${badge}<div class="cs-elist-item-main"><span class="cs-elist-name">${name}</span>${meta ? `<div class="cs-elist-meta">${esc(meta)}</div>` : ''}</div>${lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`;
    }).join('') + `</ul>`;
  }

  if (asInvestor.length) {
    relTotal += asInvestor.length;
    if (isCompany && asTarget.length)
      relHtml += `<div class="cs-rel-group-lbl">Portfolio (${asInvestor.length})</div>`;
    relHtml += `<ul class="cs-elist">` + asInvestor.map(r => {
      const lead    = r.rel.details?.lead;
      const badge   = r.other ? sectorBadge(r.other.sector) || typeBadge(r.other.type) : '';
      const name    = entityLink(r.other, r.rel.target);
      const country = r.other ? (r.other.sources?.infonodes?.country || r.other.sources?.wikidata?.country || '') : '';
      const meta    = [r.rel.id, r.rel.added_at, r.rel.sources?.join(', ')].filter(Boolean).join(' · ');
      return `<li>${badge}<div class="cs-elist-item-main"><span class="cs-elist-name">${name}</span>${meta ? `<div class="cs-elist-meta">${esc(meta)}</div>` : ''}</div>${country ? `<span class="cs-elist-country">${esc(country)}</span>` : ''}${lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`;
    }).join('') + `</ul>`;
  }

  // Non-investment relationships
  const otherRels = AppState.derived.otherRelMap[entity.id] || [];
  if (otherRels.length) {
    relHtml += `<div class="cs-rel-group-lbl">Other (${otherRels.length})</div>`;
    relHtml += `<ul class="cs-elist">` + otherRels.map(r => {
      const name  = entityLink(r.other, r.role === 'source' ? r.rel.target : r.rel.source);
      const badge = r.other ? (sectorBadge(r.other.sector) || typeBadge(r.other.type)) : '';
      const meta  = [r.rel.id, r.rel.type, r.rel.added_at, r.rel.sources?.join(', ')].filter(Boolean).join(' · ');
      return `<li>${badge}<div class="cs-elist-item-main"><span class="cs-elist-name">${name}</span>${meta ? `<div class="cs-elist-meta">${esc(meta)}</div>` : ''}</div></li>`;
    }).join('') + `</ul>`;
    relTotal += otherRels.length;
  }

  if (!relHtml) {
    relHdrLbl.textContent = 'Connections';
    relHdrCount.textContent = '';
    relBody.innerHTML = `<div class="cs-na">No relationships recorded.</div>`;
  } else {
    const bothRoles = isCompany && asTarget.length && asInvestor.length;
    relHdrLbl.textContent = bothRoles ? 'Investors & Portfolio' : (asTarget.length ? 'Investors' : 'Portfolio');
    relHdrCount.textContent = relTotal;
    relBody.innerHTML = relHtml;
  }

  /* History */
  const histCard  = document.getElementById('cs-hist-card');
  const histList  = document.getElementById('cs-hist-list');
  const histCount = document.getElementById('cs-hist-count');
  if (entity.history?.length) {
    const entries = [...entity.history].reverse().slice(0, 25);
    const trunc = v => { const s = String(v ?? 'null'); return s.length > 60 ? s.slice(0, 60) + '…' : s; };
    histList.innerHTML = entries.map(h => {
      const desc = h.description || (
        h.field && h.field !== '*'
          ? `Updated ${h.field}: ${h.old ?? 'null'} → ${h.new ?? 'null'}`
          : 'Record created'
      );
      const hasDiff = h.description && h.field && h.field !== '*' && (h.old != null || h.new != null);
      const diff = hasDiff ? `<div class="cs-hist-meta">${esc(trunc(h.old))} → ${esc(trunc(h.new))}</div>` : '';
      const meta = [h.field && h.field !== '*' ? h.field : null, h.source, h.author].filter(Boolean).join(' · ');
      return `<li class="cs-hist-item">
        <div class="cs-hist-date">${esc(h.date || '')}</div>
        <div>
          <div class="cs-hist-desc">${esc(desc)}</div>
          ${diff}
          ${meta ? `<div class="cs-hist-meta">${esc(meta)}</div>` : ''}
        </div>
      </li>`;
    }).join('');
    histCount.textContent = entity.history.length > 25
      ? `${entries.length} of ${entity.history.length}` : entity.history.length;
    histCard.style.display = '';
  } else {
    histCard.style.display = 'none';
  }

  /* Crunchbase block */
  const cbBody = document.getElementById('cs-cb-body');
  if (cb) {
    let cbHtml = '';
    if (cb.total_funding_usd)
      cbHtml += row('Funding (USD)', `<span class="cs-funding-val">${fmtFunding(cb.total_funding_usd)}</span>`);
    if (cb.total_funding_native?.amount && cb.total_funding_native.currency !== 'USD')
      cbHtml += row(`Funding (${esc(cb.total_funding_native.currency)})`, Number(cb.total_funding_native.amount).toLocaleString());
    if (cb.revenue_range)  cbHtml += row('Revenue', esc(cb.revenue_range));
    if (cb.cb_rank)        cbHtml += row('CB Rank', `#${cb.cb_rank}`);
    if (cb.stage)          cbHtml += row('Stage', esc(cb.stage));
    if (cb.patents_granted != null && cb.patents_granted !== '')
      cbHtml += row('Patents', String(cb.patents_granted));
    if (cb.extracted_at)   cbHtml += `<div class="cs-src-ts">extracted ${esc(cb.extracted_at)}</div>`;
    cbBody.innerHTML = cbHtml || `<div class="cs-na">Crunchbase data available but no enriched fields.</div>`;
  } else {
    cbBody.innerHTML = `<div class="cs-na">No Crunchbase data.</div>`;
  }

  /* Wikidata block */
  const wdBody = document.getElementById('cs-wd-body');
  if (wd) {
    let wdHtml = '';
    if (wd.label && wd.label !== entity.name) wdHtml += row('Label', esc(wd.label));
    if (wd.description) wdHtml += `<div class="cs-src-desc">${esc(wd.description)}</div>`;
    if (wd.instance_of?.length)
      wdHtml += `<div class="cs-tags">${wd.instance_of.map(i => `<span class="cs-tag">${esc(i)}</span>`).join('')}</div>`;
    if (wd.headquarters) wdHtml += row('HQ', esc(wd.headquarters));
    if (wd.employees)    wdHtml += row('Employees', Number(wd.employees).toLocaleString());
    if (wd.isin)         wdHtml += row('ISIN', `<code>${esc(wd.isin)}</code>`);
    if (wd.aliases?.length)
      wdHtml += `<div class="cs-tags">${wd.aliases.map(a => `<span class="cs-tag">${esc(a)}</span>`).join('')}</div>`;
    if (wd.retrieved_at) wdHtml += `<div class="cs-src-ts">retrieved ${esc(wd.retrieved_at)}</div>`;
    wdBody.innerHTML = wdHtml || `<div class="cs-na">Wikidata record exists but has no enriched fields.</div>`;
  } else {
    wdBody.innerHTML = `<div class="cs-na">No Wikidata enrichment.</div>`;
  }

  /* infonodes block */
  const infBody = document.getElementById('cs-inf-body');
  if (inf) {
    let infHtml = '';
    if (inf.sector)       infHtml += row('Sector', esc(inf.sector));
    if (inf.extracted_at) infHtml += `<div class="cs-src-ts">extracted ${esc(inf.extracted_at)}</div>`;
    infBody.innerHTML = infHtml || `<div class="cs-na">infonodes record exists but no additional fields.</div>`;
  } else {
    infBody.innerHTML = `<div class="cs-na">No infonodes enrichment.</div>`;
  }

  /* Validation flags */
  const valCard  = document.getElementById('cs-val-card');
  const valBody  = document.getElementById('cs-val-body');
  const valCount = document.getElementById('cs-val-count');
  const openFlags = (entity.validation || []).filter(v => v.status !== 'confirmed');
  if (openFlags.length) {
    valBody.innerHTML = openFlags.map(v => {
      const meta = [v.author, v.datestamp].filter(Boolean).join(' · ');
      return `<div class="cs-val-item">
        <span class="cs-val-badge ${esc(v.status)}">${v.status === 'flagged' ? '⛔' : '⚠'} ${esc(v.status)}</span>
        <div>
          <div class="cs-val-desc">${esc(v.description || '')}</div>
          ${meta ? `<div class="cs-hist-meta">${esc(meta)}</div>` : ''}
        </div>
      </div>`;
    }).join('');
    valCount.textContent = openFlags.length;
    valCard.style.display = '';
  } else {
    valCard.style.display = 'none';
  }

  document.getElementById('tab-company-search').scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Export / Copy for AI ───────────────────────────────────────────────────
export function buildCompanySearchSnapshot() {
  const entityId = AppState.ui.companysearch?.entityId;
  if (!entityId) {
    return `# Man in the Loop — Company Search\n\n_No entity selected. Use Company Search to find and select an entity._\n`;
  }
  const entity = AppState.derived.entityMap[entityId];
  if (!entity) return `# Man in the Loop — Company Search\n\n_Entity not found: ${entityId}_\n`;

  const cb  = entity.sources?.crunchbase;
  const wd  = entity.sources?.wikidata;
  const inf = entity.sources?.infonodes;
  const rels       = AppState.derived.relMap[entity.id] || [];
  const asTarget   = rels.filter(r => r.role === 'target');
  const asInvestor = rels.filter(r => r.role === 'investor');
  const country    = wd?.country || inf?.country || '—';
  const founded    = wd?.inception ? String(wd.inception).slice(0, 4) : '—';

  let md = `# ${entity.name} (${entity.id})\n\n`;
  md += `**Type:** ${entity.type}`;
  if (entity.sector) md += ` · **Sector:** ${entity.sector}`;
  md += ` · **Country:** ${country} · **Founded:** ${founded}\n\n`;

  const shortDesc = cb?.description || wd?.description;
  if (shortDesc) md += `> ${shortDesc}\n\n`;

  // Key facts
  const facts = [];
  if (cb?.headquarters)     facts.push(`- Headquarters: ${cb.headquarters}`);
  if (cb?.stage)            facts.push(`- Stage: ${cb.stage}`);
  if (cb?.domain)           facts.push(`- Domain: ${cb.domain}`);
  if (wd?.isin)             facts.push(`- ISIN: ${wd.isin}`);
  if (inf?.tax_id)          facts.push(`- Tax ID: ${inf.tax_id}`);
  if (entity.roles?.length) facts.push(`- Roles: ${entity.roles.join(', ')}`);
  if (cb?.acquired_by)      facts.push(`- Acquired by: ${cb.acquired_by}`);
  if (facts.length) md += `## Key Facts\n${facts.join('\n')}\n\n`;

  // Financials
  if (cb?.total_funding_usd || cb?.revenue_range || cb?.patents_granted != null) {
    md += `## Financials\n`;
    if (cb.total_funding_usd) {
      md += `- Total funding: ${fmtFunding(cb.total_funding_usd)}`;
      if (cb.total_funding_native?.currency !== 'USD' && cb.total_funding_native?.amount)
        md += ` (${cb.total_funding_native.currency} ${Number(cb.total_funding_native.amount).toLocaleString()})`;
      md += '\n';
    }
    if (cb.revenue_range)   md += `- Revenue: ${cb.revenue_range}\n`;
    if (cb.patents_granted != null && cb.patents_granted !== '') md += `- Patents: ${cb.patents_granted}\n`;
    if (cb.cb_rank)         md += `- Crunchbase rank: #${cb.cb_rank}\n`;
    md += '\n';
  }

  // Full description
  if (cb?.description_full && cb.description_full !== shortDesc)
    md += `## About\n${cb.description_full}\n\n`;

  // Founders
  if (cb?.founders?.length)
    md += `## Founders\n${cb.founders.map(f => `- ${f}`).join('\n')}\n\n`;

  // Industries
  if (cb?.primary_industry || cb?.industries?.length) {
    md += `## Industries\n`;
    if (cb.primary_industry)       md += `- Primary: ${cb.primary_industry}\n`;
    if (cb.industries?.length)     md += `- Industries: ${cb.industries.join(', ')}\n`;
    if (cb.industry_groups?.length) md += `- Groups: ${cb.industry_groups.join(', ')}\n`;
    md += '\n';
  }

  // Tags
  if (entity.tags?.length) md += `## Tags\n${entity.tags.join(', ')}\n\n`;

  // Investors
  if (asTarget.length) {
    md += `## Investors (${asTarget.length})\n`;
    md += asTarget.map(r => {
      const name = r.other?.name || r.rel.source;
      return `- ${name}${r.rel.details?.lead ? ' (LEAD)' : ''}`;
    }).join('\n') + '\n\n';
  }

  // Portfolio
  if (asInvestor.length) {
    md += `## Portfolio (${asInvestor.length})\n`;
    md += asInvestor.map(r => {
      const name    = r.other?.name || r.rel.target;
      const sector  = r.other?.sector ? ` [${r.other.sector}]` : '';
      const ctry    = r.other?.sources?.infonodes?.country || r.other?.sources?.wikidata?.country || '';
      return `- ${name}${sector}${ctry ? ` — ${ctry}` : ''}${r.rel.details?.lead ? ' (LEAD)' : ''}`;
    }).join('\n') + '\n\n';
  }

  // Wikidata
  if (wd) {
    const wdFacts = [];
    if (wd.employees)           wdFacts.push(`- Employees: ${Number(wd.employees).toLocaleString()}`);
    if (wd.headquarters)        wdFacts.push(`- HQ: ${wd.headquarters}`);
    if (wd.instance_of?.length) wdFacts.push(`- Instance of: ${wd.instance_of.join(', ')}`);
    if (wd.aliases?.length)     wdFacts.push(`- Aliases: ${wd.aliases.join(', ')}`);
    if (wdFacts.length) md += `## Wikidata\n${wdFacts.join('\n')}\n\n`;
  }

  // Validation flags
  const openFlags = (entity.validation || []).filter(v => v.status !== 'confirmed');
  if (openFlags.length) {
    md += `## Data Flags\n`;
    md += openFlags.map(v => `- [${v.status}] ${v.description || ''}`).join('\n') + '\n\n';
  }

  // External links
  const links = [];
  if (cb?.profile_url)    links.push(`Crunchbase: ${cb.profile_url}`);
  if (cb?.website)        links.push(`Website: ${cb.website}`);
  if (wd?.wikipedia_url)  links.push(`Wikipedia: ${wd.wikipedia_url}`);
  if (entity.wikidata_id) links.push(`Wikidata: https://www.wikidata.org/wiki/${entity.wikidata_id}`);
  if (links.length) md += `## Links\n${links.join('\n')}\n\n`;

  md += `---\n_Source: info.nodes defence supply chain database — ${new Date().toISOString().slice(0, 10)}_\n`;
  md += `_Suggested prompt: Tell me about ${entity.name} in the context of the European defence supply chain. What do you know about their investors, portfolio, and sector positioning?_\n`;

  return md;
}

async function handleExport() {
  const btn = document.getElementById('cs-export-btn');
  const md  = buildCompanySearchSnapshot();
  try {
    await navigator.clipboard.writeText(md);
  } catch {
    const ta = document.createElement('textarea');
    ta.value = md; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
  const orig = btn.textContent;
  btn.textContent = 'Copied!';
  setTimeout(() => { btn.textContent = orig; }, 2000);
}

// ── Public API ─────────────────────────────────────────────────────────────
export default function initCompanySearch() {
  searchEl = document.getElementById('cs-search');
  acEl     = document.getElementById('cs-ac');

  searchEl.addEventListener('input',  () => { acKbd = -1; renderAc(searchEl.value); });
  searchEl.addEventListener('keydown', e => {
    if (!acEl.classList.contains('open')) return;
    if      (e.key === 'ArrowDown') { e.preventDefault(); moveAcKbd(+1); }
    else if (e.key === 'ArrowUp')   { e.preventDefault(); moveAcKbd(-1); }
    else if (e.key === 'Enter') {
      e.preventDefault();
      const target = acKbd >= 0 ? acFlatList[acKbd] : acFlatList[0];
      if (target) selectEntity(target);
    }
    else if (e.key === 'Escape') closeAc();
  });
  searchEl.addEventListener('blur', () => setTimeout(closeAc, 160));
  document.getElementById('cs-back').addEventListener('click', clearSelection);
  document.getElementById('cs-export-btn').addEventListener('click', handleExport);
  document.getElementById('cs-rel-body').addEventListener('click', e => {
    const link = e.target.closest('.cs-elist-link');
    if (!link) return;
    const entity = AppState.derived.entityMap[link.dataset.entityId];
    if (entity) selectEntity(entity);
  });
}

export function restoreCompanySearchUrl(p) {
  if (p.entity) {
    const entity = AppState.derived.entityMap[p.entity];
    if (entity) selectEntity(entity);
  }
}
