'use strict';

import { AppState } from './state.js';
import { loadData } from './data.js';
import { getParams, setParams, setUrlReady } from './url.js';

import initOverview from './tabs/overview.js';
import initMatrix, { setMatrixSector, closeMxDetail } from './tabs/matrix.js';
import initCompanies, { setCoSector, sortCo, renderCoTable, restoreCoUrl, openCompaniesIntro } from './tabs/companies.js';
import initInvestors, { sortInv, renderInvTable, restoreInvUrl, openInvestorsIntro } from './tabs/investors.js';
import initRelationships, { renderRelTable, restoreRelUrl, openRelationshipsIntro } from './tabs/relationships.js';
import initGraph, { setGraphView, setGraphSector, setProjFilter, closeGraphDetail, pauseGraph, resumeGraph, showGraphHelp, setGraphSearch, setLeadOnly, setHideIsolated, setShowCompanies, setShowInvestors } from './tabs/graph.js';
import initMap, { toggleMapArcs, resetMapZoom, closeMapPanel, clearMapFilter, selectMapCountryByName } from './tabs/map.js';
import initWikidata, { toggleWdMode, onLiveInput } from './tabs/wikidata.js';
import initQuality from './tabs/quality.js';
import initEucalls     from './tabs/eucalls.js';
import initEdfbrowse, { openEdfBrowseIntro } from './tabs/edfbrowse.js';
import initEdfoverview from './tabs/edfoverview.js';
import initEdfMap, { clearEdfMapFilter, closeEdfMapPanel, resetEdfMapZoom, toggleEdfMapArcs } from './tabs/edfmap.js';
import initKnownIssues from './tabs/knownissues.js';
import { initEntitySidebar, openCompanySidebar, openInvestorSidebar } from './detail-sidebar.js';
import { initGlossaryTooltips, renderGlossaryTab } from './glossary.js';
import { initCopyAI } from './copy-ai.js';

// ── Preloader helper ──
function hidePreloader(tabId) {
  document.getElementById(tabId)?.querySelector('.tab-preloader')?.classList.add('done');
}

// ── Group → sub-tab config ──
const GROUPS = {
  'intro':        { tabs: null,    defaultTab: null },
  'supply-chain': { tabs: ['overview','map','graph','companies','investors','relationships','matrix'], defaultTab: 'overview' },
  'edf':          { tabs: ['edfoverview','edfmap','eucalls','edfbrowse'], defaultTab: 'edfoverview' },
  'about':        { tabs: ['about','knownissues','quality','wikidata','data','glossary'], defaultTab: 'about' },
};

// ── Unified navigation ──
// group: 'intro' | 'supply-chain' | 'edf' | 'tools' | 'about'
// tab:   sub-tab name (null for standalone groups)
// push:  true = new history entry (manual click), false = replace (restore)
function navigate(group, tab, push = true) {
  const grp    = GROUPS[group] || GROUPS['supply-chain'];
  const prevTab = AppState.ui.currentTab;
  const resolvedTab = tab || grp.defaultTab;   // null for intro/about

  AppState.ui.currentGroup = group;
  AppState.ui.currentTab   = resolvedTab || group; // use group id as pane id for standalones

  // Group buttons
  document.querySelectorAll('.tnav-btn[data-research]').forEach(b =>
    b.classList.toggle('active', b.dataset.research === group)
  );

  // Sub-nav and legend visibility (legend is supply-chain only)
  const hasSub = !!grp.tabs;
  document.body.classList.toggle('subnav-hidden', !hasSub);
  document.body.classList.toggle('legend-hidden', resolvedTab !== 'graph');
  document.querySelectorAll('.snav-group').forEach(g =>
    g.style.display = g.dataset.research === group ? 'flex' : 'none'
  );

  // Sub-tab button active state
  document.querySelectorAll('.snav-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.tab === resolvedTab)
  );

  // Tab panes — use resolvedTab or group name as pane id
  const paneId = resolvedTab || group;
  document.querySelectorAll('.tab-pane').forEach(p =>
    p.classList.toggle('active', p.id === `tab-${paneId}`)
  );

  // Graph pause / resume
  if (prevTab === 'graph' && paneId !== 'graph') pauseGraph();
  if (paneId === 'graph' && prevTab !== 'graph' && AppState.ui.graph.sim) resumeGraph();

  // Lazy-inits — hide preloader after init resolves
  if (paneId === 'graph' && !AppState.ui.graph.sim) { initGraph(); hidePreloader('tab-graph'); }
  else if (paneId === 'graph') {
    const gInp = document.getElementById('graph-search');
    if (gInp) gInp.value = AppState.ui.graph.search;
    setGraphSearch(AppState.ui.graph.search);
  }
  if (paneId === 'map' && !AppState.ui.map.built) {
    initMap().then(() => {
      hidePreloader('tab-map');
      if (AppState.ui.map.pendingCountry) {
        selectMapCountryByName(AppState.ui.map.pendingCountry);
        delete AppState.ui.map.pendingCountry;
      }
    });
  } else if (paneId === 'map' && AppState.ui.map.pendingCountry) {
    const pc = AppState.ui.map.pendingCountry;
    delete AppState.ui.map.pendingCountry;
    selectMapCountryByName(pc);
  }
  if (paneId === 'edfoverview' && !AppState.ui.edfoverview.built) {
    AppState.ui.edfoverview.built = true;
    initEdfoverview().then(() => hidePreloader('tab-edfoverview'));
  }
  if (paneId === 'edfmap' && !AppState.ui.edfmap.built) {
    AppState.ui.edfmap.built = true;
    initEdfMap().then(() => hidePreloader('tab-edfmap'));
  }
  if (paneId === 'eucalls' && !AppState.ui.eucalls.built) {
    initEucalls(); AppState.ui.eucalls.built = true; hidePreloader('tab-eucalls');
  }
  if (paneId === 'edfbrowse' && !AppState.ui.edfbrowse.built) {
    AppState.ui.edfbrowse.built = true;
    initEdfbrowse().then(() => hidePreloader('tab-edfbrowse'));
  }
  if (paneId === 'knownissues' && !AppState.ui.knownissues?.built) {
    if (!AppState.ui.knownissues) AppState.ui.knownissues = {};
    AppState.ui.knownissues.built = true;
    initKnownIssues().then(() => hidePreloader('tab-knownissues'));
  }
  if (paneId === 'glossary' && !AppState.ui.glossary?.built) {
    if (!AppState.ui.glossary) AppState.ui.glossary = {};
    AppState.ui.glossary.built = true;
    renderGlossaryTab();
  }

  // Open intro sidebars on tab switch; close conflicting overlays
  const edfTabs = ['edfbrowse', 'eucalls', 'edfmap', 'edfoverview'];
  const scTabs  = ['companies', 'investors', 'relationships'];
  if (scTabs.includes(paneId))  document.getElementById('edf-sidebar')?.classList.remove('open');
  if (edfTabs.includes(paneId)) document.getElementById('entity-sidebar')?.classList.remove('open');
  if (paneId === 'companies') openCompaniesIntro();
  if (paneId === 'investors') openInvestorsIntro();
  if (paneId === 'relationships') openRelationshipsIntro();
  if (paneId === 'edfbrowse') openEdfBrowseIntro();
  if (paneId === 'graph' && AppState.ui.graph.sim) showGraphHelp();

  // URL — omit tab for standalone groups
  const params = { research: group };
  if (resolvedTab) params.tab = resolvedTab;
  setParams(params, push);
}
AppState.navigate = navigate;

// ── Restore full state from current URL params ──
function restoreFromUrl() {
  const p     = getParams();
  const group = p.research || 'intro';
  const grp   = GROUPS[group] || GROUPS['supply-chain'];
  const tab   = p.tab || grp.defaultTab || null;

  navigate(group, tab, false);

  // Restore tab-specific filter state
  switch (tab) {
    case 'companies':
      restoreCoUrl(p);
      break;

    case 'investors':
      restoreInvUrl(p);
      break;

    case 'relationships':
      restoreRelUrl(p);
      break;

    case 'matrix':
      if (p.sector) {
        const btn = document.querySelector(`#tab-matrix .sf-btn[data-sector="${p.sector}"]`);
        if (btn) btn.click();
      }
      break;

    case 'map':
      if (p.country) {
        if (AppState.ui.map.built) selectMapCountryByName(p.country);
        else AppState.ui.map.pendingCountry = p.country;
      }
      break;

    case 'companies':
      if (p.company) {
        const co = AppState.companies.find(c => c.id === p.company);
        if (co) openCompanySidebar(co);
      }
      break;

    case 'investors':
      if (p.investor) {
        const im = AppState.derived.investorMeta[p.investor];
        if (im) openInvestorSidebar(im);
      }
      break;

    case 'graph':
      if (p.view) {
        const map = { network: 'gv-net', bipartite: 'gv-bi', projection: 'gv-proj' };
        document.getElementById(map[p.view] || 'gv-net')?.click();
      }
      if (p.sector) {
        document.querySelector(`#graph-controls .sf-btn[data-sector="${p.sector}"]`)?.click();
      }
      if (p.search) {
        const inp = document.getElementById('graph-search');
        if (inp) { inp.value = p.search; setGraphSearch(p.search); }
      }
      if (p.lead === '1') {
        const btn = document.getElementById('gv-lead-only');
        if (btn && !btn.classList.contains('active')) { btn.classList.add('active'); setLeadOnly(true); }
      }
      if (p.hideIso === '1') {
        const btn = document.getElementById('gv-hide-iso');
        if (btn && !btn.classList.contains('active')) { btn.classList.add('active'); setHideIsolated(true); }
      }
      if (p.hideCo === '1') {
        const btn = document.getElementById('gv-show-co');
        if (btn && btn.classList.contains('active')) { btn.classList.remove('active'); setShowCompanies(false); }
      }
      if (p.hideInv === '1') {
        const btn = document.getElementById('gv-show-inv');
        if (btn && btn.classList.contains('active')) { btn.classList.remove('active'); setShowInvestors(false); }
      }
      if (p.proj === 'multi') {
        document.getElementById('pf-multi')?.click();
      }
      break;

    case 'edfbrowse':
      // Lazy-init async tab: restoreEdfbrowseUrl is called at the end of initEdfbrowse()
      break;

    case 'eucalls':
      if (p.topic) {
        const inp = document.getElementById('ec-topicInput');
        if (inp) inp.value = p.topic;
      }
      break;
  }
}

// ── Bootstrap ──
loadData()
  .then(db => {
    document.getElementById('nav-meta').textContent = `updated: ${db._updated || '—'}`;
    const tnavInfo = document.getElementById('tnav-info');
    tnavInfo.textContent =
      `${AppState.companies.length} co · ${AppState.investors.length} inv · ${AppState.relationships.length} rel`;
    tnavInfo.title =
      `${AppState.companies.length} companies · ${AppState.investors.length} investors · ${AppState.relationships.length} relationships in the dataset`;

    // Init glossary tooltips
    initGlossaryTooltips();

    // Init tabs that render immediately, then hide their preloaders
    initEntitySidebar();
    initCopyAI();

    initOverview();      hidePreloader('tab-overview');
    initMatrix();        hidePreloader('tab-matrix');
    initCompanies();     hidePreloader('tab-companies');
    initInvestors();     hidePreloader('tab-investors');
    initRelationships(); hidePreloader('tab-relationships');
    initWikidata();      hidePreloader('tab-wikidata');
    initQuality();       hidePreloader('tab-quality');

    // Wire intro navigate buttons (CTA + area titles + context about link)
    document.querySelectorAll('[data-navigate-group]').forEach(el => {
      el.addEventListener('click', () => {
        const group = el.dataset.navigateGroup;
        const tab   = el.dataset.navigateTab || null;
        navigate(group, tab || GROUPS[group]?.defaultTab || null, true);
      });
    });

    // Wire group buttons
    document.querySelectorAll('.tnav-btn[data-research]').forEach(b => {
      b.addEventListener('click', () => {
        const group = b.dataset.research;
        const grp   = GROUPS[group];
        // When returning to a group, restore its last active sub-tab
        const tab = grp && grp.tabs
          ? (AppState.ui.currentGroup === group ? AppState.ui.currentTab : grp.defaultTab)
          : null;
        navigate(group, tab, true);
      });
    });

    // Wire sub-tab buttons
    document.querySelectorAll('.snav-btn').forEach(b => {
      b.addEventListener('click', () => navigate(AppState.ui.currentGroup, b.dataset.tab, true));
    });

    // Wire matrix sector buttons
    document.querySelectorAll('#tab-matrix .sf-btn').forEach(b => {
      b.addEventListener('click', () => {
        document.querySelectorAll('#tab-matrix .sf-btn').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        setMatrixSector(b.dataset.sector);
        setParams({ tab: 'matrix', ...(b.dataset.sector !== 'all' ? { sector: b.dataset.sector } : {}) });
      });
    });
    document.getElementById('mx-detail').querySelector('.sl-close')
      .addEventListener('click', closeMxDetail);

    // Wire companies sector buttons
    document.querySelectorAll('#tab-companies .sf-btn').forEach(b => {
      b.addEventListener('click', () => {
        document.querySelectorAll('#tab-companies .sf-btn').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        setCoSector(b.dataset.sector);
      });
    });
    // Wire companies sortable headers
    document.querySelectorAll('#tab-companies thead th.sortable').forEach(th => {
      th.addEventListener('click', () => sortCo(th.dataset.sort));
    });

    // Wire investors sortable headers
    document.querySelectorAll('#tab-investors thead th.sortable').forEach(th => {
      th.addEventListener('click', () => sortInv(th.dataset.sort));
    });

    // Wire graph view buttons (also update URL)
    document.getElementById('gv-net').addEventListener('click',  () => { setGraphView('network');    setParams(getGraphBaseParams()); });
    document.getElementById('gv-bi').addEventListener('click',   () => { setGraphView('bipartite');  setParams(getGraphBaseParams()); });
    document.getElementById('gv-proj').addEventListener('click', () => { setGraphView('projection'); setParams(getGraphBaseParams()); });

    const dismissGraphHint = () => document.getElementById('graph-hint')?.classList.add('hidden');

    // Wire graph sector buttons (also update URL)
    document.querySelectorAll('#graph-controls .sf-btn').forEach(b => {
      b.addEventListener('click', () => {
        document.querySelectorAll('#graph-controls .sf-btn').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        setGraphSector(b.dataset.sector);
        if (b.dataset.sector !== 'all') dismissGraphHint();
        const view = AppState.ui.graph.view || 'network';
        const params = { tab: 'graph', view };
        if (b.dataset.sector !== 'all') params.sector = b.dataset.sector;
        setParams(params);
      });
    });

    // Wire projection filter buttons (also update URL)
    const getGraphBaseParams = () => {
      const g = AppState.ui.graph;
      const p = { tab: 'graph', view: g.view || 'network' };
      if (g.sector && g.sector !== 'all') p.sector = g.sector;
      if (g.search)        p.search  = g.search;
      if (g.leadOnly)      p.lead    = '1';
      if (g.hideIsolated)  p.hideIso = '1';
      if (!g.showCompanies) p.hideCo = '1';
      if (!g.showInvestors) p.hideInv = '1';
      if (g.projFilter && g.projFilter !== 'all') p.proj = g.projFilter;
      return p;
    };
    document.getElementById('pf-all').addEventListener('click', () => {
      setProjFilter('all'); setParams(getGraphBaseParams());
    });
    document.getElementById('pf-multi').addEventListener('click', () => {
      setProjFilter('multi'); setParams(getGraphBaseParams());
    });

    // Wire graph search + toggle controls (also update URL)
    document.getElementById('graph-search').addEventListener('input', e => {
      if (e.target.value) dismissGraphHint();
      setGraphSearch(e.target.value);
      setParams(getGraphBaseParams());
    });
    document.getElementById('gv-show-co').addEventListener('click', function() {
      setShowCompanies(this.classList.toggle('active'));
      setParams(getGraphBaseParams());
    });
    document.getElementById('gv-show-inv').addEventListener('click', function() {
      setShowInvestors(this.classList.toggle('active'));
      setParams(getGraphBaseParams());
    });
    document.getElementById('gv-lead-only').addEventListener('click', function() {
      setLeadOnly(this.classList.toggle('active'));
      setParams(getGraphBaseParams());
    });
    document.getElementById('gv-hide-iso').addEventListener('click', function() {
      setHideIsolated(this.classList.toggle('active'));
      setParams(getGraphBaseParams());
    });

    // Wire graph detail panel close
    document.getElementById('graph-detail-close').addEventListener('click', closeGraphDetail);

    // Wire map controls
    document.getElementById('map-arc-toggle').addEventListener('change', e => toggleMapArcs(e.target.checked));
    document.getElementById('map-reset-zoom-btn').addEventListener('click', resetMapZoom);
    document.getElementById('map-close-panel-btn').addEventListener('click', closeMapPanel);
    document.getElementById('map-clear-filter-btn').addEventListener('click', clearMapFilter);

    // Wire EDF map controls
    document.getElementById('edfmap-arc-toggle').addEventListener('change', e => toggleEdfMapArcs(e.target.checked));
    document.getElementById('edfmap-reset-zoom-btn').addEventListener('click', resetEdfMapZoom);
    document.getElementById('edfmap-close-panel-btn').addEventListener('click', closeEdfMapPanel);
    document.getElementById('edfmap-clear-filter-btn').addEventListener('click', clearEdfMapFilter);

    // Wire wikidata mode toggle and live input
    document.getElementById('wd-mode-toggle').addEventListener('change', e => toggleWdMode(e.target.checked));
    document.getElementById('wd-live-input').addEventListener('input', onLiveInput);

    document.getElementById('loading-overlay').style.display = 'none';

    // Restore state from URL, then open URL sync for subsequent changes
    restoreFromUrl();
    setUrlReady();

    // Handle browser back / forward
    window.addEventListener('popstate', () => {
      restoreFromUrl();
    });
  })
  .catch(err => {
    document.getElementById('loading-overlay').innerHTML =
      `<div style="color:#ff4444;font-family:monospace;font-size:var(--fs-base)">Error: ${err.message}</div>
       <div style="color:#555;font-size:var(--fs-sm);margin-top:8px">Serve with: python3 -m http.server 8081</div>`;
  });
