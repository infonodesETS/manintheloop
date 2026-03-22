# Schema v2.0 — database.json

## Overview

`database.json` is a graph-based unified database combining data from Crunchbase scrapes and manual infonodes team enrichment. It replaces the legacy `investments.json` flat format.

---

## Top-level structure

```json
{
  "_schema": "2.0",
  "_updated": "YYYY-MM-DD",
  "entities": [...],
  "relationships": [...]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `_schema` | string | Schema version |
| `_updated` | string (YYYY-MM-DD) | Date of last full migration or batch update |
| `entities` | array | All nodes in the graph (companies + investors) |
| `relationships` | array | All edges (investments, funding rounds, etc.) |

---

## Entity

```json
{
  "id": "IN-0001",
  "type": "company",
  "roles": ["manufacturer"],
  "name": "Helsing",
  "sector": "Startup",
  "wikidata_id": "Q...",
  "sources": {
    "crunchbase": { ... },
    "infonodes": { ... },
    "wikidata": null
  },
  "history": [ ... ],
  "validation": [ ... ],
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

IDs are zero-padded to 4 digits and assigned in alphabetical order within each class.

### Entity types

| `type` | Description |
|--------|-------------|
| `company` | Manufacturer, startup, tech company, mining company, defence prime |
| `fund` | VC, PE, family office, CVC, accelerator |
| `government_agency` | DARPA, EIB, ARPA-E, EDF, DoD, KfW, NATO, ESA, development banks |
| `bank` | Commercial/investment banks (Deutsche Bank, Goldman Sachs, BNP, etc.) |
| `institution` | University, think tank, sovereign wealth fund, foundation |

### Roles

| `role` | Description |
|--------|-------------|
| `manufacturer` | Entity tracked as a company/producer |
| `investor` | Entity that invests in others |

An entity can have multiple roles (e.g. `["manufacturer", "investor"]` for a CVC-backed company).

---

## Sources

### `sources.crunchbase`

```json
{
  "extracted_at": "2026-03-07",
  "profile_url": "https://www.crunchbase.com/organization/helsing",
  "stage": "",
  "description": "...",
  "description_full": "...",
  "headquarters": "Munich, Bayern, Germany",
  "website": "https://www.helsing.ai",
  "cb_rank": 252,
  "revenue_range": "$1B to $10B",
  "total_funding_usd": 1519386783,
  "total_funding_native": { "amount": 1361500000, "currency": "EUR" },
  "founders": ["Gundbert Scherf", "Niklas Köhler", "Torsten Reil"],
  "industries": ["Artificial Intelligence (AI)", "Military"],
  "industry_groups": ["Government and Military", "AI"],
  "primary_industry": "Military",
  "primary_industry_url": "https://www.crunchbase.com/category/military",
  "investor_type": "",
  "patents_granted": 36,
  "domain": "helsing.ai",
  "acquired_by": null,
  "acquired_by_url": null
}
```

### `sources.infonodes`

```json
{
  "extracted_at": "2026-03-07",
  "sector": "Startup",
  "country": "Germany",
  "tax_id": "DE456662688 (VAT)",
  "main_focus": "...",
  "wikipedia_url": "https://en.wikipedia.org/wiki/Helsing_(company)"
}
```

### `sources.wikidata`

`null` at migration time. To be populated via Wikidata reconciliation.

---

## History

Append-only log of changes to the entity.

```json
{
  "date": "2026-03-14",
  "source": "migration",
  "author": "migrate.py",
  "field": "*",
  "old": null,
  "new": null,
  "description": "Initial migration from investments.json v1"
}
```

| Field | Description |
|-------|-------------|
| `date` | YYYY-MM-DD |
| `source` | `"migration"`, `"crunchbase"`, `"infonodes"`, `"manual"` |
| `author` | Script name or user handle |
| `field` | Field name changed (`"*"` for full record creation) |
| `old` | Previous value (null on creation) |
| `new` | New value (null on creation) |
| `description` | Human-readable description |

---

## Validation

Array of validation/flag entries for data quality tracking.

```json
{
  "status": "flagged",
  "description": "wikidata_id was Q2283 (Microsoft), reset to null — needs correct ID",
  "author": "migrate.py",
  "datestamp": "2026-03-14"
}
```

| `status` | Meaning |
|----------|---------|
| `needs_review` | Requires manual verification |
| `flagged` | Known error, corrected but needs confirmation |
| `merged_duplicate` | Entity was merged from duplicate source rows |
| `confirmed` | Data point has been manually verified |

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
  "added_at": "2026-03-14",
  "author": "migrate.py"
}
```

| Field | Description |
|-------|-------------|
| `id` | `REL-NNNN`, zero-padded 4 digits |
| `type` | `"investment"` (only type at v2.0) |
| `source` | IV-ID of the investor entity |
| `target` | IN-ID of the company entity |
| `details.lead` | `true` if lead investor for this round |
| `sources` | Where relationship was extracted from |
| `added_at` | YYYY-MM-DD |
| `author` | Script name or user handle |

---

## Date format

All date fields use **ISO 8601**: `YYYY-MM-DD`.

## Null conventions

- Empty string `""` → `null` for optional fields
- `0` is a valid integer (e.g. `patents_granted: 0`)
- `null` means unknown/not available
