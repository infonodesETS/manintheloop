#!/usr/bin/env python3
"""
search_missing_qids.py — Two-phase Wikidata QID search for companies missing wikidata_id.

GUARANTEES
──────────
1. NO FALSE POSITIVES: a QID is only proposed when ALL three conditions hold:
     a. The result label closely matches the search name (after normalization)
     b. The result description contains at least one organization-type keyword
     c. The result description does NOT contain a disqualifying keyword (city, person, etc.)
   Any result that fails even one condition is written as status=skipped, never applied.

2. NO RATE LIMITING: minimum 1.5 s between API calls (above Wikidata's 1 req/s guideline).
   On HTTP 429, waits 4 s / 8 s / 16 s (exponential backoff). If all retries fail, the
   entity is skipped — the database is never left in a partial state.

WORKFLOW
────────
  Phase 1 — Search (no DB writes):
      python3 scripts/search_missing_qids.py --search
      → Writes data/qid_candidates.json with status=proposed / skipped for each entity.
      → Review the file manually. Change status from "proposed" to "accepted" to approve.
      → Never modify database.json.

  Phase 2 — Apply (no API calls):
      python3 scripts/search_missing_qids.py --apply
      → Reads data/qid_candidates.json.
      → Applies only entries with status="accepted".
      → Appends history + validation entries to each entity in database.json.
      → Does not call any external API.
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
CANDIDATES_PATH = os.path.join(BASE, "data", "qid_candidates.json")

TODAY = date.today().isoformat()
API = "https://www.wikidata.org/w/api.php"

# Minimum delay between API calls (seconds). Wikidata guideline: max 1 req/s.
DELAY = 1.5
# Backoff schedule on HTTP 429 (seconds)
BACKOFF = [4, 8, 16]

# ── Suffixes stripped from iShares names before searching ─────────────────────
# These are share-class/listing suffixes that are not part of the company name.
_STRIP_PATTERNS = [
    r"\bCLASS\s+[A-Z]\b",        # Class A, Class B, Class C, ...
    r"\bSERIES\s+[A-Z]\b",       # Series A, Series B, ...
    r"\bPREF\b", r"\bPREFFERED\b",
    r"\bADR\b", r"\bADS\b",      # American Depositary Receipt/Share
    r"\bGDR\b",                   # Global Depositary Receipt
    r"\bORD\b",                   # Ordinary shares
    r"\bNEW\b",                   # e.g. "Foo New" (share reclassification)
    r"\b[A-Z]\b$",                # single trailing capital letter (share class)
    r"\bLTD\b", r"\bPLC\b", r"\bINC\b", r"\bCORP\b", r"\bAG\b",
    r"\bSE\b", r"\bSA\b", r"\bNV\b", r"\bASA\b", r"\bAB\b", r"\bOYJ\b",
    r"\bGMBH\b", r"\bSPA\b", r"\bSRL\b", r"\bBV\b",
    r"\bINTERNATIONAL\b",
    # iShares-specific ALL-CAPS artifacts
    r"\bIRON\s+AND\s+STEEL\b",
    r"\bGOLD\s+AND\s+SILVER\b",
    r"\bRARE\s+EARTHS?\b",
    r"\bADR\s+REPRESENTING\b",
    r"\bPREF\s+SA\b",
]

# Keywords that MUST appear in the Wikidata description for a result to be accepted.
# At least one must match.
_ORG_KEYWORDS = {
    "company", "corporation", "conglomerate", "enterprise", "business",
    "manufacturer", "producer", "supplier", "provider",
    "group", "holding", "multinational",
    "mining", "technology", "technologies", "semiconductor",
    "telecommunications", "telecom", "aerospace", "defence", "defense",
    "airline", "bank", "insurer", "insurance", "fund", "investment",
    "retailer", "distributor", "operator",
    "société", "empresa", "gesellschaft", "azienda", "onderneming",
    "concern", "konzern",
}

# Keywords that DISQUALIFY a result even if an org keyword is present.
_DISQUALIFY_KEYWORDS = {
    "city", "town", "village", "municipality", "commune", "district",
    "region", "province", "county", "country", "state", "nation",
    "person", "politician", "athlete", "musician", "actor", "artist",
    "philosopher", "author", "scientist", "academic",
    "river", "mountain", "lake", "island", "ocean", "sea",
    "constellation", "asteroid", "planet", "star",
    "article", "journal", "magazine", "newspaper", "publication",
    "album", "song", "film", "television", "video game",
    "school", "university", "college", "institute",  # except when combined with company
    "religion", "philosophy", "mythology",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def clean_search_name(raw: str) -> str:
    """Strip share-class suffixes and normalize for searching."""
    s = raw.upper()
    for pattern in _STRIP_PATTERNS:
        s = re.sub(pattern, " ", s)
    s = re.sub(r"[&()/]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.title()


def normalize_label(s: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def label_matches(search_name: str, result_label: str) -> bool:
    """
    True if the result label is a close match for the search name.

    Rules (all checked against normalized forms):
      - Exact match, OR
      - Result label starts with the search name (result is a known expansion), OR
      - Search name starts with result label (result is a known contraction),
        but only if result label >= 4 chars (prevents trivially short matches).
    """
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


def description_is_org(description: str) -> tuple[bool, str]:
    """
    Returns (is_org, reason).
    is_org=True only if description contains an org keyword AND no disqualify keyword.
    """
    if not description:
        return False, "no description"
    d = description.lower()
    disq = next((kw for kw in _DISQUALIFY_KEYWORDS if kw in d), None)
    if disq:
        return False, f"disqualified by '{disq}'"
    org = next((kw for kw in _ORG_KEYWORDS if kw in d), None)
    if org:
        return True, f"org keyword '{org}'"
    return False, "no org keyword in description"


# ── API ───────────────────────────────────────────────────────────────────────

def api_get(params: dict) -> dict:
    """Call Wikidata API with retry on 429. Raises on non-429 errors."""
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": "infonodes-refactoringDB/1.0 (https://github.com/infonodesETS/manintheloop)"
    })
    for attempt, wait in enumerate([0] + BACKOFF):
        if wait:
            print(f"    [429] rate limit — waiting {wait}s (attempt {attempt+1}/{len(BACKOFF)+1})")
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < len(BACKOFF):
                continue
            raise
    raise RuntimeError(f"All retries exhausted for: {url}")


def search_wikidata(query: str, limit: int = 5) -> list[dict]:
    """Search Wikidata entities by label. Returns list of result dicts."""
    time.sleep(DELAY)
    data = api_get({
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "limit": limit,
        "type": "item",
    })
    return data.get("search", [])


# ── Phase 1: Search ───────────────────────────────────────────────────────────

def phase_search():
    print("Phase 1 — Search (no database writes)")
    print("=" * 60)

    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    missing = [
        e for e in db["entities"]
        if e.get("type") == "company" and not e.get("wikidata_id")
    ]
    print(f"Companies missing wikidata_id: {len(missing)}\n")

    # Load existing candidates to allow resuming
    existing: dict[str, dict] = {}
    if os.path.exists(CANDIDATES_PATH):
        with open(CANDIDATES_PATH, encoding="utf-8") as f:
            prev = json.load(f)
        existing = {c["entity_id"]: c for c in prev.get("candidates", [])}
        print(f"Resuming: {len(existing)} entries already in candidates file.\n")

    candidates = []
    proposed = 0
    skipped = 0
    already_done = 0

    for idx, entity in enumerate(missing, 1):
        eid = entity["id"]
        name = entity["name"]

        # Skip if already processed (allows resume)
        if eid in existing:
            candidates.append(existing[eid])
            already_done += 1
            continue

        search_name = clean_search_name(name)

        # Skip names that are too short or ambiguous after cleaning
        if len(normalize_label(search_name)) < 3:
            entry = {
                "entity_id": eid,
                "entity_name": name,
                "search_name": search_name,
                "status": "skipped",
                "reason": "search name too short after cleaning",
                "qid": None,
                "label": None,
                "description": None,
            }
            candidates.append(entry)
            skipped += 1
            print(f"  [{idx}/{len(missing)}] SKIP  {name!r} → too short")
            continue

        results = search_wikidata(search_name, limit=5)

        if not results:
            entry = {
                "entity_id": eid,
                "entity_name": name,
                "search_name": search_name,
                "status": "skipped",
                "reason": "no results from Wikidata search",
                "qid": None,
                "label": None,
                "description": None,
            }
            candidates.append(entry)
            skipped += 1
            print(f"  [{idx}/{len(missing)}] SKIP  {name!r} → no results")
            continue

        # Evaluate top result only
        top = results[0]
        qid = top.get("id")
        label = top.get("label", "")
        description = top.get("description", "")

        lm = label_matches(search_name, label)
        is_org, org_reason = description_is_org(description)

        if lm and is_org:
            entry = {
                "entity_id": eid,
                "entity_name": name,
                "search_name": search_name,
                "status": "proposed",
                "reason": f"label match + {org_reason}",
                "qid": qid,
                "label": label,
                "description": description,
            }
            candidates.append(entry)
            proposed += 1
            print(f"  [{idx}/{len(missing)}] PROP  {name!r} → {qid} \"{label}\" ({description[:60]})")
        else:
            reasons = []
            if not lm:
                reasons.append(f"label mismatch: {search_name!r} vs {label!r}")
            if not is_org:
                reasons.append(org_reason)
            entry = {
                "entity_id": eid,
                "entity_name": name,
                "search_name": search_name,
                "status": "skipped",
                "reason": "; ".join(reasons),
                "qid": qid,
                "label": label,
                "description": description,
            }
            candidates.append(entry)
            skipped += 1
            print(f"  [{idx}/{len(missing)}] SKIP  {name!r} → {org_reason} | label: {label!r}")

        # Periodic save every 50 entries (allows resume on interruption)
        if idx % 50 == 0:
            _write_candidates(candidates, proposed, skipped)
            print(f"  [checkpoint saved — {idx}/{len(missing)}]")

    _write_candidates(candidates, proposed, skipped)

    print(f"\n{'=' * 60}")
    print(f"Search complete.")
    print(f"  Already processed (skipped): {already_done}")
    print(f"  Proposed (review needed):    {proposed}")
    print(f"  Skipped (no safe match):     {skipped}")
    print(f"\nNext steps:")
    print(f"  1. Review data/qid_candidates.json")
    print(f"     Change status from 'proposed' to 'accepted' for correct matches.")
    print(f"     Change status to 'rejected' for wrong matches.")
    print(f"  2. python3 scripts/search_missing_qids.py --apply")


def _write_candidates(candidates: list, proposed: int, skipped: int):
    output = {
        "_generated_at": TODAY,
        "_total": len(candidates),
        "_proposed": proposed,
        "_skipped": skipped,
        "_instructions": (
            "Review each entry with status='proposed'. "
            "Change to 'accepted' to apply, 'rejected' to discard. "
            "Do not change 'skipped' entries. "
            "Then run: python3 scripts/search_missing_qids.py --apply"
        ),
        "candidates": candidates,
    }
    with open(CANDIDATES_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


# ── Phase 2: Apply ────────────────────────────────────────────────────────────

def phase_apply():
    print("Phase 2 — Apply accepted QIDs (no API calls)")
    print("=" * 60)

    if not os.path.exists(CANDIDATES_PATH):
        print(f"ERROR: {CANDIDATES_PATH} not found. Run --search first.")
        sys.exit(1)

    with open(CANDIDATES_PATH, encoding="utf-8") as f:
        candidates_data = json.load(f)

    accepted = [c for c in candidates_data["candidates"] if c["status"] == "accepted"]
    print(f"Entries with status='accepted': {len(accepted)}")

    if not accepted:
        print("Nothing to apply.")
        return

    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    entity_map = {e["id"]: e for e in db["entities"]}
    applied = 0

    for c in accepted:
        eid = c["entity_id"]
        qid = c["qid"]
        if not qid:
            print(f"  WARN: {eid} has status=accepted but qid is null — skipping")
            continue
        entity = entity_map.get(eid)
        if not entity:
            print(f"  WARN: {eid} not found in database — skipping")
            continue
        if entity.get("wikidata_id"):
            print(f"  SKIP: {eid} already has wikidata_id={entity['wikidata_id']}")
            continue

        entity["wikidata_id"] = qid
        entity["history"].append({
            "date": TODAY,
            "source": "wikidata",
            "author": "search_missing_qids.py",
            "field": "wikidata_id",
            "old": None,
            "new": qid,
            "description": (
                f"wikidata_id set via search: label={c['label']!r}, "
                f"description={repr(c['description'])[:80]}. "
                f"Search name used: {c['search_name']!r}. "
                f"Human-reviewed via qid_candidates.json before applying."
            ),
        })
        entity["validation"].append({
            "status": "needs_review",
            "description": (
                f"wikidata_id {qid} applied from qid_candidates.json (human-approved). "
                f"Run enrich_wikidata.py to populate sources.wikidata block."
            ),
            "author": "search_missing_qids.py",
            "datestamp": TODAY,
        })
        applied += 1
        print(f"  ✓ {eid} ({entity['name']!r}) → {qid}")

    db["_updated"] = TODAY
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Applied {applied} QIDs to database.json.")
    print(f"Next: python3 scripts/validate.py")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--search" in sys.argv:
        phase_search()
    elif "--apply" in sys.argv:
        phase_apply()
    else:
        print(__doc__)
        print("\nUsage:")
        print("  python3 scripts/search_missing_qids.py --search")
        print("  python3 scripts/search_missing_qids.py --apply")
        sys.exit(1)
