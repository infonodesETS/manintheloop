#!/usr/bin/env python3
"""
import_ishares_aerospace.py — Import iShares Aerospace & Defense (GICS 201010) ETF holdings.

Input:  rawdata/ishare_aerospace_defense_GICS201010_en.csv  (converted from Italian locale)
Output: data/database.json

For each equity row:
  - If a matching company already exists (by normalized name or MANUAL_ALIASES):
      append a new sources.ishares entry (if this ETF not already recorded)
  - If no match: create a new IN-NNNN entity

Usage:
    python3 scripts/import_ishares_aerospace.py [--dry-run]

Run from the refactoringDB/ root directory.
Validate after running:
    python3 scripts/validate.py
"""

import argparse
import json
import os
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

from parse_ishares import parse_csv, normalize_name

DATABASE_PATH = os.path.join(BASE, "data", "database.json")
CSV_PATH = os.path.join(BASE, "rawdata", "ishare_aerospace_defense_GICS201010_en.csv")

ETF_NAME = "iShares Global Aerospace & Defence UCITS ETF"
ETF_TICKER = "DFND"
GICS_CODE = "201010"
EXTRACTED_AT = "2026-03-30"

TODAY = date.today().isoformat()
SCRIPT = "import_ishares_aerospace.py"

# ── Manual aliases ─────────────────────────────────────────────────────────────
# name_key (from parse_ishares.py normalize_name) → existing entity ID
# Used when the ETF name_key doesn't exactly match the DB entity's normalized name,
# but both refer to the same company.
MANUAL_ALIASES: dict[str, str] = {
    # "THALES SA" normalizes to "THALES SA" but DB has IN-1132 "Thales" → "THALES"
    "THALES SA": "IN-1132",
    # "DASSAULT AVIATION SA" → "DASSAULT AVIATION SA" vs DB "Dassault Aviation" → "DASSAULT AVIATION"
    "DASSAULT AVIATION SA": "IN-1276",
    # "LEONARDO FINMECCANICA" (after stripping SPA) vs DB "Leonardo Societa Per Azioni" → different keys
    "LEONARDO FINMECCANICA": "IN-0841",
    # "SAAB CLASS B" → DB IN-1329 "Saab" (Saab AB parent, Q219501)
    "SAAB CLASS B": "IN-1329",
}


def build_ishares_block(row: dict) -> dict:
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without modifying database.json")
    args = parser.parse_args()
    dry = args.dry_run

    # ── Load DB ────────────────────────────────────────────────────────────────
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    entities = db["entities"]

    # ── Build name_key lookup (company entities only) ─────────────────────────
    db_by_key: dict[str, dict] = {}
    for e in entities:
        if e.get("type") == "company":
            nk = normalize_name(e["name"])
            db_by_key[nk] = e  # last writer wins for true duplicates

    # Also build id → entity index for MANUAL_ALIASES lookups
    db_by_id: dict[str, dict] = {e["id"]: e for e in entities}

    # ── Find max IN-NNNN ID ───────────────────────────────────────────────────
    max_in = max(
        int(e["id"][3:]) for e in entities if e["id"].startswith("IN-")
    )

    # ── Parse ETF CSV ──────────────────────────────────────────────────────────
    rows = parse_csv(
        CSV_PATH,
        etf_name=ETF_NAME,
        etf_ticker=ETF_TICKER,
        gics_code=GICS_CODE,
        extracted_at=EXTRACTED_AT,
    )
    print(f"Parsed {len(rows)} equity rows from {os.path.basename(CSV_PATH)}")

    # ── Dedup within ETF (share classes: same name_key → keep higher weight) ──
    seen: dict[str, dict] = {}
    for row in rows:
        nk = row["name_key"]
        if nk not in seen or (row["weight_pct"] or 0) > (seen[nk]["weight_pct"] or 0):
            seen[nk] = row
    rows = list(seen.values())
    print(f"  After intra-ETF dedup: {len(rows)} rows")

    # ── Match / create ─────────────────────────────────────────────────────────
    stats = {"updated": 0, "created": 0, "skipped": 0}
    new_entities: list[dict] = []

    for row in rows:
        nk = row["name_key"]
        block = build_ishares_block(row)

        # 1. Check manual alias
        entity = None
        if nk in MANUAL_ALIASES:
            alias_id = MANUAL_ALIASES[nk]
            entity = db_by_id.get(alias_id)
            if entity:
                match_method = f"manual_alias→{alias_id}"

        # 2. Check normalized name match
        if entity is None and nk in db_by_key:
            entity = db_by_key[nk]
            match_method = "name_key"

        if entity is not None:
            # ── Update existing entity ─────────────────────────────────────
            src = entity.setdefault("sources", {})
            if src.get("ishares") is None:
                src["ishares"] = []

            existing_etfs = {b["etf_name"] for b in src["ishares"]}
            if ETF_NAME in existing_etfs:
                print(f"  SKIP (already has this ETF): {entity['id']} {entity['name']}")
                stats["skipped"] += 1
                continue

            print(f"  UPDATE ({match_method}): {entity['id']} {entity['name']}")
            if not dry:
                src["ishares"].append(block)
                entity.setdefault("history", []).append({
                    "date": TODAY,
                    "source": "ishares",
                    "author": SCRIPT,
                    "field": "sources.ishares",
                    "old": None,
                    "new": f"{ETF_NAME} ({ETF_TICKER})",
                    "description": (
                        f"Added iShares entry from {ETF_NAME} "
                        f"(GICS {GICS_CODE}, {os.path.basename(CSV_PATH)})"
                    ),
                })
            stats["updated"] += 1

        else:
            # ── Create new entity ──────────────────────────────────────────
            max_in += 1
            new_id = f"IN-{max_in:04d}"
            print(f"  CREATE {new_id}: {row['name']}")
            new_entity = {
                "id": new_id,
                "type": "company",
                "roles": ["manufacturer"],
                "name": row["name"],
                "sector": None,
                "wikidata_id": None,
                "sources": {
                    "ishares": [block],
                    "crunchbase": None,
                    "infonodes": None,
                    "wikidata": None,
                    "edf": None,
                    "edf_project": None,
                },
                "history": [{
                    "date": TODAY,
                    "source": "ishares",
                    "author": SCRIPT,
                    "field": "*",
                    "old": None,
                    "new": None,
                    "description": (
                        f"Initial import from {ETF_NAME} "
                        f"(GICS {GICS_CODE}, {os.path.basename(CSV_PATH)})"
                    ),
                }],
                "validation": [{
                    "status": "needs_review",
                    "description": (
                        "Roles and sector inferred from iShares ETF import only. "
                        "Confirm manufacturer status and enrich with Crunchbase."
                    ),
                    "author": SCRIPT,
                    "datestamp": TODAY,
                }],
                "tags": [],
            }
            new_entities.append(new_entity)
            if not dry:
                entities.append(new_entity)
                db_by_key[nk] = new_entity
                db_by_id[new_id] = new_entity
            stats["created"] += 1

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n{'DRY RUN — ' if dry else ''}Results:")
    print(f"  Updated (existing entities): {stats['updated']}")
    print(f"  Created (new entities):      {stats['created']}")
    print(f"  Skipped (ETF already set):   {stats['skipped']}")

    if new_entities:
        print(f"\nNew entities ({len(new_entities)}):")
        for e in new_entities:
            ishares = e["sources"]["ishares"][0]
            print(f"  {e['id']}  {e['name']:45s}  ({ishares['location']})")

    if dry:
        print("\nDry run — no changes written.")
        return

    # ── Write DB ───────────────────────────────────────────────────────────────
    db["_updated"] = TODAY
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"\nWritten {DATABASE_PATH}")
    print("Next: python3 scripts/validate.py")


if __name__ == "__main__":
    main()
