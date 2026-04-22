#!/usr/bin/env python3
"""
migrate_old_db_investors.py — Migrate funds, banks and investment relationships
from the legacy DB (../refactoring/data/database.json) to the new DB.

WHAT IT DOES
────────────
1. Reads all fund/bank/government_agency/company entities from old DB that
   appear as relationship sources.
2. Maps each to an existing IV-* entity in new DB (exact name match, lowercase),
   OR creates a new IV-NNNN entity for genuinely new investors.
   Exception: old IN-* company sources (e.g. BHP, Leonardo) are mapped to
   their existing IN-* counterparts in the new DB by name.
3. Maps old relationship targets (IN-* in old DB) to new DB entities via
   wikidata_id (priority) or name match.
4. Creates new investment relationships, skipping duplicates.

RE-RUN SAFETY
─────────────
Idempotent — skips entities and relationships already present.

Usage:
  python3 scripts/migrate_old_db_investors.py [--dry-run]
"""

import json, os, re, sys
from datetime import date

BASE          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_DB_PATH   = os.path.join(BASE, "..", "refactoring", "data", "database.json")
NEW_DB_PATH   = os.path.join(BASE, "data", "database.json")
TODAY         = date.today().isoformat()
DRY_RUN       = "--dry-run" in sys.argv

# Old type → new type mapping (government_agency stays; fund/bank stay)
TYPE_MAP = {
    "fund":               "fund",
    "bank":               "bank",
    "government_agency":  "government_agency",
    "company":            "company",
    "institution":        "institution",
}


def next_iv_id(entities: list) -> str:
    nums = [int(e["id"].split("-")[1]) for e in entities if e["id"].startswith("IV-")]
    return f"IV-{(max(nums, default=0) + 1):04d}"


def make_iv_entity(old_ent: dict, new_id: str) -> dict:
    wd_src = old_ent.get("sources", {}).get("wikidata") or None
    cb_src = old_ent.get("sources", {}).get("crunchbase") or None
    inf    = old_ent.get("sources", {}).get("infonodes") or None
    return {
        "id":          new_id,
        "type":        TYPE_MAP.get(old_ent["type"], "investor"),
        "roles":       old_ent.get("roles", ["investor"]),
        "name":        old_ent["name"],
        "sector":      old_ent.get("sector"),
        "wikidata_id": old_ent.get("wikidata_id"),
        "sources": {
            "edf":        None,
            "ishares":    None,
            "crunchbase": cb_src,
            "infonodes":  inf or {
                "extracted_at":  TODAY,
                "sector":        None,
                "country":       None,
                "tax_id":        None,
                "main_focus":    None,
                "wikipedia_url": None,
                "website":       None,
            },
            "wikidata":   wd_src,
        },
        "history": [{
            "date":        TODAY,
            "source":      "migration",
            "author":      "migrate_old_db_investors.py",
            "field":       "*",
            "old":         None,
            "new":         None,
            "description": f"Migrated from legacy DB (old id: {old_ent['id']})",
        }],
        "validation": [{
            "status":      "needs_review",
            "description": "Migrated from legacy refactoring DB. Review country/HQ data.",
            "author":      "migrate_old_db_investors.py",
            "datestamp":   TODAY,
        }],
        "tags": old_ent.get("tags", []),
    }


def make_relationship(src_id: str, tgt_id: str, old_rel: dict) -> dict:
    rel = {
        "source":     src_id,
        "target":     tgt_id,
        "type":       old_rel.get("type", "investment"),
        "source_ref": "legacy_db_migration",
        "created_at": TODAY,
    }
    if old_rel.get("details"):
        rel["details"] = old_rel["details"]
    return rel


def main():
    with open(OLD_DB_PATH, encoding="utf-8") as f:
        old_db = json.load(f)
    with open(NEW_DB_PATH, encoding="utf-8") as f:
        new_db = json.load(f)

    old_entities = {e["id"]: e for e in old_db["entities"]}
    new_entities  = new_db["entities"]
    new_rels      = new_db["relationships"]

    # ── Build new DB lookups ──────────────────────────────────────────────────
    new_iv_by_name  = {e["name"].lower().strip(): e for e in new_entities if e["id"].startswith("IV-")}
    new_in_by_name  = {e["name"].lower().strip(): e for e in new_entities if e["id"].startswith("IN-")}
    new_by_wikidata = {e["wikidata_id"]: e for e in new_entities if e.get("wikidata_id")}
    new_by_name_all = {e["name"].lower().strip(): e for e in new_entities}

    existing_rel_pairs = {(r["source"], r["target"]) for r in new_rels}

    # ── Map old source IDs → new IDs ─────────────────────────────────────────
    old_src_to_new: dict[str, str] = {}
    to_create: list[dict] = []     # new IV entities to add
    created_map: dict[str, str] = {}  # old_id → new_id for entities to create

    for old_id, old_e in old_entities.items():
        if old_e["type"] not in ("fund", "bank", "government_agency", "company"):
            continue
        name_key = old_e["name"].lower().strip()

        if old_e["type"] == "company":
            # Map to existing IN-* in new DB
            match = new_in_by_name.get(name_key)
            if match:
                old_src_to_new[old_id] = match["id"]
            # else: company not in new DB, skip (rare)
        else:
            # Map to existing IV-* or queue for creation
            match = new_iv_by_name.get(name_key)
            if match:
                old_src_to_new[old_id] = match["id"]
            else:
                created_map[old_id] = None  # placeholder, filled after ID assignment

    # ── Map old target IDs → new IDs ─────────────────────────────────────────
    old_tgt_to_new: dict[str, str] = {}
    for old_id, old_e in old_entities.items():
        if old_e["type"] not in ("company", "institution", "government_agency"):
            continue
        wd = old_e.get("wikidata_id")
        name_key = old_e["name"].lower().strip()
        if wd and wd in new_by_wikidata:
            old_tgt_to_new[old_id] = new_by_wikidata[wd]["id"]
        elif name_key in new_by_name_all:
            old_tgt_to_new[old_id] = new_by_name_all[name_key]["id"]

    # ── Assign new IV IDs to entities that need creation ─────────────────────
    entities_working = list(new_entities)  # local copy for ID generation
    new_iv_entities: list[dict] = []

    for old_id in list(created_map.keys()):
        old_e  = old_entities[old_id]
        new_id = next_iv_id(entities_working + new_iv_entities)
        new_e  = make_iv_entity(old_e, new_id)
        created_map[old_id]        = new_id
        old_src_to_new[old_id]     = new_id
        new_iv_by_name[old_e["name"].lower().strip()] = new_e
        new_iv_entities.append(new_e)
        print(f"  + CREATE  {new_id}  [{new_e['type']}]  {new_e['name']}")

    # ── Build new relationships ───────────────────────────────────────────────
    new_relationships: list[dict] = []
    skipped_no_src = 0
    skipped_no_tgt = 0
    skipped_dup    = 0

    for old_rel in old_db["relationships"]:
        src_new = old_src_to_new.get(old_rel["source"])
        tgt_new = old_tgt_to_new.get(old_rel["target"])

        if not src_new:
            skipped_no_src += 1
            continue
        if not tgt_new:
            skipped_no_tgt += 1
            continue

        pair = (src_new, tgt_new)
        if pair in existing_rel_pairs:
            skipped_dup += 1
            continue

        rel = make_relationship(src_new, tgt_new, old_rel)
        new_relationships.append(rel)
        existing_rel_pairs.add(pair)

    print(f"\nSummary:")
    print(f"  New IV entities to create : {len(new_iv_entities)}")
    print(f"  New relationships         : {len(new_relationships)}")
    print(f"  Skipped (no src mapping)  : {skipped_no_src}")
    print(f"  Skipped (no tgt mapping)  : {skipped_no_tgt}")
    print(f"  Skipped (duplicate)       : {skipped_dup}")

    if DRY_RUN:
        print("\n[DRY RUN] No changes written.")
        return

    new_db["entities"]      = new_entities + new_iv_entities
    new_db["relationships"] = new_rels + new_relationships
    new_db["_updated"]      = TODAY

    with open(NEW_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)

    print(f"\nDB updated: +{len(new_iv_entities)} IV entities, +{len(new_relationships)} relationships")


if __name__ == "__main__":
    main()
