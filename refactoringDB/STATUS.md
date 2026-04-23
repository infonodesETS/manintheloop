# refactoringDB — Project Status

> Authoritative resume point for AI-assisted work.
> Last updated: 2026-04-23 (EDF frontend: project list in entity cards, EDF-NNNN project profiles, co-participant expand)

## Session protocol

- **At session start**: read this file before taking any action.
- **At session end** (or after significant progress): update this file, then commit.
- **Commit rule**: every STATUS.md update must be committed with message `docs(refactoringDB): update STATUS.md`.
- **Validate before any data commit**: `python3 scripts/validate.py` must pass.

---

## Scripts reference

> Run `python3 scripts/validate.py` after any script that modifies `database.json`.
> All paths are relative to `refactoringDB/`.

### Always-safe commands

| Command | What it does | Safe to re-run? |
|---|---|---|
| `python3 scripts/validate.py` | 10-check validation — never modifies DB | Yes |
| `python3 scripts/parse_ishares.py <csv>` | Prints normalised rows to stdout | Yes |
| `python3 scripts/audit_quality.py --dry-run` | Audit B+C report only — never modifies DB | Yes |
| `python3 scripts/enrich_wikidata.py --dry-run` | Fetch + print Wikidata data, no DB writes | Yes |

### Wikidata enrichment

```bash
# Populate sources.wikidata for all entities with a wikidata_id (skips already-enriched)
#   Reads: data/database.json  |  API: wbgetentities (batches of 50, 2s delay)
#   Writes: data/database.json (sources.wikidata + history[] + validation[wikidata_enriched])
python3 scripts/enrich_wikidata.py [--dry-run]

# Force re-enrichment of ALL entities (including already-enriched) — use after bulk QID updates
python3 scripts/enrich_wikidata.py --force [--dry-run]

# Validate
python3 scripts/validate.py
```

Re-run safety: without `--force`, skips entities that already have `sources.wikidata` → safe to re-run after new QIDs are applied.

### Data quality audit

```bash
# Run audit (adds reconciliation_documented and field_conflict validation entries)
#   Audit B: documents cross-dataset reconciliation basis for 165 multi-source entities
#   Audit C: flags field-level conflicts across sources (country, headquarters)
#   Safe to re-run: skips entities that already have the relevant validation status
python3 scripts/audit_quality.py [--dry-run]

# Validate
python3 scripts/validate.py
```

### Website enrichment pipeline

Run once per enrichment cycle in this order:

```bash
# 1. Import EDF web_link field → sources.infonodes.website
#    Reads: data/edf_orgs.json, data/database.json
#    Writes: data/database.json (sources.infonodes.website + history[])
#    Skip: entities that already have crunchbase.website
python3 scripts/import_edf_websites.py [--dry-run]

# 2. Fetch official website (P856) from Wikidata for companies with wikidata_id but no website
#    Reads: data/database.json  |  API: SPARQL (batches of 50, 2s delay)
#    Writes: data/database.json (sources.infonodes.website + history[])
python3 scripts/fetch_wikidata_websites.py [--dry-run]

# 3. Validate
python3 scripts/validate.py
```

Re-run safety: both scripts skip entities that already have a website set → safe to re-run.

### QID enrichment pipeline

```bash
# Phase 1 — Wikidata Search API (resumes from checkpoint if qid_candidates.json exists)
#    Reads: data/database.json  |  Writes: data/qid_candidates.json (status=proposed/skipped)
#    API: wbsearchentities REST, 1.5s delay
python3 scripts/search_missing_qids.py --search

# Phase 1b — SPARQL label lookup + Reconciliation API for Phase 1 skipped entries
#    Reads: data/qid_candidates.json  |  Writes: data/qid_candidates.json (in-place)
#    Never overwrites accepted/rejected entries
python3 scripts/sparql_search_qids.py

# Phase 2 — Human review
# Open data/qid_candidates.json
# Change each "proposed" entry to "accepted" or "rejected"

# Phase 3 — Apply accepted QIDs to database.json
#    Reads: data/qid_candidates.json (accepted only)
#    Writes: data/database.json (wikidata_id + history[] + validation[])
#    Zero API calls
python3 scripts/search_missing_qids.py --apply

# Validate
python3 scripts/validate.py
```

Re-run safety: `--search` resumes from checkpoint. `--apply` skips entities that already have a wikidata_id.

### QID second-pass pipeline (`reprocess_skipped_qids.py`)

Run after the main QID pipeline to recover skipped entries via four strategies:

```bash
# Runs all 4 phases in sequence — safe to re-run (skips already-proposed/accepted/rejected)
#    Phase A: fix disqualify false positives (0 API calls, in-memory re-evaluation)
#    Phase B: P856 website reverse SPARQL lookup (2s delay, batch=10 entities)
#    Phase C: P31 type confirmation for no-description entries (SPARQL)
#    Phase D: results[1-4] re-search for wrong-top-result entries (Wikidata API, 1.5s delay)
#    Writes: data/qid_candidates.json only — never touches database.json
python3 scripts/reprocess_skipped_qids.py

# Then review qid_candidates.json (proposed → accepted/rejected), then apply:
python3 scripts/search_missing_qids.py --apply
python3 scripts/validate.py
```

### EDF participation pipeline (2026-04-23)

```bash
# Create EDF-NNNN project entities + edf_participation relationships
#   Reads: rawdata/edf_calls.json, data/edf_orgs.json, data/database.json
#   Writes: data/database.json (+78 EDF-NNNN entities, +1657 edf_participation rels)
python3 scripts/import_edf_projects.py [--dry-run]

# Validate
python3 scripts/validate.py
```

Re-run safety: skips existing EDF-NNNN entities (matched by project_id) and duplicate relationships.

### Investor pipeline (new — 2026-04-22)

```bash
# Step 1 — Create IV-NNNN entities + investment relationships from crunchbase.top_investors
#   Reads: data/database.json
#   Writes: data/database.json (+IV entities, +relationships)
#   Flags: --dry-run (no writes), --wikidata (SPARQL country lookup per investor, ~2s each)
python3 scripts/import_investors_crunchbase.py [--dry-run] [--wikidata]

# Step 2 — Assign known countries to well-known investors (curated lookup table)
#   ~90 entries covering major VC firms, EU institutions, US agencies, large banks
#   Writes: sources.infonodes.country on matching IV-* entities
python3 scripts/patch_investor_countries.py [--dry-run]

# Validate
python3 scripts/validate.py
```

Re-run safety: both scripts are idempotent — no duplicate entities or relationships created.
To get more investor countries: either extend `KNOWN` dict in `patch_investor_countries.py`,
or run `import_investors_crunchbase.py --wikidata` (slow: ~610 SPARQL queries × 2s each).

### Crunchbase enrichment pipeline

> **Full process documentation:** `data/crunchbase_sandbox/CRUNCHBASE.md`

```
data/crunchbase_sandbox/
  companies_export.csv                        ← full list (1149 rows: name + website)
  matches.csv                                 ← 812 rows — uploaded to Crunchbase (Cycle 1)
  non_matches.csv                             ← 337 rows — Crunchbase could not match
  crunchbase-export-matches-csv-4-13-2026.csv ← 724 rows returned by Crunchbase (Cycle 1)
  unresolved_2026-04-13.csv                   ← 21 rows CB returned but not matched to DB
  CRUNCHBASE.md                               ← process + reconciliation log
```

```bash
# Regenerate export (run at start of each new cycle)
python3 scripts/regenerate_export.py

# Import (dry-run first — always)
python3 scripts/import_crunchbase_csv.py \
    data/crunchbase_sandbox/crunchbase-export-<label>-MM-DD-YYYY.csv \
    --dry-run

# Apply
python3 scripts/import_crunchbase_csv.py \
    data/crunchbase_sandbox/crunchbase-export-<label>-MM-DD-YYYY.csv

# Validate
python3 scripts/validate.py
```

**Cycle 1 state (2026-04-14):** real import complete — 601 new + 121 updated = **731 entities** now have `sources.crunchbase`. 21 unresolved documented in `data/crunchbase_sandbox/CRUNCHBASE.md`.

### One-time build scripts (do not re-run — they regenerate IDs from scratch)

| Script | Purpose | Status |
|---|---|---|
| `scripts/build_database.py` | Initial iShares ETF import → database.json | Done 2026-04-01 |
| `scripts/build_edf_entities.py` | EDF org import → 792 new entities | Done 2026-04-01 |
| `scripts/import_startups.py` | Migrates 17 startups from old DB | Done 2026-04-01 |
| `scripts/import_by_wikidata.py` | Migrates 107 companies from old DB via QID match | Done 2026-04-01 |

> **Warning:** Re-running any of these scripts will attempt to create duplicate entities. Never re-run without modifying them to skip existing IDs first.

---

## Reference docs (read before modifying the DB)

| File | Purpose |
|---|---|
| `docs/SCHEMA.md` | Full schema v3.0 spec: entity types, ID prefixes, sources blocks, relationship types, history/validation format |
| `docs/UPDATE_PROTOCOL.md` | Rules for every DB modification: IDs permanent, history append-only, dry-run protocol, commit formats, merge/retire procedures |
| `docs/QID_LOOKUP_PROCESS.md` | How to run the 3-phase QID pipeline (search → SPARQL+Reconciliation fallback → human review → apply) |
| `data/crunchbase_sandbox/CRUNCHBASE.md` | Crunchbase enrichment cycle: step-by-step process, reconciliation strategy (4-tier matching), Cycle 1 stats, 21 unresolved entities categorised |

---

## Project goal

Build a graph database integrating three data universes:

1. **iShares ETF holdings** — Mining (GICS 151040), Tech (GICS 45), Comm Services (GICS 50)
2. **EDF (European Defence Fund) beneficiaries** — from `rawdata/edf_calls.json`
3. **Companies/startups** — migrated from `../refactoring/data/database.json` (old DB, read-only)

The old DB (`../refactoring/`) is **read-only** — never modify it. All work is inside `refactoringDB/` only.

---

## Schema v3.0 — key rules

- Entity IDs: `IN-NNNN` (company), `IV-NNNN` (investor), `PER-NNNN` (person), `REL-NNNN` (relationship)
- IDs are permanent, zero-padded to 4 digits, assigned alphabetically within each batch
- `sources.ishares` is an **array** (one element per ETF appearance)
- `history[]` is append-only — never delete or edit existing entries
- `wikidata_id` format: `Q\d+` or `null`
- Relationship types allowed: `investment`, `board_membership`, `edf_participation`
- `sources.wikidata` is script-managed — never edit manually
- See `docs/SCHEMA.md` for full spec, `docs/UPDATE_PROTOCOL.md` for update rules

---

## Folder structure

```
refactoringDB/
├── index.html                 ← Map page (D3 SVG world map + investor arcs) — branch new-frontend
├── search.html                ← Org search + profile viewer (ported from old index.html)
├── networks.html              ← placeholder
├── publications.html          ← placeholder
├── about.html                 ← placeholder
├── web/
│   ├── app.js                 ← search/profile JS (extracted from old inline script — single source of truth)
│   ├── router.js              ← URL routing (?organization=IN-XXXX + compare params)
│   ├── theme.js               ← dark/light theme toggle (shared across all pages)
│   ├── base.css               ← base styles (copied from ../refactoring/css/)
│   ├── components.css         ← component styles
│   └── companysearch.css      ← search/autocomplete/profile styles
├── data/
│   ├── database.json          ← main DB (schema v3.0) — primary artifact
│   ├── edf_orgs.json          ← PIC-keyed index of 794 EDF orgs with db_id crosswalk
│   ├── glossary.json          ← source flag tooltip descriptions (CB/EDF/iShares/WD/INF)
│   ├── qid_candidates.json    ← QID review file (1003 entries: 566 accepted, 65 rejected, 372 skipped)
│   └── crunchbase_sandbox/
│       ├── CRUNCHBASE.md         ← process + reconciliation log (read before touching anything here)
│       ├── companies_export.csv  ← full export (1149 rows: name + website)
│       ├── matches.csv           ← 812 rows uploaded to Crunchbase (Cycle 1)
│       ├── non_matches.csv       ← 337 rows excluded from Crunchbase upload
│       ├── crunchbase-export-matches-csv-4-13-2026.csv ← 724 rows from Crunchbase (Cycle 1)
│       └── unresolved_2026-04-13.csv ← 21 CB rows not matched to DB entity
├── rawdata/
│   ├── edf_calls.json         ← EDF raw data (source of truth for EDF beneficiaries)
│   ├── ishares_metals_mining_gics151040.csv
│   ├── ishares_tech_gics45.csv
│   └── ishares_comm_services_gics50.csv
├── scripts/
│   ├── parse_ishares.py       ← parses iShares CSVs → normalized dicts
│   ├── build_database.py      ← builds DB from iShares CSVs (dedup by name_key)
│   ├── build_edf_entities.py  ← imports EDF orgs, writes edf_orgs.json
│   ├── import_startups.py     ← migrates startups from old DB
│   ├── import_by_wikidata.py  ← migrates companies from old DB by wikidata_id
│   ├── search_missing_qids.py ← QID Phase 1 (Wikidata API) + --apply
│   ├── sparql_search_qids.py  ← QID Phase 1b (SPARQL + Reconciliation API fallback)
│   ├── enrich_wikidata.py     ← populates sources.wikidata for all QID-bearing entities
│   ├── import_crunchbase_csv.py ← imports Crunchbase export → sources.crunchbase (4-tier matching)
│   ├── regenerate_export.py   ← regenerates data/crunchbase_sandbox/companies_export.csv from DB
│   ├── import_investors_crunchbase.py ← creates IV-NNNN entities + relationships from top_investors
│   ├── patch_investor_countries.py    ← assigns known countries to well-known IV-* investors (~90 curated)
│   ├── patch_iv_countries_p159.py     ← SPARQL P159/P17 fallback for QID-bearing IV with no country
│   ├── migrate_old_db_investors.py    ← migrates funds/banks from legacy refactoring/ DB
│   ├── import_edf_projects.py         ← creates EDF-NNNN project entities + edf_participation rels
│   └── validate.py            ← 10-check validation (always run before committing)
├── docs/
│   ├── SCHEMA.md
│   ├── UPDATE_PROTOCOL.md
│   └── QID_LOOKUP_PROCESS.md
└── STATUS.md                  ← this file
```

> **Serving the web UI (new-frontend branch):** `python3 -m http.server 8001` from `refactoringDB/`, then open `http://localhost:8001/`.
> **Serving search UI only:** `python3 -m http.server 8000` from `Manintheloop/` root, then open `http://localhost:8000/refactoringDB/`.

---

## Current DB state (2026-04-23)

| Metric | Value |
|---|---|
| Schema | 3.0 |
| Total entities | **2101** |
| — companies (IN-NNNN) | 1149 |
| — institutions + gov agencies | 207 |
| — persons (PER-NNNN) | **0** — not yet built |
| — investors (IV-NNNN) | **667** — 610 from Crunchbase + 57 migrated from old DB (2026-04-22) |
| — EDF projects (EDF-NNNN) | **78** — from edf_calls.json (2026-04-23) |
| Relationships | **2649** — 897 Crunchbase + 95 old DB + 1657 edf_participation (2026-04-23) |
| IV entities with country | **275 / 667** — 59+62 curated + 123 SPARQL P17 + 23 P159/P17 fallback (2026-04-22) |
| Cross-border arcs on map | **129** (investor country → company country, unique pairs) |
| Companies with wikidata_id | 710 / 1149 (61.8%) — 2 wrong QIDs nulled (AVICOPTER, Sichuan Yahua) |
| Companies with sources.wikidata | 710 / 710 (100% of QID-bearing entities) |
| Companies with sources.ishares | 434 |
| Companies with sources.edf | 587 |
| Entities with sources.crunchbase | **731** (601 new + 121 updated — Cycle 1 real import 2026-04-14) |
| Companies with Crunchbase top_investors | 306 / 1149 |
| Companies with sources.infonodes.website | 1126 / 1149 (98.0%) |
| Last validate.py | PASSED (2026-04-23) — after EDF project import |
| qid_candidates.json | proposed=0, accepted=566, rejected=65, skipped=372 |
| validation: reconciliation_documented | 165 entities (2 edf+ishares, 130 crunchbase migration, 33 wikidata name-match) |
| validation: field_conflict | 44 entities (3 country real, 15 country normalisation, 30 HQ real) |
| validation: needs_review | 2146 + 610 IV entries (ongoing) |

---

## Completed work

### DB construction
- [x] iShares ETF import: 434 companies from 3 CSVs (deduplicated by `name_key`)
- [x] EDF beneficiaries: 794 orgs imported (2 matched to existing, 792 new entities)
- [x] Startups migrated from old DB (`import_startups.py`): 17 entities
- [x] Companies migrated from old DB with wikidata_id match (`import_by_wikidata.py`): 107 entities
- [x] Companies migrated from old DB without wikidata_id: 6 entities (needs_review)
- [x] 2 known QIDs applied manually (AVICOPTER → Q312094, Sichuan Yahua → Q56404682)

### Website enrichment
- [x] `import_edf_websites.py`: 726 websites from EDF `web_link` field → `sources.infonodes.website`
- [x] `fetch_wikidata_websites.py`: 220 websites from Wikidata P856 → `sources.infonodes.website`
- [x] Web research (batches): 258 additional websites via manual web search → `sources.infonodes.website`
- [x] Final coverage: 1126 / 1149 companies (98.0%) have a website
- [x] `data/crunchbase_sandbox/companies_export.csv` regenerated with `name` + `website` columns (1149 rows)

### QID enrichment
- [x] Phase 1 — Wikidata Search API (`search_missing_qids.py --search`): 245 proposed
- [x] Phase 1b — SPARQL label lookup (`sparql_search_qids.py`): +34 found
- [x] Phase 1b — Reconciliation API (`sparql_search_qids.py`): +46 found
- [x] Human review: 309 accepted, 16 rejected (of 325 proposed)
- [x] `--apply` run: 309 QIDs written to database.json
- [x] validate.py passed after apply

### Phase E — Wikipedia API search (2026-04-13)
- [x] Added `phase_e()` to `reprocess_skipped_qids.py`: searches English Wikipedia → resolves to Wikidata QID via `prop=pageprops` → standard label+description filter
- [x] Also fixed `normalize_label()` to treat `&` as `and` (fixes "Hill And Smith" vs "Hill & Smith")
- [x] Ran on 346 "no results from Wikidata search" entries; 9 proposed, 2 rejected (Pegasus spyware, Pixii product), 7 applied
- [x] Yield low for iShares (Chinese/Russian abbreviations don't map to WP titles); better for EDF European companies
- [x] validate.py PASSED

### P31 no-org-keyword pass (2026-04-13)
- [x] Run SPARQL P31 check on 22 "no org keyword in description" entries
- [x] 3 accepted (Mishra Dhatu Nigam Q6875625, Damen Schelde Naval Shipbuilding Q1158347, Royal Huisman Q2803924); 19 rejected (wrong entities: continents, languages, insects, family names, etc.)

### Diacritic/alias fixes (manual patch, 2026-04-13)
- [x] 8 skipped entries re-proposed with correct QIDs and applied: América Móvil, Fox Corporation (Class B), Grupa Kęty, Foxconn (Hon Hai), Metalúrgica Gerdau, Sensonor (Safran Sensing Norway), Thalès Alenia Space Italia, Thalès Dms France

### QID second pass (`scripts/reprocess_skipped_qids.py`)
- [x] Script written: 4-phase recovery for previously skipped entries
- [x] Phase A (disqualify false-positive fix): 53 proposals — fixed substring bug where `"nation"` matched `"multinational"`, `"state"` matched `"United States"`, `"sea"` matched `"research"`, `"actor"` matched `"contractor"`, `"video game"` blocked EA/Konami/Take-Two
- [x] Phase B (P856 website reverse lookup via SPARQL): 132 proposals — matched 672 company websites against Wikidata `wdt:P856`; batch size 10 entities (~80 URL variants per query)
- [x] Phase C (P31 type confirmation for no-description entries): 60 proposals — confirmed company type via `wdt:P31` for 64 entries that had QID+label match but no English description
- [x] Phase D (results[1–4] re-search): 20 proposals — re-searched with original entity name (not pre-stripped `search_name`) and checked all 5 results with fixed filter
- [x] **Human review complete**: 239 accepted, 28 rejected (of 267 proposals)
  - Rejected: AMD Singapore, ASM Japan, AutoTrader.co.za, BT Retail, Hexagon crystal system, NEXON Korea, Nokia Canada, NTT Docomo Business, ThyssenKrupp Nirosta (≠ Outokumpu), PTC Canada, WBD Netherlands, Airbus SE (parent for Airbus Heli DE), BAE Systems Inc. (≠ Hägglunds), Electromecanica (≠ Romarm), Elecnor Deimos (uncertain), Eight Bells (Egypt hill), Hensoldt AG (parent), John Cockerill (parent for JC Defense France), Kongsberg Våpenfabrikk (≠ Discovery), Chemo (≠ Laboratorios Liconsa), Nammo US (≠ Nammo Sweden), Naval Group (parent for Naval Belgium), Philips China, Safran Brazil (≠ Safran Electrical Power), Nortal (≠ Talgen), Telefónica (parent for subsidiary), Thales D&S (≠ Thales Cryogenics), MSM Group (≠ Vop Novaky)
- [x] After review: `--apply` run (239 QIDs written), `validate.py` PASSED (2026-04-13)

### Data quality audit (2026-04-13)
- [x] `scripts/audit_quality.py` written and run — covers Audit B (reconciliation) and Audit C (field conflicts)
- [x] **Audit B — Reconciliation documentation**: 165 `reconciliation_documented` validation entries added
  - 2 entities: edf+ishares cross-dataset match (STMicroelectronics, Telenor) — name_key normalisation via `build_edf_entities.py`
  - 130 entities: crunchbase migration from `refactoring/` legacy DB — name identity match (investments.json v1)
  - 33 entities: wikidata_id resolved from legacy DB via normalised name comparison — iShares entities enriched cross-DB
- [x] **Audit C — Field conflict detection**: 44 `field_conflict` validation entries added
  - 3 real country conflicts (sources.wikidata vs sources.infonodes disagree): Destinus (CH/NL), Chemring Group (DE/UK), Umicore (US/BE)
  - 15 country normalisation gaps ("People's Republic of China" vs "China") — same country, different form; not real conflicts
  - 30 real HQ conflicts (sources.wikidata.headquarters city vs sources.crunchbase.headquarters city+region+country when city differs)
  - 58 HQ granularity differences (city vs city+region+country, same city) — not flagged, not real conflicts
- [x] validate.py PASSED after audit

### Wikidata enrichment (2026-04-13)
- [x] `scripts/enrich_wikidata.py` written — populates `sources.wikidata` for all entities with `wikidata_id`
  - Flags: `--dry-run` (no DB writes), `--force` (re-enrich already-enriched entities)
  - Properties: P31 instance_of, P17 country, P571 inception, P159 headquarters, P856 website, P946 ISIN, P1128 employees, sitelinks.enwiki
  - Rate: batches of 50, 2s delay, backoff [5, 10, 20]s on 429
- [x] Fixed 2 wrong QIDs re-applied at migration: AVICOPTER (Q312094 → null), Sichuan Yahua (Q56404682 → null) — both confirmed wrong by Playwright verification in prior DB
- [x] Full enrichment run: 710 entities enriched (599 new + 111 force-refreshed from old DB migration data)
- [x] validate.py PASSED

### Crunchbase enrichment (2026-04-14)
- [x] `scripts/import_crunchbase_csv.py` real import run — 601 new + 121 updated = 731 entities with `sources.crunchbase`
- [x] `validate.py` PASSED after import

### Web UI — `index.html` (2026-04-14)
- [x] Organisation search UI built from `data/database.json` (adapted from refactoring/tmp/new_index.html)
- [x] Autocomplete with source flag pills (CB / EDF / iShares / WD / INF) + type badge
- [x] URL routing: `?organization=IN-XXXX&organizationName=...` — deep-linkable, browser back/forward aware (`web/router.js`)
- [x] Profile header: name, type badge, source flags, EU status line, description, external links, stat bar
- [x] Single-column collapsible source cards (all expanded by default, independently closable):
  - Infonodes → Wikidata → iShares (ETF table) → Crunchbase (grouped: Identity/Industry/Funding/Team) → EDF (org details + lazy project load) → Change History → Validation
- [x] EDF projects: lazy-loaded on demand, with participant expand/collapse; clicking a participant navigates to their profile
- [x] CSS/JS internal dependencies moved to `web/` folder (base.css, components.css, companysearch.css, router.js)

### Multi-page frontend — branch `new-frontend` (2026-04-22)

> Branch forked from `nuovoDB`. Serve from `refactoringDB/` root: `python3 -m http.server 8001`.

- [x] **`index.html`** — D3 SVG world map (ported from `../refactoring/js/tabs/map.js`)
  - Country-level aggregation: one circle per country, sized by arc degree
  - Side panel: country detail (companies list + investor badge `↓N` per company)
  - Company detail panel: HQ, funding, stage, rounds, founded year, CB description, investors list
  - Investment flow arcs: investor country (faint) → company country (bright), toggle on/off
  - **Arc directional coloring (2026-04-22):** on country click, arcs colored by direction — blue=outgoing (country invests abroad), red=incoming (foreign investor → local company), purple=bidirectional. Legend updates dynamically. Resets to teal gradient on deselect.
  - **Node stroke removed (2026-04-23):** `.map-node` stroke set to `none`/0 in all states (default, `:hover`, `.node-focus`); zoom handler no longer scales stroke-width.
  - **EU Funded filter (2026-04-23):** checkbox in toolbar (default off) dims all countries/nodes/arcs whose company-side has no EDF data. Covers 794 EDF companies across 28 countries. Composes with entity-click filter.
  - **Entity-level connection view (2026-04-23):** clicking an entity in the country side panel now updates the map — the country node label changes to the entity name, and only arcs connecting that specific entity to other countries are shown (investor→company for IN-; investor→portfolio countries for IV-). Clicking the entity-labeled node restores the country view. `restoreCountryLabels()` helper added; `activePairs` Set tracks entity-specific src→tgt arc pairs; entity ISO now included in `activeISOs` for IV entities (fixes investor country node being incorrectly dimmed).
  - **Clickable investors in company detail (2026-04-23):** resolved IV-* investors in the entity detail panel are now clickable — fires `filterMapByEntity` for the investor, showing investor profile + map connections. `restoreCountryLabels()` called at top of `filterMapByEntity` to clear stale entity label on entity→entity navigation.
  - **Clickable portfolio companies in investor detail (2026-04-23):** portfolio companies (IN-*) in IV entity detail panel are now clickable — same pattern as investor click, reuses existing `[data-action="filterMapByEntity"]` wiring.
  - **Map label font size +25% (2026-04-23):** `baseFs` constant raised from 11 to 13.75; applies uniformly to all country labels at all zoom levels.
  - **URL routing (2026-04-23):** `pushState`/`popstate` routing on all map interactions:
    - `index.html` → default panel
    - `index.html?country=840&countryname=United+States` → country selected
    - `index.html?country=840&countryname=United+States&entity=IN-0004&entityname=Adobe` → entity detail panel
    - Entity name click in country panel → entity detail URL (not direct search.html navigation)
    - Entity detail panel has "Open profile →" link to `search.html`
    - Browser back from `search.html` restores entity detail panel via URL params read in `init()`
  - Filter bar: click a company/investor to highlight connected countries on map
  - Data loaded from `data/database.json` (no AppState/SPA — standalone fetch)
  - Libraries: D3 v7, topojson-client@3, world-atlas@2 (CDN)
- [x] **`search.html`** — org search (ported from old `index.html`, navbar added)
  - **Relationships card (2026-04-22):** entity profile now shows a Relationships card with clickable portfolio companies (for IV entities) and investors (for IN entities) — data from `REL_MAP`
  - **infCardBody enhanced (2026-04-22):** shows `roles`, `tags`, `wikidata_id` from entity root alongside sources.infonodes fields
  - **Back-nav fix (2026-04-23):** `Router.replace(item)` added to `web/router.js`; initial URL-based load uses `replaceState` instead of `pushState` to avoid duplicate history entry (was causing double Back click to leave the page)
- [x] **`networks.html`**, **`publications.html`**, **`about.html`** — placeholder pages (TBD content)
- [x] **`web/theme.js`** — shared dark/light theme toggle across all pages
- [x] **`web/base.css`** — added `a.tnav-btn` rule for `<a>` tag navbar links

### Investor pipeline (2026-04-22)
- [x] `scripts/import_investors_crunchbase.py`: 610 IV-NNNN entities + 897 relationships created from `crunchbase.top_investors`
- [x] `scripts/patch_investor_countries.py`: 59 investors assigned country via curated lookup (major VC firms, EU/US institutions, banks)
- [x] Map arcs: **60 cross-border investor connections** now visible (USA largest hub)
- [x] **SPARQL Wikidata enrichment complete (2026-04-22):** `import_investors_crunchbase.py --wikidata --force-wikidata` — 194/610 matched (32%). IV with country: 59→182. Cross-border arcs: 60→106. validate.py PASSED.
- [x] **P159/P17 fallback enrichment (2026-04-22):** `patch_iv_countries_p159.py` — 23/40 remaining QID-bearing investors resolved via headquarters location → country. IV with country: 182→205. Arcs: 106→115.
- [x] **validate.py fixes (2026-04-22):** check 2 adapted for relationships without `id` field (uses `(source,target,type)` key); `VALID_ENTITY_TYPES` extended with `investor` and `public_fund`.
- [x] **Old DB migration (2026-04-22):** `scripts/migrate_old_db_investors.py` — +57 IV entities (IV-0611–IV-0667), +95 relationships from legacy `../refactoring/data/database.json`. Total: 2023 entities, 992 relationships. validate.py PASSED.
- [x] **KNOWN dict extension (2026-04-22):** `patch_investor_countries.py` — +62 entries covering UK, France, Germany, USA (banks/VC/gov), Canada, South Africa, Spain, China, South Korea, Sweden, Australia, Brazil, Belgium, Japan, Finland, Chile. IV with country: 205→275/667. Cross-border arcs: 115→129.
- [x] **Wikidata false positive audit (2026-04-22):** 9 IV QIDs nulled — label-only SPARQL match hit non-investor entities. Pattern and fix documented below.

#### Wikidata false positive pattern (IV investor enrichment)

**Root cause:** `import_investors_crunchbase.py --wikidata` matches investor names to Wikidata using a label search (SPARQL `rdfs:label` / `skos:altLabel`) without filtering by entity type (`wdt:P31`). Investor names like "Chapter One", "Greylock", "Bond", "Canary" are common English words/phrases, producing hits on unrelated entities.

**False positive categories observed:**
- Geographic entities: hamlet (Greylock → Q122567544, Massachusetts), city (Noordwijk → Q455464, Netherlands), parish (Canary → Q63519398, New South Wales)
- Cultural entities: restaurant (Chapter One → Q2129707, Dublin), band (Inc. → Q17484173, NASA → Q24876045), record label (GSR → Q59677963)
- Unrelated companies: motorcycle manufacturer (Bond → Q2866747), legal entity in Latvia (IQ Capital → Q104427238)

**Nulled in this pass (2026-04-22):** IV-0083 Bond, IV-0100 Canary, IV-0114 Chapter One, IV-0247 Greylock, IV-0249 GSR, IV-0279 Inc., IV-0308 IQ Capital, IV-0398 NASA, IV-0415 Noordwijk.

**Fix implemented (2026-04-22):** `_NON_INVESTOR_SIGNALS` frozenset added to `import_investors_crunchbase.py`. After each SPARQL match, the description is checked against known non-investor patterns (`restaurant`, `hamlet`, `municipality`, `parish`, ` band`, `record label`, `legal entity`). Any hit causes the match to be rejected and `None` returned — the entity stays with `wikidata_id = null`. Note: the P31 filter `wdt:P31/wdt:P279* wd:Q43229` was already in the query but is ineffective alone because Wikidata's "organisation" class includes restaurants, bands, etc. One edge case not covered: "UK historical motorcycle manufacturer" (Bond) — "manufacturer" is also used by legitimate corporate investors; Bond's QID remains null.

### EDF frontend (2026-04-23)
- [x] `web/app.js` — REL_MAP extended for `edf_participation` (edf_participant/edf_member roles)
- [x] Entity profile EDF card: immediate project list from REL_MAP (no lazy-load), with role, share, dates, EU Portal link
- [x] Co-participant expand: clickable list of co-participants with role, country, EU contribution — navigates to their profile
- [x] `renderEdfProjectProfile`: full profile for EDF-NNNN project entities — stats bar (participants, EU contribution, dates, status), Project details card, Participants card (sorted coordinator-first, all clickable)
- [x] `buildRegistry`: EDF project entities indexed by acronym, call_id, call_title (searchable as "ENGRT II", "AI-WASP", etc.)
- [x] `search.html`: `thirdParty` role badge styled (grey, distinct from coordinator/participant)

### EDF participation relationships (2026-04-23)
- [x] `scripts/import_edf_projects.py` — creates 78 `EDF-NNNN` project entities + 1657 `edf_participation` relationships
  - All 1657 participant slots matched via PIC→db_id crosswalk in `data/edf_orgs.json` (0 missing)
  - Each relationship: `source`=entity db_id, `target`=EDF-NNNN, `role` (coordinator/participant), `eu_contribution`
  - Entity sources: `sources.edf_project` with project_id, acronym, call_id, call_title, status, dates, budget, url, type_of_action
  - `validate.py` extended: `edf_project` added to `VALID_ENTITY_TYPES`
  - validate.py PASSED

### Infrastructure
- [x] Schema v3.0 (`docs/SCHEMA.md`)
- [x] Update protocol (`docs/UPDATE_PROTOCOL.md`)
- [x] QID lookup process (`docs/QID_LOOKUP_PROCESS.md`)
- [x] validate.py (10 checks including PER-NNNN, rel types, edf date format)
- [x] .gitignore (excludes `__pycache__/`, `*.pyc`, `*.bak`)
- [x] Initial commit on branch `nuovoDB`
- [x] `scripts/reprocess_skipped_qids.py` — 4-phase QID second-pass recovery script
- [x] `scripts/audit_quality.py` — data quality audit (reconciliation + field conflicts)
- [x] `scripts/enrich_wikidata.py` — Wikidata enrichment script (`sources.wikidata`)
- [x] `scripts/import_crunchbase_csv.py` — Crunchbase import (4-tier matching, field-level diff, re-run safe)
- [x] `scripts/regenerate_export.py` — regenerates companies_export.csv from DB
- [x] `data/crunchbase_sandbox/CRUNCHBASE.md` — Crunchbase process + reconciliation log

---

## Pending work (priority order)

### 0. Data quality — resolve flagged conflicts

From `audit_quality.py` (Audit C), 44 entities originally had `field_conflict` validation entries:

- **3 real country conflicts** — RESOLVED (2026-04-23, `patch_country_quality.py`):
  - `IN-1234` Destinus: infonodes.country set to Switzerland (was Netherlands); wikidata confirmed correct
  - `IN-1262` Chemring Group: UK confirmed (wikidata P17=Germany is Wikidata error); field_conflict→confirmed
  - `IN-1340` Umicore: Belgium confirmed; WARNING: wikidata_id Q107518759 = US subsidiary, QID needs replacing
- **15 country normalisation gaps** — RESOLVED (2026-04-23): all 40 entities with `sources.wikidata.country="People's Republic of China"` normalised to "China"; 15 field_conflicts resolved
- **30 real HQ conflicts**: city differs between wikidata and crunchbase — low priority; resolve when crunchbase is re-enriched
- **55 duplicate wikidata_ids** — RESOLVED (2026-04-23):
  - 9 groups: `accepted_duplicate` — share classes / different exchange listings (no QID change)
  - 8 groups: `expected_iv_in_duplicate` — company also acts as investor (no QID change)
  - 1 merge: IV-0240 Government of Canada retired → IV-0617 Canadian Government (relationship migrated)
  - 8 QIDs nulled: same entity under old/ticker name (IBM, PLS, VALE DO RIO DOCE, TKMS, Saab Aktiebolag, Telecom Italia S.p.a, Fortescue Metals Group, Meta for Developers)
  - 8 QIDs nulled: national sibling subsidiaries with parent QID misapplied (Integrasys×2, UMS×2, Airbus Ops×2, Arianegroup×2)
  - 35 QIDs nulled: parent QID misapplied to subsidiaries (Phase F — 24 groups)
  - 19 groups remain: all intentional (share classes + IV+IN, all tagged)
  - 12 relationships migrated to canonical entities (IN-1253→IN-0035 ×4, IN-1298→IN-0753 ×8)
  - IN-0723 Helsing: 5 relationships remain on nulled entity — flagged `needs_review` (UK vs German entity ambiguity)

### 1. Phase 2: Crunchbase enrichment — Cycle 1 COMPLETE

**Status:** Real import complete (2026-04-14). 731 entities now have `sources.crunchbase`.

**21 unresolved entities:** See `data/crunchbase_sandbox/CRUNCHBASE.md` — categorised as:
- Category A (11): linkable but name too short/different for automatic matching — manual alias needed
- Category B (3): wrong CB match (CB matched a different company) — do not import
- Category C (7): genuine mismatches or entities not in DB — skip

**Next cycle:** Run `python3 scripts/regenerate_export.py` to refresh the export, then re-upload to Crunchbase for a Cycle 2 enrichment pass.

### 3. Phase 3: Investment graph — COMPLETE (Crunchbase + old DB migration)

**Status (2026-04-22):** 667 IV entities + 992 relationships. 275 IV have country data → 129 cross-border map arcs.

**To increase arc coverage further:**
- Run `patch_iv_countries_p159.py` again if new QIDs are applied to IV entities
- Extend `KNOWN` dict in `patch_investor_countries.py` for any new investor names
- Run Crunchbase Cycle 2 to pick up new `top_investors` data
- **Known gap — QID found but P17 missing:** 392 IV entities still lack country. ~17 have QIDs with no P17 (run `patch_iv_countries_p159.py` again after any new QIDs). Rest (~375) have no QID at all.

### 4. Phase 4: EDF participation relationships — COMPLETE (2026-04-23)

- **78 EDF project entities** (type: `edf_project`, prefix `EDF-NNNN`) created from 64 calls with projects
- **1657 `edf_participation` relationships** (source=IN-*/IV-*/etc, target=EDF-NNNN)
- Each relationship carries: `role` (coordinator/participant), `eu_contribution`
- `validate.py` extended: `edf_project` added to `VALID_ENTITY_TYPES`
- Script: `scripts/import_edf_projects.py` (re-run safe, `--dry-run` flag)
- validate.py PASSED after import

### 5. QID lookup — second pass (complete)
- **455 companies** still without wikidata_id — 694/1149 (60.4%) now have QIDs
- All 267 proposals reviewed and applied (2026-04-13)
- 411 skipped entries remain — mostly EDF SMEs genuinely absent from Wikidata, or iShares truncated names (~35 chars)
- Optional: run `reprocess_skipped_qids.py` again for any remaining matches

---

## Key decisions (do not revisit without strong reason)

| Decision | Rationale |
|---|---|
| `wikidata_id` as primary bridge identifier across sources | Entity resolution: same company appears as "Leonardo" / "Leonardo SPA" / "Leonardo Società per azioni" |
| Deduplication by `name_key` (strip legal suffixes, uppercase, collapse whitespace) | Prevents duplicate entities from same company listed on different exchanges |
| EDF matching: conservative (2 auto-matched, 792 new entities) | False positives in entity matching must not happen |
| `sources.ishares` is array, not object | Same company can appear in multiple ETFs |
| ISIN not used | iShares CSVs do not contain ISIN column |
| QID false positives: must never happen | Strict label + description keyword filtering enforced in all search scripts |
| HTTP 429: must never happen | 1.5s delay (Phase 1), 2s delay (Phase 1b), backoff [4, 8, 16]s |
| SPARQL `skos:altLabel` batch queries: avoided | Too expensive on public endpoint, consistently times out |
| Disqualify keywords: word-boundary for `nation/state/sea/actor/region` | Substring match causes false positives (`"multinational"` → disqualified by `"nation"`) |
| `"video game"` removed from disqualify list | "video game **company**" is a valid org type; EA/Konami/Take-Two all have "company" in description |
| P856 SPARQL batch size: 10 entities (≤80 URL variants) | Larger batches cause HTTP 414/431 on Wikidata SPARQL endpoint |
| P856 false positives: accepted as review items | URL match is high-precision but some subsidiaries share parent's website; human reviewer corrects QID |
