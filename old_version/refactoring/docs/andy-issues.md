# User Test — Andy — Issues

_Session date: 2026-03-24_
_Source: speech-to-text transcript, unedited session walkthrough_
_App state at session: Supply Chain tabs + EDF tabs + About group, production build_

> **readme.md:** questo file è referenziato nel file map di `readme.md`. Quando tutte le issue saranno risolte, rimuovere la riga corrispondente da `readme.md`.

---

## How to read this file

Each issue is tagged with:
- **Area** — which tab/component is affected
- **Type** — Bug | UX | Content | Feature | Performance
- **Priority** — High / Medium / Low (based on user signal strength and blast radius)
- **Overlap** — reference to existing tracked issue if one exists

Issues are ordered roughly by the order Andy encountered them in the session.

---

## #01 — Nav bar counters: abbreviations opaque to new users

**Area:** Global nav bar — `#tnav-info` (top-right stat strip)
**Type:** UX / Content
**Priority:** Medium
**Status: RESOLVED** — `#tnav-info` stat strip removed entirely from `index.html` (2026-03-25, commit `fix(ux): remove tnav-info stat strip`). Counters are no longer shown in the nav bar; dataset stats available in the Overview tab and the Copy for AI context block.

The nav bar renders `${companies.length} co · ${investors.length} inv · ${relationships.length} rel` (see `main.js:210`). The abbreviations `co`, `inv`, `rel` are meaningless to anyone unfamiliar with the schema. Andy's immediate reaction: "non capisco niente di queste co-inv-rel".

Suggested fix: add `title` attributes or `tip()` on the element explaining each count. Example: "165 companies · 242 investors · 298 relationships in the dataset". Alternatively, spell out labels at wider viewports.

**Note:** Andy also floated dismissing these counters entirely ("non sono importanti") — worth discussing whether the strip adds value on the nav bar vs. inside the Overview tab only.

---

## #02 — Tooltip font size too small

**Area:** Global (all `tip()` tooltips)
**Type:** UX
**Priority:** Low

Andy explicitly flagged tooltips as slightly too small ("farei leggermente più grande il font del tooltip"). He wears glasses and noted it's a mild accessibility concern. Contrast is fine.

Suggested fix: increase `--tooltip-fs` token (or equivalent) by one step on the scale, e.g. from `--fs-xs` to `--fs-sm`. Check `css/base.css` for the tooltip size token; check `js/helpers.js` `tip()` for inline style overrides.

---

## #03 — Supply Chain Overview: stat tiles mix three abstraction levels

**Area:** `js/tabs/overview.js` — `#stats-grid`
**Type:** UX / Content
**Priority:** High

Andy spent significant time trying to understand whether the tile numbers (165 companies, 242 investors, 298 relationships, 65 defence) represent independent counts or nested subsets. Quote: "tutte queste colonne numeriche hanno un cappello che li contiene o è giusto che siano tutte distinte?"

Looking at `overview.js:20-31`, the `stats` array mixes three different levels of abstraction, all rendered with the same `stat-card` class:
1. **Entity totals** — Companies (165), Investors (242), Relationships (298) — independent global counts
2. **Relationship subtype** — Lead inv. — a count of relationships where `lead === true`, subset of (3)
3. **Sector subsets** — Defence (65), Mining, Tech, etc. — subsets of Companies (1)

No visual distinction separates these levels. Andy correctly sensed something was wrong but couldn't articulate it.

Note: stat cards already have `title` tooltips from `GLOSSARY` where keys exist (`overview.js:29`), but only if the glossary key matches — not all cards have them, and the browser `title` tooltip uses default styling.

Suggested improvements:
- Visual grouping or section headers to separate entity counts from sector breakdowns
- Remove "Lead inv." from this grid (it belongs in the Relationships tab)
- Short sub-label clarifying unit (e.g. "unique entities" vs. "subset of companies")

Andy: "è tutta inferenza che ha fatto l'AI quando io gli dicevo fai queste cose... ok però metterli sempre non ha senso".

---

## #04 — Supply Chain Overview: Wikidata Coverage tile is misplaced

**Area:** `js/tabs/overview.js` — Wikidata coverage stat
**Type:** Content / IA
**Priority:** High
**Status: RESOLVED** — Wikidata coverage tile removed from SC Overview `stats[]` array in `overview.js` (2026-03-22, CHANGELOG OV-A). The tile no longer appears in the stats grid.

Andy: "questo wikidata è un po'a cazzo nel senso che non deve stare qua... deve stare in una parte operazionale... quasi di metadati".

The Wikidata coverage metric belongs in the About / Tools group (Data Quality tab or similar), not in the Supply Chain Overview where it sits next to business-level stats. It measures data completeness, not supply chain substance.

Suggested fix: remove from Overview; promote to `js/tabs/quality.js` (Data Quality tab) where it fits naturally alongside other completeness metrics.

---

## #05 — Supply Chain Overview: Top Investor Portfolio chart labels truncated

**Area:** `js/tabs/overview.js` — top investor/portfolio bar charts
**Type:** UX
**Priority:** Medium

Bar chart labels (investor/company names) are truncated with ellipsis. Andy: "le label sono troncate". This is especially visible with longer names.

Suggested fixes:
- Increase chart container width or reduce label truncation threshold
- Add tooltips on truncated labels (overlaps with #07)
- Consider horizontal bar chart layout to give labels more room

---

## #06 — Supply Chain Overview: investor names in chart not clickable

**Area:** `js/tabs/overview.js` — Top Investor Portfolio chart
**Type:** UX / Feature
**Priority:** Medium

Andy expected that clicking an investor name (e.g. BlackRock, Banca Europea) in the chart would open a detail sidebar. Quote: "mi sarei aspettato che al click su BlackRock succedesse qualche cosa, che c'era qualche scheda anagrafica".

This is consistent with the pattern established in the Companies/Investors tables where clicking opens `detail-sidebar.js`. The chart currently has no click handler.

Suggested fix: wire `openInvestorSidebar()` on click for each bar/label element in the Top Investor Portfolio chart, matching the entity by name or ID.

---

## #07 — Truncated text (ellipsis) anywhere in the app must have a tooltip

**Area:** Global
**Type:** UX
**Priority:** Medium

Andy: "dovunque automaticamente ci sono i tre puntini, ci deve essere il tool tip, se no non leggo un benemato cazzo."

This is a blanket UX rule: any element that truncates with CSS `text-overflow: ellipsis` or manual `…` must have a `title` attribute or `tip()` tooltip exposing the full text. Currently inconsistent — some truncated cells have tooltips, others do not.

Action: audit all tables, chart labels, and sidebar fields for truncation without tooltip. Fix each occurrence.

---

## #08 — Supply Chain Map: zoom doesn't fit to active node bounding box

**Area:** `js/tabs/map.js`
**Type:** UX / Bug
**Priority:** High
**Status: RESOLVED** — `computeTransformForISOs()` and `fitMapToISOs()` implemented in `map.js` (2026-03-25, commit `fix(map): fit default zoom to data countries; zoom to entity on company click`). Default view fits all data countries; clicking a country zooms to its bounding box accounting for sidebar width. `defaultTransform` stored and restored on panel close.

Andy: "è sbagliato nel senso che è come se avesse lo zoom geografico e non lo zoom legato al contesto dei pallini. Dovrebbe prendere il bounding box dei pallini e poi centrare rispetto a questo."

When a country is selected and only a subset of nodes are active, the map retains the default geographic zoom rather than zooming to fit the visible nodes. Andy's precise formulation: "il bounding box dei pallini meno la width della sidebar".

Suggested fix (Andy's own words): compute the bounding box of all active/visible node positions, then call the D3 zoom transform to fit that box, accounting for the sidebar panel width offset. This is analogous to D3's `fitExtent()` / `fitSize()` pattern.

**Note:** Andy rated the map 7.5–8/10 overall — this is the primary blocker to a higher score.

---

## #09 — Supply Chain Graph: no auto-zoom/fit when a company is selected

**Area:** `js/tabs/graph.js`
**Type:** UX / Feature
**Priority:** Medium
**Status: RESOLVED** — `computeGraphFit()` and `applyDefaultTransform()` implemented in `graph.js` (2026-03-25, commit `feat(graph): move controls to bottom toolbar; bbox fit; click tooltip; blank-click reset`). Bounding-box fit applied at simulation end (`sim.on('end', ...)`) with animated transition; also applied immediately for bipartite/projection views.

When a user selects a country then clicks a company (e.g. Italy → Fincantieri), the graph shows only 3 connected nodes but stays at the default zoom level — making labels unreadable. Andy: "non leggo tutto il resto".

Suggested behavior: on company selection (not on country selection, where the user navigates manually), auto-fit the graph to the bounding box of the active nodes using D3's zoom transition. Edge case: if only 1 node is active, skip zoom (already well-highlighted).

Andy named the D3 mechanism: "transition" + zoom rescale. In D3 v7 this is `zoom.transform()` with a computed `zoomIdentity` from the node positions.

---

## #10 — Supply Chain Map: Clear button does not reset sidebar (Bug)

**Area:** `js/tabs/map.js` — `clearMapFilter()` / `#map-clear-filter-btn`
**Type:** Bug
**Priority:** High
**Status: RESOLVED** — `clearMapFilter()` now calls `closeMapPanel()` after resetting `AppState.ui.map.activeFilter` (map.js:134). `closeMapPanel()` restores the default zoom transform and resets the panel to intro content.

Andy had selected KGM International (an investor entity in the map panel) then pressed Clear. Expected: the panel should close and revert to the "About this map" intro state. Actual: the panel stays open showing KGM International's detail. Andy: "con clear dovrebbe spegnersi tutto e riattivarsi la parte informativa cioè quella che ce n'è nella fase di learning".

Root cause: `clearMapFilter()` (`map.js:138-141`) only resets `AppState.ui.map.activeFilter` and calls `applyMapFilter()`. It does not call `closeMapPanel()`. The panel content set by `showMapCountry()` or `filterMapByEntity` is never cleared.

Fix: `clearMapFilter()` should also call `closeMapPanel()`, which resets the panel to the "About this map" state and deselects the country highlight.

Files: `js/tabs/map.js` — `clearMapFilter()`, `closeMapPanel()`

---

## #11 — Supply Chain Map: arc direction legend disappears when a country is selected

**Area:** `js/tabs/map.js` — `drawMap()` panel body / `showMapCountry()`
**Type:** UX / Content
**Priority:** Medium

The legend text for arc direction already exists. `drawMap()` (`map.js:339-342`) sets the initial panel body to:

> "Arcs connect investor countries (faint end) to company countries (bright end), showing the direction capital flows across borders."

However, when the user clicks a country, `showMapCountry()` replaces the entire panel body with country-specific data. The legend disappears and is never visible again unless the user closes the panel and re-reads the intro.

Andy: "l'idea è fichissima... non rende l'idea. Non riesce a leggerlo senza averlo suggerito."

Fix: extract the arc direction legend to a static element outside the panel (e.g. a small permanent indicator in the map controls bar or as a fixed legend below the map). The gradient logic is in `drawArcs()` (`map.js:346-393`): source = 7% opacity, destination = full opacity.

---

## #12 — Supply Chain Graph: URL routing incomplete — most filters not in URL

**Area:** `js/main.js`, `js/tabs/graph.js`, `js/url.js`
**Type:** Feature
**Priority:** Medium

Andy: "poter mandare a Davide Del Monte questa pagina con gli esatti filtri che tu hai scritto, compreso quello di testo... avere end tipo uguale mining and filter text uguale andre".

**Current state** (from code review): `main.js:284-302` already serializes `view` and `sector` to URL params for the graph, and `restoreFromUrl()` (`main.js:182-190`) restores them. The map also serializes `country`.

**What is missing from URL** for the graph tab:
- `search` — text filter input (`#graph-search`)
- `leadOnly` — lead investments toggle
- `hideIsolated` — hide isolated nodes toggle
- `showCompanies` / `showInvestors` — visibility toggles
- `projFilter` — projection filter (all / multi)

Fix: extend the graph event handlers in `main.js` to call `setParams()` when any of the above change, and extend `restoreFromUrl()` case `'graph'` to restore all of them.

Andy: "lo farei, perché è veramente comodissimo quando queste cose funzionano bene e non ci sono quasi mai."

**Overlap:** `spec-improvement.md §1.1`.

---

## #13 — Supply Chain Map: stats bar should be contextual (filter-aware)

**Area:** `js/tabs/map.js` — `#map-status` element
**Type:** Feature
**Priority:** Medium

Andy: "ho cliccato su Cina che è legata a cinque paesi. Questo potrebbe diventare cinque countries e poi l'elenco delle compagnie collegate e il cross-border."

Currently `#map-status` is set once in `drawMap()` (`map.js:328-329`) to global totals: `"${coCount} countries · ${totCo} companies mapped · ${arcData.length} cross-border investor pairs"`. It never updates.

All the data to compute contextual counts is already available inside `showMapCountry()` (`map.js:395+`): `cd.companies`, `flowInArr`, `flowOutArr`. When a country is selected, `#map-status` should update to show per-country counts.

Andy also suggested moving this to the sidebar: "si potrebbe anche spostare come posizione nel side panel... questo rimanga fisso e il side panel compare qua, sotto".

---

## #14 — Supply Chain Map: opening side panel causes layout shift of stats text

**Area:** `js/tabs/map.js` — layout (stats bar + sidebar)
**Type:** UX / Bug
**Priority:** Medium

Andy: "questo testo si sposta a sinistra quando c'è il side panel."

When the entity detail panel opens on the right, the stats text in the top-right shifts leftward due to the layout reflow. This is jarring and makes the map feel broken.

Suggested fix: fix the stats strip to a position that is unaffected by sidebar opening (e.g. absolutely positioned, or inside a container that doesn't flex-shrink). Alternatively, move stats to the sidebar as per #13.

---

## #15 — Supply Chain Map: click on empty area should deselect and reset

**Area:** `js/tabs/map.js`
**Type:** UX / Feature
**Priority:** Medium
**Status: RESOLVED** — SVG click handler added at `map.js:338`: click on the bare SVG canvas or a non-data path calls `clearMapFilter()` → `closeMapPanel()`, restoring full unfiltered state.

Andy: "al click su un punto vuoto della mappa, il comportamento atteso dall'utente. Noi mappari faremmo così."

Clicking an empty area (no country, no node) on the map should:
1. Deselect the active country/company
2. Close the sidebar
3. Restore the full unfiltered state (all arcs visible, all nodes active)

This is standard map UX. Currently the only way to reset is via the explicit "Reset" or "Clear" button.

---

## #16 — Companies/Investors tables: click on type tag should activate as filter

**Area:** `js/tabs/companies.js`, `js/tabs/investors.js`
**Type:** Feature
**Priority:** Medium

Andy: "averli nella tabella colonna type uso le label delle categorie come filtro quindi con clicco con agency e mi filtra solo".

Currently the Type column shows badges (e.g. "Bank", "GovAgency", "Found") as static labels. Andy suggested making them clickable — clicking a badge activates it as a filter, visually docked above the table (Delicious-style tag cloud). Multiple tags could stack as AND filters; clicking the docked tag removes it.

This would complement the existing text search input in those tabs.

Files: `js/tabs/companies.js`, `js/tabs/investors.js`

---

## #17 — Sidebar inconsistency across tabs

**Area:** `js/detail-sidebar.js`, `js/tabs/graph.js`, `js/tabs/map.js`
**Type:** UX
**Priority:** Medium

Andy: "questa sidebar è full [width] mentre la sidebar del grafo è diversa ancora, quindi bisogna fare un controllo generale su ste sidebar."

Three different sidebar/panel implementations coexist:
- `detail-sidebar.js` — shared slide-in sidebar used by Companies, Investors, Relationships
- Graph tab — local `#graph-detail` panel with its own layout
- Map tab — local side panel with its own layout

Visual inconsistency is noticeable. Width, typography, section structure, and close behavior differ.

**Overlap:** `spec-improvement.md §2.4` tracks that graph and matrix were not migrated to `detail-sidebar.js`. This is the user-facing symptom of that debt.

Suggested path: at minimum, align visual styles (width, typography tokens, section headings) even without full code unification. Full migration tracked separately.

---

## #18 — "Copy as Markdown" / LLM-friendly export of current view

**Area:** Global (multiple tabs)
**Type:** Feature
**Priority:** Low
**Status: RESOLVED** — `js/copy-ai.js` implemented with `buildAiSnapshot()` dispatching per-tab snapshots to Markdown (Overview, Companies, Investors, Relationships, Map, Graph, Company Search). "Copy for AI" button (`#copy-ai-btn`) in the global nav bar. Context block prepended to every snapshot. `initCopyAI()` wired at boot.

Andy described a pattern he implemented on a Sicilian regional assembly site: a "copy resources for AI" button that generates a structured Markdown snapshot of the current view (entity list, active filters, key data points) plus a suggested prompt. This lets users paste the context directly into an LLM for analysis.

Andy: "rendere disponibili alle AI il testo grezzo per farci cose... in tutte le pagine dove c'erano dei contenuti".

Implementation sketch:
- A "Copy for AI" button (or per-tab icon) that serializes the current view to Markdown
- Include: active filters, visible entity names/IDs, key stats
- Optionally prepend a short context prompt ("You are looking at a supply chain dataset…")
- Standard: check `llms.txt` convention (Andy mentioned a robots.txt-like standard for LLM crawlers)

This is additive and low-risk. Priority is low because it requires scoping per tab.

---

## #19 — SEO / Open Graph / Twitter Card metadata

**Area:** `index.html` — `<head>`
**Type:** Feature
**Priority:** Low
**Status: PARTIALLY RESOLVED** — `og:title`, `og:description`, `og:type`, `twitter:card`, `twitter:title`, `twitter:description`, and `meta name="description"` are all present in `index.html`. Still missing: `og:image` (no social preview image) and `<link rel="canonical">`.

Andy mentioned at the end of the session: "guardati pure le cose carine di SEO e di Open Graph, Twitter Card, tutti i metadati che hai."

Current state unknown — requires a quick audit of `index.html` `<head>` for:
- `<meta property="og:title">`, `og:description`, `og:image`
- `<meta name="twitter:card">` etc.
- `<meta name="description">`
- Canonical URL

Low priority but quick win for shareability (especially relevant given #12 deep-link routing).

---

## #20 — Supply Chain Map: "Show Investment Arcs" toggle lacks UX rationale

**Area:** `js/tabs/map.js` — `#map-arc-toggle`
**Type:** UX / Content
**Priority:** Low

Andy: "perché dovrei poter spegnere queste cose mi serve spegnere questa cosa". He questioned the purpose of the arc visibility toggle. The toggle is legitimate — with many arcs the map becomes noisy and it's useful to see just the country bubbles — but that use case isn't communicated.

Suggested fix: add a `title` attribute or nearby tooltip to the toggle explaining when it's useful: "Hide investment flow arcs to see country relationships more clearly". The toggle label could also be more explicit: "Show arcs" → "Show investment flow arcs".

---

## #21 — Supply Chain Map: country panel lacks intro sentence when a country is selected

**Area:** `js/tabs/map.js` — `showMapCountry()` panel body
**Type:** UX / Content
**Priority:** Low

When a country is selected, `showMapCountry()` replaces the panel body with lists of companies, flowing-in investors, and flowing-out investors — but with no sentence at the top saying what is being shown.

Andy: "ci vorrebbe una specie di testo di spiega che dice cosa stai vedendo stai vedendo sta roba... stai vedendo le aziende che sono su [Israel]".

Suggested fix: add a one-line summary at the top of the panel body when a country is selected, e.g. "Showing 4 defence companies headquartered in Israel and 3 cross-border investor flows."

---

## #22 — Cross-tab navigation: clicking a company should be able to open it in Map or Graph

**Area:** `js/tabs/overview.js`, `js/tabs/companies.js`, `js/main.js`
**Type:** Feature
**Priority:** Low

Andy: "potresti decidere che quando ero in overview, al click mi potrebbe accendere la mappa sull'azienda". When viewing a company's detail (e.g. Fincantieri), it should be possible to jump directly to the Supply Chain Map filtered to that company's country, or to the Graph with that company highlighted.

This is additive and requires cross-tab deep-link coordination: `navigate('supply-chain', 'map')` + `selectMapCountryByName(country)`, or `navigate('supply-chain', 'graph')` + `setGraphSearch(name)`.

Not urgent — Andy's phrasing was speculative ("potresti, no, la soluzione non ti interessa").

---

## #23 — Wikidata Inspector: transient SPARQL error observed

**Area:** `js/tabs/wikidata.js`
**Type:** Bug (intermittent)
**Priority:** Low

Andy: "Cloud. C'è un errore sparkle da adesso non c'è." A Wikidata SPARQL query error appeared briefly during the session then resolved on its own. This matches expected behaviour for live Wikidata queries (rate limits, endpoint downtime), but the error state may not be user-friendly or may not recover gracefully.

Action: verify that the Wikidata Inspector shows a clear, non-alarming error state when SPARQL fails, with a retry affordance. Confirm auto-recovery when the endpoint comes back.

Files: `js/tabs/wikidata.js`

---

## Summary table

| ID | Area | Type | Priority | Status | Overlaps |
|---|---|---|---|---|---|
| #01 | Nav bar `#tnav-info` counters | UX/Content | Medium | ✅ RESOLVED | — |
| #02 | Tooltips global | UX | Low | open | — |
| #03 | SC Overview `#stats-grid` abstraction mix | UX/Content | High | open | — |
| #04 | SC Overview Wikidata tile misplaced | Content/IA | High | ✅ RESOLVED | — |
| #05 | SC Overview chart labels truncated | UX | Medium | open | — |
| #06 | SC Overview chart not clickable | UX/Feature | Medium | open | — |
| #07 | Ellipsis → tooltip global | UX | Medium | open | — |
| #08 | Map zoom to bounding box | UX/Bug | High | ✅ RESOLVED | spec-improvement 3.3 |
| #09 | Graph auto-zoom on company select | UX/Feature | Medium | ✅ RESOLVED | spec-improvement 3.2 |
| #10 | Map `clearMapFilter()` doesn't close panel | Bug | High | ✅ RESOLVED | — |
| #11 | Map arc legend disappears on country select | UX/Content | Medium | open | — |
| #12 | Graph URL routing: 5 filters missing | Feature | Medium | open | spec-improvement 1.1 |
| #13 | Map `#map-status` not contextual | Feature | Medium | open | — |
| #14 | Map stats layout shift on panel open | UX/Bug | Medium | open | — |
| #15 | Map click empty area to reset | UX/Feature | Medium | ✅ RESOLVED | — |
| #16 | Table tag-click filter | Feature | Medium | open | — |
| #17 | Sidebar inconsistency across tabs | UX | Medium | open | spec-improvement 2.4 |
| #18 | Copy as Markdown / LLM export | Feature | Low | ✅ RESOLVED | — |
| #19 | SEO / Open Graph metadata | Feature | Low | ⚠️ PARTIAL (og:image + canonical missing) | — |
| #20 | Map arc toggle lacks UX rationale | UX/Content | Low | open | — |
| #21 | Map country panel lacks intro sentence | UX/Content | Low | open | — |
| #22 | Cross-tab navigation from company detail | Feature | Low | open | — |
| #23 | Wikidata SPARQL transient error UX | Bug (intermittent) | Low | open | — |
