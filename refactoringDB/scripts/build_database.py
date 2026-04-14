#!/usr/bin/env python3
"""
build_database.py — Build database.json (schema v3.0) from iShares ETF CSV holdings.

Reads the 3 iShares CSVs from rawdata/, deduplicates by normalized company name,
assigns IN-NNNN IDs in alphabetical order, and writes data/database.json.

Usage:
    python3 scripts/build_database.py

Run from the refactoringDB/ root directory.
"""

import json
import os
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAWDATA_DIR = os.path.join(BASE, "rawdata")
OUTPUT_PATH = os.path.join(BASE, "data", "database.json")

TODAY = date.today().isoformat()

# Add scripts/ to path so we can import parse_ishares
sys.path.insert(0, os.path.join(BASE, "scripts"))
from parse_ishares import parse_csv

# ── ETF definitions ───────────────────────────────────────────────────────────

ETF_CONFIGS = [
    {
        "filepath": os.path.join(RAWDATA_DIR, "ishares_metals_mining_gics151040.csv"),
        "etf_name": "iShares MSCI Global Metals & Mining Producers ETF",
        "etf_ticker": "PICK",
        "gics_code": "151040",
    },
    {
        "filepath": os.path.join(RAWDATA_DIR, "ishares_tech_gics45.csv"),
        "etf_name": "iShares Global Tech ETF",
        "etf_ticker": "IXN",
        "gics_code": "45",
    },
    {
        "filepath": os.path.join(RAWDATA_DIR, "ishares_comm_services_gics50.csv"),
        "etf_name": "iShares Global Comm Services ETF",
        "etf_ticker": "IXP",
        "gics_code": "50",
    },
]


def build_ishares_block(row: dict) -> dict:
    """Build a sources.ishares entry from a parsed CSV row."""
    return {
        "extracted_at": row["extracted_at"],
        "etf_name": row["etf_name"],
        "etf_ticker": row["etf_ticker"],
        "gics_code": row["gics_code"],
        "stock_ticker": row["stock_ticker"],
        "stock_sector": row["stock_sector"],
        "weight_pct": row["weight_pct"],
        "location": row["location"],
        "exchange": row["exchange"],
        "currency": row["currency"],
        "source_file": row["source_file"],
    }


def build_history_entry(row: dict) -> dict:
    """Build the initial history entry for a new entity."""
    return {
        "date": TODAY,
        "source": "ishares",
        "author": "build_database.py",
        "field": "*",
        "old": None,
        "new": None,
        "description": (
            f"Initial import from {row['etf_name']} "
            f"(GICS {row['gics_code']}, {row['source_file']})"
        ),
    }


def main():
    # ── Step 1: Parse all ETF CSVs ────────────────────────────────────────────
    print("Parsing iShares ETF CSVs...")
    all_rows: list[dict] = []
    for cfg in ETF_CONFIGS:
        if not os.path.exists(cfg["filepath"]):
            print(f"  ERROR: missing file {cfg['filepath']}")
            sys.exit(1)
        rows = parse_csv(
            cfg["filepath"],
            etf_name=cfg["etf_name"],
            etf_ticker=cfg["etf_ticker"],
            gics_code=cfg["gics_code"],
            extracted_at=TODAY,
        )
        print(f"  {cfg['etf_name']}: {len(rows)} equity rows")
        all_rows.extend(rows)

    print(f"  Total rows before deduplication: {len(all_rows)}")

    # ── Step 2: Deduplicate by normalized name ────────────────────────────────
    # Strategy:
    # - Key: name_key (normalized name, stripped of legal suffixes)
    # - Same key appearing in multiple ETFs → one entity, multiple ishares entries
    # - Same key appearing twice in the same ETF (dual-listed, e.g. RIO TINTO PLC/LTD)
    #   → one entity, keep the entry with higher weight_pct
    # - When consolidating, use the display name from the highest-weight row
    #
    # Data structure: name_key → {
    #   "name": str,           # display name from highest-weight row
    #   "ishares": list[dict], # one entry per unique ETF appearance
    #   "first_row": dict,     # the canonical row (highest weight, for history)
    # }

    entities_by_key: dict[str, dict] = {}

    for row in all_rows:
        key = row["name_key"]
        etf = row["etf_name"]
        weight = row["weight_pct"] or 0.0

        if key not in entities_by_key:
            entities_by_key[key] = {
                "name": row["name"],
                "ishares": [build_ishares_block(row)],
                "first_row": row,
            }
        else:
            existing = entities_by_key[key]
            # Check if this ETF is already recorded for this entity
            existing_etfs = {b["etf_name"] for b in existing["ishares"]}

            if etf not in existing_etfs:
                # New ETF appearance → add to ishares list
                existing["ishares"].append(build_ishares_block(row))
            else:
                # Same ETF again (dual-listed stock): keep higher weight entry
                for i, block in enumerate(existing["ishares"]):
                    if block["etf_name"] == etf:
                        if weight > (block["weight_pct"] or 0.0):
                            existing["ishares"][i] = build_ishares_block(row)
                        break

            # Update canonical name/row if this row has higher weight
            current_weight = existing["first_row"]["weight_pct"] or 0.0
            if weight > current_weight:
                existing["name"] = row["name"]
                existing["first_row"] = row

    print(f"  Unique entities after deduplication: {len(entities_by_key)}")

    # ── Step 3: Sort alphabetically and assign IN-NNNN IDs ───────────────────
    sorted_keys = sorted(entities_by_key.keys())

    print(f"\nBuilding entities...")
    entities = []
    for i, key in enumerate(sorted_keys, start=1):
        data = entities_by_key[key]
        in_id = f"IN-{i:04d}"
        first_row = data["first_row"]

        entity = {
            "id": in_id,
            "type": "company",
            "roles": ["manufacturer"],
            "name": data["name"],
            "sector": None,
            "wikidata_id": None,
            "sources": {
                "ishares": data["ishares"],
                "crunchbase": None,
                "infonodes": None,
                "wikidata": None,
            },
            "history": [build_history_entry(first_row)],
            "validation": [
                {
                    "status": "needs_review",
                    "description": (
                        "Roles and sector inferred from iShares ETF import only. "
                        "Confirm manufacturer/investor status and enrich with Crunchbase."
                    ),
                    "author": "build_database.py",
                    "datestamp": TODAY,
                }
            ],
            "tags": [],
        }
        entities.append(entity)

    # ── Step 4: Write database.json ───────────────────────────────────────────
    database = {
        "_schema": "3.0",
        "_updated": TODAY,
        "entities": entities,
        "relationships": [],
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

    # ── Step 5: Summary ───────────────────────────────────────────────────────
    gics_counts: dict[str, int] = {}
    for data in entities_by_key.values():
        for block in data["ishares"]:
            g = block["gics_code"]
            gics_counts[g] = gics_counts.get(g, 0) + 1

    multi_etf = sum(1 for d in entities_by_key.values() if len(d["ishares"]) > 1)

    print(f"\n✓ Build complete.")
    print(f"  Total entities:  {len(entities)}")
    print(f"  Multi-ETF:       {multi_etf} (appear in >1 ETF)")
    print(f"  ETF breakdown (ishares entries by GICS code):")
    for g, count in sorted(gics_counts.items()):
        label = {
            "151040": "Mining (151040)",
            "45":     "Tech (45)",
            "50":     "Comm Services (50)",
        }.get(g, g)
        print(f"    {label}: {count}")
    print(f"  Relationships:   0 (populated in Phase 2)")
    print(f"  Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
