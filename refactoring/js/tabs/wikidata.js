'use strict';

import { AppState } from '../state.js';
import { esc } from '../helpers.js';

// SPARQL result cache: QID → rendered HTML
const wdCache = new Map();
// AbortController for in-flight SPARQL request
let wdAbortCtrl = null;

export default function initWikidata() {
  renderWdSidebar();

  // Close live drop on outside click
  document.addEventListener('click', e => {
    if (!e.target.closest('#wd-live-controls')) {
      document.getElementById('wd-live-drop')?.classList.remove('open');
    }
  });
}

function renderWdSidebar() {
  const { companies } = AppState;
  const wdState = AppState.ui.wikidata;

  wdState.list = companies.filter(c => c.wikidata_id).sort((a, b) => a.name.localeCompare(b.name));

  const countryCounts = {};
  wdState.list.forEach(c => {
    const co = c.sources?.wikidata?.country || 'Unknown';
    countryCounts[co] = (countryCounts[co] || 0) + 1;
  });
  const sortedCountries = Object.entries(countryCounts).sort((a, b) => b[1] - a[1]);

  const btnsEl = document.getElementById('wd-country-btns');
  btnsEl.innerHTML = '';

  const allBtn = document.createElement('button');
  allBtn.className = 'country-filter-btn active';
  allBtn.textContent = `All (${wdState.list.length})`;
  allBtn.addEventListener('click', () => setWdCountry(null, allBtn));
  btnsEl.appendChild(allBtn);

  sortedCountries.forEach(([co, n]) => {
    const btn = document.createElement('button');
    btn.className = 'country-filter-btn';
    btn.innerHTML = `${esc(co)} <span style="opacity:.5">${n}</span>`;
    btn.addEventListener('click', () => setWdCountry(co, btn));
    btnsEl.appendChild(btn);
  });

  renderWdList();
}

function setWdCountry(country, btn) {
  AppState.ui.wikidata.selectedCountry = country;
  document.querySelectorAll('#wd-country-btns .country-filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderWdList();
}

function renderWdList() {
  const { list, selectedCountry } = AppState.ui.wikidata;
  const filtered = selectedCountry
    ? list.filter(c => (c.sources?.wikidata?.country || 'Unknown') === selectedCountry)
    : list;

  const container = document.getElementById('wd-company-list');
  container.innerHTML = '';
  filtered.forEach(c => {
    const el = document.createElement('div');
    el.className = 'wd-company-item';
    el.innerHTML = `<span>${esc(c.name)}</span><span class="wd-qid">${c.wikidata_id}</span>`;
    el.addEventListener('click', () => selectWdCompany(c.wikidata_id, c.name, el));
    container.appendChild(el);
  });
}

function selectWdCompany(qid, label, el) {
  document.querySelectorAll('.wd-company-item').forEach(e => e.classList.remove('active'));
  el?.classList.add('active');
  document.getElementById('wd-selected-label').textContent = label;
  const extLink = document.getElementById('wd-external-link');
  extLink.href = `https://www.wikidata.org/wiki/${qid}`;
  extLink.style.display = 'inline';
  fetchWdData(qid, label);
}

export function toggleWdMode(isLive) {
  AppState.ui.wikidata.liveMode = isLive;
  document.getElementById('wd-local-controls').style.display = isLive ? 'none' : '';
  document.getElementById('wd-live-controls').style.display  = isLive ? 'block' : 'none';
  document.getElementById('wd-results').innerHTML = '<div class="wd-placeholder">Select or search for a Wikidata entity.</div>';
  document.getElementById('wd-selected-label').textContent = '← Select a company';
  document.getElementById('wd-external-link').style.display = 'none';
}

export function onLiveInput() {
  const wdState = AppState.ui.wikidata;
  clearTimeout(wdState.debounce);
  const q = document.getElementById('wd-live-input').value.trim();
  document.getElementById('wd-live-drop').classList.remove('open');
  if (!q) return;
  wdState.debounce = setTimeout(() => fetchWdAutocomplete(q), 300);
}

async function fetchWdAutocomplete(q) {
  try {
    const url = `https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&search=${encodeURIComponent(q)}&origin=*`;
    const data = await fetch(url).then(r => r.json());
    const drop = document.getElementById('wd-live-drop');
    drop.innerHTML = '';
    (data.search || []).forEach(item => {
      const el = document.createElement('div');
      el.className = 'live-drop-item';
      el.innerHTML = `<div class="live-label">${esc(item.label)}</div><div class="live-desc">${esc(item.description || '')}</div>`;
      el.addEventListener('click', () => selectWdLive(item.id, item.label));
      drop.appendChild(el);
    });
    drop.classList.toggle('open', !!(data.search?.length));
  } catch (e) {
    console.error(e);
  }
}

function selectWdLive(qid, label) {
  document.getElementById('wd-live-input').value = label;
  document.getElementById('wd-live-drop').classList.remove('open');
  document.getElementById('wd-selected-label').textContent = label;
  const extLink = document.getElementById('wd-external-link');
  extLink.href = `https://www.wikidata.org/wiki/${qid}`;
  extLink.style.display = 'inline';
  fetchWdData(qid, label);
}

async function fetchWdData(qid, label) {
  const loader  = document.getElementById('wd-loader');
  const errEl   = document.getElementById('wd-error');
  const results = document.getElementById('wd-results');
  loader.style.display = 'block';
  errEl.style.display  = 'none';
  results.innerHTML    = '';

  // Return cached result immediately if available
  if (wdCache.has(qid)) {
    loader.style.display = 'none';
    results.innerHTML = wdCache.get(qid);
    return;
  }

  // Cancel any in-flight request
  if (wdAbortCtrl) wdAbortCtrl.abort();
  wdAbortCtrl = new AbortController();
  const signal = wdAbortCtrl.signal;

  const endpoint = 'https://query.wikidata.org/sparql';
  const headers  = { 'Accept': 'application/sparql-results+json', 'User-Agent': 'dbv2-explorer/1.0' };

  const runQuery = async q => {
    const r = await fetch(`${endpoint}?query=${encodeURIComponent(q)}`, { headers, signal });
    if (!r.ok) throw new Error(`SPARQL ${r.status}`);
    return r.json();
  };

  try {
    const [core, people, corporate, social, stock, fin] = await Promise.all([
      runQuery(qCore(qid)),
      runQuery(qPeople(qid)),
      runQuery(qCorporate(qid)),
      runQuery(qSocial(qid)),
      runQuery(qStock(qid)),
      runQuery(qFin(qid)),
    ]);

    const merged = {};
    [core, people, corporate, social, stock].forEach(res => {
      if (res.results.bindings[0]) Object.assign(merged, res.results.bindings[0]);
    });
    if (fin.results.bindings.length) merged['__FINANCIAL'] = fin.results.bindings;

    loader.style.display = 'none';
    const html = renderWdResults(merged, qid);
    wdCache.set(qid, html);
    results.innerHTML = html;
  } catch (err) {
    if (err.name === 'AbortError') return; // silently ignore cancelled requests
    loader.style.display = 'none';
    errEl.style.display  = 'block';
    errEl.textContent    = `Error: ${err.message}`;
  }
}

function renderWdResults(result, qid) {
  const { companies } = AppState;
  const localEnt = companies.find(c => c.wikidata_id === qid);
  const localWd  = localEnt?.sources?.wikidata;

  const FIELDS = [
    ['COMPANY_label', 'Label'], ['DESCRIPTION', 'Description'], ['SECTORS', 'Sectors'],
    ['LEGAL_FORM', 'Legal form'], ['COUNTRY_label', 'Country'], ['HEADQUARTERS', 'Headquarters'],
    ['INCEPTION_DATE', 'Inception'], ['EMPLOYEES_COUNT', 'Employees'],
    ['FOUNDED_BY', 'Founded by'], ['NAMED_AFTER', 'Named after'], ['SLOGAN', 'Slogan'],
    ['REPLACES', 'Replaces'], ['REPLACED_BY', 'Replaced by'], ['LEGAL_ENTITY_IDENTIFIER', 'LEI'],
    ['CEOS_HISTORY', 'CEOs'], ['BOARD_MEMBERS', 'Board'], ['OWNERS_HISTORY', 'Owners'],
    ['PARENT_ORGANIZATIONS', 'Parent orgs'], ['SUBSIDIARIES', 'Subsidiaries'], ['PRODUCTS_SERVICES', 'Products/services'],
    ['BRANDS_OWNED', 'Brands owned'], ['PARENT_BRANDS', 'Parent brands'],
    ['STOCK_EXCHANGES', 'Stock exchanges'], ['TICKER_SYMBOLS', 'Tickers'],
    ['ISIN_CODES', 'ISIN'], ['SEC_CIK_NUMBER', 'SEC CIK'], ['SWIFT_BIC_CODE', 'SWIFT/BIC'],
    ['OFFICIAL_WEBSITE', 'Website'], ['TWITTER_HANDLES', 'Twitter'], ['LINKEDIN_IDS', 'LinkedIn'],
    ['FACEBOOK_IDS', 'Facebook'], ['INSTAGRAM_HANDLES', 'Instagram'],
    ['GITHUB_USERNAMES', 'GitHub'], ['CRUNCHBASE_PROFILE', 'Crunchbase'],
    ['BLOOMBERG_ID', 'Bloomberg'], ['LOGO_IMAGE', 'Logo'],
    ['WIKIPEDIA_URL', 'Wikipedia'], ['WIKIDATA', 'Wikidata ID'],
  ];

  let html = '';
  if (localWd) {
    html += `<div style="font-size:var(--fs-xs);text-transform:uppercase;letter-spacing:.5px;color:var(--accent);font-weight:700;margin-bottom:8px">Stored in database.json</div>`;
    html += '<table class="wd-field-table" style="margin-bottom:20px">';
    const localFields = [
      ['label', 'Label'], ['description', 'Description'], ['country', 'Country'], ['inception', 'Inception'],
      ['employees', 'Employees'], ['headquarters', 'HQ'], ['official_website', 'Website'], ['isin', 'ISIN'], ['wikipedia_url', 'Wikipedia'],
    ];
    localFields.forEach(([key, label]) => {
      const val = localWd[key];
      if (!val) return;
      html += `<tr><th>${label}</th><td>${typeof val === 'string' && val.startsWith('http') ? `<a href="${esc(val)}" target="_blank">${esc(val)}</a>` : esc(val)}</td></tr>`;
    });
    html += '</table>';
    html += `<div style="font-size:var(--fs-xs);text-transform:uppercase;letter-spacing:.5px;color:var(--accent);font-weight:700;margin-bottom:8px">Live from Wikidata SPARQL</div>`;
  }

  html += '<table class="wd-field-table">';
  FIELDS.forEach(([key, label]) => {
    const item = result[key];
    if (!item) return;
    const val = item.value;
    let cellHtml;
    if (typeof val === 'string' && val.startsWith('http')) {
      if (/\.(jpg|jpeg|png|gif|svg)$/i.test(val)) {
        cellHtml = `<a href="${esc(val)}" target="_blank"><img src="${esc(val)}" style="max-width:120px;max-height:80px"></a>`;
      } else {
        cellHtml = `<a href="${esc(val)}" target="_blank">${esc(val)}</a>`;
      }
    } else {
      cellHtml = val.split('; ').map(p => `<span style="display:block">${esc(p)}</span>`).join('');
    }
    html += `<tr><th>${label}</th><td>${cellHtml}</td></tr>`;
  });

  if (result['__FINANCIAL']?.length) {
    html += `<tr><th style="vertical-align:top">Financials</th><td>${renderFinTable(result['__FINANCIAL'])}</td></tr>`;
  }
  html += '</table>';
  return html;
}

function renderFinTable(rows) {
  const byYear = {};
  const METRICS = ['Market Cap', 'Total Revenue', 'Net Income', 'Operating Income', 'Total Assets', 'Total Equity', 'Total Liabilities', 'Total Debt', 'Employees'];
  rows.forEach(row => {
    const year = row.date ? new Date(row.date.value).getFullYear() : '?';
    if (!byYear[year]) { byYear[year] = {}; METRICS.forEach(m => { byYear[year][m] = 'N/A'; }); }
    const m = row.metric_label.value;
    const v = parseFloat(row.value.value);
    byYear[year][m] = m === 'Employees' ? Math.round(v).toLocaleString() : `${(v / 1e9).toFixed(1)}B`;
  });
  const years = Object.keys(byYear).sort((a, b) => parseInt(b) - parseInt(a));
  let t = `<table class="wd-fin-table"><thead><tr><th>Year</th>${METRICS.map(m => `<th>${m}</th>`).join('')}</tr></thead><tbody>`;
  years.forEach(y => {
    t += `<tr><td><strong>${y}</strong></td>${METRICS.map(m => `<td>${byYear[y][m]}</td>`).join('')}</tr>`;
  });
  return t + '</tbody></table>';
}

// ── SPARQL Queries ──
function qCore(id) {
  return `
    SELECT ?WIKIDATA
      (SAMPLE(?COMPANY_label) AS ?COMPANY_label)
      (SAMPLE(?description) AS ?DESCRIPTION)
      (SAMPLE(?COUNTRY_label) AS ?COUNTRY_label)
      (SAMPLE(?wikipedia_url) AS ?WIKIPEDIA_URL)
      (SAMPLE(?inception_date) AS ?INCEPTION_DATE)
      (SAMPLE(?legal_form_label) AS ?LEGAL_FORM)
      (SAMPLE(?named_after_label) AS ?NAMED_AFTER)
      (SAMPLE(?slogan) AS ?SLOGAN)
      (SAMPLE(?employees_count) AS ?EMPLOYEES_COUNT)
      (SAMPLE(?replaces_label) AS ?REPLACES)
      (SAMPLE(?replaced_by_label) AS ?REPLACED_BY)
      (SAMPLE(?lei) AS ?LEGAL_ENTITY_IDENTIFIER)
      (GROUP_CONCAT(DISTINCT ?SECTOR_label; separator=", ") AS ?SECTORS)
      (GROUP_CONCAT(DISTINCT ?HEADQUARTERS_label; separator=", ") AS ?HEADQUARTERS)
      (GROUP_CONCAT(DISTINCT ?founder_label; separator=", ") AS ?FOUNDED_BY)
    WHERE {
      VALUES ?WIKIDATA { wd:${id} }
      ?WIKIDATA rdfs:label ?COMPANY_label.
      FILTER(LANG(?COMPANY_label) = "en")
      OPTIONAL { ?WIKIDATA schema:description ?description. FILTER(LANG(?description) = "en") }
      OPTIONAL {
        ?WIKIDATA wdt:P17 ?COUNTRY.
        ?COUNTRY rdfs:label ?COUNTRY_label.
        FILTER(LANG(?COUNTRY_label) = "en")
      }
      OPTIONAL { ?WIKIDATA wdt:P571 ?inception_date. }
      OPTIONAL {
        ?wikipedia_url schema:about ?WIKIDATA;
          schema:inLanguage "en";
          schema:isPartOf <https://en.wikipedia.org/>.
      }
      OPTIONAL {
        ?WIKIDATA wdt:P452 ?SECTOR.
        ?SECTOR rdfs:label ?SECTOR_label.
        FILTER(LANG(?SECTOR_label) = "en")
      }
      OPTIONAL {
        ?WIKIDATA wdt:P159 ?HEADQUARTERS.
        ?HEADQUARTERS rdfs:label ?HEADQUARTERS_label.
        FILTER(LANG(?HEADQUARTERS_label) = "en")
      }
      OPTIONAL {
        ?WIKIDATA wdt:P1454 ?legal_form.
        ?legal_form rdfs:label ?legal_form_label.
        FILTER(LANG(?legal_form_label) = "en")
      }
      OPTIONAL {
        ?WIKIDATA wdt:P112 ?founder.
        ?founder rdfs:label ?founder_label.
        FILTER(LANG(?founder_label) = "en")
      }
      OPTIONAL {
        ?WIKIDATA wdt:P138 ?named_after.
        ?named_after rdfs:label ?named_after_label.
        FILTER(LANG(?named_after_label) = "en")
      }
      OPTIONAL { ?WIKIDATA wdt:P1451 ?slogan. FILTER(LANG(?slogan) = "en") }
      OPTIONAL { ?WIKIDATA wdt:P1128 ?employees_count. }
      OPTIONAL {
        ?WIKIDATA wdt:P1365 ?replaces.
        ?replaces rdfs:label ?replaces_label.
        FILTER(LANG(?replaces_label) = "en")
      }
      OPTIONAL {
        ?WIKIDATA wdt:P1366 ?replaced_by.
        ?replaced_by rdfs:label ?replaced_by_label.
        FILTER(LANG(?replaced_by_label) = "en")
      }
      OPTIONAL { ?WIKIDATA wdt:P1278 ?lei. }
    }
    GROUP BY ?WIKIDATA
  `;
}

function qPeople(id) {
  return `
    SELECT
      (GROUP_CONCAT(DISTINCT ?ceo_formatted; separator="; ") AS ?CEOS_HISTORY)
      (GROUP_CONCAT(DISTINCT ?owner_formatted; separator="; ") AS ?OWNERS_HISTORY)
      (GROUP_CONCAT(DISTINCT ?BOARD_MEMBER_label; separator=", ") AS ?BOARD_MEMBERS)
    WHERE {
      VALUES ?WIKIDATA { wd:${id} }
      OPTIONAL {
        ?WIKIDATA p:P169 ?ceo_statement.
        ?ceo_statement ps:P169 ?ceo_item.
        ?ceo_item rdfs:label ?ceo_label.
        FILTER(LANG(?ceo_label) = "en").
        OPTIONAL { ?ceo_statement pq:P580 ?start_date. }
        OPTIONAL { ?ceo_statement pq:P582 ?end_date. }
        BIND(CONCAT(?ceo_label, " (from ", COALESCE(STR(YEAR(?start_date)), "?"), " to ", COALESCE(STR(YEAR(?end_date)), "present"), ")") AS ?ceo_formatted)
      }
      OPTIONAL {
        ?WIKIDATA p:P127 ?owner_statement.
        ?owner_statement ps:P127 ?owner_item.
        ?owner_item rdfs:label ?owner_label.
        FILTER(LANG(?owner_label) = "en").
        OPTIONAL { ?owner_statement pq:P585 ?owner_date. }
        BIND(CONCAT(?owner_label, " (as of ", COALESCE(STR(YEAR(?owner_date)), "?"), ")") AS ?owner_formatted)
      }
      OPTIONAL {
        ?WIKIDATA wdt:P3320 ?BOARD_MEMBER.
        ?BOARD_MEMBER rdfs:label ?BOARD_MEMBER_label.
        FILTER(LANG(?BOARD_MEMBER_label) = "en")
      }
    }
    GROUP BY ?WIKIDATA
  `;
}

function qCorporate(id) {
  return `
    SELECT
      (GROUP_CONCAT(DISTINCT ?PARENT_ORGANIZATION_label; separator=", ") AS ?PARENT_ORGANIZATIONS)
      (GROUP_CONCAT(DISTINCT ?SUBSIDIARY_label; separator=", ") AS ?SUBSIDIARIES)
      (GROUP_CONCAT(DISTINCT ?PRODUCT_label; separator=", ") AS ?PRODUCTS_SERVICES)
    WHERE {
      VALUES ?WIKIDATA { wd:${id} }
      OPTIONAL {
        ?WIKIDATA wdt:P749 ?PARENT_ORGANIZATION.
        ?PARENT_ORGANIZATION rdfs:label ?PARENT_ORGANIZATION_label.
        FILTER(LANG(?PARENT_ORGANIZATION_label) = "en")
      }
      OPTIONAL {
        ?WIKIDATA wdt:P355 ?SUBSIDIARY.
        ?SUBSIDIARY rdfs:label ?SUBSIDIARY_label.
        FILTER(LANG(?SUBSIDIARY_label) = "en")
      }
      OPTIONAL {
        ?WIKIDATA wdt:P1056 ?PRODUCT.
        ?PRODUCT rdfs:label ?PRODUCT_label.
        FILTER(LANG(?PRODUCT_label) = "en")
      }
    }
    GROUP BY ?WIKIDATA
  `;
}

function qSocial(id) {
  return `
    SELECT
      (SAMPLE(?official_website) AS ?OFFICIAL_WEBSITE)
      (SAMPLE(?logo_image) AS ?LOGO_IMAGE)
      (GROUP_CONCAT(DISTINCT ?twitter_username; separator=", ") AS ?TWITTER_HANDLES)
      (GROUP_CONCAT(DISTINCT ?linkedin_id; separator=", ") AS ?LINKEDIN_IDS)
      (GROUP_CONCAT(DISTINCT ?facebook_id; separator=", ") AS ?FACEBOOK_IDS)
      (GROUP_CONCAT(DISTINCT ?instagram_username; separator=", ") AS ?INSTAGRAM_HANDLES)
      (GROUP_CONCAT(DISTINCT ?github_username; separator=", ") AS ?GITHUB_USERNAMES)
      (SAMPLE(?crunchbase_profile) AS ?CRUNCHBASE_PROFILE)
      (SAMPLE(?bloomberg_id) AS ?BLOOMBERG_ID)
    WHERE {
      VALUES ?WIKIDATA { wd:${id} }
      OPTIONAL { ?WIKIDATA wdt:P856 ?official_website. }
      OPTIONAL { ?WIKIDATA wdt:P154 ?logo_image. }
      OPTIONAL { ?WIKIDATA wdt:P2002 ?twitter_username. }
      OPTIONAL { ?WIKIDATA wdt:P4264 ?linkedin_id. }
      OPTIONAL { ?WIKIDATA wdt:P2013 ?facebook_id. }
      OPTIONAL { ?WIKIDATA wdt:P2003 ?instagram_username. }
      OPTIONAL { ?WIKIDATA wdt:P2037 ?github_username. }
      OPTIONAL { ?WIKIDATA wdt:P2088 ?crunchbase_profile. }
      OPTIONAL { ?WIKIDATA wdt:P3052 ?bloomberg_id. }
    }
    GROUP BY ?WIKIDATA
  `;
}

function qStock(id) {
  return `
    SELECT
      (GROUP_CONCAT(DISTINCT ?stock_exchange_label; separator=", ") AS ?STOCK_EXCHANGES)
      (GROUP_CONCAT(DISTINCT ?ticker_symbol; separator=", ") AS ?TICKER_SYMBOLS)
      (GROUP_CONCAT(DISTINCT ?isin; separator=", ") AS ?ISIN_CODES)
      (SAMPLE(?sec_cik) AS ?SEC_CIK_NUMBER)
      (SAMPLE(?swift_bic) AS ?SWIFT_BIC_CODE)
    WHERE {
      VALUES ?WIKIDATA { wd:${id} }
      OPTIONAL {
        ?WIKIDATA wdt:P414 ?stock_exchange.
        ?stock_exchange rdfs:label ?stock_exchange_label.
        FILTER(LANG(?stock_exchange_label) = "en")
      }
      OPTIONAL { ?WIKIDATA wdt:P249 ?ticker_symbol. }
      OPTIONAL { ?WIKIDATA wdt:P946 ?isin. }
      OPTIONAL { ?WIKIDATA wdt:P5531 ?sec_cik. }
      OPTIONAL { ?WIKIDATA wdt:P2627 ?swift_bic. }
    }
    GROUP BY ?WIKIDATA
  `;
}

function qFin(id) {
  return `
    SELECT ?metric_label ?value (SAMPLE(?date) AS ?date)
    WHERE {
      VALUES ?WIKIDATA { wd:${id} }
      {
        ?WIKIDATA p:P2226 ?statement.
        BIND("Market Cap" AS ?metric_label)
        ?statement ps:P2226 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P2139 ?statement.
        BIND("Total Revenue" AS ?metric_label)
        ?statement ps:P2139 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P2295 ?statement.
        BIND("Net Income" AS ?metric_label)
        ?statement ps:P2295 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P3362 ?statement.
        BIND("Operating Income" AS ?metric_label)
        ?statement ps:P3362 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P2403 ?statement.
        BIND("Total Assets" AS ?metric_label)
        ?statement ps:P2403 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P2137 ?statement.
        BIND("Total Equity" AS ?metric_label)
        ?statement ps:P2137 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P2138 ?statement.
        BIND("Total Liabilities" AS ?metric_label)
        ?statement ps:P2138 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P2133 ?statement.
        BIND("Total Debt" AS ?metric_label)
        ?statement ps:P2133 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      } UNION {
        ?WIKIDATA p:P1128 ?statement.
        BIND("Employees" AS ?metric_label)
        ?statement ps:P1128 ?value.
        OPTIONAL { ?statement pq:P585 ?date. }
      }
    }
    GROUP BY ?metric_label ?value ?date
    ORDER BY DESC(?date)
  `;
}
