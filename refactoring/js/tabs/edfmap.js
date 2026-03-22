'use strict';

import { loadEdfCalls } from '../edf-data.js';

// ── Country name → ISO numeric (world-atlas format) ──────────────────────────
const COUNTRY_TO_ISO = {
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

// ── Module-level state ───────────────────────────────────────────────────────
const ms = {
  countryData:       {},  // iso → { name, orgs: [] }
  projectPartnersMap:{},  // projId → Set<iso>
  orgProjectsMap:    {},  // orgKey → [{ projId, partnerIsos: Set<iso>, projAcronym, projTitle, projUrl, callId, role, euContrib }]
  arcData:           [],  // default all-projects arcs
  centroids:         {},
  projection:        null,
  svg:               null,
  g:                 null,
  zoom:              null,
  showArcs:          true,
  activeFilter:      null, // { orgKey, orgName, activeIsos: Set<iso>, pairSet: Set<string> }
};

// ── Helpers ──────────────────────────────────────────────────────────────────
function esc(s) { return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function fmtEuro(n) {
  if (!n) return '—';
  const v = Math.round(n);
  if (v >= 1e9) return `€${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `€${Math.round(v / 1e6)}M`;
  if (v >= 1e3) return `€${Math.round(v / 1e3)}K`;
  return `€${v.toLocaleString()}`;
}

function setStatus(msg) {
  const el = document.getElementById('edfmap-status');
  if (el) el.textContent = msg;
}

// ── Data builder ─────────────────────────────────────────────────────────────
function buildData(callsMap) {
  const countryData        = {};
  const projectPartnersMap = {};

  for (const call of Object.values(callsMap)) {
    for (const proj of (call.projects || [])) {
      if (!proj.participants?.length) continue;

      const projId   = proj.project_id || `${call.identifier}|${proj.acronym || proj.title || ''}`;
      const projIsos = new Set();

      for (const pt of proj.participants) {
        const iso = COUNTRY_TO_ISO[pt.country];
        if (!iso) continue;
        projIsos.add(iso);

        if (!countryData[iso]) countryData[iso] = { name: pt.country, orgs: new Map() };
        const key = pt.pic || `${pt.organization_name}||${pt.country || ''}`;

        if (!countryData[iso].orgs.has(key)) {
          countryData[iso].orgs.set(key, {
            key,
            name:          pt.organization_name || '—',
            pic:           pt.pic || null,
            eu_url:        pt.eu_url || null,
            eu_total:      0,
            participations:0,
            projects:      [],
          });
        }
        const org = countryData[iso].orgs.get(key);
        org.eu_total += parseFloat(pt.eu_contribution) || 0;
        org.participations++;
        org.projects.push({
          projId,
          projAcronym: proj.acronym || '',
          projTitle:   proj.title   || '—',
          callId:      call.identifier,
          role:        pt.role || 'participant',
          euContrib:   parseFloat(pt.eu_contribution) || 0,
          projUrl:     proj.url || null,
        });
      }

      if (projIsos.size > 0) projectPartnersMap[projId] = projIsos;
    }
  }

  // Convert org Maps to sorted arrays
  for (const iso of Object.keys(countryData)) {
    countryData[iso].orgs = [...countryData[iso].orgs.values()]
      .sort((a, b) => b.eu_total - a.eu_total);
  }

  // Build orgProjectsMap for click-to-filter
  const orgProjectsMap = {};
  for (const cd of Object.values(countryData)) {
    for (const org of cd.orgs) {
      orgProjectsMap[org.key] = org.projects.map(p => ({
        ...p,
        partnerIsos: projectPartnersMap[p.projId] || new Set(),
      }));
    }
  }

  // Build default arc data (all cross-border project pairs, weighted by co-project count)
  const pairWeight = {};
  for (const isoSet of Object.values(projectPartnersMap)) {
    const arr = [...isoSet];
    for (let i = 0; i < arr.length; i++) {
      for (let j = i + 1; j < arr.length; j++) {
        const k = [arr[i], arr[j]].sort().join('-');
        pairWeight[k] = (pairWeight[k] || 0) + 1;
      }
    }
  }

  ms.countryData        = countryData;
  ms.projectPartnersMap = projectPartnersMap;
  ms.orgProjectsMap     = orgProjectsMap;
  ms.arcData = Object.entries(pairWeight).map(([k, weight]) => {
    const [a, b] = k.split('-').map(Number);
    return { source_iso: a, target_iso: b, weight };
  });
}

// ── Map renderer ─────────────────────────────────────────────────────────────
function drawMap(world) {
  const el = document.getElementById('edfmap-svg');
  const W  = el.clientWidth  || 900;
  const H  = el.clientHeight || 500;

  ms.projection = d3.geoNaturalEarth1()
    .scale(W / 6.2)
    .translate([W / 2 - 100, H / 2 + 50]);

  const path = d3.geoPath().projection(ms.projection);

  ms.svg = d3.select('#edfmap-svg');
  ms.svg.selectAll('*').remove();
  ms.g = ms.svg.append('g');

  // Graticule
  ms.g.append('path')
    .datum(d3.geoGraticule()())
    .attr('d', path)
    .attr('fill', 'none')
    .attr('stroke', '#1a1a1a')
    .attr('stroke-width', 0.3);

  // Countries — build centroids using largest polygon to avoid overseas-territory distortion
  const countries = topojson.feature(world, world.objects.countries);
  ms.centroids = {};
  countries.features.forEach(f => {
    let c;
    if (f.geometry && f.geometry.type === 'MultiPolygon') {
      let maxArea = -1, mainPoly = null;
      for (const ring of f.geometry.coordinates) {
        const poly = { type: 'Feature', geometry: { type: 'Polygon', coordinates: ring } };
        const area = d3.geoArea(poly);
        if (area > maxArea) { maxArea = area; mainPoly = poly; }
      }
      c = mainPoly ? path.centroid(mainPoly) : path.centroid(f);
    } else {
      c = path.centroid(f);
    }
    if (c && !isNaN(c[0]) && !isNaN(c[1])) ms.centroids[+f.id] = c;
  });

  ms.g.selectAll('.edfmap-country')
    .data(countries.features)
    .join('path')
    .attr('class', d => 'edfmap-country' + (ms.countryData[+d.id] ? ' has-data' : ''))
    .attr('d', path)
    .on('click', (e, d) => {
      const iso = +d.id;
      if (ms.countryData[iso]) showCountry(iso);
    })
    .append('title')
    .text(d => {
      const iso = +d.id;
      const cd  = ms.countryData[iso];
      return cd ? `${cd.name} — ${cd.orgs.length} organisations` : `ISO ${iso}`;
    });

  // Arc layer
  const arcLayer = ms.g.append('g').attr('id', 'edfmap-arc-layer');
  drawArcs(arcLayer, ms.arcData);

  // Country nodes
  const nodeLayer = ms.g.append('g').attr('id', 'edfmap-node-layer');
  const maxCount  = Math.max(...Object.values(ms.countryData).map(d => d.orgs.length), 1);
  const rScale    = d3.scaleSqrt().domain([0, maxCount]).range([3, 12]);

  Object.entries(ms.countryData).forEach(([isoStr, cd]) => {
    const iso = +isoStr;
    const c   = ms.centroids[iso];
    if (!c) return;
    const r = rScale(cd.orgs.length);

    nodeLayer.append('circle')
      .datum({ iso, baseR: r })
      .attr('class', 'edfmap-node')
      .attr('data-iso', iso)
      .attr('cx', c[0]).attr('cy', c[1])
      .attr('r', r)
      .on('click', e => { e.stopPropagation(); showCountry(iso); })
      .append('title')
      .text(`${cd.name}: ${cd.orgs.length} organisations`);

    if (r >= 9) {
      nodeLayer.append('text')
        .datum({ cy: c[1], baseR: r })
        .attr('class', 'edfmap-label')
        .style('font-size', '16px')
        .attr('x', c[0]).attr('y', c[1] + r + 10)
        .text(cd.name);
    }
  });

  // Zoom — keep nodes/labels/arcs at constant visual size
  ms.zoom = d3.zoom().scaleExtent([0.5, 12]).on('zoom', e => {
    ms.g.attr('transform', e.transform);
    const k = e.transform.k;
    ms.g.selectAll('.edfmap-node').each(function(d) {
      d3.select(this).attr('r', d.baseR / k);
    });
    ms.g.selectAll('.edfmap-label').each(function(d) {
      d3.select(this).style('font-size', (16 / k) + 'px').attr('y', d.cy + d.baseR / k + 10 / k);
    });
    ms.g.selectAll('.edfmap-arc').each(function(d) {
      d3.select(this).attr('stroke-width', d.baseSw / k);
    });
    // Live position display for calibration
    const posEl = document.getElementById('edfmap-position');
    if (posEl) posEl.textContent =
      `tx:${e.transform.x.toFixed(0)} ty:${e.transform.y.toFixed(0)} k:${k.toFixed(3)}`;
  });
  ms.svg.call(ms.zoom);
  fitEdfMapView(W, H);
  document.getElementById('edfmap-filter-bar').style.display = 'none'; // hide on init

  // Status
  const coCount  = Object.keys(ms.countryData).length;
  const totOrgs  = Object.values(ms.countryData).reduce((s, d) => s + d.orgs.length, 0);
  setStatus(`${coCount} countries · ${totOrgs} organisations · ${ms.arcData.length} cross-border project pairs`);
}

function drawArcs(layer, arcs) {
  if (!arcs.length) return;
  const maxW = Math.max(...arcs.map(d => d.weight), 1);
  const strokeScale  = d3.scaleLinear().domain([1, maxW]).range([0.3, 1.2]);
  const opacityScale = d3.scaleLinear().domain([1, maxW]).range([0.35, 0.75]);

  arcs.forEach(arc => {
    const s = ms.centroids[arc.source_iso];
    const t = ms.centroids[arc.target_iso];
    if (!s || !t) return;
    const mx  = (s[0] + t[0]) / 2;
    const my  = (s[1] + t[1]) / 2 - Math.hypot(t[0] - s[0], t[1] - s[1]) * 0.3;
    const sw  = strokeScale(arc.weight);
    layer.append('path')
      .datum({ src: arc.source_iso, tgt: arc.target_iso, baseSw: sw })
      .attr('class', 'edfmap-arc')
      .attr('d', `M${s[0]},${s[1]} Q${mx},${my} ${t[0]},${t[1]}`)
      .attr('stroke-width', sw)
      .attr('stroke-opacity', opacityScale(arc.weight));
  });
}

// ── Country panel ─────────────────────────────────────────────────────────────
function showCountry(iso) {
  const cd = ms.countryData[iso];
  if (!cd) return;

  // Clear any active org filter
  ms.activeFilter = null;
  document.getElementById('edfmap-filter-bar').style.display = 'none';

  // Highlight selected country, dim others that have data
  ms.g.selectAll('.edfmap-country')
    .classed('selected',          d => +d.id === iso)
    .classed('edfmap-country-dim', d => +d.id !== iso && !!ms.countryData[+d.id]);

  ms.g.selectAll('.edfmap-node')
    .classed('edfmap-node-dim',   d => d.iso !== iso)
    .classed('edfmap-node-focus', d => d.iso === iso);

  // Show only arcs that touch this country
  ms.g.selectAll('.edfmap-arc')
    .classed('edfmap-arc-dim', d => d.src !== iso && d.tgt !== iso);

  document.getElementById('edfmap-panel-title').textContent = cd.name;
  document.getElementById('edfmap-panel-body').innerHTML = `
    <div class="sl-panel-section">
      <div class="sl-section-lbl">${cd.orgs.length} Organisations</div>
      <input id="edfmap-org-filter" class="edfmap-org-filter-input" type="text" placeholder="Filter organisations…" autocomplete="off">
      <div id="edfmap-org-list">
        ${cd.orgs.map(o => `
          <div class="edfmap-co-item clickable" data-orgkey="${esc(o.key)}" data-name="${esc(o.name.toLowerCase())}">
            <span class="edfmap-co-name">${esc(o.name)}</span>
            <span class="edfmap-co-meta">${fmtEuro(o.eu_total)}</span>
          </div>`).join('')}
      </div>
    </div>
  `;

  document.getElementById('edfmap-org-filter').addEventListener('input', function () {
    const q = this.value.toLowerCase();
    document.getElementById('edfmap-org-list').querySelectorAll('.edfmap-co-item').forEach(el => {
      el.style.display = el.dataset.name.includes(q) ? '' : 'none';
    });
  });

  document.getElementById('edfmap-panel-body')
    .querySelectorAll('.edfmap-co-item.clickable')
    .forEach(el => {
      el.addEventListener('click', () => filterByOrg(el.dataset.orgkey, cd.name));
    });

  document.getElementById('edfmap-panel').classList.remove('d-none');
}

// ── Org filter ────────────────────────────────────────────────────────────────
function filterByOrg(orgKey, countryName) {
  const orgProjects = ms.orgProjectsMap[orgKey];
  if (!orgProjects?.length) return;

  // Find org name and ISO
  let orgName = orgKey;
  let orgIso  = null;
  for (const [isoStr, cd] of Object.entries(ms.countryData)) {
    const found = cd.orgs.find(o => o.key === orgKey);
    if (found) { orgName = found.name; orgIso = +isoStr; break; }
  }

  // Collect partner ISOs
  const partnerIsos = new Set();
  for (const p of orgProjects) {
    for (const i of p.partnerIsos) {
      if (i !== orgIso) partnerIsos.add(i);
    }
  }
  const activeIsos = new Set([...partnerIsos, ...(orgIso ? [orgIso] : [])]);

  ms.activeFilter = { orgKey, orgName, activeIsos, orgIso, partnerIsos };
  applyFilter();

  // Drill-down: replace sidebar with org project list
  const panelBody = document.getElementById('edfmap-panel-body');
  panelBody.innerHTML = `
    <div class="sl-panel-section">
      <div class="edfmap-org-header">
        <div class="sl-section-lbl">${esc(orgName)}</div>
        <button id="edfmap-back-btn" class="edfmap-back-btn">← Back</button>
      </div>
      <div class="edfmap-org-meta">
        ${partnerIsos.size} partner countries · ${orgProjects.length} project${orgProjects.length !== 1 ? 's' : ''}
      </div>
      ${orgProjects.map(p => `
        <div class="edfmap-proj-item">
          <div class="edfmap-proj-acronym">${esc(p.projAcronym || p.projTitle)}</div>
          <div class="edfmap-proj-title">${esc(p.projTitle)}</div>
          <div class="edfmap-proj-meta">
            <span class="edfmap-role-badge ${p.role === 'coordinator' ? 'coord' : 'part'}">${p.role}</span>
            <span>${fmtEuro(p.euContrib)}</span>
            ${p.projUrl ? `<a href="${esc(p.projUrl)}" target="_blank" class="edfmap-eu-link">↗ EU</a>` : ''}
          </div>
          <div class="edfmap-proj-partners">
            Partners: ${[...p.partnerIsos].map(i => ms.countryData[i]?.name || i).join(', ')}
          </div>
        </div>`).join('')}
    </div>
  `;

  document.getElementById('edfmap-back-btn')?.addEventListener('click', () => {
    for (const [isoStr, cd] of Object.entries(ms.countryData)) {
      if (cd.orgs.find(o => o.key === orgKey)) {
        clearEdfMapFilter();
        showCountry(+isoStr);
        return;
      }
    }
    clearEdfMapFilter();
  });
}

// ── Filter application ────────────────────────────────────────────────────────
function applyFilter() {
  const f   = ms.activeFilter;
  const bar = document.getElementById('edfmap-filter-bar');

  if (!f) {
    bar.style.display = 'none';
    ms.g?.selectAll('.edfmap-country').classed('edfmap-country-dim', false);
    ms.g?.selectAll('.edfmap-node').classed('edfmap-node-dim', false).classed('edfmap-node-focus', false);
    ms.g?.selectAll('.edfmap-arc').classed('edfmap-arc-dim', false);
    return;
  }

  bar.style.display = 'flex';
  document.getElementById('edfmap-filter-label').textContent = f.orgName;

  ms.g.selectAll('.edfmap-country.has-data')
    .classed('edfmap-country-dim', d => !f.activeIsos.has(+d.id));

  ms.g.selectAll('.edfmap-node').each(function(d) {
    d3.select(this)
      .classed('edfmap-node-dim',   !f.activeIsos.has(d.iso))
      .classed('edfmap-node-focus',  f.activeIsos.has(d.iso));
  });

  // Show only arcs from org's own country to its partner countries
  ms.g.selectAll('.edfmap-arc').each(function(d) {
    const connected = f.orgIso != null && (
      (d.src === f.orgIso && f.partnerIsos.has(d.tgt)) ||
      (d.tgt === f.orgIso && f.partnerIsos.has(d.src))
    );
    d3.select(this).classed('edfmap-arc-dim', !connected);
  });
}

// ── Exported controls ─────────────────────────────────────────────────────────
function resetVisuals() {
  ms.g?.selectAll('.edfmap-country')
    .classed('selected', false)
    .classed('edfmap-country-dim', false);
  ms.g?.selectAll('.edfmap-node')
    .classed('edfmap-node-dim', false)
    .classed('edfmap-node-focus', false);
  ms.g?.selectAll('.edfmap-arc')
    .classed('edfmap-arc-dim', false);
  document.getElementById('edfmap-filter-bar').style.display = 'none';
}

export function clearEdfMapFilter() {
  ms.activeFilter = null;
  resetVisuals();
}

export function closeEdfMapPanel() {
  document.getElementById('edfmap-panel').classList.add('d-none');
  ms.activeFilter = null;
  resetVisuals();
}

export function resetEdfMapZoom() {
  if (!ms.svg || !ms.zoom) return;
  const el = document.getElementById('edfmap-svg');
  const W  = el.clientWidth  || 900;
  const H  = el.clientHeight || 500;
  fitEdfMapView(W, H, true);
}

// Zoom factor applied on top of the data-fit scale (>1 = zoom in).
// 2.5 ≈ Europe-focused: fits all EDF nodes (mostly Europe) then zooms in.
const FOCUS_FACTOR = 0.9;

function fitEdfMapView(W, H, animated = false) {
  if (!ms.zoom || !ms.countryData || !ms.centroids) return;

  // Compute bounds from centroids of countries with data — excludes world map paths
  const pts = Object.keys(ms.countryData).map(iso => ms.centroids[+iso]).filter(Boolean);
  if (!pts.length) return;

  const xs   = pts.map(p => p[0]);
  const ys   = pts.map(p => p[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const cx   = (minX + maxX) / 2;
  const cy   = (minY + maxY) / 2;
  const dx   = maxX - minX;
  const dy   = maxY - minY;

  const scale = Math.max(0.5, Math.min(8,
    FOCUS_FACTOR * 0.85 / Math.max(dx / W, dy / H)
  ));
  const tx = W / 2 - scale * cx;
  const ty = H / 2 - scale * cy;
  const t  = d3.zoomIdentity.translate(tx, ty).scale(scale);

  if (animated) ms.svg.transition().duration(500).call(ms.zoom.transform, t);
  else          ms.svg.call(ms.zoom.transform, t);
}

export function toggleEdfMapArcs(show) {
  ms.showArcs = show;
  const layer = document.getElementById('edfmap-arc-layer');
  if (layer) layer.style.display = show ? '' : 'none';
}

// ── Entry point ───────────────────────────────────────────────────────────────
export default async function initEdfMap() {
  setStatus('Loading EDF data…');
  try {
    const data = await loadEdfCalls();
    buildData(data.calls);
    setStatus('Loading world map…');
    const world = await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json').then(r => r.json());
    drawMap(world);
  } catch (err) {
    setStatus('Failed to load: ' + err.message);
  }
}
