"""
fetch_wikidata_websites.py — fetch official website (P856) from Wikidata
for companies that have a wikidata_id but no website in sources.infonodes.

Uses SPARQL VALUES block (lookup by QID — fast, indexed, no false positives).
Batch size 50, 2s delay between batches.

Writes to sources.infonodes.website in database.json.
Appends history entry per UPDATE_PROTOCOL.md.

Run:
    python3 scripts/fetch_wikidata_websites.py [--dry-run]
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "data", "database.json")

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
BATCH_SIZE = 50
DELAY = 2.0
BACKOFF = [5, 10, 20]
TODAY = date.today().isoformat()

# Known bad Wikidata P856 values — wrong URLs stored on Wikidata for these QIDs
# Format: {qid: reason}
SKIP_QID_WEBSITES: dict[str, str] = {
    "Q56404682": "bo-bedre.no is unrelated (Norwegian home magazine); Sichuan Yahua has no P856",
}
DRY_RUN = "--dry-run" in sys.argv


def sparql_get(query: str) -> list[dict]:
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{SPARQL_ENDPOINT}?{params}"
    headers = {"User-Agent": "infonodes-refactoringDB/1.0 (research project)"}
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"  [rate limit] waiting {wait}s...")
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                return data.get("results", {}).get("bindings", [])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError("SPARQL request failed after retries")


def fetch_websites_for_qids(qid_list: list[str]) -> dict[str, str]:
    """Returns {qid: website_url} for QIDs that have P856."""
    values = " ".join(f"wd:{q}" for q in qid_list)
    query = f"""
SELECT ?item ?website WHERE {{
  VALUES ?item {{ {values} }}
  ?item wdt:P856 ?website .
}}
"""
    rows = sparql_get(query)
    result = {}
    for row in rows:
        qid = row["item"]["value"].split("/")[-1]
        url = row["website"]["value"]
        if qid not in result:          # take first if multiple
            result[qid] = url
    return result


def ensure_infonodes(entity: dict) -> dict:
    """Return the infonodes dict, creating it if needed."""
    src = entity.setdefault("sources", {})
    if not isinstance(src.get("infonodes"), dict):
        src["infonodes"] = {
            "extracted_at": TODAY,
            "sector": None,
            "country": None,
            "tax_id": None,
            "main_focus": None,
            "wikipedia_url": None,
            "website": None,
        }
    return src["infonodes"]


def main():
    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)

    companies = [e for e in db["entities"] if e.get("type") == "company"]

    # Collect targets: have wikidata_id, no website anywhere
    targets = []
    for e in companies:
        if not e.get("wikidata_id"):
            continue
        src = e.get("sources", {})
        cb_site = (src.get("crunchbase") or {}).get("website") or ""
        info_site = (src.get("infonodes") or {}).get("website") or ""
        if not cb_site and not info_site:
            targets.append(e)

    print(f"Targets (have QID, no website): {len(targets)}")
    print(f"Batch size: {BATCH_SIZE} | Delay: {DELAY}s")
    print()

    # Build qid → entity map
    qid_to_entity = {e["wikidata_id"]: e for e in targets}
    qid_list = list(qid_to_entity.keys())

    total_batches = (len(qid_list) + BATCH_SIZE - 1) // BATCH_SIZE
    written = 0
    not_found = 0

    for i in range(0, len(qid_list), BATCH_SIZE):
        batch_qids = qid_list[i:i + BATCH_SIZE]
        bn = i // BATCH_SIZE + 1
        print(f"Batch {bn}/{total_batches} ({len(batch_qids)} QIDs)...")

        try:
            found = fetch_websites_for_qids(batch_qids)
        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(DELAY)
            continue

        batch_found = 0
        for qid in batch_qids:
            entity = qid_to_entity[qid]
            url = found.get(qid)
            if not url:
                not_found += 1
                continue
            if qid in SKIP_QID_WEBSITES:
                print(f"  [SKIP] {entity['id']} {entity['name']!r} — {SKIP_QID_WEBSITES[qid]}")
                not_found += 1
                continue

            print(f"  {'[DRY]' if DRY_RUN else ''} {entity['id']} {entity['name']!r} → {url}")

            if not DRY_RUN:
                infonodes = ensure_infonodes(entity)
                old_val = infonodes.get("website")
                infonodes["website"] = url
                infonodes["extracted_at"] = TODAY

                entity.setdefault("history", []).append({
                    "date": TODAY,
                    "source": "wikidata",
                    "author": "fetch_wikidata_websites.py",
                    "field": "sources.infonodes.website",
                    "old": old_val,
                    "new": url,
                    "description": f"Official website (P856) fetched from Wikidata ({qid})",
                })

            written += 1
            batch_found += 1

        print(f"  → found {batch_found}/{len(batch_qids)} in this batch")
        time.sleep(DELAY)

    print()
    print(f"{'[DRY RUN] ' if DRY_RUN else ''}Summary:")
    print(f"  Websites written: {written}")
    print(f"  QIDs with no P856 on Wikidata: {not_found}")

    if not DRY_RUN and written > 0:
        db["_updated"] = TODAY
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\nSaved → {DB_PATH}")
        print("Next: run python3 scripts/validate.py")


if __name__ == "__main__":
    main()
