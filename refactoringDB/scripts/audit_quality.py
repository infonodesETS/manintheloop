#!/usr/bin/env python3
"""
audit_quality.py — Data quality audit for database.json

Audit B: Add reconciliation_documented validation entries for entities
         that combine data from multiple independent source datasets.

Audit C: Add field_conflict validation entries for entities where the same
         semantic field has conflicting values across sources.

Usage:
    python3 scripts/audit_quality.py [--dry-run]

Flags:
    --dry-run   Print report only; do not modify database.json

Output:
    Prints a summary report.
    Writes validation[] entries to database.json (unless --dry-run).
"""

import json
import sys
from datetime import date
from collections import defaultdict

DRY_RUN = "--dry-run" in sys.argv
TODAY = date.today().isoformat()
DB_PATH = "data/database.json"

db = json.load(open(DB_PATH))
entities = db["entities"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def has_validation_status(entity, status):
    return any(v.get("status") == status for v in entity.get("validation", []))


def add_validation(entity, status, description):
    if not has_validation_status(entity, status):
        entity.setdefault("validation", []).append({
            "status": status,
            "description": description,
            "author": "audit_quality.py",
            "datestamp": TODAY,
        })
        return True
    return False


def source_present(entity, *keys):
    src = entity.get("sources") or {}
    return all(src.get(k) for k in keys)


def source_any(entity, *keys):
    src = entity.get("sources") or {}
    return any(src.get(k) for k in keys)


# ---------------------------------------------------------------------------
# Audit B — Reconciliation documentation
# ---------------------------------------------------------------------------

b_counts = defaultdict(int)

for e in entities:
    src = e.get("sources") or {}

    # --- Group 1: edf + ishares (2 entities)
    # Company appears in both iShares ETF holdings AND EDF beneficiary datasets.
    # Match was made during build_edf_entities.py via name_key normalization.
    if src.get("edf") and src.get("ishares"):
        added = add_validation(
            e,
            "reconciliation_documented",
            (
                "Entity appears in both iShares ETF holdings and EDF beneficiary datasets. "
                "Cross-dataset match performed by build_edf_entities.py via normalised name_key. "
                "Basis: name normalisation (strip legal suffixes, uppercase, collapse whitespace)."
            ),
        )
        if added:
            b_counts["edf+ishares"] += 1

    # --- Group 2: crunchbase entities (130)
    # Migrated wholesale from refactoring/ legacy DB (investments.json v1).
    # All have double migration history entries confirming name-based match.
    elif src.get("crunchbase"):
        mig_descs = [
            h.get("description", "")
            for h in e.get("history", [])
            if h.get("source") == "migration"
        ]
        old_id = None
        for d in mig_descs:
            if "old id:" in d:
                # Extract old id from description
                try:
                    old_id = d.split("old id:")[1].split(",")[0].strip().split(")")[0].strip()
                except Exception:
                    pass
        basis = (
            f"Entity migrated from refactoring/ legacy DB "
            f"(investments.json v1 → refactoring/data/database.json"
            f"{', old id: ' + old_id if old_id else ''}). "
            "Match basis: name identity between legacy DB and new DB entity pool "
            "(startup name match, no universal ID available at migration time)."
        )
        added = add_validation(e, "reconciliation_documented", basis)
        if added:
            b_counts["crunchbase_migration"] += 1

    # --- Group 3: migration-only entities without crunchbase (33)
    # Existing iShares entities whose wikidata_id was matched from legacy DB
    # via normalised name comparison (import_by_wikidata.py pattern).
    elif any(h.get("source") == "migration" for h in e.get("history", [])):
        mig_hist = [
            h for h in e.get("history", []) if h.get("source") == "migration"
        ]
        desc_text = " ".join(h.get("description", "") for h in mig_hist)
        if "wikidata_id set from refactoring" in desc_text or "Match confirmed via normalized name" in desc_text:
            added = add_validation(
                e,
                "reconciliation_documented",
                (
                    "wikidata_id resolved by matching this entity against refactoring/ legacy DB "
                    "via normalised name comparison (strip legal suffixes, uppercase, collapse whitespace). "
                    "Cross-dataset enrichment only — entity was independently created in new DB from iShares data."
                ),
            )
            if added:
                b_counts["wikidata_name_match"] += 1

# ---------------------------------------------------------------------------
# Audit C — Field-level conflict detection
# ---------------------------------------------------------------------------

c_counts = defaultdict(int)

for e in entities:
    src = e.get("sources") or {}
    info = src.get("infonodes") or {}
    cb = src.get("crunchbase") or {}
    wd = src.get("wikidata") or {}

    conflict_notes = []

    # --- Country conflict (wikidata vs infonodes) ---
    wd_country = wd.get("country") or ""
    info_country = info.get("country") or ""
    if wd_country and info_country and wd_country != info_country:
        wd_norm = (
            wd_country.lower()
            .replace("people's republic of ", "")
            .replace("republic of ", "")
        )
        info_norm = info_country.lower()

        if wd_norm == info_norm:
            # Normalisation difference only (e.g. "People's Republic of China" vs "China")
            conflict_notes.append(
                f"country normalisation gap: sources.wikidata.country='{wd_country}' "
                f"vs sources.infonodes.country='{info_country}' — same country, different form; "
                "recommend standardising to ISO 3166 short name."
            )
            c_counts["country_normalization"] += 1
        else:
            # Real conflict
            conflict_notes.append(
                f"country real conflict: sources.wikidata.country='{wd_country}' "
                f"vs sources.infonodes.country='{info_country}' — "
                "sources disagree; manual review required to set canonical value."
            )
            c_counts["country_real"] += 1

    # --- Headquarters conflict (wikidata vs crunchbase) ---
    wd_hq = wd.get("headquarters") or ""
    cb_hq = cb.get("headquarters") or ""
    if wd_hq and cb_hq and wd_hq != cb_hq:
        if wd_hq.lower() in cb_hq.lower():
            # Granularity difference only (wikidata=city, crunchbase=city+region+country)
            # Document but do not flag as conflict
            c_counts["hq_granularity"] += 1
        else:
            conflict_notes.append(
                f"headquarters real conflict: sources.wikidata.headquarters='{wd_hq}' "
                f"vs sources.crunchbase.headquarters='{cb_hq}' — "
                "sources disagree; manual review required to set canonical value."
            )
            c_counts["hq_real"] += 1

    if conflict_notes:
        description = " | ".join(conflict_notes)
        added = add_validation(e, "field_conflict", description)
        if added:
            c_counts["field_conflict_entries"] += 1

# ---------------------------------------------------------------------------
# Write DB and report
# ---------------------------------------------------------------------------

if not DRY_RUN:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Written: {DB_PATH}")
else:
    print("DRY RUN — no changes written.\n")

print("=" * 60)
print("AUDIT B — Reconciliation documentation")
print("=" * 60)
print(f"  edf+ishares cross-dataset matches documented:  {b_counts['edf+ishares']}")
print(f"  crunchbase legacy-DB migrations documented:    {b_counts['crunchbase_migration']}")
print(f"  wikidata name-match enrichments documented:    {b_counts['wikidata_name_match']}")
b_total = sum(b_counts.values())
print(f"  TOTAL new reconciliation_documented entries:   {b_total}")

print()
print("=" * 60)
print("AUDIT C — Field conflict detection")
print("=" * 60)
print(f"  country normalisation gaps (same country):     {c_counts['country_normalization']}")
print(f"  country real conflicts (sources disagree):     {c_counts['country_real']}")
print(f"  HQ granularity differences (city vs full):     {c_counts['hq_granularity']}  [not flagged]")
print(f"  HQ real conflicts (sources disagree):          {c_counts['hq_real']}")
print(f"  TOTAL new field_conflict entries:              {c_counts['field_conflict_entries']}")
