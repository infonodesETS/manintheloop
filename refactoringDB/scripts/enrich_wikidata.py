#!/usr/bin/env python3
"""
enrich_wikidata.py — Fetch Wikidata API data for entities with a confirmed wikidata_id
and populate sources.wikidata in database.json.

Wikidata properties extracted:
  P31   instance_of      → list[str]  (item labels)
  P17   country          → str        (item label)
  P571  inception        → str        (YYYY, YYYY-MM, or YYYY-MM-DD)
  P159  headquarters     → str        (item label)
  P856  official_website → str        (URL)
  P946  isin             → str
  P1128 employees        → int
  sitelinks.enwiki       → wikipedia_url str

Uses wbgetentities API (batches of 50, 2 s delay between batches).
On HTTP 429: exponential backoff [5, 10, 20] s before retrying the batch.

Usage:
  python3 scripts/enrich_wikidata.py [--dry-run] [--force]

  --dry-run   Fetch from Wikidata and print what would be written; no DB changes.
  --force     Re-enrich entities that already have sources.wikidata populated.
              Without --force, already-enriched entities are skipped.

Safe to re-run without --force: skips entities that already have sources.wikidata.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")

TODAY = date.today().isoformat()
API = "https://www.wikidata.org/w/api.php"
BATCH_SIZE = 50
DELAY = 2.0       # seconds between batches (same as fetch_wikidata_websites.py)
BACKOFF = [5, 10, 20]  # seconds on HTTP 429


# ── API helpers ───────────────────────────────────────────────────────────────

def api_get(params: dict) -> dict:
    """Call Wikidata API with retry on 429. Raises on non-429 errors."""
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": "infonodes-refactoringDB/1.0 (https://github.com/infonodesETS/manintheloop)"
    })
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"    [429] rate limit — waiting {wait}s (attempt {attempt + 1}/{len(BACKOFF) + 1})")
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError(f"All retries exhausted for: {url}")


def fetch_entities(qids: list[str], props: str = "labels|descriptions|aliases|claims|sitelinks") -> dict:
    """Fetch a batch of up to 50 QIDs. Returns raw entities dict."""
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
        entities = fetch_entities(chunk, props="labels")
        for qid, ent in entities.items():
            label = ent.get("labels", {}).get("en", {}).get("value")
            if label:
                result[qid] = label
        if i + BATCH_SIZE < len(qids):
            time.sleep(DELAY)
    return result


# ── Value extraction ──────────────────────────────────────────────────────────

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

    return None  # globecoordinate and others


def get_best_claim_value(claims: dict, pid: str, item_labels: dict):
    """Get best-rank claim value(s) for a property.
    P31 (instance_of) returns a list; all others return the first value or None.
    """
    stmts = claims.get(pid, [])
    if not stmts:
        return None

    preferred = [s for s in stmts if s.get("rank") == "preferred"]
    normal    = [s for s in stmts if s.get("rank") == "normal"]
    active = preferred or normal

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


def parse_entity(ent: dict, item_labels: dict) -> dict:
    """Build the sources.wikidata dict from a raw Wikidata entity."""
    claims   = ent.get("claims", {})
    sitelinks = ent.get("sitelinks", {})

    label       = ent.get("labels", {}).get("en", {}).get("value")
    description = ent.get("descriptions", {}).get("en", {}).get("value")
    aliases     = [a["value"] for a in ent.get("aliases", {}).get("en", [])]

    wiki_title = sitelinks.get("enwiki", {}).get("title")
    wikipedia_url = (
        f"https://en.wikipedia.org/wiki/{urllib.parse.quote(wiki_title)}"
        if wiki_title else None
    )

    return {
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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    force   = "--force"   in sys.argv

    if dry_run:
        print("DRY RUN — no changes will be written to database.json")
    print("=" * 60)

    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    # All entity types (company, institution, government_agency, …) with a wikidata_id
    all_with_qid = [e for e in db["entities"] if e.get("wikidata_id")]

    if force:
        targets = all_with_qid
        print(f"--force: enriching all {len(targets)} entities with wikidata_id")
    else:
        targets = [e for e in all_with_qid if not e.get("sources", {}).get("wikidata")]
        already = len(all_with_qid) - len(targets)
        print(f"Entities with wikidata_id:    {len(all_with_qid)}")
        print(f"  already enriched (skip):   {already}")
        print(f"  to enrich this run:        {len(targets)}")

    if not targets:
        print("\nNothing to do.")
        return

    qids = [e["wikidata_id"] for e in targets]

    # ── Pass 1: fetch all target entities ─────────────────────────────────────
    print(f"\nFetching {len(qids)} entities from Wikidata (batches of {BATCH_SIZE})...")
    raw_entities: dict[str, dict] = {}
    total_batches = (len(qids) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(qids), BATCH_SIZE):
        chunk = qids[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  Batch {batch_num}/{total_batches}: {chunk[0]} … {chunk[-1]}")
        try:
            entities = fetch_entities(chunk)
            raw_entities.update(entities)
        except Exception as ex:
            print(f"  ERROR fetching batch {batch_num}: {ex}")
        if i + BATCH_SIZE < len(qids):
            time.sleep(DELAY)

    # ── Pass 2: collect all item QIDs needed for label resolution ──────────────
    print("\nResolving item labels (P17 country, P31 instance_of, P159 headquarters)...")
    item_qids_needed: set[str] = set()
    for ent in raw_entities.values():
        for pid in ("P31", "P17", "P159"):
            for stmt in ent.get("claims", {}).get(pid, []):
                sv = stmt.get("mainsnak", {}).get("datavalue", {})
                if sv.get("type") == "wikibase-entityid":
                    qid = sv.get("value", {}).get("id")
                    if qid:
                        item_qids_needed.add(qid)

    item_labels = resolve_item_labels(list(item_qids_needed))
    print(f"  Resolved {len(item_labels)} item labels")

    # ── Pass 3: apply to database ──────────────────────────────────────────────
    print("\nApplying to database.json...")
    enriched = 0
    skipped_missing = 0

    entity_map = {e["id"]: e for e in db["entities"]}

    for entity in targets:
        qid = entity["wikidata_id"]
        raw = raw_entities.get(qid)

        if not raw or raw.get("missing"):
            print(f"  ✗ {entity['id']} {entity['name']!r} ({qid}): not found on Wikidata")
            skipped_missing += 1
            continue

        wd_data = parse_entity(raw, item_labels)

        if dry_run:
            print(f"  [dry] {entity['id']} {entity['name']!r} → {qid}")
            print(f"        label={wd_data['label']!r}  country={wd_data['country']!r}"
                  f"  HQ={wd_data['headquarters']!r}  inception={wd_data['inception']!r}")
            enriched += 1
            continue

        entity["sources"]["wikidata"] = wd_data
        entity["history"].append({
            "date": TODAY,
            "source": "wikidata",
            "author": "enrich_wikidata.py",
            "field": "sources.wikidata",
            "old": None,
            "new": f"sources.wikidata populated ({qid})",
            "description": f"Wikidata entity data fetched via wbgetentities API ({qid})",
        })
        entity["validation"].append({
            "status": "wikidata_enriched",
            "description": (
                f"sources.wikidata populated from Wikidata API ({qid}). "
                f"label={wd_data['label']!r}"
            ),
            "author": "enrich_wikidata.py",
            "datestamp": TODAY,
        })
        enriched += 1
        print(f"  ✓ {entity['id']} {entity['name']!r} → {qid}")

    if not dry_run:
        db["_updated"] = TODAY
        with open(DATABASE_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    if dry_run:
        print(f"DRY RUN complete — would enrich: {enriched}  |  not found: {skipped_missing}")
        print("Re-run without --dry-run to apply.")
    else:
        print(f"Enriched: {enriched}  |  not found on Wikidata: {skipped_missing}")
        print(f"Next: python3 scripts/validate.py")


if __name__ == "__main__":
    main()
