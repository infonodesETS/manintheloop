# CHANGELOG — refactoring/

> **Note on versioning**: `refactoring/` is intentionally excluded from the parent repository's git tracking (listed in `.gitignore`). It is the active development branch of the Manintheloop explorer. This file serves as a manual changelog to track changes, decisions, and state — replacing git history for this directory.
>
> When features stabilise they may be promoted to the parent (production) repository.

> **Rule for AI assistants**: Every resolved issue from `issues.md` must produce a dated entry here. Data gap issues moved to `known-issues.md` must also be recorded here. No issue is closed without a CHANGELOG entry.

---

## Style architecture spec

### CSS files and their scope

| File | Scope |
|---|---|
| `css/base.css` | `:root` tokens only — colors, spacing, typography scale, sidebar tokens. No selectors beyond `:root`, `*`, `body`, `html`. |
| `css/components.css` | Shared UI primitives: stat cards, tables, badges, legend, tooltip, sidebar structural shells, all `.sl-*` and `.es-*` and `.dp-*` classes. |
| `css/graph.css` | Graph tab only — `#graph-*` IDs and `.gv-*` classes. |
| `css/matrix.css` | Matrix tab only — `#matrix-*`, `#mx-*`. |
| `css/map.css` | Supply Chain Map and EDF Map — `#map-*`, `.map-*`, `#edfmap-*`, `.edfmap-*`. |
| `css/wikidata.css` | Wikidata Inspector — `#wd-*`, `.wd-*`, `.live-*`. |
| `css/eucalls.css` | EU Calls tab — `#ec-*`, `.ec-*`. |
| `css/edfbrowse.css` | EDF Browse and EDF Overview — `#eb-*`, `.eb-*`, `#eo-*`, `.eo-*`. |
| `css/about.css` | About tab — `#tab-about` scoped only. |

### Token system (`css/base.css`)

**Typography scale** — `--fs-xs` → `--fs-sm` → `--fs-base` → `--fs-body` → `--fs-lg` → `--fs-stat`

**Color palette** — `--text-primary` / `--text-secondary` / `--text-tertiary` / `--text-muted` / `--text-faint` / `--dim` / `--accent`

**Sidebar tokens** — all sidebar typography goes through `--sl-*`:
- `--sl-title-fs` — panel title
- `--sl-section-lbl-fs` — section label (uppercase accent)
- `--sl-row-lbl-fs` — row key (uppercase dim)
- `--sl-row-val-fs` — row value
- `--sl-desc-fs` — description / prose text
- `--sl-w-sm` / `--sl-w-inline` / `--sl-w-lg` — panel widths
- `--sl-header-pad` / `--sl-body-pad` / `--sl-header-bg` / `--sl-panel-bg` / `--sl-inline-bg`

### Sidebar primitives (`css/components.css`)

All sidebar panels share the same structural classes:

| Class | Role |
|---|---|
| `.sl-title` | Panel title — every sidebar header title element |
| `.sl-close` | Panel close button — every sidebar close button |
| `.sl-section-lbl` | Section label (UPPERCASE, accent color) |
| `.sl-row` / `.sl-row-lbl` / `.sl-row-val` | Key–value row (inline panels) |
| `.es-block` / `.es-row` / `.es-lbl` / `.es-val` | Key–value rows (slide-in entity sidebar) |
| `.es-desc` | Description text |
| `.es-list` / `.es-tag` | List and tag cloud |
| `.dp-inv-meta` / `.dp-co-meta` / `.dp-funding` / `.dp-desc` / `.dp-links` / `.dp-link` / `.dp-co-count` | Detail panel body content (matrix + graph) |
| `.ec-part-row` / `.ec-part-label` / `.ec-part-val` | EU Calls participant sidebar rows |

### Rules

1. **No inline `style="…"` in HTML.** All visual properties go in CSS files.
2. **No inline styles in JS-generated HTML** except for data-driven values (dynamic width/color from runtime variables). Use CSS classes.
3. **No hardcoded color/size literals** in CSS — always `var(--token)`.
4. **`em` units are banned** in sidebar content. Use `rem` via `--sl-*` tokens so font sizes are independent of panel ancestry.
5. **The `.sidebar` class** (`font-size: var(--scale-sidebar)`) is reserved for panels that explicitly use `em`-based sub-classes. New panels must not use it.
6. **One canonical class per role** — no parallel equivalents. Removed: `.dp-close` (= `.sl-close`), `.dp-title` (= `.sl-title`), `.dp-label` (= `.sl-section-lbl`), `.entity-sidebar-title` (= `.sl-title`), `.ec-part-title` (= `.sl-title`).

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

### Added — Tools → Known Issues sub-tab (`js/tabs/knownissues.js`, `known-issues.md`)
- New sub-tab in Tools group renders `known-issues.md` via `marked.js` (CDN v9)
- `known-issues.md`: in-app issue tracker; Issue #1 (EDF count mismatch), Issue #2 (budget partial coverage)
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
