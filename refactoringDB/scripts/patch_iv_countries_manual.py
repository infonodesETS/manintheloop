#!/usr/bin/env python3
"""
patch_iv_countries_manual.py — Curated country assignment for IV entities
where SPARQL P17/P159 lookup returned no result (Wikidata lacks those properties).

Each entry verified against public knowledge; QID listed for traceability.

Usage:
    python3 scripts/patch_iv_countries_manual.py [--dry-run]
"""

import json
import sys
from datetime import date

DRY_RUN = "--dry-run" in sys.argv
TODAY = date.today().isoformat()
DB_PATH = "data/database.json"

# (entity_id, country, note)
MANUAL = [
    ("IV-0063", "Canada",        "BCI (British Columbia Investment Management Corp.) — Victoria, BC, Canada"),
    ("IV-0072", "United States", "Bezos Expeditions — Jeff Bezos personal investment vehicle, USA"),
    ("IV-0155", "United States", "DCM Ventures — HQ San Mateo CA; also offices in Tokyo/Beijing but registered USA"),
    ("IV-0183", "United States", "Engine No. 1 — San Francisco CA activist investment firm"),
    ("IV-0378", "South Korea",   "MBK Partners — Seoul, South Korea private equity"),
    ("IV-0419", "United States", "Northgate Capital — Lafayette CA fund-of-funds"),
    ("IV-0435", "United States", "OrbiMed — New York NY healthcare investor"),
    ("IV-0458", "China",         "Qiming Venture Partners — Shanghai, China VC"),
    ("IV-0543", "India",         "Tata Mutual Fund — Mumbai, India; part of Tata Group"),
    ("IV-0560", "China",         "Tianqi Lithium — Chengdu, Sichuan, China"),
    ("IV-0585", "United States", "Valar Ventures — New York NY; Peter Thiel-backed VC"),
    ("IV-0618", "United States", "Chamath Palihapitiya — Social Capital founder, USA"),
    ("IV-0621", "United States", "Daniel Loeb — Third Point LLC founder, New York USA"),
    ("IV-0624", "United States", "Elad Gil — investor and entrepreneur, San Francisco CA USA"),
    ("IV-0643", "United States", "Reed Hastings — Netflix co-founder, USA"),
]

with open(DB_PATH) as f:
    db = json.load(f)

id_map = {e["id"]: e for e in db["entities"]}

patched = 0
for eid, country, note in MANUAL:
    e = id_map.get(eid)
    if e is None:
        print(f"WARN: {eid} not found")
        continue

    existing = (e["sources"].get("infonodes") or {}).get("country") or \
               (e["sources"].get("wikidata") or {}).get("country")
    if existing:
        print(f"SKIP: {eid} {e['name']} — already has country={existing}")
        continue

    if DRY_RUN:
        print(f"  [DRY] {eid}  {e['name']} → {country}")
        print(f"        {note}")
    else:
        if "infonodes" not in e["sources"]:
            e["sources"]["infonodes"] = {}
        e["sources"]["infonodes"]["country"] = country
        e["history"].append({
            "date": TODAY,
            "source": "infonodes",
            "author": "patch_iv_countries_manual.py",
            "field": "sources.infonodes.country",
            "old": None,
            "new": country,
            "description": f"Country curated manually: {note}",
        })
        print(f"  ✓ {eid}  {e['name']} → {country}")
    patched += 1

if not DRY_RUN:
    db["_updated"] = TODAY
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"\nPatched: {patched}. Run validate.py to confirm.")
else:
    print(f"\n[DRY-RUN] {patched} would be patched.")
