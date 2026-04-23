#!/usr/bin/env python3
"""
patch_country_quality.py — Two data quality fixes:

  Fix A: 3 real country conflicts — set canonical infonodes.country and mark
         field_conflict validation entries as confirmed.
         - IN-1234 Destinus: infonodes=Netherlands→Switzerland (wikidata correct)
         - IN-1262 Chemring Group: wikidata=Germany is stale; UK confirmed
         - IN-1340 Umicore: wikidata=US is stale; Belgium confirmed

  Fix B: Normalise sources.wikidata.country "People's Republic of China" → "China"
         for all 40 affected entities. Resolves the 15 field_conflict cases and
         improves consistency for the remaining 25 (wikidata-only).

Usage:
  python3 scripts/patch_country_quality.py [--dry-run]
"""

import json, os, sys
from datetime import date

BASE          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
TODAY         = date.today().isoformat()
DRY_RUN       = "--dry-run" in sys.argv

# Fix A: canonical country per entity
COUNTRY_FIXES = {
    "IN-1234": {
        "correct_country": "Switzerland",
        "note": "Destinus SA headquartered in Geneva, Switzerland. "
                "Wikidata Q117323559 country=Switzerland confirmed correct. "
                "infonodes.country was Netherlands (likely EDF registration country); corrected.",
    },
    "IN-1262": {
        "correct_country": "United Kingdom",
        "note": "Chemring Group plc headquartered in Hampshire, UK (LSE-listed). "
                "Wikidata Q1069644 P17=Germany is stale/incorrect; UK confirmed correct. "
                "infonodes.country already United Kingdom; field_conflict resolved.",
    },
    "IN-1340": {
        "correct_country": "Belgium",
        "note": "Umicore NV/SA headquartered in Brussels, Belgium. Belgium confirmed correct. "
                "WARNING: wikidata_id Q107518759 label='Umicore (United States)' — this is the "
                "US subsidiary, not the parent company. QID should be replaced with parent "
                "Umicore entity when found. P17=United States reflects subsidiary HQ, not parent.",
    },
}


def ensure_infonodes(entity):
    sources = entity.setdefault("sources", {})
    if sources.get("infonodes") is None:
        sources["infonodes"] = {}
    return sources["infonodes"]


def resolve_field_conflict(entity, eid):
    """Mark any field_conflict validation entry as confirmed."""
    resolved = 0
    for v in entity.get("validation", []):
        if v.get("status") == "field_conflict" and v.get("field") in ("country", None):
            v["status"] = "confirmed"
            v["resolved"] = TODAY
            v["resolved_note"] = COUNTRY_FIXES[eid]["note"]
            resolved += 1
    return resolved


def fix_a(entities_by_id):
    changed = 0
    for eid, cfg in COUNTRY_FIXES.items():
        e = entities_by_id.get(eid)
        if not e:
            print(f"  [WARN] {eid} not found")
            continue
        inf = ensure_infonodes(e)
        old = inf.get("country")
        new = cfg["correct_country"]
        if old == new:
            print(f"  [SKIP] {eid} {e['name']}: infonodes.country already {new!r}")
            if not DRY_RUN:
                e.setdefault("history", []).append({
                    "date": TODAY,
                    "action": "confirm_country",
                    "field": "sources.infonodes.country",
                    "value": new,
                    "note": cfg["note"],
                    "script": "patch_country_quality.py",
                })
        else:
            print(f"  [FIX]  {eid} {e['name']}: infonodes.country {old!r} → {new!r}")
            if not DRY_RUN:
                inf["country"] = new
                e.setdefault("history", []).append({
                    "date": TODAY,
                    "action": "patch_country",
                    "field": "sources.infonodes.country",
                    "old": old,
                    "new": new,
                    "note": cfg["note"],
                    "script": "patch_country_quality.py",
                })
            changed += 1
        resolved = resolve_field_conflict(e, eid) if not DRY_RUN else 0
        print(f"         field_conflict entries resolved: {resolved}")
    return changed


def fix_b(entities):
    changed = 0
    field_conflicts_resolved = 0
    for e in entities:
        sources = e.get("sources") or {}
        wd = sources.get("wikidata") or {}
        if wd.get("country") != "People's Republic of China":
            continue
        inf = sources.get("infonodes") or {}
        inf_country = inf.get("country") or ""
        print(f"  {e['id']} {e['name']}: wikidata {wd['country']!r} → 'China'  "
              f"(infonodes={inf_country!r})")
        if not DRY_RUN:
            wd["country"] = "China"
            e.setdefault("history", []).append({
                "date": TODAY,
                "action": "normalise_country",
                "field": "sources.wikidata.country",
                "old": "People's Republic of China",
                "new": "China",
                "note": "Normalised to short ISO 3166 form for map consistency.",
                "script": "patch_country_quality.py",
            })
            # resolve field_conflict if infonodes was already "China"
            if inf_country == "China":
                for v in e.get("validation", []):
                    if v.get("status") == "field_conflict":
                        v["status"] = "confirmed"
                        v["resolved"] = TODAY
                        v["resolved_note"] = (
                            "sources.wikidata.country normalised People's Republic of China→China; "
                            "matches sources.infonodes.country."
                        )
                        field_conflicts_resolved += 1
        changed += 1
    return changed, field_conflicts_resolved


def main():
    print(f"patch_country_quality.py {'(DRY RUN) ' if DRY_RUN else ''}— {TODAY}\n")

    with open(DATABASE_PATH) as f:
        db = json.load(f)

    entities = db["entities"]
    by_id = {e["id"]: e for e in entities}

    print("=== Fix A: 3 real country conflicts ===")
    a_changed = fix_a(by_id)

    print(f"\n=== Fix B: Normalise 'People's Republic of China' → 'China' ===")
    b_changed, b_resolved = fix_b(entities)

    print(f"\nSummary:")
    print(f"  Fix A: {a_changed} country values updated")
    print(f"  Fix B: {b_changed} wikidata.country normalised, {b_resolved} field_conflicts resolved")

    if not DRY_RUN and (a_changed or b_changed):
        db["_updated"] = TODAY
        with open(DATABASE_PATH, "w") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\nWritten to {DATABASE_PATH}")
    elif DRY_RUN:
        print("\n(dry-run — no writes)")


if __name__ == "__main__":
    main()
