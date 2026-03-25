'use strict';

import { AppState } from './state.js';

const TODAY = new Date().toISOString().slice(0, 10);

function contextBlock() {
  const { companies, investors, relationships } = AppState;
  const countrySet = new Set(
    companies.map(c => c.sources?.wikidata?.country || c.sources?.infonodes?.country).filter(Boolean)
  );
  return `# Man in the Loop — info.nodes Explorer
_Paste this into ChatGPT, Claude, or any AI assistant to explore and understand the data._

## About this dataset
Man in the Loop is an independent research project tracking the European defence supply chain: companies, investors, and cross-border investment flows. The database currently covers **${companies.length} companies**, **${investors.length} investors**, and **${relationships.length} documented investment relationships** across **${countrySet.size} countries**. Data is hand-curated and enriched with Wikidata, Crunchbase, and public sources. It is a work in progress — some entries may be incomplete or require verification.

`;
}

function hdr(tab) {
  return contextBlock() + `---\n_Snapshot: ${TODAY} · Tab: ${tab}_\n\n`;
}

function footer(prompt) {
  return `\n---\n_Source: info.nodes defence supply chain database — companies, investors, cross-border investment flows._\n_Suggested prompt: ${prompt}_\n`;
}

function snapshotOverview() {
  const { companies, investors, relationships } = AppState;
  const sectors = {};
  for (const c of companies) sectors[c.sector] = (sectors[c.sector] || 0) + 1;
  const sectorLines = Object.entries(sectors).sort((a, b) => b[1] - a[1])
    .map(([k, v]) => `- ${k || 'Unknown'}: ${v}`).join('\n');
  return hdr('Overview') +
    `## Dataset stats\n- Companies: ${companies.length}\n- Investors: ${investors.length}\n- Relationships: ${relationships.length}\n\n## Companies by sector\n${sectorLines}` +
    footer('What patterns do you see in this defence supply chain dataset? Which sectors or countries are most represented?');
}

function snapshotCompanies() {
  const { companies } = AppState;
  const sector = AppState.ui.companies.sector;
  const q = (document.getElementById('co-search')?.value || '').toLowerCase();
  let list = [...companies];
  if (sector !== 'all') list = list.filter(c => c.sector === sector);
  if (q) list = list.filter(c => c.name.toLowerCase().includes(q));

  const filters = [];
  if (sector !== 'all') filters.push(`sector: ${sector}`);
  if (q) filters.push(`search: "${q}"`);

  const lines = list.map(c => {
    const wd = c.sources?.wikidata;
    const country = wd?.country || '—';
    const year = wd?.inception ? String(wd.inception).slice(0, 4) : '—';
    return `- **${c.name}** (${c.id}) | ${c.sector || '—'} | ${country} | est. ${year}`;
  }).join('\n');

  return hdr('Companies') +
    (filters.length ? `**Active filters:** ${filters.join(' · ')}\n\n` : '') +
    `## Companies (${list.length} of ${companies.length})\n\n${lines}` +
    footer('Analyse these companies: what sectors, countries, or founding periods are most represented? Any notable clusters?');
}

function snapshotInvestors() {
  const { investors, derived } = AppState;
  const { investorMeta } = derived;
  const { typeFilter } = AppState.ui.investors;
  const q = (document.getElementById('inv-search')?.value || '').toLowerCase();
  let list = Object.values(investorMeta);
  if (q) list = list.filter(im => im.entity.name.toLowerCase().includes(q));
  if (typeFilter) list = list.filter(im => im.entity.type === typeFilter);
  list = list.sort((a, b) => b.total - a.total);

  const filters = [];
  if (typeFilter) filters.push(`type: ${typeFilter}`);
  if (q) filters.push(`search: "${q}"`);

  const lines = list.map(im => {
    const top = im.portfolio.slice(0, 3).map(p => p.company?.name || '?').join(', ');
    return `- **${im.entity.name}** | ${im.entity.type || '—'} | ${im.total} investments (${im.leads} lead) | e.g. ${top}`;
  }).join('\n');

  return hdr('Investors') +
    (filters.length ? `**Active filters:** ${filters.join(' · ')}\n\n` : '') +
    `## Investors (${list.length} of ${investors.length})\n\n${lines}` +
    footer('Analyse these investors: what types dominate? Which investors have the most lead investments? Any patterns in who backs defence vs tech companies?');
}

function snapshotRelationships() {
  const { relationships } = AppState;
  const q = (document.getElementById('rel-search')?.value || '').toLowerCase();
  let list = [...relationships];
  if (q) list = list.filter(r =>
    (r.company || '').toLowerCase().includes(q) ||
    (r.investor || '').toLowerCase().includes(q)
  );

  const filters = [];
  if (q) filters.push(`search: "${q}"`);

  const lines = list.slice(0, 200).map(r =>
    `- ${r.company} ← ${r.investor}${r.lead ? ' (LEAD)' : ''}`
  ).join('\n');
  const truncNote = list.length > 200 ? `\n_(showing 200 of ${list.length})_` : '';

  return hdr('Relationships') +
    (filters.length ? `**Active filters:** ${filters.join(' · ')}\n\n` : '') +
    `## Investment relationships (${list.length} of ${relationships.length})\n\n${lines}${truncNote}` +
    footer('What investment clusters or patterns do you see in these company-investor relationships? Which investors are most connected?');
}

function snapshotMap() {
  const { countryData, activeFilter } = AppState.ui.map;
  if (activeFilter && countryData[activeFilter]) {
    const cd = countryData[activeFilter];
    const companies = cd.companies.map(c => `- **${c.name}** | ${c.sector || '—'}`).join('\n');
    return hdr('Map') +
      `## Country: ${cd.name}\n\n- Companies: ${cd.companies.length}\n- Inbound investor flows: ${(cd.flowsIn || []).length}\n- Outbound investor flows: ${(cd.flowsOut || []).length}\n\n### Companies headquartered here\n${companies}` +
      footer(`Analyse the companies headquartered in ${cd.name}: what sectors are present? Who invests in them?`);
  }
  // No country selected — dump all countries with data
  const entries = Object.values(countryData)
    .filter(cd => cd.companies?.length)
    .sort((a, b) => b.companies.length - a.companies.length);
  const lines = entries.map(cd => `- **${cd.name}**: ${cd.companies.length} companies`).join('\n');
  return hdr('Map') +
    `## Countries with supply chain companies (${entries.length})\n\n${lines}` +
    footer('Which countries have the most companies? What does the geographic distribution of the defence supply chain look like?');
}

function snapshotGraph() {
  const { graph } = AppState.ui;
  const { companies, investors } = AppState;
  const filters = [];
  if (graph.sector !== 'all') filters.push(`sector: ${graph.sector}`);
  if (graph.search) filters.push(`search: "${graph.search}"`);
  if (graph.leadOnly) filters.push('lead investments only');
  if (graph.hideIsolated) filters.push('isolated nodes hidden');

  const visibleCos = graph.sector !== 'all'
    ? companies.filter(c => c.sector === graph.sector)
    : companies;
  const coLines = visibleCos.slice(0, 100).map(c => `- ${c.name} (${c.sector || '—'})`).join('\n');

  return hdr('Graph') +
    (filters.length ? `**Active filters:** ${filters.join(' · ')}\n\n` : '') +
    `## Visible companies (${visibleCos.length})\n${coLines}${visibleCos.length > 100 ? `\n_(showing 100 of ${visibleCos.length})_` : ''}\n\n` +
    `## Investors in dataset: ${investors.length}` +
    footer('Analyse the network structure of these companies and their investors. What clusters or hubs are most prominent?');
}

export function buildAiSnapshot() {
  const tab = AppState.ui.currentTab;
  switch (tab) {
    case 'overview':       return snapshotOverview();
    case 'companies':      return snapshotCompanies();
    case 'investors':      return snapshotInvestors();
    case 'relationships':  return snapshotRelationships();
    case 'map':            return snapshotMap();
    case 'graph':          return snapshotGraph();
    default:               return snapshotOverview();
  }
}

export function initCopyAI() {
  const btn = document.getElementById('copy-ai-btn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    const md = buildAiSnapshot();
    try {
      await navigator.clipboard.writeText(md);
      btn.textContent = 'Copied!';
    } catch {
      // fallback: create a temporary textarea
      const ta = document.createElement('textarea');
      ta.value = md; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      btn.textContent = 'Copied!';
    }
    setTimeout(() => { btn.textContent = 'Copy for AI'; }, 2000);
  });
}
