"""
import_edf_websites.py — populate sources.infonodes.website from edf_orgs.json

For each EDF org that has a web_link and a db_id crosswalk, writes the URL
into sources.infonodes.website in database.json — unless the entity already
has a crunchbase website (which takes precedence as more authoritative).

History source: "edf"
Author:         import_edf_websites.py

Run:
    python3 scripts/import_edf_websites.py [--dry-run]
"""

import json
import sys
from datetime import date

BASE_DIR = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
DB_PATH = __import__("os").path.join(BASE_DIR, "data", "database.json")
EDF_PATH = __import__("os").path.join(BASE_DIR, "data", "edf_orgs.json")

TODAY = date.today().isoformat()
DRY_RUN = "--dry-run" in sys.argv


def normalize_url(url: str) -> str:
    url = url.strip()
    if url and not url.startswith("http"):
        url = "https://" + url
    return url


def main():
    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)
    with open(EDF_PATH, encoding="utf-8") as f:
        edf = json.load(f)

    # Build db_id → web_link map from edf_orgs
    edf_links: dict[str, str] = {}
    for org in edf["orgs"].values():
        db_id = org.get("db_id")
        wl = org.get("web_link") or ""
        wl = wl.strip()
        if db_id and wl:
            edf_links[db_id] = normalize_url(wl)

    print(f"EDF orgs with web_link + db_id: {len(edf_links)}")

    entities_by_id = {e["id"]: e for e in db["entities"]}

    updated = 0
    skipped_cb = 0
    skipped_already = 0
    not_found = 0

    for db_id, url in sorted(edf_links.items()):
        entity = entities_by_id.get(db_id)
        if not entity:
            not_found += 1
            continue

        # Skip if crunchbase already has a website (more authoritative)
        cb = entity.get("sources", {}).get("crunchbase") or {}
        if isinstance(cb, dict) and cb.get("website"):
            skipped_cb += 1
            continue

        # Check current infonodes.website
        infonodes = entity.get("sources", {}).get("infonodes") or {}
        current = infonodes.get("website") if isinstance(infonodes, dict) else None
        if current == url:
            skipped_already += 1
            continue

        print(f"  {'[DRY]' if DRY_RUN else ''} {db_id} {entity['name']!r} → {url}")

        if not DRY_RUN:
            # Ensure sources.infonodes exists as a dict
            if not isinstance(entity.get("sources", {}).get("infonodes"), dict):
                entity.setdefault("sources", {})["infonodes"] = {
                    "extracted_at": TODAY,
                    "sector": None,
                    "country": None,
                    "tax_id": None,
                    "main_focus": None,
                    "wikipedia_url": None,
                    "website": None,
                }
            old_val = entity["sources"]["infonodes"].get("website")
            entity["sources"]["infonodes"]["website"] = url
            entity["sources"]["infonodes"]["extracted_at"] = TODAY

            # Append history entry
            entity.setdefault("history", []).append({
                "date": TODAY,
                "source": "edf",
                "author": "import_edf_websites.py",
                "field": "sources.infonodes.website",
                "old": old_val,
                "new": url,
                "description": "Website URL imported from edf_orgs.json web_link field",
            })

        updated += 1

    print()
    print(f"{'[DRY RUN] ' if DRY_RUN else ''}Results:")
    print(f"  Written/would write: {updated}")
    print(f"  Skipped (crunchbase takes precedence): {skipped_cb}")
    print(f"  Skipped (already set to same value):   {skipped_already}")
    print(f"  db_id not found in DB:                 {not_found}")

    if not DRY_RUN and updated > 0:
        db["_updated"] = TODAY
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\nSaved → {DB_PATH}")


if __name__ == "__main__":
    main()
