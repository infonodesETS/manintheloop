'use strict';

// ── router.js ─────────────────────────────────────────────────────────────────
// URL scheme: ?organization=IN-0461&organizationName=Airbus
//
// push(item)      — call on selectItem(); updates URL without page reload
// clear()         — call on clearSelection(); removes params from URL
// resolve(registry, entityMap) — call after buildRegistry(); returns the
//                   registry item matching current URL params, or null

const PARAM_ID   = 'organization';
const PARAM_NAME = 'organizationName';

// Return the canonical ID for a registry item:
// prefer dbEntity.id (IN-/IV-/PER-), fall back to EDF PIC string
function itemId(item) {
  return item.dbEntity?.id ?? (item.pic ? String(item.pic) : null);
}

export function push(item) {
  const id   = itemId(item);
  const name = item.name;
  if (!id) return;

  const url = new URL(window.location.href);
  url.searchParams.set(PARAM_ID,   id);
  url.searchParams.set(PARAM_NAME, name);
  history.pushState({ organization: id, organizationName: name }, '', url);
}

export function clear() {
  const url = new URL(window.location.href);
  url.searchParams.delete(PARAM_ID);
  url.searchParams.delete(PARAM_NAME);
  history.pushState(null, '', url);
}

// Returns the matching registry item for the current URL params, or null.
// Tries: 1) exact id match on dbEntity.id or PIC  2) exact name match
export function resolve(registry, entityMap) {
  const params = new URLSearchParams(window.location.search);
  const id     = params.get(PARAM_ID);
  const name   = params.get(PARAM_NAME);
  if (!id && !name) return null;

  // Try id first
  if (id) {
    // Match against dbEntity.id
    const byEntityId = registry.find(r => r.dbEntity?.id === id);
    if (byEntityId) return byEntityId;
    // Match against EDF PIC
    const byPic = registry.find(r => r.pic && String(r.pic) === id);
    if (byPic) return byPic;
  }

  // Fall back to name (case-insensitive)
  if (name) {
    const lower = name.toLowerCase();
    const byName = registry.find(r => r.name.toLowerCase() === lower);
    if (byName) return byName;
  }

  return null;
}

// Listen for browser back/forward and invoke callback(item|null)
export function onPopState(registry, entityMap, callback) {
  window.addEventListener('popstate', () => {
    const item = resolve(registry, entityMap);
    callback(item);
  });
}
