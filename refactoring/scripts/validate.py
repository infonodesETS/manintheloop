#!/usr/bin/env python3
"""
validate.py — Validates database.json against schema v2.0 rules.

Checks:
  1. No duplicate id in entities[]
  2. No duplicate id in relationships[]
  3. All relationship source/target IDs exist in entities[]
  4. roles values only "manufacturer" or "investor"
  5. type values only allowed set
  6. wikidata_id format: Q[digits] or null
  7. Date fields: YYYY-MM-DD format
  8. Required fields present: id, name, type, roles, history
"""

import json
import re
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")

VALID_ENTITY_TYPES = {"company", "fund", "government_agency", "bank", "institution"}
VALID_ROLES = {"manufacturer", "investor"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKIDATA_RE = re.compile(r"^Q\d+$")


def err(msg: str):
    print(f"  ✗ {msg}")


def ok(msg: str):
    print(f"  ✓ {msg}")


def main():
    if not os.path.exists(DATABASE_PATH):
        print(f"ERROR: {DATABASE_PATH} not found. Run migrate.py first.")
        sys.exit(1)

    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    entities = db.get("entities", [])
    relationships = db.get("relationships", [])

    errors: list[str] = []

    # ── Check 1: No duplicate entity IDs ─────────────────────────────────────
    print("\n[1] Checking entity ID uniqueness...")
    entity_ids = [e["id"] for e in entities]
    seen_entity_ids: set[str] = set()
    dups = []
    for eid in entity_ids:
        if eid in seen_entity_ids:
            dups.append(eid)
        seen_entity_ids.add(eid)
    if dups:
        for d in dups:
            err(f"Duplicate entity id: {d}")
            errors.append(f"Duplicate entity id: {d}")
    else:
        ok(f"All {len(entities)} entity IDs are unique")

    entity_id_set = set(entity_ids)

    # ── Check 2: No duplicate relationship IDs ────────────────────────────────
    print("\n[2] Checking relationship ID uniqueness...")
    rel_ids = [r["id"] for r in relationships]
    seen_rel_ids: set[str] = set()
    dup_rels = []
    for rid in rel_ids:
        if rid in seen_rel_ids:
            dup_rels.append(rid)
        seen_rel_ids.add(rid)
    if dup_rels:
        for d in dup_rels:
            err(f"Duplicate relationship id: {d}")
            errors.append(f"Duplicate relationship id: {d}")
    else:
        ok(f"All {len(relationships)} relationship IDs are unique")

    # ── Check 3: Relationship source/target exist in entities ─────────────────
    print("\n[3] Checking relationship source/target references...")
    dangling = []
    for r in relationships:
        rid = r.get("id", "?")
        src = r.get("source")
        tgt = r.get("target")
        if src not in entity_id_set:
            msg = f"{rid}: source '{src}' not in entities"
            dangling.append(msg)
            errors.append(msg)
        if tgt not in entity_id_set:
            msg = f"{rid}: target '{tgt}' not in entities"
            dangling.append(msg)
            errors.append(msg)
    if dangling:
        for d in dangling:
            err(d)
    else:
        ok(f"All relationship source/target references are valid")

    # ── Check 4: Roles values ─────────────────────────────────────────────────
    print("\n[4] Checking roles values...")
    invalid_roles = []
    for e in entities:
        for role in e.get("roles", []):
            if role not in VALID_ROLES:
                msg = f"{e.get('id','?')} ({e.get('name','?')}): invalid role '{role}'"
                invalid_roles.append(msg)
                errors.append(msg)
    if invalid_roles:
        for m in invalid_roles:
            err(m)
    else:
        ok("All roles values are valid")

    # ── Check 5: Type values ──────────────────────────────────────────────────
    print("\n[5] Checking entity type values...")
    invalid_types = []
    for e in entities:
        t = e.get("type")
        if t not in VALID_ENTITY_TYPES:
            msg = f"{e.get('id','?')} ({e.get('name','?')}): invalid type '{t}'"
            invalid_types.append(msg)
            errors.append(msg)
    if invalid_types:
        for m in invalid_types:
            err(m)
    else:
        ok("All entity types are valid")

    # ── Check 6: wikidata_id format ───────────────────────────────────────────
    print("\n[6] Checking wikidata_id format...")
    invalid_wikidata = []
    for e in entities:
        wid = e.get("wikidata_id")
        if wid is not None:
            if not WIKIDATA_RE.match(str(wid)):
                msg = f"{e.get('id','?')} ({e.get('name','?')}): invalid wikidata_id '{wid}'"
                invalid_wikidata.append(msg)
                errors.append(msg)
    if invalid_wikidata:
        for m in invalid_wikidata:
            err(m)
    else:
        ok("All wikidata_id values are valid (Q\\d+ or null)")

    # ── Check 7: Date fields format ───────────────────────────────────────────
    print("\n[7] Checking date fields (YYYY-MM-DD)...")
    date_errors = []

    def check_date(context: str, val):
        if val is not None and not DATE_RE.match(str(val)):
            msg = f"{context}: invalid date '{val}'"
            date_errors.append(msg)
            errors.append(msg)

    for e in entities:
        eid = e.get("id", "?")
        ename = e.get("name", "?")
        ctx = f"{eid} ({ename})"

        # history dates
        for h in e.get("history", []):
            check_date(f"{ctx} history.date", h.get("date"))

        # sources.crunchbase.extracted_at
        cb = (e.get("sources") or {}).get("crunchbase") or {}
        if isinstance(cb, dict):
            check_date(f"{ctx} crunchbase.extracted_at", cb.get("extracted_at"))

        # sources.infonodes.extracted_at
        inf = (e.get("sources") or {}).get("infonodes") or {}
        if isinstance(inf, dict):
            check_date(f"{ctx} infonodes.extracted_at", inf.get("extracted_at"))

        # validation datestamps
        for v in e.get("validation", []):
            ds = v.get("datestamp")
            if ds is not None:
                check_date(f"{ctx} validation.datestamp", ds)

    for r in relationships:
        check_date(f"{r.get('id','?')} added_at", r.get("added_at"))

    if date_errors:
        for m in date_errors[:20]:  # cap output
            err(m)
        if len(date_errors) > 20:
            print(f"  ... and {len(date_errors) - 20} more date errors")
    else:
        ok("All date fields are in YYYY-MM-DD format")

    # ── Check 8: Required fields ───────────────────────────────────────────────
    print("\n[8] Checking required fields (id, name, type, roles, history)...")
    REQUIRED = ["id", "name", "type", "roles", "history"]
    missing_fields = []
    for e in entities:
        for field in REQUIRED:
            if field not in e or e[field] is None:
                msg = f"{e.get('id','?')} ({e.get('name','?')}): missing required field '{field}'"
                missing_fields.append(msg)
                errors.append(msg)
    if missing_fields:
        for m in missing_fields:
            err(m)
    else:
        ok("All entities have required fields")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s) found.")
        sys.exit(1)
    else:
        total = len(entities)
        companies = sum(1 for e in entities if e.get("type") == "company")
        investors = total - companies
        print(f"VALIDATION PASSED ✓")
        print(f"  Total entities:  {total}  ({companies} companies, {investors} investors)")
        print(f"  Relationships:   {len(relationships)}")


if __name__ == "__main__":
    main()
