#!/usr/bin/env python3
"""
import_investors_crunchbase.py — Create IV-* investor entities and investment
relationships from the crunchbase.top_investors field already present on IN-* entities.

WHAT IT DOES
────────────
  1. Collects all unique investor names from sources.crunchbase.top_investors
     across all IN-* entities.
  2. For each unique name: creates an IV-NNNN entity (skips if already present).
  3. For each IN-* / investor pair: creates an "investment" relationship
     (idempotent — skips if the pair already exists).
  4. Optionally runs a Wikidata SPARQL search to find the QID + HQ country for
     each new investor (--wikidata flag). Results are stored in sources.wikidata
     so the map can draw cross-border arcs.

USAGE
─────
  python3 scripts/import_investors_crunchbase.py [--dry-run] [--wikidata]

  --dry-run   Print what would be done; no DB changes.
  --wikidata  After creating IV entities, search Wikidata for each one to get
              the country/HQ. Adds ~2s delay per investor (rate-limit friendly).
              Skip if you only want the entities/relationships without geo data.

RE-RUN SAFETY
─────────────
  Fully idempotent. Existing IV-* entities and relationships are never duplicated.
  On re-run with --wikidata, only investors without sources.wikidata are looked up
  (use --force-wikidata to re-fetch all).
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

DRY_RUN        = "--dry-run"        in sys.argv
DO_WIKIDATA    = "--wikidata"       in sys.argv
FORCE_WIKIDATA = "--force-wikidata" in sys.argv

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WD_API          = "https://www.wikidata.org/w/api.php"
USER_AGENT      = "infonodes-refactoringDB/1.0 (https://github.com/infonodesETS/manintheloop)"
DELAY           = 2.0   # seconds between Wikidata requests
BACKOFF         = [5, 10, 20]

# Known types for common VC / PE firm keywords → stored in entity.type
_VC_KEYWORDS  = {"ventures", "venture", "capital", "partners", "fund", "equity",
                 "growth", "invest", "asset", "management", "advisors", "advisory"}
_GOV_KEYWORDS = {"bank", "agency", "authority", "government", "ministry",
                 "department", "commission", "bundesbank", "bpifrance"}

# Wikidata descriptions that clearly indicate a non-investor entity.
# Used to reject label matches that pass P31/Q43229 only because Wikidata's
# "organisation" class is broad enough to include restaurants, bands, etc.
_NON_INVESTOR_SIGNALS = frozenset([
    "restaurant",   # e.g. "Restaurant in Dublin, Ireland"
    "hamlet",       # e.g. "hamlet in Berkshire County, Massachusetts"
    "municipality", # e.g. "city and municipality in the Netherlands"
    "parish",       # e.g. "parish of Stapylton County, New South Wales"
    " band",        # e.g. "American Band", "Japanese rock band" (space guards against "broadband")
    "record label", # e.g. "record label"
    "legal entity", # e.g. "legal entity in Latvia" (non-investor holding structure)
])


def investor_type(name: str) -> str:
    low = name.lower()
    words = set(re.split(r"[\s\-&]+", low))
    if words & _GOV_KEYWORDS:
        return "public_fund"
    if words & _VC_KEYWORDS:
        return "fund"
    return "investor"


# ── Wikidata helpers ──────────────────────────────────────────────────────────

def _http_get(url: str, params: dict | None = None, post_data: bytes | None = None) -> dict:
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        data=post_data,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"    [429] rate limit — waiting {wait}s")
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError(f"All retries exhausted: {url}")


def sparql_query(q: str) -> list[dict]:
    data = _http_get(
        SPARQL_ENDPOINT,
        params={"query": q, "format": "json"},
    )
    return data.get("results", {}).get("bindings", [])


def search_investor_wikidata(name: str) -> dict | None:
    """
    Search Wikidata for an investor/fund by name.
    Returns dict with {qid, label, description, country, hq_city} or None.
    """
    # SPARQL: find org with matching label + is-a organisation/company/fund/bank
    q = f"""
SELECT ?item ?itemLabel ?itemDescription ?countryLabel ?hqLabel WHERE {{
  ?item rdfs:label "{name}"@en.
  ?item wdt:P31/wdt:P279* wd:Q43229.
  OPTIONAL {{ ?item wdt:P17 ?country. }}
  OPTIONAL {{ ?item wdt:P159 ?hq. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT 3
"""
    try:
        rows = sparql_query(q)
    except Exception as e:
        print(f"    SPARQL error for '{name}': {e}")
        return None

    if not rows:
        return None

    row = rows[0]
    qid     = row["item"]["value"].rsplit("/", 1)[-1]
    label   = row.get("itemLabel", {}).get("value", name)
    desc    = row.get("itemDescription", {}).get("value", "")
    country = row.get("countryLabel", {}).get("value")
    hq      = row.get("hqLabel", {}).get("value")

    # Reject if description contains a clear non-investor signal.
    # Wikidata Q43229 (organisation) is too broad — it includes restaurants,
    # bands, record labels, and geographic entities that share investor names.
    if desc:
        low = desc.lower()
        for sig in _NON_INVESTOR_SIGNALS:
            if sig in low:
                print(f"    [skipped {qid}] non-investor description: {desc!r}")
                return None

    return {"qid": qid, "label": label, "description": desc, "country": country, "hq": hq}


# ── ID generator ──────────────────────────────────────────────────────────────

def next_iv_id(entities: list[dict]) -> str:
    nums = [int(e["id"].split("-")[1]) for e in entities if e["id"].startswith("IV-")]
    n = max(nums, default=0) + 1
    return f"IV-{n:04d}"


def make_iv_entity(name: str, iv_id: str) -> dict:
    return {
        "id":         iv_id,
        "type":       investor_type(name),
        "roles":      ["investor"],
        "name":       name,
        "sector":     None,
        "wikidata_id": None,
        "sources": {
            "edf":        None,
            "ishares":    None,
            "crunchbase": None,
            "infonodes":  {"extracted_at": TODAY, "sector": None, "country": None,
                           "tax_id": None, "main_focus": None, "wikipedia_url": None, "website": None},
            "wikidata":   None,
        },
        "history": [{
            "date":        TODAY,
            "source":      "crunchbase",
            "author":      "import_investors_crunchbase.py",
            "field":       "*",
            "old":         None,
            "new":         None,
            "description": f"Investor entity created from crunchbase.top_investors reference",
        }],
        "validation": [{
            "status":      "needs_review",
            "description": "Auto-created from Crunchbase top_investors list. Country/HQ pending Wikidata enrichment.",
            "author":      "import_investors_crunchbase.py",
            "datestamp":   TODAY,
        }],
        "tags": [],
    }


def make_relationship(inv_id: str, co_id: str) -> dict:
    return {
        "source":     inv_id,
        "target":     co_id,
        "type":       "investment",
        "source_ref": "crunchbase_top_investors",
        "created_at": TODAY,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    entities      = db["entities"]
    relationships = db["relationships"]

    # Build lookup: name (lowercased) → IV entity
    name_to_iv: dict[str, dict] = {}
    for e in entities:
        if e["id"].startswith("IV-"):
            name_to_iv[e["name"].lower()] = e

    # Build lookup: (inv_id, co_id) → existing relationship
    rel_pairs: set[tuple[str, str]] = {(r["source"], r["target"]) for r in relationships}

    new_entities: list[dict]      = []
    new_relationships: list[dict] = []

    companies_with_investors = [
        e for e in entities
        if e["id"].startswith("IN-") and e.get("sources", {}).get("crunchbase", {}) and
           e["sources"]["crunchbase"].get("top_investors")
    ]

    print(f"Companies with top_investors: {len(companies_with_investors)}")

    # Collect all unique investor names (preserving first-seen casing)
    seen_names: dict[str, str] = {}  # lowercase → canonical name
    for co in companies_with_investors:
        for name in co["sources"]["crunchbase"]["top_investors"]:
            key = name.strip().lower()
            if key and key not in seen_names:
                seen_names[key] = name.strip()

    print(f"Unique investor names: {len(seen_names)}")

    # Create IV entities for new investors
    for key, name in sorted(seen_names.items()):
        if key in name_to_iv:
            continue  # already exists
        iv_id  = next_iv_id(entities + new_entities)
        iv_ent = make_iv_entity(name, iv_id)
        new_entities.append(iv_ent)
        name_to_iv[key] = iv_ent
        entities.append(iv_ent)  # keep next_iv_id consistent

    print(f"New IV entities to create: {len(new_entities)}")

    # Create relationships
    for co in companies_with_investors:
        for name in co["sources"]["crunchbase"]["top_investors"]:
            key    = name.strip().lower()
            iv_ent = name_to_iv.get(key)
            if not iv_ent:
                continue
            pair = (iv_ent["id"], co["id"])
            if pair in rel_pairs:
                continue
            new_relationships.append(make_relationship(iv_ent["id"], co["id"]))
            rel_pairs.add(pair)

    print(f"New relationships to create: {len(new_relationships)}")

    # Wikidata enrichment
    if DO_WIKIDATA:
        to_enrich = [
            e for e in (new_entities if not FORCE_WIKIDATA
                        else [e for e in entities if e["id"].startswith("IV-")])
            if not e.get("wikidata_id") and not (e.get("sources", {}).get("wikidata"))
        ]
        print(f"\nWikidata lookup for {len(to_enrich)} investors (~{len(to_enrich)*2}s)…")
        matched = 0
        for i, iv in enumerate(to_enrich, 1):
            print(f"  [{i}/{len(to_enrich)}] {iv['name']}", end="", flush=True)
            time.sleep(DELAY)
            result = search_investor_wikidata(iv["name"])
            if result:
                iv["wikidata_id"] = result["qid"]
                iv["sources"]["wikidata"] = {
                    "retrieved_at": TODAY,
                    "label":        result["label"],
                    "description":  result["description"],
                    "country":      result["country"],
                    "headquarters": result["hq"],
                    "official_website": None,
                    "isin": None, "employees": None, "wikipedia_url": None,
                    "instance_of": [], "inception": None, "aliases": [],
                }
                iv["history"].append({
                    "date":        TODAY,
                    "source":      "wikidata",
                    "author":      "import_investors_crunchbase.py",
                    "field":       "sources.wikidata",
                    "old":         None,
                    "new":         f"QID {result['qid']}, country={result['country']}",
                    "description": f"Wikidata enrichment via SPARQL label search",
                })
                print(f" → {result['qid']} ({result.get('country', 'no country')})")
                matched += 1
            else:
                print(" → not found")
        print(f"\nWikidata matched: {matched}/{len(to_enrich)}")

    if DRY_RUN:
        print("\n[DRY RUN] No changes written.")
        return

    # Commit (entities list is already mutated in-place via append above)
    db["relationships"] = relationships + new_relationships
    db["_updated"]      = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\nDB updated: +{len(new_entities)} IV entities, +{len(new_relationships)} relationships")


if __name__ == "__main__":
    main()
