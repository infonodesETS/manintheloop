# Man in the Loop — info.nodes Explorer

Standalone web application for exploring the defence supply chain, European Defence Fund landscape, and related entity/investment data. Lives entirely inside `refactoring/` with no dependency on any other tool in the repository.

> **Development status**: active development branch. Changes tracked in [`CHANGELOG.md`](./CHANGELOG.md). When features stabilise they are promoted to the parent (production) repository.
> **Build status**: Under Construction — UI and data subject to change. Known issues documented in [`known-issues.md`](./known-issues.md).

---

## Quick start

```bash
cd refactoring/
python3 -m http.server 8000
```

Open `http://localhost:8000`. The app fetches `data/database.json` at runtime — it will not work as a `file://` URL due to CORS restrictions.

---

## Architecture overview

Single-page application. **No build step, no bundler.** Vanilla JS ES modules loaded directly by the browser. All logic lives in `js/`; all styles in `css/`; all data in `data/`.

Two data sources:
- `data/database.json` — supply chain entities and relationships (schema v2.0)
- `data/edf_calls.json` — all EDF calls + funded projects (fetched by `scripts/fetch_edf_bulk.py`)

Routing is URL-based (`?research=<group>&tab=<subtab>`), managed by `js/main.js` and `js/url.js`. Each sub-tab is an independent ES module in `js/tabs/`.

---

## File map

```
refactoring/
│
├── index.html                  ← SPA shell: nav structure, tab panes, legend, loading overlay
├── automated-investigation.html ← [EXPERIMENT] standalone long-form page, not linked from index
│
├── data/
│   ├── database.json           ← schema v2.0 — entities (IN-*, IV-*) + relationships (REL-*)
│   └── edf_calls.json          ← EDF calls + funded projects (generated — do not edit by hand)
│
├── js/
│   ├── main.js                 ← entry point: data bootstrap, navigate(), event wiring
│   ├── state.js                ← AppState singleton — shared data store across all tabs
│   ├── data.js                 ← loads database.json, derives COMPANIES / INVESTORS / RELATIONSHIPS
│   ├── edf-data.js             ← singleton fetch for edf_calls.json (cached promise, shared)
│   ├── detail-sidebar.js       ← slide-in entity detail sidebar (companies + investors)
│   ├── helpers.js              ← shared render helpers: esc(), fmtFunding(), badges, tip()
│   ├── url.js                  ← URL param read/write, setUrlReady() guard
│   └── tabs/                   ← one ES module per sub-tab (see JS layer below)
│
├── css/
│   ├── base.css                ← :root design tokens ONLY — typography, colors, spacing, sidebar tokens
│   ├── components.css          ← shared primitives: stat cards, tables, badges, sidebar shells
│   ├── graph.css               ← Graph tab (#graph-*, .gv-*)
│   ├── matrix.css              ← Matrix tab (#matrix-*, #mx-*)
│   ├── map.css                 ← Supply Chain Map + EDF Map (#map-*, .map-*, #edfmap-*, .edfmap-*)
│   ├── wikidata.css            ← Wikidata Inspector (#wd-*, .wd-*, .live-*)
│   ├── eucalls.css             ← EDF Calls Search (#ec-*, .ec-*)
│   ├── edfbrowse.css           ← EDF Beneficiaries + EDF Overview (#eb-*, .eb-*, #eo-*, .eo-*)
│   └── about.css               ← About tab (#tab-about scoped)
│
├── scripts/
│   ├── fetch_edf_bulk.py       ← fetches all EDF calls + projects → data/edf_calls.json
│   ├── validate.py             ← validates database.json against schema rules
│   ├── enrich_wikidata.py      ← Wikidata enrichment for entities
│   ├── migrate.py              ← one-shot migration from legacy investments.json
│   ├── fix_qid_shift.py
│   ├── search_missing_qids.py
│   ├── fix_wikidata.py
│   └── apply_inspector_ids.py
│
├── CHANGELOG.md                ← dated change log (replaces git history for this directory)
├── STYLE.md                    ← CSS architecture, typography tokens, sidebar system, rules
├── SCHEMA.md                   ← database.json schema v2.0 field specification
├── UPDATE_PROTOCOL.md          ← reconciliation rules for adding new data
├── issues.md                   ← active data/code issues
├── known-issues.md             ← in-app known issues (rendered in Tools → Known Issues tab)
└── readme.md                   ← this file
```

---

## JavaScript layer

| File | Role | Edit this to change… |
|---|---|---|
| `main.js` | Entry point — loads data, wires `navigate()`, handles routing | App boot sequence, nav event handlers |
| `state.js` | `AppState` singleton | Shared data structures available to all tabs |
| `data.js` | Loads + derives from `database.json` | How entities/relationships are parsed and indexed |
| `edf-data.js` | Singleton fetch for `edf_calls.json` | EDF data loading, caching strategy |
| `detail-sidebar.js` | Slide-in entity sidebar (companies + investors) | Entity sidebar content, CB/Wikidata blocks |
| `helpers.js` | Shared renderers: `esc()`, `fmtFunding()`, `sectorBadge()`, `typeBadge()`, `tip()` | Badge HTML, tooltip behaviour, funding formatting |
| `url.js` | URL param read/write, `setUrlReady()` guard | URL scheme, deep-link behaviour |

**Tab modules** (`js/tabs/`):

| Module | Tab | Group |
|---|---|---|
| `overview.js` | Supply Chain Overview | Supply Chain |
| `map.js` | Supply Chain Map | Supply Chain |
| `graph.js` | Graph (force-directed) | Supply Chain |
| `companies.js` | Companies table | Supply Chain |
| `investors.js` | Investors table | Supply Chain |
| `relationships.js` | Relationships table | Supply Chain |
| `matrix.js` | Investment matrix | Supply Chain |
| `edfoverview.js` | EDF Overview | European Defence Fund |
| `edfmap.js` | EDF Map | European Defence Fund |
| `eucalls.js` | EDF Calls Search | European Defence Fund |
| `edfbrowse.js` | EDF Beneficiaries | European Defence Fund |
| `wikidata.js` | Wikidata Inspector | About / Tools |
| `quality.js` | Data Quality | About / Tools |
| `knownissues.js` | Known Issues (renders `known-issues.md`) | About / Tools |

---

## CSS layer

Token-first system. `css/base.css` holds **only `:root` custom properties** — no component rules. Every other CSS file is scoped to its own tab or component set. No hardcoded size or color literals anywhere: all values go through `var(--token)`.

**Typography:** 7-step font-size scale (`--fs-xs` → `--fs-stat`) rooted at `html { font-size: 120% }` (1rem = 19.2px). 4 line-height tokens (`--lh-tight` → `--lh-loose`). Sidebar typography aliases the main scale via `--sl-*` tokens.

→ **Full token reference, CSS file scope, sidebar system, and rules: [`STYLE.md`](./STYLE.md)**

---

## Data layer

The app reads two files at runtime. Neither is bundled — they are fetched as JSON.

| File | Source | Schema |
|---|---|---|
| `data/database.json` | Hand-curated + script-enriched | v2.0 — entities (IN-*, IV-*) + relationships (REL-*) |
| `data/edf_calls.json` | Generated by `scripts/fetch_edf_bulk.py` | Nested: calls → topics → projects → participants |

→ **Full field specification: [`SCHEMA.md`](./SCHEMA.md)**
→ **How to add/reconcile new data: [`UPDATE_PROTOCOL.md`](./UPDATE_PROTOCOL.md)**

---

## Navigation

Two-level nav: group bar (top) + sub-tab bar (second row). URL scheme: `?research=<group>&tab=<subtab>`.

| Group | Sub-tabs |
|---|---|
| **Intro** | _(standalone)_ |
| **Supply Chain** | Overview · Map · Graph · Companies · Investors · Relationships · Matrix |
| **European Defence Fund** | Overview · Map · EDF Calls Search · EDF Beneficiaries |
| **About** | About · Known Issues · Data Quality · Wikidata Inspector · Data · Glossary |

---

## Dependencies (all CDN, no install)

| Library | Version | Purpose |
|---|---|---|
| Bootstrap | 5.3.3 | Layout, forms, utilities |
| D3.js | v7 | Force graphs, geographic maps, scales |
| TopoJSON client | 3 | Decoding world-atlas topology |
| world-atlas | 2 | Countries TopoJSON (fetched on Map tabs) |
| marked | 9 | Markdown → HTML (Known Issues tab) |
| Barlow Condensed | — | Primary UI font (Google Fonts) |
| JetBrains Mono | — | Monospace accent font (Google Fonts) |

---

## Experimental pages

### `automated-investigation.html`

Standalone long-form investigative page — a narrative report generated directly from the same data. Uses the same design system (Barlow Condensed, JetBrains Mono, green-accent terminal palette) but presents data as a scrollable editorial investigation with chapters, charts, a D3 network graph, and entity profiles.

**Not linked from `index.html`.** Access directly via `/automated-investigation.html`.
