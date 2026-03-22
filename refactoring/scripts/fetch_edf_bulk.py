#!/usr/bin/env python3
"""
fetch_edf_bulk.py — Fetch all EDF calls from the EU Participant Portal and save
to data/edf_calls.json.

What it does
------------
1. Paginated bulk fetch of all EDF topic identifiers (same logic as the browser
   tab's autocomplete fetch, but with no CORS restrictions).
2. For every call: fetch full metadata (ccm2Id, title, status, description,
   budget) plus funded project list.
3. For every project: fetch participant-level details (budget, countries, roles).
4. Save structured output to data/edf_calls.json.

Modes
-----
  (default)   Full fetch: all calls, all projects, all participants.
  --update    Incremental: re-check only open/forthcoming calls, or closed calls
              that still have no projects. Merges into existing edf_calls.json.
  --limit N   Stop after processing N calls (for testing). Default: 0 (no limit).

Usage
-----
  python3 scripts/fetch_edf_bulk.py
  python3 scripts/fetch_edf_bulk.py --limit 5
  python3 scripts/fetch_edf_bulk.py --update
  python3 scripts/fetch_edf_bulk.py --update --limit 10

API endpoints used
------------------
  Search API  POST https://api.tech.ec.europa.eu/search-api/prod/rest/search
              pageNumber is 1-indexed; parameters go in the POST body.
  Projects    GET  https://ec.europa.eu/info/funding-tenders/opportunities/api/topicProjectsList.json?topicId=...
  Doc API     GET  https://api.tech.ec.europa.eu/search-api/prod/rest/document/{programId}{businessId}?apiKey=SEDIA_NONH2020_PROD
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlencode, quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE, "data", "edf_calls.json")

# ── API constants ──────────────────────────────────────────────────────────────
SEARCH_API   = "https://api.tech.ec.europa.eu/search-api/prod/rest/search"
DOC_API      = "https://api.tech.ec.europa.eu/search-api/prod/rest/document"
PROJECTS_API = "https://ec.europa.eu/info/funding-tenders/opportunities/api/topicProjectsList.json"
YEARS        = [2027, 2026, 2025, 2024, 2023, 2022, 2021]
PAGE_SIZE    = 50
MAX_PAGES    = 10    # safety cap per year

# ── Polite delays (seconds) ────────────────────────────────────────────────────
DELAY_PAGE    = 0.5   # between paginated bulk-fetch pages
DELAY_YEAR    = 0.8   # between years during bulk fetch
DELAY_CALL    = 1.0   # between calls during detail fetch
DELAY_PROJECT = 0.8   # between projects during detail fetch


# ══════════════════════════════════════════════════════════════════════════════
# HTTP helpers
# ══════════════════════════════════════════════════════════════════════════════

def http_get(url: str, timeout: int = 20) -> dict | list | None:
    """GET request → parsed JSON, or None on error."""
    try:
        req = Request(url, headers={"Accept": "application/json", "User-Agent": "infonodes-fetcher/1.0"})
        with urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        print(f"    [warn] GET {url[:80]}… → {e}", file=sys.stderr)
        return None


def http_post(url: str, params: dict, timeout: int = 20) -> dict | None:
    """POST request with application/x-www-form-urlencoded body → parsed JSON."""
    body = urlencode(params).encode()
    try:
        req = Request(
            url, data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "infonodes-fetcher/1.0",
            }
        )
        with urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except (HTTPError, URLError, json.JSONDecodeError) as e:
        print(f"    [warn] POST {url[:80]}… → {e}", file=sys.stderr)
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Bulk fetch: all EDF identifiers + metadata
# ══════════════════════════════════════════════════════════════════════════════

def fetch_all_topics() -> dict:
    """
    Returns a dict keyed by identifier:
      { "EDF-2024-DA-...": { identifier, title, status, deadline, ccm2Id,
                             description, budget_overview, _fetched_at }, ... }
    """
    seen    = {}   # identifier → record
    query   = {"bool": {"must": [{"terms": {"type": ["1", "2", "8"]}}]}}

    for year in YEARS:
        print(f"\n  Year {year}:")
        new_this_year = 0

        for page in range(1, MAX_PAGES + 1):
            data = http_post(SEARCH_API, {
                "apiKey":     "SEDIA",
                "text":       f"EDF-{year}",
                "query":      json.dumps(query),
                "pageNumber": page,
                "pageSize":   PAGE_SIZE,
            })
            if not data:
                break

            results    = data.get("results") or []
            new_page   = 0

            for r in results:
                meta   = r.get("metadata") or {}
                id_raw = meta.get("identifier") or []
                raw_id = (id_raw[0] if (isinstance(id_raw, list) and id_raw) else id_raw) or ""
                if not raw_id:
                    continue
                identifier = str(raw_id).upper()
                if not identifier.startswith("EDF-"):
                    continue
                if identifier in seen:
                    continue

                def get1(key):
                    v = meta.get(key) or []
                    return (v[0] if (isinstance(v, list) and v) else v) or ""

                budget_overview = None
                budget_raw = meta.get("budgetOverview") or []
                if budget_raw:
                    try:
                        budget_overview = json.loads(budget_raw[0] if isinstance(budget_raw, list) else budget_raw)
                    except (json.JSONDecodeError, TypeError):
                        pass

                seen[identifier] = {
                    "identifier":     identifier,
                    "title":          get1("title") or get1("topicTitle"),
                    "status":         get1("status"),
                    "deadline":       get1("deadlineDate") or get1("submissionDeadlineDate"),
                    "ccm2Id":         get1("ccm2Id"),
                    "description":    get1("descriptionByte"),
                    "budget_overview": budget_overview,
                    "_fetched_at":    datetime.now(timezone.utc).isoformat(),
                    "projects":       None,   # populated in phase 2
                }
                new_page += 1
                new_this_year += 1

            print(f"    p{page}: {len(results)} results, {new_page} new → {len(seen)} total")

            if new_page == 0 or len(results) < PAGE_SIZE:
                break
            time.sleep(DELAY_PAGE)

        time.sleep(DELAY_YEAR)

    # Sort by year desc, then identifier asc
    ordered = dict(sorted(
        seen.items(),
        key=lambda kv: (
            -(int(kv[0].split("-")[1]) if kv[0].split("-")[1].isdigit() else 0),
            kv[0]
        )
    ))
    print(f"\n  Total unique EDF topics: {len(ordered)}")
    return ordered


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2 — Per-call detail: topic meta (if needed) + projects + participants
# ══════════════════════════════════════════════════════════════════════════════

def fetch_topic_meta(identifier: str) -> dict | None:
    """
    Fetch ccm2Id, description, budget_overview for a specific identifier.
    Uses suffix-only text search to avoid year-bucket result dilution.
    """
    parts  = identifier.split("-", 2)   # ["EDF", "2024", "DA-C4ISR-..."]
    suffix = parts[2] if len(parts) == 3 else identifier

    query = {
        "bool": {
            "must": [
                {"terms": {"type": ["1", "2", "8"]}},
                {"term":  {"identifier": identifier}},
            ]
        }
    }
    data = http_post(SEARCH_API, {
        "apiKey":     "SEDIA",
        "text":       suffix,
        "query":      json.dumps(query),
        "pageNumber": 1,
        "pageSize":   50,
    })
    if not data:
        return None

    results = data.get("results") or []
    id_upper = identifier.upper()

    match = None
    for r in results:
        meta   = r.get("metadata") or {}
        ids    = meta.get("identifier") or meta.get("topicCode") or []
        id_arr = ids if isinstance(ids, list) else [ids]
        if any((i or "").upper() == id_upper for i in id_arr):
            match = meta
            break

    if not match:
        return None

    def get1(key):
        v = match.get(key) or []
        return (v[0] if (isinstance(v, list) and v) else v) or ""

    budget_overview = None
    budget_raw = match.get("budgetOverview") or []
    if budget_raw:
        try:
            budget_overview = json.loads(budget_raw[0] if isinstance(budget_raw, list) else budget_raw)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "ccm2Id":         get1("ccm2Id"),
        "description":    get1("descriptionByte"),
        "budget_overview": budget_overview,
    }


def fetch_projects(topic_id: str) -> list:
    """Fetch the list of funded projects for a topic (by ccm2Id)."""
    url  = f"{PROJECTS_API}?topicId={quote(str(topic_id))}"
    data = http_get(url)
    if not isinstance(data, list):
        return []
    return data


def norm_budget(val) -> str:
    if not val:
        return ""
    s = str(val).replace("€", "").replace("$", "").replace(",", "").strip()
    try:
        float(s)
        return s
    except ValueError:
        return ""


def fetch_project_details(program_id: str, business_id: str) -> dict:
    """Fetch participant-level details for a single project via DOC_API."""
    url  = f"{DOC_API}/{program_id}{business_id}?apiKey=SEDIA_NONH2020_PROD"
    data = http_get(url)
    if not data:
        return {}

    meta = data.get("metadata") or {}

    def get1(key, default=""):
        v = meta.get(key)
        if isinstance(v, list):
            return v[0] if v else default
        return v or default

    ORG_DETAILS_BASE = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/how-to-participate/org-details/"

    participants = []
    try:
        part_json = get1("participants", "[]")
        for p in json.loads(part_json):
            addr    = p.get("postalAddress") or {}
            cc      = addr.get("countryCode") or ""
            country      = cc.get("description", "") if isinstance(cc, dict) else cc
            country_code = cc.get("abbreviation", "") if isinstance(cc, dict) else ""
            pic = str(p.get("pic") or "")
            participants.append({
                "organization_name": p.get("legalName") or "",
                "pic":               pic,
                "eu_url":            f"{ORG_DETAILS_BASE}{pic}" if pic else "",
                "role":              p.get("role") or "",
                "order":             p.get("order"),
                "status":            p.get("status") or "",
                "activity_type":     p.get("activityType") or "",
                "organization_type": p.get("organizationType") or "",
                "type":              p.get("type") or "",
                "sme":               p.get("sme"),
                "country":           country,
                "country_code":      country_code,
                "city":              addr.get("city") or "",
                "postal_code":       addr.get("postalCode") or "",
                "street":            addr.get("street") or "",
                "latitude":          p.get("latitude") or "",
                "longitude":         p.get("longitude") or "",
                "web_link":          p.get("webLink") or "",
                "eu_contribution":   norm_budget(p.get("eucontribution") or ""),
            })
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass

    return {
        "status":          get1("status"),
        "start_date":      get1("startDate"),
        "end_date":        get1("endDate"),
        "overall_budget":  norm_budget(get1("overallBudget")),
        "eu_contribution": norm_budget(get1("euContributionAmount")),
        "objective":       get1("objective"),
        "type_of_action":  get1("typeOfAction"),
        "participants":    participants,
    }


def fetch_call_detail(record: dict) -> dict:
    """
    Enrich a call record with full project + participant data.
    Mutates and returns the record.
    """
    identifier = record["identifier"]
    ccm2_id    = record.get("ccm2Id")

    # If we don't have ccm2Id yet, do a topic meta fetch
    if not ccm2_id:
        print(f"    fetching topic meta for {identifier}…")
        meta = fetch_topic_meta(identifier)
        if meta:
            record["ccm2Id"]          = meta["ccm2Id"]
            record["description"]     = meta["description"]
            record["budget_overview"] = meta["budget_overview"]
            ccm2_id = record["ccm2Id"]
        else:
            print(f"    [warn] could not resolve ccm2Id for {identifier}")
            record["projects"] = []
            return record

    # Fetch funded project list
    raw_projects = fetch_projects(ccm2_id)
    if not raw_projects:
        record["projects"] = []
        return record

    print(f"    {len(raw_projects)} project(s) found — fetching details…")
    detailed = []
    for i, p in enumerate(raw_projects):
        program_id  = str(p.get("programId") or "")
        business_id = str(p.get("businessIdentifier") or "")
        details     = fetch_project_details(program_id, business_id)
        project = {
            "title":       p.get("title") or "",
            "acronym":     p.get("acronym") or "",
            "project_id":  business_id,
            "url":         f"https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/projects-details/{program_id}/{business_id}",
            **details,
        }
        detailed.append(project)
        if i < len(raw_projects) - 1:
            time.sleep(DELAY_PROJECT)

    record["projects"]          = detailed
    record["_projects_fetched_at"] = datetime.now(timezone.utc).isoformat()
    return record


# ══════════════════════════════════════════════════════════════════════════════
# Load / save
# ══════════════════════════════════════════════════════════════════════════════

def load_existing() -> dict:
    if not os.path.exists(OUTPUT_PATH):
        return {}
    try:
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        calls = data.get("calls") or {}
        print(f"  Loaded {len(calls)} existing calls from {OUTPUT_PATH}")
        return calls
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [warn] Could not read existing file: {e}", file=sys.stderr)
        return {}


def save(calls: dict) -> None:
    output = {
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_total_calls":  len(calls),
        "calls":         calls,
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved {len(calls)} calls → {OUTPUT_PATH}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--update", action="store_true",
                        help="Incremental mode: only re-check open/forthcoming calls and closed calls without projects")
    parser.add_argument("--reenrich", action="store_true",
                        help="Re-fetch project details for all calls that already have projects (use after script changes)")
    parser.add_argument("--limit", type=int, default=0, metavar="N",
                        help="Stop after processing N calls (0 = no limit, default 0)")
    args = parser.parse_args()

    mode = "reenrich" if args.reenrich else ("update" if args.update else "full")
    print("=" * 60)
    print("EDF Bulk Fetch")
    print(f"Mode : {mode}")
    if args.limit:
        print(f"Limit: {args.limit} calls")
    print("=" * 60)

    # ── Phase 1: get identifier list ──────────────────────────────────────────
    if args.reenrich or args.update:
        mode_label = "reenrich" if args.reenrich else "update"
        print(f"\n[Phase 1] Loading existing data ({mode_label} mode — skipping bulk fetch)…")
        calls = load_existing()
        if not calls:
            print("  No existing data found. Run without --update/--reenrich first.")
            sys.exit(1)
    else:
        print("\n[Phase 1] Fetching all EDF topic identifiers…")
        fresh    = fetch_all_topics()
        existing = load_existing()

        # Merge: keep existing project data, overlay fresh metadata
        calls = {}
        for identifier, record in fresh.items():
            if identifier in existing:
                old = existing[identifier]
                record["projects"]             = old.get("projects")
                record["_projects_fetched_at"] = old.get("_projects_fetched_at")
            calls[identifier] = record

        # Keep any existing calls not returned by fresh fetch (shouldn't happen, but safe)
        for identifier, record in existing.items():
            if identifier not in calls:
                calls[identifier] = record

    # ── Phase 2: per-call detail fetch ────────────────────────────────────────
    def needs_detail(record: dict) -> bool:
        status   = (record.get("status") or "").lower()
        projects = record.get("projects")
        if projects is None:
            return True   # never fetched
        if isinstance(projects, list) and len(projects) == 0:
            # Closed call with no projects: re-check (projects may have been added)
            if "closed" in status:
                return True
        # Open/forthcoming: re-check metadata (status may have changed)
        if "open" in status or "forthcoming" in status:
            return True
        return False

    if args.reenrich:
        to_fetch = [r for r in calls.values() if isinstance(r.get("projects"), list) and len(r["projects"]) > 0]
        print(f"\n[Phase 2] Reenrich mode: re-fetching project details for {len(to_fetch)} calls with existing projects…")
    elif args.update:
        to_fetch = [r for r in calls.values() if needs_detail(r)]
        print(f"\n[Phase 2] Update mode: {len(to_fetch)} calls need re-checking…")
    else:
        to_fetch = list(calls.values())
        print(f"\n[Phase 2] Fetching details for all {len(to_fetch)} calls…")

    if args.limit:
        to_fetch = to_fetch[: args.limit]
        print(f"  (limited to {args.limit})")

    for i, record in enumerate(to_fetch):
        identifier = record["identifier"]
        status     = record.get("status") or "unknown"
        n_projects = len(record["projects"]) if isinstance(record.get("projects"), list) else "?"
        print(f"\n  [{i+1}/{len(to_fetch)}] {identifier}  [{status}]  projects={n_projects}")

        fetch_call_detail(record)

        n_after = len(record["projects"]) if isinstance(record.get("projects"), list) else 0
        print(f"    → {n_after} project(s) stored")

        if i < len(to_fetch) - 1:
            time.sleep(DELAY_CALL)

    # ── Save ──────────────────────────────────────────────────────────────────
    save(calls)
    print("\nDone.")


if __name__ == "__main__":
    main()
