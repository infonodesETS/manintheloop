'use strict';
import * as Router from './router.js';

// ── Helpers ───────────────────────────────────────────────────────────────────
const esc = s => String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

function initials(name) {
  return name.split(/\s+/).map(w => w[0]||'').join('').slice(0,2).toUpperCase() || '?';
}
function highlight(text, q) {
  if (!q) return esc(text);
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`,'gi');
  return esc(text).replace(re,'<mark>$1</mark>');
}
function fmtEur(val) {
  if (!val) return null;
  const n = parseFloat(val);
  if (isNaN(n) || n === 0) return null;
  if (n >= 1e6) return `€${(n/1e6).toFixed(1)}M`;
  if (n >= 1e3) return `€${(n/1e3).toFixed(0)}K`;
  return `€${n.toFixed(0)}`;
}
function fmtFunding(n) {
  if (!n) return null;
  if (n >= 1e9) return `$${(n/1e9).toFixed(1)}B`;
  if (n >= 1e6) return `$${(n/1e6).toFixed(0)}M`;
  return `$${n.toLocaleString()}`;
}
function row(lbl, val) {
  return `<div class="cs-row"><span class="cs-row-lbl">${lbl}</span><span class="cs-row-val">${val}</span></div>`;
}
const NA = '<span class="cs-na-inline">Not available in the source</span>';
function na(v) {
  if (v == null || v === '' || (Array.isArray(v) && v.length === 0)) return NA;
  return null;
}
function fmtNative(obj) {
  if (!obj || typeof obj !== 'object') return NA;
  const { amount, currency } = obj;
  if (amount == null) return NA;
  const n = Number(amount);
  const fmt = isNaN(n) ? String(amount) : n.toLocaleString();
  return esc(`${currency ? currency + ' ' : ''}${fmt}`);
}

// ── Source/type badges ────────────────────────────────────────────────────────
const SECTOR_CLASS = { Defence:'defence', Mining:'mining', Tech:'tech', Startup:'startup' };
const TYPE_CLASS   = { fund:'fund', government_agency:'gov', bank:'bank', institution:'institution', company:'company' };

function sectorBadge(s) {
  const cls = SECTOR_CLASS[s] || 'default';
  return `<span class="badge badge-${cls}">${esc(s)}</span>`;
}
function typeBadge(t) {
  const cls = TYPE_CLASS[t] || 'default';
  const label = t?.replace(/_/g,' ') || t;
  return `<span class="badge badge-${cls}">${esc(label)}</span>`;
}
function srcBadge(kind) {
  const map = {
    merged:   ['DB + EDF','merged'],
    'db-only':['DB only','db-only'],
    'edf-only':['EDF only','edf-only'],
  };
  const [label, cls] = map[kind] || ['?',''];
  return `<span class="src-badge ${cls}">${label}</span>`;
}
function matchBadge(method) {
  if (!method) return '';
  const labels = { exact_norm:'exact', subset_tokens:'subsidiary', prefix_brand:'brand', manual:'manual', auto_name:'auto' };
  return `<span class="cs-ac-match">[${labels[method] || method}]</span>`;
}

// ── Data loading ──────────────────────────────────────────────────────────────
let DB       = null;
let ORGS     = null;
let EDF      = null;
let GLOSSARY = null;

async function loadData() {
  const [dbRes, orgsRes, glossRes] = await Promise.all([
    fetch('data/database.json'),
    fetch('data/edf_orgs.json'),
    fetch('data/glossary.json'),
  ]);
  DB       = await dbRes.json();
  ORGS     = await orgsRes.json();
  GLOSSARY = await glossRes.json();
}

async function loadEdf() {
  if (EDF) return EDF;
  const res = await fetch('rawdata/edf_calls.json');
  EDF = await res.json();
  return EDF;
}

// ── Source flags ─────────────────────────────────────────────────────────────
function sourceFlagsHtml(item, inline = false) {
  const e = item.dbEntity;
  const sf = GLOSSARY?.source_flags || {};
  const tip = key => sf[key] ? ` title="${esc(sf[key])}"` : '';
  const flags = [];
  if (e?.sources?.crunchbase)  flags.push(`<span class="src-flag src-flag-cb"${tip('CB')}>CB</span>`);
  if (item.edfOrg)             flags.push(`<span class="src-flag src-flag-edf"${tip('EDF')}>EDF</span>`);
  const isCount = (e?.sources?.ishares || []).length;
  if (isCount > 0)             flags.push(`<span class="src-flag src-flag-is"${tip('iShares')}>iShares${isCount > 1 ? ` ×${isCount}` : ''}</span>`);
  if (e?.sources?.wikidata)    flags.push(`<span class="src-flag src-flag-wd"${tip('WD')}>WD</span>`);
  if (e?.sources?.infonodes)   flags.push(`<span class="src-flag src-flag-inf"${tip('INF')}>INF</span>`);
  if (!flags.length) return '';
  return `<span class="src-flags${inline ? ' inline' : ''}">${flags.join('')}</span>`;
}

// ── Build unified registry ────────────────────────────────────────────────────
let REGISTRY = [];
let ENTITY_MAP = {};

function buildRegistry() {
  for (const e of DB.entities) {
    ENTITY_MAP[e.id] = e;
  }

  const edfByDbId = {};
  for (const org of Object.values(ORGS.orgs)) {
    if (org.db_id) {
      if (!edfByDbId[org.db_id]) edfByDbId[org.db_id] = [];
      edfByDbId[org.db_id].push(org);
    }
  }

  const picToDbEntity = {};
  for (const e of DB.entities) {
    const pic = e.sources?.edf?.pic;
    if (pic) picToDbEntity[pic] = e;
  }

  const seenDbIds = new Set();

  // 1. EDF orgs first
  for (const org of Object.values(ORGS.orgs)) {
    const dbEntity = (org.db_id && ENTITY_MAP[org.db_id]) || picToDbEntity[org.pic] || null;
    if (dbEntity) {
      seenDbIds.add(dbEntity.id);
      REGISTRY.push({
        id:       `EDF:${org.pic}`,
        name:     dbEntity.name,
        edfName:  org.organization_name,
        kind:     'merged',
        pic:      org.pic,
        dbEntity,
        edfOrg:   org,
        country:  org.country || dbEntity.sources?.infonodes?.country || dbEntity.sources?.wikidata?.country || '',
        _key: [
          dbEntity.name, org.organization_name,
          org.country,
          dbEntity.sources?.infonodes?.country,
          dbEntity.sources?.crunchbase?.headquarters,
          ...(dbEntity.sources?.crunchbase?.industries || []),
          ...(dbEntity.tags || []),
        ].filter(Boolean).join(' ').toLowerCase(),
      });
      continue;
    }
    REGISTRY.push({
      id:      `EDF:${org.pic}`,
      name:    org.organization_name,
      kind:    'edf-only',
      pic:     org.pic,
      dbEntity: null,
      edfOrg:  org,
      country: org.country || '',
      _key: [org.organization_name, org.country, org.activity_type].filter(Boolean).join(' ').toLowerCase(),
    });
  }

  // 2. DB-only entities — exclude IV- investors
  for (const e of DB.entities) {
    if (seenDbIds.has(e.id)) continue;
    if (e.id.startsWith('IV-')) continue;
    REGISTRY.push({
      id:       e.id,
      name:     e.name,
      kind:     'db-only',
      pic:      null,
      dbEntity: e,
      edfOrg:   null,
      country:  e.sources?.infonodes?.country || e.sources?.wikidata?.country || '',
      _key: [
        e.name,
        e.sources?.crunchbase?.headquarters,
        e.sources?.infonodes?.country,
        e.sources?.wikidata?.country,
        ...(e.sources?.crunchbase?.industries || []),
        ...(e.tags || []),
      ].filter(Boolean).join(' ').toLowerCase(),
    });
  }

  // 3. Investor entities (IV-NNNN)
  for (const e of DB.entities) {
    if (!e.id.startsWith('IV-')) continue;
    const country = e.sources?.wikidata?.country || '';
    REGISTRY.push({
      id:       e.id,
      name:     e.name,
      kind:     'investor',
      pic:      null,
      dbEntity: e,
      edfOrg:   null,
      country,
      _key: [e.name, e.type, country, ...(e.tags || [])].filter(Boolean).join(' ').toLowerCase(),
    });
  }

  // Build relationship map
  REL_MAP = {};
  for (const r of (DB.relationships || [])) {
    const push = (id, role, other) => {
      if (!REL_MAP[id]) REL_MAP[id] = [];
      REL_MAP[id].push({ rel: r, role, other: ENTITY_MAP[other] });
    };
    push(r.source, 'investor', r.target);
    push(r.target, 'target',   r.source);
  }

  // Build PIC lookup map
  PIC_MAP = {};
  for (const item of REGISTRY) {
    if (item.pic) PIC_MAP[String(item.pic)] = item;
  }
}

let REL_MAP = {};
let PIC_MAP = {};

// ── Search & autocomplete ─────────────────────────────────────────────────────
let activeFilter = 'all';
let searchEl, acEl;
let acList = [], acKbd = -1;

function filteredRegistry() {
  if (activeFilter === 'all')    return REGISTRY;
  if (activeFilter === 'merged') return REGISTRY.filter(r => r.kind === 'merged');
  if (activeFilter === 'db')     return REGISTRY.filter(r => r.kind === 'db-only' || r.kind === 'investor');
  if (activeFilter === 'edf')    return REGISTRY.filter(r => r.kind === 'edf-only');
  return REGISTRY;
}

function closeAc() {
  acEl.classList.remove('open');
  acEl.innerHTML = '';
  acKbd = -1;
  acList = [];
}

function renderAc(raw) {
  const q = raw.trim().toLowerCase();
  if (!q) { renderSuggestions(); return; }

  const pool = filteredRegistry();
  const scored = pool.map(item => {
    const n = item.name.toLowerCase();
    const c = (item.country || '').toLowerCase();
    let s = 0;
    if (n === q)               s = 200;
    else if (n.startsWith(q))  s = 100;
    else if (n.includes(q))    s = 60;
    else if (c === q)          s = 40;
    else if (c.startsWith(q))  s = 30;
    else if (c.includes(q))    s = 25;
    else if (item._key.includes(q)) s = 20;
    const dbId = (item.dbEntity?.id || '').toLowerCase();
    if (dbId) {
      if (dbId === q)              s = Math.max(s, 200);
      else if (dbId.startsWith(q)) s = Math.max(s, 150);
      else if (dbId.includes(q))   s = Math.max(s, 50);
    }
    return { item, s };
  }).filter(x => x.s > 0).sort((a,b) => b.s - a.s || a.item.name.localeCompare(b.item.name));

  if (!scored.length) {
    acEl.innerHTML = `<div class="cs-ac-empty">No results for "<strong>${esc(raw)}</strong>"</div>`;
    acEl.classList.add('open');
    acList = [];
    return;
  }

  const exactCountryMatches = scored.filter(x => (x.item.country || '').toLowerCase() === q).length;
  const countryMode = exactCountryMatches >= 3;
  const groupLimit  = countryMode ? Infinity : null;

  const merged    = scored.filter(x => x.item.kind === 'merged');
  const dbOnly    = scored.filter(x => x.item.kind === 'db-only');
  const edfOnly   = scored.filter(x => x.item.kind === 'edf-only');
  const investors = scored.filter(x => x.item.kind === 'investor');
  acList = [];
  let html = '';

  function renderGroup(label, items, limit) {
    if (!items.length) return;
    const slice = limit === Infinity ? items : items.slice(0, limit);
    for (const { item } of slice) {
      const e   = item.dbEntity;
      let badge = '';
      if (item.kind === 'investor') {
        badge = `<span class="badge badge-investor">${esc(e?.type || 'investor')}</span>`;
      } else if (e?.sector) {
        badge = sectorBadge(e.sector);
      } else if (e?.type) {
        badge = typeBadge(e.type);
      }
      const portSize = item.kind === 'investor'
        ? (REL_MAP[item.id] || []).filter(r => r.role === 'investor').length
        : 0;
      html += `<div class="cs-ac-item" role="option" data-idx="${acList.length}">
        <span class="cs-ac-name">${highlight(item.name, raw)}</span>
        ${item.country ? `<span class="cs-ac-country">${esc(item.country)}</span>` : ''}
        ${item.kind === 'investor' && portSize ? `<span class="cs-ac-country">${portSize} co.</span>` : ''}
        ${item.kind !== 'investor' ? sourceFlagsHtml(item, true) : ''}
        ${badge}
      </div>`;
      acList.push(item);
    }
  }

  renderGroup('DB + EDF', merged,    groupLimit ?? 8);
  renderGroup('DB only',  dbOnly,    groupLimit ?? 8);
  renderGroup('EDF only', edfOnly,   groupLimit ?? 12);
  renderGroup('Investors', investors, groupLimit ?? 6);

  acEl.innerHTML = html;
  acEl.classList.add('open');
  acEl.querySelectorAll('.cs-ac-item').forEach(el => {
    el.addEventListener('mousedown', ev => {
      ev.preventDefault();
      const item = acList[Number(el.dataset.idx)];
      if (item) selectItem(item);
    });
  });
}

function renderSuggestions() {
  const pool = filteredRegistry().filter(r => r.kind !== 'investor');
  const shuffled = [...pool].sort(() => Math.random() - 0.5).slice(0, 24);
  acList = [];
  const groups = { merged: [], 'db-only': [], 'edf-only': [] };
  for (const item of shuffled) groups[item.kind]?.push(item);

  let html = '';
  function rg(label, items) {
    if (!items.length) return;
    for (const item of items.slice(0,8)) {
      const e = item.dbEntity;
      const org = item.edfOrg;
      const country = e?.sources?.infonodes?.country || org?.country || '';
      let badge = '';
      if (e?.sector) badge = sectorBadge(e.sector);
      else if (e?.type) badge = typeBadge(e.type);
      html += `<div class="cs-ac-item" role="option" data-idx="${acList.length}">
        <span class="cs-ac-name">${esc(item.name)}</span>
        ${country ? `<span class="cs-ac-country">${esc(country)}</span>` : ''}
        ${sourceFlagsHtml(item, true)}
        ${badge}
      </div>`;
      acList.push(item);
    }
  }
  rg('DB + EDF', groups.merged);
  rg('DB only', groups['db-only']);
  rg('EDF only', groups['edf-only']);

  acEl.innerHTML = html;
  acEl.classList.add('open');
  acEl.querySelectorAll('.cs-ac-item').forEach(el => {
    el.addEventListener('mousedown', ev => {
      ev.preventDefault();
      const item = acList[Number(el.dataset.idx)];
      if (item) selectItem(item);
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
    if (acList[acKbd]) searchEl.value = acList[acKbd].name;
  }
}

// ── Select / clear ────────────────────────────────────────────────────────────
let currentItem = null;

// ── Compare state ─────────────────────────────────────────────────────────────
let selectedB  = null;
let acListB    = [];
let acKbdB     = -1;
let searchElB  = null;
let acElB      = null;

function selectItem(item, replaceHistory = false) {
  currentItem = item;
  closeAc();
  searchEl.value = item.name;
  document.getElementById('cs-clear').style.display = '';
  document.getElementById('cs-hero').classList.add('compact');
  document.getElementById('cs-showing').textContent = item.name;
  document.getElementById('cs-compare').classList.remove('visible');
  if (selectedB) document.getElementById('cs-cmp-btn').disabled = false;
  if (replaceHistory) Router.replace(item); else Router.push(item);
  renderProfile(item);
}

function clearSelection() {
  currentItem = null;
  searchEl.value = '';
  document.getElementById('cs-clear').style.display = 'none';
  document.getElementById('cs-hero').classList.remove('compact');
  document.getElementById('cs-showing').textContent = '';
  document.getElementById('cs-profile').classList.remove('visible');
  document.getElementById('cs-compare').classList.remove('visible');
  Router.clear();
  searchEl.focus();
}

// ── Compare B search ──────────────────────────────────────────────────────────

function closeAcB() {
  if (!acElB) return;
  acElB.classList.remove('open');
  acElB.innerHTML = '';
  acKbdB = -1;
  acListB = [];
}

function renderAcB(raw) {
  if (!acElB) return;
  const q = raw.trim().toLowerCase();
  if (!q) { closeAcB(); return; }

  const scored = REGISTRY.map(item => {
    const n = item.name.toLowerCase();
    let s = 0;
    if (n === q)               s = 200;
    else if (n.startsWith(q))  s = 100;
    else if (n.includes(q))    s = 60;
    else if (item._key.includes(q)) s = 20;
    const dbId = (item.dbEntity?.id || '').toLowerCase();
    if (dbId) {
      if (dbId === q)              s = Math.max(s, 200);
      else if (dbId.startsWith(q)) s = Math.max(s, 150);
      else if (dbId.includes(q))   s = Math.max(s, 50);
    }
    return { item, s };
  }).filter(x => x.s > 0).sort((a,b) => b.s - a.s || a.item.name.localeCompare(b.item.name));

  if (!scored.length) {
    acElB.innerHTML = `<div class="cs-ac-empty">No results for "<strong>${esc(raw)}</strong>"</div>`;
    acElB.classList.add('open');
    acListB = [];
    return;
  }

  acListB = [];
  let html = '';
  for (const { item } of scored.slice(0, 20)) {
    const e   = item.dbEntity;
    let badge = '';
    if (item.kind === 'investor') badge = `<span class="badge badge-investor">${esc(e?.type || 'fund')}</span>`;
    else if (e?.sector) badge = sectorBadge(e.sector);
    else if (e?.type)   badge = typeBadge(e.type);
    html += `<div class="cs-ac-item" role="option" data-idx="${acListB.length}">
      <span class="cs-ac-name">${highlight(item.name, raw)}</span>
      ${item.country ? `<span class="cs-ac-country">${esc(item.country)}</span>` : ''}
      ${item.kind !== 'investor' ? sourceFlagsHtml(item, true) : ''}
      ${badge}
    </div>`;
    acListB.push(item);
  }
  acElB.innerHTML = html;
  acElB.classList.add('open');
  acElB.querySelectorAll('.cs-ac-item').forEach(el => {
    el.addEventListener('mousedown', ev => {
      ev.preventDefault();
      const item = acListB[Number(el.dataset.idx)];
      if (item) selectItemB(item);
    });
  });
}

function moveAcKbdB(delta) {
  if (!acElB) return;
  const items = acElB.querySelectorAll('.cs-ac-item');
  if (!items.length) return;
  items[acKbdB]?.classList.remove('kbd');
  acKbdB = Math.max(-1, Math.min(items.length - 1, acKbdB + delta));
  if (acKbdB >= 0) {
    items[acKbdB].classList.add('kbd');
    items[acKbdB].scrollIntoView({ block: 'nearest' });
    if (acListB[acKbdB]) searchElB.value = acListB[acKbdB].name;
  }
}

function selectItemB(item) {
  selectedB = item;
  closeAcB();
  searchElB.value = item.name;
  document.getElementById('cs-clear-b').style.display = '';
  const btn = document.getElementById('cs-cmp-btn');
  if (currentItem) btn.disabled = false;
}

function clearSelectionB() {
  selectedB = null;
  if (searchElB) searchElB.value = '';
  document.getElementById('cs-clear-b').style.display = 'none';
  document.getElementById('cs-cmp-btn').disabled = true;
  closeAcB();
}

// ── Build profile column HTML ─────────────────────────────────────────────────

function buildProfileColHtml(item, colId) {
  const e   = item.dbEntity;
  const org = item.edfOrg;
  const cb  = e?.sources?.crunchbase;
  const wd  = e?.sources?.wikidata;
  const inf = e?.sources?.infonodes || {};

  let badges = '';
  if (item.kind === 'investor') {
    badges += typeBadge(e?.type || 'fund');
    if (e?.id) badges += `<span class="cs-hdr-id">${esc(e.id)}</span>`;
  } else {
    if (e?.sector) badges += sectorBadge(e.sector);
    if (e?.type)   badges += typeBadge(e.type);
    if (item.kind !== 'db-only' && org?.pic)
      badges += `<span class="cs-hdr-id" title="PIC">PIC ${esc(org.pic)}</span>`;
    if (e?.id) badges += `<span class="cs-hdr-id">${esc(e.id)}</span>`;
  }

  let euHtml = '';
  if (item.kind !== 'investor') {
    const hasEdf = item.kind === 'merged' || item.kind === 'edf-only';
    euHtml = hasEdf
      ? `<img src="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg" class="eu-flag"><span class="eu-status-funded">Funded by European Commission</span>`
      : `<img src="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg" class="eu-flag eu-flag--inactive"><span class="eu-status-unfunded">Not funded by European Commission</span>`;
  }

  const srcFlagsHtml = item.kind !== 'investor' ? sourceFlagsHtml(item) : '';
  const desc = cb?.description || wd?.description || '';

  let links = '';
  if (item.kind === 'investor') {
    if (wd?.wikipedia_url)    links += `<a class="cs-ext-link cs-wd" href="${esc(wd.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`;
    if (e?.wikidata_id)       links += `<a class="cs-ext-link cs-wd" href="https://www.wikidata.org/wiki/${esc(e.wikidata_id)}" target="_blank">${esc(e.wikidata_id)} ↗</a>`;
    if (wd?.official_website) links += `<a class="cs-ext-link" href="${esc(wd.official_website)}" target="_blank">${esc(wd.official_website.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`;
  } else {
    if (cb?.profile_url) links += `<a class="cs-ext-link cs-cb" href="${esc(cb.profile_url)}" target="_blank">Crunchbase ↗</a>`;
    if (cb?.website)     links += `<a class="cs-ext-link" href="${esc(cb.website)}" target="_blank">${esc(cb.website.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`;
    if (wd?.wikipedia_url) links += `<a class="cs-ext-link cs-wd" href="${esc(wd.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`;
    if (e?.wikidata_id)  links += `<a class="cs-ext-link cs-wd" href="https://www.wikidata.org/wiki/${esc(e.wikidata_id)}" target="_blank">${esc(e.wikidata_id)} ↗</a>`;
    if (org?.web_link) {
      const url = org.web_link.startsWith('http') ? org.web_link : `https://${org.web_link}`;
      links += `<a class="cs-ext-link" href="${esc(url)}" target="_blank">${esc(org.web_link.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`;
    }
  }

  let statsHtml = '';
  if (item.kind === 'investor') {
    const portfolio = (REL_MAP[e?.id] || []).filter(r => r.role === 'investor');
    const leads = portfolio.filter(r => r.rel.details?.lead);
    const stats = [
      { v: portfolio.length, l: 'Portfolio' },
      { v: leads.length,     l: 'Lead rounds' },
    ];
    if (wd?.inception) stats.push({ v: String(wd.inception).slice(0,4), l: 'Founded' });
    if (wd?.employees) stats.push({ v: Number(wd.employees).toLocaleString(), l: 'Employees' });
    if (wd?.country)   stats.push({ v: wd.country, l: 'Country' });
    statsHtml = stats.map(s =>
      `<div class="cs-stat"><div class="cs-stat-val">${esc(String(s.v))}</div><div class="cs-stat-lbl">${s.l}</div></div>`
    ).join('');
  } else {
    const stats = [];
    if (cb?.total_funding_usd) stats.push({ v: fmtFunding(cb.total_funding_usd), l: 'Total Funding', cls: '' });
    if (wd?.employees)         stats.push({ v: Number(wd.employees).toLocaleString(), l: 'Employees', cls: '' });
    if (wd?.inception)         stats.push({ v: String(wd.inception).slice(0,4), l: 'Founded', cls: '' });
    if (org) {
      const eu = fmtEur(org.total_eu_contribution);
      if (eu) stats.push({ v: eu, l: 'EU Contribution', cls: 'edf-stat' });
      if (org.project_count > 0) stats.push({ v: org.project_count, l: 'EDF Projects', cls: 'edf-stat' });
    }
    statsHtml = stats.map(s =>
      `<div class="cs-stat${s.cls ? ' '+s.cls : ''}"><div class="cs-stat-val">${s.v ?? '—'}</div><div class="cs-stat-lbl">${s.l}</div></div>`
    ).join('');
  }

  const cards = [];
  if (item.kind === 'investor') {
    const portfolio = (REL_MAP[e?.id] || []).filter(r => r.role === 'investor');
    if (portfolio.length) {
      const sorted = [...portfolio].sort((a, b) => {
        const aL = a.rel.details?.lead ? 1 : 0;
        const bL = b.rel.details?.lead ? 1 : 0;
        if (bL !== aL) return bL - aL;
        return (a.other?.name || '').localeCompare(b.other?.name || '');
      });
      let h = `<ul class="cs-elist">`;
      for (const { rel, other } of sorted) {
        if (!other) continue;
        const cbi     = other.sources?.crunchbase;
        const isLead  = rel.details?.lead;
        const funding = cbi?.total_funding_usd ? fmtFunding(cbi.total_funding_usd) : null;
        const stage   = cbi?.last_funding_type || cbi?.funding_status || null;
        const country = other.sources?.infonodes?.country || other.sources?.wikidata?.country || cbi?.headquarters?.split(',').pop()?.trim() || '';
        const inds    = (cbi?.industries || []).slice(0,3).join(' · ');
        h += `<li class="cs-portfolio-item${isLead ? ' cs-portfolio-lead' : ''}">
          <div class="cs-elist-item-main">
            <button class="cs-portfolio-btn" data-id="${esc(other.id)}">${esc(other.name)}</button>
            <div class="cs-elist-meta">
              ${esc(other.id)}
              ${isLead ? `<span class="cs-lead-badge">lead</span>` : ''}
              ${stage   ? `· ${esc(stage)}` : ''}
              ${funding ? `· <strong>${esc(funding)}</strong>` : ''}
            </div>
            ${inds ? `<div class="cs-portfolio-inds">${esc(inds)}</div>` : ''}
          </div>
          ${country ? `<span class="cs-elist-country">${esc(country)}</span>` : ''}
        </li>`;
      }
      h += `</ul>`;
      cards.push(makeCard('portfolio', 'Crunchbase — Portfolio', h, portfolio.length));
    }
    if (wd) cards.push(makeCard('wd', 'Wikidata', wdCardBody(wd)));
  } else {
    if (e) cards.push(makeCard('inf', 'Infonodes', infCardBody(inf, e)));
    const isArr = e?.sources?.ishares || [];
    if (isArr.length) cards.push(makeCard('is', 'iShares', isCardBody(isArr), `${isArr.length} ETF${isArr.length !== 1 ? 's' : ''}`));
    if (wd) cards.push(makeCard('wd', 'Wikidata', wdCardBody(wd)));
    if (cb) cards.push(makeCard('cb', 'Crunchbase', cbCardBody(cb)));
    if (org) {
      const edfHtml = edfCardBody(item).replace(/<button[^>]*id="edf-load-btn"[^>]*>[\s\S]*?<\/button>/, `<div class="cs-na">Open full profile to load projects.</div>`);
      cards.push(makeCard('edf', 'European Defence Fund', edfHtml, `${org.project_count || 0} project${(org.project_count||0)!==1?'s':''}`, `card-edf-${colId}`));
    }
  }

  const hist = e?.history;
  if (hist?.length) cards.push(makeCard('hist', 'Change History', histCardBody(hist), hist.length));
  const val = e?.validation;
  if (val?.length) cards.push(makeCard('val', 'Validation', valCardBody(val), val.length));

  return `
    <div class="cs-cmp-col-title">Entity ${colId.toUpperCase()}</div>
    <div class="cs-hdr-card">
      <div class="cs-logo">${esc(initials(item.name))}</div>
      <div class="cs-hdr-main">
        <div class="cs-hdr-name">${esc(item.name)}</div>
        <div class="cs-hdr-badges">${badges}</div>
        ${srcFlagsHtml ? `<div>${srcFlagsHtml}</div>` : ''}
        ${euHtml ? `<div>${euHtml}</div>` : ''}
        ${desc ? `<div class="cs-hdr-desc">${esc(desc)}</div>` : ''}
        ${links ? `<div class="cs-hdr-actions"><div class="cs-ext-links">${links}</div></div>` : ''}
      </div>
    </div>
    ${statsHtml ? `<div class="cs-stats">${statsHtml}</div>` : ''}
    <div class="cs-cmp-cards">${cards.join('')}</div>`;
}

// ── Open / close compare ──────────────────────────────────────────────────────

function openCompare() {
  if (!currentItem || !selectedB) return;

  document.getElementById('cs-profile').classList.remove('visible');

  const cmpEl = document.getElementById('cs-compare');
  cmpEl.innerHTML = `<div class="cs-cmp-grid">
    <div class="cs-cmp-col" id="cs-cmp-col-a">${buildProfileColHtml(currentItem, 'a')}</div>
    <div class="cs-cmp-col" id="cs-cmp-col-b">${buildProfileColHtml(selectedB, 'b')}</div>
  </div>`;
  cmpEl.classList.add('visible');
  Router.pushCompare(currentItem, selectedB);

  cmpEl.querySelectorAll('.cs-card-hdr').forEach(hdr => {
    hdr.addEventListener('click', () => hdr.closest('.cs-card').classList.toggle('collapsed'));
  });

  cmpEl.querySelectorAll('.cs-portfolio-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetItem = REGISTRY.find(r => r.dbEntity?.id === btn.dataset.id);
      if (targetItem) selectItem(targetItem);
    });
  });

  wireInvestorPills(cmpEl);

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Render profile ────────────────────────────────────────────────────────────
function renderProfile(item) {
  if (item.kind === 'investor') { renderInvestorProfile(item); return; }

  const profile = document.getElementById('cs-profile');
  profile.classList.remove('visible');
  void profile.offsetWidth;
  profile.classList.add('visible');

  const e   = item.dbEntity;
  const org = item.edfOrg;
  const cb  = e?.sources?.crunchbase;
  const wd  = e?.sources?.wikidata;
  const inf = e?.sources?.infonodes;

  document.getElementById('cs-logo').textContent = initials(item.name);
  document.getElementById('cs-name').textContent = item.name;

  let badges = '';
  if (e?.sector) badges += sectorBadge(e.sector);
  if (e?.type)   badges += typeBadge(e.type);
  if (item.kind !== 'db-only' && org?.pic)
    badges += `<span class="cs-hdr-id" title="EU Participant ID (PIC)">PIC ${esc(org.pic)}</span>`;
  if (e?.id)
    badges += `<span class="cs-hdr-id" title="Database ID">${esc(e.id)}</span>`;
  if (item.kind === 'merged' && org?.match_method)
    badges += `<span class="cs-hdr-id cs-hdr-id--match" title="Match method">${esc(org.match_method)} / ${esc(org.match_confidence)}</span>`;
  document.getElementById('cs-badges').innerHTML = badges;
  document.getElementById('cs-src-flags').innerHTML = sourceFlagsHtml(item);

  const hasEdf = item.kind === 'merged' || item.kind === 'edf-only';
  const euEl = document.getElementById('cs-eu-status');
  if (hasEdf) {
    euEl.innerHTML = `<img src="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg" aria-hidden="true" class="eu-flag"><span class="eu-status-funded">Funded by European Commission</span>`;
  } else {
    euEl.innerHTML = `<img src="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg" aria-hidden="true" class="eu-flag eu-flag--inactive"><span class="eu-status-unfunded">Not funded by European Commission</span>`;
  }

  const desc = cb?.description || wd?.description || '';
  const descEl = document.getElementById('cs-desc');
  descEl.textContent = desc;
  descEl.style.display = desc ? '' : 'none';

  let links = '';
  if (cb?.profile_url)
    links += `<a class="cs-ext-link cs-cb" href="${esc(cb.profile_url)}" target="_blank">Crunchbase ↗</a>`;
  if (cb?.website)
    links += `<a class="cs-ext-link" href="${esc(cb.website)}" target="_blank">${esc(cb.website.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`;
  if (wd?.wikipedia_url)
    links += `<a class="cs-ext-link cs-wd" href="${esc(wd.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`;
  if (e?.wikidata_id)
    links += `<a class="cs-ext-link cs-wd" href="https://www.wikidata.org/wiki/${esc(e.wikidata_id)}" target="_blank">${esc(e.wikidata_id)} ↗</a>`;
  if (org?.web_link) {
    const url = org.web_link.startsWith('http') ? org.web_link : `https://${org.web_link}`;
    links += `<a class="cs-ext-link" href="${esc(url)}" target="_blank">${esc(org.web_link.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`;
  }
  document.getElementById('cs-links').innerHTML = links;

  const stats = [];
  if (cb?.total_funding_usd)   stats.push({ v: fmtFunding(cb.total_funding_usd), l: 'Total Funding', cls: '' });
  if (wd?.employees)           stats.push({ v: Number(wd.employees).toLocaleString(),  l: 'Employees', cls: '' });
  if (wd?.inception)           stats.push({ v: String(wd.inception).slice(0,4),        l: 'Founded', cls: '' });
  if (org) {
    const eu = fmtEur(org.total_eu_contribution);
    if (eu) stats.push({ v: eu, l: 'EU Contribution', cls: 'edf-stat' });
    if (org.project_count > 0)     stats.push({ v: org.project_count,     l: 'EDF Projects',     cls: 'edf-stat', anchor: 'card-edf' });
    if (org.call_count > 0)        stats.push({ v: org.call_count,         l: 'EDF Calls',         cls: 'edf-stat' });
    if (org.coordinator_count > 0) stats.push({ v: org.coordinator_count,  l: 'Coordinated',       cls: 'edf-stat' });
  }
  document.getElementById('cs-stats').innerHTML = stats.map(s =>
    `<div class="cs-stat${s.cls ? ' '+s.cls : ''}${s.anchor ? ' cs-stat--link' : ''}" ${s.anchor ? `data-anchor="${s.anchor}"` : ''}>
      <div class="cs-stat-val">${s.v ?? '—'}</div>
      <div class="cs-stat-lbl">${s.l}</div>
    </div>`
  ).join('');
  document.getElementById('cs-stats').querySelectorAll('.cs-stat--link').forEach(el => {
    el.addEventListener('click', () => {
      document.getElementById(el.dataset.anchor)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  renderCards(item);
}

// ── Investor profile ──────────────────────────────────────────────────────────
function renderInvestorProfile(item) {
  const profile = document.getElementById('cs-profile');
  profile.classList.remove('visible');
  void profile.offsetWidth;
  profile.classList.add('visible');

  const e = item.dbEntity;
  const wd = e?.sources?.wikidata;

  document.getElementById('cs-logo').textContent = initials(item.name);
  document.getElementById('cs-name').textContent  = item.name;
  document.getElementById('cs-desc').textContent  = wd?.description || '';
  document.getElementById('cs-desc').style.display = wd?.description ? '' : 'none';
  document.getElementById('cs-eu-status').innerHTML = '';

  let badges = typeBadge(e?.type || 'fund');
  if (e?.id) badges += `<span class="cs-hdr-id">${esc(e.id)}</span>`;
  document.getElementById('cs-badges').innerHTML  = badges;
  document.getElementById('cs-src-flags').innerHTML = '';

  let links = '';
  if (wd?.wikipedia_url) links += `<a class="cs-ext-link cs-wd" href="${esc(wd.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`;
  if (e?.wikidata_id)    links += `<a class="cs-ext-link cs-wd" href="https://www.wikidata.org/wiki/${esc(e.wikidata_id)}" target="_blank">${esc(e.wikidata_id)} ↗</a>`;
  if (wd?.official_website) links += `<a class="cs-ext-link" href="${esc(wd.official_website)}" target="_blank">${esc(wd.official_website.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`;
  document.getElementById('cs-links').innerHTML = links;

  const portfolio = (REL_MAP[e?.id] || []).filter(r => r.role === 'investor');
  const leads     = portfolio.filter(r => r.rel.details?.lead);
  const stats = [
    { v: portfolio.length, l: 'Portfolio',   cls: '' },
    { v: leads.length,     l: 'Lead rounds', cls: '' },
  ];
  if (wd?.inception)  stats.push({ v: String(wd.inception).slice(0,4), l: 'Founded', cls: '' });
  if (wd?.employees)  stats.push({ v: Number(wd.employees).toLocaleString(), l: 'Employees', cls: '' });
  if (wd?.country)    stats.push({ v: wd.country, l: 'Country', cls: '' });
  document.getElementById('cs-stats').innerHTML = stats.map(s =>
    `<div class="cs-stat${s.cls ? ' '+s.cls : ''}">
      <div class="cs-stat-val">${esc(String(s.v))}</div>
      <div class="cs-stat-lbl">${s.l}</div>
    </div>`
  ).join('');

  const cards = [];

  if (portfolio.length) {
    let h = `<ul class="cs-elist">`;
    const sorted = [...portfolio].sort((a, b) => {
      const aLead = a.rel.details?.lead ? 1 : 0;
      const bLead = b.rel.details?.lead ? 1 : 0;
      if (bLead !== aLead) return bLead - aLead;
      return (a.other?.name || '').localeCompare(b.other?.name || '');
    });
    for (const { rel, other } of sorted) {
      if (!other) continue;
      const cb      = other.sources?.crunchbase;
      const isLead  = rel.details?.lead;
      const funding = cb?.total_funding_usd ? fmtFunding(cb.total_funding_usd) : null;
      const stage   = cb?.last_funding_type || cb?.funding_status || null;
      const country = other.sources?.infonodes?.country || other.sources?.wikidata?.country || cb?.headquarters?.split(',').pop()?.trim() || '';
      const inds    = (cb?.industries || []).slice(0,3).join(' · ');
      h += `<li class="cs-portfolio-item${isLead ? ' cs-portfolio-lead' : ''}">
        <div class="cs-elist-item-main">
          <button class="cs-portfolio-btn" data-id="${esc(other.id)}">${esc(other.name)}</button>
          <div class="cs-elist-meta">
            ${esc(other.id)}
            ${isLead ? `<span class="cs-lead-badge">lead</span>` : ''}
            ${stage  ? `· ${esc(stage)}` : ''}
            ${funding ? `· <strong>${esc(funding)}</strong>` : ''}
          </div>
          ${inds ? `<div class="cs-portfolio-inds">${esc(inds)}</div>` : ''}
        </div>
        ${country ? `<span class="cs-elist-country">${esc(country)}</span>` : ''}
      </li>`;
    }
    h += `</ul>`;
    cards.push(makeCard('portfolio', 'Crunchbase — Portfolio', h, portfolio.length));
  }

  if (wd) cards.push(makeCard('wd', 'Wikidata', wdCardBody(wd)));

  const hist = e?.history;
  if (hist?.length) cards.push(makeCard('hist', 'Change History', histCardBody(hist), hist.length));
  const val = e?.validation;
  if (val?.length)  cards.push(makeCard('val', 'Validation', valCardBody(val), val.length));

  const container = document.getElementById('cs-cards');
  container.innerHTML = cards.join('');

  container.querySelectorAll('.cs-card-hdr').forEach(hdr => {
    hdr.addEventListener('click', () => hdr.closest('.cs-card').classList.toggle('collapsed'));
  });

  container.querySelectorAll('.cs-portfolio-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetItem = REGISTRY.find(r => r.dbEntity?.id === btn.dataset.id);
      if (targetItem) selectItem(targetItem);
    });
  });
}

// ── Single-column cards ───────────────────────────────────────────────────────

function makeCard(cls, title, bodyHtml, count, id) {
  const countHtml = count != null ? `<span class="cs-card-count">${count}</span>` : '';
  const idAttr = id ? ` id="${id}"` : '';
  return `<div class="cs-card cs-card-${cls}"${idAttr}>
    <div class="cs-card-hdr">
      <div class="cs-card-title"><span>${title}</span>${countHtml}</div>
      <span class="cs-card-toggle">▾</span>
    </div>
    <div class="cs-card-body">${bodyHtml}</div>
  </div>`;
}

function infCardBody(inf, e) {
  let h = '';
  if (e?.id)          h += row('DB ID', `<code>${esc(e.id)}</code>`);
  if (e?.type)        h += row('Type', esc(e.type));
  h += row('Sector',      e?.sector      ? esc(e.sector)      : NA);
  h += row('Wikidata ID', e?.wikidata_id ? `<code>${esc(e.wikidata_id)}</code>` : NA);
  h += row('Roles', e?.roles?.length
    ? `<span class="cs-tag-list">${e.roles.map(r => `<span class="cs-tag">${esc(r)}</span>`).join('')}</span>`
    : NA);
  h += row('Tags', e?.tags?.length
    ? `<span class="cs-tag-list">${e.tags.map(t => `<span class="cs-tag">${esc(t)}</span>`).join('')}</span>`
    : NA);
  h += row('Country',   inf.country   ? esc(inf.country)   : NA);
  h += row('Focus',     inf.main_focus ? esc(inf.main_focus) : NA);
  h += row('Tax ID',    inf.tax_id    ? `<code>${esc(inf.tax_id)}</code>` : NA);
  h += row('Website',   inf.website
    ? `<a class="cs-ext-link" href="${esc(inf.website)}" target="_blank">${esc(inf.website.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`
    : NA);
  h += row('Wikipedia', inf.wikipedia_url
    ? `<a class="cs-ext-link cs-wd" href="${esc(inf.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`
    : NA);
  if (inf.extracted_at) h += `<div class="cs-src-ts">Extracted: ${esc(inf.extracted_at)}</div>`;
  return h || '<div class="cs-na">No Infonodes data.</div>';
}

function isCardBody(arr) {
  let h = `<table class="is-table"><thead><tr>
    <th>ETF</th><th>Ticker</th><th>Weight</th><th>Sector</th><th>Location</th><th>Exchange</th><th>Currency</th><th>GICS</th><th>Source file</th>
  </tr></thead><tbody>`;
  for (const s of arr) {
    h += `<tr>
      <td>${esc(s.etf_name || '—')}</td>
      <td>${esc(s.stock_ticker || '—')}</td>
      <td class="is-weight">${s.weight_pct != null ? s.weight_pct + '%' : '—'}</td>
      <td>${esc(s.stock_sector || '—')}</td>
      <td>${esc(s.location || '—')}</td>
      <td>${esc(s.exchange || '—')}</td>
      <td>${esc(s.currency || '—')}</td>
      <td>${esc(s.gics_code || '—')}</td>
      <td><code>${esc(s.source_file || '—')}</code></td>
    </tr>`;
  }
  h += `</tbody></table>`;
  if (arr[0]?.extracted_at) h += `<div class="cs-src-ts">Extracted: ${esc(arr[0].extracted_at)}</div>`;
  return h;
}

function wdCardBody(wd) {
  let h = '';
  if (wd.label)          h += row('Label', esc(wd.label));
  if (wd.description)    h += `<div class="cs-src-desc">${esc(wd.description)}</div>`;
  h += row('Also known as', wd.aliases?.length
    ? `<span class="cs-tag-list">${wd.aliases.map(a => `<span class="cs-tag">${esc(a)}</span>`).join('')}</span>`
    : NA);
  h += row('Instance of', wd.instance_of?.length
    ? (Array.isArray(wd.instance_of) ? wd.instance_of : [wd.instance_of]).map(v => esc(v)).join(', ')
    : NA);
  h += row('Country',   wd.country    ? esc(wd.country)  : NA);
  h += row('Founded',   wd.inception  ? esc(String(wd.inception).slice(0,4)) : NA);
  h += row('HQ',        wd.headquarters ? esc(wd.headquarters) : NA);
  h += row('Employees', wd.employees  ? Number(wd.employees).toLocaleString() : NA);
  h += row('ISIN',      wd.isin       ? `<code>${esc(wd.isin)}</code>` : NA);
  h += row('Website',   wd.official_website
    ? `<a class="cs-ext-link" href="${esc(wd.official_website)}" target="_blank">${esc(wd.official_website.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`
    : NA);
  h += row('Wikipedia', wd.wikipedia_url
    ? `<a class="cs-ext-link cs-wd" href="${esc(wd.wikipedia_url)}" target="_blank">Wikipedia ↗</a>`
    : NA);
  if (wd.retrieved_at) h += `<div class="cs-src-ts">Retrieved: ${esc(wd.retrieved_at)}</div>`;
  return h || '<div class="cs-na">No Wikidata properties.</div>';
}

function cbCardBody(cb) {
  let h = '';

  h += `<div class="cb-group">Identity &amp; Status</div>`;
  if (cb.description_full || cb.description)
    h += `<div class="cs-src-desc">${esc(cb.description_full || cb.description)}</div>`;
  h += row('Status',       cb.operating_status ? esc(cb.operating_status) : NA);
  h += row('Stage',        cb.stage            ? esc(cb.stage)            : NA);
  h += row('Company type', cb.company_type     ? esc(cb.company_type)     : NA);
  h += row('Founded',      cb.founded_date     ? esc(String(cb.founded_date).slice(0,10)) : NA);
  h += row('HQ',           cb.headquarters     ? esc(cb.headquarters)     : NA);
  h += row('Regions',      cb.headquarters_regions ? esc(cb.headquarters_regions) : NA);
  h += row('Revenue',      cb.revenue_range    ? esc(cb.revenue_range)    : NA);
  h += row('CB Rank',      cb.cb_rank          ? `#${cb.cb_rank}`         : NA);
  h += row('Domain',       cb.domain           ? `<code>${esc(cb.domain)}</code>` : NA);
  h += row('Website',      cb.website
    ? `<a class="cs-ext-link" href="${esc(cb.website)}" target="_blank">${esc(cb.website.replace(/^https?:\/\/(www\.)?/,'').replace(/\/.*$/,''))} ↗</a>`
    : NA);
  h += row('Profile',      cb.profile_url
    ? `<a class="cs-ext-link cs-cb" href="${esc(cb.profile_url)}" target="_blank">Crunchbase ↗</a>`
    : NA);
  h += row('Source file',  cb.source_file      ? `<code>${esc(cb.source_file)}</code>` : NA);

  h += `<div class="cb-group">Industry</div>`;
  h += row('Primary',      cb.primary_industry     ? esc(cb.primary_industry) : NA);
  h += row('Industry URL', cb.primary_industry_url
    ? `<a class="cs-ext-link cs-cb" href="${esc(cb.primary_industry_url)}" target="_blank">${esc(cb.primary_industry_url)}</a>`
    : NA);
  h += row('Groups',     cb.industry_groups?.length
    ? `<span class="cs-tag-list">${cb.industry_groups.map(g=>`<span class="cs-tag">${esc(g)}</span>`).join('')}</span>`
    : NA);
  h += row('Industries', cb.industries?.length
    ? `<span class="cs-tag-list">${cb.industries.map(i=>`<span class="cs-tag">${esc(i)}</span>`).join('')}</span>`
    : NA);

  h += `<div class="cb-group">Funding</div>`;
  h += row('Status',         cb.funding_status          ? esc(cb.funding_status) : NA);
  h += row('Total funding',  cb.total_funding_usd       ? fmtFunding(cb.total_funding_usd) : NA);
  h += row('Equity funding', cb.total_equity_funding_usd ? fmtFunding(cb.total_equity_funding_usd) : NA);
  h += row('Native amount',  fmtNative(cb.total_funding_native));
  h += row('Rounds',         cb.num_funding_rounds != null ? String(cb.num_funding_rounds) : NA);
  h += row('Last round',     cb.last_funding_date       ? esc(String(cb.last_funding_date).slice(0,10)) : NA);
  h += row('Last type',      cb.last_funding_type       ? esc(cb.last_funding_type) : NA);
  h += row('Last amount',    cb.last_funding_amount_usd ? fmtFunding(cb.last_funding_amount_usd) : NA);
  h += row('Investors',      cb.num_investors != null   ? String(cb.num_investors) : NA);
  h += row('Top investors',  cb.top_investors?.length
    ? `<span class="cs-tag-list">${cb.top_investors.map(i=>`<button class="cs-tag cs-tag-investor" data-investor-name="${esc(i)}">${esc(i)}</button>`).join('')}</span>`
    : NA);
  h += row('Inv. stage',     cb.investment_stage        ? esc(cb.investment_stage) : NA);
  h += row('Inv. type',      cb.investor_type           ? esc(cb.investor_type)    : NA);

  h += `<div class="cb-group">Team &amp; IP</div>`;
  h += row('Founders', cb.founders?.length
    ? `<span class="cs-tag-list">${cb.founders.map(f=>`<span class="cs-tag">${esc(f)}</span>`).join('')}</span>`
    : NA);
  h += row('Board', cb.board?.length
    ? `<span class="cs-tag-list">${cb.board.map(b=>`<span class="cs-tag">${esc(b)}</span>`).join('')}</span>`
    : NA);
  h += row('Patents', cb.patents_granted != null ? String(cb.patents_granted) : NA);

  h += `<div class="cb-group">Acquisition</div>`;
  h += row('Acquired by', cb.acquired_by
    ? (cb.acquired_by_url
        ? `<a class="cs-ext-link cs-cb" href="${esc(cb.acquired_by_url)}" target="_blank">${esc(cb.acquired_by)}</a>`
        : esc(cb.acquired_by))
    : NA);

  if (cb.extracted_at) h += `<div class="cs-src-ts">Extracted: ${esc(cb.extracted_at)}</div>`;
  return h || '<div class="cs-na">No Crunchbase data.</div>';
}

function edfCardBody(item) {
  const org = item.edfOrg;
  const edb = item.dbEntity?.sources?.edf || {};
  let h = `<div class="edf-identity-block">`;
  if (org.organization_name !== item.name) h += row('Legal name', esc(org.organization_name));
  h += row('PIC',          org.pic         ? `<code>${esc(String(org.pic))}</code>` : NA);
  const euUrl = edb.eu_url;
  h += row('EU portal',    euUrl
    ? `<a class="cs-ext-link" href="${esc(euUrl)}" target="_blank">EC org page ↗</a>`
    : NA);
  h += row('Country',      (org.country || org.city)
    ? esc(org.country || '') + (org.city ? ` — ${esc(org.city)}` : '')
    : NA);
  h += row('Country code', org.country_code  ? `<code>${esc(org.country_code)}</code>` : NA);
  h += row('Activity type',org.activity_type ? esc(org.activity_type) : NA);
  h += row('Org type',     org.type_code     ? esc(org.type_code)     : NA);
  const sme = edb.sme;
  h += row('SME',          sme != null ? (sme ? 'Yes' : 'No') : NA);
  const euFmt = fmtEur(org.total_eu_contribution);
  h += row('EU contribution', euFmt ? `<span class="edf-contrib">${euFmt}</span>` : NA);
  h += row('Calls',        org.call_count        != null ? String(org.call_count)        : NA);
  h += row('Coordinated',  org.coordinator_count != null ? String(org.coordinator_count) : NA);
  h += row('Match',        `${esc(org.match_method || '—')} / ${esc(org.match_confidence || '—')}`);
  const sf = edb.source_file;
  h += row('Source file',  sf ? `<code>${esc(sf)}</code>` : NA);
  const ext = edb.extracted_at;
  h += ext ? `<div class="cs-src-ts">Extracted: ${esc(ext)}</div>` : '';
  h += `</div>`;
  const projCount = org.project_count || 0;
  if (projCount > 0) {
    h += `<div id="edf-proj-list">
      <button class="edf-load-btn" id="edf-load-btn" data-pic="${esc(String(org.pic))}">
        Load ${projCount} project${projCount !== 1 ? 's' : ''} ↓
      </button>
    </div>`;
  } else {
    h += `<div class="cs-na">No funded projects in this dataset.</div>`;
  }
  return h;
}

function histCardBody(hist) {
  const entries = [...hist].reverse();
  let h = `<ol class="hist-list">`;
  for (const e of entries) {
    h += `<li class="hist-item">
      <div class="hist-meta">
        <span class="hist-date">${esc(e.date)}</span>
        ${e.field && e.field !== '*' ? `<span class="hist-field">${esc(e.field)}</span>` : ''}
        <span class="hist-source">${esc(e.source || '')}</span>
        ${e.author ? `<span class="hist-source" style="opacity:.6">${esc(e.author)}</span>` : ''}
      </div>
      <div class="hist-desc">${esc(e.description || '')}</div>
      ${(e.old != null || e.new != null) ? `<div class="hist-diff">${e.old != null ? `<span class="hist-old">${esc(String(e.old))}</span> → ` : ''}${e.new != null ? `<span class="hist-new">${esc(String(e.new))}</span>` : ''}</div>` : ''}
    </li>`;
  }
  return h + `</ol>`;
}

function valCardBody(val) {
  let h = '';
  const sorted = [...val].sort((a, b) => (b.datestamp || '').localeCompare(a.datestamp || ''));
  for (const v of sorted) {
    const cls = (v.status || '').replace(/[^a-z0-9_]/gi, '_');
    h += `<div class="val-item">
      <span class="val-status ${cls}">${esc(v.status || '—')}</span>
      <div class="val-desc">${esc(v.description || '')}</div>
      ${v.author || v.datestamp ? `<div class="hist-meta">${v.author ? `<span class="hist-source">${esc(v.author)}</span>` : ''}${v.datestamp ? `<span class="hist-date">${esc(v.datestamp)}</span>` : ''}</div>` : ''}
    </div>`;
  }
  return h || '<div class="cs-na">No validation entries.</div>';
}

function findInvestorByName(name) {
  const q = name.trim().toLowerCase();
  return REGISTRY.find(r => r.kind === 'investor' && r.name.toLowerCase() === q)
      || REGISTRY.find(r => r.kind === 'investor' && r.name.toLowerCase().includes(q));
}

function wireInvestorPills(container) {
  container.querySelectorAll('.cs-tag-investor').forEach(btn => {
    const item = findInvestorByName(btn.dataset.investorName);
    if (item) {
      btn.classList.add('cs-tag-investor--linked');
      btn.addEventListener('click', () => selectItem(item));
    }
  });
}

function renderCards(item) {
  const e   = item.dbEntity;
  const org = item.edfOrg;
  const cards = [];

  const inf = e?.sources?.infonodes || {};
  if (e) cards.push(makeCard('inf', 'Infonodes', infCardBody(inf, e)));

  const isArr = e?.sources?.ishares || [];
  if (isArr.length) cards.push(makeCard('is', 'iShares', isCardBody(isArr), `${isArr.length} ETF${isArr.length !== 1 ? 's' : ''}`));

  const wd = e?.sources?.wikidata;
  if (wd) cards.push(makeCard('wd', 'Wikidata', wdCardBody(wd)));

  const cb = e?.sources?.crunchbase;
  if (cb) cards.push(makeCard('cb', 'Crunchbase', cbCardBody(cb)));

  if (org) cards.push(makeCard('edf', 'European Defence Fund', edfCardBody(item), `${org.project_count || 0} project${(org.project_count || 0) !== 1 ? 's' : ''}`, 'card-edf'));

  const hist = e?.history;
  if (hist?.length) cards.push(makeCard('hist', 'Change History', histCardBody(hist), hist.length));

  const val = e?.validation;
  if (val?.length) cards.push(makeCard('val', 'Validation', valCardBody(val), val.length));

  const container = document.getElementById('cs-cards');
  container.innerHTML = cards.join('');

  container.querySelectorAll('.cs-card-hdr').forEach(hdr => {
    hdr.addEventListener('click', () => hdr.closest('.cs-card').classList.toggle('collapsed'));
  });

  container.querySelector('#edf-load-btn')?.addEventListener('click', async () => {
    const btn = container.querySelector('#edf-load-btn');
    btn.textContent = 'Loading…';
    btn.disabled = true;
    try {
      await loadEdf();
      renderEdfProjects(org.pic);
    } catch {
      document.getElementById('edf-proj-list').innerHTML =
        `<div class="cs-na">Failed to load project data.</div>`;
    }
  });

  wireInvestorPills(container);
}

function renderEdfProjects(pic) {
  const listEl = document.getElementById('edf-proj-list');
  if (!listEl || !EDF) return;

  const found = [];
  for (const [callId, call] of Object.entries(EDF.calls)) {
    for (const proj of (call.projects || [])) {
      const participation = (proj.participants || []).find(p => String(p.pic) === String(pic));
      if (participation) {
        found.push({ call, proj, participation });
      }
    }
  }

  if (!found.length) {
    listEl.innerHTML = `<div class="cs-na">No projects found for this PIC.</div>`;
    return;
  }

  let html = `<ul class="edf-projects">`;
  for (let i = 0; i < found.length; i++) {
    const { call, proj, participation } = found[i];
    const eu       = fmtEur(participation.eu_contribution);
    const role     = participation.role || '';
    const start    = (proj.start_date || '').slice(0,10);
    const end      = (proj.end_date   || '').slice(0,10);
    const totalEu  = fmtEur(proj.eu_contribution);
    const partCount = (proj.participants || []).length;
    html += `<li class="edf-proj-item">
      <div class="edf-proj-title">
        ${proj.acronym ? `<strong>${esc(proj.acronym)}</strong> — ` : ''}${esc(proj.title)}
      </div>
      ${proj.objective ? `<div class="edf-proj-desc">${esc(proj.objective)}</div>` : ''}
      <div class="edf-proj-meta">
        <span>${esc(call.identifier)}</span>
        ${role ? `<span class="edf-proj-role ${role}">${esc(role)}</span>` : ''}
        ${eu ? `<span>org share: <span class="edf-contrib">${eu}</span></span>` : ''}
        ${totalEu ? `<span>project total: ${esc(totalEu)}</span>` : ''}
        ${start ? `<span>${start}${end ? ' → '+end : ''}</span>` : ''}
        ${proj.url ? `<a href="${esc(proj.url)}" target="_blank" class="edf-proj-link">EU Portal ↗</a>` : ''}
      </div>
      ${partCount > 0 ? `<button class="edf-load-btn" data-proj-idx="${i}">Load ${partCount} participant${partCount !== 1 ? 's' : ''}</button>` : ''}
      <ul class="edf-participants" id="edf-parts-${i}"></ul>
    </li>`;
  }
  html += `</ul>`;
  listEl.innerHTML = html;

  listEl.querySelectorAll('[data-proj-idx]').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = Number(btn.dataset.projIdx);
      const { proj } = found[idx];
      const partsEl = document.getElementById(`edf-parts-${idx}`);
      if (partsEl.classList.contains('open')) {
        partsEl.classList.remove('open');
        partsEl.innerHTML = '';
        btn.textContent = `Load ${(proj.participants||[]).length} participant${(proj.participants||[]).length !== 1 ? 's' : ''}`;
        return;
      }
      renderProjectParticipants(partsEl, proj.participants || []);
      partsEl.classList.add('open');
      btn.textContent = 'Hide participants';
    });
  });
}

function renderProjectParticipants(partsEl, participants) {
  let html = '';
  for (const p of participants) {
    const eu = fmtEur(p.eu_contribution);
    const role = p.role || '';
    html += `<li class="edf-participant-item">
      <button class="edf-participant-btn" data-pic="${esc(String(p.pic || ''))}">${esc(p.organization_name)}</button>
      ${role ? `<span class="edf-proj-role ${role.toLowerCase()}">${esc(role)}</span>` : ''}
      ${p.country ? `<span class="edf-participant-country">${esc(p.country)}</span>` : ''}
      ${eu ? `<span class="edf-part-contrib">${eu}</span>` : ''}
    </li>`;
  }
  partsEl.innerHTML = html;

  partsEl.querySelectorAll('.edf-participant-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = PIC_MAP[btn.dataset.pic];
      if (item) selectItem(item);
    });
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  try {
    await loadData();
    buildRegistry();

    document.getElementById('cs-loading').style.display = 'none';
    document.getElementById('cs-hero').style.display = '';

    searchEl  = document.getElementById('cs-search');
    acEl      = document.getElementById('cs-ac');
    searchElB = document.getElementById('cs-search-b');
    acElB     = document.getElementById('cs-ac-b');

    // ── Compare toggle ────────────────────────────────────────────────────────
    const cmpChk    = document.getElementById('cs-cmp-chk');
    const cmpSecond = document.getElementById('cs-cmp-second');
    const cmpBtn    = document.getElementById('cs-cmp-btn');
    const clearBtnB = document.getElementById('cs-clear-b');

    cmpChk.addEventListener('change', () => {
      if (cmpChk.checked) {
        cmpSecond.classList.add('open');
        searchElB.focus();
      } else {
        cmpSecond.classList.remove('open');
        clearSelectionB();
        document.getElementById('cs-compare').classList.remove('visible');
        if (currentItem) {
          document.getElementById('cs-profile').classList.add('visible');
          Router.clearCompare();
        }
      }
    });

    searchElB.addEventListener('input', () => {
      clearBtnB.style.display = searchElB.value ? '' : 'none';
      renderAcB(searchElB.value);
    });
    searchElB.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown')  { e.preventDefault(); moveAcKbdB(1); }
      if (e.key === 'ArrowUp')    { e.preventDefault(); moveAcKbdB(-1); }
      if (e.key === 'Enter') {
        if (acKbdB >= 0 && acListB[acKbdB]) selectItemB(acListB[acKbdB]);
        else closeAcB();
      }
      if (e.key === 'Escape') closeAcB();
    });
    clearBtnB.addEventListener('click', () => {
      clearSelectionB();
      searchElB.focus();
    });
    document.addEventListener('click', e => {
      if (!e.target.closest('#cs-cmp-second')) closeAcB();
    });

    cmpBtn.addEventListener('click', () => {
      if (currentItem && selectedB) openCompare();
    });

    // Clear (×) button
    const clearBtn = document.getElementById('cs-clear');
    searchEl.addEventListener('input', () => {
      clearBtn.style.display = searchEl.value ? '' : 'none';
    });
    clearBtn.addEventListener('click', () => {
      if (currentItem) {
        clearSelection();
      } else {
        searchEl.value = '';
        clearBtn.style.display = 'none';
        closeAc();
        searchEl.focus();
        renderSuggestions();
      }
    });

    searchEl.addEventListener('input', () => renderAc(searchEl.value));
    searchEl.addEventListener('focus', () => {
      if (!searchEl.value) renderSuggestions();
    });
    searchEl.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown')  { e.preventDefault(); moveAcKbd(1); }
      if (e.key === 'ArrowUp')    { e.preventDefault(); moveAcKbd(-1); }
      if (e.key === 'Enter') {
        if (acKbd >= 0 && acList[acKbd]) selectItem(acList[acKbd]);
        else closeAc();
      }
      if (e.key === 'Escape') closeAc();
    });
    document.addEventListener('click', e => {
      if (!e.target.closest('.cs-search-wrap')) closeAc();
    });

    document.getElementById('cs-back').addEventListener('click', clearSelection);

    document.querySelectorAll('.filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeFilter = btn.dataset.filter;
        if (searchEl.value) renderAc(searchEl.value);
        else renderSuggestions();
      });
    });

    const totalOrgs   = DB.entities.length;
    const totalCo     = DB.entities.filter(e => e.type === 'company').length;
    const totalInv    = DB.entities.filter(e => e.id.startsWith('IV-')).length;
    document.querySelector('.cs-hero-prompt').textContent =
      `${totalOrgs.toLocaleString()} orgs · ${totalCo.toLocaleString()} companies · ${totalInv.toLocaleString()} investors`;

    // ── Routing — restore state from URL on load and on back/forward
    const initialItem    = Router.resolve(REGISTRY, ENTITY_MAP);
    const initialCmpItem = Router.resolveCompare(REGISTRY);

    if (initialItem) {
      selectItem(initialItem, true);
      if (initialCmpItem) {
        selectedB = initialCmpItem;
        searchElB.value = initialCmpItem.name;
        document.getElementById('cs-clear-b').style.display = '';
        cmpChk.checked = true;
        cmpSecond.classList.add('open');
        openCompare();
      }
    }

    Router.onPopState(REGISTRY, ENTITY_MAP, item => {
      const cmpItem = Router.resolveCompare(REGISTRY);
      if (item && cmpItem) {
        selectItem(item);
        selectedB = cmpItem;
        searchElB.value = cmpItem.name;
        document.getElementById('cs-clear-b').style.display = '';
        cmpChk.checked = true;
        cmpSecond.classList.add('open');
        openCompare();
      } else if (item) {
        cmpChk.checked = false;
        cmpSecond.classList.remove('open');
        clearSelectionB();
        selectItem(item);
      } else {
        clearSelection();
      }
    });

  } catch (err) {
    document.getElementById('cs-loading').innerHTML =
      `<div class="cs-error">Error loading data: ${esc(String(err))}</div>`;
    console.error(err);
  }
}

init();
