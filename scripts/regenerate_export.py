#!/usr/bin/env python3
"""
regenerate_export.py — Regenerate data/crunchbase_sandbox/companies_export.csv from database.json.

Run at the start of each Crunchbase upload cycle to ensure the export reflects the latest DB state
(new entities added, websites updated, etc.).

Output: data/crunchbase_sandbox/companies_export.csv
  Columns: name, website
  Rows: all company entities, sorted alphabetically by name
  Website priority: sources.crunchbase.website > sources.infonodes.website

After running this script, manually split into matches/non_matches as needed before uploading.

Usage:
  python3 scripts/regenerate_export.py
"""

import csv
import json
import os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
OUTPUT_PATH = os.path.join(BASE, "data", "crunchbase_sandbox", "companies_export.csv")


def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    rows = []
    for e in db["entities"]:
        if e.get("type") != "company":
            continue
        src = e.get("sources") or {}
        website = (
            (src.get("crunchbase") or {}).get("website")
            or (src.get("infonodes") or {}).get("website")
            or ""
        )
        rows.append({"name": e["name"], "website": website})

    rows.sort(key=lambda r: r["name"])

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "website"])
        w.writeheader()
        w.writerows(rows)

    with_website = sum(1 for r in rows if r["website"])
    print(f"Written {len(rows)} rows → {OUTPUT_PATH}")
    print(f"  With website:    {with_website} ({with_website / len(rows) * 100:.1f}%)")
    print(f"  Without website: {len(rows) - with_website}")
    print(f"\nNext: upload data/crunchbase_sandbox/companies_export.csv to Crunchbase bulk enrichment.")


if __name__ == "__main__":
    main()
