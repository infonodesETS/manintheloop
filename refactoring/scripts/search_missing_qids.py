#!/usr/bin/env python3
"""
search_missing_qids.py — Searches Wikidata for the 48 companies still missing wikidata_id.
Applies best match when confident, skips when ambiguous or not found.
Re-enriches all newly assigned entities.
"""

import json, os, re, time, urllib.request, urllib.parse
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
TODAY = date.today().isoformat()
API   = "https://www.wikidata.org/w/api.php"
DELAY = 0.35

# Manual overrides for names that search won't find cleanly
OVERRIDES = {
    "Freeport Mcmoran":                          "Q1451578",   # Freeport-McMoRan
    "KGHM International":                        "Q649044",    # KGHM Polska Miedź
    "China Aerospace Science and Technology Corporation": "Q1413583",  # CASC
    "Concern PVO Almaz Antey":                   "Q1331507",   # Almaz-Antey
    "United Aircraft":                           "Q1425671",   # United Aircraft Corporation
    "United Shipbuilding Corporation":           "Q2087817",   # USC Russia
    "Turkish Aerospace (TAI)":                   "Q841097",    # TAI
    "Tactical Missiles Corp (KTRV)":             "Q4451987",   # KTRV
    "IMI Systems":                               "Q3151155",   # IMI (Israeli weapons)
    "PGZ (Polish Armaments)":                    "Q9378395",   # PGZ
    "Diehl Defence":                             "Q1214879",   # Diehl Stiftung group
    "Fokker Technologies":                       "Q1444213",   # Fokker Technologies
    "Chinalco (Gallium)":                        "Q4462219",   # Chalco / Chinalco
    "Chinalco Rare Earth":                       "Q4462219",   # same parent
    "Arafura Resources":                         "Q4783971",   # Arafura Resources
    "Indian Rare Earths":                        "Q6016234",   # IREL (India)
    "Sichuan Yahua":                             "Q56404682",  # Sichuan Yahua Industrial Group
    "Nexa Technologies":                         "Q63071700",  # Nexa Technologies (Amesys spin-off)
    "Amesys SAS":                                "Q2843668",   # Amesys
    "NeoPerformance":                            "Q124380993", # Neo Performance Materials
    "AVICOPTER PLC":                             "Q312094",    # AVIC Helicopter (subsidiary of AVIC — best available)
    "Advanced Middle East Systems (AMES)":       None,         # very small, no Wikidata entry
    "Alcoa Warrick":                             None,         # US subsidiary of Alcoa, no standalone entry
    "Comec":                                     None,         # too generic, no clear match
    "Patricomp Oy":                              None,         # small Finnish MRO, no entry
}

# Skip list — definitely no Wikidata entry (very new startups)
NO_ENTRY = {
    "ARX Robotics", "Alpine Eagle", "Alta Ares", "Arondite", "C2Grid",
    "Comand AI", "Destinus", "Helsing", "ICEYE", "Intelic",
    "Nordic Air Defence", "Origin Robotics", "Quantum Systems",
    "Roark Aerospace", "TEKEVER", "Unmanned Defense Systems", "XRF.ai",
    "KoBold Metals", "Delian Alliance Industries",
}

def api_get(params):
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "infonodes/2.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode())

def search_wikidata(query, limit=3):
    data = api_get({"action": "wbsearchentities", "search": query,
                    "language": "en", "limit": limit, "type": "item"})
    return data.get("search", [])

def batch_entities(qids, props="labels|descriptions|aliases|claims|sitelinks"):
    data = api_get({"action": "wbgetentities", "ids": "|".join(qids),
                    "languages": "en", "props": props})
    return data.get("entities", {})

def resolve_item_labels(qids):
    result = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i+50]
        ents = batch_entities(chunk, props="labels")
        for qid, ent in ents.items():
            lbl = ent.get("labels", {}).get("en", {}).get("value")
            if lbl: result[qid] = lbl
        if i + 50 < len(qids): time.sleep(DELAY)
    return result

def extract_claim_value(snak, item_labels):
    sv = snak.get("datavalue", {})
    vtype, value = sv.get("type"), sv.get("value")
    if vtype == "wikibase-entityid":
        qid = value.get("id"); return item_labels.get(qid, qid)
    if vtype == "time":
        raw = value.get("time", "")
        m = re.match(r"^\+?(\d{4})-(\d{2})-(\d{2})", raw)
        if m:
            y,mo,d = m.group(1),m.group(2),m.group(3)
            if mo=="00": return y
            if d=="00": return f"{y}-{mo}"
            return f"{y}-{mo}-{d}"
        return raw
    if vtype == "string": return str(value)
    if vtype == "monolingualtext": return value.get("text")
    if vtype == "quantity":
        amt = value.get("amount","").lstrip("+")
        try: return int(float(amt))
        except: return amt
    return None

def get_best(claims, pid, item_labels):
    stmts = claims.get(pid, [])
    active = [s for s in stmts if s.get("rank")=="preferred"] or \
             [s for s in stmts if s.get("rank")=="normal"]
    vals = []
    for s in active:
        snak = s.get("mainsnak",{})
        if snak.get("snaktype") != "value": continue
        v = extract_claim_value(snak, item_labels)
        if v is not None: vals.append(v)
    if not vals: return None
    return vals if pid == "P31" else vals[0]

def parse_entity(ent, item_labels):
    claims = ent.get("claims",{}); sl = ent.get("sitelinks",{})
    lbl = ent.get("labels",{}).get("en",{}).get("value")
    desc = ent.get("descriptions",{}).get("en",{}).get("value")
    aliases = [a["value"] for a in ent.get("aliases",{}).get("en",[])]
    enwiki = sl.get("enwiki",{}); wt = enwiki.get("title")
    wp = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(wt)}" if wt else None
    return {
        "retrieved_at": TODAY, "label": lbl, "description": desc, "aliases": aliases,
        "instance_of":  get_best(claims,"P31",item_labels),
        "country":      get_best(claims,"P17",item_labels),
        "inception":    get_best(claims,"P571",item_labels),
        "headquarters": get_best(claims,"P159",item_labels),
        "official_website": get_best(claims,"P856",item_labels),
        "isin":         get_best(claims,"P946",item_labels),
        "employees":    get_best(claims,"P1128",item_labels),
        "wikipedia_url": wp,
    }

def auto_search(name):
    """Search Wikidata; return (qid, label, desc) or None."""
    results = search_wikidata(name, limit=3)
    if not results: return None
    top = results[0]
    top_label = top.get("label","").lower()
    top_desc  = top.get("description","").lower()
    name_lower = name.lower()
    # Accept if label closely matches search name
    words = [w for w in name_lower.split() if len(w) > 2]
    match_score = sum(1 for w in words if w in top_label)
    if match_score >= max(1, len(words) - 1):
        return top["id"], top.get("label",""), top.get("description","")
    return None

def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    missing = [e for e in db["entities"]
               if e.get("type") == "company" and not e.get("wikidata_id")]
    print(f"Companies missing wikidata_id: {len(missing)}\n")

    assigned = {}   # entity name → qid
    skipped  = []

    for entity in missing:
        name = entity["name"]

        # 1. Override table
        if name in OVERRIDES:
            qid = OVERRIDES[name]
            if qid is None:
                print(f"  - {name}: no Wikidata entry (manual override)")
                skipped.append(name)
            else:
                print(f"  ↑ {name}: {qid} (override)")
                assigned[name] = qid
            time.sleep(0.05)
            continue

        # 2. Known no-entry startups
        if name in NO_ENTRY:
            print(f"  ○ {name}: startup, likely no Wikidata entry yet")
            skipped.append(name)
            continue

        # 3. Auto-search
        time.sleep(DELAY)
        result = auto_search(name)
        if result:
            qid, label, desc = result
            print(f"  ✓ {name}: {qid} → \"{label}\" ({desc[:50]})")
            assigned[name] = qid
        else:
            print(f"  ? {name}: no confident match found")
            skipped.append(name)

    print(f"\nAssigned: {len(assigned)}  |  Skipped: {len(skipped)}")

    if not assigned:
        print("Nothing to apply.")
        return

    # Apply QIDs to entities
    for entity in db["entities"]:
        name = entity["name"]
        if name not in assigned: continue
        qid = assigned[name]
        entity["wikidata_id"] = qid
        entity["history"].append({
            "date": TODAY, "source": "search_missing_qids.py",
            "author": "search_missing_qids.py", "field": "wikidata_id",
            "old": None, "new": qid,
            "description": "wikidata_id found via Wikidata search API",
        })
        entity["validation"].append({
            "status": "needs_review",
            "description": f"wikidata_id {qid} auto-assigned via search — verify correct entity",
            "author": "search_missing_qids.py", "datestamp": TODAY,
        })

    # Enrich newly assigned entities
    new_entities = [e for e in db["entities"]
                    if e.get("type")=="company" and e["name"] in assigned]
    new_qids = [e["wikidata_id"] for e in new_entities]
    print(f"\nFetching Wikidata for {len(new_qids)} new entities...")

    raw = {}
    for i in range(0, len(new_qids), 50):
        chunk = new_qids[i:i+50]
        raw.update(batch_entities(chunk))
        if i+50 < len(new_qids): time.sleep(DELAY)

    item_qids = set()
    for ent in raw.values():
        for pid in ("P31","P17","P159"):
            for stmt in ent.get("claims",{}).get(pid,[]):
                sv = stmt.get("mainsnak",{}).get("datavalue",{})
                if sv.get("type")=="wikibase-entityid":
                    q = sv.get("value",{}).get("id")
                    if q: item_qids.add(q)

    item_labels = resolve_item_labels(list(item_qids))

    enriched = 0
    for entity in new_entities:
        qid = entity["wikidata_id"]
        r = raw.get(qid)
        if not r or r.get("missing"):
            print(f"  ✗ {entity['name']} ({qid}): not on Wikidata")
            continue
        entity["sources"]["wikidata"] = parse_entity(r, item_labels)
        enriched += 1

    db["_updated"] = TODAY
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Applied {len(assigned)} QIDs, enriched {enriched}.")
    if skipped:
        print(f"\nStill missing ({len(skipped)}):")
        for n in skipped: print(f"  - {n}")

if __name__ == "__main__":
    main()
