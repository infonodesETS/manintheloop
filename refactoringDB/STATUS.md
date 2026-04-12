# refactoringDB — Project Status

> This file is the authoritative resume point for AI-assisted work.
> Update it after every significant session.
> Last updated: 2026-04-12

---

## What this project is

A new graph database (`refactoringDB/`) built alongside the old one (`../refactoring/`).
It integrates three data universes into a single schema v3.0:

1. **iShares ETF holdings** — Mining (GICS 151040), Tech (GICS 45), Comm Services (GICS 50)
2. **EDF (European Defence Fund) beneficiaries** — from `rawdata/edf_calls.json`
3. **Companies/startups** — migrated from `../refactoring/data/database.json`

The old DB is schema v2.0 and is **read-only** — never modify it.
All work happens inside `refactoringDB/` only.

---

## Current DB state (2026-04-12)

| Metric | Value |
|---|---|
| Schema | 3.0 |
| Total entities | 1356 |
| — companies | 1149 |
| — institutions | 184 |
| — government_agencies | 23 |
| — persons (PER-NNNN) | 0 (not yet built) |
| Relationships | 0 (not yet built) |
| Companies with wikidata_id | 455 / 1149 (39.6%) |
| Companies with sources.ishares | 434 |
| Companies with sources.edf | 587 |
| Entities with sources.crunchbase | 130 |

---

## Folder structure

```
refactoringDB/
├── data/
│   ├── database.json          ← main DB (schema v3.0)
│   ├── edf_orgs.json          ← PIC-keyed index of 794 EDF orgs with db_id crosswalk
│   ├── qid_candidates.json    ← QID review file (all entries reviewed, 309 accepted)
│   └── companies_export.csv   ← STALE — needs regeneration
├── rawdata/
│   ├── edf_calls.json         ← EDF raw data (copied from ../refactoring/data/)
│   ├── ishares_metals_mining_gics151040.csv
│   ├── ishares_tech_gics45.csv
│   └── ishares_comm_services_gics50.csv
├── scripts/
│   ├── parse_ishares.py       ← parses iShares CSVs into normalized dicts
│   ├── build_database.py      ← builds DB from iShares CSVs (dedup by name_key)
│   ├── build_edf_entities.py  ← imports EDF orgs, writes edf_orgs.json
│   ├── import_startups.py     ← migrates startups from old DB
│   ├── import_by_wikidata.py  ← migrates companies from old DB by wikidata_id
│   ├── search_missing_qids.py ← Phase 1 QID search (Wikidata API) + --apply
│   ├── sparql_search_qids.py  ← Phase 1b QID search (SPARQL + Reconciliation API)
│   └── validate.py            ← 10-check validation (must pass before every commit)
├── docs/
│   ├── SCHEMA.md              ← schema v3.0 full specification
│   ├── UPDATE_PROTOCOL.md     ← rules for IDs, history, validation
│   └── QID_LOOKUP_PROCESS.md  ← how to run QID lookup pipeline
└── STATUS.md                  ← this file
```

---

## What has been done

### Data import
- [x] 434 companies from 3 iShares ETF CSVs (deduplicated by name_key)
- [x] 794 EDF beneficiary orgs imported (2 matched to existing, 792 new entities)
- [x] 17 startups migrated from old DB (via `import_startups.py`)
- [x] 107 companies migrated from old DB with wikidata_id match
- [x] 6 companies migrated from old DB without wikidata_id (needs_review flag)

### QID enrichment
- [x] Phase 1: Wikidata Search API — 245 proposed
- [x] Phase 1b SPARQL: label-mismatch lookup — 34 additional found
- [x] Phase 1b Reconciliation API: no-results fallback — 46 additional found
- [x] Human review: 309 accepted, 16 rejected, 678 permanently skipped
- [x] `--apply` run: 309 QIDs written to database.json
- [x] `validate.py` passed after apply

### Infrastructure
- [x] Schema v3.0 defined (docs/SCHEMA.md)
- [x] UPDATE_PROTOCOL.md written
- [x] QID_LOOKUP_PROCESS.md written
- [x] validate.py with 10 checks (incl. PER-NNNN, rel types, edf date format)
- [x] Initial git commit on branch `nuovoDB`

---

## What is NOT done yet (priority order)

### 1. Regenerate companies_export.csv
The CSV is stale (built at 1036 entities, now 1356).
```bash
python3 -c "
import json, csv
with open('data/database.json') as f:
    db = json.load(f)
companies = [e for e in db['entities'] if e.get('type')=='company']
with open('data/companies_export.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['name', 'domain'])
    for e in sorted(companies, key=lambda x: x['name']):
        domain = (e.get('sources') or {}).get('crunchbase', {})
        domain = domain.get('domain', '') if isinstance(domain, dict) else ''
        w.writerow([e['name'], domain])
print('Done.')
"
```

### 2. Phase 2: Crunchbase enrichment (board members)
- 130 companies have `sources.crunchbase` blocks
- Extract board members → create PER-NNNN entities
- Create `board_membership` relationships (PER → IN)
- Schema: PER-NNNN IDs, `board_member` role, `board_membership` rel type

### 3. Phase 3: Investment graph migration
- Old DB has 140 funds + 28 banks (investors) not yet in new DB
- Old DB has 293 `investment` relationships not yet migrated
- These need IV-NNNN entity IDs per schema v3.0

### 4. Phase 4: EDF participation relationships
- 587 companies have `sources.edf` but no relationships yet
- Build `edf_participation` relationships from `rawdata/edf_calls.json`
- Links IN-NNNN / institution entities → EDF projects/calls

### 5. QID lookup — second pass
- 694 companies still without wikidata_id
- Most are EDF SMEs or obscure mining companies
- Some have truncated names from iShares CSV (cut at ~35 chars)
- See `docs/QID_LOOKUP_PROCESS.md` for how to re-run the pipeline

---

## Key decisions made

- **Entity resolution**: wikidata_id is the primary bridge identifier across sources
- **Deduplication**: by `name_key` (normalized: strip legal suffixes, uppercase, collapse whitespace)
- **EDF matching**: conservative — only 2 auto-matched to existing entities; rest created as new entities to avoid false positives
- **iShares dual-listed stocks**: same company on multiple exchanges → one entity, `sources.ishares` is array
- **No ISIN**: iShares CSVs do not contain ISIN column
- **QID false positives**: must never happen — strict label + description filtering enforced
- **HTTP 429**: must never happen — 1.5s delay (Phase 1), 2s delay (Phase 1b), backoff [4,8,16]s

---

## How to validate

Always run before committing:
```bash
python3 scripts/validate.py
```
Must output `VALIDATION PASSED ✓`.

---

## Git

- Branch: `nuovoDB`
- Main branch: `main`
- Last commit: `feat(refactoringDB): initialize graph database v3.0 with QID enrichment`
