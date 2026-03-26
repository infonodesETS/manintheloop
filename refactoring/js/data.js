'use strict';

import { AppState } from './state.js';

export async function loadData() {
  const r = await fetch('data/database.json');
  if (!r.ok) throw new Error(r.statusText);
  const db = await r.json();

  AppState.db = db;

  db.entities.forEach(e => { AppState.derived.entityMap[e.id] = e; });

  AppState.companies     = db.entities.filter(e => e.type === 'company');
  AppState.investors     = db.entities.filter(e => e.type !== 'company');
  AppState.relationships = db.relationships.filter(r => r.type === 'investment');

  // Build investor portfolio metadata
  AppState.investors.forEach(inv => {
    AppState.derived.investorMeta[inv.id] = { entity: inv, portfolio: [], leads: 0, total: 0 };
  });
  AppState.relationships.forEach(rel => {
    const im = AppState.derived.investorMeta[rel.source];
    if (!im) return;
    const comp = AppState.derived.entityMap[rel.target];
    const lead = rel.details?.lead || false;
    im.portfolio.push({ company: comp, lead });
    im.total++;
    if (lead) im.leads++;
  });

  // Build company → investors lookup
  const ciMap = {};
  AppState.relationships.forEach(rel => {
    if (!ciMap[rel.target]) ciMap[rel.target] = [];
    const inv = AppState.derived.entityMap[rel.source];
    ciMap[rel.target].push({ name: inv?.name || rel.source, lead: rel.details?.lead || false });
  });
  AppState.companies.forEach(c => { c._investors = ciMap[c.id] || []; });

  // Build COMPANIES / INVESTORS / RAW for matrix + graph
  AppState.ALL_COMPANIES = [...AppState.companies];
  AppState.COMPANIES     = [...AppState.companies];
  AppState.INVESTORS     = Object.values(AppState.derived.investorMeta)
    .sort((a, b) => b.total - a.total || b.leads - a.leads);

  AppState.relationships.forEach(rel => {
    const cname = AppState.derived.entityMap[rel.target]?.name;
    const iname = AppState.derived.entityMap[rel.source]?.name;
    if (cname && iname) AppState.derived.raw.push([cname, iname, rel.details?.lead || false]);
  });

  AppState.companies.forEach(c => { AppState.derived.companyMap[c.name] = c; });
  AppState.investors.forEach(i => { AppState.derived.invMap[i.name] = AppState.derived.investorMeta[i.id]; });

  // Build entity rel maps (investment + other) — used by company search and detail sidebar
  const relMap = {}, otherRelMap = {};
  for (const rel of db.relationships) {
    if (rel.type === 'investment') {
      if (!relMap[rel.source]) relMap[rel.source] = [];
      if (!relMap[rel.target]) relMap[rel.target] = [];
      relMap[rel.source].push({ rel, role: 'investor', other: AppState.derived.entityMap[rel.target] || null });
      relMap[rel.target].push({ rel, role: 'target',   other: AppState.derived.entityMap[rel.source] || null });
    } else {
      if (!otherRelMap[rel.source]) otherRelMap[rel.source] = [];
      if (!otherRelMap[rel.target]) otherRelMap[rel.target] = [];
      otherRelMap[rel.source].push({ rel, role: 'source', other: AppState.derived.entityMap[rel.target] || null });
      otherRelMap[rel.target].push({ rel, role: 'target', other: AppState.derived.entityMap[rel.source] || null });
    }
  }
  AppState.derived.relMap      = relMap;
  AppState.derived.otherRelMap = otherRelMap;

  return db;
}
