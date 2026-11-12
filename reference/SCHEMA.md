# Schema v3.0 — database.json

## Overview

`database.json` is a graph-based database integrating iShares ETF holdings (Mining, Tech, Comm Services) with EDF beneficiary data. It follows the same graph structure as the `refactoring/` v2.0 schema, extended with a `person` entity type and an `ishares` source block.

---

## Top-level structure

```json
{
  "_schema": "3.0",
  "_updated": "YYYY-MM-DD",
  "entities": [...],
  "relationships": [...]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `_schema` | string | Schema version |
| `_updated` | string (YYYY-MM-DD) | Date of last update |
| `entities` | array | All nodes (companies + investors + persons) |
| `relationships` | array | All edges (investments, board memberships, etc.) |

---

## Entity

```json
{
  "id": "IN-0001",
  "type": "company",
  "roles": ["manufacturer"],
  "name": "Apple",
  "sector": null,
  "wikidata_id": null,
  "sources": {
    "ishares": [...],
    "crunchbase": null,
    "infonodes": null,
    "wikidata": null
  },
  "history": [...],
  "validation": [],
  "tags": []
}
```

### Required fields

`id`, `name`, `type`, `roles`, `history`

### ID prefixes

| Prefix | Entity class |
|--------|-------------|
| `IN-NNNN` | Companies (manufacturers, tracked entities) |
| `IV-NNNN` | Investor entities (funds, agencies, banks) |
| `PER-NNNN` | Persons (board members, executives) |

IDs are zero-padded to 4 digits and assigned in alphabetical order by name within each class.

### Entity types

| `type` | Description |
|--------|-------------|
| `company` | Manufacturer, startup, tech company, mining company |
| `fund` | VC, PE, family office, CVC, accelerator |
| `government_agency` | EDF, EIB, DARPA, NATO, national agencies |
| `bank` | Commercial/investment banks |
| `institution` | University, think tank, foundation |
| `person` | Individual (board member, executive) |
| `investor` | Investor entity (393 in use at 2026-11-12; `IV-` class) |
| `public_fund` | Public fund (52 in use) |
| `edf_project` | EDF project (`EDF-NNNN`, 129 in use; see `UPDATE_PROTOCOL.md`) |

> The list above is the set accepted by `scripts/validate.py` (check 5). `investor`, `public_fund` and `edf_project` were in use but missing from this table until B1 (2026-11).

### Roles

| `role` | Description |
|--------|-------------|
| `manufacturer` | Entity tracked as a company/producer |
| `investor` | Entity that invests in others |
| `board_member` | Person serving on a board of directors |

An entity can have multiple roles.

> **Not to be confused with** the `role` field of an `edf_participation` relationship (`participant`, `coordinator`, …) and with the relationship type `role` / field `role_code` introduced in B1 (see *Relationships* below).

---

## Sources

### `sources.ishares`

Array — one entry per ETF the entity appears in.

```json
"ishares": [
  {
    "extracted_at": "2026-04-01",
    "etf_name": "iShares MSCI Global Metals & Mining Producers ETF",
    "etf_ticker": "PICK",
    "gics_code": "151040",
    "gics_sector": "Materials",
    "stock_ticker": "BHP",
    "stock_sector": "Materials",
    "weight_pct": 12.25,
    "location": "Australia",
    "exchange": "Asx - All Markets",
    "currency": "USD",
    "source_file": "ishares_metals_mining_gics151040.csv"
  }
]
```

If a company appears in only one ETF, the array has one element. If it appears in multiple ETFs (e.g. a company in both GICS 45 and GICS 50), each appearance is a separate array element.

### `sources.crunchbase`

`null` at initial import. Populated by `scripts/import_crunchbase_csv.py`.

Script-managed — do not edit manually. Re-run the import script to refresh.

```json
{
  "extracted_at": "YYYY-MM-DD",
  "source_file": "crunchbase-export-YYYY-MM-DD.csv",
  "profile_url": "https://www.crunchbase.com/organization/...",
  "stage": "",
  "description": "Short description from Crunchbase",
  "description_full": "Full description (may be null)",
  "website": "https://...",
  "cb_rank": null,
  "headquarters": "City, State, Country",
  "headquarters_regions": "Region1, Region2",
  "operating_status": "Active",
  "founded_date": "YYYY-MM-DD",
  "company_type": "For Profit",
  "investment_stage": null,
  "investor_type": "",
  "primary_industry": "Industry name",
  "primary_industry_url": "https://www.crunchbase.com/...",
  "industry_groups": ["Group1", "Group2"],
  "industries": ["Industry1", "Industry2"],
  "founders": ["Name1", "Name2"],
  "num_funding_rounds": null,
  "funding_status": null,
  "last_funding_date": "YYYY-MM-DD",
  "last_funding_amount_usd": null,
  "last_funding_type": null,
  "total_equity_funding_usd": null,
  "total_funding_usd": null,
  "total_funding_native": {"amount": 0, "currency": "USD"},
  "top_investors": ["Investor1", "Investor2"],
  "num_investors": null,
  "revenue_range": null,
  "patents_granted": null,
  "domain": null,
  "acquired_by": null,
  "acquired_by_url": null,
  "board": []
}
```

| Field | Source | Notes |
|---|---|---|
| `extracted_at` | import script | Date of this import run |
| `source_file` | import script | Filename of the CB export used — provenance |
| `profile_url` | `Organization Name URL` | |
| `stage` | `Stage` | |
| `description` | `Description` | Short |
| `description_full` | `Full Description` | Long form |
| `website` | `Website` | |
| `cb_rank` | `CB Rank (Company)` | int |
| `headquarters` | `Headquarters Location` | City, State, Country |
| `headquarters_regions` | `Headquarters Regions` | |
| `operating_status` | `Operating Status` | |
| `founded_date` | `Founded Date` | YYYY-MM-DD |
| `company_type` | `Company Type` | |
| `investment_stage` | `Investment Stage` | |
| `investor_type` | `Investor Type` | |
| `primary_industry` | `Primary Industry` | |
| `primary_industry_url` | `Primary Industry URL` | |
| `industry_groups` | `Industry Groups` | list |
| `industries` | `Industries` | list |
| `founders` | `Founders` | list |
| `num_funding_rounds` | `Number of Funding Rounds` | int |
| `funding_status` | `Funding Status` | |
| `last_funding_date` | `Last Funding Date` | |
| `last_funding_amount_usd` | `Last Funding Amount (in USD)` | int |
| `last_funding_type` | `Last Funding Type` | |
| `total_equity_funding_usd` | `Total Equity Funding Amount (in USD)` | int |
| `total_funding_usd` | `Total Funding Amount (in USD)` | int |
| `total_funding_native` | `Total Funding Amount` + currency | `{amount, currency}` |
| `top_investors` | `Top 5 Investors` | list |
| `num_investors` | `Number of Investors` | int |
| `revenue_range` | — | Not in bulk export; preserved if set manually |
| `patents_granted` | — | Not in bulk export |
| `domain` | — | Not in bulk export |
| `acquired_by` | — | Not in bulk export |
| `acquired_by_url` | — | Not in bulk export |
| `board` | — | Not in bulk export; populated separately |

### `sources.sec`

Added in B1 (decisions S1, S4, S7 in `reference/S1…S7`). **Reference to the source only**: the data lives in the relationships and in `rawdata/sec-edgar/`, which is never modified. **Addresses never go in the DB** (S4); `validate.py` rejects `indirizzo` / `address` keys inside this block.

```json
"sec": {
  "release": "2026-10-17",
  "refs": [{"file": "detentori-oltre-5.csv", "row": 12}],
  "person_ids": ["P0551"]
}
```

| Field | Notes |
|---|---|
| `release` | Release date of the SEC data set (`rawdata/sec-edgar/<release>/`) |
| `refs` | One entry per source row used to create or update the entity: file and row |
| `person_ids` | `PER-` entities only: the `P####` of Andrea's registry. If two `P####` turn out to be the same person, **both** are kept (S7) |

> The exact field names are a proposal of B1; they are confirmed when `scripts/import_sec_ownership.py` is written (B5). Not otherwise checked by `validate.py`.

### `sources.infonodes`

`null` at initial import.

```json
{
  "extracted_at": "YYYY-MM-DD",
  "sector": "Mining",
  "country": "Australia",
  "tax_id": null,
  "main_focus": null,
  "wikipedia_url": null,
  "website": null
}
```

### `sources.wikidata`

`null` at initial import. Script-managed cache — never edit manually.

---

## History

Append-only log of changes. Every data modification appends one entry.

```json
{
  "date": "2026-04-01",
  "source": "ishares",
  "author": "build_database.py",
  "field": "*",
  "old": null,
  "new": null,
  "description": "Initial import from iShares ETF CSV"
}
```

| Field | Description |
|-------|-------------|
| `date` | YYYY-MM-DD |
| `source` | `"ishares"`, `"crunchbase"`, `"infonodes"`, `"manual"`, `"migration"` (more values exist in practice) |
| `action` | Optional. `"entity_retired"` marks a tombstone: **the site and `build_chat_index.py` hide any entity with a history entry whose `action` is `entity_retired`** (`app.js`, `networks.html`, `key-figures.html`) |
| `author` | Script name or user handle |
| `field` | Field name changed (`"*"` for full record creation/import) |
| `old` | Previous value (null on creation) |
| `new` | New value (null on creation) |
| `description` | Human-readable description |

---

## Validation

```json
{
  "status": "needs_review",
  "description": "roles inferred from iShares ETF only — confirm manufacturer/investor status",
  "author": "build_database.py",
  "datestamp": "2026-04-01"
}
```

| `status` | Meaning |
|----------|---------|
| `needs_review` | Requires manual verification |
| `flagged` | Known issue, correction pending |
| `merged_duplicate` | Entity merged from duplicate rows (legacy; use `merged_from`) |
| `confirmed` | Data point manually verified |

The authoritative list of statuses with their meaning and when to use them is in `reference/UPDATE_PROTOCOL.md` (*Updating an existing entity field*). Statuses found in the database at 2026-11-12 (count of entries): `needs_review` 3331, `wikidata_enriched` 3283, `website_enriched` 1202, `crunchbase_enriched` 960, `reconciliation_documented` 731, `field_conflict` 188, `cb_hq_mismatch_subsidiary` 42, `duplicate_wikidata_id` 40, `qid_nulled_subsidiary` 35, `confirmed` 27, `accepted_duplicate` 22, `field_conflict_resolved` 22, `compatible_sources` 19, `cb_wrong_entity` 18, `expected_iv_in_duplicate` 16, `wikidata_false_positive` 9, `qid_nulled_duplicate` 8, `qid_nulled_sibling_subsidiary` 8, `retired` 5, `wikidata_country_corrected` 4, `resolved` 4, `merged_duplicate` 4, `confirmed_no_entry` 2, `qid_removed` 1, `merged_from` 1, `wikidata_stale` 1, `uncertain_match` 1, `country_confirmed` 1. Documented but never used so far: `share_class_variant` (S3 will use it). Statuses without a definition in `UPDATE_PROTOCOL.md` are listed here for completeness only.

**Tombstones (retired entities).** A retired entity keeps all its content. It has (a) a `history[]` entry with `action: "entity_retired"` (read by the site) and (b) a `validation[]` entry with `status: "retired"` and a pointer to the winner (`canonical` or `merged_into`; `null` if there is none). Never delete the entity.

---

## Relationships

> **Correction (B1, 2026-11-12).** Until now this section described `id`, `sources`, `added_at`, `author` and `details` on every relationship. The 3,490 relationships in the database do not have those fields (no `id`, no `sources`, no `added_at`, no `author`). This section now describes what the data really has, plus the new types.

### Fields in use today (types `investment`, `board_membership`, `edf_participation`)

```json
{ "source": "IV-0336", "target": "IN-0001", "type": "investment",
  "source_ref": "crunchbase_top_investors", "created_at": "2026-04-22" }

{ "source": "IN-0468", "target": "EDF-0001", "type": "edf_participation",
  "role": "coordinator", "eu_contribution": 22975375.01, "created_at": "2026-04-23" }
```

| Field | Present in | Notes |
|---|---|---|
| `source`, `target`, `type` | all | identify the relationship; key `(source, target, type)` is unique (check 2) |
| `created_at` | all | `YYYY-MM-DD`. This is the date field of relationships (there is no `added_at`) |
| `source_ref` | `investment` | provenance label (`crunchbase_top_investors` 1,083, `legacy_db_migration` 94) |
| `details` | 94 `investment` | free object, only `lead` is used |
| `role` | `edf_participation` | `participant`, `thirdParty`, `coordinator`, `associatedPartner` |
| `eu_contribution` | `edf_participation` | number |
| `history` | 1 relationship | `[{date, author, description}]` (poorer than the form below; tolerated on old relationships) |

These relationships have **no `id`**. Do not assume `REL-NNNN` exists for them.

### Relationship types

| `type` | source → target | Description |
|--------|-----------------|-------------|
| `investment` | IV-* → IN-* | Investor holds stake in company (Crunchbase / legacy) |
| `board_membership` | PER-* → IN-* | Person on board of company (kept for compatibility; not used in the data yet) |
| `edf_participation` | IN-* → EDF-* | Company participated in EDF project |
| `ownership` | IV-* / IN-* / PER-* → IN-* | **New (S2).** Stake of ≥5% of capital or of votes (threshold S4) |
| `role` | PER-* → IN-* | **New (S2, S7).** A role of a person in a company; Release 2 |
| `parte_di` | IV-*/IN-* → IV-*/IN-* | **New (S6).** Group link: the source is part of the target. Added only after a person has checked it; always with `source_ref` |

### New types: `ownership`, `role`, `parte_di`

These carry their **own `id`** (`REL-NNNN`, four digits or more, unique) and are checked by `validate.py` check 11. Older relationships are not changed and get no `id`.

```json
{
  "id": "REL-3491", "type": "ownership",
  "source": "IV-0077", "target": "IN-0034",
  "classe": "Class A", "holder_type": "fund",
  "pct": 7.0, "pct_voti": null, "shares": null,
  "filing_date": "2025-10-17", "as_of": "2025-10-17", "as_of_origine": "deposito",
  "release": "2026-10-17", "current": true,
  "source_ref": "2026-10-17/detentori-oltre-5.csv#12",
  "created_at": "2026-11-20",
  "history": []
}
```

**Common fields** (all three types): `id`, `type`, `source`, `target`, `source_ref` (non-empty), `created_at`, optional `current` (boolean), optional `history`.

**`ownership`** (S3, S4, S5):

| Field | Rule |
|---|---|
| `classe` | required, non-empty string, as written in the filing (S3 R2). Part of the key |
| `holder_type` | `fund`, `company` or `person` (S2; to be confirmed at the first import) |
| `pct`, `pct_voti`, `shares` | number or `null`; `pct` and `pct_voti` between 0 and 100; at least one of the three is not `null`. An empty percentage in the SEC file means "below 1%", **not zero** (S4) |
| `filing_date`, `as_of`, `release` | `YYYY-MM-DD` or `null` |
| `as_of_origine` | `proxy`, `testo` or `deposito`; required when `as_of` is set (S5) |
| `current` | `true` while the row is in the latest imported release; `false` when it disappears (never delete, S5) |

Unique key: `(source, target, type, classe)`.

**`role`** (S7; imported with Release 2): `role_code` (controlled vocabulary, defined by the mapping table before Release 2; today only checked as non-empty) and `role_text` (original wording of the filing, unchanged). A string with several roles becomes **several relationships**, all with the same `role_text`. Unique key: `(source, target, type, role_code)`. `role_code` is deliberately not called `role`, to avoid confusion with the `role` of `edf_participation`.

**`parte_di`** (S6): group link between two entities already in the database. `validate.py` checks the shape; that a person has verified the link is a process rule recorded in `source_ref`.

**`history[]` of the new types** (S5, append-only): each entry has `date`, `release`, `source_ref`, `field`, `old`, `new`. Old values are never lost.

## Person entity

```json
{
  "id": "PER-0001",
  "type": "person",
  "roles": ["board_member"],
  "name": "Nome Cognome",
  "sector": null,
  "wikidata_id": null,
  "sources": {
    "crunchbase": null,
    "infonodes": null,
    "wikidata": null
  },
  "history": [...],
  "validation": [],
  "tags": []
}
```

Note: `sources.ishares` is not applicable to `person` entities. IDs are `PER-NNNN`, four digits or more (S1): the permanent ID is assigned once; the `P####` of the SEC release is kept only as a source reference in `sources.sec.person_ids`.

---

## Date format

All date fields use **ISO 8601**: `YYYY-MM-DD`.

## Null conventions

- Empty string `""` → `null` for optional fields
- `0` is a valid integer
- `null` means unknown/not available
- `[]` is a valid empty array (never `null` for arrays)
