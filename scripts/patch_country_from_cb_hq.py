#!/usr/bin/env python3
"""
patch_country_from_cb_hq.py — Populate sources.infonodes.country from CB headquarters
for IN-* entities that have no country in infonodes/wikidata/edf sources.

CB headquarters format: "City, State, Country"  (last segment = country)

Run:
  python3 scripts/patch_country_from_cb_hq.py [--dry-run]
"""

import json, os, sys
from datetime import date

BASE          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
TODAY         = date.today().isoformat()
DRY_RUN       = "--dry-run" in sys.argv

# Normalise known Wikidata country variants
NORMALISE = {
    "People's Republic of China": "China",
    "PRC":                        "China",
    "USA":                        "United States",
    "US":                         "United States",
    "UK":                         "United Kingdom",
    "Great Britain":              "United Kingdom",
}


def get_country(e):
    s = e.get("sources") or {}
    return (
        ((s.get("infonodes") or {}).get("country") or "").strip() or
        ((s.get("wikidata")  or {}).get("country") or "").strip() or
        ((s.get("edf")       or {}).get("country") or "").strip()
    )


def extract_country_from_hq(hq):
    """Return last comma-separated segment of CB headquarters string."""
    if not hq:
        return ""
    parts = [p.strip() for p in hq.split(",")]
    return parts[-1] if parts else ""


CB_MISMATCH_FLAGS = {"cb_hq_mismatch_subsidiary", "cb_hq_mismatch_severe", "cb_wrong_entity"}


def has_cb_mismatch(e):
    """True if the entity has any CB HQ mismatch or wrong-entity validation flag."""
    for v in (e.get("validation") or []):
        if v.get("status") in CB_MISMATCH_FLAGS:
            return True
    return False


def main():
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    patched = 0
    normalised = 0

    for e in db["entities"]:
        if not e["id"].startswith("IN-"):
            continue
        s   = e.setdefault("sources", {}) or {}
        if not s.get("infonodes"):
            s["infonodes"] = {}
        inf = s["infonodes"]
        cb  = (s.get("crunchbase") or {})

        existing = get_country(e)

        # Case 1: no country at all — try CB HQ
        # Skip: entities with wikidata_id (should have gotten country from enrich_wikidata.py)
        # Skip: entities with CB HQ mismatch flags (CB matched a regional subsidiary)
        if not existing and not e.get("wikidata_id") and not has_cb_mismatch(e):
            hq = cb.get("headquarters", "")
            country = extract_country_from_hq(hq)
            country = NORMALISE.get(country, country)
            if not country:
                continue
            print(f"  PATCH  {e['id']} {e['name']}: country ← '{country}' (from CB HQ: {hq})")
            if not DRY_RUN:
                inf["country"] = country
                e.setdefault("history", []).append({
                    "date":   TODAY,
                    "action": "field_set",
                    "field":  "sources.infonodes.country",
                    "value":  country,
                    "source": "crunchbase_headquarters",
                    "by":     "patch_country_from_cb_hq.py",
                })
            patched += 1

        # Case 2: wikidata.country needs normalisation
        # Skip: entities with CB mismatch flags (their wikidata.country may also be wrong)
        if has_cb_mismatch(e):
            continue
        wd = s.get("wikidata") or {}
        wd_country = wd.get("country", "")
        if wd_country and wd_country in NORMALISE:
            normed = NORMALISE[wd_country]
            print(f"  NORM   {e['id']} {e['name']}: wikidata.country '{wd_country}' → '{normed}'")
            if not DRY_RUN:
                wd["country"] = normed
                e.setdefault("history", []).append({
                    "date":   TODAY,
                    "action": "field_normalised",
                    "field":  "sources.wikidata.country",
                    "from":   wd_country,
                    "to":     normed,
                    "by":     "patch_country_from_cb_hq.py",
                })
            normalised += 1

    print(f"\nSummary: {patched} patched, {normalised} normalised", end="")
    if DRY_RUN:
        print("  (DRY RUN — no writes)")
    else:
        print()
        with open(DATABASE_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print("Saved.")


if __name__ == "__main__":
    main()
