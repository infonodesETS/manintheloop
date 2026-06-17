'use strict';

// ── URL state sync ────────────────────────────────────────────────────────────
// Provides read/write access to URL query params for shareable filter state.
// setParams() is a no-op until setUrlReady() is called, preventing spurious
// URL writes during initial data loading and restore.

let _ready = false;

export function setUrlReady() { _ready = true; }

/** Return all current query params as a plain object. */
export function getParams() {
  return Object.fromEntries(new URLSearchParams(location.search));
}

// Auto-inject ?research= group when only ?tab= is provided by tab-level code.
const TAB_TO_RESEARCH = {
  intro:         'intro',
  overview:      'supply-chain', matrix:        'supply-chain', graph:        'supply-chain',
  companies:     'supply-chain', investors:     'supply-chain', relationships:'supply-chain',
  map:           'supply-chain',
  edfoverview:   'edf',          edfmap:        'edf',          eucalls:      'edf',
  edfbrowse:     'edf',
  about:         'about',        knownissues:   'about',        quality:      'about',
  wikidata:      'about',        data:          'about',        glossary:     'about',
};

/**
 * Replace the full URL query string.
 * Falsy / default-sentinel values are omitted for cleaner URLs.
 * push=true creates a browser history entry (use for tab switches);
 * push=false (default) replaces current entry (use for filter changes).
 * If params includes `tab` but not `research`, the research group is
 * auto-injected from TAB_TO_RESEARCH so tab-level code stays unchanged.
 */
export function setParams(params, push = false) {
  if (!_ready) return;
  // Auto-inject research group from tab name if not explicitly provided
  if (params.tab && !params.research) {
    params = { research: TAB_TO_RESEARCH[params.tab] || 'supply-chain', ...params };
  }
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== null && v !== undefined && v !== '' && v !== false) {
      sp.set(k, String(v));
    }
  }
  const url = new URL(location.href);
  url.search = sp.toString();
  if (push) {
    history.pushState(null, '', url);
  } else {
    history.replaceState(null, '', url);
  }
}
