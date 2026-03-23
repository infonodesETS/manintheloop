'use strict';

import { AppState } from '../state.js';
import { esc, sectorBadge } from '../helpers.js';
import { getParams, setParams } from '../url.js';

// Wikidata country name → ISO numeric (world-atlas format)
const WD_TO_ISO = {
  'United States':        840,
  'USA':                  840,
  'Germany':              276,
  'Germania':             276,
  'United Kingdom':       826,
  'UK':                   826,
  'France':               250,
  'Francia':              250,
  'Israel':               376,
  'Sweden':               752,
  'Norway':               578,
  'Norvegia':             578,
  'Finland':              246,
  'Denmark':              208,
  'Netherlands':          528,
  'Belgium':              56,
  'Belgio':               56,
  'Switzerland':          756,
  'Austria':              40,
  'Italy':                380,
  'Spain':                724,
  'Poland':               616,
  'Polonia':              616,
  'Czech Republic':       203,
  'Czech Rep.':           203,
  'Czechia':              203,
  'Romania':              642,
  'Estonia':              233,
  'Latvia':               428,
  'Lithuania':            440,
  'Ukraine':              804,
  'Russia':               643,
  'Turkey':               792,
  'India':                356,
  'China':                156,
  'Cina':                 156,
  "People's Republic of China": 156,
  'Japan':                392,
  'Giappone':             392,
  'South Korea':          410,
  'Australia':            36,
  'Canada':               124,
  'Brazil':               76,
  'South Africa':         710,
  'Singapore':            702,
  'United Arab Emirates': 784,
  'EAU (Dubai)':          784,
  'Saudi Arabia':         682,
  'Portugal':             620,
  'Greece':               300,
  'Hungary':              348,
  'Slovakia':             703,
  'Luxembourg':           442,
  'Ireland':              372,
  'Cyprus':               196,
  'Malta':                470,
  'Croatia':              191,
  'Slovenia':             705,
  'Serbia':               688,
  'Bulgaria':             100,
  'North Macedonia':      807,
  'Albania':              8,
  'Moldova':              498,
  'Belarus':              112,
  'Kazakhstan':           398,
  'Mexico':               484,
  'Argentina':            32,
  'Chile':                152,
  'Cile':                 152,
  'Colombia':             170,
  'Peru':                 604,
  'New Zealand':          554,
  'Indonesia':            360,
  'Malaysia':             458,
  'Thailand':             764,
  'Vietnam':              704,
  'Philippines':          608,
  'Pakistan':             586,
  'Bangladesh':           50,
  'Egypt':                818,
  'Nigeria':              566,
  'Kenya':                404,
  'Morocco':              504,
  'Tunisia':              788,
  'Ethiopia':             231,
};

// Canonical English display names (ISO → name); built from first occurrence only
const ISO_TO_NAME = {};
for (const [name, iso] of Object.entries(WD_TO_ISO)) {
  if (!(iso in ISO_TO_NAME)) ISO_TO_NAME[iso] = name;
}

export default function initMap() {
  return buildMapView();
}

export function toggleMapArcs(show) {
  AppState.ui.map.showArcs = show;
  const layer = document.getElementById('map-arc-layer');
  if (layer) layer.style.display = show ? '' : 'none';
}

export function resetMapZoom() {
  const { svg, zoom } = AppState.ui.map;
  if (svg && zoom) svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
}

export function closeMapPanel() {
  document.getElementById('map-panel').classList.add('d-none');
  d3.select('#map-svg').selectAll('.map-country').classed('selected', false);
  AppState.ui.map.g?.selectAll('.map-arc').classed('arc-dim', false);
  const p = getParams(); delete p.country; setParams(p);
  document.getElementById('map-panel-title').textContent = 'About this map';
  document.getElementById('map-panel-body').innerHTML = `
    <div class="sl-panel-section">
      <div class="sl-section-lbl">What this map shows and how to navigate it</div>
      <p class="map-intro-text">Each circle represents a country with at least one company in the supply chain dataset. Circle size reflects the number of cross-border investor connections — larger circles are financial hubs, not necessarily where more companies are headquartered.</p>
      <p class="map-intro-text">Arcs connect investor countries (faint end) to company countries (bright end), showing the direction capital flows across borders.</p>
      <p class="map-intro-text">Click a country circle or a shaded country area to explore its companies and investor relationships. Use the toggles above the map to show or hide arcs.</p>
    </div>
  `;
}

export function selectMapCountryByName(name) {
  const iso = WD_TO_ISO[name];
  if (iso && AppState.ui.map.countryData?.[iso]) showMapCountry(iso);
}

export function clearMapFilter() {
  AppState.ui.map.activeFilter = null;
  applyMapFilter();
}

function buildMapView() {
  AppState.ui.map.built = true;
  document.getElementById('map-status').textContent = 'Loading world map…';

  const { companies, relationships, derived } = AppState;
  const { entityMap } = derived;
  const mapState = AppState.ui.map;

  // Build country data from companies
  mapState.countryData = {};
  companies.forEach(c => {
    const country = c.sources?.infonodes?.country || c.sources?.wikidata?.country;
    if (!country) return;
    const iso = WD_TO_ISO[country];
    if (!iso) return;
    if (!mapState.countryData[iso]) mapState.countryData[iso] = { name: ISO_TO_NAME[iso] || country, companies: [] };
    mapState.countryData[iso].companies.push(c);
  });

  // Build arc data: directed investor-country → company-country, weight = number of relationships
  const pairWeight = {};
  relationships.forEach(rel => {
    const comp = entityMap[rel.target];
    const inv  = entityMap[rel.source];
    if (!comp || !inv) return;
    const compCountry = comp.sources?.infonodes?.country || comp.sources?.wikidata?.country;
    const invCountry  = inv.sources?.infonodes?.country  || inv.sources?.wikidata?.country;
    const compISO = WD_TO_ISO[compCountry];
    const invISO  = WD_TO_ISO[invCountry];
    if (!compISO || !invISO || compISO === invISO) return;
    const key = `${invISO}→${compISO}`;  // directed: investor → company
    pairWeight[key] = (pairWeight[key] || 0) + 1;
  });

  mapState.arcData = Object.entries(pairWeight).map(([key, weight]) => {
    const [src, tgt] = key.split('→').map(Number);
    return { src, tgt, weight };  // src = investor country, tgt = company country
  });

  return fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
    .then(r => r.json())
    .then(world => drawMap(world))
    .catch(err => {
      document.getElementById('map-status').textContent = 'Failed to load map: ' + err.message;
    });
}

function drawMap(world) {
  const el = document.getElementById('map-svg');
  const W = el.clientWidth || 900;
  const H = el.clientHeight || 500;
  const mapState = AppState.ui.map;

  mapState.projection = d3.geoNaturalEarth1()
    .scale(W / 6.2)
    .translate([W / 2 - 100, H / 2 + 50]);

  const path = d3.geoPath().projection(mapState.projection);

  mapState.svg = d3.select('#map-svg');
  mapState.svg.selectAll('*').remove();

  mapState.g = mapState.svg.append('g');

  // Graticule
  const grat = d3.geoGraticule()();
  mapState.g.append('path')
    .datum(grat)
    .attr('d', path)
    .attr('fill', 'none')
    .attr('stroke', '#1a1a1a')
    .attr('stroke-width', 0.3);

  // Countries — compute centroids for all features (needed for arcs)
  const countries = topojson.feature(world, world.objects.countries);
  mapState.centroids = {};
  countries.features.forEach(f => {
    const iso = +f.id;
    const c = path.centroid(f);
    if (c && !isNaN(c[0]) && !isNaN(c[1])) mapState.centroids[iso] = c;
  });

  // Manual centroid overrides for countries whose topojson includes overseas territories
  // that pull the computed centroid far from the mainland. [lon, lat] in geographic coords.
  const CENTROID_OVERRIDES = {
    250: [2.3,   46.2],  // France — excludes French Guiana, Martinique, Réunion etc.
    528: [5.3,   52.1],  // Netherlands — excludes Caribbean islands
    620: [-8.0,  39.5],  // Portugal — excludes Azores, Madeira
    826: [-2.0,  54.0],  // United Kingdom — excludes overseas territories
    840: [-98.0, 39.5],  // United States — balances Alaska/Hawaii pull
  };
  Object.entries(CENTROID_OVERRIDES).forEach(([iso, [lon, lat]]) => {
    const projected = mapState.projection([lon, lat]);
    if (projected && !isNaN(projected[0])) mapState.centroids[+iso] = projected;
  });

  mapState.g.selectAll('.map-country')
    .data(countries.features)
    .join('path')
    .attr('class', d => {
      const iso = +d.id;
      return 'map-country' + (mapState.countryData[iso] ? ' has-data' : '');
    })
    .attr('d', path)
    .on('click', (e, d) => {
      const iso = +d.id;
      if (mapState.countryData[iso]) showMapCountry(iso);
    })
    .append('title')
    .text(d => {
      const iso = +d.id;
      const cd = mapState.countryData[iso];
      return cd ? `${cd.name} — ${cd.companies.length} companies` : ISO_TO_NAME[iso] || `ISO ${iso}`;
    });

  // Arc layer — visible by default
  const arcLayer = mapState.g.append('g').attr('id', 'map-arc-layer');
  drawArcs(arcLayer);

  // Country nodes (on top of arcs)
  const nodeLayer = mapState.g.append('g').attr('id', 'map-node-layer');

  // Compute arc degree per country (number of distinct arc connections)
  const arcDegree = {};
  mapState.arcData.forEach(arc => {
    arcDegree[arc.src] = (arcDegree[arc.src] || 0) + 1;
    arcDegree[arc.tgt] = (arcDegree[arc.tgt] || 0) + 1;
  });
  const maxDegree = Math.max(...Object.values(arcDegree), 1);
  const rScale = d3.scaleSqrt().domain([0, maxDegree]).range([4, 22]);

  Object.entries(mapState.countryData).forEach(([iso, cd]) => {
    iso = +iso;
    const c = mapState.centroids[iso];
    if (!c) return;
    const r = rScale(arcDegree[iso] || 0);
    // Store baseR as datum property per the map zoom performance fix
    const circDatum = { iso, baseR: r };
    nodeLayer.append('circle')
      .datum(circDatum)
      .attr('class', 'map-node')
      .attr('data-iso', iso)
      .attr('cx', c[0]).attr('cy', c[1])
      .attr('r', r)
      .on('click', (e) => { e.stopPropagation(); showMapCountry(iso); })
      .append('title')
      .text(`${cd.name}: ${cd.companies.length} companies · ${arcDegree[iso] || 0} cross-border connections`);

    if (r >= 8) {
      const baseFs = 11;
      const lblDatum = { cy: c[1], baseR: r, baseFs };
      nodeLayer.append('text')
        .datum(lblDatum)
        .attr('class', 'map-label')
        .attr('x', c[0]).attr('y', c[1] + r + baseFs)
        .style('font-size', baseFs + 'px')
        .text(cd.name);
    }
  });

  // Zoom — keep nodes/labels/arcs at constant visual size
  // Uses datum().baseR (JS object property) instead of DOM attribute strings
  mapState.zoom = d3.zoom().scaleExtent([0.5, 12]).on('zoom', e => {
    mapState.g.attr('transform', e.transform);
    const k = e.transform.k;
    mapState.g.selectAll('.map-node').each(function(d) {
      const baseR = d.baseR;
      d3.select(this)
        .attr('r', baseR / k)
        .attr('stroke-width', 1.5 / k);
    });
    mapState.g.selectAll('.map-label').each(function(d) {
      const fs = d.baseFs / k;
      d3.select(this)
        .style('font-size', fs + 'px')
        .attr('y', d.cy + d.baseR / k + fs);
    });
    mapState.g.selectAll('.map-arc').each(function(d) {
      d3.select(this).attr('stroke-width', d.baseSw / k);
    });
  });
  mapState.svg.call(mapState.zoom);

  const coCount = Object.keys(mapState.countryData).length;
  const totCo = Object.values(mapState.countryData).reduce((s, d) => s + d.companies.length, 0);
  document.getElementById('map-status').textContent =
    `${coCount} countries · ${totCo} companies mapped · ${mapState.arcData.length} cross-border investor pairs`;
  document.getElementById('map-panel').classList.remove('d-none');

  applyMapFilter(); // initialise filter bar state (hidden by default)

  // Open panel by default with intro content
  document.getElementById('map-panel-title').textContent = 'About this map';
  document.getElementById('map-panel-body').innerHTML = `
    <div class="sl-panel-section">
      <div class="sl-section-lbl">What this map shows and how to navigate it</div>
      <p class="map-intro-text">Each circle represents a country with at least one company in the supply chain dataset. Circle size reflects the number of cross-border investor connections — larger circles are financial hubs, not necessarily where more companies are headquartered.</p>
      <p class="map-intro-text">Arcs connect investor countries (faint end) to company countries (bright end), showing the direction capital flows across borders.</p>
      <p class="map-intro-text">Click a country circle or a shaded country area to explore its companies and investor relationships. Use the toggles above the map to show or hide arcs.</p>
    </div>
  `;
}

function drawArcs(layer) {
  const mapState = AppState.ui.map;
  if (!mapState.arcData.length) return;
  const maxW = Math.max(...mapState.arcData.map(d => d.weight), 1);
  const strokeScale  = d3.scaleLinear().domain([1, maxW]).range([1, 4]);
  const opacityScale = d3.scaleLinear().domain([1, maxW]).range([0.55, 0.9]);

  // Defs for per-arc directional gradients (investor country → company country)
  const arcColor = '#68ccd1';
  let defs = d3.select('#map-svg').select('defs');
  if (defs.empty()) defs = d3.select('#map-svg').insert('defs', ':first-child');

  mapState.arcData.forEach((arc, i) => {
    const s = mapState.centroids[arc.src];
    const t = mapState.centroids[arc.tgt];
    if (!s || !t) return;
    const mx = (s[0] + t[0]) / 2;
    const my = (s[1] + t[1]) / 2 - Math.hypot(t[0] - s[0], t[1] - s[1]) * 0.3;
    const sw = strokeScale(arc.weight);
    const op = opacityScale(arc.weight);
    const gradId = `map-arc-grad-${i}`;

    // Gradient: transparent at source (capital flowing out), opaque at destination (flowing in)
    defs.append('linearGradient')
      .attr('id', gradId)
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', s[0]).attr('y1', s[1])
      .attr('x2', t[0]).attr('y2', t[1])
      .call(g => {
        g.append('stop').attr('offset', '0%')
          .attr('stop-color', arcColor).attr('stop-opacity', 0.07);
        g.append('stop').attr('offset', '100%')
          .attr('stop-color', arcColor).attr('stop-opacity', op);
      });

    const arcDatum = { src: arc.src, tgt: arc.tgt, baseSw: sw };
    layer.append('path')
      .datum(arcDatum)
      .attr('class', 'map-arc')
      .attr('d', `M${s[0]},${s[1]} Q${mx},${my} ${t[0]},${t[1]}`)
      .attr('stroke', `url(#${gradId})`)
      .attr('stroke-width', sw);
  });
}

function showMapCountry(iso) {
  const mapState = AppState.ui.map;
  const { relationships, derived } = AppState;
  const { entityMap } = derived;
  const cd = mapState.countryData[iso];
  if (!cd) return;

  d3.select('#map-svg').selectAll('.map-country')
    .classed('selected', d => +d.id === iso);

  // Show only arcs connected to this country
  AppState.ui.map.g?.selectAll('.map-arc')
    .classed('arc-dim', d => d.src !== iso && d.tgt !== iso);

  const sectorCount = {};
  cd.companies.forEach(c => {
    const s = c.sector || 'Other';
    sectorCount[s] = (sectorCount[s] || 0) + 1;
  });

  // Capital flowing IN: foreign investors → companies in this country
  const flowIn = {};
  relationships.forEach(rel => {
    const comp = entityMap[rel.target];
    if (!comp) return;
    const compCountry = comp.sources?.infonodes?.country || comp.sources?.wikidata?.country;
    if (WD_TO_ISO[compCountry] !== iso) return;
    const inv = entityMap[rel.source];
    if (!inv) return;
    const invCountry = inv.sources?.infonodes?.country || inv.sources?.wikidata?.country;
    if (WD_TO_ISO[invCountry] === iso) return; // skip domestic
    if (!flowIn[rel.source]) flowIn[rel.source] = inv.name;
  });

  // Capital flowing OUT: investors based in this country → foreign companies
  const flowOut = {};
  relationships.forEach(rel => {
    const inv = entityMap[rel.source];
    if (!inv) return;
    const invCountry = inv.sources?.infonodes?.country || inv.sources?.wikidata?.country;
    if (WD_TO_ISO[invCountry] !== iso) return;
    const comp = entityMap[rel.target];
    if (!comp) return;
    const compCountry = comp.sources?.infonodes?.country || comp.sources?.wikidata?.country;
    if (WD_TO_ISO[compCountry] === iso) return; // skip domestic
    if (!flowOut[rel.source]) flowOut[rel.source] = inv.name;
  });

  const flowInArr  = Object.entries(flowIn);
  const flowOutArr = Object.entries(flowOut);

  const renderInvestorList = (arr) => arr.slice(0, 25).map(([id, name]) => `
    <div class="map-co-item clickable" data-action="filterMapByEntity" data-id="${esc(id)}">
      <span>${esc(name)}</span>
      <span class="map-item-id">${id}</span>
    </div>`).join('') + (arr.length > 25 ? `<div class="map-item-more">+${arr.length - 25} more</div>` : '');

  const hasIn  = flowInArr.length > 0;
  const hasOut = flowOutArr.length > 0;

  const updateArcVisibility = () => {
    const showIn  = !hasIn  || document.getElementById('map-flow-in-btn')?.classList.contains('active');
    const showOut = !hasOut || document.getElementById('map-flow-out-btn')?.classList.contains('active');
    AppState.ui.map.g?.selectAll('.map-arc').classed('arc-dim', d => {
      if (d.tgt === iso) return !showIn;
      if (d.src === iso) return !showOut;
      return true; // not connected
    });
  };

  const sectorSummary = Object.entries(sectorCount)
    .sort((a, b) => b[1] - a[1])
    .map(([s, n]) => `${esc(s)} (${n})`)
    .join(', ');

  document.getElementById('map-panel-title').textContent = cd.name;
  document.getElementById('map-panel-body').innerHTML = `
    <div class="map-sector-row">
      <span class="map-sector-lbl">Sectors:</span> ${sectorSummary}
    </div>
    <div class="sl-panel-section">
      <div class="sl-section-lbl map-section-hd">
        ${cd.companies.length} Companies
        <button id="map-toggle-co" class="sf-btn active">on</button>
      </div>
      <div id="map-companies-list">
        ${cd.companies.map(c => `
          <div class="map-co-item clickable" data-action="filterMapByEntity" data-id="${esc(c.id)}">
            <span>${esc(c.name)}</span>
            ${sectorBadge(c.sector)}
          </div>`).join('')}
      </div>
    </div>
    ${hasIn ? `<div class="sl-panel-section">
      <div class="sl-section-lbl map-section-hd">
        ↓ Capital Flowing In (${flowInArr.length})
        <button id="map-flow-in-btn" class="sf-btn active">on</button>
      </div>
      <div id="map-flow-in-list">${renderInvestorList(flowInArr)}</div>
    </div>` : ''}
    ${hasOut ? `<div class="sl-panel-section">
      <div class="sl-section-lbl map-section-hd">
        ↑ Capital Flowing Out (${flowOutArr.length})
        <button id="map-flow-out-btn" class="sf-btn active">on</button>
      </div>
      <div id="map-flow-out-list">${renderInvestorList(flowOutArr)}</div>
    </div>` : ''}
  `;

  document.getElementById('map-toggle-co')?.addEventListener('click', function () {
    this.classList.toggle('active');
    this.textContent = this.classList.contains('active') ? 'on' : 'off';
    document.getElementById('map-companies-list').style.display =
      this.classList.contains('active') ? '' : 'none';
  });

  document.getElementById('map-flow-in-btn')?.addEventListener('click', function () {
    this.classList.toggle('active');
    const on = this.classList.contains('active');
    this.textContent = on ? 'on' : 'off';
    document.getElementById('map-flow-in-list').style.display = on ? '' : 'none';
    updateArcVisibility();
  });

  document.getElementById('map-flow-out-btn')?.addEventListener('click', function () {
    this.classList.toggle('active');
    const on = this.classList.contains('active');
    this.textContent = on ? 'on' : 'off';
    document.getElementById('map-flow-out-list').style.display = on ? '' : 'none';
    updateArcVisibility();
  });

  document.getElementById('map-panel-body').querySelectorAll('[data-action="filterMapByEntity"]').forEach(el => {
    el.addEventListener('click', () => filterMapByEntity(el.dataset.id, iso));
  });

  document.getElementById('map-panel').classList.remove('d-none');
  setParams({ ...getParams(), country: cd.name });
}

function filterMapByEntity(entityId, fromIso) {
  if (AppState.ui.map.activeFilter?.id === entityId) { clearMapFilter(); return; }
  const { derived, relationships } = AppState;
  const { entityMap } = derived;
  const ent = entityMap[entityId];
  if (!ent) return;

  const activeISOs = new Set();

  if (entityId.startsWith('IN-')) {
    const country = ent.sources?.infonodes?.country || ent.sources?.wikidata?.country;
    const ownISO = WD_TO_ISO[country];
    if (ownISO) activeISOs.add(ownISO);
    // Highlight investor home countries
    relationships.filter(r => r.target === entityId).forEach(rel => {
      const inv = entityMap[rel.source];
      if (!inv) return;
      const invCountry = inv.sources?.infonodes?.country || inv.sources?.wikidata?.country;
      const invISO = WD_TO_ISO[invCountry];
      if (invISO) activeISOs.add(invISO);
    });
  } else if (entityId.startsWith('IV-')) {
    relationships.filter(r => r.source === entityId).forEach(rel => {
      const comp = entityMap[rel.target];
      if (!comp) return;
      const country = comp.sources?.infonodes?.country || comp.sources?.wikidata?.country;
      const iso = WD_TO_ISO[country];
      if (iso) activeISOs.add(iso);
    });
  }

  AppState.ui.map.activeFilter = { id: entityId, name: ent.name, isos: activeISOs };
  applyMapFilter();

  // Drill-down: replace sidebar with entity detail
  const panelBody = document.getElementById('map-panel-body');
  let detail = '';

  if (entityId.startsWith('IN-')) {
    const cb  = ent.sources?.crunchbase || {};
    const wd  = ent.sources?.wikidata   || {};
    const inv = relationships.filter(r => r.target === entityId).map(r => entityMap[r.source]).filter(Boolean);
    const funding = cb.total_funding_usd ? `$${(cb.total_funding_usd / 1e6).toFixed(0)}M` : null;
    detail = `
      <div class="sl-section-lbl">${esc(ent.name)}</div>
      <div class="map-detail-meta">
        ${sectorBadge(ent.sector)}
        ${wd.country ? `<span class="map-item-id">${esc(wd.country)}</span>` : ''}
        ${funding ? `<span class="map-item-id">${funding}</span>` : ''}
      </div>
      ${inv.length ? `<div class="sl-section-lbl" style="margin-top:12px">${inv.length} Investor${inv.length !== 1 ? 's' : ''}</div>
        ${inv.map(iv => {
          const isLead = relationships.find(r => r.source === iv.id && r.target === entityId)?.is_lead;
          return `<div class="map-co-item"><span>${esc(iv.name)}</span>${isLead ? '<span class="badge-lead">LEAD</span>' : ''}</div>`;
        }).join('')}` : ''}
    `;
  } else {
    const portfolio = relationships.filter(r => r.source === entityId).map(r => entityMap[r.target]).filter(Boolean);
    detail = `
      <div class="sl-section-lbl">${esc(ent.name)}</div>
      <div class="map-item-id" style="margin-bottom:10px">${esc(ent.type || '')}</div>
      ${portfolio.length ? `<div class="sl-section-lbl">${portfolio.length} Portfolio Companies</div>
        ${portfolio.map(c => `
          <div class="map-co-item">
            <span>${esc(c.name)}</span>
            ${sectorBadge(c.sector)}
          </div>`).join('')}` : ''}
    `;
  }

  panelBody.innerHTML = `
    <div class="sl-panel-section">
      <div class="map-detail-header">
        <button id="map-back-btn" class="edfmap-back-btn">← Back</button>
      </div>
      ${detail}
    </div>
  `;

  document.getElementById('map-back-btn')?.addEventListener('click', () => {
    clearMapFilter();
    if (fromIso) showMapCountry(fromIso);
  });
}

function applyMapFilter() {
  const { ui } = AppState;
  const { g: mapGSel, activeFilter: f } = ui.map;
  const bar = document.getElementById('map-filter-bar');

  if (!f) {
    bar.style.display = 'none';
    mapGSel?.selectAll('.map-country').classed('country-dim', false);
    mapGSel?.selectAll('.map-node').classed('node-dim', false).classed('node-focus', false);
    mapGSel?.selectAll('.map-arc').classed('arc-dim', false);
    return;
  }

  bar.style.display = 'flex';
  document.getElementById('map-filter-label').textContent = f.name;

  mapGSel.selectAll('.map-country.has-data')
    .classed('country-dim', d => !f.isos.has(+d.id));

  mapGSel.selectAll('.map-node').each(function(d) {
    const iso = d.iso;
    d3.select(this)
      .classed('node-dim',   !f.isos.has(iso))
      .classed('node-focus',  f.isos.has(iso));
  });

  mapGSel.selectAll('.map-arc').each(function(d) {
    const src = d.src;
    const tgt = d.tgt;
    d3.select(this).classed('arc-dim', !(f.isos.has(src) && f.isos.has(tgt)));
  });
}
