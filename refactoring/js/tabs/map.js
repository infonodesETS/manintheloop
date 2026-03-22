'use strict';

import { AppState } from '../state.js';
import { esc, sectorBadge } from '../helpers.js';
import { getParams, setParams } from '../url.js';

// Wikidata country name → ISO numeric (world-atlas format)
const WD_TO_ISO = {
  'United States':        840,
  'Germany':              276,
  'United Kingdom':       826,
  'France':               250,
  'Israel':               376,
  'Sweden':               752,
  'Norway':               578,
  'Finland':              246,
  'Denmark':              208,
  'Netherlands':          528,
  'Belgium':              56,
  'Switzerland':          756,
  'Austria':              40,
  'Italy':                380,
  'Spain':                724,
  'Poland':               616,
  'Czech Republic':       203,
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
  'Japan':                392,
  'South Korea':          410,
  'Australia':            36,
  'Canada':               124,
  'Brazil':               76,
  'South Africa':         710,
  'Singapore':            702,
  'United Arab Emirates': 784,
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

const ISO_TO_NAME = Object.fromEntries(Object.entries(WD_TO_ISO).map(([k, v]) => [v, k]));

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
  const p = getParams(); delete p.country; setParams(p);
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
    if (!mapState.countryData[iso]) mapState.countryData[iso] = { name: country, companies: [] };
    mapState.countryData[iso].companies.push(c);
  });

  // Build arc data: for each investor, find countries of investees
  const invCountries = {};
  relationships.forEach(rel => {
    const comp = entityMap[rel.target];
    if (!comp) return;
    const country = comp.sources?.infonodes?.country || comp.sources?.wikidata?.country;
    if (!country) return;
    const iso = WD_TO_ISO[country];
    if (!iso) return;
    if (!invCountries[rel.source]) invCountries[rel.source] = new Set();
    invCountries[rel.source].add(iso);
  });

  const pairWeight = {};
  Object.values(invCountries).forEach(isoSet => {
    const arr = [...isoSet];
    for (let i = 0; i < arr.length; i++) {
      for (let j = i + 1; j < arr.length; j++) {
        const key = [arr[i], arr[j]].sort().join('-');
        pairWeight[key] = (pairWeight[key] || 0) + 1;
      }
    }
  });

  mapState.arcData = Object.entries(pairWeight).map(([key, weight]) => {
    const [a, b] = key.split('-').map(Number);
    return { source_iso: a, target_iso: b, weight };
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
  const maxCount = Math.max(...Object.values(mapState.countryData).map(d => d.companies.length), 1);
  const rScale = d3.scaleSqrt().domain([0, maxCount]).range([4, 22]);

  Object.entries(mapState.countryData).forEach(([iso, cd]) => {
    iso = +iso;
    const c = mapState.centroids[iso];
    if (!c) return;
    const r = rScale(cd.companies.length);
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
      .text(`${cd.name}: ${cd.companies.length} companies`);

    if (r >= 8) {
      const lblDatum = { cy: c[1], baseR: r };
      nodeLayer.append('text')
        .datum(lblDatum)
        .attr('class', 'map-label')
        .attr('x', c[0]).attr('y', c[1] + r + 10)
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
      const cy    = d.cy;
      const baseR = d.baseR;
      d3.select(this)
        .attr('font-size', 11 / k)
        .attr('y', cy + baseR / k + 10 / k);
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
}

function drawArcs(layer) {
  const mapState = AppState.ui.map;
  if (!mapState.arcData.length) return;
  const maxW = Math.max(...mapState.arcData.map(d => d.weight), 1);
  const strokeScale  = d3.scaleLinear().domain([1, maxW]).range([1, 4]);
  const opacityScale = d3.scaleLinear().domain([1, maxW]).range([0.45, 0.85]);

  mapState.arcData.forEach(arc => {
    const s = mapState.centroids[arc.source_iso];
    const t = mapState.centroids[arc.target_iso];
    if (!s || !t) return;
    const mx = (s[0] + t[0]) / 2;
    const my = (s[1] + t[1]) / 2 - Math.hypot(t[0] - s[0], t[1] - s[1]) * 0.3;
    const sw = strokeScale(arc.weight);
    // Store baseSw as datum property for zoom handler
    const arcDatum = { src: arc.source_iso, tgt: arc.target_iso, baseSw: sw };
    layer.append('path')
      .datum(arcDatum)
      .attr('class', 'map-arc')
      .attr('data-src', arc.source_iso)
      .attr('data-tgt', arc.target_iso)
      .attr('d', `M${s[0]},${s[1]} Q${mx},${my} ${t[0]},${t[1]}`)
      .attr('stroke-width', sw)
      .attr('stroke-opacity', opacityScale(arc.weight));
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

  const sectorCount = {};
  cd.companies.forEach(c => {
    const s = c.sector || 'Other';
    sectorCount[s] = (sectorCount[s] || 0) + 1;
  });

  const invMap2 = {};
  relationships.forEach(rel => {
    const comp = entityMap[rel.target];
    if (comp && (comp.sources?.infonodes?.country === cd.name || comp.sources?.wikidata?.country === cd.name)) {
      const inv = entityMap[rel.source];
      if (inv && !invMap2[rel.source]) invMap2[rel.source] = inv.name;
    }
  });
  const invArr = Object.entries(invMap2);

  document.getElementById('map-panel-title').textContent = cd.name;
  document.getElementById('map-panel-body').innerHTML = `
    <div class="sl-panel-section">
      <div class="sl-section-lbl">${cd.companies.length} Companies</div>
      ${cd.companies.map(c => `
        <div class="map-co-item clickable" data-action="filterMapByEntity" data-id="${esc(c.id)}">
          <span>${esc(c.name)}</span>
          ${sectorBadge(c.sector)}
        </div>`).join('')}
    </div>
    <div class="sl-panel-section">
      <div class="sl-section-lbl">By Sector</div>
      ${Object.entries(sectorCount).sort((a, b) => b[1] - a[1]).map(([s, n]) => `
        <div class="map-co-item">
          <span>${sectorBadge(s)}</span>
          <span class="map-item-count">${n}</span>
        </div>`).join('')}
    </div>
    ${invArr.length ? `<div class="sl-panel-section">
      <div class="sl-section-lbl">${invArr.length} Active Investors</div>
      ${invArr.slice(0, 25).map(([id, name]) => `
        <div class="map-co-item clickable" data-action="filterMapByEntity" data-id="${esc(id)}">
          <span>${esc(name)}</span>
          <span class="map-item-id">${id}</span>
        </div>`).join('')}
      ${invArr.length > 25 ? `<div class="map-item-more">+${invArr.length - 25} more</div>` : ''}
    </div>` : ''}
  `;

  document.getElementById('map-panel-body').querySelectorAll('[data-action="filterMapByEntity"]').forEach(el => {
    el.addEventListener('click', () => filterMapByEntity(el.dataset.id));
  });

  document.getElementById('map-panel').classList.remove('d-none');
  setParams({ ...getParams(), country: cd.name });
}

function filterMapByEntity(entityId) {
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
    relationships.filter(r => r.target === entityId).forEach(rel => {
      relationships.filter(r2 => r2.source === rel.source).forEach(rel2 => {
        const comp2 = entityMap[rel2.target];
        if (!comp2) return;
        const c2 = comp2.sources?.infonodes?.country || comp2.sources?.wikidata?.country;
        const iso2 = WD_TO_ISO[c2];
        if (iso2) activeISOs.add(iso2);
      });
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
