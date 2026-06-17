'use strict';

export const GLOSSARY = {
  company:           'Manufacturer or tracked entity in the research database (ID: IN-NNNN)',
  investor:          'Fund, bank, government agency, or institution that finances one or more companies (ID: IV-NNNN)',
  relationship:      'Documented investment link between an Investor and a Company',
  lead:              'The investor leads the funding round — primary decision-maker',
  follow:            'The investor participates in the round but does not lead it',
  mining:            'Extraction of critical raw materials for defence: semiconductors, rare earths, strategic metals',
  defence:           'Companies that produce weapons systems, military platforms, or defence technologies',
  tech:              'Technology companies with defence exposure: AI, cloud computing, cybersecurity, infrastructure',
  startup:           'European early-stage companies in the military and security sector',
  edf:               'European Defence Fund — EU fund financing defence R&D across 201 calls (2021–2027)',
  participation:     'Organisation that received EDF funding as a partner in a funded project',
  'eu-contribution': 'EU funding amount assigned to an organisation for a specific EDF project',
};

export function initGlossaryTooltips() {
  document.querySelectorAll('.gl-term[data-gl]').forEach(el => {
    const def = GLOSSARY[el.dataset.gl];
    if (def) el.setAttribute('data-tooltip', def);
  });
}

export function renderGlossaryTab() {
  const el = document.getElementById('glossary-body');
  if (!el) return;
  el.innerHTML = Object.entries(GLOSSARY).map(([term, def]) =>
    `<div class="gl-entry">
      <span class="gl-entry-term">${term.replace(/-/g, '\u2011')}</span>
      <span class="gl-entry-def">${def}</span>
    </div>`
  ).join('');
}
