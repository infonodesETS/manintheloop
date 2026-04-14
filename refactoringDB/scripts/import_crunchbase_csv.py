#!/usr/bin/env python3
"""
import_crunchbase_csv.py — Import a Crunchbase bulk-enrichment CSV into database.json.

MATCHING (3 tiers, in order)
─────────────────────────────
  1. Exact name      — Organization Name == entity.name
  2. Website         — CB Website == sources.infonodes.website or sources.crunchbase.website
                       (both normalised: https, no www., no trailing slash)
  3. Normalised name — strip legal suffixes, lowercase, collapse whitespace

One CB row can match multiple DB entities (e.g. share classes: Alphabet Class A + Class C
both map to the same Crunchbase profile). All matches receive the same data.

RE-RUN SAFETY (idempotent)
───────────────────────────
  - Always updates sources.crunchbase on match (never skips already-enriched entities).
  - On re-run: computes field-level diff. Only changed fields are listed in the history entry.
  - Unchanged entities (zero field changes) are logged but NOT written — no spurious history noise.
  - source_file + extracted_at stored in every crunchbase block for full provenance.

PRESERVED FIELDS
─────────────────
  board, patents_granted, domain, acquired_by, acquired_by_url, revenue_range
  → These are NOT in the Crunchbase bulk export. If a previous import populated them,
    they are carried forward silently. Never overwritten with null by this script.

OUTPUTS
────────
  - data/database.json updated (unless --dry-run)
  - data/crunchbase_sandbox/import_report_YYYY-MM-DD.json  (full match stats + unresolved list)
  - data/crunchbase_sandbox/unresolved_YYYY-MM-DD.csv      (rows Crunchbase returned but DB
                                                            could not match — for manual review)

RE-RUN CYCLE
─────────────
  1. python3 scripts/regenerate_export.py          # refresh companies_export.csv from DB
  2. (manual) upload companies_export.csv → Crunchbase bulk enrichment → download enriched CSV
  3. python3 scripts/import_crunchbase_csv.py <enriched_csv> [--dry-run]
  4. python3 scripts/validate.py

Usage:
  python3 scripts/import_crunchbase_csv.py <crunchbase_csv> [--dry-run]
"""

import csv
import json
import os
import re
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
SANDBOX_DIR = os.path.join(BASE, "data", "crunchbase_sandbox")

TODAY = date.today().isoformat()

# Fields NOT present in the Crunchbase bulk export — carry forward from old data if set.
_PRESERVE_FIELDS = ["board", "patents_granted", "domain", "acquired_by", "acquired_by_url",
                    "revenue_range"]

# Fields excluded from the diff (metadata, not content)
_DIFF_SKIP = {"extracted_at", "source_file"}


# ── Name / website normalisation ──────────────────────────────────────────────

_STRIP_PATTERNS = [
    r"\bCLASS\s+[A-Z]\b", r"\bSERIES\s+[A-Z]\b",
    r"\bPREF\b", r"\bPREFFERED\b",
    r"\bADR\b", r"\bADS\b", r"\bGDR\b", r"\bORD\b", r"\bNEW\b",
    r"\b[A-Z]\b$",
    r"\bLTD\b", r"\bPLC\b", r"\bINC\b", r"\bCORP\b", r"\bAG\b",
    r"\bSE\b", r"\bSA\b", r"\bNV\b", r"\bASA\b", r"\bAB\b", r"\bOYJ\b",
    r"\bGMBH\b", r"\bSPA\b", r"\bSRL\b", r"\bBV\b",
    r"\bINTERNATIONAL\b",
]


def normalise_name(s: str) -> str:
    """Strip legal suffixes, lowercase, collapse whitespace."""
    s = s.upper()
    for pattern in _STRIP_PATTERNS:
        s = re.sub(pattern, " ", s)
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def normalise_website(url: str) -> str:
    """Normalise URL for comparison: https, no www., no trailing slash."""
    url = url.lower().strip()
    url = url.replace("http://", "https://")
    url = re.sub(r"^https://www\.", "https://", url)
    return url.rstrip("/")


# ── Field parsers ─────────────────────────────────────────────────────────────

def parse_list(value: str) -> list:
    if not value or not value.strip():
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def parse_int(value: str) -> int | None:
    if not value or not value.strip():
        return None
    try:
        return int(float(value.replace(",", "")))
    except (ValueError, TypeError):
        return None


def parse_funding_native(amount: str, currency: str) -> dict | None:
    amt = parse_int(amount)
    if amt is None or not currency or not currency.strip():
        return None
    return {"amount": amt, "currency": currency.strip()}


# ── CB row → sources.crunchbase block ─────────────────────────────────────────

def map_cb_row(row: dict, source_file: str, old_cb: dict | None) -> dict:
    """
    Map a Crunchbase CSV row to a sources.crunchbase block.
    Carries forward preserved fields from old_cb if they were previously set.
    """
    block = {
        "extracted_at": TODAY,
        "source_file": source_file,
        "profile_url": row.get("Organization Name URL") or None,
        "stage": row.get("Stage") or "",
        "description": row.get("Description") or None,
        "description_full": row.get("Full Description") or None,
        "website": row.get("Website") or None,
        "cb_rank": parse_int(row.get("CB Rank (Company)", "")),
        "headquarters": row.get("Headquarters Location") or None,
        "headquarters_regions": row.get("Headquarters Regions") or None,
        "operating_status": row.get("Operating Status") or None,
        "founded_date": row.get("Founded Date") or None,
        "company_type": row.get("Company Type") or None,
        "investment_stage": row.get("Investment Stage") or None,
        "investor_type": row.get("Investor Type") or "",
        "primary_industry": row.get("Primary Industry") or None,
        "primary_industry_url": row.get("Primary Industry URL") or None,
        "industry_groups": parse_list(row.get("Industry Groups", "")),
        "industries": parse_list(row.get("Industries", "")),
        "founders": parse_list(row.get("Founders", "")),
        "num_funding_rounds": parse_int(row.get("Number of Funding Rounds", "")),
        "funding_status": row.get("Funding Status") or None,
        "last_funding_date": row.get("Last Funding Date") or None,
        "last_funding_amount_usd": parse_int(row.get("Last Funding Amount (in USD)", "")),
        "last_funding_type": row.get("Last Funding Type") or None,
        "total_equity_funding_usd": parse_int(
            row.get("Total Equity Funding Amount (in USD)", "")),
        "total_funding_usd": parse_int(row.get("Total Funding Amount (in USD)", "")),
        "total_funding_native": parse_funding_native(
            row.get("Total Funding Amount", ""),
            row.get("Total Funding Amount Currency", ""),
        ),
        "top_investors": parse_list(row.get("Top 5 Investors", "")),
        "num_investors": parse_int(row.get("Number of Investors", "")),
        # Fields not in this export — carry forward from old_cb if set, else null/empty default
        "revenue_range": None,
        "patents_granted": None,
        "domain": None,
        "acquired_by": None,
        "acquired_by_url": None,
        "board": [],
    }

    # Carry forward preserved fields from a previous import
    if old_cb:
        for field in _PRESERVE_FIELDS:
            old_val = old_cb.get(field)
            if old_val:  # non-null, non-empty
                block[field] = old_val

    return block


# ── Diff ──────────────────────────────────────────────────────────────────────

def diff_fields(old: dict | None, new: dict) -> list:
    """Return field names where old and new differ (excludes metadata fields)."""
    if old is None:
        return []
    return [k for k in new if k not in _DIFF_SKIP and old.get(k) != new.get(k)]


# ── Match indexes ─────────────────────────────────────────────────────────────

def build_indexes(db: dict) -> tuple:
    by_name = {}        # exact name → [entity, ...]
    by_website = {}     # normalised website → [entity, ...]
    by_norm_name = {}   # normalised name → [entity, ...]

    for e in db["entities"]:
        if e.get("type") != "company":
            continue

        by_name.setdefault(e["name"], []).append(e)

        src = e.get("sources") or {}
        for ws in filter(None, [
            (src.get("crunchbase") or {}).get("website"),
            (src.get("infonodes") or {}).get("website"),
        ]):
            key = normalise_website(ws)
            if key:
                by_website.setdefault(key, []).append(e)

        nn = normalise_name(e["name"])
        if nn:
            by_norm_name.setdefault(nn, []).append(e)

    return by_name, by_website, by_norm_name


def match_row(row: dict, by_name, by_website, by_norm_name) -> tuple:
    """
    Returns ([matched entities], tier_name).

    Tier 1 — exact name
    Tier 2 — website (normalised)
    Tier 3 — normalised name (strip legal suffixes, lowercase)
    Tier 4 — bidirectional prefix: one normalised name starts with the other
              (min 6 chars). Catches CB canonical truncations, e.g.:
              "RENK Group" → our "Renk", "Phaxiam" → our "Phaxiam Therapeutics"
    """
    cb_name = row["Organization Name"]
    cb_ws = normalise_website(row.get("Website") or "")

    if cb_name in by_name:
        return by_name[cb_name], "exact"
    if cb_ws and cb_ws in by_website:
        return by_website[cb_ws], "website"
    nn = normalise_name(cb_name)
    if nn and nn in by_norm_name:
        return by_norm_name[nn], "normalised"

    # Tier 4: bidirectional prefix on normalised names
    if nn and len(nn) >= 6:
        for key, entities in by_norm_name.items():
            if len(key) < 6:
                continue
            if nn.startswith(key) or key.startswith(nn):
                return entities, "prefix"

    return [], "unresolved"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    pos_args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not pos_args:
        print(__doc__)
        print("Usage: python3 scripts/import_crunchbase_csv.py <crunchbase_csv> [--dry-run]")
        sys.exit(1)

    csv_path = pos_args[0]
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(BASE, csv_path)
    source_file = os.path.basename(csv_path)

    if dry_run:
        print("DRY RUN — no changes will be written to database.json")
    print("=" * 60)
    print(f"Source file: {source_file}")

    # ── Load ───────────────────────────────────────────────────────────────────
    with open(csv_path, encoding="utf-8-sig") as f:
        cb_rows = list(csv.DictReader(f))
    print(f"Crunchbase rows: {len(cb_rows)}")

    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)
    print(f"DB entities:     {sum(1 for e in db['entities'] if e.get('type') == 'company')} companies")

    by_name, by_website, by_norm_name = build_indexes(db)

    # ── Process ────────────────────────────────────────────────────────────────
    stats = {"exact": 0, "website": 0, "normalised": 0, "prefix": 0, "unresolved": 0}
    counts = {"imported": 0, "updated": 0, "unchanged": 0}
    unresolved_rows = []

    print()
    for row in cb_rows:
        entities, tier = match_row(row, by_name, by_website, by_norm_name)
        stats[tier] += 1

        if tier == "unresolved":
            unresolved_rows.append(row)
            print(f"  UNRESOLVED   {row['Organization Name']!r}")
            continue

        for entity in entities:
            old_cb = (entity.get("sources") or {}).get("crunchbase")
            new_cb = map_cb_row(row, source_file, old_cb)
            changed = diff_fields(old_cb, new_cb)
            is_rerun = old_cb is not None

            if is_rerun and not changed:
                counts["unchanged"] += 1
                print(f"  UNCHANGED    {entity['id']} {entity['name']!r} [{tier}]")
                continue

            action = "UPDATE" if is_rerun else "IMPORT"
            detail = f" — {len(changed)} fields changed: {', '.join(changed[:5])}" if changed else ""
            print(f"  {action:<8} {entity['id']} {entity['name']!r} [{tier}]{detail}")

            if dry_run:
                counts["updated" if is_rerun else "imported"] += 1
                continue

            entity["sources"]["crunchbase"] = new_cb
            entity["history"].append({
                "date": TODAY,
                "source": "crunchbase",
                "author": "import_crunchbase_csv.py",
                "field": "sources.crunchbase",
                "old": (f"extracted_at={old_cb['extracted_at']}, "
                        f"source={old_cb.get('source_file', 'unknown')}")
                       if old_cb else None,
                "new": f"extracted_at={TODAY}, source={source_file}",
                "description": (
                    f"sources.crunchbase {'updated' if is_rerun else 'populated'} "
                    f"from {source_file}"
                    + (f". Changed fields: {', '.join(changed)}" if changed else "")
                ),
            })
            entity["validation"].append({
                "status": "crunchbase_enriched",
                "description": (
                    f"sources.crunchbase {'updated' if is_rerun else 'imported'} "
                    f"from {source_file} ({TODAY})"
                    + (f". Changed: {', '.join(changed)}" if changed else "")
                ),
                "author": "import_crunchbase_csv.py",
                "datestamp": TODAY,
            })
            counts["updated" if is_rerun else "imported"] += 1

    # ── Report ─────────────────────────────────────────────────────────────────
    os.makedirs(SANDBOX_DIR, exist_ok=True)

    report = {
        "_generated_at": TODAY,
        "source_file": source_file,
        "dry_run": dry_run,
        "stats": {
            "cb_rows_total": len(cb_rows),
            "matched_exact": stats["exact"],
            "matched_website": stats["website"],
            "matched_normalised": stats["normalised"],
            "matched_prefix": stats["prefix"],
            "unresolved": stats["unresolved"],
            "imported_new": counts["imported"],
            "updated_changed": counts["updated"],
            "unchanged_skipped": counts["unchanged"],
        },
        "unresolved": [
            {"name": r["Organization Name"], "website": r.get("Website", "")}
            for r in unresolved_rows
        ],
    }

    report_path = os.path.join(SANDBOX_DIR, f"import_report_{TODAY}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if unresolved_rows:
        unresolved_csv_path = os.path.join(SANDBOX_DIR, f"unresolved_{TODAY}.csv")
        with open(unresolved_csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["name", "website"])
            w.writeheader()
            w.writerows(
                {"name": r["Organization Name"], "website": r.get("Website", "")}
                for r in unresolved_rows
            )
        print(f"Unresolved CSV:  {unresolved_csv_path}")

    # ── Save DB ────────────────────────────────────────────────────────────────
    if not dry_run:
        db["_updated"] = TODAY
        with open(DATABASE_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Matched exact:        {stats['exact']}")
    print(f"Matched website:      {stats['website']}")
    print(f"Matched normalised:   {stats['normalised']}")
    print(f"Matched prefix:       {stats['prefix']}")
    print(f"Unresolved:           {stats['unresolved']}")
    print(f"Imported (new):       {counts['imported']}")
    print(f"Updated (changed):    {counts['updated']}")
    print(f"Unchanged (skipped):  {counts['unchanged']}")
    print(f"\nReport: {report_path}")
    if not dry_run:
        print(f"Next:   python3 scripts/validate.py")
    else:
        print(f"Re-run without --dry-run to apply.")


if __name__ == "__main__":
    main()
