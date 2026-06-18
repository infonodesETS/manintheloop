#!/usr/bin/env python3
"""
import_mintl_companies.py — Import MINTL company list from Crunchbase CSV export.

Reads:  rawdata/mintl-update-companies-20260618-foglio1-csv6-18-2026.csv
        data/database.json
Writes: data/database.json (+N new IN-NNNN entities)

Usage:
    python3 scripts/import_mintl_companies.py [--dry-run]

IDs assigned alphabetically by name within this batch, starting from max(IN-*)+1.
"""

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "database.json"
CSV_PATH = ROOT / "rawdata" / "mintl-update-companies-20260618-foglio1-csv6-18-2026.csv"
SOURCE_FILE = CSV_PATH.name
TODAY = date.today().isoformat()

# Entities already confirmed in DB — skip, do not create duplicates
# Key: exact Organization Name from CSV  |  Value: existing DB id
ALREADY_IN_DB = {
    "Taiwan Semiconductor Manufacturing Company": "IN-0356",  # name: "Taiwan Semiconductor Manufacturing"
    "Intelic": "IN-1236",
}

# False-positive substring matches found during pre-import search (documented here for the record):
#   "xAI"   → matched IN-0672/0673/1401 "Exail*"        — different company, xAI is NEW
#   "Scale"  → matched IV-0489 "Scale Venture Partners",
#               IV-0490 "Scale-Up Ventures",
#               IN-1406 "Astroscale"                     — all different, Scale AI is NEW


def parse_int(s):
    if not s or not s.strip():
        return None
    try:
        return int(s.replace(",", "").replace(" ", ""))
    except ValueError:
        return None


def parse_list(s):
    if not s or not s.strip():
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def extract_domain(website):
    if not website:
        return None
    m = re.match(r"https?://(?:www\.)?([^/]+)", website)
    return m.group(1) if m else None


def infer_type(name):
    if name == "State Street":
        return "bank"
    return "company"


def infer_sector(funding_status):
    if funding_status in ("Early Stage Venture", "Late Stage Venture", "Seed"):
        return "Startup"
    return None


def build_cb_block(row):
    website = row.get("Website", "").strip() or None
    tf_amount = parse_int(row.get("Total Funding Amount", ""))
    tf_currency = row.get("Total Funding Amount Currency", "USD").strip() or "USD"

    return {
        "extracted_at": TODAY,
        "source_file": SOURCE_FILE,
        "profile_url": row.get("Organization Name URL", "").strip() or None,
        "stage": row.get("Stage", "").strip() or None,
        "description": row.get("Description", "").strip() or None,
        "description_full": row.get("Full Description", "").strip() or None,
        "website": website,
        "cb_rank": parse_int(row.get("CB Rank (Company)", "")),
        "headquarters": row.get("Headquarters Location", "").strip() or None,
        "headquarters_regions": row.get("Headquarters Regions", "").strip() or None,
        "operating_status": row.get("Operating Status", "").strip() or None,
        "founded_date": row.get("Founded Date", "").strip() or None,
        "company_type": row.get("Company Type", "").strip() or None,
        "investment_stage": row.get("Investment Stage", "").strip() or None,
        "investor_type": row.get("Investor Type", "").strip() or None,
        "primary_industry": row.get("Primary Industry", "").strip() or None,
        "primary_industry_url": row.get("Primary Industry URL", "").strip() or None,
        "industry_groups": parse_list(row.get("Industry Groups", "")),
        "industries": parse_list(row.get("Industries", "")),
        "founders": parse_list(row.get("Founders", "")),
        "num_funding_rounds": parse_int(row.get("Number of Funding Rounds", "")),
        "funding_status": row.get("Funding Status", "").strip() or None,
        "last_funding_date": row.get("Last Funding Date", "").strip() or None,
        "last_funding_amount_usd": parse_int(row.get("Last Funding Amount (in USD)", "")),
        "last_funding_type": row.get("Last Funding Type", "").strip() or None,
        "total_equity_funding_usd": parse_int(row.get("Total Equity Funding Amount (in USD)", "")),
        "total_funding_usd": parse_int(row.get("Total Funding Amount (in USD)", "")),
        "total_funding_native": {"amount": tf_amount, "currency": tf_currency},
        "top_investors": parse_list(row.get("Top 5 Investors", "")),
        "num_investors": parse_int(row.get("Number of Investors", "")),
        "revenue_range": row.get("Estimated Revenue Range", "").strip() or None,
        "patents_granted": None,
        "domain": extract_domain(website),
        "acquired_by": None,
        "acquired_by_url": None,
        "board": [],
    }


def build_entity(entity_id, name, row):
    funding_status = row.get("Funding Status", "").strip()
    return {
        "id": entity_id,
        "type": infer_type(name),
        "roles": ["manufacturer"],
        "name": name,
        "sector": infer_sector(funding_status),
        "wikidata_id": None,
        "sources": {
            "ishares": None,
            "crunchbase": build_cb_block(row),
            "infonodes": None,
            "wikidata": None,
        },
        "tags": [],
        "history": [
            {
                "date": TODAY,
                "source": "crunchbase",
                "author": "import_mintl_companies.py",
                "field": "*",
                "old": None,
                "new": None,
                "description": f"New entity created from MINTL CB export ({SOURCE_FILE})",
            }
        ],
        "validation": [
            {
                "status": "needs_review",
                "description": "Entity created from MINTL Crunchbase CSV export — type, roles, and sector require human review",
                "author": "import_mintl_companies.py",
                "datestamp": TODAY,
            }
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing")
    args = parser.parse_args()

    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)

    max_in = max(int(e["id"][3:]) for e in db["entities"] if e["id"].startswith("IN-"))
    next_id = max_in + 1

    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Assign IDs alphabetically by name
    rows.sort(key=lambda r: r["Organization Name"].strip().lower())

    new_entities = []
    skipped_present = []
    imported_names = []

    for row in rows:
        name = row["Organization Name"].strip()

        if name in ALREADY_IN_DB:
            skipped_present.append((name, ALREADY_IN_DB[name]))
            continue

        entity_id = f"IN-{next_id:04d}"
        entity = build_entity(entity_id, name, row)
        new_entities.append(entity)
        imported_names.append((entity_id, name))
        next_id += 1

    # Report
    print(f"CSV rows read:           {len(rows)}")
    print(f"Already in DB (skipped): {len(skipped_present)}")
    for name, eid in skipped_present:
        print(f"  {eid}  {name}")
    print(f"New entities to create:  {len(new_entities)}")
    for eid, name in imported_names:
        print(f"  {'[DRY] ' if args.dry_run else ''}{eid}  {name}")

    if args.dry_run:
        print("\nDry-run: no changes written.")
        return

    db["entities"].extend(new_entities)
    db["_updated"] = TODAY

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(new_entities)} new entities. DB total: {len(db['entities'])} entities.")


if __name__ == "__main__":
    main()
