'use strict';

import { AppState } from '../state.js';
import { esc, fmtFunding, sectorBadge, typeBadge, dualBadge, tip, hideTip } from '../helpers.js';

// Live D3 selections — updated by each build function so search can run without rebuilding
let _nd = null, _lk = null;
// Tooltip pin state — when true, mouseout does not close the tooltip
let _tipPinned = false;

export function showGraphHelp() {
  const panel = document.getElementById('graph-detail');
  document.getElementById('graph-help').style.display = '';
  document.getElementById('graph-inner').style.display = 'none';
  document.getElementById('graph-detail-title').textContent = 'How to explore';
  document.getElementById('graph-detail-close').style.display = 'none';
  panel.classList.add('open');
}

export default function initGraph() {
  // Apply default sector on first load
  const s = AppState.ui.graph.sector;
  AppState.COMPANIES = s === 'all' ? [...AppState.ALL_COMPANIES] : AppState.ALL_COMPANIES.filter(c => c.sector === s);
  buildGraphView();
  // Dismiss hint immediately if a non-all sector is pre-selected
  if (s !== 'all') document.getElementById('graph-hint')?.classList.add('hidden');
  showGraphHelp();
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && AppState.ui.currentTab === 'graph') closeGraphDetail();
  });
}

export function setGraphSearch(q) {
  AppState.ui.graph.search = q;
  applyGraphSearch();
}

export function setLeadOnly(v) {
  AppState.ui.graph.leadOnly = v;
  buildGraphView();
}

export function setHideIsolated(v) {
  AppState.ui.graph.hideIsolated = v;
  buildGraphView();
}

export function setShowCompanies(v) {
  AppState.ui.graph.showCompanies = v;
  buildGraphView();
}

export function setShowInvestors(v) {
  AppState.ui.graph.showInvestors = v;
  buildGraphView();
}

function applyGraphSearch() {
  if (!_nd || !_lk) return;
  const q = AppState.ui.graph.search.trim().toLowerCase();
  if (!q) { _nd.classed('ghl', false).classed('gdim', false); _lk.classed('ghl', false).classed('gdim', false); return; }

  const matchIds = new Set();
  _nd.each(d => { if ((d.id || '').toLowerCase().includes(q)) matchIds.add(d.id); });

  const connectedIds = new Set(matchIds);
  AppState.derived.raw.forEach(([c, i]) => {
    if (matchIds.has(c)) connectedIds.add(i);
    if (matchIds.has(i)) connectedIds.add(c);
  });

  _nd.classed('ghl', d => connectedIds.has(d.id));
  _lk.classed('ghl', l => {
    const s = l.source.id || l.source, t = l.target.id || l.target;
    return connectedIds.has(s) && connectedIds.has(t) && (matchIds.has(s) || matchIds.has(t));
  });
}

export function closeGraphDetail() {
  _nd?.classed('ghl', false);
  _lk?.classed('ghl', false).attr('stroke-opacity', null);
  showGraphHelp();
}

export function pauseGraph() {
  const { graph } = AppState.ui;
  if (graph.sim)     graph.sim.stop();
  if (graph.simBi)   graph.simBi.stop();
  if (graph.simProj) graph.simProj.stop();
}

export function resumeGraph() {
  const { graph } = AppState.ui;
  if (graph.sim)     graph.sim.restart();
  if (graph.simBi)   graph.simBi.restart();
  if (graph.simProj) graph.simProj.restart();
}

function graphShowPanel(d) {
  const { derived, COMPANIES } = AppState;
  const { companyMap, invMap } = derived;
  const panel = document.getElementById('graph-detail');
  let html = '';

  if (d._gtype === 'investor') {
    const im = invMap[d.id] || invMap[d.entity?.name];
    if (!im) return;
    const portfolioFiltered = im.portfolio.filter(p => COMPANIES.some(c => c.name === p.company?.name));
    const _gTitleEl = document.getElementById('graph-detail-title');
    _gTitleEl.textContent = im.entity.name; _gTitleEl.title = im.entity.name;
    html += typeBadge(im.entity.type);
    const invCountry = im.entity.sources?.wikidata?.country || im.entity.sources?.infonodes?.country || '';
    const pfCountries = [...new Set(portfolioFiltered.map(p => p.company?.sources?.wikidata?.country || p.company?.sources?.infonodes?.country).filter(Boolean))];
    const typeLabel = (im.entity.type || 'investor').replace(/_/g, ' ');
    html += `<p class="gv-context">`;
    html += `<strong>${esc(im.entity.name)}</strong> is a ${esc(typeLabel)}`;
    if (invCountry) html += ` based in <strong>${esc(invCountry)}</strong>`;
    html += `. In the current view it has backed <strong>${portfolioFiltered.length}</strong> compan${portfolioFiltered.length === 1 ? 'y' : 'ies'}`;
    if (pfCountries.length) html += ` across <strong>${pfCountries.length}</strong> countr${pfCountries.length === 1 ? 'y' : 'ies'}`;
    html += `. Highlighted edges connect to its portfolio; shared edges with other investor nodes indicate co-investments.</p>`;
    html += `<div class="dp-inv-meta">${im.total} investments · ${im.leads} lead</div>`;
    html += `<div class="sl-section-lbl">Portfolio (${portfolioFiltered.length})</div><ul class="es-list">`;
    [...portfolioFiltered].sort((a, b) => (b.lead ? 1 : 0) - (a.lead ? 1 : 0)).forEach(p => {
      html += `<li><span title="${esc(p.company?.name)}">${esc(p.company?.name)}</span>${p.lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`;
    });
    html += '</ul>';
    const coSet = {};
    im.portfolio.forEach(p => {
      (p.company?._investors || []).filter(x => x.name !== im.entity.name).forEach(o => {
        coSet[o.name] = (coSet[o.name] || 0) + 1;
      });
    });
    const coList = Object.entries(coSet).sort((a, b) => b[1] - a[1]).slice(0, 6);
    if (coList.length) {
      html += '<div class="sl-section-lbl">Co-investors</div><ul class="es-list">';
      coList.forEach(([n, cnt]) => {
        html += `<li><span title="${esc(n)}">${esc(n)}</span><span class="dp-co-count">${cnt > 1 ? cnt + '×' : ''}</span></li>`;
      });
      html += '</ul>';
    }
  } else {
    const c = companyMap[d.name || d.id];
    if (!c) return;
    const wd = c.sources?.wikidata;
    const cb = c.sources?.crunchbase;
    const _gTitleEl2 = document.getElementById('graph-detail-title');
    _gTitleEl2.textContent = c.name; _gTitleEl2.title = c.name;
    if (c.sector) html += `${sectorBadge(c.sector)} `;
    html += `<span class="badge-type badge-type--company">Manufacturer</span>`;
    if (c.roles?.includes('investor')) html += ` ${dualBadge()}`;
    const country = wd?.country || '';
    const invCountries = [...new Set(
      (c._investors || []).map(x => {
        const im2 = invMap[x.name];
        return im2?.entity?.sources?.wikidata?.country || im2?.entity?.sources?.infonodes?.country;
      }).filter(Boolean)
    )];
    html += `<p class="gv-context">`;
    html += `<strong>${esc(c.name)}</strong> is a company`;
    if (country) html += ` headquartered in <strong>${esc(country)}</strong>`;
    html += `. It has received funding from <strong>${(c._investors || []).length}</strong> investor${(c._investors || []).length === 1 ? '' : 's'}`;
    if (invCountries.length) {
      const shown = invCountries.slice(0, 3).map(esc).join(', ');
      const extra = invCountries.length > 3 ? ` +${invCountries.length - 3} more` : '';
      html += ` from <strong>${shown}${extra}</strong>`;
    }
    html += `. Highlighted edges connect to each investor that backed it.</p>`;
    const inception = wd?.inception ? String(wd.inception).slice(0, 4) : '';
    const meta = [country, inception ? `est. ${inception}` : ''].filter(Boolean).join(' · ');
    if (meta) html += `<div class="dp-co-meta">${esc(meta)}</div>`;
    const funding = cb?.total_funding_usd;
    if (funding) html += `<div class="dp-funding">Funding: <span>${fmtFunding(funding)}</span></div>`;
    const desc = cb?.description || wd?.description;
    if (desc) html += `<div class="dp-desc">${esc(desc.slice(0, 200))}${desc.length > 200 ? '…' : ''}</div>`;
    if (c._investors?.length) {
      html += `<div class="sl-section-lbl">Investors (${c._investors.length})</div><ul class="es-list">`;
      [...c._investors].sort((a, b) => (b.lead ? 1 : 0) - (a.lead ? 1 : 0)).forEach(x => {
        html += `<li><span title="${esc(x.name)}">${esc(x.name)}</span>${x.lead ? '<span class="badge-lead">LEAD</span>' : ''}</li>`;
      });
      html += '</ul>';
    }
  }

  document.getElementById('graph-help').style.display = 'none';
  document.getElementById('graph-inner').style.display = '';
  document.getElementById('graph-detail-close').style.display = '';
  document.getElementById('graph-inner').innerHTML = html;
  panel.classList.add('open');
}

export function setGraphView(v) {
  AppState.ui.graph.view = v;
  ['net', 'bi', 'proj'].forEach(k => document.getElementById('gv-' + k)?.classList.remove('active'));
  document.getElementById('gv-' + { network: 'net', bipartite: 'bi', projection: 'proj' }[v])?.classList.add('active');
  document.getElementById('proj-filter-btns').style.display = v === 'projection' ? 'flex' : 'none';
  buildGraphView();
}

export function setGraphSector(s) {
  AppState.ui.graph.sector = s;
  AppState.COMPANIES = s === 'all' ? [...AppState.ALL_COMPANIES] : AppState.ALL_COMPANIES.filter(c => c.sector === s);
  buildGraphView();
}

export function setProjFilter(f) {
  AppState.ui.graph.projFilter = f;
  document.getElementById('pf-all').classList.toggle('active', f === 'all');
  document.getElementById('pf-multi').classList.toggle('active', f === 'multi');
  buildGraphView();
}

function buildGraphView() {
  _tipPinned = false;
  hideTip();
  const { graph } = AppState.ui;
  if (graph.sim)    graph.sim.stop();
  if (graph.simBi)  graph.simBi.stop();
  if (graph.simProj) graph.simProj.stop();

  if      (graph.view === 'network')    buildNetwork();
  else if (graph.view === 'bipartite')  buildBipartite();
  else if (graph.view === 'projection') buildProjection();
}

// Maps entity type to short CSS key for gbadge coloring
function typeKey(t) {
  if (t === 'government_agency') return 'govt';
  if (t === 'institution') return 'inst';
  return t || 'fund'; // fund | bank | inst | govt
}

function gR_inv(d) { return 5 + Math.sqrt(d.total || 1) * 4; }
function gR_co(d)  { return 4 + Math.sqrt((d._investors || []).length) * 2; }
function gR(d)     { return d._gtype === 'investor' ? gR_inv(d) : gR_co(d); }

function appendNodeShapes(nd) {
  // Companies → circles
  nd.filter(d => d._gtype === 'company')
    .append('circle').attr('r', gR);
  // Investors → squares (rect)
  nd.filter(d => d._gtype === 'investor')
    .append('rect')
    .attr('width',  d => gR_inv(d) * 2)
    .attr('height', d => gR_inv(d) * 2)
    .attr('x', d => -gR_inv(d))
    .attr('y', d => -gR_inv(d))
    .attr('rx', 2);
  // Dual-role companies → star overlay
  nd.filter(d => d._gtype === 'company' && d.roles?.includes('investor'))
    .append('text').attr('class', 'gstar')
    .attr('text-anchor', 'middle').attr('dy', '0.35em').text('★');
  // Labels for all nodes
  nd.append('text').attr('class', 'glabel')
    .attr('dy', d => (d._gtype === 'investor' ? gR_inv(d) : gR_co(d)) + 11)
    .attr('text-anchor', 'middle')
    .text(d => d.id.length > 15 ? d.id.slice(0, 14) + '…' : d.id);
  // Count badge for investors with portfolio > 1
  nd.filter(d => d._gtype === 'investor' && d.total > 1)
    .append('text')
    .attr('class', d => `gbadge gbadge--${typeKey(d.type)}`)
    .attr('dy', 4).attr('text-anchor', 'middle').text(d => d.total);
}

function setupGraphSvg() {
  const svg = d3.select('#graph-svg');
  svg.selectAll('*').remove();
  const svgEl = document.getElementById('graph-svg');
  const W = svgEl.clientWidth;
  const H = svgEl.clientHeight;
  const g = svg.append('g');
  const zoom = d3.zoom().scaleExtent([0.05, 5]).on('zoom', e => g.attr('transform', e.transform));
  svg.call(zoom);
  AppState.ui.graph.zoom = zoom;
  return { svg, g, W, H };
}

// Compute a zoom transform that fits all nodes in the viewport (bounding-box fit).
// Mirrors map.js computeTransformForISOs logic.
function computeGraphFit(nodes, W, H, pad = 50) {
  const pts = nodes.filter(n => n.x != null && n.y != null);
  if (pts.length < 2) return d3.zoomIdentity;
  const xs = pts.map(n => n.x), ys = pts.map(n => n.y);
  const minX = Math.min(...xs) - pad, maxX = Math.max(...xs) + pad;
  const minY = Math.min(...ys) - pad, maxY = Math.max(...ys) + pad;
  const k = Math.min(W / (maxX - minX), H / (maxY - minY), 3);
  return d3.zoomIdentity
    .translate(W / 2 - k * (minX + maxX) / 2, H / 2 - k * (minY + maxY) / 2)
    .scale(k);
}

function applyDefaultTransform(svg, zoom, t, animate = false) {
  AppState.ui.graph.defaultTransform = t;
  if (animate) svg.transition().duration(500).call(zoom.transform, t);
  else svg.call(zoom.transform, t);
}

function gOnClick(e, d, nd, lk) {
  e.stopPropagation();
  document.getElementById('graph-hint')?.classList.add('hidden');
  // Tooltip pinned on click — stays open until another node is clicked or background is clicked
  _tipPinned = true;
  if (d._gtype === 'investor') tip(e, d.entity?.name || d.name, `${d.total} investments · ${d.leads} lead`, d.portfolio?.slice(0, 3).map(p => p.company?.name).join(', '));
  else tip(e, d.name, `${(d._investors || []).length} investors`, d.sector || '');
  const connected = new Set([d.id]);
  AppState.derived.raw.forEach(([c, i]) => {
    if (c === d.id || i === d.id) { connected.add(c); connected.add(i); }
  });
  nd.classed('ghl',  n => connected.has(n.id));
  nd.classed('gdim', n => !connected.has(n.id));
  lk.classed('ghl',  l => {
    const s = l.source.id || l.source, t = l.target.id || l.target;
    return connected.has(s) && connected.has(t);
  });
  lk.classed('gdim', l => {
    const s = l.source.id || l.source, t = l.target.id || l.target;
    return !(connected.has(s) && connected.has(t));
  });
  graphShowPanel(d);
}

function buildNetwork() {
  const { COMPANIES, INVESTORS, derived, ui } = AppState;
  const { raw } = derived;
  const { svg, g, W, H } = setupGraphSvg();
  const cx = W / 2, cy = H / 2;
  const { leadOnly, hideIsolated, showCompanies, showInvestors } = ui.graph;

  let links = raw
    .filter(([c]) => COMPANIES.some(x => x.name === c))
    .map(([c, i, lead]) => ({ source: i, target: c, lead }));
  if (leadOnly) links = links.filter(l => l.lead);
  if (!showCompanies) links = [];
  if (!showInvestors) links = [];

  const activeIds = hideIsolated ? new Set(links.flatMap(l => [l.source, l.target])) : null;

  let coNodes = !showCompanies ? [] : COMPANIES
    .filter(c => !activeIds || activeIds.has(c.name))
    .map((c, i, arr) => {
      const a = (i / arr.length) * 2 * Math.PI;
      const Rco = Math.min(W, H) * 0.15;
      return { ...c, id: c.name, _gtype: 'company', x: cx + Rco * Math.cos(a), y: cy + Rco * Math.sin(a) };
    });
  const Rco = Math.min(W, H) * 0.15, Rinv = Math.min(W, H) * 0.42;
  let invNodes = !showInvestors ? [] : INVESTORS
    .filter(im => im.portfolio.some(p => COMPANIES.some(c => c.name === p.company?.name)))
    .filter(im => !activeIds || activeIds.has(im.entity.name))
    .map((im, i, arr) => {
      const a = (i / arr.length) * 2 * Math.PI;
      return { ...im.entity, id: im.entity.name, _gtype: 'investor', total: im.total, leads: im.leads, portfolio: im.portfolio, x: cx + Rinv * Math.cos(a), y: cy + Rinv * Math.sin(a) };
    });

  const nodeIds = new Set([...coNodes, ...invNodes].map(n => n.id));
  links = links.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));
  const nodes = [...coNodes, ...invNodes];

  // Apply initial bounding-box fit from ring positions
  applyDefaultTransform(svg, AppState.ui.graph.zoom, computeGraphFit(nodes, W, H));

  const lkG = g.append('g'), ndG = g.append('g');
  const lk = lkG.selectAll('line').data(links).join('line')
    .attr('class', d => `glink${d.lead ? ' lead' : ''}`)
    .attr('stroke-width', d => d.lead ? 1.5 : 0.7);

  const nd = ndG.selectAll('g').data(nodes, d => d.id).join('g')
    .attr('class', d => d._gtype === 'investor'
      ? `gnode-inv gnode-inv--${d.type || 'fund'}`
      : `gnode-co gnode-co--${d.sector || 'default'}`)
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) ui.graph.sim.alphaTarget(0.1).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end',   (e, d) => { if (!e.active) ui.graph.sim.alphaTarget(0); d.fx = null; d.fy = null; }))
    .on('click', (e, d) => gOnClick(e, d, nd, lk))
    .on('mouseover', (e, d) => {
      if (_tipPinned) return;
      if (d._gtype === 'investor') tip(e, d.entity?.name || d.name, `${d.total} investments · ${d.leads} lead`, d.portfolio.slice(0, 3).map(p => p.company?.name).join(', '));
      else tip(e, d.name, `${(d._investors || []).length} investors`, d.sector || '');
    })
    .on('mouseout', () => { if (!_tipPinned) hideTip(); });

  appendNodeShapes(nd);

  svg.on('click', () => {
    nd.classed('ghl', false).classed('gdim', false); lk.classed('ghl', false).classed('gdim', false).attr('stroke-opacity', null);
    _tipPinned = false;
    hideTip();
    closeGraphDetail();
    const t = AppState.ui.graph.defaultTransform;
    const z = AppState.ui.graph.zoom;
    if (t && z) svg.transition().duration(500).call(z.transform, t);
  });

  _nd = nd; _lk = lk;
  applyGraphSearch();

  ui.graph.sim = d3.forceSimulation(nodes)
    .alphaDecay(0.05)
    .force('link',   d3.forceLink(links).id(d => d.id).distance(180).strength(0.35))
    .force('charge', d3.forceManyBody().strength(d => d._gtype === 'investor' ? -90 : -45))
    .force('radial', d3.forceRadial(d => d._gtype === 'company' ? Rco : Rinv, cx, cy).strength(d => d._gtype === 'company' ? 0.45 : 0.22))
    .force('col',    d3.forceCollide(d => gR(d) + 7))
    .on('tick', () => {
      lk.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      nd.attr('transform', d => `translate(${d.x},${d.y})`);
    })
    .on('end', () => {
      applyDefaultTransform(svg, AppState.ui.graph.zoom, computeGraphFit(nodes, W, H), true);
    });
}

function buildBipartite() {
  const { COMPANIES, INVESTORS, derived, ui } = AppState;
  const { raw } = derived;
  const { svg, g, W, H } = setupGraphSvg();
  const { leadOnly, hideIsolated, showCompanies, showInvestors } = ui.graph;

  let links = raw
    .filter(([c]) => COMPANIES.some(x => x.name === c))
    .map(([c, i, lead]) => ({ source: i, target: c, lead }));
  if (leadOnly) links = links.filter(l => l.lead);
  if (!showCompanies || !showInvestors) links = [];

  const activeIds = hideIsolated ? new Set(links.flatMap(l => [l.source, l.target])) : null;

  const coFiltered = !showCompanies ? [] : COMPANIES.filter(c => !activeIds || activeIds.has(c.name));
  const coNodes = coFiltered.map((c, i) => ({
    ...c, id: c.name, _gtype: 'company',
    x: W * 0.72, y: (H / (coFiltered.length + 1)) * (i + 1),
    _x0: W * 0.72, _y0: (H / (coFiltered.length + 1)) * (i + 1),
  }));
  const filteredInv = !showInvestors ? [] : INVESTORS
    .filter(im => im.portfolio.some(p => COMPANIES.some(c => c.name === p.company?.name)))
    .filter(im => !activeIds || activeIds.has(im.entity.name));
  const invNodes = filteredInv.map((im, i) => ({
    ...im.entity, id: im.entity.name, _gtype: 'investor', total: im.total, leads: im.leads, portfolio: im.portfolio,
    x: W * 0.25, y: (H / (filteredInv.length + 1)) * (i + 1),
    _x0: W * 0.25, _y0: (H / (filteredInv.length + 1)) * (i + 1),
  }));

  const nodeIds = new Set([...invNodes, ...coNodes].map(n => n.id));
  links = links.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));
  const nodes = [...invNodes, ...coNodes];

  // Bipartite positions are column-exact — fit immediately
  applyDefaultTransform(svg, AppState.ui.graph.zoom, computeGraphFit(nodes, W, H));

  const lkG = g.append('g'), ndG = g.append('g');
  const lk = lkG.selectAll('line').data(links).join('line')
    .attr('class', d => `glink${d.lead ? ' lead' : ''}`)
    .attr('stroke-width', d => d.lead ? 1.5 : 0.7);
  const nd = ndG.selectAll('g').data(nodes, d => d.id).join('g')
    .attr('class', d => d._gtype === 'investor'
      ? `gnode-inv gnode-inv--${d.type || 'fund'}`
      : `gnode-co gnode-co--${d.sector || 'default'}`)
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) ui.graph.simBi.alphaTarget(0.1).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end',   (e, d) => { if (!e.active) ui.graph.simBi.alphaTarget(0); d.fx = null; d.fy = null; }))
    .on('click', (e, d) => gOnClick(e, d, nd, lk))
    .on('mouseover', (e, d) => {
      if (_tipPinned) return;
      if (d._gtype === 'investor') tip(e, d.entity?.name || d.name, `${d.total} inv · ${d.leads} lead`);
      else tip(e, d.name, `${(d._investors || []).length} investors`, d.sector || '');
    })
    .on('mouseout', () => { if (!_tipPinned) hideTip(); });

  appendNodeShapes(nd);

  svg.on('click', () => {
    nd.classed('ghl', false).classed('gdim', false); lk.classed('ghl', false).classed('gdim', false).attr('stroke-opacity', null);
    _tipPinned = false;
    hideTip();
    closeGraphDetail();
    const t = AppState.ui.graph.defaultTransform;
    const z = AppState.ui.graph.zoom;
    if (t && z) svg.transition().duration(500).call(z.transform, t);
  });

  _nd = nd; _lk = lk;
  applyGraphSearch();

  ui.graph.simBi = d3.forceSimulation(nodes)
    .alphaDecay(0.05)
    .force('link',  d3.forceLink(links).id(d => d.id).distance(130).strength(0.4))
    .force('charge', d3.forceManyBody().strength(-50))
    .force('x',     d3.forceX(d => d._x0).strength(0.22))
    .force('y',     d3.forceY(d => d._y0).strength(0.06))
    .force('col',   d3.forceCollide(d => gR(d) + 5))
    .on('tick', () => {
      lk.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      nd.attr('transform', d => `translate(${d.x},${d.y})`);
    })
    .on('end', () => {
      applyDefaultTransform(svg, AppState.ui.graph.zoom, computeGraphFit(nodes, W, H), true);
    });
}

function buildProjection() {
  const { COMPANIES, INVESTORS, derived, ui } = AppState;
  const { raw } = derived;
  const { svg, g, W, H } = setupGraphSvg();
  // Projection shows investors only — if investors are hidden, render nothing
  if (!ui.graph.showInvestors) { _nd = null; _lk = null; return; }
  const coSet = new Set(COMPANIES.map(c => c.name));
  const filteredRaw = raw.filter(([c]) => coSet.has(c));

  const coMap2 = {};
  filteredRaw.forEach(([c, i]) => {
    if (!coMap2[c]) coMap2[c] = new Set();
    coMap2[c].add(i);
  });

  const linkMap = {};
  filteredRaw.forEach(([c, i]) => {
    [...(coMap2[c] || [])].forEach(j => {
      if (i === j) return;
      const key = [i, j].sort().join('|||');
      if (!linkMap[key]) linkMap[key] = { a: [i, j].sort()[0], b: [i, j].sort()[1], cos: [] };
      if (!linkMap[key].cos.includes(c)) linkMap[key].cos.push(c);
    });
  });

  let links = Object.values(linkMap).map(c => ({ source: c.a, target: c.b, weight: c.cos.length, cos: c.cos }));
  if (ui.graph.projFilter === 'multi') links = links.filter(l => l.weight > 1);
  if (ui.graph.leadOnly) {
    // In projection, only keep links where at least one investor has a lead investment
    const leadInvs = new Set(raw.filter(([,, lead]) => lead).map(([, i]) => i));
    links = links.filter(l => leadInvs.has(l.source) || leadInvs.has(l.target));
  }

  const activeInProj = ui.graph.hideIsolated
    ? new Set(links.flatMap(l => [l.source, l.target]))
    : null;
  const allInvNames = new Set(filteredRaw.map(([, i]) => i));
  const nodes = INVESTORS
    .filter(im => allInvNames.has(im.entity.name))
    .filter(im => !activeInProj || activeInProj.has(im.entity.name))
    .map(im => ({
      id: im.entity.name, total: im.total, leads: im.leads, portfolio: im.portfolio,
      entity: im.entity, _gtype: 'investor',
      x: W / 2 + (Math.random() - 0.5) * 300,
      y: H / 2 + (Math.random() - 0.5) * 300,
    }));

  // Apply initial fit from randomised starting positions
  applyDefaultTransform(svg, AppState.ui.graph.zoom, computeGraphFit(nodes, W, H));

  const lkG = g.append('g'), ndG = g.append('g');
  const lk = lkG.selectAll('line').data(links).join('line')
    .attr('stroke', d => d.weight > 1 ? 'rgba(104,204,209,.5)' : 'rgb(65,67,69)')
    .attr('stroke-width', d => 0.6 + d.weight * 1.1).attr('fill', 'none')
    .on('mouseover', (e, d) => {
      const s = d.source.id || d.source, t = d.target.id || d.target;
      tip(e, `${s} × ${t}`, `${d.weight} shared`, d.cos.join(', '));
    })
    .on('mouseout', () => { if (!_tipPinned) hideTip(); });

  function rP(d) { return 5 + Math.sqrt(d.total) * 4; }

  const nd = ndG.selectAll('g').data(nodes, d => d.id).join('g')
    .attr('class', d => `gnode-inv gnode-inv--${d.entity?.type || d.type || 'fund'}`)
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) ui.graph.simProj.alphaTarget(0.1).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end',   (e, d) => { if (!e.active) ui.graph.simProj.alphaTarget(0); d.fx = null; d.fy = null; }))
    .on('click', (e, d) => {
      e.stopPropagation();
      _tipPinned = true;
      tip(e, d.id, `${d.total} investments · ${d.leads} lead`);
      nd.classed('ghl', n => n.id === d.id || links.some(l => {
        const s = l.source.id || l.source, t = l.target.id || l.target;
        return (s === d.id && t === n.id) || (t === d.id && s === n.id);
      }));
      lk.classed('ghl', l => {
        const s = l.source.id || l.source, t = l.target.id || l.target;
        return s === d.id || t === d.id;
      });
      graphShowPanel(d);
    })
    .on('mouseover', (e, d) => { if (!_tipPinned) tip(e, d.id, `${d.total} investments · ${d.leads} lead`); })
    .on('mouseout', () => { if (!_tipPinned) hideTip(); });

  // Projection has only investors; use rP as the size fn, wrap it to match appendNodeShapes signature
  nd.each(function(d) {
    const r = rP(d);
    d3.select(this).append('rect')
      .attr('width', r * 2).attr('height', r * 2)
      .attr('x', -r).attr('y', -r).attr('rx', 2);
    d3.select(this).append('text').attr('class', 'glabel')
      .attr('dy', r + 11).attr('text-anchor', 'middle')
      .text(d.id.length > 15 ? d.id.slice(0, 14) + '…' : d.id);
    if (d.total > 1) d3.select(this).append('text')
      .attr('class', `gbadge gbadge--${typeKey(d.entity?.type || d.type)}`)
      .attr('dy', 4).attr('text-anchor', 'middle').text(d.total);
  });

  svg.on('click', () => {
    nd.classed('ghl', false).classed('gdim', false); lk.classed('ghl', false).classed('gdim', false).attr('stroke-opacity', null);
    _tipPinned = false;
    hideTip();
    closeGraphDetail();
    const t = AppState.ui.graph.defaultTransform;
    const z = AppState.ui.graph.zoom;
    if (t && z) svg.transition().duration(500).call(z.transform, t);
  });

  _nd = nd; _lk = lk;
  applyGraphSearch();

  ui.graph.simProj = d3.forceSimulation(nodes)
    .alphaDecay(0.05)
    .force('link',   d3.forceLink(links).id(d => d.id).distance(d => 60 + 50 / Math.max(d.weight, 1)).strength(0.25))
    .force('charge', d3.forceManyBody().strength(-120))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('col',    d3.forceCollide(d => rP(d) + 9))
    .on('tick', () => {
      lk.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      nd.attr('transform', d => `translate(${d.x},${d.y})`);
    })
    .on('end', () => {
      applyDefaultTransform(svg, AppState.ui.graph.zoom, computeGraphFit(nodes, W, H), true);
    });
}
