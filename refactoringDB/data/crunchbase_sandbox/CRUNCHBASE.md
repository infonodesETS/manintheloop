# Crunchbase Enrichment — Process & Reconciliation Log

> **Resumption document.** Read this before touching any file in this folder.
> Last updated: 2026-04-13

---

## Context

We are building a single graph database (`data/database.json`) by integrating data from
multiple heterogeneous sources (iShares ETFs, EDF beneficiaries, old manual DB, Wikidata,
Crunchbase). There are **no universal unique identifiers** across these sources. Every
reconciliation step carries a risk of false matches, silent overwrites, and data drift.

This document records:
- What has been done in each Crunchbase cycle
- Which entities were matched, how, and with what confidence
- Which entities remain unresolved, and why
- The process to follow in future cycles

---

## Files in this directory

| File | Description |
|---|---|
| `companies_export.csv` | Full export from DB (1149 companies, name + website). Regenerate with `scripts/regenerate_export.py` before each new cycle. |
| `matches.csv` | 812 rows uploaded to Crunchbase bulk enrichment (cycle 1, 2026-04-13). Subset of companies_export.csv with a known website. |
| `non_matches.csv` | 337 rows excluded from upload (combined from two non-matches files from Crunchbase). These are companies Crunchbase could not find at all. |
| `import_report_YYYY-MM-DD.json` | Auto-generated per import run. Contains match stats, tier breakdown, and full unresolved list. |
| `unresolved_YYYY-MM-DD.csv` | CB rows returned but not matched to any DB entity. Review manually before each import. |
| `CRUNCHBASE.md` | This file. |

> Raw Crunchbase exports should be saved here with the filename pattern:
> `crunchbase-export-<label>-MM-DD-YYYY.csv`

---

## The enrichment cycle

This process is designed to be re-run. Each cycle refreshes `sources.crunchbase` for all
matched entities, records what changed, and updates the audit trail.

### Step 1 — Regenerate the export

```bash
python3 scripts/regenerate_export.py
# Writes: data/crunchbase_sandbox/companies_export.csv
# 1149 rows (all companies), sorted alphabetically
# Website priority: sources.crunchbase.website > sources.infonodes.website
```

### Step 2 — Build the upload set

The full export contains 1149 rows. Crunchbase bulk enrichment works best with websites.
Split into upload candidates and exclusions manually, or reuse the existing `non_matches.csv`.

```bash
# If reusing previous non_matches.csv (recommended for re-runs):
python3 -c "
import csv
non = {r['name'] for r in csv.DictReader(open('data/crunchbase_sandbox/non_matches.csv'))}
rows = [r for r in csv.DictReader(open('data/crunchbase_sandbox/companies_export.csv')) if r['name'] not in non]
w = csv.DictWriter(open('data/crunchbase_sandbox/matches.csv','w',newline=''), fieldnames=['name','website'])
w.writeheader(); w.writerows(rows)
print(len(rows), 'rows written')
"
```

### Step 3 — Upload to Crunchbase

1. Go to Crunchbase bulk enrichment tool
2. Upload `data/crunchbase_sandbox/matches.csv`
3. Wait for processing
4. Download enriched CSV
5. Save to `data/crunchbase_sandbox/crunchbase-export-<label>-MM-DD-YYYY.csv`

### Step 4 — Import into database.json

```bash
# Preview first — always
python3 scripts/import_crunchbase_csv.py \
    data/crunchbase_sandbox/crunchbase-export-<label>-MM-DD-YYYY.csv \
    --dry-run

# Review the output and unresolved_YYYY-MM-DD.csv
# Then apply:
python3 scripts/import_crunchbase_csv.py \
    data/crunchbase_sandbox/crunchbase-export-<label>-MM-DD-YYYY.csv

# Validate
python3 scripts/validate.py

# Commit
git add data/database.json data/crunchbase_sandbox/
git commit -m "data: enrich crunchbase — N entities updated (YYYY-MM-DD)"
```

---

## Reconciliation strategy

### The problem

There are no shared IDs between our DB and Crunchbase. Our entity names come from three
different sources (iShares CSVs, EDF calls, old manual DB), each with its own naming
conventions. Crunchbase returns its own canonical names.

**Example of the name drift problem:**
- We have: `"Renk"` → CB uploaded: `"Renk"` → CB returned: `"RENK Group"`
- We have: `"Xinjiang Xinxin Mining Industry LT"` (truncated at 34 chars in iShares CSV)
  → CB returned: `"Xinjiang Xinxin Mining Industry"`

### Matching tiers (in order)

The import script (`scripts/import_crunchbase_csv.py`) tries four tiers:

| Tier | Method | Risk |
|---|---|---|
| 1. Exact name | `Organization Name == entity.name` | Low — but misses CB canonical renames |
| 2. Website | Normalised URL comparison (https, no www., no trailing slash) | Low-medium — subsidiary sites can share parent URL |
| 3. Normalised name | Strip legal suffixes (SA, AS, Ltd, …), lowercase | Medium — common words may produce false positives |
| 4. Prefix match | One normalised name starts with the other (min 6 chars) | Medium — e.g. "RENK Group" → "Renk"; "Phaxiam" → "Phaxiam Therapeutics" |

**Preserved fields**: `board`, `patents_granted`, `domain`, `acquired_by`, `acquired_by_url`,
`revenue_range` are **never overwritten** by the import script. If previously set manually,
they carry forward silently.

### Re-run behaviour

On re-run, the script:
- Computes a field-level diff between old and new `sources.crunchbase`
- Entities with zero changes are skipped (no history noise)
- Changed entities get a new `history[]` entry listing exactly which fields changed
- Every import adds a `validation[status: "crunchbase_enriched"]` entry with the source filename

This means: at any future date, you can open any entity in `database.json` and trace
exactly which Crunchbase export populated or changed each field.

---

## Cycle 1 — 2026-04-13

### Input

| | |
|---|---|
| Uploaded | `matches.csv` (812 rows) |
| Crunchbase returned | `crunchbase-export-matches-csv-4-13-2026.csv` (724 rows) |
| Match rate | 724 / 812 = 89.2% |

### Match results (dry-run)

| Tier | Count |
|---|---|
| Exact name | 401 |
| Website | 200 |
| Normalised name | 54 |
| Prefix | 48 |
| **Total matched** | **703 / 724 (97.1%)** |
| Unresolved | **21** |

### Status

> **Complete** — real import run 2026-04-14. 601 new + 121 updated = **722 entities** processed; 731 total with `sources.crunchbase` (includes prior manual imports).
> `validate.py` PASSED after import.

---

## Unresolved entities — Cycle 1 (21 rows)

These 21 rows were returned by Crunchbase but could not be matched to any DB entity
through any of the 4 tiers. Review before importing.

### Category A — Linkable but name too short/different for automatic matching (manual fix needed)

These are almost certainly the right companies. Either the name is too short for the
prefix matcher (< 6 chars) or the canonical name diverged too much.

| CB name | CB website | Likely DB entity | Action |
|---|---|---|---|
| `RENK Group` | renk.com | `Renk` / `Renk Magnet Motor` (IN-0979, IN-0980) | Manually accept or add alias |
| `Tilde` | tilde.com | `Tilde Sia` (IN-1149) — but tilde.com ≠ tilde.lv | Verify website first |
| `JX` | jx-nmm.com | `JX Advanced Metals` (IN-0192) | Name too short (2 chars) |
| `JENA` | jena.so | `Jena Optronik` (IN-0805) — but jena.so ≠ jena-optronik.de | Verify: different entity? |
| `Skyld` | skyld.io | `Skyld Security And Defence` (IN-1068) | |
| `Belss` | belss.lv | `Belss Sia` (IN-0524) — belss.lv vs belss.lv/en/ | URL normalisation edge case |
| `cyex` | cyex.io | `Cyex Korlatolt Felelossegu Tarsasag` (IN-0597) | Name too short |
| `GMV` | gmvsyncromatics.com | `Gmv Innovating Solutions` (IN-0710) or `Gmv Aerospace` (IN-0709) | gmvsyncromatics.com ≠ gmv.es |
| `tns` | tns.co | `Tns Mars` (IN-1153) | Name too short (3 chars) |
| `Adyta` | adyta.pt | `Adyta Lda` (IN-0443) | adyta.pt ≠ adyta.pt/en |
| `Mews` | mews.com | `Mews France` (IN-0868) or `Mews Labs` — different subentity | Clarify which entity |

### Category B — Wrong CB match (CB matched a different company than intended)

These require investigation. Do not auto-import.

| CB name | CB website | Issue |
|---|---|---|
| `Sage` | sagehealth.com | CB matched a US health company. Our entity is `THE SAGE` (IN-0378), a UK software company. Wrong match. |
| `Nucoro` | nucoro.com | CB matched a fintech startup. Our entity is `Nucor` (IN-0270), a US steel manufacturer. Wrong match. |
| `Sia` | sia.tech | Too generic. `Sia` is a blockchain storage project; our `Sia Dati` (IN-1051) is an Italian IT company. Wrong match. |

### Category C — Genuinely not in DB or CB matched a subsidiary/parent

CB matched these from our input but returned an entity we don't have, or a
related-but-different entity (subsidiary, parent, regional division).

| CB name | CB website | Notes |
|---|---|---|
| `Nanshan Aluminum` | nanshanalu.com | We have `Shandong Nanshan Aluminium A` (IN-0328) — related but CB returned a different entity |
| `John Cockerill Hydrogen` | hydrogen.johncockerill.com | We have `John Cockerill Defense` (IN-0808) — CB matched a different division |
| `AES Embedded Solutions` | aes-connect.com | Not in DB |
| `GKN Aerospace` | gknaerospace.com | We have `Gkn Fokker Aerospace` (IN-0707) — CB returned parent GKN Aerospace instead |
| `Pegasus Development` | pegasusbuild.com | Not in DB — CB mismatch |
| `Thames Cryogenics` | thamescryogenics.com | Not in DB |
| `Integrated Technology Services` | its-egy.com | Not in DB |

---

## Known risks and decisions

| Risk | Decision |
|---|---|
| CB returns canonical name, not our name | 4-tier matching covers most cases. Tier 4 (prefix) is most aggressive — review prefix matches carefully. |
| Same Crunchbase profile matched to multiple DB entities (share classes) | Accepted. All matched entities receive the same CB data. Documented in `history[]`. |
| CB website differs from our DB website | Both are stored separately (`sources.crunchbase.website` vs `sources.infonodes.website`). No overwrite. |
| Re-run overwrites valid manual edits to `sources.crunchbase` | Preserved fields (`board`, `domain`, etc.) are never overwritten. Other fields are always refreshed from the latest CB export — this is intentional. |
| CB bulk enrichment sometimes returns a parent company instead of the subsidiary we have | Must be caught during human review of `unresolved_YYYY-MM-DD.csv` before each import. |
