'use strict';

// ── router.js ─────────────────────────────────────────────────────────────────
// URL scheme: ?organization=IN-0461&organizationName=Airbus
//
// push(item)      — call on selectItem(); updates URL without page reload
// replace(item)   — use for initial load (avoids duplicate history entry)
// clear()         — call on clearSelection(); removes params from URL
// resolve(registry, entityMap) — call after buildRegistry(); returns the
//                   registry item matching current URL params, or null

const PARAM_ID       = 'organization';
const PARAM_NAME     = 'organizationName';
const PARAM_CMP_ID   = 'comparewith';
const PARAM_CMP_NAME = 'comparewithName';

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

export function replace(item) {
  const id   = itemId(item);
  const name = item.name;
  if (!id) return;

  const url = new URL(window.location.href);
  url.searchParams.set(PARAM_ID,   id);
  url.searchParams.set(PARAM_NAME, name);
  history.replaceState({ organization: id, organizationName: name }, '', url);
}

export function clear() {
  const url = new URL(window.location.href);
  url.searchParams.delete(PARAM_ID);
  url.searchParams.delete(PARAM_NAME);
  url.searchParams.delete(PARAM_CMP_ID);
  url.searchParams.delete(PARAM_CMP_NAME);
  history.pushState(null, '', url);
}

// Push both entities into the URL for compare mode.
export function pushCompare(itemA, itemB) {
  const idA = itemId(itemA);
  const idB = itemId(itemB);
  if (!idA || !idB) return;
  const url = new URL(window.location.href);
  url.searchParams.set(PARAM_ID,       idA);
  url.searchParams.set(PARAM_NAME,     itemA.name);
  url.searchParams.set(PARAM_CMP_ID,   idB);
  url.searchParams.set(PARAM_CMP_NAME, itemB.name);
  history.pushState(
    { organization: idA, organizationName: itemA.name,
      comparewith: idB, comparewithName: itemB.name },
    '', url
  );
}

// Remove compare params, keeping the main entity in the URL.
export function clearCompare() {
  const url = new URL(window.location.href);
  url.searchParams.delete(PARAM_CMP_ID);
  url.searchParams.delete(PARAM_CMP_NAME);
  history.pushState(null, '', url);
}

// Returns the compare registry item from the current URL, or null.
export function resolveCompare(registry) {
  const params = new URLSearchParams(window.location.search);
  const id   = params.get(PARAM_CMP_ID);
  const name = params.get(PARAM_CMP_NAME);
  if (!id && !name) return null;

  if (id) {
    const byEntityId = registry.find(r => r.dbEntity?.id === id);
    if (byEntityId) return byEntityId;
    const byPic = registry.find(r => r.pic && String(r.pic) === id);
    if (byPic) return byPic;
  }
  if (name) {
    const lower = name.toLowerCase();
    const byName = registry.find(r => r.name.toLowerCase() === lower);
    if (byName) return byName;
  }
  return null;
}

// Returns the matching registry item for the current URL params, or null.
// Tries: 1) exact id match on dbEntity.id or PIC  2) exact name match
export function resolve(registry, entityMap) {
  const params = new URLSearchParams(window.location.search);
  const id     = params.get(PARAM_ID);
  const name   = params.get(PARAM_NAME);
  if (!id && !name) return null;

  if (id) {
    const byEntityId = registry.find(r => r.dbEntity?.id === id);
    if (byEntityId) return byEntityId;
    const byPic = registry.find(r => r.pic && String(r.pic) === id);
    if (byPic) return byPic;
  }

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
