#!/usr/bin/env python3
"""
validate.py — Validates database.json against schema v3.0 rules.

Checks:
  1. No duplicate id in entities[]
  2. No duplicate id in relationships[]
  3. All relationship source/target IDs exist in entities[]
  4. roles values only: manufacturer, investor, board_member
  5. type values only: company, fund, government_agency, bank, institution, person, edf_project
  6. wikidata_id format: Q[digits] or null
  7. Date fields: YYYY-MM-DD format
  8. Required fields present: id, name, type, roles, history
  9. PER-NNNN IDs only on person entities
 10. Relationship type values only: investment, board_membership, edf_participation
"""

import json
import re
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")

VALID_ENTITY_TYPES = {"company", "fund", "investor", "public_fund", "government_agency", "bank", "institution", "person", "edf_project"}
VALID_ROLES = {"manufacturer", "investor", "board_member"}
VALID_REL_TYPES = {"investment", "board_membership", "edf_participation"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKIDATA_RE = re.compile(r"^Q\d+$")
PER_ID_RE = re.compile(r"^PER-\d{4}$")
IN_ID_RE = re.compile(r"^IN-\d{4}$")
IV_ID_RE = re.compile(r"^IV-\d{4}$")
REL_ID_RE = re.compile(r"^REL-\d{4}$")


def err(msg: str):
    print(f"  ✗ {msg}")


def ok(msg: str):
    print(f"  ✓ {msg}")


def main():
    if not os.path.exists(DATABASE_PATH):
        print(f"ERROR: {DATABASE_PATH} not found. Run build_database.py first.")
        sys.exit(1)

    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    entities = db.get("entities", [])
    relationships = db.get("relationships", [])
    errors: list[str] = []

    # ── Check 1: No duplicate entity IDs ──────────────────────────────────────
    print("\n[1] Checking entity ID uniqueness...")
    entity_ids = [e["id"] for e in entities]
    seen: set[str] = set()
    dups = []
    for eid in entity_ids:
        if eid in seen:
            dups.append(eid)
        seen.add(eid)
    if dups:
        for d in dups:
            err(f"Duplicate entity id: {d}")
            errors.append(f"Duplicate entity id: {d}")
    else:
        ok(f"All {len(entities)} entity IDs are unique")

    entity_id_set = set(entity_ids)

    # ── Check 2: No duplicate relationships (source, target, type) ───────────
    print("\n[2] Checking relationship uniqueness...")
    seen_r: set[tuple] = set()
    dup_rels = []
    for r in relationships:
        key = (r.get("source"), r.get("target"), r.get("type"))
        if key in seen_r:
            dup_rels.append(key)
        seen_r.add(key)
    if dup_rels:
        for d in dup_rels:
            err(f"Duplicate relationship: {d}")
            errors.append(f"Duplicate relationship: {d}")
    else:
        ok(f"All {len(relationships)} relationships are unique")

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
        ok("All relationship source/target references are valid")

    # ── Check 4: Roles values ──────────────────────────────────────────────────
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

    # ── Check 5: Entity type values ────────────────────────────────────────────
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

    # ── Check 6: wikidata_id format ────────────────────────────────────────────
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

    # ── Check 7: Date fields format ────────────────────────────────────────────
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

        for h in e.get("history", []):
            check_date(f"{ctx} history.date", h.get("date"))

        cb = (e.get("sources") or {}).get("crunchbase") or {}
        if isinstance(cb, dict):
            check_date(f"{ctx} crunchbase.extracted_at", cb.get("extracted_at"))

        inf = (e.get("sources") or {}).get("infonodes") or {}
        if isinstance(inf, dict):
            check_date(f"{ctx} infonodes.extracted_at", inf.get("extracted_at"))

        ishares_list = (e.get("sources") or {}).get("ishares") or []
        if isinstance(ishares_list, list):
            for j, ish in enumerate(ishares_list):
                if isinstance(ish, dict):
                    check_date(f"{ctx} ishares[{j}].extracted_at", ish.get("extracted_at"))

        edf = (e.get("sources") or {}).get("edf") or {}
        if isinstance(edf, dict):
            check_date(f"{ctx} edf.extracted_at", edf.get("extracted_at"))

        for v in e.get("validation", []):
            ds = v.get("datestamp")
            if ds is not None:
                check_date(f"{ctx} validation.datestamp", ds)

    for r in relationships:
        check_date(f"{r.get('id','?')} added_at", r.get("added_at"))

    if date_errors:
        for m in date_errors[:20]:
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

    # ── Check 9: PER-NNNN IDs only on person entities ─────────────────────────
    print("\n[9] Checking PER-NNNN ID consistency...")
    per_errors = []
    for e in entities:
        eid = e.get("id", "")
        etype = e.get("type", "")
        is_per = PER_ID_RE.match(eid) is not None
        if is_per and etype != "person":
            msg = f"{eid} ({e.get('name','?')}): PER-NNNN ID but type is '{etype}'"
            per_errors.append(msg)
            errors.append(msg)
        if not is_per and etype == "person":
            msg = f"{eid} ({e.get('name','?')}): type 'person' but ID is not PER-NNNN"
            per_errors.append(msg)
            errors.append(msg)
    if per_errors:
        for m in per_errors:
            err(m)
    else:
        ok("All PER-NNNN IDs are consistent with person type")

    # ── Check 10: Relationship type values ────────────────────────────────────
    print("\n[10] Checking relationship type values...")
    invalid_rel_types = []
    for r in relationships:
        rt = r.get("type")
        if rt not in VALID_REL_TYPES:
            msg = f"{r.get('id','?')}: invalid relationship type '{rt}'"
            invalid_rel_types.append(msg)
            errors.append(msg)
    if invalid_rel_types:
        for m in invalid_rel_types:
            err(m)
    else:
        ok("All relationship type values are valid")

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s) found.")
        sys.exit(1)
    else:
        companies = sum(1 for e in entities if e.get("type") == "company")
        persons = sum(1 for e in entities if e.get("type") == "person")
        other = len(entities) - companies - persons
        print("VALIDATION PASSED ✓")
        print(f"  Total entities:  {len(entities)}  ({companies} companies, {persons} persons, {other} other)")
        print(f"  Relationships:   {len(relationships)}")
        print(f"  Schema:          {db.get('_schema', '?')}")
        print(f"  Last updated:    {db.get('_updated', '?')}")


if __name__ == "__main__":
    main()
