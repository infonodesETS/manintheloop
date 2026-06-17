# Man in the Loop — info.nodes experiments

A collection of data tools for mapping defense-tech ecosystems, built with open web standards.

- **[Startup Map](crunchbase_scraping/test_startup/)** — Investment matrix & network graph for 18 EU/NATO defense-tech startups
- **[Investment Map](crunchbase_full/)** — Full investment matrix for 150+ defense & critical-resources companies
- **[Wikidata Inspector](wikidata_inspector/)** — Browse and inspect company data via the Wikidata knowledge graph
- **[EU Call Checker](call-checker_infonodes/)** — Search EU funding calls across years via the EC Participant Portal API

---

## Data Structure

Both maps are powered by two JSON files that act as the single source of truth. Data is versioned by extraction date and source, allowing multiple snapshots per company to coexist and accumulate over time.

### `crunchbase_full/investments.json`

Master data file for the Investment Map. Contains **165 companies** across Mining, Tech, Defence, and Startup sectors.

**Stats (as of 2026-03-07):**

| Snapshot | Count |
|---|---|
| Total companies | 165 |
| With Crunchbase data (`20260307`) | 151 |
| With infonodes team data (`20260307_infonodes`) | 164 |
| With both sources | 150 |
| infonodes-only (no Crunchbase yet) | 14 |
| Flagged for review (`validation_status`) | 4 |

**Top-level structure:**

```json
{
  "Company Name": {
    "<YYYYMMDD>": { ... },
    "<YYYYMMDD>_infonodes": { ... },
    "validation_status": [ ... ]
  }
}
```

Each company key maps to an object with one or more **dated snapshots** plus an optional `validation_status` array.

---

**Snapshot: `<YYYYMMDD>` — Crunchbase extraction**

```json
"20260307": {
  "extracting-source": "crunchbase",
  "Organization Name URL": "https://www.crunchbase.com/organization/helsing",
  "Stage": "",
  "Industries": "Artificial Intelligence (AI), Drones, Military, Software",
  "Headquarters Location": "Munich, Bayern, Germany",
  "Description": "Short description from Crunchbase.",
  "CB Rank (Company)": "252",
  "Estimated Revenue Range": "$1B to $10B",
  "Website": "https://www.helsing.ai",
  "Investor Type": "",
  "Top 5 Investors": "General Catalyst, Lightspeed Venture Partners, Accel, ...",
  "Lead Investors": "General Catalyst, Prima Materia",
  "Total Funding Amount": "1361500000",
  "Total Funding Amount Currency": "EUR",
  "Total Funding Amount (in USD)": "1519386783",
  "Founders": "Gundbert Scherf, Niklas Köhler, Torsten Reil",
  "Primary Industry": "Military",
  "Primary Industry URL": "https://www.crunchbase.com/category/military",
  "Industry Groups": "Artificial Intelligence (AI), Government and Military, ..."
}
```

---

**Snapshot: `<YYYYMMDD>_infonodes` — infonodes team extraction**

```json
"20260307_infonodes": {
  "extracting-source": "infonodes_team",
  "extracting-date": "20260307",
  "sector": "Startup",
  "country": "Germany",
  "tax_id": "DE456662688 (VAT)",
  "main_focus": "Development of autonomous military systems and AI for defense.",
  "wikidata_id": "",
  "wikipedia_url": "https://en.wikipedia.org/wiki/Helsing_(company)",
  "wikidata_url": ""
}
```

---

**`validation_status` — audit trail**

An array of validation entries, one per review event. Grows over time; the most recent entry reflects the current status.

```json
"validation_status": [
  {
    "status": "merged_duplicate",
    "author": "claude-sonnet-4-6",
    "validation_description": "Two source rows merged into one entry. Manual review needed.",
    "datestamp": "20260307"
  },
  {
    "status": "validated",
    "author": "human-reviewer",
    "validation_description": "Confirmed correct after checking legal entity registry.",
    "datestamp": "20260310"
  }
]
```

Possible `status` values:

| Value | Meaning |
|---|---|
| `validated` | Confirmed correct by a reviewer |
| `needs_review` | Flagged, review pending |
| `merged_duplicate` | Two or more source rows collapsed into one entry |
| `uncertain_match` | Source name differs from JSON key; may be a different legal entity |
| `flagged` | Generic flag for any other data quality issue |

Currently flagged companies:

| Company | Status | Issue |
|---|---|---|
| `Glencore` | `merged_duplicate` | Appears as both Mining and Tech in source sheet; Wikidata ID in Tech row is misassigned (points to Nvidia) |
| `Rio Tinto` | `merged_duplicate` | "Rio Tinto Lithium" row merged into parent entry; may warrant a separate business-unit entry |
| `NeoPerformance` | `merged_duplicate` | Two rows (Neodimio + Gallium focus) merged; `sector` field retains only the first row's value |
| `Patricomp Oy` | `uncertain_match` | Source sheet lists "Patria Group" (parent); Patricomp Oy is a subsidiary — possibly distinct entities |

---

### `crunchbase_scraping/test_startup/startups.json`

Data file for the Startup Map. Contains **18 EU/NATO defense-tech startups**, enriched from Crunchbase and manual research.

**Top-level structure:**

```json
{
  "Company Name": {
    "<YYYYMMDD>": { ... }
  }
}
```

**Snapshot fields:**

```json
"20260307": {
  "extracting-source": "crunchbase",
  "loc": "Munich, DE",
  "ind": "AI · Drones · Military",
  "investors": [
    { "name": "General Catalyst", "is_lead": true },
    { "name": "Accel", "is_lead": false }
  ],
  "cb_url": "https://www.crunchbase.com/organization/helsing",
  "stage": "",
  "industries_full": "Artificial Intelligence (AI), Drones, Military, Software",
  "hq_full": "Munich, Bayern, Germany",
  "description": "Short description.",
  "description_full": "Extended description.",
  "website": "https://www.helsing.ai",
  "founders": "Gundbert Scherf, Niklas Köhler, Torsten Reil",
  "acquired_by": "",
  "acquired_by_url": "",
  "patents_granted": "36",
  "domain": "helsing.ai"
}
```

Key difference from `investments.json`: the `investors` field is a structured array (one object per investor with an `is_lead` flag), making it directly consumable by the investment matrix and network graph without further parsing.

---

## Metadata

| Field | Value |
|---|---|
| Last updated | 2026-03-07 |
| Primary sources | Crunchbase, infonodes team research, Wikidata |
| External sheet | [Google Sheets source](https://docs.google.com/spreadsheets/d/e/2PACX-1vSg4v9OkP8ZAmUQ_AOukHt8-_jjoiZR62_aeIvay9SqLv6GVxgnZbzT9hckXN0lq8WyHcxZ3smmGvsI/pub?gid=766453961&single=true&output=csv) |
| Companies tracked | 165 (investments) + 18 (startups) |
| Sectors | Mining, Tech, Defence, Startup |
| Data model | `company → date_snapshot → fields` |
| Validation model | `company → validation_status → [{ status, author, description, datestamp }]` |

---

Built with the assistance of [Claude](https://claude.ai) / [Anthropic](https://www.anthropic.com).
GitHub: [infonodesETS/manintheloop](https://github.com/infonodesETS/manintheloop)
