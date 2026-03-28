# Man in the Loop — info.nodes Explorer

Standalone web application for exploring the defence supply chain, European Defence Fund landscape, and related entity/investment data. Lives entirely inside `refactoring/` with no dependency on any other tool in the repository.

> **Development status**: active development on `dev` branch. Changes tracked in [`CHANGELOG.md`](./CHANGELOG.md). Merged to `main` when stable — `main` is deployed via GitHub Pages at `https://infonodesets.github.io/manintheloop/`.
> **Build status**: Under Construction — UI and data subject to change. Known issues documented in [`docs/data-issues.md`](./docs/data-issues.md).

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
│
├── data/
│   ├── database.json           ← schema v2.0 — entities (IN-*, IV-*) + relationships (REL-*)
│   └── edf_calls.json          ← EDF calls + funded projects (generated — do not edit by hand)
│
├── docs/
│   ├── CHANGELOG.md            ← dated change log (replaces git history for this directory)
│   ├── STYLE.md                ← CSS architecture, typography tokens, sidebar system, rules
│   ├── SCHEMA.md               ← database.json schema v2.0 field specification
│   ├── UPDATE_PROTOCOL.md      ← reconciliation rules for adding new data
│   ├── spec-improvement.md     ← resolved, pending, and improvement backlog
│   ├── infonodes-issues.md     ← user test issues tracker (Davide, Andrea, Laura — 2026-03-27)
│   ├── andy-issues.md          ← user test session (Andy, 2026-03-24) — separate tracker
│   ├── issues.md               ← legacy general issues (pre-user-test)
│   └── data-issues.md          ← in-app data issues (rendered in Tools → Data Issues tab)
│
├── js/
│   ├── main.js                 ← entry point: data bootstrap, navigate(), event wiring
│   ├── state.js                ← AppState singleton — shared data store across all tabs
│   ├── data.js                 ← loads database.json, derives COMPANIES / INVESTORS / RELATIONSHIPS
│   ├── edf-data.js             ← singleton fetch for edf_calls.json (cached promise, shared)
│   ├── detail-sidebar.js       ← slide-in entity detail sidebar (companies + investors)
│   ├── helpers.js              ← shared render helpers: esc(), fmtFunding(), badges, tip()
│   ├── theme.js                ← dark/light toggle: applies data-theme attr, persists to localStorage
│   ├── url.js                  ← URL param read/write, setUrlReady() guard
│   └── tabs/                   ← one ES module per sub-tab (see JS layer below)
│
├── css/
│   ├── base.css                ← :root design tokens ONLY — typography, colors, spacing, sidebar tokens
│   ├── components.css          ← shared primitives: stat cards, tables, badges, sidebar shells
│   ├── graph.css               ← Graph tab (#graph-*, .gv-*)
│   ├── map.css                 ← Supply Chain Map + EDF Map (#map-*, .map-*, #edfmap-*, .edfmap-*)
│   ├── wikidata.css            ← Wikidata Inspector (#wd-*, .wd-*, .live-*)
│   ├── eucalls.css             ← EDF Calls Search (#ec-*, .ec-*)
│   ├── edfbrowse.css           ← EDF Beneficiaries + EDF Overview (#eb-*, .eb-*, #eo-*, .eo-*)
│   ├── about.css               ← About tab (#tab-about scoped)
│   └── companysearch.css       ← Company Search tab (#tab-companysearch, #cs-*, .cs-*)
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
| `theme.js` | Dark/light toggle — reads/writes `localStorage['mitl-theme']`, sets `data-theme` on `<html>` | Theme persistence, toggle button wiring |
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
| `edfoverview.js` | EDF Overview | European Defence Fund |
| `edfmap.js` | EDF Map | European Defence Fund |
| `eucalls.js` | EDF Calls Search | European Defence Fund |
| `edfbrowse.js` | EDF Beneficiaries | European Defence Fund |
| `wikidata.js` | Wikidata Inspector | About / Tools |
| `quality.js` | Data Quality | About / Tools |
| `knownissues.js` | Data Issues (renders `docs/data-issues.md`) | About / Tools |
| `companysearch.js` | Company Search | _(standalone group)_ |

---

## CSS layer

Token-first system. `css/base.css` holds **only `:root` custom properties** — no component rules. Every other CSS file is scoped to its own tab or component set. No hardcoded size or color literals anywhere: all values go through `var(--token)`.

**Typography:** 7-step font-size scale (`--fs-xs` → `--fs-stat`) rooted at `html { font-size: 120% }` (1rem = 19.2px). 4 line-height tokens (`--lh-tight` → `--lh-loose`). Sidebar typography aliases the main scale via `--sl-*` tokens.

→ **Full token reference, CSS file scope, sidebar system, and rules: [`STYLE.md`](./docs/STYLE.md)**

---

## Data layer

The app reads two files at runtime. Neither is bundled — they are fetched as JSON.

| File | Source | Schema |
|---|---|---|
| `data/database.json` | Hand-curated + script-enriched | v2.0 — entities (IN-*, IV-*) + relationships (REL-*) |
| `data/edf_calls.json` | Generated by `scripts/fetch_edf_bulk.py` | Nested: calls → topics → projects → participants |

→ **Full field specification: [`SCHEMA.md`](./docs/SCHEMA.md)**
→ **How to add/reconcile new data: [`UPDATE_PROTOCOL.md`](./docs/UPDATE_PROTOCOL.md)**

---

## Enriching data — UPDATE_PROTOCOL.md

> **This is the critical document if you are adding or modifying data.** Read it before touching `database.json`.

[`docs/UPDATE_PROTOCOL.md`](./docs/UPDATE_PROTOCOL.md) defines the exact rules for keeping `database.json` consistent across updates. All changes to entity data must follow this protocol.

### Core rules (summary)

| Rule | What it means |
|---|---|
| **IDs are permanent** | `IN-NNNN`, `IV-NNNN`, `REL-NNNN` are never reused or reassigned once created |
| **History is append-only** | Never delete or modify existing `history[]` entries — only append |
| **Full provenance required** | Every history entry must cite raw source file, row, field, and exact value |
| **Validate before committing** | Run `python3 scripts/validate.py` — all 8 checks must pass |
| **Atomic git commits** | One logical change per commit; git log = external audit trail independent of in-JSON history |
| **Deduplication before adding** | Search existing entities (case-insensitive) before creating a new one |
| **IDs assigned sequentially** | New entities get `max(existing) + 1` in their class |

### Operations covered

- **Adding a company** (`IN-NNNN`) — required fields, initial history entry, `needs_review` validation flag
- **Adding an investor** (`IV-NNNN`) — same as company; deduplication check mandatory
- **Updating a field** — update value + append history entry with `old`/`new`/`source`/`author`
- **Batch Crunchbase re-scrape** — diff old vs. new snapshot, update `sources.crunchbase`, append per-field history
- **Resolving a validation flag** — correct the field, append history, set `status: "confirmed"`
- **Merging a duplicate** — lower ID wins; merge history + sources; update all REL references; retire higher ID

### Running validation

```bash
python3 scripts/validate.py
```

Run from `refactoring/`. All 8 checks must pass before any commit touching `database.json`.

### Updating the navbar date

After every commit, update the `_updated` field at the top of `data/database.json`:

```json
{ "_updated": "YYYY-MM-DD", ... }
```

Set it to today's date. `js/main.js` reads this field at boot and renders it as `updated: YYYY-MM-DD` in the top navbar — it is the only date shown to users in the UI and signals when the dataset or app was last changed.

---

## Improving the app — spec-improvement.md

> **Read this before making structural changes to the app.**

[`docs/spec-improvement.md`](./docs/spec-improvement.md) tracks:

- **Resolved** — features added since the spec (routing, EDF group, detail sidebar, glossary, data issues tab…)
- **Pending** — known gaps and incomplete work (onboarding, AppState inconsistencies)
- **Improvement backlog** — 9 prioritised items from the original §16 constraints and architectural observations, each with files to touch and a risk rating

Use it to pick safe work items and avoid re-introducing already-solved problems.

→ **[`docs/spec-improvement.md`](./docs/spec-improvement.md)**

---

## User test issues

> **Read this for the current implementation backlog.**

[`docs/infonodes-issues.md`](./docs/infonodes-issues.md) tracks issues collected from live user test sessions (Davide, Andrea, Laura — 2026-03-27). Many resolved as of 2026-03-28; see [`docs/CHANGELOG.md`](./docs/CHANGELOG.md) for the full history.

→ **[`docs/infonodes-issues.md`](./docs/infonodes-issues.md)**

---

## Navigation

Two-level nav: group bar (top) + sub-tab bar (second row). URL scheme: `?research=<group>&tab=<subtab>`.

| Group | Sub-tabs |
|---|---|
| **Intro** | _(standalone)_ |
| **Supply Chain** | Overview · Map · Graph · Companies · Investors · Relationships |
| **European Defence Fund** | Overview · Map · EDF Calls Search · EDF Beneficiaries |
| **About** | About · Data Issues · Data Quality · Wikidata Inspector · Data · Glossary |

---

## Dependencies (all CDN, no install)

| Library | Version | Purpose |
|---|---|---|
| Bootstrap | 5.3.3 | Layout, forms, utilities |
| D3.js | v7 | Force graphs, geographic maps, scales |
| TopoJSON client | 3 | Decoding world-atlas topology |
| world-atlas | 2 | Countries TopoJSON (fetched on Map tabs) |
| marked | 9 | Markdown → HTML (Data Issues tab) |
| Barlow Condensed | — | Primary UI font (Google Fonts) |
| JetBrains Mono | — | Monospace accent font (Google Fonts) |

