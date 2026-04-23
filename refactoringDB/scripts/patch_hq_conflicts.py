#!/usr/bin/env python3
"""
patch_hq_conflicts.py — Resolve 26 headquarters field_conflict validation entries.

For each entity, updates the existing field_conflict entry and adds a
field_conflict_resolved (or compatible_sources) entry documenting which
source is canonical. For AMD, both sources are wrong — sets
sources.infonodes.headquarters to the verified value.

Usage:
    python3 scripts/patch_hq_conflicts.py [--dry-run]
"""

import json
import sys
from datetime import date

DRY_RUN = "--dry-run" in sys.argv
TODAY = date.today().isoformat()
DB_PATH = "data/database.json"

# ---------------------------------------------------------------------------
# Resolution table
# ---------------------------------------------------------------------------
# canonical_source: 'wikidata' | 'crunchbase' | 'compatible' | 'manual'
# canonical_hq: set only for 'manual' (both sources wrong)
# note: human-readable rationale

RESOLUTIONS = {
    "IN-1244": {
        "canonical_source": "crunchbase",
        "note": "AeroVironment relocated HQ from Simi Valley CA to Arlington VA in 2022; Crunchbase is current.",
    },
    "IN-1246": {
        "canonical_source": "crunchbase",
        "note": "Albemarle moved HQ from Baton Rouge to Charlotte NC; Crunchbase is current.",
    },
    "IN-1249": {
        "canonical_source": "manual",
        "canonical_hq": "Santa Clara, California, United States",
        "note": (
            "Both sources wrong: WD=Sunnyvale (outdated — AMD moved to Santa Clara in 2017), "
            "CB=Cologne Germany (AMD EU design centre, not corporate HQ). "
            "Canonical: Santa Clara, CA — set in sources.infonodes.headquarters."
        ),
    },
    "IN-1256": {
        "canonical_source": "wikidata",
        "note": "BAE Systems HQ is Farnborough, Hampshire; Crunchbase 'London' is incorrect.",
    },
    "IN-1259": {
        "canonical_source": "compatible",
        "note": "Bahçeşehir is a district of Istanbul; sources agree at different granularity.",
    },
    "IN-1274": {
        "canonical_source": "compatible",
        "note": "Both say Prague; Crunchbase adds region/country detail. Not a real conflict.",
    },
    "IN-1275": {
        "canonical_source": "wikidata",
        "note": (
            "DAQO New Energy's listed/corporate HQ is Shanghai; "
            "CB 'Wanzhou, Guangdong' conflates the legacy factory location with the wrong province."
        ),
    },
    "IN-1276": {
        "canonical_source": "compatible",
        "note": (
            "WD=Paris (official registered address); CB=Saint-Cloud (main facility, adjacent commune). "
            "Both are accurate at different specificity."
        ),
    },
    "IN-1285": {
        "canonical_source": "wikidata",
        "note": "General Dynamics relocated HQ from Falls Church to Reston VA in 2020; Wikidata is current.",
    },
    "IN-1290": {
        "canonical_source": "crunchbase",
        "note": (
            "WD QID Q7257522 maps to HII parent (Newport News); "
            "HII Mission Technologies is the IT subsidiary with offices in McLean VA — CB is correct."
        ),
    },
    "IN-1298": {
        "canonical_source": "wikidata",
        "note": (
            "CB 'Bhiwandi, Maharashtra, India' is a mismatch — likely a different company. "
            "Indra Sistemas SA is headquartered in Alcobendas, Spain."
        ),
    },
    "IN-1300": {
        "canonical_source": "crunchbase",
        "note": (
            "WD Lubin (Poland) is the parent KGHM Polska Miedź HQ; "
            "KGHM International Ltd. is the Canadian subsidiary, headquartered in Vancouver BC."
        ),
    },
    "IN-1302": {
        "canonical_source": "crunchbase",
        "note": "CB 'Berkeley, California' is the specific address; WD 'Silicon Valley' is a vague region label.",
    },
    "IN-1314": {
        "canonical_source": "crunchbase",
        "note": (
            "Newmont corporate address is Greenwood Village CO (suburb of Denver); "
            "CB is more precise. WD 'Denver' is the metropolitan approximation."
        ),
    },
    "IN-1315": {
        "canonical_source": "wikidata",
        "note": (
            "CB 'Richardson, Texas' is likely a mismatch to a different company. "
            "Nexa Technologies is the French body-scanner maker in Aix-en-Provence."
        ),
    },
    "IN-1318": {
        "canonical_source": "crunchbase",
        "note": "Palantir redomiciled HQ from Palo Alto CA to Denver CO in 2020; Crunchbase is current.",
    },
    "IN-1322": {
        "canonical_source": "wikidata",
        "note": (
            "QinetiQ HQ is Farnborough, Hampshire; "
            "CB 'Cardigan, Ceredigion' refers to a remote test site, not corporate HQ."
        ),
    },
    "IN-1323": {
        "canonical_source": "compatible",
        "note": "Kiryat Bialik is in the Greater Haifa metropolitan area; sources compatible at different granularity.",
    },
    "IN-1324": {
        "canonical_source": "crunchbase",
        "note": (
            "WD Arlington County is RTX parent HQ; "
            "Raytheon Missiles & Defense division HQ is Tucson AZ — CB is correct for this entity."
        ),
    },
    "IN-1325": {
        "canonical_source": "wikidata",
        "note": "Recylex SA is registered in Suresnes (suburb of Paris); CB 'Paris' is the broader metro area.",
    },
    "IN-1330": {
        "canonical_source": "wikidata",
        "note": (
            "Safran SA official corporate HQ is Paris; "
            "CB 'Pantin' is the location of a Safran subsidiary facility, not the group HQ."
        ),
    },
    "IN-1335": {
        "canonical_source": "crunchbase",
        "note": (
            "WD Essen is ThyssenKrupp parent HQ; "
            "ThyssenKrupp Marine Systems GmbH is headquartered in Kiel — CB is correct."
        ),
    },
    "IN-1338": {
        "canonical_source": "crunchbase",
        "note": (
            "WD Hsinchu Science Park is TSMC parent (Taiwan) HQ; "
            "TSMC Arizona entity is located in Phoenix AZ — CB is correct."
        ),
    },
    "IN-1342": {
        "canonical_source": "wikidata",
        "note": (
            "United Shipbuilding Corporation relocated its registered HQ to Saint Petersburg in 2012; "
            "CB 'Moscow' reflects earlier management office location."
        ),
    },
    "IN-1343": {
        "canonical_source": "wikidata",
        "note": (
            "Uralvagonzavod's main production facility and registered address is Nizhny Tagil; "
            "CB 'Moscow' refers to a management representative office."
        ),
    },
    "IN-1346": {
        "canonical_source": "compatible",
        "note": "München is the German name for Munich; same city. Normalisation difference only.",
    },
}

# ---------------------------------------------------------------------------
# Load DB
# ---------------------------------------------------------------------------

with open(DB_PATH) as f:
    db = json.load(f)

id_map = {e["id"]: e for e in db["entities"]}

# ---------------------------------------------------------------------------
# Apply resolutions
# ---------------------------------------------------------------------------

patched = 0
skipped = 0

for eid, res in RESOLUTIONS.items():
    e = id_map.get(eid)
    if e is None:
        print(f"WARN: {eid} not found in DB — skipped")
        skipped += 1
        continue

    # Find existing field_conflict (headquarters) validation entry
    fc_entry = None
    for v in e.get("validation", []):
        if v.get("status") == "field_conflict" and "headquarters" in v.get("description", ""):
            fc_entry = v
            break

    if fc_entry is None:
        print(f"INFO: {eid} {e['name']} — no field_conflict(headquarters) entry found, skipping")
        skipped += 1
        continue

    canonical_source = res["canonical_source"]
    note = res["note"]

    new_status = "compatible_sources" if canonical_source == "compatible" else "field_conflict_resolved"

    # Build new validation entry
    new_entry = {
        "status": new_status,
        "description": (
            f"HQ conflict resolved ({canonical_source}): {note}"
            if canonical_source not in ("compatible", "manual")
            else f"HQ sources compatible: {note}"
            if canonical_source == "compatible"
            else f"HQ manual override: {note}"
        ),
        "author": "patch_hq_conflicts.py",
        "datestamp": TODAY,
    }

    # For manual override: set sources.infonodes.headquarters
    infonodes_hq_set = False
    if canonical_source == "manual":
        canonical_hq = res["canonical_hq"]
        if not DRY_RUN:
            if "infonodes" not in e["sources"]:
                e["sources"]["infonodes"] = {}
            e["sources"]["infonodes"]["headquarters"] = canonical_hq
            e["history"].append({
                "date": TODAY,
                "source": "infonodes",
                "author": "patch_hq_conflicts.py",
                "field": "sources.infonodes.headquarters",
                "old": None,
                "new": canonical_hq,
                "description": f"Canonical HQ set manually: {note}",
            })
        infonodes_hq_set = True

    # Check if already resolved
    already_resolved = any(
        v.get("status") in ("compatible_sources", "field_conflict_resolved")
        and "headquarters" in v.get("description", "")
        for v in e.get("validation", [])
    )
    if already_resolved:
        print(f"INFO: {eid} {e['name']} — already resolved, skipping")
        skipped += 1
        continue

    if DRY_RUN:
        action = f"[DRY-RUN] Would set status={new_status}"
        if infonodes_hq_set:
            action += f", infonodes.headquarters={res['canonical_hq']}"
        print(f"  {eid}  {e['name']}")
        print(f"    {action}")
        print(f"    {note}")
    else:
        e.setdefault("validation", []).append(new_entry)
        patched += 1

    patched += 1 if DRY_RUN else 0  # count dry-run hits too for summary

if not DRY_RUN:
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Done: {patched} resolved, {skipped} skipped. Run validate.py to confirm.")
else:
    print(f"\nDry-run complete: {patched} would be patched, {skipped} skipped.")
