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
   | `merged_from` | Set on the **winner** entity: records which loser ID was absorbed (set by `dedup_entities.py`) |
   | `merged_duplicate` | Legacy alias for `merged_from` — do not use for new merges |
   | `reconciliation_documented` | Cross-dataset match basis documented (set by `audit_quality.py` Audit B) |
   | `field_conflict` | Field value differs across sources — manual review required (set by `audit_quality.py` Audit C) |
   | `duplicate_wikidata_id` | Two or more entities share the same `wikidata_id` — set by `audit_quality.py` Audit D; resolved by merge, `share_class_variant`, or `qid_removed` |
   | `share_class_variant` | Entity is an intentional separate listing of the same company (different share class, exchange, or depositary receipt); `duplicate_wikidata_id` expected and correct |
   | `qid_removed` | A previously assigned `wikidata_id` was removed because it belonged to a different entity (parent, sibling subsidiary, or mismatched CB profile); entry must state the old QID, its Wikidata label, and the reason for removal |
   | `bad_crunchbase_match` | `sources.crunchbase` block contains data from a wrong Crunchbase match; block should be removed and re-matched in a future Crunchbase cycle |

   > **Rule:** `history[]` is the granular provenance trail (one entry per field per change). `validation[]` is the entity-level enrichment ledger (one entry per enrichment pass per entity). Both are append-only.

5. Bump `_updated`. Run `validate.py` before committing.

---

## Safe script execution (dry-run protocol)

### Scripts with built-in `--dry-run` (preferred)

The following scripts support `--dry-run` and should always be previewed that way first:

| Script | Dry-run flag | Notes |
|---|---|---|
| `enrich_wikidata.py` | `--dry-run` | Fetches from Wikidata, prints what would be written |
| `import_edf_websites.py` | `--dry-run` | Prints website assignments without writing |
| `fetch_wikidata_websites.py` | `--dry-run` | Prints P856 lookups without writing |
| `audit_quality.py` | `--dry-run` | Prints audit report without writing |
| `dedup_entities.py --merge` | `--dry-run` | Previews merge result (absorbed fields, redirected rels) without writing |
| `import_crunchbase_csv.py` | `--dry-run` | Prints field-level diff without writing |

Workflow for `--dry-run` scripts:
1. Run with `--dry-run`, review output.
2. If output looks correct, run without the flag.
3. Run `validate.py`, then commit.

### Scripts without `--dry-run` (manual backup required)

For scripts that do not support `--dry-run`:

1. **Backup** before running:
   ```bash
   cp data/database.json data/database.json.bak
   ```
2. **Run** the script.
3. **Restore**, compare, then re-run after review:
   ```bash
   cp data/database.json.bak data/database.json
   ```
4. Run `validate.py`, then commit.
5. **Remove** the backup:
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

**Wikidata enrichment:**
```
data: enrich wikidata — sources.wikidata populated for N entities (YYYY-MM-DD)

Script: scripts/enrich_wikidata.py [--force]
Validation: all checks passed.
```

**Field correction:**
```
data: correct <field> — IN-XXXX <company> (YYYY-MM-DD)

<what was wrong, what source confirmed the correction>
```

**Entity deduplication (merge):**
```
data: merge duplicate — IN-XXXX ← IN-YYYY (<winner name> ← <loser name>) (YYYY-MM-DD)

Reason: <why they are the same entity>
Absorbed: <what data moved from loser to winner>
Validation: all checks passed.
```

**Entity deduplication (QID removal):**
```
data: remove wrong QID — IN-XXXX <entity name> (YYYY-MM-DD)

Old QID: QNNNNNN (<Wikidata label>)
Reason: <why the QID was wrong>
Validation: all checks passed.
```

---

## Merging a duplicate entity

Use `scripts/dedup_entities.py`, which handles all merge mechanics automatically.

### Choosing winner vs loser

**Do not use the lower ID as the rule.** The winner is the entity with the higher data-richness score (computed by `dedup_entities.py --list`): more source blocks, Crunchbase data, Wikidata data, history entries, and relationships each add weight. Run `--list` to see scores before deciding.

Tiebreakers (in order):
1. Higher relationship count (`rels=`)
2. More source blocks present
3. Entity that came from the primary enrichment pipeline (not a bare iShares ticker entry)

### Decision types

Before merging, classify the duplicate pair:

| Type | Action | Tool |
|---|---|---|
| Same legal entity, name alias (ticker, old name, legal suffix) | `--merge WINNER LOSER` | `dedup_entities.py` |
| Share class / different exchange listing (A/B shares, GDR, A-share/H-share) | Set `share_class_variant` on both; remove `duplicate_wikidata_id` | manual patch |
| Subsidiary or division with parent's QID | Set `wikidata_id = null` on subsidiary; add `qid_removed` validation | manual patch |

### Procedure

```bash
# 1. List all duplicate QID groups (safe, read-only)
python3 scripts/dedup_entities.py --list

# 2. Preview a specific merge (safe, no writes)
python3 scripts/dedup_entities.py --merge WINNER_ID LOSER_ID --dry-run

# 3. Apply
python3 scripts/dedup_entities.py --merge WINNER_ID LOSER_ID

# 4. Validate
python3 scripts/validate.py
```

After applying a merge, add a `dedup_decision` history entry on the winner explaining **why** the pair was identified as the same entity (name pattern, Wikidata label match, iShares ticker-as-name, etc.). The script's auto-generated history entry records *what* was absorbed; the manual annotation records *why* the decision was made.

For `qid_removed` actions (subsidiaries with wrong parent QID), the `wikidata_id` history entry must state:
- The old QID and its Wikidata label
- Why the entity got it (CB name-match propagation, QID pipeline false positive, etc.)
- What the entity actually is (national subsidiary, product division, etc.)
- Whether a correct QID may exist (run QID pipeline to find it)

---

## ID retirement

Retired IDs must be documented below.

### Retired IDs

Retired IDs are loser entities from merges. Their data was fully absorbed into the winner.

| Retired ID | Merged into | Loser name | Winner name | Reason | Date |
|---|---|---|---|---|---|
| IN-0366 | IN-0365 | Telecom Italia S.p.a | Telecom Italia | Identical name, same legal entity | 2026-04-01 |
| IN-0473 | IN-0472 | Airbus Operations (duplicate) | Airbus Operations | Identical name, same legal entity | 2026-04-01 |
| IN-0502 | IN-0501 | Arianegroup (duplicate) | Arianegroup | Identical name, same legal entity | 2026-04-01 |
| IN-0784 | IN-0783 | Integrasys (duplicate) | Integrasys | Identical name, same legal entity | 2026-04-01 |
| IN-1168 | IN-1167 | United Monolithic Semiconductors (duplicate) | United Monolithic Semiconductors | Identical name, same legal entity | 2026-04-01 |
| IN-0062 | IN-1294 | Business Machines | IBM | "International Business Machines" = IBM; different iShares entry point | 2026-04-15 |
| IN-0401 | IN-1344 | VALE DO RIO DOCE | Vale | Former full legal name pre-2009 rebrand | 2026-04-15 |
| IN-0133 | IN-1282 | Fortescue | Fortescue Metals Group | Same company, abbreviated entry | 2026-04-15 |
| IN-0035 | IN-1253 | Arafura RARE Earths | Arafura Resources | Company rebranded 2022 | 2026-04-15 |
| IN-0282 | IN-1318 | Palantir Technologies Class A | Palantir Technologies | "Class A" = iShares naming artifact; only one public share class | 2026-04-15 |
| IN-0242 | IN-1311 | MP Materials Class A | MP Materials | "Class A" = iShares naming artifact | 2026-04-15 |
| IN-1014 | IN-1329 | Saab Aktiebolag | Saab | "Aktiebolag" = Swedish for "company" (legal suffix) | 2026-04-15 |
| IN-1118 | IN-1241 | Tekever Uas | TEKEVER | UAS division registered under parent name; same QID confirmed same entity | 2026-04-15 |
| IN-0897 | IN-1312 | Nammo Raufoss As | Nammo | Raufoss = factory town; same legal entity | 2026-04-15 |
| IN-0151 | IN-1286 | Grupo Mexico B | Grupo Mexico | B-share iShares entry merged into primary entity | 2026-04-15 |
| IN-0287 | IN-1320 | PLS | Pilbara Minerals | PLS = ASX ticker for Pilbara Minerals | 2026-04-15 |
| IN-1247 | IN-0017 | Alphabet | Alphabet Class A | Generic EDF entity merged into canonical Class A listing | 2026-04-15 |
| IN-0228 | IN-1310 | META Platforms Class A | Meta for Developers | Only one public Meta share class; "Class A" = iShares artifact | 2026-04-15 |
| IN-1335 | IN-1150 | ThyssenKrupp Marine Systems | Tkms | TKMS = acronym for ThyssenKrupp Marine Systems; same entity | 2026-04-15 |
| IN-0753 | IN-1298 | Indra Sistemas | Indra | Same legal entity (Indra Sistemas S.A.) with two separate EDF PICs | 2026-04-15 |
| IV-0043 | IN-0032 | Apple | Apple | Dual-role entity: same company appears as iShares holding (IN-) and CB investor (IV-); name-based merge | 2026-04-15 |
| IV-0445 | IN-0233 | Microsoft | Microsoft | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0466 | IN-0271 | NVIDIA | Nvidia | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0575 | IN-0312 | Samsung Electronics | Samsung Electronics | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0602 | IN-0339 | SoftBank | Softbank | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0608 | IN-0341 | South32 | South32 | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0647 | IN-0375 | Tencent | Tencent | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0701 | IN-0409 | Vodafone | Vodafone | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0374 | IN-0812 | Kaitseministeerium | Kaitseministeerium | Dual-role entity (government agency + investor): name-based merge | 2026-04-15 |
| IV-0025 | IN-1245 | Agnico-Eagle Mines Limited | Agnico-Eagle Mines Limited | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0036 | IN-1248 | Amazon | Amazon | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0439 | IN-1307 | Ma'aden | Ma'aden | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0658 | IN-1336 | Tianqi Lithium | Tianqi Lithium | Dual-role entity: name-based merge | 2026-04-15 |
| IV-0718 | IN-1350 | Zijin Mining | Zijin Mining | Dual-role entity: name-based merge | 2026-04-15 |
