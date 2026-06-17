#!/usr/bin/env python3
"""
import_investors_csv.py — Build IV-NNNN investor entities and REL-NNNN investment
relationships from the Crunchbase bulk-enrichment CSV.

SOURCE FIELDS USED
───────────────────
  Top 5 Investors   → investor appeared in portfolio company's top 5
  Lead Investors    → investor led at least one round for this company

WHAT IT BUILDS
───────────────
  For each unique investor name found across all CSV rows:
    → one IV-NNNN entity  (type inferred: fund/corporate/gov/bank)
    → one REL-NNNN per portfolio company  (details.lead = True if in Lead Investors)

MATCHING PORTFOLIO COMPANIES
──────────────────────────────
  CSV row → DB entity matched via sources.crunchbase.profile_url (exact) then
  normalised name (strip legal suffixes, lowercase). Only entities already in
  the DB with sources.crunchbase are considered (they were matched in cycle 1).

RE-RUN SAFETY
──────────────
  - Existing IV-NNNN entities (matched by normalised name) are NOT recreated.
    Their portfolio is extended with any new REL-NNNN relationships.
  - Existing REL-NNNN (same investor_id + target_id) are NOT duplicated.
  - Running twice produces identical output.

Usage:
  python3 scripts/import_investors_csv.py <crunchbase_csv> [--dry-run]

Example:
  python3 scripts/import_investors_csv.py \\
      data/crunchbase_sandbox/crunchbase-export-matches-csv-4-13-2026.csv --dry-run
"""

import csv
import json
import os
import re
import sys
from datetime import date

BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH     = os.path.join(BASE, "data", "database.json")
TODAY       = date.today().isoformat()
DRY_RUN     = "--dry-run" in sys.argv

# ── CLI ───────────────────────────────────────────────────────────────────────

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    print("Usage: python3 scripts/import_investors_csv.py <csv_path> [--dry-run]")
    sys.exit(1)

CSV_PATH = args[0]
if not os.path.exists(CSV_PATH):
    print(f"Error: file not found: {CSV_PATH}")
    sys.exit(1)

# ── Helpers ───────────────────────────────────────────────────────────────────

_LEGAL = [
    r"\bCLASS\s+[A-Z]\b", r"\bSERIES\s+[A-Z]\b",
    r"\bPREF\b", r"\bPREFFERED\b",
    r"\bADR\b", r"\bADS\b", r"\bGDR\b", r"\bORD\b", r"\bNEW\b",
    r"\b[A-Z]\b$",
    r"\bLTD\b", r"\bPLC\b", r"\bINC\b", r"\bCORP\b", r"\bAG\b",
    r"\bSE\b", r"\bSA\b", r"\bNV\b", r"\bASA\b", r"\bAB\b", r"\bOYJ\b",
    r"\bGMBH\b", r"\bSPA\b", r"\bSRL\b", r"\bBV\b",
    r"\bINTERNATIONAL\b",
]

def norm_name(s: str) -> str:
    s = s.upper()
    for p in _LEGAL:
        s = re.sub(p, " ", s)
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()

def parse_list(val: str) -> list[str]:
    if not val or not val.strip():
        return []
    return [v.strip() for v in val.split(",") if v.strip()]

def infer_type(name: str) -> str:
    """Rough heuristic: fund / bank / gov / corporate."""
    n = name.lower()
    gov_kw  = ["department", "ministry", "agency", "office", "government",
                "federal", "national", "european commission", "eismea",
                "eic accelerator", "arpa", "darpa", "nato"]
    bank_kw = ["bank", "securities", "credit", "capital markets",
                "investment bank", "hsbc", "goldman", "morgan stanley",
                "jp morgan", "barclays", "bnp", "deutsche bank", "citigroup"]
    corp_kw = ["corporate", "ventures", "venture arm"]
    if any(k in n for k in gov_kw):
        return "government_agency"
    if any(k in n for k in bank_kw):
        return "bank"
    return "fund"

def next_id(prefix: str, existing: set[str]) -> str:
    nums = [int(i[len(prefix):]) for i in existing if i.startswith(prefix)]
    n = max(nums, default=0) + 1
    return f"{prefix}{n:04d}"

# ── Load DB ───────────────────────────────────────────────────────────────────

print(f"Loading {DB_PATH} …")
with open(DB_PATH) as f:
    db = json.load(f)

entities      = db["entities"]
relationships = db.get("relationships", [])

# Index existing entities
existing_ids   = {e["id"] for e in entities}
existing_rels  = {(r["source"], r["target"]) for r in relationships}

# Index IN- entities: by profile_url and by norm_name
url_to_db:  dict[str, str] = {}   # cb profile_url → entity id
name_to_db: dict[str, str] = {}   # norm_name      → entity id

for e in entities:
    cb = (e.get("sources") or {}).get("crunchbase") or {}
    pu = cb.get("profile_url")
    if pu:
        url_to_db[pu.strip().rstrip("/")] = e["id"]
    name_to_db[norm_name(e["name"])] = e["id"]

# Index existing IV- entities by norm_name
iv_by_norm: dict[str, str] = {}   # norm_name → IV id
for e in entities:
    if e["id"].startswith("IV-"):
        iv_by_norm[norm_name(e["name"])] = e["id"]

# ── Parse CSV ─────────────────────────────────────────────────────────────────

print(f"Reading {CSV_PATH} …")
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

source_file = os.path.basename(CSV_PATH)

# Build: investor_name → { top5: set[db_entity_id], lead: set[db_entity_id] }
inv_portfolio: dict[str, dict] = {}

unmatched_companies = []

for row in rows:
    cb_name    = row.get("Organization Name", "").strip()
    cb_url     = (row.get("Organization Name URL") or "").strip().rstrip("/")
    top5_raw   = parse_list(row.get("Top 5 Investors", ""))
    lead_raw   = parse_list(row.get("Lead Investors", ""))

    # Match CSV row → DB entity
    db_id = url_to_db.get(cb_url) or name_to_db.get(norm_name(cb_name))
    if not db_id:
        unmatched_companies.append(cb_name)
        continue

    all_investors = set(top5_raw) | set(lead_raw)
    lead_set      = set(lead_raw)

    for inv_name in all_investors:
        if inv_name not in inv_portfolio:
            inv_portfolio[inv_name] = {"top5": set(), "lead": set(), "db_ids": set()}
        inv_portfolio[inv_name]["db_ids"].add(db_id)
        if inv_name in top5_raw:
            inv_portfolio[inv_name]["top5"].add(db_id)
        if inv_name in lead_set:
            inv_portfolio[inv_name]["lead"].add(db_id)

# ── Build new entities and relationships ──────────────────────────────────────

new_entities      = []
new_relationships = []
skipped_iv        = 0
skipped_rel       = 0

# Sort investor names for deterministic IV-NNNN assignment
for inv_name in sorted(inv_portfolio.keys()):
    data       = inv_portfolio[inv_name]
    norm       = norm_name(inv_name)
    portfolio  = data["db_ids"]
    lead_ids   = data["lead"]

    # Resolve or create IV entity
    if norm in iv_by_norm:
        iv_id = iv_by_norm[norm]
        skipped_iv += 1
    else:
        iv_id = next_id("IV-", existing_ids | {e["id"] for e in new_entities})
        iv_entity = {
            "id":         iv_id,
            "type":       infer_type(inv_name),
            "roles":      ["investor"],
            "name":       inv_name,
            "sector":     None,
            "wikidata_id": None,
            "sources": {
                "infonodes":  None,
                "wikidata":   None,
                "crunchbase": None,
                "ishares":    [],
            },
            "history": [{
                "date":        TODAY,
                "source":      "crunchbase",
                "author":      "import_investors_csv.py",
                "field":       "*",
                "old":         None,
                "new":         None,
                "description": (
                    f"Extracted from investor strings in {source_file}. "
                    f"Portfolio: {len(portfolio)} compan{'y' if len(portfolio)==1 else 'ies'}, "
                    f"{len(lead_ids)} as lead."
                ),
            }],
            "validation": [],
            "tags":       [],
        }
        new_entities.append(iv_entity)
        iv_by_norm[norm] = iv_id
        existing_ids.add(iv_id)

    # Create REL-NNNN for each portfolio company
    for target_id in sorted(portfolio):
        if (iv_id, target_id) in existing_rels:
            skipped_rel += 1
            continue
        rel_id = next_id("REL-", {r["id"] for r in relationships} | {r["id"] for r in new_relationships})
        is_lead = target_id in lead_ids
        rel = {
            "id":       rel_id,
            "type":     "investment",
            "source":   iv_id,
            "target":   target_id,
            "details":  {"lead": is_lead},
            "sources":  ["crunchbase"],
            "added_at": TODAY,
            "author":   "import_investors_csv.py",
        }
        new_relationships.append(rel)
        existing_rels.add((iv_id, target_id))

# ── Report ────────────────────────────────────────────────────────────────────

total_investors  = len(inv_portfolio)
total_rels       = sum(len(d["db_ids"]) for d in inv_portfolio.values())
lead_rels        = sum(len(d["lead"])   for d in inv_portfolio.values())

print()
print("=" * 60)
print(f"  Investors found in CSV:       {total_investors}")
print(f"  IV entities to create:        {len(new_entities)}")
print(f"  IV entities already existed:  {skipped_iv}")
print(f"  REL to create:                {len(new_relationships)}")
print(f"  REL already existed:          {skipped_rel}")
print(f"  Lead relationships:           {lead_rels} / {total_rels}")
print(f"  Companies unmatched in DB:    {len(unmatched_companies)}")
if unmatched_companies:
    for c in unmatched_companies[:10]:
        print(f"    - {c}")
    if len(unmatched_companies) > 10:
        print(f"    … and {len(unmatched_companies)-10} more")
print("=" * 60)

# Top 10 investors by portfolio size
top10 = sorted(inv_portfolio.items(), key=lambda x: -len(x[1]["db_ids"]))[:10]
print("\nTop 10 investors by portfolio size in DB:")
for inv_name, d in top10:
    print(f"  {len(d['db_ids']):3d} companies  ({len(d['lead'])} lead)  {inv_name}")

if DRY_RUN:
    print("\n[dry-run] No changes written.")
    sys.exit(0)

# ── Write ─────────────────────────────────────────────────────────────────────

db["entities"]      = entities + new_entities
db["relationships"] = relationships + new_relationships
db["_updated"]      = TODAY

with open(DB_PATH, "w") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"\n✓ Written: {len(new_entities)} IV entities, {len(new_relationships)} REL entries → {DB_PATH}")
print("  Run: python3 scripts/validate.py")
