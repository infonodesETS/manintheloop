#!/usr/bin/env python3
"""
build_edf_entities.py — Extract EDF participant organisations from edf_calls.json
and merge them into database.json.

For each unique organisation (by PIC):
  - Aggregates stats: total EU contribution, project count, call count, coordinator count.
  - Maps EDF type code to entity type:
      PRC → company
      HES → institution  (Higher Education)
      REC → institution  (Research org)
      PUB → government_agency
      OTH → institution
  - Tries to match against existing database.json entities by normalized name.
  - Match: adds sources.edf block + history entry (no new entity created).
  - No match: creates new IN-NNNN entity with sources.edf.

Also writes data/edf_orgs.json — a flat PIC-keyed index for reference.

Usage:
    python3 scripts/build_edf_entities.py [--dry-run]

Run from the refactoringDB/ root directory.
"""

import json
import os
import re
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDF_CALLS_PATH = os.path.join(BASE, "rawdata", "edf_calls.json")
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
EDF_ORGS_PATH = os.path.join(BASE, "data", "edf_orgs.json")

TODAY = date.today().isoformat()

# ── Type code → entity type mapping ──────────────────────────────────────────
TYPE_MAP = {
    "PRC": "company",          # Private company
    "HES": "institution",      # Higher Education & Secondary
    "REC": "institution",      # Research organisation
    "PUB": "government_agency",
    "OTH": "institution",
}

# Legal suffixes to strip for name normalization (same pattern as parse_ishares.py)
_LEGAL_SUFFIXES = [
    r"\bCORPORATION\b", r"\bCORPORATE\b", r"\bCORPORA[TT]ION\b",
    r"\bCORP\b", r"\bLIMITED\b", r"\bLTD\b",
    r"\bINCORPORATED\b", r"\bINC\b",
    r"\bPUBLIC LIMITED COMPANY\b", r"\bPLC\b",
    r"\bSOCIETE ANONYME\b", r"\bS\.?A\.?\b",
    r"\bN\.?V\.?\b", r"\bGMBH\b", r"\bKGAA\b",
    r"\bAKTIENGESELLSCHAFT\b", r"\bAG\b",
    r"\bSE\b", r"\bSPA\b", r"\bS\.?P\.?A\.?\b",
    r"\bAB\b", r"\bASA\b", r"\bOYJ\b", r"\bOY\b",
    r"\bCOMPANY\b", r"\bCO\b",
    r"\bGROUP\b", r"\bGROUPE\b",
    r"\bHOLDINGS?\b",
    r"\bINTERNATIONAL\b", r"\bINTL\b",
    r"\bSH\b", r"\bCIA\b",
    r"\bGMBH\b", r"\bKG\b",
    r"\bSARL\b", r"\bSAS\b", r"\bSNC\b",
    r"\bBV\b", r"\bSRL\b",
    r"\bUNIVERSITY\b", r"\bUNIVERSITÀ\b", r"\bUNIVERSIDAD\b",
    r"\bUNIVERSITÄT\b", r"\bUNIVERSITEIT\b", r"\bUNIVERSITE\b",
]


def normalize_name(raw: str) -> str:
    """Strip legal suffixes and normalize to uppercase for comparison."""
    s = raw.upper().strip()
    for pattern in _LEGAL_SUFFIXES:
        s = re.sub(pattern, " ", s)
    s = re.sub(r"[,.\-/&]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def significant_tokens(name_key: str, min_len: int = 3) -> list[str]:
    """Return tokens of length >= min_len for subset matching."""
    return [t for t in name_key.split() if len(t) >= min_len]


def clean_csv_name(raw: str) -> str:
    """
    Strip outer CSV quoting and unescape doubled double-quotes.
    Some EDF org names arrive as: '"NAME WITH ""NICKNAME"""'
    Correct result: 'NAME WITH "NICKNAME"'
    """
    s = raw.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    s = s.replace('""', '"')
    return s.strip()


def display_name(raw: str) -> str:
    """Title-case the name with CSV artifacts and legal suffixes stripped."""
    cleaned = clean_csv_name(raw)
    key = normalize_name(cleaned)
    # Preserve quoted nicknames (e.g. "Elie Carafoli") with title case
    result = key.title()
    return result


# ── Step 1: Extract and aggregate unique orgs from edf_calls.json ─────────────

def extract_edf_orgs(edf_calls_path: str) -> dict[str, dict]:
    """
    Returns a dict: pic → aggregated org record.

    Each record:
        pic, organization_name, activity_type, type_code, entity_type,
        sme, country, country_code, city, postal_code, street,
        web_link, eu_url,
        total_eu_contribution (float),
        project_count (int), call_count (int), coordinator_count (int),
        calls (set of call identifiers), projects (set of project ids)
    """
    with open(edf_calls_path, encoding="utf-8") as f:
        data = json.load(f)

    orgs: dict[str, dict] = {}
    calls_dict = data.get("calls", {})

    for call_id, call in calls_dict.items():
        for proj in (call.get("projects") or []):
            proj_id = proj.get("project_id") or proj.get("acronym") or "?"
            for part in (proj.get("participants") or []):
                pic = str(part.get("pic", "")).strip()
                if not pic:
                    continue

                contribution = 0.0
                try:
                    contribution = float(part.get("eu_contribution") or 0)
                except (ValueError, TypeError):
                    pass

                is_coordinator = (part.get("role") or "").lower() == "coordinator"
                type_code = (part.get("type") or "OTH").upper()

                if pic not in orgs:
                    orgs[pic] = {
                        "pic": pic,
                        "organization_name": part.get("organization_name", ""),
                        "activity_type": part.get("activity_type") or "",
                        "type_code": type_code,
                        "entity_type": TYPE_MAP.get(type_code, "institution"),
                        "sme": part.get("sme"),
                        "country": part.get("country") or None,
                        "country_code": part.get("country_code") or None,
                        "city": part.get("city") or None,
                        "postal_code": part.get("postal_code") or None,
                        "street": part.get("street") or None,
                        "web_link": part.get("web_link") or None,
                        "eu_url": part.get("eu_url") or None,
                        "total_eu_contribution": 0.0,
                        "project_count": 0,
                        "call_count": 0,
                        "coordinator_count": 0,
                        "_call_set": set(),
                        "_project_set": set(),
                    }

                org = orgs[pic]
                org["total_eu_contribution"] += contribution
                org["_project_set"].add(proj_id)
                org["_call_set"].add(call_id)
                if is_coordinator:
                    org["coordinator_count"] += 1

    # Finalize counts and remove internal sets
    for org in orgs.values():
        org["project_count"] = len(org["_project_set"])
        org["call_count"] = len(org["_call_set"])
        del org["_project_set"]
        del org["_call_set"]
        org["total_eu_contribution"] = round(org["total_eu_contribution"], 2)

    return orgs


def build_sources_edf_block(org: dict) -> dict:
    """Build a sources.edf block from an aggregated org record."""
    return {
        "extracted_at": TODAY,
        "pic": org["pic"],
        "eu_url": org["eu_url"],
        "activity_type": org["activity_type"],
        "type_code": org["type_code"],
        "sme": org["sme"],
        "country": org["country"],
        "country_code": org["country_code"],
        "city": org["city"],
        "web_link": org["web_link"],
        "total_eu_contribution": org["total_eu_contribution"],
        "project_count": org["project_count"],
        "call_count": org["call_count"],
        "coordinator_count": org["coordinator_count"],
        "source_file": "edf_calls.json",
    }


# ── Step 2: Build name index for existing entities ────────────────────────────

def build_name_index(entities: list[dict]) -> dict[str, str]:
    """
    Returns: normalized_name_key → entity_id
    Used for matching EDF orgs against existing database entities.
    """
    index = {}
    for e in entities:
        key = normalize_name(e.get("name", ""))
        if key:
            index[key] = e["id"]
    return index


def find_match(
    org_name: str,
    name_index: dict[str, str],
    entities_by_id: dict[str, dict],
) -> str | None:
    """
    Try to match an EDF org name against existing entities.
    Returns matched entity id or None.

    Tier 1: exact normalized name match.
    Tier 2: subset token match — all ≥3-char tokens of the shorter name
            appear in the longer name's token set.
    """
    org_key = normalize_name(org_name)
    if not org_key:
        return None

    # Tier 1: exact
    if org_key in name_index:
        return name_index[org_key]

    # Tier 2: subset tokens
    # All tokens of the shorter name must appear in the longer AND must cover
    # at least 60% of the longer name's tokens to avoid false positives.
    org_tokens = set(significant_tokens(org_key))
    if len(org_tokens) < 2:
        return None  # too ambiguous with a single token

    for db_key, eid in name_index.items():
        db_tokens = set(significant_tokens(db_key))
        if len(db_tokens) < 2:
            continue
        shorter = org_tokens if len(org_tokens) <= len(db_tokens) else db_tokens
        longer = db_tokens if len(org_tokens) <= len(db_tokens) else org_tokens
        if shorter and shorter.issubset(longer):
            coverage = len(shorter) / len(longer)
            if coverage >= 0.6:
                return eid

    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main(dry_run: bool = False):
    # ── Load inputs ───────────────────────────────────────────────────────────
    print("Extracting EDF organisations...")
    edf_orgs = extract_edf_orgs(EDF_CALLS_PATH)
    print(f"  Unique orgs (by PIC): {len(edf_orgs)}")

    type_counts: dict[str, int] = {}
    for o in edf_orgs.values():
        t = o["entity_type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, n in sorted(type_counts.items()):
        print(f"    {t}: {n}")

    print(f"\nLoading database.json...")
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    entities: list[dict] = db["entities"]
    print(f"  Existing entities: {len(entities)}")

    # Find max IN-NNNN ID
    max_in = 0
    for e in entities:
        eid = e.get("id", "")
        if eid.startswith("IN-"):
            try:
                n = int(eid[3:])
                if n > max_in:
                    max_in = n
            except ValueError:
                pass

    entities_by_id: dict[str, dict] = {e["id"]: e for e in entities}
    name_index = build_name_index(entities)

    # ── Match and merge ───────────────────────────────────────────────────────
    print(f"\nMatching EDF orgs against existing entities...")
    matched = 0
    created = 0
    next_in = max_in + 1

    # Collect new entities separately (sort alphabetically before assigning IDs)
    new_entities_staging: list[dict] = []  # list of org dicts that need new IDs

    pic_to_db_id: dict[str, str] = {}  # pic → db entity id (for edf_orgs.json)

    for pic, org in edf_orgs.items():
        org_name = org["organization_name"]
        match_id = find_match(org_name, name_index, entities_by_id)

        if match_id:
            # Add sources.edf to existing entity
            entity = entities_by_id[match_id]
            if "sources" not in entity or entity["sources"] is None:
                entity["sources"] = {}
            entity["sources"]["edf"] = build_sources_edf_block(org)
            entity["history"].append({
                "date": TODAY,
                "source": "edf",
                "author": "build_edf_entities.py",
                "field": "sources.edf",
                "old": None,
                "new": None,
                "description": (
                    f"EDF participant data added: PIC {pic}, "
                    f"{org['project_count']} projects, "
                    f"€{org['total_eu_contribution']:,.0f} EU contribution"
                ),
            })
            pic_to_db_id[pic] = match_id
            matched += 1
        else:
            new_entities_staging.append(org)

    # Sort new entities alphabetically and assign IN-NNNN IDs
    new_entities_staging.sort(key=lambda o: normalize_name(o["organization_name"]))

    for org in new_entities_staging:
        in_id = f"IN-{next_in:04d}"
        next_in += 1
        pic = org["pic"]

        entity = {
            "id": in_id,
            "type": org["entity_type"],
            "roles": ["manufacturer"],
            "name": display_name(org["organization_name"]),
            "sector": None,
            "wikidata_id": None,
            "sources": {
                "edf": build_sources_edf_block(org),
                "ishares": None,
                "crunchbase": None,
                "infonodes": None,
                "wikidata": None,
            },
            "history": [
                {
                    "date": TODAY,
                    "source": "edf",
                    "author": "build_edf_entities.py",
                    "field": "*",
                    "old": None,
                    "new": None,
                    "description": (
                        f"Initial import from EDF calls data: PIC {pic}, "
                        f"{org['project_count']} projects, "
                        f"€{org['total_eu_contribution']:,.0f} EU contribution"
                    ),
                }
            ],
            "validation": [
                {
                    "status": "needs_review",
                    "description": (
                        "Entity added from EDF participant data. "
                        "Roles and sector need manual review. "
                        "Check if this org appears in iShares ETFs or Crunchbase."
                    ),
                    "author": "build_edf_entities.py",
                    "datestamp": TODAY,
                }
            ],
            "tags": [],
        }
        entities.append(entity)
        entities_by_id[in_id] = entity
        # Rebuild name index entry
        key = normalize_name(org["organization_name"])
        if key:
            name_index[key] = in_id
        pic_to_db_id[pic] = in_id
        created += 1

    # ── Build edf_orgs.json ───────────────────────────────────────────────────
    edf_orgs_output: dict[str, dict] = {}
    for pic, org in edf_orgs.items():
        db_id = pic_to_db_id.get(pic)
        edf_orgs_output[pic] = {
            "pic": pic,
            "organization_name": org["organization_name"],
            "activity_type": org["activity_type"],
            "type_code": org["type_code"],
            "country": org["country"],
            "country_code": org["country_code"],
            "city": org["city"],
            "web_link": org["web_link"],
            "total_eu_contribution": org["total_eu_contribution"],
            "project_count": org["project_count"],
            "call_count": org["call_count"],
            "coordinator_count": org["coordinator_count"],
            "db_id": db_id,
            "match_method": "auto_name" if db_id else None,
            "match_confidence": "suggested" if db_id else None,
        }

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n  Matched to existing entities: {matched}")
    print(f"  New entities created:         {created}")
    print(f"  Total entities after merge:   {len(entities)}")

    if dry_run:
        print("\n[DRY RUN] No files written.")
        return

    # ── Write outputs ─────────────────────────────────────────────────────────
    db["entities"] = entities
    db["_updated"] = TODAY

    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"\n✓ database.json updated.")

    with open(EDF_ORGS_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "_generated_at": TODAY,
            "_total_orgs": len(edf_orgs_output),
            "_matched": matched,
            "_new": created,
            "orgs": edf_orgs_output,
        }, f, ensure_ascii=False, indent=2)
    print(f"✓ edf_orgs.json written ({len(edf_orgs_output)} orgs).")
    print(f"\nNext steps:")
    print(f"  1. python3 scripts/validate.py")
    print(f"  2. Review auto-matched entries in data/edf_orgs.json")
    print(f"     (set match_confidence: 'confirmed' after manual check)")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)
