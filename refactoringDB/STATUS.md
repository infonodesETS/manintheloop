# refactoringDB — Project Status

> Authoritative resume point for AI-assisted work.
> Last updated: 2026-04-12 (website enrichment complete)

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

### Crunchbase enrichment pipeline (Phase 2 — not yet started)

```bash
# Input: data/companies_export.csv (1149 rows: name + website)
# Upload to Crunchbase bulk enrichment tool, receive enriched CSV

# Step 1 — Import enriched CSV (script not yet written)
#    Reads: <crunchbase_output.csv>, data/database.json
#    Writes: data/database.json (sources.crunchbase + history[] + validation[])
#            PER-NNNN entities for board members
#            REL-NNNN relationships of type board_membership
python3 scripts/import_crunchbase_csv.py <crunchbase_output.csv> [--dry-run]

# Step 2 — Regenerate export CSV after any DB update
#    Reads: data/database.json
#    Writes: data/companies_export.csv
python3 scripts/regenerate_export.py   # (not yet written — generate on demand)

# Validate
python3 scripts/validate.py
```

### Regenerate companies_export.csv (manual one-liner if no script)

```python
import json, csv
db = json.load(open('data/database.json'))
rows = []
for e in db['entities']:
    if e.get('type') != 'company': continue
    src = e.get('sources', {})
    website = (src.get('crunchbase') or {}).get('website') or (src.get('infonodes') or {}).get('website') or ''
    rows.append({'name': e['name'], 'website': website})
rows.sort(key=lambda r: r['name'])
with open('data/companies_export.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['name', 'website']); w.writeheader(); w.writerows(rows)
```

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
├── data/
│   ├── database.json          ← main DB (schema v3.0) — primary artifact
│   ├── edf_orgs.json          ← PIC-keyed index of 794 EDF orgs with db_id crosswalk
│   ├── qid_candidates.json    ← QID review file (all 325 entries reviewed)
│   └── companies_export.csv   ← STALE — needs regeneration
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
│   └── validate.py            ← 10-check validation (always run before committing)
├── docs/
│   ├── SCHEMA.md
│   ├── UPDATE_PROTOCOL.md
│   └── QID_LOOKUP_PROCESS.md
└── STATUS.md                  ← this file
```

---

## Current DB state (2026-04-12)

| Metric | Value |
|---|---|
| Schema | 3.0 |
| Total entities | 1356 |
| — companies (IN-NNNN) | 1149 |
| — institutions | 184 |
| — government_agencies | 23 |
| — persons (PER-NNNN) | **0** — not yet built |
| — investors (IV-NNNN) | **0** — not yet migrated |
| Relationships | **0** — not yet built |
| Companies with wikidata_id | 455 / 1149 (39.6%) |
| Companies with sources.ishares | 434 |
| Companies with sources.edf | 587 |
| Entities with sources.crunchbase | 130 |
| Companies with sources.infonodes.website | 1126 / 1149 (98.0%) |
| Last validate.py | PASSED (2026-04-12) |

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
- [x] `companies_export.csv` regenerated with `name` + `website` columns (1149 rows)

### QID enrichment
- [x] Phase 1 — Wikidata Search API (`search_missing_qids.py --search`): 245 proposed
- [x] Phase 1b — SPARQL label lookup (`sparql_search_qids.py`): +34 found
- [x] Phase 1b — Reconciliation API (`sparql_search_qids.py`): +46 found
- [x] Human review: 309 accepted, 16 rejected (of 325 proposed)
- [x] `--apply` run: 309 QIDs written to database.json
- [x] validate.py passed after apply

### Infrastructure
- [x] Schema v3.0 (`docs/SCHEMA.md`)
- [x] Update protocol (`docs/UPDATE_PROTOCOL.md`)
- [x] QID lookup process (`docs/QID_LOOKUP_PROCESS.md`)
- [x] validate.py (10 checks including PER-NNNN, rel types, edf date format)
- [x] .gitignore (excludes `__pycache__/`, `*.pyc`, `*.bak`)
- [x] Initial commit on branch `nuovoDB`

---

## Pending work (priority order)

### 1. Phase 2: Crunchbase enrichment — full CSV import

**Input:** `data/companies_export.csv` (1149 rows: `name` + `website`) → upload to Crunchbase bulk enrichment.

**Expected output:** Crunchbase returns a CSV with fields per company — funding, board members, description, HQ, etc.

**Import steps:**
1. Write `scripts/import_crunchbase_csv.py` to parse the returned CSV
2. Map fields → `sources.crunchbase` block per entity (by name/website match)
3. For each enriched entity: append `history[]` per field + `validation[]` entry `status: "crunchbase_enriched"`
4. Extract board members → create **PER-NNNN** entities + **REL-NNNN** `board_membership` relationships
5. Validate and commit

- Follow `docs/UPDATE_PROTOCOL.md` — "Adding a new person (PER entity)" and "Updating an existing entity field"

### 3. Phase 3: Investment graph migration from old DB
- Old DB (`../refactoring/data/database.json`) has 140 funds + 28 banks not yet in new DB
- Old DB has 293 `investment` relationships not yet migrated
- Create **IV-NNNN** entities for funds/banks, then **REL-NNNN** relationships
- Follow `docs/SCHEMA.md` — investor entity structure

### 4. Phase 4: EDF participation relationships
- 587 companies have `sources.edf` but no relationships yet
- Build `edf_participation` relationships from `rawdata/edf_calls.json`
- Links IN-NNNN / institution entities → EDF projects/calls
- Source of truth: `rawdata/edf_calls.json` (dict keyed by call identifier, each call has `projects[]` with `participants[]`)

### 5. QID lookup — second pass
- 694 companies still without wikidata_id
- Mostly EDF SMEs or obscure mining companies (many genuinely absent from Wikidata)
- Some have truncated names from iShares CSV (cut at ~35 chars)
- Re-run pipeline: see `docs/QID_LOOKUP_PROCESS.md`

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
