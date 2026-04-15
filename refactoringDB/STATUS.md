# refactoringDB — Project Status

> Authoritative resume point for AI-assisted work.
> Last updated: 2026-04-14 (dedup: 5 true-duplicate entities merged; Audit D flags 99 entities with shared wikidata_id; 2074 entities total)

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
| `python3 scripts/audit_quality.py --dry-run` | Audit B+C+D report only — never modifies DB | Yes |
| `python3 scripts/dedup_entities.py --list` | List all wikidata_id duplicate groups + auto-merge candidates | Yes |
| `python3 scripts/dedup_entities.py --merge A B --dry-run` | Preview merge of B into A — never modifies DB | Yes |
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
├── index.html                 ← web UI — org search + profile viewer (serve from Manintheloop/ root)
├── web/
│   ├── router.js              ← URL routing (?organization=IN-XXXX&organizationName=...)
│   ├── base.css               ← base styles (copied from ../refactoring/css/)
│   ├── components.css         ← component styles
│   └── companysearch.css      ← search/autocomplete/profile styles
├── data/
│   ├── database.json          ← main DB (schema v3.0) — primary artifact
│   ├── edf_orgs.json          ← PIC-keyed index of 794 EDF orgs with db_id crosswalk
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
│   ├── import_investors_csv.py  ← extracts IV-NNNN + REL-NNNN from CB export (Top5 + Lead Investors)
│   ├── regenerate_export.py   ← regenerates data/crunchbase_sandbox/companies_export.csv from DB
│   └── validate.py            ← 10-check validation (always run before committing)
├── docs/
│   ├── SCHEMA.md
│   ├── UPDATE_PROTOCOL.md
│   └── QID_LOOKUP_PROCESS.md
└── STATUS.md                  ← this file
```

> **Serving the web UI:** `python3 -m http.server 8000` from `Manintheloop/` root (one level above `refactoringDB/`), then open `http://localhost:8000/refactoringDB/`.

---

## Current DB state (2026-04-14)

| Metric | Value |
|---|---|
| Schema | 3.0 |
| Total entities | **2074** |
| — companies (IN-NNNN) | 1144 |
| — institutions + gov | 207 |
| — investors (IV-NNNN) | **723** (extracted from CB CSV Top 5 + Lead Investors) |
| — persons (PER-NNNN) | **0** — not yet built |
| Relationships | **1042** investment REL-NNNN (605 as lead) |
| Companies with wikidata_id | 710 / 1149 (61.8%) |
| Companies with sources.wikidata | 710 / 710 (100% of QID-bearing entities) |
| Companies with sources.ishares | 434 |
| Companies with sources.edf | 587 |
| Entities with sources.crunchbase | 687 (731 Cycle 1 − 44 bad matches removed 2026-04-14) |
| Companies with sources.infonodes.website | 1126 / 1149 (98.0%) |
| Last validate.py | PASSED (2026-04-14) |
| qid_candidates.json | proposed=0, accepted=566, rejected=65, skipped=372 |
| validation: reconciliation_documented | 690 entities |
| validation: field_conflict | 175 entities |
| validation: duplicate_wikidata_id | 94 entities (99 flagged − 5 already merged) |
| validation: merged_from | 5 entities |
| validation: needs_review | 2146 entries (ongoing) |

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

### Investor graph (2026-04-14)
- [x] `scripts/import_investors_csv.py` written — extracts unique investors from `Top 5 Investors` + `Lead Investors` columns of CB export
- [x] 723 IV-NNNN entities created (type inferred: fund / bank / government_agency)
- [x] 1042 REL-NNNN investment relationships created (605 as lead, `details.lead = true`)
- [x] Re-run safe: skips existing IV by normalised name, skips existing REL by source+target pair
- [x] `validate.py` PASSED (2079 entities, 1042 relationships)

### Entity deduplication (2026-04-14)
- [x] `scripts/dedup_entities.py` written — merge tool with `--list`, `--merge WINNER LOSER`, `--dry-run`
- [x] Merge logic: ishares entries appended (per ticker), edf/crunchbase/infonodes copied if missing, roles unioned, history/validation absorbed with `[from LOSER_ID]` prefix, relationships redirected + deduped
- [x] All changes tracked: history entry + `merged_from` validation entry on winner; loser removed from entities
- [x] **Audit D** added to `audit_quality.py`: flags all entities sharing a wikidata_id with `duplicate_wikidata_id` validation status
- [x] Audit D run: 46 QIDs shared → 99 entities flagged
- [x] **5 AUTO_MERGE pairs applied** (identical names, confirmed same legal entity):
  - IN-0365 ← IN-0366 (Telecom Italia / Telecom Italia S.p.a) — absorbed TITR ishares entry
  - IN-0472 ← IN-0473 (Airbus Operations × 2)
  - IN-0501 ← IN-0502 (Arianegroup × 2)
  - IN-0783 ← IN-0784 (Integrasys × 2)
  - IN-1167 ← IN-1168 (United Monolithic Semiconductors × 2)
- [x] validate.py PASSED — 2074 entities, 1042 relationships
- [x] **41 REVIEW pairs remain** — see `python3 scripts/dedup_entities.py --list` for full breakdown:
  - Share class variants (keep both): FOX A/B, TATA Steel/GDR
  - Parent + iShares listing duplicate: Palantir, MP Materials, Pilbara/PLS, Vale/VALE DO RIO DOCE, Fortescue, Grupo Mexico, IBM/Business Machines, Saab, TEKEVER/Tekever Uas, Nammo/Raufoss, Arafura
  - Subsidiary with likely wrong QID: Ericsson ×4, Airbus D&S ×4, KNDS ×3, Indra ×3, Safran pairs, Bittium pair, Damen pair, Helsing pair, Valneva pair, and others

### Crunchbase match audit (2026-04-14)
- [x] Discovered wrong CB match for IN-0032 Apple (matched to Apple Apaman, Japanese rental brokerage) — `sources.crunchbase` removed manually
- [x] Domain-mismatch audit: compared `sources.crunchbase.website` against `sources.infonodes.website` / `sources.wikidata.website` for all 731 CB-enriched entities
- [x] 144 domain mismatches found; classified into: confirmed bad (country mismatch), description contradiction, ambiguous/same-entity-different-domain
- [x] **44 bad matches removed** via two-pass audit:
  - 18 by country mismatch (CB HQ country contradicts known wikidata country — e.g. PLS AU→TX, Naval FR→BR, Delta Electronics TW→MA, Baltic Workboats EE→FL)
  - 26 by CB description contradiction keywords (DeFi/blockchain, clothing/crochet, sports club, toner cartridge, digital marketing agency, road maintenance, interior design, food marketplace, streaming service, asset management platform, community development, import/export)
- [x] validate.py PASSED — 2079 entities, 1042 relationships
- [x] ~100 remaining domain mismatches are ambiguous (parent/subsidiary/regional sites) — pending manual review CSV

### Web UI — `index.html` (2026-04-14)
- [x] Organisation search UI built from `data/database.json` (adapted from refactoring/tmp/new_index.html)
- [x] Autocomplete with source flag pills (CB / EDF / iShares / WD / INF) + type badge
- [x] URL routing: `?organization=IN-XXXX&organizationName=...` — deep-linkable, browser back/forward aware (`web/router.js`)
- [x] Profile header: name, type badge, source flags, EU status line, description, external links, stat bar
- [x] Single-column collapsible source cards (all expanded by default, independently closable):
  - Infonodes → Wikidata → iShares (ETF table) → Crunchbase (grouped: Identity/Industry/Funding/Team) → EDF (org details + lazy project load) → Change History → Validation
- [x] EDF projects: lazy-loaded on demand, with participant expand/collapse; clicking a participant navigates to their profile
- [x] CSS/JS internal dependencies moved to `web/` folder (base.css, components.css, companysearch.css, router.js)
- [x] Investor search + portfolio profile: IV-NNNN entities searchable; profile shows portfolio card (leads first, clickable → company), Wikidata data, history, validation

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
- [x] `scripts/import_investors_csv.py` — investor graph builder (IV-NNNN + REL-NNNN from CB export)
- [x] `scripts/regenerate_export.py` — regenerates companies_export.csv from DB
- [x] `data/crunchbase_sandbox/CRUNCHBASE.md` — Crunchbase process + reconciliation log

---

## Pending work (priority order)

### 0a. Entity deduplication — 41 REVIEW pairs remaining

From `python3 scripts/dedup_entities.py --list`. Each pair needs a decision:
- **Keep both** (share class variants): FOX A/B (Q60238941), TATA Steel/GDR (Q963101), Samsung/NON Voting (Q20718), SSAB A/B (Q54075), Alphabet A/C (Q20800404), Jiangxi Copper A/H (Q1518015)
- **Merge** (same company, different name/era): IBM/Business Machines, Vale/VALE DO RIO DOCE, Fortescue/FMG, Arafura/Rare Earths, Palantir A, MP Materials A, Grupo Mexico B, Pilbara/PLS, Saab/Aktiebolag, TEKEVER/UAS, Nammo/Raufoss, TSMC/Arizona, Telefonica/Moviles
- **Fix QID on subsidiary** (wrong QID inherited from CB match): Ericsson ×4, Airbus D&S ×4, KNDS ×3, Indra ×3, Safran pairs, Bittium pair, Damen pair, Helsing pair, Valneva pair, Beyond Gravity pair, MBDA pair, Renk pair, Tekever, Telespazio, TKMS/ThyssenKrupp, Eviden pair, Chinalco pair, Patria pair, Knds Ammo
- For merges: run `python3 scripts/dedup_entities.py --merge WINNER LOSER`
- For QID fixes: update wikidata_id on subsidiary to correct QID (or null), then re-run `enrich_wikidata.py`

### 0b. Crunchbase match audit — remaining ~100 ambiguous domain mismatches

From the 2026-04-14 audit, ~100 entities have a CB website that differs from the known website but was not auto-removed (no country mismatch, no description contradiction). These are likely parent/subsidiary/regional-domain cases but need human confirmation.

- Generate review CSV: `id, name, known_website, cb_website, cb_hq, cb_description`
- For each row: mark `ok` (same entity, different domain) or `wrong` (different company)
- For `wrong` entries: remove `sources.crunchbase` via a patch script
- Key ambiguous cases noted: Airbus subsidiaries (IN-0463–0467), Safran subsidiaries, Rockwell Collins→Collins Aerospace rebrand, D-Orbit rebrand, Phaxiam→Erytech rebrand, Talgen/Nortal

### 0c. Data quality — resolve flagged conflicts

From `audit_quality.py` (Audit C), 44 entities have `field_conflict` validation entries:

- **3 real country conflicts** (manual review required):
  - `IN-1234` Destinus: wikidata=Switzerland, infonodes=Netherlands
  - `IN-1262` Chemring Group: wikidata=Germany, infonodes=United Kingdom
  - `IN-1340` Umicore: wikidata=United States, infonodes=Belgium
  - For each: verify the correct country, set canonical value in `sources.infonodes.country`, append `history[]` entry, resolve `field_conflict` → `confirmed`
- **15 country normalisation gaps**: "People's Republic of China" vs "China" — normalise `sources.wikidata.country` to short ISO 3166 form (or vice versa) via a one-off script
- **30 real HQ conflicts**: city differs between wikidata and crunchbase — low priority; resolve when crunchbase is re-enriched
- **46 duplicate wikidata_ids** (Audit A — deferred): same QID on multiple entities (share classes, subsidiaries); requires case-by-case review

### 1. Phase 2: Crunchbase enrichment — Cycle 1 COMPLETE

**Status:** Real import complete (2026-04-14). 731 entities now have `sources.crunchbase`.

**21 unresolved entities:** See `data/crunchbase_sandbox/CRUNCHBASE.md` — categorised as:
- Category A (11): linkable but name too short/different for automatic matching — manual alias needed
- Category B (3): wrong CB match (CB matched a different company) — do not import
- Category C (7): genuine mismatches or entities not in DB — skip

**Next cycle:** Run `python3 scripts/regenerate_export.py` to refresh the export, then re-upload to Crunchbase for a Cycle 2 enrichment pass.

### 3. Phase 3: Investment graph — COMPLETE (2026-04-14)
- 723 IV-NNNN entities built from CB CSV (Top 5 + Lead Investors)
- 1042 REL-NNNN investment relationships (605 lead)
- **Optional next steps:**
  - Wikidata enrichment for IV-NNNN entities (QID pipeline already written — run `search_missing_qids.py` targeting IV- entities)
  - Old DB had 233 IV- entities with partial Wikidata data — cross-reference and carry over via name match if needed
  - Cycle 2 CB export could add investor-level CB profiles (separate upload targeting investor names)

### 4. Phase 4: EDF participation relationships
- 587 companies have `sources.edf` but no relationships yet
- Build `edf_participation` relationships from `rawdata/edf_calls.json`
- Links IN-NNNN / institution entities → EDF projects/calls
- Source of truth: `rawdata/edf_calls.json` (dict keyed by call identifier, each call has `projects[]` with `participants[]`)

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
