#!/usr/bin/env python3
"""
patch_iv_countries_p159.py — P159/P17 fallback country lookup for IV entities.

For IV-* entities that have a wikidata_id but sources.wikidata.country = null,
attempts to resolve the country via a single batched SPARQL query per batch:
  - wdt:P17  (country of the organization — direct)
  - wdt:P159/wdt:P17  (country of the headquarters location — fallback)

Both are tried in the same query; P17 wins if present, P159/P17 as fallback.

Usage:
  python3 scripts/patch_iv_countries_p159.py [--dry-run]
"""

import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import date

BASE          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
TODAY         = date.today().isoformat()
DRY_RUN       = "--dry-run" in sys.argv

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT      = "infonodes-refactoringDB/1.0 (https://github.com/infonodesETS/manintheloop)"
DELAY           = 2.0
BACKOFF         = [5, 10, 20]
BATCH_SIZE      = 25


def sparql_query(q: str) -> list[dict]:
    params = urllib.parse.urlencode({"query": q, "format": "json"})
    url    = f"{SPARQL_ENDPOINT}?{params}"
    req    = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"    [429] waiting {wait}s…")
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode()).get("results", {}).get("bindings", [])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError("All retries exhausted")


def batch_lookup(qids: list[str]) -> dict[str, str]:
    """
    Returns {qid: country_label}.
    Priority: direct P17 > P159/P17 fallback.
    If both exist for the same item, P17 wins (first-seen wins per qid).
    """
    values = " ".join(f"wd:{q}" for q in qids)
    # Two OPTIONAL blocks: direct P17 and P159→P17.
    # We SELECT with DISTINCT and take first match per QID in Python.
    query = f"""
SELECT DISTINCT ?item ?countryLabel ?via WHERE {{
  VALUES ?item {{ {values} }}
  {{
    ?item wdt:P17 ?country.
    BIND("direct" AS ?via)
  }} UNION {{
    ?item wdt:P159 ?hq.
    ?hq   wdt:P17 ?country.
    BIND("p159" AS ?via)
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
ORDER BY ?item ?via
"""
    rows    = sparql_query(query)
    results: dict[str, str] = {}
    for row in rows:
        qid     = row["item"]["value"].rsplit("/", 1)[-1]
        country = row.get("countryLabel", {}).get("value")
        via     = row.get("via", {}).get("value", "?")
        if country and qid not in results:
            results[qid] = (country, via)
    return results


def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    def get_country(e):
        src = e.get("sources") or {}
        return (src.get("infonodes") or {}).get("country") or \
               (src.get("wikidata")  or {}).get("country")

    candidates = [
        e for e in db["entities"]
        if e["id"].startswith("IV-")
        and e.get("wikidata_id")
        and not get_country(e)
    ]

    print(f"IV with QID but no country: {len(candidates)}")
    if not candidates:
        print("Nothing to do.")
        return

    patched = 0
    for i in range(0, len(candidates), BATCH_SIZE):
        batch = candidates[i : i + BATCH_SIZE]
        qids  = [e["wikidata_id"] for e in batch]
        n     = i // BATCH_SIZE + 1
        total = (len(candidates) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\nBatch {n}/{total}: {len(qids)} QIDs…", flush=True)
        time.sleep(DELAY)

        try:
            results = batch_lookup(qids)
        except Exception as ex:
            print(f"  SPARQL error: {ex}")
            continue

        for e in batch:
            hit = results.get(e["wikidata_id"])
            label = f"{e['id']}  {e['name']!r}"
            if hit:
                country, via = hit
                print(f"  ✓ {label} → {country}  [{via}]")
                if not DRY_RUN:
                    src = e.setdefault("sources", {})
                    wd  = src.get("wikidata")
                    if not isinstance(wd, dict):
                        wd = {"retrieved_at": TODAY}
                        src["wikidata"] = wd
                    wd["country"] = country
                    e.setdefault("history", []).append({
                        "date":        TODAY,
                        "source":      "wikidata",
                        "author":      "patch_iv_countries_p159.py",
                        "field":       "sources.wikidata.country",
                        "old":         None,
                        "new":         country,
                        "description": f"Country resolved via {via} SPARQL fallback (P159/P17)",
                    })
                patched += 1
            else:
                print(f"  — {label}: not found")

    print(f"\nPatched: {patched}/{len(candidates)}")

    if DRY_RUN:
        print("[DRY RUN] No changes written.")
        return

    db["_updated"] = TODAY
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("DB updated.")


if __name__ == "__main__":
    main()
