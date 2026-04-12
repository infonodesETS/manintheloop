# Update Protocol — database.json Reconciliation

## Purpose

This document defines the rules for updating `database.json` when new data is available, without corrupting existing IDs, history, or validation entries.

---

## Guiding principles

1. **IDs are permanent.** Once assigned, `IN-NNNN`, `IV-NNNN`, `PER-NNNN`, and `REL-NNNN` IDs must never be reused or reassigned.
2. **History is append-only.** Never delete existing history entries. Modification of an existing entry is only permitted to add missing provenance. No information may be removed.
3. **Validation survives updates.** Existing `validation[]` entries are preserved; new ones may be appended.
4. **IDs are assigned alphabetically.** New entities get the next available sequential ID in their class.
5. **Full provenance is required.** Every history entry must be traceable back to its raw source. Specify the raw source file, the exact field/value, and — when correcting — both the original entry and the evidence used.
6. **`sources.wikidata` is script-managed.** Never manually edit it; edits will be silently lost on the next `enrich_wikidata.py` run.
7. **Every data change must produce a dedicated git commit.** A commit modifying `database.json` must be atomic (one logical change), include a descriptive message naming affected entities, and pass `validate.py` before pushing.

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
4. Add a `needs_review` validation entry.
5. Bump `_updated` at the top level to today's date.
6. Run `validate.py` before committing.

---

## Adding a new investor (IV entity)

Same as adding a company, but use the next `IV-NNNN` ID and set `roles: ["investor"]`.

> **Deduplication:** Before adding, search existing investor entities case-insensitively. If a match exists, use the existing ID — never create a duplicate.

---

## Adding a new person (PER entity)

1. Choose the next unused `PER-NNNN` ID.
2. Create the entity with required fields. Set `type: "person"`, `roles: ["board_member"]`.
3. Add a history entry:
   ```json
   {
     "date": "YYYY-MM-DD",
     "source": "crunchbase",
     "author": "your-handle",
     "field": "*",
     "old": null,
     "new": null,
     "description": "Person added: board member of <company> per Crunchbase"
   }
   ```
4. Create a `board_membership` relationship:
   ```json
   {
     "id": "REL-NNNN",
     "type": "board_membership",
     "source": "PER-NNNN",
     "target": "IN-NNNN",
     "details": { "role": "Board Member" },
     "sources": ["crunchbase"],
     "added_at": "YYYY-MM-DD",
     "author": "your-handle"
   }
   ```
5. Bump `_updated`. Run `validate.py` before committing.

> **Deduplication:** Before adding, search existing PER entities. Same person at multiple companies → one PER entity, multiple REL entries.

---

## Updating an existing entity field

1. Locate the entity by `id`.
2. Update the field value.
3. **Append to `history[]`** (mandatory for every field change):
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
4. **Append to `validation[]`** when the update is part of an enrichment pass (mandatory):
   ```json
   {
     "status": "<enrichment_type>",
     "description": "<what was enriched and from which source>",
     "author": "<script-name or your-handle>",
     "datestamp": "YYYY-MM-DD"
   }
   ```
   Use the following `status` values:

   | Status | When to use |
   |---|---|
   | `needs_review` | Initial import — entity added but not yet verified |
   | `website_enriched` | `sources.infonodes.website` added from EDF, Wikidata P856, or web research |
   | `crunchbase_enriched` | Crunchbase CSV import applied to this entity |
   | `wikidata_enriched` | Wikidata QID or `sources.wikidata` block written |
   | `confirmed` | Human review confirmed a specific field (e.g., QID, merge) |
   | `merged_duplicate` | Duplicate entity merged into this canonical entity |

   > **Rule:** `history[]` is the granular provenance trail (one entry per field per change). `validation[]` is the entity-level enrichment ledger (one entry per enrichment pass per entity). Both are append-only.

5. Bump `_updated`. Run `validate.py` before committing.

---

## Safe script execution (dry-run protocol)

Any script that modifies `database.json` in-place should be previewed before committing.

1. **Backup** before running:
   ```bash
   cp data/database.json data/database.json.bak
   ```
2. **Run** the script.
3. **Compare** before/after with a Python diff.
4. **Restore** immediately after inspection:
   ```bash
   cp data/database.json.bak data/database.json
   ```
5. **Review** the extracted changes. Flag anything requiring human judgment.
6. **Re-run**, then validate and commit.
7. **Remove** the backup:
   ```bash
   rm data/database.json.bak
   ```

> `data/database.json.bak` must never be committed.

---

## Running validate.py

```bash
python3 scripts/validate.py
```

All checks must pass before any commit that modifies `database.json`.

---

## Commit message formats

**iShares import:**
```
data: import ishares <ETF> — <N> entities added (YYYY-MM-DD)

Script: scripts/build_database.py
Validation: all checks passed.
```

**Crunchbase enrichment:**
```
data: enrich crunchbase — IN-XXXX..IN-YYYY updated (YYYY-MM-DD)

<brief description of changes>

Script: manual / scripts/enrich_crunchbase.py
Validation: all checks passed.
```

**Board member addition:**
```
data: add board members — <company> PER-XXXX..PER-YYYY (YYYY-MM-DD)

Script: manual
Validation: all checks passed.
```

**Field correction:**
```
data: correct <field> — IN-XXXX <company> (YYYY-MM-DD)

<what was wrong, what source confirmed the correction>
```

---

## Merging a duplicate entity

1. Choose the **lower ID** as canonical.
2. Merge all sources, history (sorted by date), and validation from the duplicate.
3. Update all relationships referencing the duplicate ID.
4. Add a history entry on the canonical entity documenting the merge.
5. **Delete** the duplicate entity.
6. Add a `merged_duplicate` validation entry.
7. Bump `_updated`. Run `validate.py`.

---

## ID retirement

Retired IDs must be documented below.

### Retired IDs

| ID | Type | Reason | Date |
|---|---|---|---|
| _(none yet)_ | | | |
