#!/usr/bin/env python3
"""
fix_wikidata.py — Apply wikidata_id corrections to database.json.

Fixes:
  - NVIDIA: restore Q2283 (wrongly reset to null by migrate.py bug)
  - Amazon: restore Q380 (wrongly reset to null by migrate.py bug)
"""

import json
import os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
TODAY = date.today().isoformat()

# company name (as in database.json) → correct wikidata_id
CORRECTIONS = {
    "NVIDIA": "Q2283",
    "Amazon": "Q380",
}

def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    changed = 0
    for entity in db["entities"]:
        name = entity.get("name")
        if name not in CORRECTIONS:
            continue
        if entity.get("type") != "company":
            continue

        correct_id = CORRECTIONS[name]
        old_id = entity.get("wikidata_id")

        if old_id == correct_id:
            print(f"  {name}: already {correct_id}, skipping")
            continue

        # Apply fix
        entity["wikidata_id"] = correct_id

        # Update validation: change the 'flagged' entry about this ID to 'confirmed'
        for v in entity.get("validation", []):
            if v.get("status") == "flagged" and correct_id in (v.get("description") or ""):
                v["status"] = "confirmed"
                v["description"] = (
                    f"wikidata_id {correct_id} confirmed correct. "
                    f"Original migrate.py flag was a false positive — "
                    f"the legacy wikipedia_url was wrong, not the wikidata_id."
                )
                v["datestamp"] = TODAY

        # Append history entry
        entity["history"].append({
            "date": TODAY,
            "source": "fix_wikidata.py",
            "author": "fix_wikidata.py",
            "field": "wikidata_id",
            "old": old_id,
            "new": correct_id,
            "description": (
                f"Restored correct wikidata_id. migrate.py had incorrectly flagged "
                f"{correct_id} as wrong based on a contaminated wikipedia_url in the "
                f"legacy source (Issue 1 in refactoring/issues.md)."
            ),
        })

        print(f"  ✓ {name}: null → {correct_id}")
        changed += 1

    db["_updated"] = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {changed} correction(s) applied.")

if __name__ == "__main__":
    main()
