'use strict';

// ── Shared EDF calls data loader — cached singleton fetch ──────────────────
// Both edfoverview and edfbrowse import this so the JSON is only fetched once.

let _promise = null;

export function loadEdfCalls() {
  if (!_promise) {
    _promise = fetch('data/edf_calls.json')
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status} ${r.statusText}`); return r.json(); });
  }
  return _promise;
}
