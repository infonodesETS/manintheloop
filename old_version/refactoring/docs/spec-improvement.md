# spec-improvement.md — App Improvement Map

_Last updated: 2026-03-24_

---

## Purpose

This document tracks the delta between `spec-refactoring.md` (the original baseline, dated 2026-03-15) and the current state of the app. It is the working reference for safe, incremental improvement.

Three sections:

1. **Resolved** — features and fixes added since the spec was written
2. **Pending** — known gaps and incomplete work
3. **Improvement backlog** — architectural and UX improvements, each with risk annotation

> **Rule:** before touching a module, verify current behavior against `spec-refactoring.md` §10 for that tab. This doc records intent; the spec records how things actually work. Both together prevent regressions.

---

## 1. Resolved since spec

These items were documented as absent or as constraints in the original spec and have since been addressed.

### 1.1 URL routing and two-level navigation
**Spec §16:** "No URL routing. Refreshing always opens to Overview."

**Resolved:** `js/url.js` implements full URL-based routing via `?research=<group>&tab=<subtab>`. `navigate(group, tab)` in `main.js` replaces `showTab(name)`. The nav is now two-level: group bar (top) + sub-tab bar (per group). Browser back/forward history is supported.

Files: `js/url.js`, `js/main.js`

---

### 1.2 Intro group / landing page
**Spec:** no landing page — app opened directly on Overview.

**Resolved:** `intro` is now the default group on load. It is a standalone pane with no sub-tabs, navigating to other groups via `data-navigate-group` buttons.

Files: `index.html`, `js/main.js`

---

### 1.3 European Defence Fund group (3 new tabs)
**Spec:** EDF data was handled entirely within `eucalls.js`.

**Resolved:** Full EDF group with 4 sub-tabs:
- `edfoverview.js` — EDF funding overview and statistics
- `edfmap.js` — geographic map of EDF beneficiaries (mirrors `map.js` architecture)
- `eucalls.js` — EDF Calls Search (existing, moved to EDF group)
- `edfbrowse.js` — EDF Beneficiaries browser

Files: `js/tabs/edfoverview.js`, `js/tabs/edfmap.js`, `js/tabs/edfbrowse.js`, `css/edfbrowse.css`

---

### 1.4 Shared EDF data module
**Spec:** `edf_calls.json` loaded inline inside `eucalls.js` only.

**Resolved:** `js/edf-data.js` is a singleton fetch with a cached promise. All EDF tabs share the same load — no redundant fetches.

Files: `js/edf-data.js`

---

### 1.5 Shared entity detail sidebar
**Spec:** each tab with entity detail used a tab-local slide-in panel.

**Resolved:** `js/detail-sidebar.js` provides three shared functions — `openCompanySidebar(entity)`, `openInvestorSidebar(investorMeta)`, `openIntroSidebar(title, html)` — used by `companies.js`, `investors.js`, `relationships.js`, and `main.js` (for overview/matrix entity clicks).

Files: `js/detail-sidebar.js`

---

### 1.6 Data Issues tab
**Spec:** not present.

**Resolved:** `js/tabs/knownissues.js` renders `docs/data-issues.md` via `marked` (CDN v9) into `#knownissues-body`. Accessible at `?research=about&tab=knownissues`. Labeled "Data Issues" in the UI.

Files: `js/tabs/knownissues.js`, `docs/data-issues.md`

---

### 1.7 Glossary tab
**Spec:** not present.

**Resolved:** `js/glossary.js` (root-level, not a tab module) renders the glossary and wires hover tooltips. Lazy-initialised on first visit like other About sub-tabs.

Files: `js/glossary.js`

---

### 1.8 AppState extensions
**Spec §6:** `ui` contained: `currentTab`, `matrix`, `companies`, `investors`, `relationships`, `graph`, `wikidata`, `eucalls`, `map`.

**Resolved:** `ui` now also contains:
- `currentGroup` — tracks active group (alongside `currentTab`)
- `edfoverview.built`, `edfmap.built`, `edfbrowse.built` — lazy-init guards (static in `state.js`)
- `knownissues` and `glossary` — lazy-init guards created dynamically in `main.js` on first visit

Files: `js/state.js`, `js/main.js`

---

### 1.9 New CSS and dependencies
- Added: `css/about.css` (About group scoping), `css/edfbrowse.css` (EDF Overview + EDF Beneficiaries)
- Added: `marked` v9 (CDN) for Markdown rendering in Data Issues tab
- Added: JetBrains Mono (Google Fonts) as monospace accent font

---

## 2. Pending

Known gaps that have not been addressed. All are tracked in `docs/issues.md` or implied by the current codebase state.

### 2.1 Tutorial / onboarding
**Source:** `docs/issues.md` Issue #10

The app lacks orientation for first-time users. The intro group is skipped immediately by anyone who bookmarks a direct URL. No explanation of the three groups or how to navigate between them.

**Proposed options:**
- Welcome modal on first visit (sessionStorage guard), collapsible
- Guided tour via shepherd.js / intro.js
- Static contextual copy added to each group's default landing pane

Risk: **low** — additive only, no existing logic to break.

---

### 2.2 `knownissues` and `glossary` built-guards are inconsistent with other tabs
`edfoverview`, `edfmap`, `edfbrowse` have their `built` guards declared statically in `state.js`. `knownissues` and `glossary` are created dynamically in `main.js`:

```javascript
if (!AppState.ui.knownissues) AppState.ui.knownissues = {};
AppState.ui.knownissues.built = true;
```

This means `AppState.ui.knownissues` is `undefined` until first visit, which breaks any code that reads it before then.

**Proposed fix:** add `knownissues: { built: false }` and `glossary: { built: false }` to `state.js` alongside the other EDF entries.

Risk: **low** — `state.js` change, no functional impact if done carefully.

Files: `js/state.js`, `js/main.js`

---

### 2.3 `about` and `data` tabs have no JS module
Both `#tab-about` and `#tab-data` are rendered entirely as static HTML in `index.html`. This is fine for now, but it means any dynamic content (e.g. pulling `_updated` date into the About tab, or rendering the schema into the Data tab) requires either a dedicated module or inline scripts.

**Note:** this is not a bug — static HTML is intentional and low-maintenance. Track here in case content grows.

Risk: **none currently** — do not act without a specific content requirement.

---

### 2.4 `detail-sidebar.js` not used by matrix, graph, or overview
These three tabs still use tab-local detail panels (`#mx-detail`, `#graph-detail`). The shared sidebar was added for Companies / Investors / Relationships. Matrix and Graph have more complex interaction requirements (filtered panel content, pinning, node highlighting) that made migration non-trivial.

**Note:** no urgent need to migrate. Track here so any work on matrix/graph detail panels is done with the sidebar architecture in mind.

Risk: **medium if migrated** — matrix and graph detail logic is tightly coupled to their render cycles.

---

## 3. Improvement backlog

Items from `spec-refactoring.md §16` (original known constraints) plus observations from the current codebase. Each item includes a risk rating and the files to touch.

---

### 3.1 No debounce on search inputs
**Origin:** spec §16

Companies, Investors, and Relationships search inputs re-render the full table on every keystroke. No `setTimeout` debounce exists in any of those modules.

**Impact:** negligible at current data size (~100 entities), noticeable if dataset grows significantly.

**Fix:** wrap the `input` event handler in a 150–200ms `setTimeout`/`clearTimeout` debounce in each module.

Files: `js/tabs/companies.js`, `js/tabs/investors.js`, `js/tabs/relationships.js`
Risk: **low** — isolated to each module's event wiring.

---

### 3.2 Graph simulations accumulate in AppState, never GC'd
**Origin:** spec §16

Every call to `buildGraphView()` creates a new D3 force simulation and stores it in `AppState.ui.graph.sim` / `simBi` / `simProj`. Old simulations are stopped but not destroyed — they hold references to DOM nodes that may have been replaced.

**Fix:** call `.stop()` on the existing simulation and set the reference to `null` before building a new one. Also remove D3 event listeners from replaced SVG elements.

Files: `js/tabs/graph.js`
Risk: **medium** — graph is the most complex module. Test all three modes and sector filters after any change.

---

### 3.3 Map state mixes D3 internals with UI state in AppState
**Origin:** spec §16

`AppState.ui.map` holds both display state (`showArcs`, `activeFilter`) and D3 rendering state (`svg`, `g`, `projection`, `centroids`, `zoom`). This makes it impossible to reset display state without also discarding the D3 scene.

**Fix:** separate into `AppState.ui.map.display` (resetable) and `AppState.ui.map.scene` (D3 references, never reset).

Files: `js/tabs/map.js`, `js/state.js`
Risk: **medium** — every reference to `AppState.ui.map.*` in `map.js` must be updated. No impact on other modules.

---

### 3.4 EDF Calls module-level state is outside AppState
**Origin:** spec §16

`eucalls.js` keeps 7 module-level variables (`currentData`, `currentPattern`, `currentYears`, `edfCallsList`, `edfCallsDb`, `acReady`, `acEnterBlocked`, `fundedOnly`, `participantStore`) entirely outside `AppState`. Cannot be inspected from devtools via `AppState`, and cannot be reset without reloading the tab.

**Fix:** move into `AppState.ui.eucalls` (which currently only holds `{ built: false }`). The module can still use local `const` aliases for convenience.

Files: `js/tabs/eucalls.js`, `js/state.js`
Risk: **medium** — `eucalls.js` is the most complex tab. Changes are self-contained but the module is large.

---

### 3.5 Wikidata cache is module-scoped and invisible
**Origin:** spec §16

`wdCache` (a `Map<QID, html>`) is declared in module scope in `wikidata.js`. Fetched results persist for the session with no way to invalidate, inspect, or clear from outside.

**Fix (minimal):** expose a `clearWdCache()` export and wire a UI button in the Wikidata tab. Or move the cache into `AppState.ui.wikidata.cache`.

Files: `js/tabs/wikidata.js`
Risk: **low** — purely additive if exposing a clear function. Slightly higher if moving to AppState (verify no circular import).

---

### 3.6 `WD_TO_ISO` country table in `map.js` is hardcoded
**Origin:** spec §16

The Wikidata label → ISO numeric mapping is a ~80-entry hardcoded object in `map.js`. Countries not in the table are silently ignored — no warning, no fallback.

**Fix (minimal):** log unmapped countries to the console during `buildMapView()` so missing entries are visible during development.
**Fix (structural):** move `WD_TO_ISO` to a standalone `js/country-map.js` module, shared between `map.js` and `edfmap.js` (which likely has its own copy or the same gap).

Files: `js/tabs/map.js`, `js/tabs/edfmap.js`
Risk: **low** — the table itself is data, not logic. Extraction is mechanical.

---

### 3.7 `spec-refactoring.md` is now outdated
The original spec describes the single-nav, 10-tab, pre-routing architecture. It no longer reflects current module structure, AppState shape, bootstrap flow, or navigation system.

**Options:**
- Update it in-place (risk: losing the original baseline for reference)
- Keep it frozen as a historical baseline and treat this document (`spec-improvement.md`) as the living architecture reference

**Recommended:** keep `spec-refactoring.md` frozen. Add a note at the top pointing to this document. Update `readme.md` accordingly.

Files: `docs/spec-refactoring.md`, `docs/spec-improvement.md`, `readme.md`
Risk: **none** — documentation only.

---

## Risk summary

| Item | Section | Risk | Effort |
|---|---|---|---|
| Debounce on search inputs | 3.1 | Low | Low |
| Expose Wikidata cache clear | 3.5 | Low | Low |
| Extract `WD_TO_ISO` to shared module | 3.6 | Low | Low |
| Fix `knownissues`/`glossary` built-guards | 2.2 | Low | Low |
| Tutorial / onboarding | 2.1 | Low | Medium |
| Add `spec-refactoring.md` obsolescence note | 3.7 | None | Low |
| Graph simulation GC | 3.2 | Medium | Medium |
| Separate map display/scene state | 3.3 | Medium | Medium |
| Move EDF Calls state into AppState | 3.4 | Medium | High |
| Migrate matrix/graph to detail-sidebar | 2.4 | Medium | High |
