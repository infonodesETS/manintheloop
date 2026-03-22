#!/usr/bin/env python3
"""
apply_inspector_ids.py — Applies wikidata_ids from wikidata_inspector/data/companies.json
to database.json entities that currently have wikidata_id: null.

False positives explicitly excluded (wrong entity matched by substring):
  - "Intelic" would match "Intel" (Q248) — Intelic is a Dutch C2 startup, not Intel
  - "AVICOPTER PLC" would match "AVIC" (Q312094) — AVICOPTER is an AVIC subsidiary, not AVIC itself
"""

import json
import os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSPECTOR_PATH = os.path.join(BASE, "..", "wikidata_inspector", "data", "companies.json")
DATABASE_PATH  = os.path.join(BASE, "data", "database.json")
TODAY = date.today().isoformat()

# Exact mapping: database entity name → wikidata_id
# Built from cross-reference + manual curation (false positives removed)
MAPPING = {
    "Airbus":                           "Q2311",
    "Albemarle":                        "Q127074",
    "American Elements":                "Q4743673",
    "Babcock International":            "Q385426",
    "Bayan Resources":                  "Q96100147",
    "Baykar":                           "Q6023024",
    "CASIC":                            "Q10874081",
    "CODELCO":                          "Q1105695",
    "CSSC":                             "Q1073512",
    "Chemring Group":                   "Q1069644",
    "China Minmetals":                  "Q846839",
    "China Northern Rare Earth":        "Q55697404",
    "Colt CZ Group":                    "Q55568528",
    "Czechoslovak Group":               "Q27350567",
    "DAQO NEW ENERGY":                  "Q16973267",
    "DOWA Holdings":                    "Q5302643",
    "Dassault Aviation":                "Q460487",
    "Elbit Systems":                    "Q1325369",
    "Elkem":                            "Q1331615",
    "Eviden":                           "Q5418319",
    "Exxelia Group":                    "Q103812026",
    "Ferroglobe":                       "Q125144368",
    "Fincantieri":                      "Q1327429",
    "First Quantum Minerals":           "Q1419532",
    "GCL Technology":                   "Q124670561",
    "Ganfeng Lithium":                  "Q10954805",
    "HAVELSAN":                         "Q5628993",
    "Hemlock Semiconductor Operations": "Q5712288",
    "Hoshine Silicon":                  "Q108003110",
    "Iluka Resources Ltd":              "Q1117761",
    "Indium":                           "Q16986090",
    "Israel Aerospace Industries":      "Q876017",
    "Kongsberg":                        "Q1770909",
    "Liontown":                         "Q109625740",
    "Lynas Rare Earths Ltd":            "Q6708384",
    "MBDA":                             "Q1475070",
    "MP Materials":                     "Q105563992",
    "MTU Aero Engines GmbH":            "Q128929",
    "Melrose Industries":               "Q3305280",
    "Mineral Resources":                "Q108541568",
    "Mitsubishi Materials":             "Q1423176",
    "Nammo":                            "Q1964355",
    "Naval Group":                      "Q1227511",
    "Norincogroup":                     "Q1538336",
    "Pilbara Minerals":                 "Q56064089",
    "Plasan":                           "Q744498",
    "QinetiQ":                          "Q1759946",
    "Rafael Advanced Defense Systems":  "Q154610",
    "Recylex":                          "Q30292359",
    "Roketsan":                         "Q2548367",
    "Rolls-Royce":                      "Q243278",
    "Shenghe Resources":                "Q15916333",
    "Sociedad Quimica Y Minera (SQM)":  "Q3067064",
    "ThyssenKrupp Marine Systems":      "Q551068",
    "Tianqi Lithium":                   "Q55635834",
    "Tongwei":                          "Q16923900",
    "Umicore":                          "Q107518759",
    "Uralvagonzavod":                   "Q1762250",
    "Vital Materials":                  "Q121407257",
    "Wacker Chemie":                    "Q535517",
    "Xinte Energy":                     "Q124670171",
    "Zhuzhou Smelter Group":            "Q20063580",
    # Excluded (false positives):
    # "AVICOPTER PLC" → Q312094 (AVIC) — AVICOPTER is AVIC subsidiary
    # "Intelic"       → Q248    (Intel) — Intelic is a Dutch C2 startup
}

def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    applied = 0
    skipped = 0

    for entity in db["entities"]:
        if entity.get("type") != "company":
            continue
        if entity.get("wikidata_id"):
            continue  # already has an ID

        name = entity["name"]
        qid = MAPPING.get(name)
        if not qid:
            skipped += 1
            continue

        entity["wikidata_id"] = qid
        entity["history"].append({
            "date": TODAY,
            "source": "apply_inspector_ids.py",
            "author": "apply_inspector_ids.py",
            "field": "wikidata_id",
            "old": None,
            "new": qid,
            "description": "wikidata_id assigned from wikidata_inspector/data/companies.json cross-reference",
        })
        entity["validation"].append({
            "status": "needs_review",
            "description": f"wikidata_id {qid} assigned via name-matching from inspector list — confirm correct entity",
            "author": "apply_inspector_ids.py",
            "datestamp": TODAY,
        })

        print(f"  ✓ {name} → {qid}")
        applied += 1

    db["_updated"] = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\nApplied: {applied}  |  Still missing: {skipped}")

if __name__ == "__main__":
    main()
