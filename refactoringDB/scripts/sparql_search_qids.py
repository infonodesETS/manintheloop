"""
sparql_search_qids.py — Phase 1b: fallback QID search for skipped entities.

Runs after search_missing_qids.py --search. Handles two cases:

  Phase A — label-mismatch entries:
      The Wikidata search API found a result but the label didn't match closely
      enough (e.g. "Taiwan Semiconductor Manufacturing" → "TSMC"). The real
      Wikidata label is embedded in the skip reason. We look it up via SPARQL
      rdfs:label (fast, indexed).

  Phase B — no-results entries:
      The Wikidata search API returned nothing. We use the Wikidata
      reconciliation API (wikidata.reconci.link/en/api) which handles fuzzy
      matching, aliases, and partial names — designed for exactly this task.
      Batches of 20 queries per POST, 2s delay between batches.

Adds new "proposed" entries to data/qid_candidates.json.
Existing entries with status accepted/proposed/rejected are never overwritten.

After running, review qid_candidates.json and run:
    python3 scripts/search_missing_qids.py --apply
"""

import json
import os
import re
import time
import urllib.request
import urllib.parse
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES_PATH = os.path.join(BASE, "data", "qid_candidates.json")

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
RECONCILE_ENDPOINT = "https://wikidata-reconciliation.wmcloud.org/en/api"

TODAY = date.today().isoformat()

DELAY = 2.0          # seconds between API calls / batches
BATCH_SIZE = 20      # queries per reconciliation POST
BACKOFF = [5, 10, 20]

# Minimum reconciliation score to consider a match (0–100)
SCORE_THRESHOLD = 60

# ── Description / type filtering ──────────────────────────────────────────────

ORG_KEYWORDS = {
    "company", "corporation", "firm", "enterprise", "group", "holding",
    "manufacturer", "producer", "supplier", "vendor", "provider",
    "mining", "steel", "metal", "semiconductor", "technology", "aerospace",
    "defence", "defense", "telecommunications", "telecom", "pharmaceutical",
    "bank", "insurance", "conglomerate", "industry", "industries",
    "association", "organization", "organisation", "agency",
    "contractor", "consultancy", "consulting", "software", "hardware",
    "multinational", "listed", "publicly", "exchange", "plc", "inc", "ltd",
    "founded", "headquartered", "subsidiary", "division",
    "robotics", "space", "satellite", "aviation", "shipbuilding",
    "weapons", "ammunition", "electronics", "chemicals", "energy",
    "research", "institute", "laboratory", "centre", "center",
}

DISQUALIFY_KEYWORDS = {
    "city", "town", "village", "municipality", "commune", "region", "province",
    "country", "nation", "state", "island", "ocean", "sea", "lake", "river",
    "mountain", "constellation", "star", "planet", "galaxy",
    "person", "individual", "philosopher", "politician", "artist", "musician",
    "actor", "actress", "author", "writer", "scientist", "athlete",
    "album", "song", "film", "movie", "television", "radio", "newspaper",
    "article", "journal", "magazine", "book", "novel",
    "school", "college", "university", "academic", "education",
    "religion", "church", "temple", "mosque",
    "disease", "disorder", "syndrome", "condition", "medical", "chemical element",
    "fictional", "character",
    "disambiguation",
}

SKIP_LABELS = {
    "American Samoa", "Bose–Einstein condensate", "Capricornus", "Carina",
    "Circumpolar deep water", "Fox Broadcasting Company", "Jade Emperor",
    "go", "Klagenfurt am Wörthersee", "necrotizing enterocolitis",
    "East Nusa Tenggara", "GNU Screen", "Thomas Carlyle", "United States",
    "coagulation factor IX", "assignat", "Muromachi period",
    "self-managed social center", "Inocybe", "Video Games Europe",
    "Wang Zhongli", "Delft University of Technology", "astronaut",
    "artificial intelligence", "Armenian Soviet Encyclopedia",
    "Akhtar Saeed Medical and Dental College", "Kobelco Kobe Steelers",
    "Maybach Music Group", "Eric S. Toberer",
    "Public libraries in the United States survey",
    "New Mexico Digital Collections", "VP-CHB",
}


def description_is_org(description: str) -> tuple[bool, str]:
    if not description:
        return False, "no description"
    low = description.lower()
    disq = next((kw for kw in DISQUALIFY_KEYWORDS if kw in low), None)
    if disq:
        return False, f"disqualified by '{disq}'"
    has_org = any(kw in low for kw in ORG_KEYWORDS)
    if not has_org:
        return False, "no org keyword in description"
    return True, "ok"


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def http_get(url: str) -> dict:
    headers = {"User-Agent": "infonodes-refactoringDB/1.0 (research project)"}
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"  [rate limit] waiting {wait}s ...")
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError("GET request failed after retries")


def http_post(url: str, data: dict) -> dict:
    headers = {
        "User-Agent": "infonodes-refactoringDB/1.0 (research project)",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = urllib.parse.urlencode(data).encode()
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"  [rate limit] waiting {wait}s ...")
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
        except Exception:
            if attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError("POST request failed after retries")


# ── Phase A: SPARQL label lookup for label-mismatch entries ───────────────────

def sparql_label_batch(label_entries: list[dict]) -> list[dict]:
    """Exact rdfs:label lookup via SPARQL for known Wikidata labels."""
    labels = [e["wikidata_label"] for e in label_entries]
    label_to_entity = {e["wikidata_label"]: e for e in label_entries}

    escaped = " ".join(
        f'"{l.replace(chr(34), chr(92)+chr(34))}"@en' for l in labels
    )
    query = f"""
SELECT DISTINCT ?item ?searchLabel ?itemDescription WHERE {{
  VALUES ?searchLabel {{ {escaped} }}
  ?item rdfs:label ?searchLabel .
  OPTIONAL {{ ?item schema:description ?itemDescription .
             FILTER(LANG(?itemDescription) = "en") }}
}}
"""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{SPARQL_ENDPOINT}?{params}"
    resp = http_get(url)
    rows = resp.get("results", {}).get("bindings", [])

    results = []
    seen = set()
    for row in rows:
        qid = row["item"]["value"].split("/")[-1]
        label = row["searchLabel"]["value"]
        description = row.get("itemDescription", {}).get("value", "")

        if label in SKIP_LABELS:
            continue
        entry = label_to_entity.get(label)
        if not entry:
            continue
        is_org, _ = description_is_org(description)
        if not is_org:
            continue
        key = (entry["entity_id"], qid)
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "entity_id": entry["entity_id"],
            "entity_name": entry["entity_name"],
            "search_name": entry["search_name"],
            "wikidata_label": label,
            "qid": qid,
            "description": description,
            "source": "sparql_label",
        })
    return results


# ── Phase B: Reconciliation API for no-results entries ────────────────────────

def reconcile_batch(entries: list[dict]) -> list[dict]:
    """
    POST to Wikidata reconciliation API with up to BATCH_SIZE queries.
    Returns candidates that pass score threshold + description filter.
    """
    queries = {}
    for i, e in enumerate(entries):
        queries[f"q{i}"] = {
            "query": e["search_name"],
            "limit": 3,
        }

    resp = http_post(RECONCILE_ENDPOINT, {"queries": json.dumps(queries)})

    results = []
    seen = set()
    for i, entry in enumerate(entries):
        key = f"q{i}"
        matches = resp.get(key, {}).get("result", [])
        for match in matches:
            score = match.get("score") or 0
            if score < SCORE_THRESHOLD:
                continue
            qid = match.get("id", "")
            if not qid.startswith("Q"):
                continue
            label = match.get("name", "")
            description = match.get("description", "")

            if label in SKIP_LABELS:
                continue
            is_org, reason = description_is_org(description)
            if not is_org:
                continue

            dedup_key = (entry["entity_id"], qid)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            results.append({
                "entity_id": entry["entity_id"],
                "entity_name": entry["entity_name"],
                "search_name": entry["search_name"],
                "wikidata_label": label,
                "qid": qid,
                "description": description,
                "score": score,
                "source": "reconciliation",
            })
    return results


# ── Merge results into candidates file ────────────────────────────────────────

def merge_into_candidates(candidates: list[dict], new_found: list[dict],
                          existing_by_id: dict) -> int:
    added = 0
    for r in new_found:
        eid = r["entity_id"]
        existing = existing_by_id.get(eid)
        if existing and existing["status"] in ("accepted", "proposed", "rejected"):
            continue
        source_note = r.get("source", "sparql")
        score_note = f", score={r['score']}" if "score" in r else ""
        new_entry = {
            "entity_id": eid,
            "entity_name": r["entity_name"],
            "search_name": r["search_name"],
            "status": "proposed",
            "reason": (
                f"found via {source_note}: "
                f"wikidata_label={r['wikidata_label']!r}{score_note}"
            ),
            "qid": r["qid"],
            "label": r["wikidata_label"],
            "description": r["description"],
        }
        if existing:
            idx = next(i for i, c in enumerate(candidates) if c["entity_id"] == eid)
            candidates[idx] = new_entry
        else:
            candidates.append(new_entry)
        existing_by_id[eid] = new_entry
        added += 1
    return added


def save_candidates(data: dict, candidates: list[dict]):
    proposed = sum(1 for c in candidates if c["status"] == "proposed")
    skipped = sum(1 for c in candidates if c["status"] == "skipped")
    data.update({
        "_generated_at": TODAY,
        "_total": len(candidates),
        "_proposed": proposed,
        "_skipped": skipped,
        "candidates": candidates,
    })
    with open(CANDIDATES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    with open(CANDIDATES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    candidates = data["candidates"]
    existing_by_id = {c["entity_id"]: c for c in candidates}

    # ── Collect Phase A targets (label-mismatch) ──────────────────────────────
    label_mismatch_entries = []
    for c in candidates:
        if c["status"] != "skipped":
            continue
        m = re.search(r"label mismatch: '([^']+)' vs '([^']+)'", c.get("reason", ""))
        if not m:
            continue
        wikidata_label = m.group(2)
        if wikidata_label in SKIP_LABELS:
            continue
        label_mismatch_entries.append({
            "entity_id": c["entity_id"],
            "entity_name": c["entity_name"],
            "search_name": c["search_name"],
            "wikidata_label": wikidata_label,
        })

    # ── Collect Phase B targets (no results) ──────────────────────────────────
    no_results_entries = [
        {
            "entity_id": c["entity_id"],
            "entity_name": c["entity_name"],
            "search_name": c["search_name"],
        }
        for c in candidates
        if c["status"] == "skipped"
        and c.get("reason") == "no results from Wikidata search"
        and len(c.get("search_name", "")) >= 5
    ]

    print(f"Phase A — label-mismatch targets: {len(label_mismatch_entries)}")
    print(f"Phase B — no-results targets:     {len(no_results_entries)}")
    print()

    total_added = 0

    # ── Phase A: SPARQL rdfs:label batch ──────────────────────────────────────
    if label_mismatch_entries:
        print("=== Phase A: SPARQL label lookup ===")
        SPARQL_BATCH = 15
        for i in range(0, len(label_mismatch_entries), SPARQL_BATCH):
            batch = label_mismatch_entries[i:i + SPARQL_BATCH]
            bn = i // SPARQL_BATCH + 1
            total_b = (len(label_mismatch_entries) + SPARQL_BATCH - 1) // SPARQL_BATCH
            print(f"  Batch {bn}/{total_b}: {[e['wikidata_label'] for e in batch]}")
            try:
                found = sparql_label_batch(batch)
                for r in found:
                    print(f"    FOUND {r['entity_id']} {r['entity_name']!r} "
                          f"→ {r['qid']} ({r['description'][:60]})")
                added = merge_into_candidates(candidates, found, existing_by_id)
                total_added += added
            except Exception as e:
                print(f"    ERROR: {e}")
            time.sleep(DELAY)

        save_candidates(data, candidates)
        print(f"  [checkpoint saved — Phase A complete]\n")

    # ── Phase B: Reconciliation API ───────────────────────────────────────────
    if no_results_entries:
        print("=== Phase B: Reconciliation API ===")
        total_batches = (len(no_results_entries) + BATCH_SIZE - 1) // BATCH_SIZE
        for i in range(0, len(no_results_entries), BATCH_SIZE):
            batch = no_results_entries[i:i + BATCH_SIZE]
            bn = i // BATCH_SIZE + 1
            names = [e["search_name"] for e in batch]
            print(f"  Batch {bn}/{total_batches}: {names}")
            try:
                found = reconcile_batch(batch)
                for r in found:
                    print(f"    FOUND {r['entity_id']} {r['entity_name']!r} "
                          f"→ {r['qid']} score={r.get('score','?')} "
                          f"({r['description'][:60]})")
                added = merge_into_candidates(candidates, found, existing_by_id)
                total_added += added
            except Exception as e:
                print(f"    ERROR: {e}")

            # Checkpoint every 5 batches
            if bn % 5 == 0:
                save_candidates(data, candidates)
                print(f"  [checkpoint saved — {bn}/{total_batches}]")

            time.sleep(DELAY)

        save_candidates(data, candidates)
        print(f"  [checkpoint saved — Phase B complete]\n")

    # ── Final summary ─────────────────────────────────────────────────────────
    proposed = sum(1 for c in candidates if c["status"] == "proposed")
    skipped = sum(1 for c in candidates if c["status"] == "skipped")

    print(f"{'='*60}")
    print(f"Done.")
    print(f"  New candidates added/upgraded: {total_added}")
    print(f"  Total proposed now:            {proposed}")
    print(f"  Total skipped now:             {skipped}")
    print(f"\nNext: review data/qid_candidates.json, then run:")
    print(f"  python3 scripts/search_missing_qids.py --apply")


if __name__ == "__main__":
    main()
