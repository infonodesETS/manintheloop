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

### Roles

| `role` | Description |
|--------|-------------|
| `manufacturer` | Entity tracked as a company/producer |
| `investor` | Entity that invests in others |
| `board_member` | Person serving on a board of directors |

An entity can have multiple roles.

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
| `source` | `"ishares"`, `"crunchbase"`, `"infonodes"`, `"manual"`, `"migration"` |
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
| `merged_duplicate` | Entity merged from duplicate rows |
| `confirmed` | Data point manually verified |

---

## Relationship

```json
{
  "id": "REL-0001",
  "type": "investment",
  "source": "IV-0001",
  "target": "IN-0001",
  "details": { "lead": true },
  "sources": ["crunchbase"],
  "added_at": "2026-04-01",
  "author": "nelsonmau"
}
```

### Relationship types

| `type` | source → target | Description |
|--------|-----------------|-------------|
| `investment` | IV-* → IN-* | Investor holds stake in company |
| `board_membership` | PER-* → IN-* | Person on board of company |
| `edf_participation` | IN-* → (edf project ref) | Company participated in EDF project |

---

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

Note: `sources.ishares` is not applicable to `person` entities.

---

## Date format

All date fields use **ISO 8601**: `YYYY-MM-DD`.

## Null conventions

- Empty string `""` → `null` for optional fields
- `0` is a valid integer
- `null` means unknown/not available
- `[]` is a valid empty array (never `null` for arrays)
