#!/usr/bin/env python3
"""
import_by_wikidata.py — Import companies from refactoring/data/database.json
that have a wikidata_id but are not yet in the new database.json.

Matching logic (in priority order):
  1. wikidata_id match against existing new DB entities → skip (already present)
  2. normalized name match → skip (already present under different form)
  3. No match → create new IN-NNNN entity

Only imports entities of type "company" that have a wikidata_id.
Entities without wikidata_id are intentionally excluded (see docs/UPDATE_PROTOCOL.md).

Usage:
    python3 scripts/import_by_wikidata.py [--dry-run]

Run from the refactoringDB/ root directory.
"""

import json
import os
import re
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_DB_PATH = os.path.join(BASE, "..", "refactoring", "data", "database.json")
DATABASE_PATH = os.path.join(BASE, "data", "database.json")

TODAY = date.today().isoformat()


def normalize_name(raw: str) -> str:
    s = raw.upper().strip()
    for pattern in [
        r"\bCORPORATION\b", r"\bCORPORATE\b", r"\bCORP\b",
        r"\bLIMITED\b", r"\bLTD\b", r"\bINCORPORATED\b", r"\bINC\b",
        r"\bPLC\b", r"\bAG\b", r"\bSE\b", r"\bGMBH\b",
        r"\bGROUP\b", r"\bHOLDINGS?\b", r"\bSPA\b", r"\bS\.P\.A\.\b",
        r"\bNV\b", r"\bN\.V\.\b", r"\bSA\b", r"\bS\.A\.\b",
        r"\bASA\b", r"\bOYJ\b", r"\bAB\b",
        r"\bINTERNATIONAL\b", r"\bINTL\b",
        r"\bMINES?\b", r"\bMINING\b", r"\bRESOURCES?\b",
        r"\bINDUSTRIES\b", r"\bINDUSTRY\b",
        r"\bTECHNOLOGIES\b", r"\bTECHNOLOGY\b", r"\bSYSTEMS\b",
        r"\bSOCIETA PER AZIONI\b", r"\bSOCIETE ANONYME\b",
    ]:
        s = re.sub(pattern, "", s)
    return re.sub(r"\s+", " ", s).strip()


def main(dry_run: bool = False):
    print("Loading old database.json...")
    with open(OLD_DB_PATH, encoding="utf-8") as f:
        old_db = json.load(f)

    # Only companies with a wikidata_id
    candidates = [
        e for e in old_db["entities"]
        if e.get("type") == "company" and e.get("wikidata_id")
    ]
    print(f"  Companies con wikidata_id nel vecchio DB: {len(candidates)}")

    print("\nLoading new database.json...")
    with open(DATABASE_PATH, encoding="utf-8") as f:
        new_db = json.load(f)

    new_entities: list[dict] = new_db["entities"]

    # Build lookup indexes
    new_by_wikidata = {
        e["wikidata_id"]: e["id"]
        for e in new_entities if e.get("wikidata_id")
    }
    new_by_name = {normalize_name(e["name"]): e["id"] for e in new_entities}

    max_in = max(int(e["id"][3:]) for e in new_entities if e["id"].startswith("IN-"))
    next_in = max_in + 1

    skipped_wikidata = []   # already in new DB by wikidata_id
    skipped_name = []       # already in new DB by name
    to_import = []          # not found by any method

    for old_e in candidates:
        qid = old_e["wikidata_id"]
        name_key = normalize_name(old_e["name"])

        if qid in new_by_wikidata:
            skipped_wikidata.append((old_e["name"], qid, new_by_wikidata[qid]))
        elif name_key in new_by_name:
            skipped_name.append((old_e["name"], qid, new_by_name[name_key]))
        else:
            to_import.append(old_e)

    print(f"\n  Già presenti via wikidata_id: {len(skipped_wikidata)}")
    print(f"  Già presenti via nome:        {len(skipped_name)}")
    print(f"  Da importare:                 {len(to_import)}")

    if skipped_name:
        print("\n--- Match per nome (wikidata_id diverso — verificare) ---")
        for name, qid, new_id in skipped_name:
            print(f"  {name!r} ({qid}) → già {new_id}")

    print(f"\n--- Da importare ({len(to_import)}) ---")
    for old_e in sorted(to_import, key=lambda e: e["name"].upper()):
        print(f"  {old_e['wikidata_id']}  {old_e['name']!r}")

    if dry_run:
        print("\n[DRY RUN] No files written.")
        return

    # Sort alphabetically and assign IDs
    to_import_sorted = sorted(to_import, key=lambda e: normalize_name(e["name"]))

    imported = []
    for old_e in to_import_sorted:
        in_id = f"IN-{next_in:04d}"
        next_in += 1

        old_sources = old_e.get("sources", {})
        new_sources = {
            "ishares": None,
            "edf": None,
            "crunchbase": old_sources.get("crunchbase"),
            "infonodes": old_sources.get("infonodes"),
            "wikidata": old_sources.get("wikidata"),
        }

        new_history = list(old_e.get("history", [])) + [
            {
                "date": TODAY,
                "source": "migration",
                "author": "import_by_wikidata.py",
                "field": "*",
                "old": None,
                "new": None,
                "description": (
                    f"Imported from refactoring/data/database.json "
                    f"(old id: {old_e['id']}, wikidata_id: {old_e['wikidata_id']}). "
                    f"Identity verified via wikidata_id — no name normalization inference used."
                ),
            }
        ]

        new_validation = list(old_e.get("validation", [])) + [
            {
                "status": "needs_review",
                "description": (
                    "Imported from old DB via wikidata_id. "
                    "Verify iShares/EDF presence and whether Crunchbase data is current."
                ),
                "author": "import_by_wikidata.py",
                "datestamp": TODAY,
            }
        ]

        new_entity = {
            "id": in_id,
            "type": old_e.get("type", "company"),
            "roles": old_e.get("roles", ["manufacturer"]),
            "name": old_e["name"],
            "sector": old_e.get("sector"),
            "wikidata_id": old_e["wikidata_id"],
            "sources": new_sources,
            "history": new_history,
            "validation": new_validation,
            "tags": old_e.get("tags", []),
        }

        new_entities.append(new_entity)
        new_by_wikidata[old_e["wikidata_id"]] = in_id
        new_by_name[normalize_name(old_e["name"])] = in_id
        imported.append((old_e["name"], old_e["wikidata_id"], in_id))

    new_db["entities"] = new_entities
    new_db["_updated"] = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Imported {len(imported)} entities.")
    print(f"  Total entities now: {len(new_entities)}")
    print(f"\nNext: python3 scripts/validate.py")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
