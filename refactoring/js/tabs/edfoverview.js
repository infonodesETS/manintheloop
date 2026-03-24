'use strict';

import { loadEdfCalls } from '../edf-data.js';

// ── EDF Overview — on-the-fly metrics from edf_calls.json ─────────────────

function fmtEuro(n) {
  if (!n) return '—';
  const v = Math.round(n);
  if (v >= 1e9) return `€${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `€${Math.round(v / 1e6)}M`;
  if (v >= 1e3) return `€${Math.round(v / 1e3)}K`;
  return `€${v.toLocaleString()}`;
}

function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Derive all metrics from the raw calls map ──────────────────────────────

function computeMetrics(callsMap) {
  const calls = Object.values(callsMap);

  // ── Call-level metrics ──
  const callCount = calls.length;

  // Sum budget allocations — deduplicate by topic ID globally (topics are shared across calls)
  let totalBudget = 0;
  let budgetAvailable = false;
  let budgetCallCount = 0;
  const seenTopics = new Set();
  for (const call of calls) {
    const topicMap = call.budget_overview?.budgetTopicActionMap || {};
    if (Object.keys(topicMap).length > 0) budgetCallCount++;
    for (const [topicId, actions] of Object.entries(topicMap)) {
      if (seenTopics.has(topicId)) continue;
      seenTopics.add(topicId);
      // Budget is the same across all actions of a topic — count it once
      const first = actions[0];
      if (!first) continue;
      for (const v of Object.values(first.budgetYearMap || {})) {
        const n = parseFloat(v);
        if (!isNaN(n) && n > 0) { totalBudget += n; budgetAvailable = true; }
      }
    }
  }

  // ── Project-level metrics ──
  const projectSet    = new Set();    // unique "callId|projTitle" keys
  const projectObjs   = [];          // { call_id, acronym, title, status, eu_contribution }
  const participantMap = {};          // key → { name, country, count, eu_total }
  const countryMap    = {};          // country → { participants, eu_total }

  let callsWithProjects = 0;
  let totalEuContribution = 0;

  for (const call of calls) {
    const projects = (call.projects || []).filter(p => (parseFloat(p.eu_contribution) || 0) > 0);
    if (projects.length > 0) callsWithProjects++;

    for (const proj of projects) {
      const pk = `${call.identifier}|${proj.title || proj.acronym}`;
      if (!projectSet.has(pk)) {
        projectSet.add(pk);
        projectObjs.push({
          call_id:        call.identifier,
          acronym:        proj.acronym || '',
          title:          proj.title || '—',
          status:         proj.status || '',
          eu_contribution: parseFloat(proj.eu_contribution) || 0,
        });
      }

      for (const pt of (proj.participants || [])) {
        const ptEu = parseFloat(pt.eu_contribution) || 0;
        totalEuContribution += ptEu;

        const key  = pt.pic || `${pt.organization_name}||${pt.country || ''}`;
        if (!participantMap[key]) {
          participantMap[key] = {
            name:    pt.organization_name || '—',
            country: pt.country || '—',
            count:   0,
            eu_total: 0,
          };
        }
        participantMap[key].count++;
        participantMap[key].eu_total += ptEu;

        const co = pt.country || '—';
        if (!countryMap[co]) countryMap[co] = { participants: 0, eu_total: 0 };
        countryMap[co].participants++;
        countryMap[co].eu_total += ptEu;
      }
    }
  }

  const fundedProjectCount  = projectSet.size;
  const uniqueParticipants  = Object.keys(participantMap).length;

  const topCountries    = Object.entries(countryMap)
    .sort((a, b) => b[1].participants - a[1].participants);
  const topParticipants = Object.values(participantMap)
    .sort((a, b) => b.count - a.count)
    .slice(0, 20);

  return {
    callCount, totalBudget, budgetAvailable, budgetCallCount,
    callsWithProjects, totalEuContribution,
    fundedProjectCount, uniqueParticipants,
    topCountries, topParticipants,
    hasProjectData: fundedProjectCount > 0,
  };
}

// ── Render ─────────────────────────────────────────────────────────────────

function renderStatCard(val, lbl) {
  return `<div class="stat-card"><div class="val">${val}</div><div class="lbl">${esc(lbl)}</div></div>`;
}

function renderBar(label, value, max, extra = '', wide = false, href = null) {
  const pct = max > 0 ? Math.round(value / max * 100) : 0;
  const labelHtml = href
    ? `<a href="${href}" class="eo-bar-link">${esc(label)}</a>`
    : `<span>${esc(label)}</span>`;
  return `<div class="eo-bar-row d-flex align-items-center gap-2 mb-1${href ? ' eo-bar-row--link' : ''}">
    <span class="eo-bar-label${wide ? ' eo-bar-label--wide' : ''}">${labelHtml}</span>
    <div class="prog-track flex-grow-1"><div class="prog-fill" style="width:${pct}%"></div></div>
    <span class="eo-bar-val">${value.toLocaleString()}${extra ? `<span class="eo-bar-extra"> ${extra}</span>` : ''}</span>
  </div>`;
}

function render(m) {
  const wrap = document.getElementById('eo-wrap');
  if (!wrap) return;

  // Stat cards — 2-column layout
  // Row 1: EDF Calls | Total Allocated Budget
  // Row 2: Calls with Funded Projects | Budget of Calls with Funded Projects
  // Row 3: Funded Projects | Unique Participants
  const cards = [
    renderStatCard(m.callCount.toLocaleString(), 'European Defence Fund Calls'),
    m.budgetAvailable ? renderStatCard(fmtEuro(m.totalBudget), 'Total Allocated Budget *') : renderStatCard('—', 'Total Allocated Budget'),
    renderStatCard(m.callsWithProjects.toLocaleString(), 'Calls with Funded Projects'),
    renderStatCard(fmtEuro(m.totalEuContribution) || '—', 'Total EU Contribution'),
    renderStatCard(m.fundedProjectCount.toLocaleString(), 'Funded Projects'),
    renderStatCard(m.uniqueParticipants.toLocaleString(), 'Unique Participants'),
  ];
  document.getElementById('eo-stats-grid').innerHTML = cards.join('');

  if (!m.hasProjectData) {
    document.getElementById('eo-rankings').innerHTML = `
      <div class="stat-card" style="text-align:center;padding:28px 18px;color:#555;font-size:var(--fs-base)">
        No funded project data available yet — project participants will appear here once the dataset is populated.
      </div>`;
    return;
  }

  // Country ranking
  const maxC   = m.topCountries[0]?.[1].participants || 1;
  const ctryHtml = m.topCountries.slice(0, 20).map(([c, d]) =>
    renderBar(c, d.participants, maxC, d.eu_total > 0 ? fmtEuro(d.eu_total) : '')
  ).join('');

  // Participant ranking — label links to EDF Beneficiaries pre-filtered by org name
  const maxP   = m.topParticipants[0]?.count || 1;
  const partHtml = m.topParticipants.map(p => {
    const href = `?research=edf&tab=edfbrowse&search=${encodeURIComponent(p.name)}`;
    return renderBar(p.name, p.count, maxP, p.eu_total > 0 ? fmtEuro(p.eu_total) : '', true, href);
  }).join('');

  document.getElementById('eo-rankings').innerHTML = `
    <div class="row g-3">
      <div class="col-md-4">
        <div class="stat-card">
          <div class="section-title">Countries by Participations</div>
          <div id="eo-country-bars" class="mt-2">${ctryHtml}</div>
        </div>
      </div>
      <div class="col-md-8">
        <div class="stat-card">
          <div class="section-title">Top Participants by Projects</div>
          <div id="eo-part-bars" class="mt-2">${partHtml}</div>
        </div>
      </div>
    </div>`;
}

// ── Init ───────────────────────────────────────────────────────────────────

export default async function initEdfoverview() {
  try {
    const json = await loadEdfCalls();
    const callsMap = json.calls || {};
    const metrics  = computeMetrics(callsMap);
    render(metrics);
  } catch (err) {
    const wrap = document.getElementById('eo-wrap');
    if (wrap) wrap.innerHTML = `<div style="color:#ff4444;font-size:var(--fs-base);font-family:monospace;padding:20px">
      Error loading EDF data: ${esc(err.message)}</div>`;
  }
}
