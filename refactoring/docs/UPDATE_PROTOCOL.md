# Update Protocol — database.json Reconciliation

## Purpose

This document defines the rules for updating `database.json` when new data is available from Crunchbase or the infonodes team, without corrupting existing IDs, history, or validation entries.

---

## Guiding principles

1. **IDs are permanent.** Once assigned, `IN-NNNN`, `IV-NNNN`, and `REL-NNNN` IDs must never be reused or reassigned.
2. **History is append-only.** Never delete existing history entries. Modification of an existing entry is only permitted to **add missing provenance** to auto-generated descriptions (e.g. vague migrate.py entries like "Extracted from investor strings during migration") — in this case the description may be expanded with raw source details. No information may be removed.
3. **Validation survives updates.** Existing `validation[]` entries are preserved; new ones may be appended.
4. **IDs are assigned alphabetically.** New entities get the next available sequential ID in their class.
5. **Full provenance is required.** Every history entry must be traceable back to its raw source. This means:
   - Specify the **raw source file** (e.g. `CSV`, `investments.json`, `Wikidata API`)
   - Specify the **exact row/field/value** that originated the data (e.g. `CSV row 'Hensoldt', field 'Top 5 Investors', value 'Leonardo Company'`)
   - When data is corrected or merged, reference both the **original raw entry** and the **evidence used** to confirm the change (e.g. Wikidata URL, Playwright search result)
   - Users must be able to reconstruct the full data lineage from raw source to current state by reading the history.

---

## Adding a new company (IN entity)

1. Choose the next unused `IN-NNNN` ID (check max existing + 1).
2. Create the entity with all required fields (`id`, `name`, `type`, `roles`, `history`).
3. Add a history entry:
   ```json
   {
     "date": "YYYY-MM-DD",
     "source": "manual",
     "author": "your-handle",
     "field": "*",
     "old": null,
     "new": null,
     "description": "New company added: <reason>"
   }
   ```
4. Add a `needs_review` validation entry for roles (until confirmed).
5. Bump `_updated` at the top level of `database.json` to today's date.
6. Run `validate.py` before committing.

---

## Adding a new investor (IV entity)

Same as adding a company, but use the next `IV-NNNN` ID and set `roles: ["investor"]`.

> **Deduplication:** Before adding, search existing investor entities case-insensitively. If a match exists, use the existing ID — never create a duplicate.

Bump `_updated` at the top level of `database.json` to today's date before committing.

---

## Updating an existing entity field

1. Locate the entity by `id`.
2. Update the field value.
3. Append to `history[]`:
   ```json
   {
     "date": "YYYY-MM-DD",
     "source": "crunchbase",
     "author": "your-handle",
     "field": "sources.crunchbase.total_funding_usd",
     "old": 1000000,
     "new": 2000000,
     "description": "Funding updated from new Crunchbase scrape"
   }
   ```
4. If the field was flagged in `validation[]`, update its status to `confirmed` or add a new entry explaining resolution.
5. **Bump `_updated`** at the top level of `database.json` to today's date (`YYYY-MM-DD`). This applies to every change — field updates, merges, removals, normalisation passes.
6. Run `validate.py` before committing.

---

## Batch Crunchbase re-scrape reconciliation

When a new full scrape is available (new date key in legacy format), follow these steps:

1. **Identify changed fields** by diffing old vs. new snapshot per company.
2. **For each changed field:**
   - Update the value in `sources.crunchbase`
   - Update `sources.crunchbase.extracted_at` to the new scrape date
   - Append a history entry per changed field (or one entry with `field: "*"` if many fields changed)
3. **For new investors** found in the scrape:
   - Check for deduplication (case-insensitive name match)
   - Add new IV entities and REL entries as needed
4. **Do not delete** existing relationships — only add or update `details.lead`.
5. Update `_updated` at the top level to today's date.
6. Run `validate.py` before committing.

---

## Resolving a validation flag

1. Find the entity with `validation[].status == "flagged"` or `"needs_review"`.
2. Correct the field (e.g. set the right `wikidata_id`).
3. Append to `history[]` documenting the correction.
4. Change the validation entry's `status` to `"confirmed"` and add a `datestamp`.
5. Bump `_updated` at the top level of `database.json` to today's date.
6. Run `validate.py` before committing.

Example — correcting a bad `wikidata_id`:
```json
{
  "status": "confirmed",
  "description": "wikidata_id corrected to Q1002897 (verified against Wikidata)",
  "author": "your-handle",
  "datestamp": "2026-03-20"
}
```

---

## Merging a duplicate entity

If the same real-world entity exists under two IDs:

1. Choose the **lower ID** as canonical.
2. Merge all sources, history (sorted by date), and validation from the duplicate into canonical.
3. Update all relationships referencing the duplicate ID to use the canonical ID.
4. Add a history entry on the canonical entity:
   ```json
   {
     "date": "YYYY-MM-DD",
     "source": "manual",
     "author": "your-handle",
     "field": "*",
     "old": null,
     "new": null,
     "description": "Merged duplicate entity <duplicate-id> into this record"
   }
   ```
5. **Delete** the duplicate entity from `entities[]` (IDs are never reused, so the deleted ID is permanently retired).
6. Add a `merged_duplicate` validation entry.
7. Bump `_updated` at the top level of `database.json` to today's date.
8. Run `validate.py`.

---

## Removing a spurious relationship

A relationship is spurious if it has no backing in any recognised source (CSV, Crunchbase scrape, or manual infonodes entry). Spurious relationships may only be deleted after cross-checking against the raw source.

1. **Verify** the relationship is absent from all known sources (CSV Top 5, Lead Investors, manual additions).
2. **Delete** the `REL-NNNN` entry from `relationships[]`.
3. **Retire the ID** — add it to the "Retired IDs" section at the bottom of this file with the reason.
4. **Document** the removal in the target entity's `history[]`:
   ```json
   {
     "date": "YYYY-MM-DD",
     "source": "manual",
     "author": "your-handle",
     "field": "relationships",
     "old": "REL-NNNN",
     "new": null,
     "description": "Removed spurious relationship: <investor> not found in any source"
   }
   ```
5. Bump `_updated` at the top level of `database.json` to today's date.
6. Run `validate.py` before committing.

---

## Running validate.py

```bash
python3 refactoring/scripts/validate.py
```

All 8 checks must pass before any commit that modifies `database.json`.

---

## ID retirement

Retired IDs (merged duplicates, deleted test entries) must be documented in a comment block at the bottom of this file:

### Retired IDs

| ID | Type | Reason | Date |
|---|---|---|---|
| REL-0009 | relationship | Spurious — HTGF -> Alpine Eagle not in any source | 2026-03-28 |
| REL-0017 | relationship | Spurious — Amazon -> Amazon self-reference created during migration | 2026-03-28 |
| REL-0094 | relationship | Spurious — Entropy Industrial Capital -> Delian Alliance Industries not in any source | 2026-03-28 |
| REL-0134 | relationship | Spurious — European Investment Fund -> ICEYE not in any source | 2026-03-28 |
| IV-0010 | entity | Merged into IN-0010 (Amazon) — duplicate created by migrate.py from investor strings | 2026-03-28 |
| IV-0031 | entity | Merged into IN-0029 (BHP) — duplicate created by migrate.py from investor strings | 2026-03-28 |
| IV-0151 | entity | Merged into IN-0098 (Ma'aden) — duplicate created by migrate.py from investor strings | 2026-03-28 |
| IV-0153 | entity | Merged into IN-0102 (Microsoft) — duplicate created by migrate.py from investor strings | 2026-03-28 |
| IV-0221 | entity | Merged into IN-0149 (Tianqi Lithium) — duplicate created by migrate.py from investor strings | 2026-03-28 |
| IV-0143 | entity | Merged into IN-0094 (Leonardo) — 'Leonardo Company' confirmed same entity via Playwright Wikidata search (Q910379) | 2026-03-28 |
| IV-0053 | entity | Merged into IV-0052 (Citi) — 'Citibank' same entity; both had wikidata_id Q857063, confirmed via Playwright | 2026-03-28 |
| IV-0118 | entity | Merged into IV-0117 (HTGF) — 'HTGF (High-Tech Gruenderfonds)' full-name form of same fund; both had wikidata_id Q1617690 | 2026-03-28 |
| IV-0122 | entity | Parse error — 'Inc' was suffix of 'General American Investors Company,Inc' split on comma by migrate.py | 2026-03-28 |
| REL-0067 | relationship | Parse error — spurious rel from IV-0122 ('Inc') -> Broadcom; REL-0066 already correctly represents this | 2026-03-28 |
