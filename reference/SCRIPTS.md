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
| `python3 scripts/checks/check_site_refs.py [cartella]` | Ogni file locale richiamato dalle pagine e dai moduli di `docs/` (`src`, `href`, `fetch`, `import`) esiste; exit 1 con l'elenco dei mancanti. Gira anche nell'Action `Controlli PR` (F5.1) | Yes |
| `python3 scripts/checks/check_site_clean.py [cartella]` | In `docs/` solo i file del sito (pagine e `CNAME`, i JSON ammessi in `data/`, `.js`/`.css` in `web/`, `.html` in `reports/`, niente file nascosti); un file nuovo da pubblicare si aggiunge all'elenco nello script. Exit 1 con l'elenco. Gira nell'Action `Controlli PR` (F5.2) | Yes |
| `python3 scripts/checks/check_index.py [database] [indice]` | Indice MARLA (`docs/data/mitl-index.json`) coerente con il database (F5.4). **Errori** (exit 1): JSON non valido, chiavi mancanti, `sito` diverso dall'URL di MARLA, `id` assenti dal database o doppi o nella lista sbagliata, relazioni verso `id` fuori dall'indice, tipo di relazione non ammesso (elenco letto da `validate.py`), `url` sbagliati. **Avvisi** (exit 0, anche come `::warning::` sulla PR): schede ritirate ancora nell'indice, soggetti, progetti o relazioni del database che mancano nell'indice o viceversa, `generato` più vecchio di `_updated`. Non importa `build_chat_index.py`. Nell'Action «Controlli PR». |
| `python3 scripts/sync_site_data.py --check` | Nell'Action «Controlli PR» (F5.6): `docs/data/edf_calls.json` identico a `rawdata/edf_calls.json`; il filtro dei percorsi comprende `rawdata/edf_calls.json`. |
| `python3 scripts/checks/check_secrets_paths.py [cartella]` | Nei file tracciati (o in una cartella, per le prove) nessun percorso personale (`/home/<utente>/`, `/Users/…/`, `C:\Users\…`), chiave privata, token noto (GitHub, `sk-`, AWS, Exa), segreto assegnato o email di provider personali; non stampa mai il valore intero. Exit 1 con l'elenco. Gira su **tutte** le PR nell'Action `Segreti e percorsi` (F5.3) | Yes |
| `python3 -I scripts/check_parte_di_branch.py` | Controlla in sola lettura che un branch abbia solo aggiunto legami `parte_di` (e le relative validation) rispetto a `origin/main` | Yes |
| `python3 scripts/patch_set_infonodes.py ID tax_id VALORE --source … --why …` | Dry-run di default: scrive `tax_id` in un campo vuoto (con fonte primaria); rifiuta se il campo ha già un valore o se un'altra scheda attiva ha lo stesso (con `--history-letta --apply`) | Dry-run yes; `--apply` no (il campo si riempie una volta) |
| `python3 scripts/patch_remove_edf_duplicates.py ID --keep EDF-NNNN --why …` | Dry-run di default: toglie da una scheda le relazioni `edf_participation` che sono copie identiche (stesso progetto, ruolo e contributo UE) di relazioni di un'altra scheda attiva; si ferma (exit 2) se una non ha copia; le relazioni tolte restano intere nella `history` (con `--history-letta --apply` scrive). Nato dal caso Airbus Defence and Space (2026-11-19). |
| `python3 scripts/add_validation.py ID --status confirmed\|bad_crunchbase_match\|qid_restored --why … [--wikidata-id QNNN]` | Dry-run di default: aggiunge una sola voce di `validation` senza cambiare altri campi; `qid_restored` (2026-11-19) richiede `--wikidata-id` uguale al QID attuale della scheda e chiude un caso del controllo 12 (QID tolto e rimesso, verificato e tenuto); `--history-letta --apply` per scrivere |
| `python3 scripts/add_parte_di.py FIGLIA CAPOGRUPPO …` | Dry-run di default: aggiunge UN legame `parte_di` con `--author` (approvazione) e `--history-letta --apply` (vedi `UPDATE_PROTOCOL.md`, *Group links*) | Dry-run yes; `--apply` no (id nuovo) |
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

### SEC ownership import (B5, Release 1; reference/S3-S7, UPDATE_PROTOCOL.md *SEC relationships*)

| Command | What it does | Safe to re-run? |
|---|---|---|
| `python3 scripts/import_sec_ownership.py [--out DIR]` | Dry-run (default): reads `rawdata/sec-edgar/<release>/`, the reviewed tables in `work/b5-release1/` (`proposta-aziende.csv`, `proposta-classi.csv`, `proposta-gestori.csv`, `proposta-ruoli.csv`) and prints the reconciliation (571 rows = 546 importable + 25 discarded), new `PER-`/`IV-` cards, `ownership` and `role` relationships, changed and vanished rows. Writes only the reports (`--out`, default `work/b5-release1/dry-run/`) | Yes |
| `python3 scripts/import_sec_ownership.py --db COPY.json --out DIR --apply` | Writes into the database file given by `--db`: new cards (first free IDs, alphabetical), `ownership` and `role` relationships, `history[]` for changed values, `current: false` for vanished rows. Stops if a row is blocked, a key is duplicated or `proposta-ruoli.csv` has a row without `revisione_nelson`. **On the real database it needs `--database-reale` (decision of Nelson); always try on a copy outside the repo first** | Yes: the second run changes nothing |
| `python3 work/b5-release1/proponi_ruoli.py --db COPY.json [--riscrivi]` | Proposes `proposta-ruoli.csv` (wording → role codes) for the persons already created; refuses to overwrite a reviewed table without `--riscrivi` | Yes (does not touch the database) |
| `python3 work/b5-release1/verifica_tabelle.py` | Mechanical check of the three matching tables | Yes |

State at 2026-11-17: tried on a clean copy of the database only (150 new cards, 546 `ownership`, 47 `role`), not run on the real one.

### One-time build scripts (do not re-run — they regenerate IDs from scratch)

| Script | Purpose | Status |
|---|---|---|
| `scripts/build_database.py` | Initial iShares ETF import → database.json | Done 2026-04-01 |
| `scripts/build_edf_entities.py` | EDF org import → 792 new entities | Done 2026-04-01 |
| `scripts/import_startups.py` | Migrates 17 startups from old DB | Done 2026-04-01 |
| `scripts/import_by_wikidata.py` | Migrates 107 companies from old DB via QID match | Done 2026-04-01 |

> **Warning:** Re-running any of these scripts will attempt to create duplicate entities. Never re-run without modifying them to skip existing IDs first.

