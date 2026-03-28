# CHANGELOG — refactoring/

> **Note on versioning**: `refactoring/` is tracked in the single `infonodesETS/manintheloop` git repository. Two branches:
> - `main` — production; deployed via GitHub Pages at `https://infonodesets.github.io/manintheloop/`
> - `dev` — active development; merged into `main` when features stabilise
>
> This file is the human-readable change log for `refactoring/`. It complements git history with context, decisions, and data provenance that commit messages alone cannot capture.

> **Rule for AI assistants**: Every resolved issue from `issues.md` must produce a dated entry here. Data gap issues moved to `data-issues.md` must also be recorded here. No issue is closed without a CHANGELOG entry.

---

## Style architecture

See [`STYLE.md`](./STYLE.md) for the full living specification: token tables, CSS file scope, sidebar primitives, and rules.

**Quick rules:**

1. **No inline `style="…"` in HTML.** All visual properties go in CSS files.
2. **No inline styles in JS-generated HTML** except for data-driven values (dynamic width/color from runtime variables). Use CSS classes or `var(--token)` in inline styles when the value is truly dynamic.
3. **No hardcoded color/size literals** in CSS or JS — always `var(--token)`.
4. **`em` units are banned outside `.sidebar` context.** Use `rem` via `--fs-*` tokens.
5. **The `.sidebar` class** is reserved for panels using the em-cascade contract documented in `STYLE.md`.
6. **One canonical class per role** — no parallel equivalents.

---

## [2026-03-28] — data-issues.md #5 partial progress; #6 resolved

**Source:** `data-issues.md` #5, #6

### Resolved — #6 Officina Stellare budget discrepancy

Full audit of `edf_calls.json` (generated 2026-03-15): exactly 1 participation for OFFICINA STELLARE SPA (PIC 935106094) in call `EDF-2023-DA-SPACE-SSA`, `eu_contribution = €1,500,000` — matching the EU portal. `edfmap.js` aggregation is correct. The ~€2M figure was not reproducible with current data; likely an artefact of a pre-March-2026 snapshot. No code change needed.

### Partial progress — #5 Investors missing Wikidata IDs

2 ambiguous investor names resolved via Wikidata Playwright search:
- IV-0188 Santander → Q6496310 (Banco Santander, Spain). Previous search had returned German subsidiary as false match; confirmed correct entity is the parent group. Context: linked as investor to CODELCO and Sigma Lithium.
- IV-0080 Enova → Q5379469 (Enova SF, Norwegian government enterprise). Context: linked as investor to Elkem (Norwegian silicon company).

Remaining unresolvable: Bond, ESG, Matrix, REV, Third Point, JARE — no Wikidata entries found. Count updated: 101/240 null wikidata_id.

---

## [2026-03-28] — data-issues.md #9 fully resolved; UPDATE_PROTOCOL principle #6 added

**Source:** `data-issues.md` #9, `UPDATE_PROTOCOL.md`

### Resolved — #9 Multi-country and ambiguous country values

The 4 remaining non-standard country values in `database.json` were resolved via Wikidata Playwright lookup and normalised with full provenance history entries:

| Entity | Old | New | Evidence |
|---|---|---|---|
| IN-0059 Ferroglobe | `UK/Spagna` | `United Kingdom` | Q125144368 — HQ London |
| IN-0131 Rio Tinto | `Australia / UK` | `United Kingdom` | Q821293 — Rio Tinto plc, UK primary incorporation |
| IN-0143 Southern Copper Corporation | `USA / Mexico` | `United States` | Q7569806 — Delaware corp, HQ Phoenix AZ |
| IV-0088 European Union | `internationality` | `European Union` | Q458 — supranational entity |

`#5` investor count updated: 240 total entities, 103 with null `wikidata_id` (was 242/105 before entity merges).

### UPDATE_PROTOCOL: principle #6 added

Every `database.json` change must produce an **atomic, dedicated git commit** with a message naming affected entities, fields, and reason. Git log serves as external audit trail independent of in-JSON history. `validate.py` must pass before every push.

---

## [2026-03-28] — data-issues.md #1 resolved: EDF count mismatch explained

**Source:** `data-issues.md` #1

### Resolved — #1 EDF calls with projects: 63 vs 64

Root cause: `edfoverview.js` filters `eu_contribution > 0` (→ 63), `eucalls.js` counts `projects.length > 0` (→ 64). The 1-call discrepancy is `EDF-2022-FPA-MCBRN-MCM`, which has a project entry with null `eu_contribution`. Both counts are correct given their respective filter semantics. Labels are accurate. No code change needed.

---

## [2026-03-28] — data-issues.md #10, #11 resolved; #8, #12 removed

**Source:** `data-issues.md` #8, #10, #11, #12

### Resolved — #10 Anduril investors audit

Cross-checked all investor relationships in `database.json` against `raw-data/database-man-in-the-loop-aziende-siti-web-csv-3-6-2026.csv` (Top 5 Investors + Lead Investors fields). All 11 Anduril investor relationships are backed by the CSV source. The concern about "extra" investors was valid but the data is correct — Crunchbase exports both Top 5 and Lead Investors, and migrate.py imported all of them. No relationships removed. Cross-check also identified 4 spurious relationships across other entities (REL-0009, REL-0017, REL-0094, REL-0134) which were removed following the UPDATE_PROTOCOL spurious relationship procedure.

### Resolved — #11 Company name and country inconsistencies

- **Country names:** 69 fields normalised to canonical English forms across 59 entities (Cina→China, USA→United States, UK→United Kingdom, Giappone→Japan, etc.). Multi-country and ambiguous values (`Australia / UK`, `UK/Spagna`, `USA / Mexico`, `internationality`) deferred — tracked in `data-issues.md #9`.
- **Company name variants:** Full audit of `database.json` against CSV raw data. Resolved by merging 8 duplicate entities: IV-0010 (Amazon), IV-0031 (BHP), IV-0051 (Ma'aden), IV-0053 (Citibank), IV-0118 (HTGF High-Tech Gruenderfonds), IV-0122 (Inc — parse error), IV-0143 (Leonardo Company), IV-0153 (Microsoft), IV-0221 (Tianqi Lithium). All merges confirmed via Wikidata and raw CSV provenance. Retired IDs documented in `UPDATE_PROTOCOL.md`.

### Removed — #8 Cyrillic artefact in automated-investigation.html

`automated-investigation.html` was deleted from the repository (2026-03-28). Issue is moot.

### Removed — #12 Disclaimer for low-data countries

Deferred indefinitely — no UI work planned for this sprint. Removed from active issues.

---

## [2026-03-28] — Matrix removed; issues backlog pruned; docs aligned

**Source:** `infonodes-issues.md` #15, #48 + housekeeping
**Resolved:** #15, #48; deleted #01, #02, #03, #04, #14, #16, #17, #18, #22, #30, #33, #51, #53, #54; marked #21 ✅

### Removed — Matrix tab

- `index.html`: removed `<link css/matrix.css>`, Matrix nav button, entire `#tab-matrix` pane
- `index.html`: removed "investment matrix" from meta descriptions and intro copy
- `js/main.js`: removed `initMatrix`/`setMatrixSector`/`closeMxDetail` import, `'matrix'` from supply-chain tabs array, `case 'matrix'` from `restoreFromUrl`, `initMatrix()` call, matrix sector button + close button wiring
- `js/tabs/matrix.js` and `css/matrix.css` retained as archive files (not loaded)

### Changed — `docs/infonodes-issues.md`

- Deleted 14 issues: #01 #02 #03 #04 #14 #16 #17 #18 #22 #30 #33 #51 #53 #54 (editorial/architectural decisions deferred indefinitely or duplicates)
- Marked resolved: #15, #21, #48
- Applied missing `✅ RESOLVED` titles to 21 previously-resolved issues: #10 #11 #12 #23 #24 #25 #26 #27 #28 #34 #35 #36 #37 #38 #39 #41 #43 #45 #47 #49 #52

### Changed — `docs/STYLE.md`

- Removed `css/matrix.css` from CSS file scope table

### Changed — `readme.md`

- File map: added `infonodes-issues.md`, `infonodes-roadmap.md`; added `companysearch.css`; removed `matrix.css`
- Tab modules table: added `companysearch.js`; removed `matrix.js`
- Navigation table: removed Matrix from Supply Chain sub-tabs
- Roadmap section: removed stale issue count

---

## [2026-03-28] — SC Map: arcs hidden by default, outbound-only on click, higher contrast

**Source:** `infonodes-issues.md` #08, #09, #42
**Resolved:** #08, #09, #42

### Changed — `js/state.js`
- `map.showArcs`: `true` → `false` — arcs off by default

### Changed — `js/tabs/map.js`
- Arc layer initialised with `display:none` — hidden until country click or global toggle
- `showMapCountry()`: shows arc layer on click; dims all arcs where `d.src !== iso` (outbound only) **#09**
- `closeMapPanel()`: restores arc layer visibility based on `showArcs` toggle state
- `drawArcs()`: stroke range `[1,4]` → `[1.5,5]`; opacity range `[0.55,0.9]` → `[0.75,1.0]`; faint gradient end `0.07` → `0.18` **#08**

### Changed — `css/base.css`
- `--map-arc-color` dark: `#68ccd1` → `#40e8f0` (more saturated cyan) **#08**
- `--map-arc-color` light: `#0a5080` → `#0d6aaa` (brighter blue) **#08**

### Changed — `index.html`
- `#map-arc-toggle`: removed `checked` attribute — checkbox unchecked by default **#42**

---

## [2026-03-28] — Graph view: layout overhaul, routing, auto-fit, drag pin, export

**Source:** `infonodes-issues.md` #44, #55, #57, #60 + additional bug fixes and polish
**Resolved:** #44, #55, #57, #60

### Changed — `index.html`

- `#graph-filter-float` added inside `#graph-pane`: contains `#graph-search` (search input) and `#graph-sector-btns` (sector filter buttons). Positioned absolute top-right of the graph pane. **#57**
- `#graph-controls` now contains only the View buttons (Network / Bipartite / Projection). Companies/Investors toggle buttons hidden with `style="display:none"`.
- `#legend` restructured: "Roles" section (Manufacturer + Dual role items) removed. Legend is now right-aligned and compact.
- Default active sector button changed from `Startup` to `All`.

### Changed — `css/graph.css`

- `#graph-filter-float`: `position: absolute; top: 10px; right: 10px; z-index: 10; width: fit-content` — floating filter box anchored top-right. **#57**
- `#graph-sector-btns`: `flex-direction: column` — sector buttons stacked vertically.
- `#proj-filter-btns`: `display: none !important` — "All edges / Co-invest ≥2" filters permanently hidden.
- `#graph-controls`: `margin-right: 5%` — visual gap between view controls and legend.

### Changed — `css/components.css`

- `#legend`: `left: 0` removed; `right: 0; width: fit-content; border-left` — legend now compact and right-aligned, no longer spanning full viewport width.
- `#legend-body`: `flex: 1` → `width: auto`.

### Changed — `css/base.css`

- `--content-h`: removed `- var(--legend-h)` from all variants (default, `subnav-hidden`). Content now fills full available height since the legend is no longer a full-width bar. Eliminates the black gap below graph view.
- `--fs-svg-md`: `11px` → `13px` — graph node labels (`.glabel`) are now larger.

### Changed — `js/tabs/graph.js`

- **#60** — `graphShowPanel()` calls `setParams()` with `entity=<id>&entity-name=<slug>` after opening the detail panel. URL reflects selected node.
- **#60** — `closeGraphDetail()` deletes `entity` and `entity-name` from URL. Also fixed: now clears both `ghl` **and** `gdim` classes (previously only `ghl` was cleared, leaving nodes permanently dimmed after Escape/close).
- **#60** — `selectGraphEntity(id)` exported: finds entity by ID in `companyMap`/`invMap` and calls `graphShowPanel`. Used by `restoreFromUrl()` to reopen the panel on page load.
- **#55** — Added `svgFit(nodes)` helper: always re-reads live `clientWidth`/`clientHeight` from `#graph-svg`. All simulation `on('end')` callbacks now use `svgFit(nodes)` instead of stale closed-over `W`/`H`. Initial bounding-box fit wrapped in `requestAnimationFrame`.
- **#44** — Drag `on('end')` handler changed from `d.fx = null; d.fy = null` to `d.fx = d.x; d.fy = d.y` across network, bipartite, and projection. Nodes stay pinned at drop position. **#44**
- Imported `getParams`, `setParams` from `../url.js`.

### Changed — `js/main.js`

- **#60** — `restoreFromUrl()` case `'graph'`: added `if (p.entity) selectGraphEntity(p.entity)` — restores selected node on page load.
- Imported `selectGraphEntity` from `./tabs/graph.js`.
- Sector button selector updated from `#graph-controls .sf-btn` → `#graph-sector-btns .sf-btn` (3 occurrences).

### Changed — `js/state.js`

- `graph.sector` default: `'Startup'` → `'all'` — graph now shows all companies on fresh load with no sector param. Fixes "looks like a selected node" bug (only Startup subset was shown).

### Changed — `js/copy-ai.js`

- Graph snapshot: visible companies now render hierarchically — each company lists its investors as indented sub-items (`  - Investor1: Name (LEAD)`). Previously only flat company names were exported.

### Changed — `docs/STYLE.md`

- `--fs-svg-md` value updated: `11px` → `13px`.

---

## [2026-03-28] — #40: all panels moved to left side, full-height overlay fix, width harmonization

**Source:** `infonodes-issues.md` #40
**Resolved:** #40

### Changed — `css/components.css`

- `#mx-detail`: `border-left` → `border-right` (Matrix panel now on left).
- `.entity-sidebar` wrapper: `inset: 0` → `top: calc(var(--nav-h) + var(--tab-h) + var(--subtab-h)); left: 0; right: 0; bottom: 0` — overlay no longer covers topnav/tab bars. Fixes full-height issue reported for Companies and EDF Browse.
- `.entity-sidebar-panel`: `top:0; right:0` → `top:0; left:0`, `translateX(100%)` → `translateX(-100%)`, `border-left` → `border-right` — panel slides in from left.

### Changed — `css/graph.css`

- `#graph-detail`: `border-left` → `border-right`.

### Changed — `css/map.css`

- `#map-panel`, `#edfmap-panel`: `border-left` → `border-right`.

### Changed — `css/eucalls.css`

- `.ec-part-sidebar` wrapper: same `top: calc(...)` fix as `.entity-sidebar`.
- `.ec-part-sidebar-panel`: moved to left, `translateX(-100%)` slide, `border-right`, width changed from `--sl-w-sm` (380px) to `--sl-w-inline` (450px) — harmonizes with all other panels.

### Changed — `index.html`

- `#matrix-wrap`: `#mx-detail` moved before `#matrix-scroll` (left side).
- `#graph-layout`: `#graph-detail` moved before `#graph-pane` (left side).
- `#map-layout`: `#map-panel` moved before `#map-main` (left side).
- `#edfmap-layout`: `#edfmap-panel` moved before `#edfmap-main` (left side).
- Note: `#wd-sidebar` (Wikidata) was already on the left (`border-right`) — no change needed.

---

## [2026-03-28] — Navigation: clickable stat cards, EDF overview bar charts, edfmap/edfbrowse routing

**Source:** `infonodes-issues.md` #32 + new feature work
**Resolved:** #32

### Added — `js/tabs/overview.js`

- **#32** — Sector stat cards ("Companies by sector") are now clickable: clicking navigates to the Companies tab with that sector pre-filtered. Cards get `stat-card--link` class and `data-sector` attribute. Added "(click to filter)" hint in section label.

### Added — `js/tabs/edfoverview.js`

- Stat cards with natural navigation targets are now clickable (`stat-card--link`): "EDF Calls" → EU Calls tab, "Calls with Funded Projects" → EU Calls tab, "Funded Projects" → EDF Beneficiaries, "Unique Participants" → EDF Beneficiaries.
- "Countries by Participations" bar chart: each row is now clickable — navigates to EDF Map focused on the selected country.
- "Top Participants by Projects" bar chart: each row is now clickable — navigates to EDF Beneficiaries pre-filtered by organisation name. Replaced `<a href>` label links with full-row JS delegation.
- Added "(click to explore)" hints on both chart section titles.
- Imported `AppState` to support programmatic navigation.

### Added — `js/tabs/edfmap.js`

- Exported `selectEdfMapCountryByName(name)`: looks up a country by display name in `ms.countryData` and calls `showCountry(iso)`. Used for routing and cross-tab navigation.

### Changed — `js/state.js`

- `AppState.ui.edfmap`: added `pendingCountry: null` — stores a country name to select after lazy-init completes.
- `AppState.ui.edfbrowse`: added `pendingSearch: null` — stores a search string to apply after lazy-init completes.
- `AppState.ui.companies.sector`: `setCoSector()` now also updates `.sf-btn` active state, fixing the button highlight when navigating from Overview sector cards.

### Changed — `js/tabs/companies.js`

- `setCoSector(s)`: added `.sf-btn` active class toggle so the sector filter button is visually activated when called programmatically (e.g. from Overview cards).

### Changed — `js/main.js`

- Imported `selectEdfMapCountryByName` from `edfmap.js` and `restoreEdfbrowseUrl` from `edfbrowse.js`.
- `navigate()`: added pending country/search consumption for `edfmap` and `edfbrowse` panes — mirrors the existing `pendingCountry` pattern for SC Map.
- `restoreFromUrl()`: added `case 'edfmap'` — restores `?country=X` param on page load (pending if not yet built). Fixed `case 'edfbrowse'` — restores URL params even when tab is already built; falls back to `pendingSearch` for not-yet-built state.

### Changed — `css/components.css`

- Added `.stat-card--link`: `cursor: pointer` + hover border/box-shadow accent + label accent color on hover.
- Added `.ov-stats-hint`: small inline hint label for "(click to filter / explore)".

### Changed — `css/edfbrowse.css`

- `.eo-bar-row--link:hover`: background highlight + accent label color on hover.
- Removed `.eo-bar-link` / `.eo-bar-link:hover` — no longer used (replaced by full-row JS delegation).

---

## [2026-03-28] — Accessibility & UX polish: typography, contrast, map interaction, country palette

**Source:** `infonodes-issues.md` user test sessions (Laura, Davide, Andrea — 2026-03-27)
**Resolved:** #35 (partial), #36, #37, #39, #41, #43, #45, #49, #52, #59 + font-size token reassignment sweep

### Changed — `css/base.css`

- **`--fs-xs`** bumped from `.65rem` (~12.5px) to `.70rem` (~13.4px). New minimum floor: 13px. Inline comment and STYLE.md updated.
- **`--text-faint`** dark mode: `#6b6b6b` → `#757575` (contrast on `#000000`: 4.26:1 → 4.84:1 — now passes WCAG AA).
- **`--text-faint`** light mode: `#8a8780` → `#6c6966` (contrast on `#f8f7f4`: 2.97:1 → 4.63:1 — now passes WCAG AA). **#36**
- **`--dim`** light mode: `rgba(0,0,0,0.45)` → `rgba(0,0,0,0.60)` (contrast ~3.27:1 → ~5.09:1 — fixes all inactive nav button text in light mode). **#36**
- **`--map-arc-color`** token added (dark: `#68ccd1`, light: `#0a5080`). SC Map reads this at draw time via `getComputedStyle`; arc gradients now theme-aware. **#41**
- Light mode map tokens improved for country contrast: `--map-bg` `#dedad4→#d4d0ca`, `--map-land` `#c8c4bc→#bfbbb3`, `--map-data` `#b8ccb8→#8ab88a`, `--map-data-hover` `#a0b8a0→#72a872`, `--map-selected` `#7a9e7a→#4a7a4a`. **#41**
- `.ki-body p` font-size: `var(--fs-lg)` → `var(--fs-body)` — Data Issues tab body text aligned to scale. **#52**
- Added `.ctrl-group-lbl` utility class: xs, uppercase, bold, `--text-faint`, for toolbar group labels.

### Changed — `css/companysearch.css` — font-size token reassignment

Interactive elements bumped from `--fs-xs` → `--fs-sm`: `#cs-back`, `.cs-ext-link`, `#cs-export-btn`, `.cs-tag`, `.cs-card-hdr`, `.cs-rel-group-lbl`, `.cs-src-hdr`.
Reading content bumped from `--fs-sm` → `--fs-base`: `.cs-hist-desc`, `.cs-src-desc`.

### Changed — `css/map.css`

- Light mode override added: `[data-theme="light"] .edfmap-arc { stroke: rgba(10,80,128,0.55) }` — EDF Map arcs now visible in light mode. **#41**
- Interactive elements bumped from `--fs-xs` → `--fs-sm`: `.edfmap-back-btn`, `.edfmap-eu-link`, `.map-ctrl-btn`, `.map-filter-clear`.

### Changed — `css/graph.css`

- `#graph-hint` text: `--fs-sm` → `--fs-base`.

### Changed — `css/edfbrowse.css`

- `.eb-ext-link` (drawer link): `--fs-xs` → `--fs-sm`.
- Form/input elements bumped from `--fs-sm` → `--fs-base`: `#eb-search`, `#eb-funded-label`, `#eb-country-select`, `.eb-pg-btn`.

### Changed — `js/tabs/map.js`

- **#43** — SVG background click handler: replaced fragile `e.target === svg.node() || tagName === 'path' && !has-data` condition with `!classList.contains('has-data') && !classList.contains('map-node')`. Clicking empty ocean, background, or non-data country now reliably deselects.
- Arc color now reads `--map-arc-color` CSS token via `getComputedStyle` at draw time (theme-aware). **#41**

### Changed — `js/tabs/edfmap.js`

- **#49** — SVG background click handler added after zoom setup: clicking empty area calls `clearEdfMapFilter()` if a filter is active, else `closeEdfMapPanel()`. Mirrors SC Map behavior.

### Changed — `js/tabs/companysearch.js`

- **#37** — Validation flags card (`#cs-val-card`) always hidden. Internal `needs_review` / `flagged` metadata no longer exposed to end users.
- **#59** — Entity ID `<span class="cs-hdr-id">` now has `title="Database ID — internal identifier for this entity"`.

### Changed — `js/tabs/overview.js`

- **#39** — Geographic breakdown: replaced politically-connoted Western/China-Russia palette with continent-based coloring. New sets: `EUROPE` (#5b8dd9 blue), `AMERICAS` (#f0944d orange), `ASIA_PAC` (#9b6dd6 purple), `MENA` (#e8c44a amber), `AFRICA` (#5dbe8a teal). `alignColor()` renamed `continentColor()`. Legend updated to show continent names.

### Changed — `index.html`

- **#45** — Graph toolbar: added `<span class="ctrl-group-lbl">View</span>` before Network/Bipartite/Projection buttons and `<span class="ctrl-group-lbl">Sector</span>` before sector filter buttons. Existing `ctrl-sep` divider between groups is now flanked by labeled groups.

---

## [2026-03-26] — Company Search tab: full entity profile view, routing, and Intro integration

### Added — `css/companysearch.css` (new file)

- Full scoped stylesheet for the Company Search tab (`#cs-*` / `.cs-*` selectors only).
- Hero layout, search input, autocomplete dropdown, profile header card, stat bar, two-column section grid, entity list with `.cs-elist-link` hover styles, history diff block, source blocks (Crunchbase / Wikidata / infonodes), validation flags.
- `#tab-company-search { padding: 0; }` overrides `.tab-pane.scrollable` default padding so the hero fills edge-to-edge.

### Added — `js/tabs/companysearch.js` (new file)

- `initCompanySearch()` — wires search input (autocomplete, keyboard nav), back button, export button, and delegated click handler on `#cs-rel-body` for clickable entity links.
- `renderProfile(entity)` — full entity profile render using `AppState.derived.relMap` and `AppState.derived.otherRelMap`; investment and non-investment relationships separated.
- `selectEntity(entity)` — sets URL params `{ research:'company-search', entity:id, 'entity-name':slug }` and renders profile; `entity-name` is a cosmetic human-readable slug, not used by routing.
- `clearSelection()` — removes entity/entity-name from URL and shows search hero.
- `getSearchEntities()` — lazy-builds a deduplicated, name-sorted search list from `AppState.derived.entityMap`; cached on first call.
- `entityLink(other, fallback)` — renders `<button class="cs-elist-link" data-entity-id="…">` for clickable entity names in connection lists; plain text fallback when entity is unknown.
- `buildCompanySearchSnapshot()` — exported; produces rich Markdown for Copy for AI (profile data + all connections).
- `restoreCompanySearchUrl(p)` — exported; called from `main.js` when `group === 'company-search'` to restore entity from URL on page load.

### Changed — `js/state.js`

- Added `relMap: {}` and `otherRelMap: {}` to `AppState.derived`.
- Added `companysearch: { entityId: null }` to `AppState.ui`.

### Changed — `js/data.js`

- At end of `loadData()`: builds `relMap` (investment relationships) and `otherRelMap` (non-investment relationships) keyed by entity ID with `{ rel, role, other }` entries; stored in `AppState.derived`.

### Changed — `js/main.js`

- Imported `initCompanySearch` and `restoreCompanySearchUrl` from `./tabs/companysearch.js`.
- Added `'company-search': { tabs: null, defaultTab: null }` to GROUPS.
- `navigate()`: focuses search input when navigating to `company-search` pane.
- `restoreFromUrl()`: calls `restoreCompanySearchUrl(p)` when `group === 'company-search'`.
- Boot: calls `initCompanySearch()`.

### Changed — `js/copy-ai.js`

- Imported `buildCompanySearchSnapshot` from `./tabs/companysearch.js`.
- Added `case 'company-search': return buildCompanySearchSnapshot();` to `buildAiSnapshot()`.

### Changed — `index.html`

- Added `<link rel="stylesheet" href="css/companysearch.css">`.
- Nav: replaced `<a href="entity-profile.html">` with `<button class="tnav-btn" data-research="company-search">Company Search</button>` (second position, after Intro).
- Added `#tab-company-search` tab pane with `class="tab-pane scrollable"`.
- Intro: added Company Search as area `01 /` (Supply Chain→02, EDF→03, Data&About→04); added `→ Company Search` CTA button as first item in `intro-cta-row`.

### Changed — `entity-profile.html`

- Added all previously missing schema fields: infonodes source block, Tags card, `primary_industry` as link, `OTHER_RELS` non-investment relationships section, history old→new diff rendering, validation author/datestamp, Wikidata label row.
- File kept as standalone page; unlinked from main nav (routing is via `?research=company-search&entity=ID`).

### Fixed

- Company Search tab scroll: added `scrollable` class to `#tab-company-search` pane so `overflow-y: auto` applies; `padding: 0` in CSS prevents double padding from `.tab-pane.scrollable`.
- Clickable entity names in Investors / Portfolio connection lists: clicking navigates to that entity's profile within Company Search.
- Entity-name URL slug: `entity-name` param appended to URL for human readability (e.g. `?research=company-search&entity=IN-0008&entity-name=alpine-eagle`); ignored by routing logic.

---

## [2026-03-24] — Sirogja user test: 8 more UX/accessibility fixes (batch 2)

**Source:** `sirogja-issues.md` (resolved: #1, #4, #8, #11, #14, #17, #20, #21)

### Changed — `js/tabs/edfmap.js`

- **#8** — EDF Map arcs now have hover tooltips: "EDF partnership: [Country A] ↔ [Country B] (N shared projects)". Arc legend section added to intro panel ("Each arc connects two countries sharing at least one EDF-funded project…").

### Changed — `js/tabs/map.js`

- **#11** — SC Map flowing-in/out distinction improved: (a) arc hover tooltip now shows "Investor flow: [Src] → [Dst] (N connections)"; (b) sidebar section headers are now colour-coded: "Capital Flowing In" in accent green, "Capital Flowing Out" in amber (`#ff9944`) via CSS classes `.map-flow-in-hd` / `.map-flow-out-hd`.

### Changed — `js/tabs/graph.js` + `js/main.js`

- **#21** — SC Graph initial state: added a hint overlay (`#graph-hint`) positioned at the bottom of the graph pane with message "All nodes are visible — Filter by sector above, or search for a company or investor to focus the graph". Overlay auto-hides on first sector filter selection (non-"all"), search input, or node click.

### Changed — `index.html`

- **#1** — EDF acronym: EDF sub-nav buttons now have `title="European Defence Fund — [section]"` attributes so hovering reveals the full name. Glossary system (`data-gl="edf"`) already handles inline `EDF` terms in static content.
- **#20** — About > Data tab expanded: each data file now has a full provenance block (`origin`, `content`, `scope`, `update frequency`, `powers` list). External link to EU Funding portal added.

### Changed — CSS

- `css/components.css`: `.lg-item` text brightened from `var(--dim)` → `var(--text-secondary)`, font raised to `var(--fs-sm)`, dot size 8→9px; `.lg-label` text to `#fff`; `.lg-group-label` to `var(--text-tertiary)` — **#14** legend more visible
- `css/map.css`: added `.map-flow-in-hd` (accent green) and `.map-flow-out-hd` (amber) for flowing-in/out section headers — **#11**; EDF Map compact panel overrides (`#edfmap-panel .eb-det-*`) bumped from `var(--fs-xs)` → `var(--fs-sm)` for detail rows and metadata — **#17**
- `css/map.css`: `.edfmap-org-filter-input` border raised to `rgba(255,255,255,0.3)`, background to `rgba(255,255,255,0.07)`, placeholder from `var(--text-faint)` → `var(--text-muted)` — **#4**
- `css/graph.css`: added `#graph-hint` overlay — **#21**
- `css/components.css`: added `.a-data-meta`, `.a-ext-link` for About > Data expanded content — **#20**

---

## [2026-03-24] — Sirogja user test: 8 UX/bug fixes

**Source:** `sirogja-issues.md` (resolved: #2, #5, #6, #7, #12, #13, #15, #16)

### Fixed — `js/tabs/edfmap.js`

- **#2/#5** — EDF Map: clicking ✕ Clear on an org filter now restores the country panel (org list + partners) instead of leaving a blank sidebar. Added `ms.selectedCountry` tracking; `clearEdfMapFilter()` calls `showCountry(ms.selectedCountry)` when active. `closeEdfMapPanel()` clears `ms.selectedCountry`.
- **#6** — EC Portal link (`↗`) changed from large green badge to a small bordered text link (`↗ EC Portal`). Applied in both `edfmap.js` and `edfbrowse.js` (project item headers). Affects all three `eb-ext-link` usages.
- **#7** — EDF Map country panel now shows total EU contribution alongside the org count (e.g. "68 Organisations · €314M EU contribution"). Computed from `cd.orgs.reduce(sum, eu_total)` in `showCountry()`.

### Fixed — `js/tabs/map.js`

- **#15** — SC Map entity filter now forces arc layer visible when a filter is active (regardless of the arc toggle state), and restores to the `showArcs` state when filter is cleared. Was: arcs stayed hidden if the toggle was OFF when a filter was applied.
- **#12** — SC Map country panel now shows an explicit italicised note ("↓ No inbound cross-border investments recorded" / "↑ No outbound…") when the corresponding flow is absent. Was: absent flow sections were silently omitted.

### Fixed — `js/tabs/graph.js`

- **#13** — SC Graph: clicking a node now dims all unconnected nodes and links (opacity 0.12, CSS class `gdim`). Was: only highlighted connected nodes without dimming others. Deselect (background click or search clear) restores full opacity.

### Changed — `js/tabs/edfoverview.js`

- **#16** — EDF Overview: top participants list items are now clickable links that navigate to EDF Beneficiaries filtered by org name (`?research=edf&tab=edfbrowse&search=<name>`). `renderBar()` accepts an optional `href` param; participant bars use it, country bars do not.

### Changed — CSS

- `css/edfbrowse.css`: `.eb-ext-link` restyled — `font-size: var(--fs-xs)`, `color: var(--accent)`, transparent background, border instead of filled; added `.eo-bar-link` and `.eo-bar-row--link` for clickable participant rows
- `css/map.css`: added `.map-no-flow` (italic, faint, small) and `.edfmap-country-stats`/`.edfmap-country-budget` for country panel budget stat
- `css/graph.css`: added `.gnode-co.gdim`, `.gnode-inv.gdim` (opacity 0.12) and `.glink.gdim` (stroke-opacity 0.06)

---

## [2026-03-24] — Typography: centralised font-size and line-height token system

**Strategy source:** analysis of Medium and Substack type scales (√φ ≈ 1.27× / major third 1.25× ratio), matched against existing token inventory.

### Added — `css/base.css`

- `--lh-tight: 1.2` / `--lh-snug: 1.35` / `--lh-body: 1.55` / `--lh-loose: 1.65` — four line-height tokens covering all typographic contexts
- Root comment updated: documents `html { font-size: 120% }` as authoritative (1rem = 19.2px, Medium-range editorial base) and 12px as the minimum floor
- Em-cascade contract comment added to `--scale-sidebar` block

### Removed — `css/base.css`

- `--scale-wd-sidebar: 1.38rem` — was defined but unused throughout the codebase

### Changed — `css/base.css`

Sidebar typography tokens simplified to alias the main scale (no independent values):
- `--sl-title-fs`: `1.56rem` → `var(--fs-xl)` (~31.7px, +2px)
- `--sl-section-lbl-fs`: `.85rem` → `var(--fs-base)` (~16.8px, +0.5px)
- `--sl-row-lbl-fs`: `.85rem` → `var(--fs-base)` (~16.8px, +0.5px)
- `--sl-row-val-fs`: `.98rem` → `var(--fs-body)` (~19.2px, +0.4px)
- `--sl-desc-fs`: `1.04rem` → `var(--fs-body)` (~19.2px, −0.4px)

### Changed — CSS hardcoded font-sizes → tokens

| File | Selector | Was | Now |
|---|---|---|---|
| `graph.css` | `.gv-btn` | `.75rem` | `var(--fs-sm)` |
| `graph.css` | `#graph-search` | `.75rem` | `var(--fs-sm)` |
| `map.css` | `.edfmap-proj-acronym` | `0.82rem` | `var(--fs-base)` |
| `map.css` | `.edfmap-proj-title` | `0.75rem` | `var(--fs-sm)` |
| `map.css` | `.edfmap-role-badge` | `0.65rem` | `var(--fs-xs)` |
| `map.css` | `.edfmap-proj-partners` | `0.7rem` | `var(--fs-xs)` |
| `edfbrowse.css` | `.eb-dr-field` | `.75em` | `var(--fs-sm)` |
| `edfbrowse.css` | `.eb-mono` | `.78em` | `var(--fs-sm)` |
| `edfbrowse.css` | `.eb-ext-link` | `1.2rem` | `var(--fs-lg)` |
| `wikidata.css` | `.country-filter-btn` | `.72em` | `var(--fs-sm)` |

Kept as raw values (intentional, not typographic): `18px` on `.sl-close`, `7px` on `.dot-lead::after`, `1` on stat/icon/button line-heights.

### Changed — CSS hardcoded line-heights → tokens (22 instances across 7 files)

`base.css`, `eucalls.css`, `map.css`, `edfbrowse.css`, `graph.css`, `components.css`, `about.css` — all hardcoded `1.1`/`1.2`/`1.4`/`1.5`/`1.55`/`1.6`/`1.65` replaced with `var(--lh-*)`.

### Changed — JS inline font-sizes → `var(--token)` (16 instances across 7 files)

`main.js`, `tabs/overview.js`, `tabs/matrix.js`, `tabs/quality.js`, `tabs/wikidata.js`, `tabs/edfoverview.js`, `helpers.js` — all hardcoded `.68rem`–`.9rem` literals replaced with `var(--fs-xs)`, `var(--fs-sm)`, or `var(--fs-base)`.

### Also updated — style architecture spec (top of this file)

Token system section updated to reflect new `--lh-*` tokens and `--sl-*` alias structure.

---

## [2026-03-23] — EDF Map: arcs off by default, sidebar open by default with navigation guide

**Files:** `js/tabs/edfmap.js`, `index.html`

- `ms.showArcs` initialised to `false`; arc layer starts hidden on map draw
- `showCountry()`: always reveals arc layer when a country is clicked (only arcs touching that country)
- `applyFilter()`: reveals arc layer when an org filter is active
- `resetVisuals()`: hides arc layer again if toggle is off (respects `ms.showArcs`)
- `index.html`: `edfmap-arc-toggle` checkbox unchecked by default
- `drawMap()`: sidebar opened immediately with intro text, dataset stats, and "How to navigate" guide

---

## [2026-03-23] — EDF Map: project detail dropdown in org sidebar (same pattern as EDF Beneficiaries)

### Changed — `js/tabs/edfmap.js`

- `ms`: aggiunto `rawCallsMap` per accesso ai dati raw dei progetti
- `buildData`: salva `callsMap` in `ms.rawCallsMap`
- Aggiunto helper `fmtDate(s)`
- `filterByOrg`: rendering progetti sostituito con struttura identica a EDF Beneficiaries — `eb-proj-item--clickable`, `eb-proj-header` (caret, acronym, title, role badge, status, `↗`), `eb-proj-meta` (call_id, EU contrib, date), `eb-proj-detail` (dropdown con Call title, Total budget, Participants, Objective); lookup raw project via `ms.rawCallsMap[callId].projects.find(r => r.acronym === projAcronym)`
- Aggiunto click delegation su `panelBody` per toggle `eb-proj-detail.open` e rotazione caret

### Source
Screenshot: `edfmap-proj-dropdown.png`

---

## [2026-03-23] — EDF Map: Partner Countries section in country sidebar

### Changed — `js/tabs/edfmap.js`

- Nuova funzione `renderPartnersRow(iso, orgKeys)`: calcola i paesi partner dagli `orgProjectsMap` degli org visibili; li ordina per conteggio progetti condivisi; renderizza chip inline in `#edfmap-partners-row`
- `showCountry`: aggiunta sezione "Partner Countries" con `#edfmap-partners-row` sopra la lista org; chiamata iniziale con tutti gli org del paese
- Filtro org (`edfmap-org-filter`): oltre a nascondere le righe, raccoglie i `visibleKeys` e chiama `renderPartnersRow` — i partner countries si aggiornano in tempo reale mostrando solo i paesi connessi alle org filtrate

### Changed — `css/map.css`

- Aggiunte: `.edfmap-partners-row` (flex wrap, gap 5px), `.edfmap-partner-tag` (chip teal border-radius), `.edfmap-partner-count` (mono accent), `.edfmap-partner-none`

### Source
`japi-issues.md` #15 → resolved. Screenshot: `15-edfmap-italy-partners.png`, `15-edfmap-italy-partners-filtered.png`

---

## [2026-03-23] — EDF Beneficiaries: font sizes, inline detail rows, ext link style

### Changed — `css/edfbrowse.css`

- All row content (`eb-org-name`, `eb-org-type`, `eb-country-tag`, `eb-num`, `eb-dim`, `eb-coord-badge`, `eb-caret-cell`) → `var(--fs-body)`
- All proj item content (`eb-proj-acronym`, `eb-proj-title`, `eb-role-badge`, `eb-proj-status`, `eb-proj-meta`, `eb-proj-caret`, `eb-proj-count`, `eb-ext-link`, `eb-det-row`, `eb-det-lbl`, `eb-det-val`, `eb-det-objective`) → `var(--fs-body)`
- `.eb-det-rows-inline`: nuova classe wrapper — le tre righe (Call | Total budget | Participants) rese inline con separatore `|` via `::before`
- `.eb-ext-link`: `↗` link restyled — background `var(--accent)`, colore `#000`, bold, `font-size: 1.2rem`, border-radius 3px

### Changed — `js/tabs/edfbrowse.js`

- `buildDrawer`: righe inline (Call, Total budget, Participants) wrappate in `eb-det-rows-inline`; objective resta sotto separata

---

## [2026-03-23] — EDF Beneficiaries: project detail dropdown in org sidebar

### Changed — `js/tabs/edfbrowse.js`

- `buildDrawer`: ogni `eb-proj-item` ora pre-genera un `eb-proj-detail` con dati dall'lookup in `rawCallsMap` — Call title, Total budget, Participants count, Objective (max 160px scroll); aggiunto `eb-proj-caret` (›) nell'header; classe `eb-proj-item--clickable`
- `initEdfbrowse`: aggiunto click handler per delega su `#edf-sidebar` — click su `eb-proj-item--clickable` toglla `eb-proj-detail.open` e ruota il caret; i link `↗` non intercettati

### Changed — `css/edfbrowse.css`

- Aggiunte: `.eb-proj-item--clickable` (cursor pointer, border-left accent su hover), `.eb-proj-caret` (rotazione 90° su `.open`), `.eb-proj-detail` (hidden → `.open` display block), `.eb-det-row` / `.eb-det-lbl` / `.eb-det-val`, `.eb-det-objective` (max-height 160px, overflow-y auto)

### Source
`japi-issues.md` #21 → resolved

---

## [2026-03-23] — EDF Calls: comparison view fix, inline styles cleanup, accordion container

### Changed — `js/tabs/eucalls.js`

- `buildComparisonTable`: nasconde la card "Comparison View" quando `yearsDisplay.length < 2` (un solo anno = niente da confrontare)
- `projectCard`: inline styles rimossi → classi CSS dedicate: `.ec-part-role`, `.ec-part-country`, `.ec-no-participants`, `.ec-objective-scroll`; rimosso `bg-light` da `card-header`

### Changed — `index.html`

- `#ec-yearsAccordion`: rimosso `class="accordion"` — il container non usa più Bootstrap accordion

### Changed — `css/eucalls.css`

- Aggiunte: `.ec-part-role` (`opacity:.6; font-size: var(--fs-sm)`), `.ec-part-country` (`opacity:.5; font-size: var(--fs-sm)`), `.ec-no-participants`, `.ec-objective-scroll` (`max-height:480px; overflow-y:auto`)

### Source
`japi-issues.md` #17 → resolved, #20 → confirmed resolved

---

## [2026-03-23] — EDF Calls: dropdown label, item layout, font sizes

### Changed — `index.html`

- Label semplificata: `Topic Identifier or Call Title — try: …` → `Search EDF Calls — by title, keyword, or identifier`

### Changed — `js/tabs/eucalls.js`

- `renderDrop`: invertito ordine — `live-label` ora mostra il titolo del call (prominente), `live-desc` mostra l'identifier + status dot + deadline (secondario)

### Changed — `css/wikidata.css`

- `.live-drop-item`: `font-size: .85em` → `var(--fs-body)`
- `.live-drop-item .live-desc`: `font-size: .75em` → `var(--fs-body)`

### Changed — `css/eucalls.css`

- `.ec-header-note`: `var(--fs-sm)` → `var(--fs-body)`

---

## [2026-03-23] — EDF Calls: dropdown aperto di default al caricamento

### Changed — `js/tabs/eucalls.js`

- `applyCallsList()`: aggiunta chiamata `showDropFiltered('')` dopo `acReady = true` — il dropdown dei call si apre automaticamente quando i dati sono pronti, senza richiedere click sull'input
- Source: japi-issues.md #18 → resolved

---

## [2026-03-22] — EDF Map: organisation filter input in sidebar

### Added — `js/tabs/edfmap.js`

- Text input below "N Organisations" label — filters org rows in real-time on `input` event; non-matching rows hidden via `display: none`; matching is case-insensitive substring on org name

### Added — `css/map.css`

- `.edfmap-org-filter-input`: full-width input styled to match dark theme; accent border on focus

---

## [2026-03-22] — SC Map: sidebar UX — open by default, toggles, sector row, width

### Changed — `js/tabs/map.js`

- **Sidebar open by default**: `#map-panel` no longer starts hidden (`d-none` removed from HTML); `drawMap` populates it with intro title + three explanatory paragraphs on load
- **`closeMapPanel` reset**: instead of hiding the panel, ✕ button now resets it to the intro content (panel always visible)
- **Companies toggle**: `on/off` button (`.sf-btn`) inline in the Companies section header — hides/shows the company list without affecting arcs
- **Flow In / Flow Out toggles moved inline**: removed top `map-flow-toggles` bar; each toggle is now a `.sf-btn` button inside its own section header (↓ Capital Flowing In / ↑ Capital Flowing Out); toggling off hides both the sidebar list and dims the corresponding arcs
- **Sector row replaces By Sector section**: compact `Sectors: Defence (5), Startup (4), …` line at the top of panel body, sorted by count descending; uses `.map-sector-row` / `.map-sector-lbl`

### Changed — `css/map.css`

- Removed `.map-flow-toggles` and `.map-toggle-label` (no longer used)
- Added `.map-sector-row` (`font-size: var(--fs-base)`) and `.map-sector-lbl` for the inline sector summary
- Added `.map-section-hd` (`display: flex; align-items: center; gap: 8px`) for section headers with inline toggle buttons

### Changed — `css/base.css`

- `--sl-w-inline`: **300px → 450px** — applies to all inline panels (SC Map, EDF Map, Graph, Matrix)

---

## [2026-03-22] — SC Map: arc model fix, country name normalization, drill-down sidebar

### Fixed — `js/tabs/map.js`

- **Country alias mapping**: aggiunto supporto per nomi italiani e abbreviazioni presenti nel database (`Cile`, `Germania`, `Francia`, `Norvegia`, `Polonia`, `Belgio`, `Cina`, `Giappone`) e alias inglesi (`UK`, `USA`, `Czech Rep.`, `EAU (Dubai)`, `People's Republic of China`) in `WD_TO_ISO`
- **ISO_TO_NAME**: ricostruito con "first-occurrence wins" (loop `for...of`) invece di `Object.fromEntries` che prendeva l'ultimo valore — ora i nomi canonici inglesi (inseriti per primi) vincono anche quando ci sono alias successivi
- **Display names**: `cd.name` ora usa `ISO_TO_NAME[iso] || country` — tutti i paesi mostrano nomi canonici inglesi nella mappa, sidebar, tooltip (es. "Chile" non "Cile", "Germany" non "Germania")
- **Cross-border arc pairs**: da 29 a 41 — CODELCO (Cile) ora genera archi verso UK, USA, France, Germany; altri paesi con nomi italiani/abbreviati ora inclusi correttamente
- **Investor lookup**: `showMapCountry` ora matcha per ISO code (`WD_TO_ISO[compCountry] === iso`) invece che per stringa (`cd.name`) — robusto per tutti gli alias dello stesso paese
- **Drill-down sidebar**: `filterMapByEntity(entityId, fromIso)` implementa sidebar a due livelli come EDF Map: click su company/investor → dettaglio entità con investors o portfolio + pulsante "← Back" che ripristina vista paese
- Source: japi-issues.md #6 → resolved; Playwright test: `screenshots/map-chile-arcs-fixed.png`, `screenshots/map-chile-final.png`

---

## [2026-03-22] — SC Map: directed arcs, gradient, node sizing, centroid overrides, zoom labels, flow toggles

### Changed / Added — `js/tabs/map.js`

- **Directed arc model**: chiave da `[compISO, invISO].sort().join('-')` (non direzionale) a `invISO→compISO` — `src` = investitore, `tgt` = company; archi totali da 41 → 45 (directed pairs)
- **SVG linearGradient per arco**: `gradientUnits="userSpaceOnUse"`, origine all'investitore (`src`) con `stop-opacity: 0.07`, destinazione alla company (`tgt`) con opacità scalata sul peso; usa `url(#gradId)` come stroke
- **Node sizing by arc degree**: dimensione nodi proporzionale al numero di archi connessi (`arcDegree[src]++ / arcDegree[tgt]++`) via `d3.scaleSqrt` — rivela hub finanziari (Luxembourg, Saudi Arabia, Switzerland) vs concentrazioni di company
- **CENTROID_OVERRIDES**: coordinate geografiche manuali per Francia (2.3, 46.2), Paesi Bassi (5.3, 52.1), Portogallo (-8.0, 39.5), UK (-2.0, 54.0), USA (-98.0, 39.5) — France centroid era sbagliato per i territori d'oltremare nel topojson
- **Label zoom scaling**: sostituito `attr('font-size', ...)` con `style('font-size', ...)` nello zoom handler — il CSS `.map-label` sovrascriveva `attr()`; `baseFs / k` ridimensiona le label proporzionalmente allo zoom
- **Capital Flowing In / Out sidebar**: sezioni separate per investitori esteri in company locali (↓ In) e investitori locali in company estere (↑ Out)
- **Flow direction toggle filters**: checkbox "↓ In" e "↑ Out" nella sidebar country-detail; `updateArcVisibility()` applica `arc-dim` via `d.tgt === iso` (in) / `d.src === iso` (out); toggle renderizzati solo se la direzione esiste nel dataset (es. Saudi Arabia mostra solo "↑ Out")

### Changed — `css/map.css`

- `.map-arc`: rimossi `stroke` e `stroke-opacity` (ora gestiti dal gradient SVG); transizione su `opacity` invece di `stroke-opacity`
- `.map-arc.arc-dim`: usa `opacity: 0.06` (non `stroke-opacity`) perché gradient stroke non risponde a `stroke-opacity` sull'elemento
- `.map-label`: rimosso `font-size` dalla regola CSS — ora controllato esclusivamente da JS via `style()`
- Aggiunta `.map-flow-toggles` per i toggle In/Out nella sidebar

---

## [2026-03-22] — EDF Map: rimosso transform hardcoded, fix centering

### Changed — `js/tabs/edfmap.js`

- Rimossi `d3.zoomIdentity.translate(-2926, -261).scale(3.647)` da init e da `resetEdfMapZoom()` — sostituiti con `d3.zoomIdentity`
- La proiezione `geoNaturalEarth1` con `translate([W/2-100, H/2+50])` centra già il mondo correttamente; il transform aggiuntivo spostava la mappa sull'Asia
- Source: japi-issues.md #13 → resolved

---

## [2026-03-22] — Overview headers: Supply Chain e EDF

### Changed — `index.html`, `css/base.css`

- Aggiunto blocco `.ov-header` in `tab-overview` (Supply Chain) e `tab-edfoverview` (EDF): `intro-prompt` (comando mono) + `ov-title` (titolo grande) + `intro-desc` (testo descrittivo con glossary terms)
- `.ov-header`: `max-width: 680px; margin: 0 auto 28px` — stesso centramento di `.intro-wrap`
- `.ov-title`: dimensionato con `--fs-stat`, coerente con la scala tipografica esistente

---

## [2026-03-22] — User test (Japi): session 2 — navbar, map, legend, overview

### Changed — `index.html`, `js/main.js`, `js/glossary.js`, `js/tabs/map.js`, `js/tabs/overview.js`, `css/map.css`, `css/components.css`

- **NAV-A** — Gruppo "Data" rimosso dalla navbar. Known Issues, Data Quality, Wikidata Inspector spostati come sub-tab di "About". `GROUPS['data']` eliminato; `GROUPS['about']` ora ha `tabs: ['about','knownissues','quality','wikidata','data','glossary']`, `defaultTab: 'about'`. (japi #22 → resolved)
- **NAV-B** — Aggiunti due nuovi sub-tab in About: "Data" (`tab-data`) con link download a `database.json` e `edf_calls.json`; "Glossary" (`tab-glossary`) con rendering dei termini da `GLOSSARY`. `glossary.js` esporta `renderGlossaryTab()`. CSS: `.gl-entry`, `.a-data-file`, `.a-data-link`, `.a-data-desc` aggiunti a `components.css`.
- **NAV-C** — Intro area 03: `data-navigate-group` aggiornato da `data` a `about`, label "Data & About →". Brand-wip link: `?research=data` → `?research=about`.
- **MAP-A** — Map filter bar: `applyMapFilter()` ora chiamata a fine `drawMap()` — risolve bug per cui la bar mostrava "Filtering: [x Clear]" di default (cascading CSS: `.map-filter-bar { display: flex }` sovrascriveva `.hidden { display: none }`). (japi #6 partial)
- **MAP-B** — Map sidebar: click su company/investor aggiunge classe `.active` con stile persistente (border-left accent + background verde). Click ripetuto toglie filtro e classe. CSS `.map-co-item.clickable.active` aggiunto in `map.css`. (japi #6 partial)
- **LG-A** — Legend: label "Legenda" → "Legend". Visibilità ristretta a `tab=graph` (prima era visibile su tutto il gruppo supply-chain). `main.js`: `group !== 'supply-chain'` → `resolvedTab !== 'graph'`.
- **OV-A** — Supply Chain Overview: rimossa tile "Wikidata cov. X%" da `stats[]` in `overview.js`.
- **GL-A** — `.gl-term` border-bottom: `1px` → `3px dashed`.
- **OV-B** — Stat tile tooltip: sostituito approccio `::after` CSS (tagliato da `overflow-y: auto`) con `title` nativo su `.stat-card`. `overview.js` importa `GLOSSARY` e imposta `title` sulla card.

### Source
`japi-issues.md` #6 (partially resolved), #22 (resolved)

---

## [2026-03-22] — Intro: fix overflow verticale (content nascosto sotto navbar)

### Changed — `css/base.css`

- `#tab-intro`: cambiato da `flex-direction: row; align-items: center; justify-content: center` a `flex-direction: column; align-items: center` — con column-flex l'overflow finisce in basso (scrollabile), non in alto (irraggiungibile)
- `.intro-wrap`: aggiunto `margin: auto` — centra verticalmente quando c'è spazio, collassa a 0 quando il contenuto è più alto del container (comportamento corretto per scroll)

---

## [2026-03-22] — Tier 4: L-A — Legenda spostata in footer bar

### Changed — `index.html`, `css/base.css`, `css/components.css`, `js/main.js`

- **L-A** — Legenda settori spostata da posizione inter-navbar (confusa con elementi interattivi) a footer bar fissato in basso (`position: fixed; bottom: 0`)
- Rimosso `#legend-toggle` dalla topnav e il relativo JS handler
- Aggiunta label "Legenda" come primo elemento della bar
- Layout aggiornato: `#content` usa `margin-top: tab-h + subtab-h` (senza più `legend-h`); altezza rimane `100vh - nav-h - tab-h - subtab-h - legend-h` per fare spazio al footer
- Rimosso `--legend-top` token e tutte le regole `body.legend-closed`
- `border-bottom` → `border-top` e `top` → `bottom` su `#legend`

---

## [2026-03-22] — EDF Calls: leggibilità testi (TESTO 1 + TESTO 2)

### Changed — `index.html`, `css/eucalls.css`

- **TESTO 1** — Header note paragrafi: rimosso `text-muted` Bootstrap da `<p class="mb-0 ec-header-note">` (sovrascriveva `color` del token); `.ec-header-note` portato a `color: var(--text-primary)`; aggiunto `.ec-progress-msg` per il paragrafo di stato nella sezione progress
- **TESTO 2** — Comparison View table: aggiunto `--bs-table-bg: transparent` e `--bs-table-striped-bg: transparent` su `.table` per evitare sfondo bianco Bootstrap; aggiunto `color: var(--text-primary); background-color: transparent` su `td`; `table-hover` row override con `!important`

---

## [2026-03-22] — User test (Japi): Tier 3 — 5 fix JS behaviour

### Changed — `js/tabs/graph.js`, `js/tabs/map.js`, `js/tabs/eucalls.js`, `css/map.css`

- **G-A** — Graph: `closeGraphDetail()` ora azzera le classi `ghl` su `_nd` e `_lk`; aggiunto listener `keydown Escape` in `initGraph()` che chiama `closeGraphDetail()` quando il tab Graph è attivo
- **M-A** — Map filter bar: resa più prominente con `background`, `border-top/bottom`, `font-size: var(--fs-base)`, `font-family: var(--font-mono)`
- **M-B** — Map entity filter: `filterMapByEntity()` ora toglla il filtro se l'entità cliccata è già quella attiva (`activeFilter?.id === entityId` → `clearMapFilter()`)
- **EDF-C-C** — EDF search scope: aggiunto campo `desc` in `edfCallsList` (600 char dalla descrizione); `showDropFiltered` esteso per matchare anche su `c.desc`
- **EDF-C-F** — (coperta da EDF-C-C) ricerca per parola chiave ora trova risultati anche nelle descrizioni dei call

---

## [2026-03-22] — User test (Japi): Tier 2 — 4 fix JS/HTML

### Changed — `index.html`, `js/tabs/eucalls.js`, `css/eucalls.css`

- **G-C** — Graph: aggiunti `title` descrittivi ai 3 bottoni Network / Bipartite / Projection
- **EDF-M-A** — Già fixata: `edfmap.js` aveva già `zoom.transform translate(-2926,-261) scale(3.647)`. Confermata e chiusa.
- **EDF-C-B** — EDF Calls: placeholder aggiornato con esempi concreti (`CYBER, EDF-2023-DA-GROUND, drone…`); aggiunto hint inline sulla label
- **EDF-C-D** — Accordion rimosso: `createAccordionItem` riscritta con `ec-year-block` statico sempre visibile; aggiunto CSS `.ec-year-header` / `.ec-year-body`

---

## [2026-03-22] — Wikidata Inspector spostato in gruppo Data; Tools rimosso dalla navbar

### Changed — `index.html`, `js/main.js`

- Rimosso gruppo "Tools" dalla group nav e dal sub-nav
- Wikidata Inspector spostato in `snav-group[data]` (primo sub-tab, default)
- `GROUPS['data']` ora include `['wikidata','quality','knownissues']`
- Intro area "03 / Tools" aggiornata a `data-navigate-group="data"`

---

## [2026-03-22] — User test (Japi): Tier 1 — 5 fix CSS/HTML

### Changed — `css/components.css`, `css/graph.css`, `css/eucalls.css`, `css/edfbrowse.css`, `css/matrix.css`, `index.html`, `js/tabs/edfbrowse.js`

- **C-A** — Sidebar investors: `justify-content: space-between` → `flex-start` su `.es-list li`; aggiunto `margin-left: auto` su `.badge-lead` per mantenerlo a destra quando presente
- **G-B** — Graph toolbar: aggiunto `background: rgba(0,0,0,0.70)` + `border-radius` + `padding` + `backdrop-filter` a `#graph-controls`
- **EDF-C-A** — EDF Calls header note: aggiunto `font-family: var(--font); color: var(--text-secondary)` su `.ec-header-note`
- **EDF-B-B** — Beneficiaries: aggiunto `<td class="eb-caret-cell">›</td>` in ogni riga; caret accent-colored, si illumina su hover
- **SC-MX-A** — Matrix toolbar: aggiunta legenda inline con badge `LEAD` e `follow` con testo descrittivo

---

## [2026-03-22] — User test (Japi): Intro & Nav globale — fix armonizzato

### Changed — `index.html`, `css/base.css`, `css/components.css`, `js/main.js`, `js/glossary.js` (new)

- **Pillar 1 — Intro launcher**: i 3 titoli area diventano clickabili (`data-navigate-group`); aggiunta CTA row con due pulsanti "→ Explore Supply Chain" e "→ European Defence Fund"
- **Pillar 2 — Context block**: blocco "about this research" in fondo all'Intro con definizione breve dei 3 settori (Defence / Mining / Tech) e link "→ Full context in About"
- **Pillar 3 — Glossary tooltips**: nuovo `js/glossary.js` con 12 termini; `.gl-term[data-gl]` applicato a 9 termini nell'Intro; tooltip CSS puro via `::after + attr(data-tooltip)`
- **Pillar 4 — Gruppo Data in nav**: Data Quality e Known Issues spostati da Tools a nuovo gruppo "Data" nella group nav; brand-wip link aggiornato; Tools ora contiene solo Wikidata Inspector
- Source: issue `japi-issues.md` I-A, I-B, I-C, I-D

---

## [2026-03-22] — Issue 7: Graph tab — search highlight, lead-only, hide isolated

### Changed — `js/tabs/graph.js`, `js/main.js`, `js/state.js`, `index.html`, `css/graph.css`

Three new toolbar controls (all views): **Search** highlights matching nodes + neighbours live without rebuilding; **Lead only** filters edges to lead investments only; **Hide isolated** removes unconnected nodes. Graph sidebar now opens by default with a "How to explore" help panel (views, shapes, controls) — replaced by entity detail on node click, restored on close. Fixed font-size tokens in help panel (`--sl-desc-fs` / `--sl-row-val-fs` instead of `--fs-xs`).

---

## [2026-03-22] — Issue 6: 6 investor wikidata_ids found (105 remaining)

### Changed — `data/database.json`, `issues.md`
- Re-searched all 111 null-QID investors via Wikidata SPARQL + `wbsearchentities` (MCP CKAN + Playwright)
- **6 new matches applied**: Elliott Management Corp. (Q5365696), Brazilian Development Bank (Q796822), TCV (Q107144758), U.S. Department of Commerce (Q503577), Research Council of Norway (Q4356293), Federal Government of the USA (Q48525)
- `sources.wikidata` populated for all 6; 105 remain null (small/niche VCs, individuals, ambiguous names)

---

## [2026-03-22] — Issue 3 closed: Bayan Resources already in database

### Changed — `issues.md`, `data/database.json`
- Issue 3 was stale — IN-0026 (Bayan Resources) exists with full CB data, Q96100147, sources.wikidata
- Cleared `needs_review` validation flag on IN-0026 — Q96100147 confirmed correct

---

## [2026-03-22] — Issue 2: Helsing wikidata_id found (18 remaining)

### Changed — `data/database.json`, `issues.md`
- Re-searched all 19 null-QID companies via Wikidata `wbsearchentities` + SPARQL (Playwright + MCP CKAN)
- **Helsing** now has a Wikidata entry: `Q127380521` — created since March 2026 search; enwiki "Helsing (company)"
- Applied `wikidata_id`, `sources.wikidata`, `wikipedia_url` for Helsing
- 18 companies remain without a Wikidata entry (all confirmed absent 2026-03-22)

---

## [2026-03-22] — Issue 1 resolved: wikipedia_url corrected for all companies

### Changed — `data/database.json`
- All `sources.infonodes.wikipedia_url` values for company entities derived from confirmed `wikidata_id` via Wikidata `wbgetentities` API (enwiki sitelinks), queried via Playwright in 3 batches of 50 QIDs
- **30 contaminated URLs fixed** (e.g. NVIDIA → Microsoft, Glencore → Nvidia, IBM → Cisco, etc.)
- **72 missing URLs added** (companies that had `null` but do have a Wikipedia page)
- **1 nulled** (Bayan Resources — QID has no enwiki sitelink)
- 29 already correct, untouched
- `_updated` bumped to `2026-03-22`

---

## [2026-03-22] — Investigation page linked from main navbar

### Changed — `index.html`, `automated-investigation.html`
- `index.html`: added ✨ Investigation link to group navbar between Tools and About (plain `<a>` tag, same `tnav-btn` class)
- `automated-investigation.html`: experiment banner updated to AI attribution — "Generated through AI — Claude Sonnet 4.6 on 22 March 2026. Experimental demo."

---

## [2026-03-21] — `automated-investigation.html` — experimental standalone investigation page

### Added
- `automated-investigation.html`: standalone long-form investigative page, **experiment only** — not linked from `index.html` or the navigation. Access via direct URL path.
- Page presents data from `database.json` and `edf_calls.json` as a narrative editorial investigation: hero, four chapters (EU Money, Power Brokers, Startups, Research), D3 force-directed network, and company profile cards.
- Design system applied from `index.html`: Barlow Condensed + JetBrains Mono fonts, `--accent: #00ff41` green terminal palette, sector/investor entity colour tokens (`--c-defence`, `--c-mining`, `--c-tech`, `--c-startup`), CSS variables for surface, border, and typography scale — replacing the previous editorial serif/red palette.
- Experiment banner displayed below nav to mark the page as non-canonical.

---

## [2026-03-21] — URL deep-linking for map country + company/investor sidebars

### Changed — `js/tabs/map.js`, `js/detail-sidebar.js`, `js/main.js`, `js/url.js`
- Map (Supply Chain): clicking a country/node now sets `&country=<name>` in URL; closing the panel clears it; `selectMapCountryByName()` exported for restore
- Map restore: `pendingCountry` pattern handles lazy-init — country is stored before map fetch resolves, applied in `.then()`; popstate re-apply if already built
- Company sidebar: `openCompanySidebar()` sets `&company=<id>&name=<name>` (name is human-readable label only, not used for lookup); close clears both
- Investor sidebar: `openInvestorSidebar()` sets `&investor=<id>&name=<name>`; close clears both
- `restoreFromUrl()` in `main.js`: added `case 'map'`, `case 'companies'`, `case 'investors'` to restore sidebar/selection from URL params on direct load or popstate
- `detail-sidebar.js` and `map.js` now import `getParams`/`setParams` from `url.js`; `openCompanySidebar`/`openInvestorSidebar` imported in `main.js`

---

## [2026-03-21] — Preloader unification + Supply Chain map preloader fix

### Changed — `index.html`, `css/base.css`, `js/tabs/map.js`, `js/main.js`
- All 14 tab preloaders: `<span>Loading...</span>` replaced with `<div class="loading-text">loading {tab}…</div>` — matches initial overlay visual language (monospace, `--fs-xs`, `--text-faint`); tab-specific text per tab
- Removed orphaned `.tab-preloader span` CSS rule from `base.css`
- Supply Chain Map preloader fix: `initMap()` was hiding preloader immediately (fire-and-forget fetch); `buildMapView()` now returns the fetch promise, `initMap()` passes it through, `main.js` calls `.then(() => hidePreloader(...))` — same async pattern as EDF Map
- EDF Map reset zoom: hardcoded to `tx:-2926, ty:-261, k:3.647` instead of `zoomIdentity`

---

## [2026-03-21] — Issue 9: orphaned CSS classes defined

### Changed — All CSS files (`base.css`, `components.css`, `graph.css`, `map.css`, `wikidata.css`, `eucalls.css`, `about.css`)
- Defined all classes/ID rules introduced during `index.html` inline-style cleanup that had no CSS definition yet (Issue 9)
- `base.css`: `.hidden { display:none }`, `.loading-text`, `.ctrl-sep`, `.lg-dot--{defence,mining,tech,startup,fund,govt,bank,inst,mfr}`, `.lg-star--dual`
- `components.css`: `.sf-label`, `.wd-cov-row`, `.tbl-wrap--lg`, `#wd-cov-pct`, `#q-missing`, `#mx-toolbar`
- `graph.css`: `#proj-filter-btns { gap: 6px }`
- `map.css`: `.map-toggle-label`, `.map-ctrl-btn`, `.map-status`, `.map-filter-bar`, `.map-filter-clear`, `#map-arc-toggle`/`#edfmap-arc-toggle`, `#edfmap-position`
- `wikidata.css`: `.wd-mode-label`, `.wd-country-filter-lbl`, `.wd-loader-text`, `#wd-country-btns`, `#wd-live-input`, `#wd-selected-label`, `#wd-external-link`, `#wd-loader .spin`
- `eucalls.css`: `.ec-container`, `.ec-header-note`, `.ec-form-footer`, `.ec-funded-label`, `.ec-funded-text`, 9 ID rules (`#ec-totalCallsCount`, `#ec-fileDate`, `#ec-callStatusText`, `#ec-fundedOnly`, `#ec-fundedCount`, `#ec-btnSpinner`, `#ec-patternTitle`, `#ec-partClose`, `#ec-jsonContent`)
- `about.css`: `.a-collab-text`, `.a-note`, `.a-mt8/10/14`, `.a-mb18`, `#tab-about .a-section p strong`
- `eucalls.js` `ecShow()`: also removes `.hidden` class to avoid CSS/inline conflict; `wikidata.js` `toggleWdMode()`: explicit `'block'` instead of `''` for same reason

---

## [2026-03-21] — Full sidebar CSS centralization

### Changed — Sidebar structural unification (`index.html`, `css/components.css`, `css/eucalls.css`, `js/tabs/matrix.js`, `js/tabs/graph.js`, `js/main.js`)
- All sidebar title elements migrated to `.sl-title`; all close buttons to `.sl-close`; removed duplicate CSS classes `.dp-close`, `.dp-title`, `.dp-label`, `.entity-sidebar-title`, `.ec-part-title`
- `#edfmap-panel`, `#map-panel`: removed `.sidebar` class (em-base irrelevant — all children use `rem` tokens)
- `#ec-part-sidebar-panel`: removed `.sidebar`; `.ec-part-label`/`.ec-part-val`/`.ec-part-title` migrated from `em` to `--sl-row-lbl-fs`/`--sl-row-val-fs`/`.sl-title`; `.ec-part-link` and `.ec-part-val--dim` added
- `matrix.js` + `graph.js`: `dp-label` → `sl-section-lbl`, `dp-list` → `es-list`; all inline styles replaced with `dp-inv-meta`, `dp-co-meta`, `dp-funding`, `dp-desc`, `dp-links`, `dp-link`, `dp-co-count` classes (hardcoded hex `#555`/`#666`/`#aaa` eliminated)
- `es-list li`: added `justify-content: space-between`; `es-list li span:first-child` gets ellipsis truncation
- `--sl-*` typography tokens scaled ×1.3 across all sidebars: title 1.56rem, section-lbl/row-lbl 0.85rem, row-val 0.98rem, desc 1.04rem

---

## [2026-03-21] — EDF Map tab + Wikidata sidebar CSS unification

### Added — European Defence Fund — Map tab (`js/tabs/edfmap.js`, `index.html`, `css/map.css`)
- New sub-tab **Map** in the European Defence Fund group, positioned between Overview and EDF Calls Search
- Data sourced exclusively from `data/edf_calls.json`; no modifications to the data file
- `js/tabs/edfmap.js`: self-contained ES module with module-level `ms` state object, lazy-initialised on first visit (`AppState.ui.edfmap.built` guard), returns a Promise
- **Data build** (`buildData()`): flattens all call → project → participant records; deduplicates organisations by PIC (or `"name||country"` fallback); builds ISO3 country map, arc weight map (co-project pair counts), and per-country org list
- **Map** (`drawMap()`): D3 v7 `geoNaturalEarth1` projection; country fills, circles sized by org count (`d3.scaleSqrt`, domain `[0, max]`, range `[3, 12]`), weighted arcs, country name labels
- **MultiPolygon centroid fix**: for countries with overseas territories the centroid is computed on the largest polygon by `d3.geoArea()` (fixes France, Spain, Portugal, Norway, etc.)
- **Fixed 16 px labels at any zoom**: `font-size` set via `.style()` (inline style, wins over CSS class specificity) as `16/k` SVG units; recalculated on every zoom event; `font-size` intentionally absent from the `.edfmap-label` CSS class
- **Country click** (`showCountry()`): dims unrelated countries/nodes; filters arcs to only those touching the selected ISO; sidebar shows beneficiary list
- **Org click** (`filterByOrg()`): shows only arcs from the org's own country (`orgIso`) to each of its partner countries (`partnerIsos`); sidebar shows org's projects with role badge, acronym, contribution, EC Portal link
- **Reset** (`clearEdfMapFilter()`): restores all visuals; exported and wired in `main.js`
- **Live position display**: `#edfmap-position` span updated on every zoom event showing `tx / ty / k` for calibration
- **Initial zoom**: `d3.zoomIdentity.translate(-2926, -261).scale(3.647)` — centred on Europe
- Exports: `initEdfMap`, `clearEdfMapFilter`, `closeEdfMapPanel`, `resetEdfMapZoom`, `toggleEdfMapArcs`
- `js/state.js`: added `edfmap: { built: false }` to `ui`
- `js/main.js`: import + lazy-init block + wired controls (arc toggle, reset zoom, close panel, clear filter); EDF GROUPS updated to `['edfoverview','edfmap','eucalls','edfbrowse']`
- `css/map.css`: full EDF map CSS block appended — green theme (`.edfmap-country.has-data { fill: #0a2a0a }`, `.edfmap-node { fill: var(--accent) }`), teal arcs, sidebar/panel/proj-item/role-badge styles; `.edfmap-label` has no `font-size` property (controlled by JS)

### Changed — Wikidata Inspector sidebar CSS (`css/wikidata.css`)
- Removed standalone `font-size` overrides from `#wd-sidebar` and `#wd-main` that inflated text relative to other sidebars
- All child font-sizes converted from relative `em` units to shared design tokens: `var(--sl-row-val-fs)`, `var(--fs-xs)`, `var(--sl-row-lbl-fs)`
- `.wd-field-table td` color changed from hardcoded `rgba(255,255,255,0.75)` to `var(--text-secondary)` — consistent with other sidebar rows
- Result: Wikidata Inspector sidebar now matches the visual scale and color treatment of all other sidebars in the app

---

## [2026-03-21] — CSS design system refactoring: sidebar uniformity + font tokens + EDF UX

### Changed — Sidebar CSS unified (`css/base.css`, `css/components.css`, `css/graph.css`, `css/map.css`, `css/eucalls.css`, `css/wikidata.css`, `css/edfbrowse.css`)
- New `--sl-*` tokens: `--sl-inline-bg`, `--sl-title-fs`, `--sl-section-lbl-fs`, `--sl-row-lbl-fs`, `--sl-row-val-fs`
- Shared panel primitives added to `components.css`: `.sl-title`, `.sl-close`, `.sl-section-lbl`, `.sl-row`, `.sl-row-lbl`, `.sl-row-val`
- `#graph-detail`, `#map-panel`, `#mx-detail` restructured to header/body flex pattern
- Entity sidebar and EC participant sidebar migrated to `--sl-*` tokens

### Changed — Font design tokens applied to all table tabs (`js/tabs/companies.js`, `investors.js`, `relationships.js`, `edfbrowse.js`)
- All hardcoded font sizes (`.68rem`, `.75rem`, `.8rem`, `.82rem`) → `--fs-xs`, `--fs-sm`, `--fs-base`
- All hardcoded colors (`#444`, `#666`, `#aaa`, `#333`) → `--text-faint`, `--text-muted`, `--text-tertiary`, `--grey-dark`
- Investor names in Relationships wrapped in `<strong>` to match Companies/Investors bold name pattern
- EDF table headers: `--fs-xs`/`--dim` → `--fs-sm`/`--accent`, `border-bottom: 1px` → `2px`; row hover matched to Companies pattern
- `.eb-org-name`: `--fs-sm` + no weight → `--fs-base` + `font-weight: var(--fw-bold)`
- `#rel-tbody tr` added to `cursor: pointer` rule in `components.css`

### Added — EDF Beneficiaries: org detail sidebar (`index.html`, `js/tabs/edfbrowse.js`)
- Inline row drawer replaced by `#edf-sidebar` slide-in panel (reuses `.entity-sidebar` CSS)
- Drawer rows (`eb-drawer-row`) removed from table render; `toggleDrawer` removed; `openEdfSidebar` / `closeEdfSidebar` added
- Overlay + close button wired in `initEdfbrowse`

### Changed — EDF Beneficiaries header layout (`css/edfbrowse.css`, `index.html`)
- `#eb-header` changed to flex row; toolbar first, stats bar second (`flex: 1`)
- Stats bar `margin-bottom` removed; toolbar `margin-bottom` removed
- Country select now sorted A-Z (`localeCompare`) instead of by participation count

---

## [unreleased]

### Planned
- Consider periodic cron / reminder to re-run `fetch_edf_bulk.py` as new EDF calls are published

---

## [2026-03-17] — Investor Wikidata enrichment + sidebar Crunchbase block

### Added — Investor `wikidata_id` enrichment (Playwright + Wikidata API)
- Searched all 242 `IV-` investor entities against Wikidata `wbsearchentities` API via Playwright browser (5 batches of ~50, 300 ms delay each)
- 131/242 investors matched confidently and assigned a `wikidata_id`; 111 left `null` (no entry on Wikidata, ambiguous results, or personal names without a clear match)
- History entry appended to each updated entity (`author: "playwright_search"`)

### Added — Investor `sources.wikidata` enrichment (`enrich_wikidata.py` logic, inline)
- Same extraction pipeline as companies: `wbgetentities` in batches of 50, label resolution for P31/P17/P159
- Fields populated: `retrieved_at`, `label`, `description`, `aliases`, `instance_of`, `country`, `inception`, `headquarters`, `official_website`, `isin`, `employees`, `wikipedia_url`
- 131 enriched, 0 failed

### Added — Entity sidebar: Crunchbase block (`js/detail-sidebar.js`, `css/components.css`)
- New `cbSection(cb)` function mirrors `wdSection`: visually distinct amber-tinted box (`.es-cb-block`, `--cb-accent: #f4a147`)
- Shows all `sources.crunchbase` fields: profile URL, HQ, website, domain, stage, revenue range, total funding (USD + native if currency differs), CB rank, investor type, patents, acquired by, founders (tags), primary industry, industries (tags), industry groups (tags), `extracted_at` footer
- Renders "not available" (`.es-na`) when no CB data exists — box always visible
- `wdSection` updated with same "not available" fallback instead of returning `''`
- Both sidebars (company + investor) now always show both boxes

### Changed — Company sidebar restructured
- Main info section reduced to Country + Founded (both from WD/infonodes)
- All CB fields (stage, funding, website, industries) moved into the new CB block
- Order: description → info → CB block → WD block → focus → investors → validation

### Changed — Entity sidebar width
- `.entity-sidebar-panel`: `width: 400px` → `width: 800px` (max-width: 95vw preserved)

---

## [2026-03-17] — Company sidebar: full Wikidata block + description moved to top

### Changed — Company entity sidebar (`js/detail-sidebar.js`, `css/components.css`)
- CB description moved to top of sidebar, immediately below name/badges header
- New `.es-wd-block` section added after the main info rows: visually distinct (teal-tinted bg + border), header "Data from Wikipedia / Wikidata" with dot indicator
- Shows all available `sources.wikidata` fields: description, aliases (as tags), instance_of (as tags), HQ, employees (locale-formatted), ISIN, official website, Wikipedia link, Wikidata QID link, retrieved_at timestamp
- Wikidata QID link moved from main info block into the WD section
- CSS: `.es-wd-block`, `.es-wd-header`, `.es-wd-desc`, `.es-wd-updated` added to `components.css`

---

## [2026-03-17] — Landing page, Known Issues tab, EDF Overview fixes

### Changed — Landing page
- Default group on load changed from `supply-chain` to `intro` (`main.js` + `index.html` active class)

### Added — Tools → Data Issues sub-tab (`js/tabs/knownissues.js`, `docs/data-issues.md`)
- New sub-tab in Tools group renders `docs/data-issues.md` via `marked.js` (CDN v9)
- `docs/data-issues.md`: in-app issue tracker; Issue #1 (EDF count mismatch), Issue #2 (budget partial coverage)
- CSS scoped to `.ki-body`: `max-width: 80%`, `margin: auto`, font sizes scaled ×1.5
- `marked@9` added to CDN scripts in `index.html`

### Fixed — EDF Overview: Total Allocated Budget over-count (×N bug)
- **Root cause 1**: budget summed per action within each topic — but all actions in a topic share the same `budgetYearMap` value → counted N times. Fix: take first action only per topic.
- **Root cause 2**: same topic ID appears across multiple calls (e.g. topic `113484` in 10 calls) → each call added the same budget again. Fix: global `seenTopics` Set deduplicates topic IDs across all calls.
- Result: €373.54B → €42.96B → €5.07B (consistent with 120/201 calls having budget data; official envelope ~€7.95B)

### Changed — EDF Overview: stat card layout and metrics
- Grid changed to 4-column; row-1 tiles (EDF Calls, Total Allocated Budget) each span 2 columns
- "EDF Calls" renamed to "European Defence Fund Calls"
- "Budget of Calls with Funded Projects" (from `budgetTopicActionMap`) replaced with **"Total EU Contribution"** (sum of `participants[].eu_contribution`) — now consistent with EDF Beneficiaries stats bar
- Row 2: Calls with Funded Projects · Total EU Contribution · Funded Projects · Unique Participants

### Changed — Top nav brand-wip
- "Under Construction" pill updated to: "Work in Progress — Data may contain errors, see [Known Issues](?research=tools&tab=knownissues)"

---

## [2026-03-16] — Entity sidebars, EDF Overview tab, UI polish

### Added — Entity detail sidebars (`js/detail-sidebar.js`, `css/components.css`, `index.html`)
- New slide-in sidebar component (`#entity-sidebar`) shared across Companies, Investors, Relationships tabs
- `openCompanySidebar(company)`: renders sector badge, dual-role badge, entity ID, Wikidata link, country, founded year, stage, total funding, website, CB description, infonodes focus, industries tag cloud, investors list with type badges and lead flags, validation issues
- `openInvestorSidebar(im)`: renders type badge, entity ID, portfolio count, lead count, full portfolio company list with sector badges and lead flags
- Click delegation on `#co-tbody` (row → company), `#inv-tbody` (row → investor), `#rel-tbody` (investor name cell → investor sidebar, company name cell → company sidebar)
- CSS: `.entity-sidebar`, `.entity-sidebar-panel` (slide-in from right, 400px), `.entity-sidebar-overlay` (dimmed backdrop), `.es-*` content block classes, `.es-click-cell` hover underline
- `initEntitySidebar()` wires overlay click + close button; called once after data loads in `main.js`

### Added — EDF Overview sub-tab (`js/tabs/edfoverview.js`, `js/edf-data.js`)
- New leading sub-tab "Overview" in the European Defence Fund group (`defaultTab` changed from `eucalls` to `edfoverview`)
- Metrics computed on-the-fly from `data/edf_calls.json` on every page load — no hardcoded values
- **Call-level metrics** (always available): total EDF calls, total allocated budget (summed from all `budget_overview.budgetTopicActionMap` year values), calls with funded projects
- **Project-level metrics** (when project data populated): funded projects count, unique participants count
- **Rankings** (when project data available): top-20 countries by participation count + EU contribution, top-20 organisations by project count + EU contribution
- Layout: stat cards row + two-column rankings (countries 4/12, participants 8/12)
- Graceful "no data yet" placeholder shown when `projects` arrays are empty
- **`js/edf-data.js`**: new shared singleton fetch module — `loadEdfCalls()` caches the promise so `edf_calls.json` (3.7MB) is fetched only once even when both EDF Overview and EDF Beneficiaries tabs are opened; `edfbrowse.js` updated to use it

### Changed — Supply Chain sub-tab order
- Old order: Overview · Matrix · Graph · Companies · Investors · Relationships · Map
- New order: Overview · Map · Graph · Companies · Investors · Relationships · Matrix
- Visual separators added between logical groups in the sub-nav

### Changed — Branding and top nav
- `info.nodes` part of brand now lowercase white (`#fff`); "Man in the Loop" stays green (`var(--accent)`); dot stays green — achieved via `.brand-infonodes` wrapper span
- Added "Under Construction" amber pill badge (`.brand-wip`) trailing the brand in `#topnav`

### Changed — Tools / Wikidata Inspector UI
- `#wd-sidebar` font-size: `1.38rem` (previous `1.2rem` × 1.15)
- `#wd-layout` sidebar column: `260px` → `399px`
- `#wd-main` font-size: `1.2rem`; all child element font-sizes converted from `rem` → `em` so they scale: `.wd-field-table th/td`, `.wd-fin-table`, `.wd-placeholder`, `.live-drop-item`, `.live-drop-item .live-desc`
- `.wd-field-table td` font-size set explicitly to `1.1rem`

### Changed — EDF Overview layout
- `#eo-wrap` base font-size: `1.2rem` (all text in overview except `.val` stat numbers)
- Countries / Participants column split changed from 50/50 to 4/12 (33%) / 8/12 (67%)
- Participant bar labels widened: `.eo-bar-label--wide` = `260px`; country labels stay `160px`
- Both rankings capped at top 20 (was 20 countries / 15 participants, now consistent)

---

## [2026-03-16] — Two-level nav: group bar + sub-tab bar + Intro + About

### Changed — Navigation architecture (`index.html`, `js/main.js`, `js/url.js`, `css/base.css`)
- Flat single-row tab nav replaced with a two-level structure:
  - `#tabnav` (top row, `--tab-h: 46px`): research **group** buttons — Intro · Supply Chain · European Defence Fund · Tools · About — plus trailing `↗ GitHub` link button
  - `#subnav` (second row, `--subtab-h: 38px`): sub-tab buttons scoped to the active group, hidden for standalone groups (Intro, About)
- Group → sub-tab mapping:
  - **Intro**: standalone (no sub-tabs)
  - **Supply Chain**: Overview · Matrix · Graph · Companies · Investors · Relationships · Map
  - **European Defence Fund**: EU Calls · EDF Browse
  - **Tools**: Wikidata Inspector · Data Quality
  - **About**: standalone (no sub-tabs)
- `body.subnav-hidden` CSS class added/removed on group switch; all fixed-position offsets (`#legend`, `#content`) adjust automatically via CSS variable overrides (`--legend-top`, `--content-h`)

### Changed — URL scheme (`js/url.js`, `js/main.js`)
- URL now uses `?research=<group>&tab=<subtab>` (two-level) instead of `?tab=<name>` (flat)
  - Examples: `?research=supply-chain&tab=companies`, `?research=edf&tab=edfbrowse`, `?research=intro`
  - Standalone groups omit `tab` param for cleaner URLs
- `TAB_TO_RESEARCH` lookup in `url.js` auto-injects `research` param when tab-level code calls `setParams({ tab: '...' })` — no changes needed in any tab JS file
- `navigate(group, tab, push)` replaces `showTab(name, push)` as the unified navigation function in `main.js`
- `restoreFromUrl()` reads `?research=` instead of `?tab=` and delegates to `navigate()`

### Added — Intro tab (`#tab-intro`)
- New standalone tab with terminal-style layout (green-on-black, `JetBrains Mono`)
- Content: project tagline, one-paragraph description, three research area cards (Supply Chain, EDF, Tools) with sub-tab lists
- CSS scoped in `base.css` under `.intro-*` classes; uses the `@keyframes blink` cursor animation

### Added — About tab (`#tab-about`, `css/about.css`)
- New standalone tab with content from `../about.html`: Who we are, Objective and scope, 3 main focus areas, Methodology, company list
- CSS in `css/about.css`, fully scoped to `#tab-about` to avoid conflicts with existing `.section-title` and other global rules
- `JetBrains Mono` added to Google Fonts link in `index.html`

### Changed — Branding
- `<title>` updated from `database.json v2 — Explorer` to `Man in the Loop — Explorer`
- `#topnav .brand` updated to `Man in the Loop — Explorer`

---

## [2026-03-15] — EDF Browse tab + URL routing + UI fixes

### Added — EDF Browse tab (`js/tabs/edfbrowse.js`, `css/edfbrowse.css`)
- New tab **"EDF Browse"**: participant-focused explorer of `data/edf_calls.json`, lazy-initialised on first visit, all DOM IDs prefixed `eb-`
- **Data model**: flattens all funded project participants into an aggregated view keyed by PIC (or `name||country` fallback); one row per unique organisation
- **Table columns**: Organisation · Country · Participations · Coordinator count · Total EU contribution · Projects · SME — sortable by all numeric and text columns
- **Stats bar**: live totals for organisations, countries, participations, funded projects, total EU contribution — recalculates on every filter change
- **"Funded projects only" toggle** (default: ON) — gates the entire dataset rebuild; when OFF includes participations from projects with `eu_contribution = 0`
- **Country select**: dropdown sorted by participation count descending, with per-country counts; positioned inline after the toggle; resets to "All countries" when funded toggle changes
- **Search**: filters by organisation name and country
- **Expandable drawers**: click any row to see PIC, activity type, EC Portal link, and all the organisation's projects — each showing acronym, title, role badge (coordinator/partner), status badge (ongoing/closed), call ID, EU contribution, dates
- **Pagination**: 50 rows per page; renders only when needed (715 orgs → 15 pages in funded-only mode)
- **Design**: stats bar layout, chip/select filter patterns, expandable drawer rows
- **Per-participant EU contribution**: uses participant-level `eu_contribution` field (not project total) for accurate per-organisation funding figures
- Coordinator rows marked with a subtle green left border; coordinator count shown as a badge

### Added — URL-based state / shareable links (`js/url.js`)
- New module `js/url.js` with `getParams()`, `setParams()`, `setUrlReady()` — centralised URL read/write
- `setUrlReady()` guard: all `setParams()` calls are silent no-ops during initial loading and restore, preventing spurious URL writes at startup
- `setParams(params, push)`: `push=true` creates a browser history entry (tab switches); `push=false` (default) uses `replaceState` (filter changes) — back button navigates between tabs, not between every filter state
- Default values are omitted from the URL for clean shareable links
- **Tab routing**: every tab switch writes `?tab=<name>` — direct URL access restores the correct tab on load
- **Per-tab filter sync**:
  - `companies`: `search`, `sector`, `sort`, `asc`
  - `investors`: `search`, `sort`, `asc`
  - `relationships`: `search`
  - `matrix`: `sector` (restored via button click simulation in `main.js`)
  - `graph`: `view`, `sector` (restored via existing `setGraphView` / `setGraphSector` exports)
  - `edfbrowse`: `search`, `country`, `funded`, `sort`, `asc`
  - `eucalls`: `topic` (input value only; no auto-search on restore)
- **Restore on load**: `restoreFromUrl()` in `main.js` runs after data loads, navigates to the correct tab and applies all filter params before `setUrlReady()` is called
- **Browser back/forward**: `popstate` listener calls `restoreFromUrl()` — full state is reconstructed from the URL
- **Lazy-init tabs** (`edfbrowse`): URL restore runs at the end of the async `initEdfbrowse()` by re-reading `getParams()` once the fetch resolves

### Fixed — `#content` margin-top gap (`css/base.css`)
- `body` already applies `padding-top: var(--nav-h)` (44px); `#content` was also adding `var(--nav-h)` to its `margin-top`, double-counting it and creating a 44px dead zone below the legend bar in every tab
- Fix: `margin-top` reduced from `calc(--nav-h + --tab-h + --legend-h)` to `calc(--tab-h + --legend-h)`; legend-closed override similarly reduced from `calc(--nav-h + --tab-h)` to `var(--tab-h)`

### Changed — Country filter in EDF Browse
- Replaced country filter chips (`.eb-chip` row) with an inline `<select>` element (`#eb-country-select`), positioned after the funded-only toggle in the toolbar
- Select options include participation counts; list is rebuilt on every `rebuild()` call to reflect the current funded/unfunded dataset

### Known gaps in EDF Browse (potential future additions)
- Flag emoji per country
- Multi-select country filter
- Cross-reference with `database.json`: "In DB" badge + filter toggle
- Cross-reference with investor relationships: badge + filter toggle
- Categories column (AIR, NAVAL, CYBER…) per organisation
- Stats bar: SME count, matched in DB, with investor data

---

## [2026-03-15]

### Added — `fetch_edf_bulk.py` (offline data pipeline)
- New script `scripts/fetch_edf_bulk.py` generating `data/edf_calls.json`
  - Phase 1: paginated fetch of all 201 EDF identifiers + full metadata (ccm2Id, title, status, deadline, description, budget_overview) — no CORS, direct API access
  - Phase 2: per-call funded project list + full participant details via DOC_API
  - `--limit N` for test runs · `--update` for incremental refresh · `--reenrich` to re-fetch participant details after script field changes
  - Polite delays (0.5s/page, 0.8s/year, 1.0s/call, 0.8s/project)
  - Merges into existing file on re-run, preserving already-fetched project data
- Participant fields extracted: `organization_name`, `pic`, `eu_url`, `role`, `order`, `status`, `activity_type`, `organization_type`, `type`, `sme`, `country`, `country_code`, `city`, `postal_code`, `street`, `latitude`, `longitude`, `web_link`, `eu_contribution`
- Full run completed: 201 calls · 64 with funded projects · 78 projects · 1,657 participants · 2.7 MB

### Added — EU Calls tab (browser)
- **Tab integration** (`js/tabs/eucalls.js`, `css/eucalls.css`): ported from standalone `call-checker_infonodes/`, lazy-initialised on first visit, all DOM IDs prefixed `ec-`
- **Call list + autocomplete**: loads from `data/edf_calls.json` at startup; dropdown filters by identifier or title; status dots (open/forthcoming/closed)
- **Funded-only filter**: default ON — shows 64 calls with known projects; toggle OFF for all 201
- **Header**: live call count + file date from `edf_calls.json._generated_at`; explanatory text about EC publication timeline
- **Fast path**: calls with projects in JSON render instantly (zero API calls); `ccm2Id` fast path skips text search for remaining cases
- **Fallback chain**: `edf_calls.json` → localStorage (6h TTL, stale-while-revalidate) → live API fetch
- **Background delta check**: one API page on tab open, warns if new calls not in file
- **Call detail retrieval fixes**: suffix-only text search avoids year-bucket dilution; single-year search for exact identifiers; `pageSize:50`, `pageNumber:1` (1-indexed) in POST body
- **Participant sidebar**: click any participant name → right panel slides in with full profile (role, PIC, activity type, SME, address, coords, website, EU portal link); overlay/✕ to close

### Architecture decision
- Adopted `database.json` pattern for EDF data: Python script owns the heavy lifting, browser is nearly API-silent

---

## [2026-03-08] — EU Calls tab (initial integration)

### Added
- EU Call Checker ported from `call-checker_infonodes/index.html` into the refactored explorer as a new tab
- CORS proxy chain: direct POST → `corsproxy.io` for EU Search API; direct GET → `allorigins.win` → `corsproxy.io` for other endpoints
- EDF-only search enforcement with modal for non-EDF identifiers
- Log panel showing step-by-step retrieval progress
- Comparison table and per-year accordion for results
- JSON export modal

---

## [2026-03-01] — Refactoring baseline

### Added
- Full ES module architecture (`js/main.js` + `js/tabs/*.js` + `js/state.js` + `js/data.js`)
- Tabs: Overview, Matrix, Graph, Companies, Investors, Relationships, Map, Wikidata Inspector, Data Quality
- `data/database.json` schema v2.0 as single source of truth
- Scripts: `migrate.py`, `validate.py`, `enrich_wikidata.py`, and related enrichment utilities
- `SCHEMA.md`, `UPDATE_PROTOCOL.md`, `readme.md`
