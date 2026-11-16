# Scripts reference

> Spostato da `STATUS.md` (stato `4c437bf`), testo invariato. Non è un punto di ripartenza: le informazioni qui possono essere datate. Prima di fidarsi di un numero o di un percorso, rimisurare.

## Scripts reference

> Run `python3 scripts/validate.py` after any script that modifies `database.json`.
> All paths are relative to `refactoringDB/`.

### Playwright screenshots

All screenshots taken during Playwright sessions must be saved to `tmp/playwright/` (create the folder if it doesn't exist). The entire `tmp/` directory is in `.gitignore` — never commit screenshots.

### Always-safe commands

| Command | What it does | Safe to re-run? |
|---|---|---|
| `python3 scripts/validate.py` | 10-check validation — never modifies DB | Yes |
| `python3 scripts/check_docs.py` | Confronta le PR fuse in `main` con quelle citate in piano, log e `STATUS.md`; segnala l'arretrato (exit 1) | Yes |
| `python3 scripts/parse_ishares.py <csv>` | Prints normalised rows to stdout | Yes |
| `python3 scripts/audit_quality.py --dry-run` | Audit B+C report only — never modifies DB | Yes |
| `python3 scripts/enrich_wikidata.py --dry-run` | Fetch + print Wikidata data, no DB writes | Yes |

### Wikidata enrichment

```bash
# Populate sources.wikidata for all entities with a wikidata_id (skips already-enriched)
#   Reads: docs/data/database.json  |  API: wbgetentities (batches of 50, 2s delay)
#   Writes: docs/data/database.json (sources.wikidata + history[] + validation[wikidata_enriched])
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
#    Reads: docs/data/edf_orgs.json, docs/data/database.json
#    Writes: docs/data/database.json (sources.infonodes.website + history[])
#    Skip: entities that already have crunchbase.website
python3 scripts/import_edf_websites.py [--dry-run]

# 2. Fetch official website (P856) from Wikidata for companies with wikidata_id but no website
#    Reads: docs/data/database.json  |  API: SPARQL (batches of 50, 2s delay)
#    Writes: docs/data/database.json (sources.infonodes.website + history[])
python3 scripts/fetch_wikidata_websites.py [--dry-run]

# 3. Validate
python3 scripts/validate.py
```

Re-run safety: both scripts skip entities that already have a website set → safe to re-run.

### QID enrichment pipeline

```bash
# Phase 1 — Wikidata Search API (resumes from checkpoint if qid_candidates.json exists)
#    Reads: docs/data/database.json  |  Writes: work/qid_candidates.json (status=proposed/skipped)
#    API: wbsearchentities REST, 1.5s delay
python3 scripts/search_missing_qids.py --search

# Phase 1b — SPARQL label lookup + Reconciliation API for Phase 1 skipped entries
#    Reads: work/qid_candidates.json  |  Writes: work/qid_candidates.json (in-place)
#    Never overwrites accepted/rejected entries
python3 scripts/sparql_search_qids.py

# Phase 2 — Human review
# Open work/qid_candidates.json
# Change each "proposed" entry to "accepted" or "rejected"

# Phase 3 — Apply accepted QIDs to database.json
#    Reads: work/qid_candidates.json (accepted only)
#    Writes: docs/data/database.json (wikidata_id + history[] + validation[])
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
#    Writes: work/qid_candidates.json only — never touches database.json
python3 scripts/reprocess_skipped_qids.py

# Then review qid_candidates.json (proposed → accepted/rejected), then apply:
python3 scripts/search_missing_qids.py --apply
python3 scripts/validate.py
```

### EDF participation pipeline (2026-04-23)

```bash
# Create EDF-NNNN project entities + edf_participation relationships
#   Reads: rawdata/edf_calls.json, docs/data/edf_orgs.json, docs/data/database.json
#   Writes: docs/data/database.json (+78 EDF-NNNN entities, +1657 edf_participation rels)
python3 scripts/import_edf_projects.py [--dry-run]

# Validate
python3 scripts/validate.py
```

Re-run safety: skips existing EDF-NNNN entities (matched by project_id) and duplicate relationships.

### Investor pipeline (new — 2026-04-22)

```bash
# Step 1 — Create IV-NNNN entities + investment relationships from crunchbase.top_investors
#   Reads: docs/data/database.json
#   Writes: docs/data/database.json (+IV entities, +relationships)
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

> **Full process documentation:** `work/crunchbase/CRUNCHBASE.md`

```
work/crunchbase/
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
    work/crunchbase/crunchbase-export-<label>-MM-DD-YYYY.csv \
    --dry-run

# Apply
python3 scripts/import_crunchbase_csv.py \
    work/crunchbase/crunchbase-export-<label>-MM-DD-YYYY.csv

# Validate
python3 scripts/validate.py
```

**Cycle 1 state (2026-04-14):** real import complete — 601 new + 121 updated = **731 entities** now have `sources.crunchbase`. 21 unresolved documented in `work/crunchbase/CRUNCHBASE.md`.

### One-time build scripts (do not re-run — they regenerate IDs from scratch)

| Script | Purpose | Status |
|---|---|---|
| `scripts/build_database.py` | Initial iShares ETF import → database.json | Done 2026-04-01 |
| `scripts/build_edf_entities.py` | EDF org import → 792 new entities | Done 2026-04-01 |
| `scripts/import_startups.py` | Migrates 17 startups from old DB | Done 2026-04-01 |
| `scripts/import_by_wikidata.py` | Migrates 107 companies from old DB via QID match | Done 2026-04-01 |

> **Warning:** Re-running any of these scripts will attempt to create duplicate entities. Never re-run without modifying them to skip existing IDs first.

