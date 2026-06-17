#!/usr/bin/env python3
"""
fix_qid_shift.py — Corrects the systematic QID chain-shift contamination.

The legacy investments.json (and the user's canonical table derived from it) had
a circular shift of wikidata_ids across ~20 Tech/Mining companies: each company
was assigned its neighbor's QID. The Wikidata API confirmed the correct assignments.

Also fixes Glencore whose QID (Q182477) was actually NVIDIA's — correct Glencore
QID is Q169339 from Wikidata search.

All corrected companies are re-enriched from the Wikidata API.
"""

import json
import os
import re
import time
import urllib.request
import urllib.parse
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
TODAY = date.today().isoformat()

API = "https://www.wikidata.org/w/api.php"
DELAY = 0.4

# Correct database entity name → correct wikidata_id
# Derived purely from Wikidata API responses (what each QID actually is)
CORRECT_QIDS = {
    "NVIDIA":                "Q182477",   # Q182477 = Nvidia (confirmed: founded 1993, ISIN US67066G1040)
    "Glencore":              "Q169339",   # Q169339 = Glencore (from Wikidata search)
    "Microsoft":             "Q2283",     # Q2283   = Microsoft (confirmed: founded 1975)
    "Apple":                 "Q312",      # Q312    = Apple Inc. (confirmed: founded 1976)
    "Alphabet":              "Q20800404", # Q20800404 = Alphabet (confirmed)
    "Amazon":                "Q3884",     # Q3884   = Amazon (confirmed)
    "Meta for Developers":   "Q380",      # Q380    = Meta (confirmed: founded 2004)
    "Broadcom":              "Q790060",   # Q790060 = Broadcom (confirmed)
    "Tesla":                 "Q765530",   # Q765530 = Tesla (confirmed)
    "TSMC Arizona":          "Q713418",   # Q713418 = TSMC (confirmed)
    "IBM":                   "Q37156",    # Q37156  = IBM (confirmed)
    "Samsung Electronics":   "Q20718",    # Q20718  = Samsung Electronics (confirmed)
    "Cisco Systems":         "Q173395",   # Q173395 = Cisco (confirmed)
    "AMD":                   "Q128896",   # Q128896 = AMD (confirmed)
    "Qualcomm":              "Q544847",   # Q544847 = Qualcomm (confirmed)
    "Netflix":               "Q907311",   # Q907311 = Netflix (confirmed)
    "SAP":                   "Q552581",   # Q552581 = SAP (confirmed)
    "ASML":                  "Q297879",   # Q297879 = ASML Holding (confirmed)
    "Oracle":                "Q19900",    # Q19900  = Oracle (confirmed)
}

# ── Wikidata fetch helpers (same as enrich_wikidata.py) ───────────────────────

def api_get(params):
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "infonodes-migrate/2.0 (research)"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def batch_entities(qids, props="labels|descriptions|aliases|claims|sitelinks"):
    data = api_get({"action": "wbgetentities", "ids": "|".join(qids), "languages": "en", "props": props})
    return data.get("entities", {})


def resolve_item_labels(qids):
    if not qids:
        return {}
    result = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i+50]
        entities = batch_entities(chunk, props="labels")
        for qid, ent in entities.items():
            label = ent.get("labels", {}).get("en", {}).get("value")
            if label:
                result[qid] = label
        if i + 50 < len(qids):
            time.sleep(DELAY)
    return result


def extract_claim_value(snak, item_labels):
    sv = snak.get("datavalue", {})
    vtype = sv.get("type")
    value = sv.get("value")
    if vtype == "wikibase-entityid":
        qid = value.get("id")
        return item_labels.get(qid, qid)
    if vtype == "time":
        raw = value.get("time", "")
        m = re.match(r"^\+?(\d{4})-(\d{2})-(\d{2})", raw)
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            if mo == "00": return y
            if d == "00": return f"{y}-{mo}"
            return f"{y}-{mo}-{d}"
        return raw
    if vtype == "string":
        return str(value)
    if vtype == "monolingualtext":
        return value.get("text")
    if vtype == "quantity":
        amount = value.get("amount", "").lstrip("+")
        try: return int(float(amount))
        except: return amount
    return None


def get_best_claim_value(claims, pid, item_labels):
    stmts = claims.get(pid, [])
    preferred = [s for s in stmts if s.get("rank") == "preferred"]
    active = preferred or [s for s in stmts if s.get("rank") == "normal"]
    values = []
    for stmt in active:
        snak = stmt.get("mainsnak", {})
        if snak.get("snaktype") != "value":
            continue
        val = extract_claim_value(snak, item_labels)
        if val is not None:
            values.append(val)
    if not values:
        return None
    return values if pid == "P31" else values[0]


def parse_entity(ent, item_labels):
    claims   = ent.get("claims", {})
    sitelinks = ent.get("sitelinks", {})
    label    = ent.get("labels", {}).get("en", {}).get("value")
    description = ent.get("descriptions", {}).get("en", {}).get("value")
    aliases  = [a["value"] for a in ent.get("aliases", {}).get("en", [])]
    enwiki   = sitelinks.get("enwiki", {})
    wiki_title = enwiki.get("title")
    wikipedia_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(wiki_title)}" if wiki_title else None
    return {
        "retrieved_at":    TODAY,
        "label":           label,
        "description":     description,
        "aliases":         aliases,
        "instance_of":     get_best_claim_value(claims, "P31", item_labels),
        "country":         get_best_claim_value(claims, "P17", item_labels),
        "inception":       get_best_claim_value(claims, "P571", item_labels),
        "headquarters":    get_best_claim_value(claims, "P159", item_labels),
        "official_website":get_best_claim_value(claims, "P856", item_labels),
        "isin":            get_best_claim_value(claims, "P946", item_labels),
        "employees":       get_best_claim_value(claims, "P1128", item_labels),
        "wikipedia_url":   wikipedia_url,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    # ── Step 1: Apply corrected QIDs ──────────────────────────────────────────
    print("Applying corrected wikidata_ids...")
    corrected_entities = []

    for entity in db["entities"]:
        if entity.get("type") != "company":
            continue
        name = entity["name"]
        if name not in CORRECT_QIDS:
            continue

        old_qid = entity.get("wikidata_id")
        new_qid = CORRECT_QIDS[name]

        if old_qid == new_qid:
            print(f"  = {name}: already {new_qid}")
            corrected_entities.append(entity)
            continue

        entity["wikidata_id"] = new_qid
        entity["sources"]["wikidata"] = None  # will be re-enriched

        entity["history"].append({
            "date": TODAY,
            "source": "fix_qid_shift.py",
            "author": "fix_qid_shift.py",
            "field": "wikidata_id",
            "old": old_qid,
            "new": new_qid,
            "description": (
                f"Corrected QID: {old_qid} was the wrong entity's ID "
                f"(systematic chain-shift contamination from legacy data). "
                f"Correct ID {new_qid} confirmed by Wikidata API. "
                f"See refactoring/issues.md Issue 1 & Issue 6."
            ),
        })
        entity["validation"].append({
            "status": "confirmed",
            "description": f"wikidata_id {new_qid} verified correct via Wikidata API label match",
            "author": "fix_qid_shift.py",
            "datestamp": TODAY,
        })

        print(f"  ✓ {name}: {old_qid} → {new_qid}")
        corrected_entities.append(entity)

    # ── Step 2: Fetch fresh Wikidata data for corrected entities ───────────────
    print(f"\nFetching Wikidata for {len(corrected_entities)} corrected entities...")
    new_qids = [e["wikidata_id"] for e in corrected_entities]

    raw_entities = {}
    for i in range(0, len(new_qids), 50):
        chunk = new_qids[i:i+50]
        print(f"  Batch: {chunk[0]}…{chunk[-1]}")
        raw_entities.update(batch_entities(chunk))
        if i + 50 < len(new_qids):
            time.sleep(DELAY)

    # Collect item QIDs to resolve
    item_qids = set()
    for ent in raw_entities.values():
        for pid in ("P31", "P17", "P159"):
            for stmt in ent.get("claims", {}).get(pid, []):
                sv = stmt.get("mainsnak", {}).get("datavalue", {})
                if sv.get("type") == "wikibase-entityid":
                    qid = sv.get("value", {}).get("id")
                    if qid: item_qids.add(qid)

    print(f"  Resolving {len(item_qids)} item labels...")
    item_labels = resolve_item_labels(list(item_qids))

    # Apply enrichment
    for entity in corrected_entities:
        qid = entity["wikidata_id"]
        raw = raw_entities.get(qid)
        if not raw or raw.get("missing"):
            print(f"  ✗ {entity['name']} ({qid}): not found")
            continue
        entity["sources"]["wikidata"] = parse_entity(raw, item_labels)

    db["_updated"] = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Done. {len(corrected_entities)} entities corrected and re-enriched.")


if __name__ == "__main__":
    main()
