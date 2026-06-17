#!/usr/bin/env python3
"""
import_startups.py — Import startup entities from refactoring/data/database.json
into the new database.json.

For each startup (sector=Startup) in the old DB:
  - Checks if already present in new DB by normalized name (skip if found).
  - Creates a new IN-NNNN entity preserving:
      sources.crunchbase  (full block from old DB)
      sources.infonodes   (full block from old DB)
      sources.wikidata    (full block from old DB, if any)
      wikidata_id
      sector
      roles
      validation[]        (preserved from old DB)
  - Adds a new history entry documenting the import.
  - Adds the old DB's history entries first, then the import entry.

Usage:
    python3 scripts/import_startups.py [--dry-run]

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
        r"\bCORPORATION\b", r"\bCORP\b", r"\bLIMITED\b", r"\bLTD\b",
        r"\bINCORPORATED\b", r"\bINC\b", r"\bPLC\b", r"\bAG\b", r"\bSE\b",
        r"\bGMBH\b", r"\bGROUP\b", r"\bHOLDINGS?\b",
    ]:
        s = re.sub(pattern, "", s)
    return re.sub(r"\s+", " ", s).strip()


def main(dry_run: bool = False):
    print("Loading old database.json...")
    with open(OLD_DB_PATH, encoding="utf-8") as f:
        old_db = json.load(f)

    old_startups = [
        e for e in old_db["entities"]
        if e.get("sector") == "Startup"
    ]
    print(f"  Startup nel vecchio DB: {len(old_startups)}")

    print("\nLoading new database.json...")
    with open(DATABASE_PATH, encoding="utf-8") as f:
        new_db = json.load(f)

    new_entities: list[dict] = new_db["entities"]
    name_index = {normalize_name(e["name"]): e["id"] for e in new_entities}

    # Max IN-NNNN
    max_in = max(
        int(e["id"][3:]) for e in new_entities if e["id"].startswith("IN-")
    )
    next_in = max_in + 1

    skipped = []
    imported = []

    for old_e in old_startups:
        key = normalize_name(old_e["name"])
        if key in name_index:
            skipped.append((old_e["name"], name_index[key]))
            continue

        in_id = f"IN-{next_in:04d}"
        next_in += 1

        # Build sources block — carry over all sources from old DB
        old_sources = old_e.get("sources", {})
        new_sources = {
            "ishares": None,
            "edf": None,
            "crunchbase": old_sources.get("crunchbase"),
            "infonodes": old_sources.get("infonodes"),
            "wikidata": old_sources.get("wikidata"),
        }

        # Carry over history from old DB, then append import entry
        old_history = old_e.get("history", [])
        new_history = list(old_history) + [
            {
                "date": TODAY,
                "source": "migration",
                "author": "import_startups.py",
                "field": "*",
                "old": None,
                "new": None,
                "description": (
                    f"Imported from refactoring/data/database.json "
                    f"(old id: {old_e['id']}, sector: Startup). "
                    f"sources.crunchbase and sources.infonodes preserved from old DB."
                ),
            }
        ]

        # Carry over validation, add new entry
        old_validation = old_e.get("validation", [])
        new_validation = list(old_validation) + [
            {
                "status": "needs_review",
                "description": (
                    "Imported startup — verify roles, iShares/EDF presence, "
                    "and whether Crunchbase data is still current."
                ),
                "author": "import_startups.py",
                "datestamp": TODAY,
            }
        ]

        new_entity = {
            "id": in_id,
            "type": old_e.get("type", "company"),
            "roles": old_e.get("roles", ["manufacturer"]),
            "name": old_e["name"],
            "sector": old_e.get("sector"),
            "wikidata_id": old_e.get("wikidata_id"),
            "sources": new_sources,
            "history": new_history,
            "validation": new_validation,
            "tags": old_e.get("tags", []),
        }

        new_entities.append(new_entity)
        name_index[key] = in_id
        imported.append((old_e["name"], old_e["id"], in_id))

    # Summary
    print(f"\n  Già presenti (skip):  {len(skipped)}")
    for name, existing_id in skipped:
        print(f"    {name!r} → già {existing_id}")

    print(f"\n  Da importare:         {len(imported)}")
    for name, old_id, new_id in imported:
        print(f"    {old_id} → {new_id}: {name!r}")

    if dry_run:
        print("\n[DRY RUN] No files written.")
        return

    new_db["entities"] = new_entities
    new_db["_updated"] = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Imported {len(imported)} startup entities.")
    print(f"  Total entities now: {len(new_entities)}")
    print(f"\nNext: python3 scripts/validate.py")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
