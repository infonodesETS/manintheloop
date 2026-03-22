#!/usr/bin/env python3
"""
enrich_wikidata.py — Fetches Wikidata API data for all company entities with a confirmed
wikidata_id and populates sources.wikidata in database.json.

Wikidata properties extracted:
  P31  instance of       → list[str]
  P17  country           → str
  P571 inception date    → str (YYYY-MM-DD)
  P159 headquarters      → str
  P856 official website  → str
  P946 ISIN              → str
  P1128 employees        → int
  sitelinks.enwiki       → wikipedia_url str

Uses the Wikidata wbgetentities API (batches of 50).
Adds a 0.5 s delay between batches to be respectful of rate limits.
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
BATCH_SIZE = 50
DELAY = 0.5  # seconds between batches

# Properties to fetch
PROPS = {
    "P31":  "instance_of",     # item
    "P17":  "country",         # item
    "P571": "inception",       # time
    "P159": "headquarters",    # item
    "P856": "official_website",# url / string
    "P946": "isin",            # string
    "P1128":"employees",       # quantity
}


def api_get(params: dict) -> dict:
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "infonodes-migrate/2.0 (research)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def batch_entities(qids: list[str], props: str = "labels|descriptions|aliases|claims|sitelinks") -> dict:
    """Fetch a batch of up to 50 QIDs from Wikidata. Returns entities dict."""
    data = api_get({
        "action": "wbgetentities",
        "ids": "|".join(qids),
        "languages": "en",
        "props": props,
    })
    return data.get("entities", {})


def resolve_item_labels(qids: list[str]) -> dict[str, str]:
    """Resolve a list of QIDs to their English labels. Returns {qid: label}."""
    if not qids:
        return {}
    result = {}
    for i in range(0, len(qids), BATCH_SIZE):
        chunk = qids[i:i + BATCH_SIZE]
        entities = batch_entities(chunk, props="labels")
        for qid, ent in entities.items():
            label = ent.get("labels", {}).get("en", {}).get("value")
            if label:
                result[qid] = label
        if i + BATCH_SIZE < len(qids):
            time.sleep(DELAY)
    return result


def extract_claim_value(snak: dict, item_labels: dict) -> str | int | None:
    """Extract a human-readable value from a claim snak."""
    sv = snak.get("datavalue", {})
    vtype = sv.get("type")
    value = sv.get("value")

    if vtype == "wikibase-entityid":
        qid = value.get("id")
        return item_labels.get(qid, qid)  # fallback to QID if label not resolved

    if vtype == "time":
        raw = value.get("time", "")
        # Format: +YYYY-MM-DDT00:00:00Z  (precision varies)
        m = re.match(r"^\+?(\d{4})-(\d{2})-(\d{2})", raw)
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            if mo == "00":
                return y
            if d == "00":
                return f"{y}-{mo}"
            return f"{y}-{mo}-{d}"
        return raw

    if vtype == "string":
        return str(value)

    if vtype == "monolingualtext":
        return value.get("text")

    if vtype == "quantity":
        amount = value.get("amount", "").lstrip("+")
        try:
            return int(float(amount))
        except (ValueError, TypeError):
            return amount

    if vtype == "globecoordinate":
        return None  # skip

    return None


def get_best_claim_value(claims: dict, pid: str, item_labels: dict) -> str | int | list | None:
    """Get best-rank claim value(s) for a property."""
    stmts = claims.get(pid, [])
    if not stmts:
        return None

    # Filter to preferred rank, then normal
    preferred = [s for s in stmts if s.get("rank") == "preferred"]
    normal    = [s for s in stmts if s.get("rank") == "normal"]
    active    = preferred or normal

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
    # P31 (instance_of) → return list; others → return first
    if pid == "P31":
        return values
    return values[0]


def parse_entity(ent: dict, item_labels: dict) -> dict:
    """Build the sources.wikidata dict from a raw Wikidata entity."""
    claims = ent.get("claims", {})
    sitelinks = ent.get("sitelinks", {})

    label       = ent.get("labels", {}).get("en", {}).get("value")
    description = ent.get("descriptions", {}).get("en", {}).get("value")
    aliases_raw = ent.get("aliases", {}).get("en", [])
    aliases     = [a["value"] for a in aliases_raw]

    # sitelinks
    enwiki = sitelinks.get("enwiki", {})
    wiki_title = enwiki.get("title")
    wikipedia_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(wiki_title)}" if wiki_title else None

    result = {
        "retrieved_at": TODAY,
        "label": label,
        "description": description,
        "aliases": aliases,
        "instance_of": get_best_claim_value(claims, "P31", item_labels),
        "country": get_best_claim_value(claims, "P17", item_labels),
        "inception": get_best_claim_value(claims, "P571", item_labels),
        "headquarters": get_best_claim_value(claims, "P159", item_labels),
        "official_website": get_best_claim_value(claims, "P856", item_labels),
        "isin": get_best_claim_value(claims, "P946", item_labels),
        "employees": get_best_claim_value(claims, "P1128", item_labels),
        "wikipedia_url": wikipedia_url,
    }
    return result


def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    # Collect all company entities that have a wikidata_id
    targets = [
        e for e in db["entities"]
        if e.get("type") == "company" and e.get("wikidata_id")
    ]
    print(f"Entities to enrich: {len(targets)}")

    qids = [e["wikidata_id"] for e in targets]

    # ── Pass 1: fetch all target entities ─────────────────────────────────────
    print("Fetching entity data from Wikidata...")
    raw_entities: dict[str, dict] = {}
    for i in range(0, len(qids), BATCH_SIZE):
        chunk = qids[i:i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}: {chunk[0]}…{chunk[-1]}")
        try:
            entities = batch_entities(chunk)
            raw_entities.update(entities)
        except Exception as ex:
            print(f"  ERROR fetching batch: {ex}")
        if i + BATCH_SIZE < len(qids):
            time.sleep(DELAY)

    # ── Pass 2: collect all item QIDs needed for label resolution ──────────────
    print("Resolving item labels (P17, P31, P159)...")
    item_qids_needed: set[str] = set()
    for ent in raw_entities.values():
        for pid in ("P31", "P17", "P159"):
            for stmt in ent.get("claims", {}).get(pid, []):
                snak = stmt.get("mainsnak", {})
                sv = snak.get("datavalue", {})
                if sv.get("type") == "wikibase-entityid":
                    qid = sv.get("value", {}).get("id")
                    if qid:
                        item_qids_needed.add(qid)

    item_labels = resolve_item_labels(list(item_qids_needed))
    print(f"  Resolved {len(item_labels)} item labels")

    # ── Pass 3: apply to database ──────────────────────────────────────────────
    print("Applying to database.json...")
    enriched = 0
    failed = 0

    for entity in db["entities"]:
        if entity.get("type") != "company":
            continue
        qid = entity.get("wikidata_id")
        if not qid:
            continue

        raw = raw_entities.get(qid)
        if not raw or raw.get("missing"):
            print(f"  ✗ {entity['name']} ({qid}): not found on Wikidata")
            failed += 1
            continue

        wd_data = parse_entity(raw, item_labels)
        entity["sources"]["wikidata"] = wd_data
        entity["history"].append({
            "date": TODAY,
            "source": "wikidata",
            "author": "enrich_wikidata.py",
            "field": "sources.wikidata",
            "old": None,
            "new": f"Wikidata data retrieved ({qid})",
            "description": f"sources.wikidata populated from Wikidata API ({qid})",
        })
        enriched += 1

    db["_updated"] = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Enriched: {enriched}  |  Failed/missing: {failed}")


if __name__ == "__main__":
    main()
