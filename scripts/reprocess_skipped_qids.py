#!/usr/bin/env python3
"""
reprocess_skipped_qids.py — Second-pass QID recovery for skipped entities.

Runs four strategies in sequence, each feeding the next:

  Phase A — Fix disqualify false positives (0 API calls)
    Re-evaluates skipped entries that have a qid+description but were
    disqualified by substring false positives:
      'nation' matched in 'multinational'
      'state'  matched in 'United States', 'real estate'
      'sea'    matched in 'research'
      'actor'  matched in 'contractor'
    Also: 'video game' removed from disqualify list (it's an industry).
    Uses word-boundary regex for these ambiguous keywords.

  Phase B — P856 website reverse lookup (SPARQL)
    672 of the 694 missing-QID companies have a known website.
    Queries Wikidata for entities with matching wdt:P856 values.
    Bypasses name matching — URL is a strong identifier.
    Batches of 50 entities (≤8 URL variants each) per SPARQL query.

  Phase C — P31 type confirmation for no-description entries (SPARQL)
    64 entries already have matching QID+label but no English description,
    so description_is_org() returned False. Fetches wdt:P31 (instance of)
    for each QID; if any is a known company/business type → proposed.
    Batches of 30 QIDs per SPARQL query.

  Phase D — Results[1–4] re-search for wrong-top-result entries (Wikidata API)
    57 entries were skipped because results[0] had a wrong description.
    Re-searches using the original entity name (not the pre-stripped search_name,
    which strips industry terms like 'GOLD AND SILVER' and 'RARE EARTHS').
    Checks all 5 results with the fixed description filter.

  Phase E — Wikipedia API search (English Wikipedia → Wikidata QID)
    Targets skipped entries with "no results from Wikidata search" — especially
    iShares names truncated to ~35 chars (e.g. 'China Nonferrous Mining Corporatio').
    Two-step: (1) search en.wikipedia.org for the entity name, (2) resolve each
    Wikipedia article to its Wikidata QID via prop=pageprops&wikibase_item.
    Then fetches Wikidata label+description and applies the same label-match +
    org-keyword filter as all other phases.
    Batches pageprops and wbgetentities calls to reduce API round-trips.
    Delay: 1.5s per Wikipedia search (same as Wikidata search API).

Safety guarantees (same as original pipeline):
  - Never overwrites accepted/rejected/proposed entries.
  - No writes to database.json — output is qid_candidates.json only.
  - Human review gate before any DB write.
  - Rate limiting: 2s delay for SPARQL, 1.5s for Wikidata API.
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
CANDIDATES_PATH = os.path.join(BASE, "data", "qid_candidates.json")

TODAY = date.today().isoformat()
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WD_API = "https://www.wikidata.org/w/api.php"

SPARQL_DELAY = 2.0
SEARCH_DELAY = 1.5
WP_DELAY = 1.5       # delay between Wikipedia search API calls
BACKOFF = [5, 10, 20]

SPARQL_BATCH = 30    # QIDs or entity-groups per SPARQL query
P856_BATCH = 10      # entities per P856 query (up to 10 URL variants each → ~100 URIs, safe for SPARQL)
SEARCH_LIMIT = 5     # results to fetch from Wikidata search API
WP_SEARCH_LIMIT = 5  # Wikipedia articles to fetch per entity
WP_API = "https://en.wikipedia.org/w/api.php"


# ── Fixed disqualify / org-keyword logic ──────────────────────────────────────

# Must use WORD-BOUNDARY matching to avoid false positives:
#   'nation' in 'multinational', 'state' in 'United States'/'real estate',
#   'sea' in 'research', 'actor' in 'contractor'
_WORD_DISQUALIFY = frozenset({"nation", "state", "sea", "actor", "region"})

# Safe to match as substrings (unambiguous — don't appear inside other words)
_SUB_DISQUALIFY = frozenset({
    "city", "town", "village", "municipality", "commune", "district",
    "province", "county", "country",
    "person", "politician", "athlete", "musician", "actress",
    "author", "writer", "scientist",
    "river", "mountain", "lake", "island", "ocean",
    "constellation", "asteroid", "planet", "star",
    "article", "journal", "magazine", "newspaper", "publication",
    "album", "song", "film", "television", "radio",
    "school", "university", "college",
    "religion", "church", "temple", "mosque",
    "disease", "disorder", "syndrome", "chemical element",
    "fictional", "character", "disambiguation",
    # NOTE: 'video game' intentionally omitted — 'video game company' is a
    # valid org type (EA, Konami, Take-Two are all companies).
})

_ORG_KEYWORDS = frozenset({
    "company", "corporation", "firm", "enterprise", "group", "holding",
    "manufacturer", "producer", "supplier", "vendor", "provider",
    "mining", "technology", "technologies", "semiconductor",
    "telecommunications", "telecom", "aerospace", "defence", "defense",
    "airline", "bank", "insurer", "insurance", "fund", "investment",
    "retailer", "distributor", "operator", "conglomerate",
    "contractor",              # covers 'oil and gas contractor', 'defense contractor'
    "institute", "laboratory", # consistent with sparql_search_qids.py
    "multinational", "listed", "publicly",
    "founded", "headquartered", "subsidiary", "division",
    "société", "empresa", "gesellschaft", "konzern",
    # NOTE: 'game'/'gaming'/'marketplace'/'platform' intentionally omitted —
    # too broad; 'video game company' already passes via 'company'.
})

# Known Wikidata P31 values that confirm a company/business type
_COMPANY_P31 = frozenset({
    "Q4830453",   # business
    "Q783794",    # company
    "Q6881511",   # enterprise
    "Q891723",    # public company
    "Q2085381",   # holding company
    "Q134161",    # joint-stock company
    "Q17917956",  # joint venture
    "Q1778805",   # limited company
    "Q167037",    # corporation
    "Q1616075",   # industrial enterprise
    "Q740752",    # business group
    "Q219577",    # holding company (alt)
    "Q190227",    # subsidiary
    "Q1288519",   # limited liability company
    "Q2361776",   # public limited company
    "Q4176306",   # startup company
    "Q1149776",   # joint venture (alt)
    "Q2624811",   # publicly traded company
    "Q163740",    # nonprofit organization (broad)
    "Q43229",     # organization (broad — accept with note)
    "Q2608215",   # organization (alt)
})

# P31 values that definitively rule out a company
_NON_COMPANY_P31 = frozenset({
    "Q5",         # human
    "Q515",       # city
    "Q6256",      # country
    "Q7930989",   # city/municipality
    "Q3957",      # town
    "Q532",       # village
    "Q1549591",   # big city
    "Q3624078",   # sovereign state
    "Q23442",     # island
    "Q46831",     # mountain range
    "Q35509",     # river
    "Q8502",      # mountain
    "Q16521",     # taxon (biological)
    "Q11424",     # film
    "Q482994",    # album
    "Q7275",      # political party (keep out — not the same as a company)
})


def description_is_org_fixed(description: str) -> tuple[bool, str]:
    """
    Improved version with word-boundary matching for ambiguous disqualify keywords.
    Returns (is_org, reason).
    """
    if not description:
        return False, "no description"
    d = description.lower()

    for kw in _WORD_DISQUALIFY:
        if re.search(r"\b" + re.escape(kw) + r"\b", d):
            return False, f"disqualified by '{kw}'"

    disq = next((kw for kw in _SUB_DISQUALIFY if kw in d), None)
    if disq:
        return False, f"disqualified by '{disq}'"

    org = next((kw for kw in _ORG_KEYWORDS if kw in d), None)
    if org:
        return True, f"org keyword '{org}'"
    return False, "no org keyword in description"


# ── Label matching (from original script) ────────────────────────────────────

def normalize_label(s: str) -> str:
    s = s.lower()
    s = s.replace("&", " and ")   # treat & and 'and' as equivalent
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def label_matches(search_name: str, result_label: str) -> bool:
    s = normalize_label(search_name)
    r = normalize_label(result_label)
    if not s or len(s) < 3:
        return False
    if s == r:
        return True
    if r.startswith(s) and len(s) >= 4:
        return True
    if s.startswith(r) and len(r) >= 4:
        return True
    return False


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def _ua_headers() -> dict:
    return {"User-Agent": "infonodes-refactoringDB/1.0 (https://github.com/infonodesETS/manintheloop)"}


def http_get(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers=_ua_headers())
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"  [rate limit] waiting {wait}s ...")
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError(f"GET failed after retries: {url[:80]}")


def sparql_query(query: str) -> list[dict]:
    """Execute a SPARQL query and return bindings list."""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{SPARQL_ENDPOINT}?{params}"
    resp = http_get(url, timeout=30)
    return resp.get("results", {}).get("bindings", [])


def wikidata_search(query: str, limit: int = SEARCH_LIMIT) -> list[dict]:
    """Call Wikidata wbsearchentities. Returns list of result dicts."""
    time.sleep(SEARCH_DELAY)
    params = urllib.parse.urlencode({
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": limit,
        "type": "item",
        "format": "json",
    })
    resp = http_get(f"{WD_API}?{params}", timeout=15)
    return resp.get("search", [])


# ── Candidates I/O ────────────────────────────────────────────────────────────

def load_candidates() -> tuple[dict, list[dict], dict[str, dict]]:
    """Returns (raw_data, candidates_list, candidates_by_entity_id)."""
    with open(CANDIDATES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    candidates = data["candidates"]
    by_id = {c["entity_id"]: c for c in candidates}
    return data, candidates, by_id


def save_candidates(data: dict, candidates: list[dict], label: str = ""):
    proposed = sum(1 for c in candidates if c["status"] == "proposed")
    skipped = sum(1 for c in candidates if c["status"] == "skipped")
    accepted = sum(1 for c in candidates if c["status"] == "accepted")
    rejected = sum(1 for c in candidates if c["status"] == "rejected")
    data.update({
        "_generated_at": TODAY,
        "_total": len(candidates),
        "_proposed": proposed,
        "_skipped": skipped,
        "candidates": candidates,
    })
    with open(CANDIDATES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tag = f" [{label}]" if label else ""
    print(f"  [saved{tag}] proposed={proposed} skipped={skipped} "
          f"accepted={accepted} rejected={rejected}")


def upgrade_to_proposed(candidates: list[dict], by_id: dict[str, dict],
                         entry: dict, qid: str, label: str, description: str,
                         reason: str) -> bool:
    """
    Upgrade or insert a candidate as proposed. Returns True if changed.
    Never downgrades accepted/rejected/proposed entries.
    """
    eid = entry["entity_id"]
    existing = by_id.get(eid)
    if existing and existing["status"] in ("accepted", "proposed", "rejected"):
        return False

    new_entry = {
        "entity_id": eid,
        "entity_name": entry["entity_name"],
        "search_name": entry.get("search_name", entry["entity_name"]),
        "status": "proposed",
        "reason": reason,
        "qid": qid,
        "label": label,
        "description": description,
    }
    if existing:
        idx = next(i for i, c in enumerate(candidates) if c["entity_id"] == eid)
        candidates[idx] = new_entry
    else:
        candidates.append(new_entry)
    by_id[eid] = new_entry
    return True


# ── Phase A: Fix disqualify false positives ───────────────────────────────────

def phase_a(candidates: list[dict], by_id: dict[str, dict]) -> int:
    """
    Re-evaluate skipped entries that have a stored QID+description using the
    fixed description_is_org_fixed() function. Upgrades passing entries to
    proposed.
    """
    print("\n=== Phase A: Fix disqualify false positives (0 API calls) ===")

    upgraded = 0
    for c in list(candidates):
        if c["status"] != "skipped":
            continue
        qid = c.get("qid")
        description = c.get("description") or ""
        label = c.get("label") or ""
        if not qid or not description:
            continue

        # Re-run with fixed filter
        is_org, org_reason = description_is_org_fixed(description)
        # Label must still match (already confirmed by original script or
        # this is a label-mismatch entry — accept both)
        search_name = c.get("search_name", c["entity_name"])
        lm = label_matches(search_name, label)

        old_reason = c.get("reason", "")
        was_disqualify = old_reason.startswith("disqualified by")
        was_no_org = old_reason == "no org keyword in description"

        if is_org and (lm or was_disqualify or was_no_org):
            reason = f"reprocessed: {org_reason} (was: {old_reason})"
            if upgrade_to_proposed(candidates, by_id, c, qid, label,
                                   description, reason):
                print(f"  UPGRADE  {c['entity_id']} {c['entity_name']!r}")
                print(f"           was: {old_reason}")
                print(f"           now: {org_reason} | label={label!r}")
                upgraded += 1

    print(f"\n  Phase A: {upgraded} entries upgraded to proposed.")
    return upgraded


# ── Phase B: P856 website reverse lookup ─────────────────────────────────────

def url_variants(url: str) -> list[str]:
    """Generate canonical URL variants for P856 SPARQL matching."""
    url = url.strip()
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return [url]

    domain = parsed.netloc.lower()
    # Strip path to homepage only (P856 typically stores the root URL),
    # and drop any query params or fragments
    path = parsed.path.rstrip("/")

    # Domain: with/without www
    domains = [domain]
    if domain.startswith("www."):
        domains.append(domain[4:])
    elif domain:
        domains.append("www." + domain)

    variants = set()
    for scheme in ("https", "http"):
        for d in domains:
            # Both homepage (path="") and original path, with/without trailing slash
            for p in ("", path) if path else ("",):
                variants.add(f"{scheme}://{d}{p}")
                variants.add(f"{scheme}://{d}{p}/")

    # Always include the original (in case it has a meaningful path like /en/)
    variants.add(url)
    variants.add(url.rstrip("/"))
    return list(variants)


def _get_website(entity: dict) -> str:
    src = entity.get("sources", {})
    return (
        ((src.get("crunchbase") or {}).get("website") or "")
        or ((src.get("infonodes") or {}).get("website") or "")
    )


def phase_b(candidates: list[dict], by_id: dict[str, dict],
            data: dict) -> int:
    """
    For each company still missing a proposed QID, look up its website via
    Wikidata wdt:P856 (official website) using SPARQL.
    """
    print("\n=== Phase B: P856 website reverse lookup (SPARQL) ===")

    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    # Build map: entity_id → website, only for entities still skipped/unresolved
    still_missing = []
    for e in db["entities"]:
        if e.get("type") != "company" or e.get("wikidata_id"):
            continue
        eid = e["id"]
        existing = by_id.get(eid)
        if existing and existing["status"] in ("accepted", "proposed", "rejected"):
            continue
        site = _get_website(e)
        if not site:
            continue
        still_missing.append({
            "entity_id": eid,
            "entity_name": e["name"],
            "search_name": e["name"],
            "website": site,
        })

    print(f"  Entities with website, still needing QID: {len(still_missing)}")

    # Build reverse map: normalized_url → entity (first occurrence wins)
    url_to_entity: dict[str, dict] = {}
    for entry in still_missing:
        for v in url_variants(entry["website"]):
            if v not in url_to_entity:
                url_to_entity[v] = entry

    total_found = 0
    total_batches = (len(still_missing) + P856_BATCH - 1) // P856_BATCH

    for batch_num, i in enumerate(range(0, len(still_missing), P856_BATCH), 1):
        batch = still_missing[i : i + P856_BATCH]

        # Collect all URL variants for this batch
        batch_variants: list[str] = []
        for entry in batch:
            batch_variants.extend(url_variants(entry["website"]))
        # Deduplicate while preserving order
        seen_uris: set[str] = set()
        unique_variants = []
        for v in batch_variants:
            if v not in seen_uris:
                seen_uris.add(v)
                unique_variants.append(v)

        # Build SPARQL VALUES clause — angle-bracket URI format
        values_str = " ".join(f"<{v}>" for v in unique_variants)
        query = f"""
SELECT DISTINCT ?item ?url ?itemLabel ?itemDescription WHERE {{
  VALUES ?url {{ {values_str} }}
  ?item wdt:P856 ?url .
  OPTIONAL {{
    ?item rdfs:label ?itemLabel .
    FILTER(LANG(?itemLabel) = "en")
  }}
  OPTIONAL {{
    ?item schema:description ?itemDescription .
    FILTER(LANG(?itemDescription) = "en")
  }}
}}
"""
        print(f"  Batch {batch_num}/{total_batches}: "
              f"{len(batch)} entities, {len(unique_variants)} URL variants")
        try:
            time.sleep(SPARQL_DELAY)
            rows = sparql_query(query)
        except Exception as e:
            print(f"    SPARQL error: {e}")
            continue

        for row in rows:
            qid = row["item"]["value"].split("/")[-1]
            url = row["url"]["value"]
            label = row.get("itemLabel", {}).get("value", "")
            description = row.get("itemDescription", {}).get("value", "")

            # Map URL back to entity
            entry = url_to_entity.get(url)
            if not entry:
                # Try stripped trailing slash variant
                entry = url_to_entity.get(url.rstrip("/"))
            if not entry:
                continue

            # Sanity check: if description available, it must not be disqualified
            if description:
                is_org, org_reason = description_is_org_fixed(description)
                if not is_org:
                    # Check if it's an outright non-org (human, city, etc.)
                    reason_str = f"P856 match, but description filtered: {org_reason}"
                    print(f"    SKIP  {entry['entity_id']} {entry['entity_name']!r} "
                          f"→ {qid} ({description[:60]!r})")
                    continue
                reason = f"P856 website match ({entry['website']}) + {org_reason}"
            else:
                reason = f"P856 website match ({entry['website']}) — no description"

            if upgrade_to_proposed(candidates, by_id, entry, qid, label,
                                   description, reason):
                print(f"    FOUND {entry['entity_id']} {entry['entity_name']!r} "
                      f"→ {qid} label={label!r} ({description[:50]!r})")
                total_found += 1

        # Checkpoint every 5 batches
        if batch_num % 5 == 0:
            save_candidates(data, candidates, f"Phase B batch {batch_num}")

    save_candidates(data, candidates, "Phase B complete")
    print(f"\n  Phase B: {total_found} new proposals from P856 lookup.")
    return total_found


# ── Phase C: P31 type confirmation for no-description entries ─────────────────

def phase_c(candidates: list[dict], by_id: dict[str, dict],
            data: dict) -> int:
    """
    For skipped entries that have a matching QID+label but no English description,
    fetch wdt:P31 (instance of) to confirm they are a company/business type.
    """
    print("\n=== Phase C: P31 type confirmation for no-description entries (SPARQL) ===")

    targets = [
        c for c in candidates
        if c["status"] == "skipped"
        and c.get("reason") == "no description"
        and c.get("qid")
        and c.get("label")
    ]
    print(f"  No-description targets: {len(targets)}")

    total_found = 0
    total_batches = (len(targets) + SPARQL_BATCH - 1) // SPARQL_BATCH

    for batch_num, i in enumerate(range(0, len(targets), SPARQL_BATCH), 1):
        batch = targets[i : i + SPARQL_BATCH]
        qids = [c["qid"] for c in batch]
        qid_to_candidate = {c["qid"]: c for c in batch}

        values_str = " ".join(f"wd:{q}" for q in qids)
        query = f"""
SELECT ?item ?instanceOf WHERE {{
  VALUES ?item {{ {values_str} }}
  ?item wdt:P31 ?instanceOf .
}}
"""
        print(f"  Batch {batch_num}/{total_batches}: {len(batch)} QIDs")
        try:
            time.sleep(SPARQL_DELAY)
            rows = sparql_query(query)
        except Exception as e:
            print(f"    SPARQL error: {e}")
            continue

        # Collect P31 values per QID
        p31_by_qid: dict[str, list[str]] = {}
        for row in rows:
            qid = row["item"]["value"].split("/")[-1]
            p31 = row["instanceOf"]["value"].split("/")[-1]
            p31_by_qid.setdefault(qid, []).append(p31)

        for qid, p31_values in p31_by_qid.items():
            c = qid_to_candidate.get(qid)
            if not c:
                continue

            is_company = any(p in _COMPANY_P31 for p in p31_values)
            is_non_company = any(p in _NON_COMPANY_P31 for p in p31_values)

            if is_non_company:
                print(f"    SKIP  {c['entity_id']} {c['entity_name']!r} "
                      f"→ non-company P31: {p31_values}")
                continue

            if is_company:
                matched_type = next(p for p in p31_values if p in _COMPANY_P31)
                reason = f"no-description QID confirmed via P31={matched_type} (label match)"
                if upgrade_to_proposed(candidates, by_id, c, qid, c["label"],
                                       "", reason):
                    print(f"    FOUND {c['entity_id']} {c['entity_name']!r} "
                          f"→ {qid} label={c['label']!r} P31={matched_type}")
                    total_found += 1
            else:
                # Unknown P31 — leave as skipped (safer to require manual review)
                unknown = [p for p in p31_values if p not in _NON_COMPANY_P31]
                print(f"    UNKN  {c['entity_id']} {c['entity_name']!r} "
                      f"→ unrecognized P31: {unknown}")

    save_candidates(data, candidates, "Phase C complete")
    print(f"\n  Phase C: {total_found} new proposals from P31 confirmation.")
    return total_found


# ── Phase D: Results[1–4] re-search ──────────────────────────────────────────

_STRIP_PATTERNS = [
    r"\bCLASS\s+[A-Z]\b",
    r"\bSERIES\s+[A-Z]\b",
    r"\bPREF\b", r"\bPREFFERED\b",
    r"\bADR\b", r"\bADS\b",
    r"\bGDR\b",
    r"\bORD\b",
    r"\bNEW\b",
    r"\b[A-Z]\b$",
    r"\bLTD\b", r"\bPLC\b", r"\bINC\b", r"\bCORP\b",
    r"\bAG\b", r"\bSE\b", r"\bSA\b", r"\bNV\b", r"\bASA\b",
    r"\bAB\b", r"\bOYJ\b", r"\bGMBH\b", r"\bSPA\b", r"\bSRL\b", r"\bBV\b",
]


def clean_name_light(raw: str) -> str:
    """
    Lighter cleaning: only strip share-class/legal suffixes.
    Does NOT strip industry terms (GOLD, SILVER, RARE EARTHS, etc.).
    Used for Phase D re-search to avoid losing meaningful keywords.
    """
    s = raw.upper()
    for pattern in _STRIP_PATTERNS:
        s = re.sub(pattern, " ", s)
    s = re.sub(r"[&()/]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.title()


def phase_d(candidates: list[dict], by_id: dict[str, dict],
            data: dict) -> int:
    """
    Re-search entities whose top result had the wrong description. Checks
    results[0–4] with the fixed filter. Uses original entity_name (lightly
    cleaned) rather than the pre-stripped search_name.
    """
    print("\n=== Phase D: Results[1–4] re-search (Wikidata API) ===")

    targets = [
        c for c in candidates
        if c["status"] == "skipped"
        and c.get("reason") in ("no org keyword in description",)
        and c.get("entity_name")
    ]
    print(f"  Wrong-top-result targets: {len(targets)}")

    total_found = 0

    for idx, c in enumerate(targets, 1):
        eid = c["entity_id"]
        # Guard — might have been upgraded by earlier phase
        if by_id.get(eid, {}).get("status") in ("accepted", "proposed", "rejected"):
            continue

        entity_name = c["entity_name"]
        search_query = clean_name_light(entity_name)

        if len(normalize_label(search_query)) < 3:
            continue

        print(f"  [{idx}/{len(targets)}] {entity_name!r} → search: {search_query!r}")

        try:
            results = wikidata_search(search_query, limit=SEARCH_LIMIT)
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

        found_any = False
        for rank, r in enumerate(results):
            qid = r.get("id", "")
            label = r.get("label", "")
            description = r.get("description", "")

            lm = label_matches(search_query, label)
            is_org, org_reason = description_is_org_fixed(description)

            if lm and is_org:
                reason = (f"re-search results[{rank}]: label match + {org_reason} "
                          f"(original results[0] had wrong desc)")
                if upgrade_to_proposed(candidates, by_id, c, qid, label,
                                       description, reason):
                    print(f"    FOUND [{rank}] {qid} {label!r} "
                          f"({description[:60]!r})")
                    total_found += 1
                    found_any = True
                    break

        if not found_any:
            print(f"    still no match in top {SEARCH_LIMIT} results")

    save_candidates(data, candidates, "Phase D complete")
    print(f"\n  Phase D: {total_found} new proposals from re-search.")
    return total_found


# ── Phase E: Wikipedia API search ────────────────────────────────────────────

def wp_search(query: str, limit: int = WP_SEARCH_LIMIT) -> list[str]:
    """Search English Wikipedia; return list of article titles."""
    params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "srsort": "relevance",
        "format": "json",
        "utf8": 1,
    })
    resp = http_get(f"{WP_API}?{params}", timeout=15)
    return [r["title"] for r in resp.get("query", {}).get("search", [])]


def wp_pageprops(titles: list[str]) -> dict[str, str]:
    """
    Batch-fetch Wikidata QIDs for a list of Wikipedia article titles.
    Returns {title: qid} for articles that have a wikibase_item property.
    Handles redirects automatically via &redirects=1.
    """
    if not titles:
        return {}
    params = urllib.parse.urlencode({
        "action": "query",
        "prop": "pageprops",
        "titles": "|".join(titles[:50]),  # API limit: 50 titles per call
        "redirects": 1,
        "format": "json",
    })
    resp = http_get(f"{WP_API}?{params}", timeout=20)
    pages = resp.get("query", {}).get("pages", {})
    result = {}
    for page in pages.values():
        qid = page.get("pageprops", {}).get("wikibase_item", "")
        title = page.get("title", "")
        if qid and title:
            result[title] = qid
    return result


def wd_entities_batch(qids: list[str]) -> dict[str, tuple[str, str]]:
    """
    Batch-fetch English label + description for a list of QIDs from Wikidata.
    Returns {qid: (label, description)}.
    """
    if not qids:
        return {}
    params = urllib.parse.urlencode({
        "action": "wbgetentities",
        "ids": "|".join(qids[:50]),  # API limit: 50 IDs per call
        "props": "labels|descriptions",
        "languages": "en",
        "format": "json",
    })
    resp = http_get(f"{WD_API}?{params}", timeout=30)
    result = {}
    for qid, entity in resp.get("entities", {}).items():
        label = entity.get("labels", {}).get("en", {}).get("value", "")
        description = entity.get("descriptions", {}).get("en", {}).get("value", "")
        result[qid] = (label, description)
    return result


def phase_e(candidates: list[dict], by_id: dict[str, dict],
            data: dict) -> int:
    """
    Search English Wikipedia for each skipped entity that got "no results from
    Wikidata search". Resolves Wikipedia articles to Wikidata QIDs via
    prop=pageprops, then fetches label+description from Wikidata and applies
    the standard label-match + org-keyword filter before proposing.

    Particularly effective for iShares names truncated to ~35 chars:
      'China Nonferrous Mining Corporatio' → 'China Nonferrous Mining Corporation'
      label_matches() handles prefix matches, so truncated names pass the filter.
    """
    print("\n=== Phase E: Wikipedia API search (Wikipedia → Wikidata QID) ===")

    targets = [
        c for c in candidates
        if c["status"] == "skipped"
        and c.get("reason") == "no results from Wikidata search"
    ]
    print(f"  Targets: {len(targets)}")

    total_found = 0

    for idx, c in enumerate(targets, 1):
        eid = c["entity_id"]
        if by_id.get(eid, {}).get("status") in ("accepted", "proposed", "rejected"):
            continue

        entity_name = c["entity_name"]
        search_name = c.get("search_name", entity_name)

        if len(normalize_label(search_name)) < 3:
            print(f"  [{idx}/{len(targets)}] SKIP too-short: {entity_name!r}")
            continue

        # Step 1 — search Wikipedia
        time.sleep(WP_DELAY)
        try:
            wp_titles = wp_search(search_name, limit=WP_SEARCH_LIMIT)
        except Exception as e:
            print(f"  [{idx}/{len(targets)}] WP search error ({entity_name!r}): {e}")
            continue

        if not wp_titles:
            continue

        # Step 2 — resolve top Wikipedia results to QIDs (batched, no extra delay)
        try:
            title_to_qid = wp_pageprops(wp_titles[:3])
        except Exception as e:
            print(f"  [{idx}/{len(targets)}] WP pageprops error ({entity_name!r}): {e}")
            continue

        qids = list(dict.fromkeys(title_to_qid.values()))  # deduplicated, ordered
        if not qids:
            continue

        # Step 3 — fetch Wikidata label+description for those QIDs (batched)
        try:
            qid_info = wd_entities_batch(qids)
        except Exception as e:
            print(f"  [{idx}/{len(targets)}] Wikidata entity error ({entity_name!r}): {e}")
            continue

        # Step 4 — apply label-match + org-keyword filter
        found = False
        for title, qid in title_to_qid.items():
            label, description = qid_info.get(qid, ("", ""))

            lm = label_matches(search_name, label)
            is_org, org_reason = description_is_org_fixed(description)

            if lm and is_org:
                reason = (f"Wikipedia search → {title!r} → {qid} "
                          f"+ {org_reason}")
                if upgrade_to_proposed(candidates, by_id, c, qid, label,
                                       description, reason):
                    print(f"  [{idx}/{len(targets)}] FOUND {eid} {entity_name!r}")
                    print(f"    → {qid} {label!r} ({description[:60]!r})")
                    total_found += 1
                    found = True
                break

        if not found and wp_titles:
            print(f"  [{idx}/{len(targets)}] no match: {entity_name!r} "
                  f"(WP top: {wp_titles[0]!r})")

        # Checkpoint every 25 entities
        if idx % 25 == 0:
            save_candidates(data, candidates, f"Phase E checkpoint {idx}")

    save_candidates(data, candidates, "Phase E complete")
    print(f"\n  Phase E: {total_found} new proposals from Wikipedia search.")
    return total_found


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(CANDIDATES_PATH):
        print(f"ERROR: {CANDIDATES_PATH} not found.")
        print("Run python3 scripts/search_missing_qids.py --search first.")
        sys.exit(1)

    print("reprocess_skipped_qids.py — Second-pass QID recovery")
    print("=" * 60)
    print(f"Date: {TODAY}")

    data, candidates, by_id = load_candidates()

    initial_proposed = sum(1 for c in candidates if c["status"] == "proposed")
    initial_skipped = sum(1 for c in candidates if c["status"] == "skipped")
    print(f"Initial state: proposed={initial_proposed} skipped={initial_skipped}\n")

    # Run all phases
    a = phase_a(candidates, by_id)
    save_candidates(data, candidates, "Phase A complete")

    b = phase_b(candidates, by_id, data)
    c = phase_c(candidates, by_id, data)
    d = phase_d(candidates, by_id, data)
    e = phase_e(candidates, by_id, data)

    # Final summary
    final_proposed = sum(1 for c in candidates if c["status"] == "proposed")
    final_skipped = sum(1 for c in candidates if c["status"] == "skipped")

    print(f"\n{'=' * 60}")
    print(f"DONE.")
    print(f"  Phase A (disqualify fix):  {a:3d} new proposals")
    print(f"  Phase B (P856 website):    {b:3d} new proposals")
    print(f"  Phase C (P31 type):        {c:3d} new proposals")
    print(f"  Phase D (re-search):       {d:3d} new proposals")
    print(f"  Phase E (Wikipedia):       {e:3d} new proposals")
    print(f"  Total new:                 {a+b+c+d+e:3d}")
    print(f"  Final proposed:            {final_proposed}")
    print(f"  Final skipped:             {final_skipped}")
    print(f"\nNext steps:")
    print(f"  1. Review data/qid_candidates.json")
    print(f"     Change status='proposed' → 'accepted' or 'rejected'")
    print(f"  2. python3 scripts/search_missing_qids.py --apply")
    print(f"  3. python3 scripts/validate.py")


if __name__ == "__main__":
    main()
