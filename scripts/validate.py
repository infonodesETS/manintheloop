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
 10. Relationship type values only: investment, board_membership, edf_participation,
     ownership, role, parte_di
 11. Fields of the new relationship types (ownership, role, parte_di) — schema B1,
     decisions S1-S7 in reference/S*.md. Not applied to older relationship types.
 12. A wikidata_id removed from an entity (history `null_wikidata_id`, history field wikidata_id
     old=QID new=null, validation `qid_removed` / `qid_nulled_duplicate`) must not come back on an
     active entity (retired entities are skipped). Known cases from before B3 are listed in
     work/qid-rimessi-noti.json: only NEW cases fail. To restore a QID on purpose add a validation
     entry status `qid_restored` with `wikidata_id` after the removal.

Usage: python3 scripts/validate.py [path/to/database.json]
"""

import json
import re
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "docs", "data", "database.json")

VALID_ENTITY_TYPES = {"company", "fund", "investor", "public_fund", "government_agency", "bank", "institution", "person", "edf_project"}
VALID_ROLES = {"manufacturer", "investor", "board_member"}
VALID_REL_TYPES = {"investment", "board_membership", "edf_participation", "ownership", "role", "parte_di"}
# Types introduced by B1 (S2, S6): they carry their own `id` and are checked in [11].
NEW_REL_TYPES = {"ownership", "role", "parte_di"}
HOLDER_TYPES = {"fund", "company", "person"}          # S2 (holder_type); to be confirmed with the first import
AS_OF_ORIGINS = {"proxy", "testo", "deposito"}         # S5
HISTORY_KEYS = {"date", "release", "source_ref", "field", "old", "new"}  # S5, new types only
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKIDATA_RE = re.compile(r"^Q\d+$")
PER_ID_RE = re.compile(r"^PER-\d{4,}$")   # S1: four digits or more
IN_ID_RE = re.compile(r"^IN-\d{4,}$")
IV_ID_RE = re.compile(r"^IV-\d{4,}$")
REL_ID_RE = re.compile(r"^REL-\d{4,}$")   # only the new relationship types have an id

QID_BASELINE_PATH = os.path.join(BASE, "work", "qid-rimessi-noti.json")


def qid_rimessi(entities):
    """Coppie 'ID:QID' di entita attive il cui QID e stato tolto e poi rimesso (senza qid_restored).
    La stessa logica e in scripts/search_missing_qids.py (qid_is_blocked): gli script girano con -I e
    non importano i fratelli, quindi la copia e voluta; tenerle allineate."""
    out = []
    for e in entities:
        if any(h.get("action") == "entity_retired" for h in e.get("history", [])):
            continue
        cur = e.get("wikidata_id")
        if not cur:
            continue
        removed, sets, restored = "", "", []
        for h in e.get("history", []):
            dt = h.get("date") or ""
            if h.get("action") == "null_wikidata_id" and h.get("old") == cur and not h.get("from_entity"):
                removed = max(removed, dt)
            elif h.get("field") == "wikidata_id" and h.get("old") == cur and h.get("new") is None:
                removed = max(removed, dt)
            elif h.get("field") == "wikidata_id" and h.get("old") is None and h.get("new") == cur:
                sets = max(sets, dt)
        for v in e.get("validation", []):
            dt = v.get("datestamp") or ""
            if v.get("status") in ("qid_removed", "qid_nulled_duplicate") and v.get("wikidata_id_removed") == cur and not v.get("from_entity"):
                removed = max(removed, dt)
            if v.get("status") == "qid_restored" and v.get("wikidata_id") == cur:
                restored.append(dt)
        if removed and sets and sets >= removed and not any(d >= removed for d in restored):
            out.append(f"{e['id']}:{cur}")
    return out


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

    # ── Check 2: No duplicate relationships ───────────────────────────────────
    # Key: (source, target, type); ownership adds `classe` (S3 R2), role adds `role_code` (S7).
    print("\n[2] Checking relationship uniqueness...")
    seen_r: set[tuple] = set()
    dup_rels = []
    for r in relationships:
        key = (r.get("source"), r.get("target"), r.get("type"))
        if r.get("type") == "ownership":
            key += (r.get("classe"),)
        elif r.get("type") == "role":
            key += (r.get("role_code"),)
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
        rctx = f"{r.get('type','?')} {r.get('source','?')}->{r.get('target','?')}"
        for field in ("added_at", "created_at", "filing_date", "as_of", "release"):
            check_date(f"{rctx} {field}", r.get(field))
        for h in r.get("history") or []:
            if isinstance(h, dict):
                check_date(f"{rctx} history.date", h.get("date"))

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

    # ── Check 11: new relationship types (ownership, role, parte_di) ─────────
    print("\n[11] Checking ownership / role / parte_di relationships...")
    new_errors: list[str] = []

    def bad(r, msg):
        m = f"{r.get('id','?')} ({r.get('type')} {r.get('source')}->{r.get('target')}): {msg}"
        new_errors.append(m)
        errors.append(m)

    def is_num(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def prefix(eid):
        return str(eid).split("-")[0] if eid else ""

    seen_rel_ids: set[str] = set()
    n_new = 0
    for r in relationships:
        t = r.get("type")
        if t not in NEW_REL_TYPES:
            continue
        n_new += 1
        rid = r.get("id")
        if not isinstance(rid, str) or not REL_ID_RE.match(rid):
            bad(r, f"missing or invalid id '{rid}' (expected REL-NNNN)")
        elif rid in seen_rel_ids:
            bad(r, f"duplicate relationship id '{rid}'")
        else:
            seen_rel_ids.add(rid)
        if not isinstance(r.get("source_ref"), str) or not r.get("source_ref"):
            bad(r, "source_ref is required (non-empty string)")
        if not DATE_RE.match(str(r.get("created_at"))):
            bad(r, "created_at is required (YYYY-MM-DD)")
        if "current" in r and not isinstance(r["current"], bool):
            bad(r, "current must be true or false")
        hist = r.get("history")
        if hist is not None:
            if not isinstance(hist, list):
                bad(r, "history must be a list")
            else:
                for i, h in enumerate(hist):
                    if not isinstance(h, dict):
                        bad(r, f"history[{i}] is not an object")
                        continue
                    miss = HISTORY_KEYS - set(h.keys())
                    if miss:
                        bad(r, f"history[{i}] missing keys: {sorted(miss)}")

        sp, tp = prefix(r.get("source")), prefix(r.get("target"))
        if t == "ownership":
            if sp not in ("IV", "IN", "PER") or tp != "IN":
                bad(r, "ownership goes from IV-/IN-/PER- (holder) to IN- (company)")
            if not isinstance(r.get("classe"), str) or not r.get("classe"):
                bad(r, "classe is required (non-empty string, as in the filing)")
            if r.get("holder_type") not in HOLDER_TYPES:
                bad(r, f"holder_type must be one of {sorted(HOLDER_TYPES)}")
            for f in ("pct", "pct_voti"):
                v = r.get(f)
                if v is not None and (not is_num(v) or v < 0 or v > 100):
                    bad(r, f"{f} must be a number between 0 and 100, or null")
            v = r.get("shares")
            if v is not None and (not is_num(v) or v < 0):
                bad(r, "shares must be a non-negative number or null")
            if r.get("pct") is None and r.get("pct_voti") is None and r.get("shares") is None:
                bad(r, "at least one of pct, pct_voti, shares is required")
            if r.get("as_of") is not None and r.get("as_of_origine") not in AS_OF_ORIGINS:
                bad(r, f"as_of_origine must be one of {sorted(AS_OF_ORIGINS)} when as_of is set")
            if r.get("as_of") is None and r.get("as_of_origine") is not None:
                bad(r, "as_of_origine set but as_of is null")
        elif t == "role":
            if sp != "PER" or tp != "IN":
                bad(r, "role goes from PER- (person) to IN- (company)")
            for f in ("role_code", "role_text"):
                if not isinstance(r.get(f), str) or not r.get(f):
                    bad(r, f"{f} is required (non-empty string)")
        elif t == "parte_di":
            if sp not in ("IV", "IN") or tp not in ("IV", "IN"):
                bad(r, "parte_di links two IV-/IN- entities")
            if r.get("source") == r.get("target"):
                bad(r, "parte_di cannot link an entity to itself")
    if new_errors:
        for m in new_errors[:30]:
            err(m)
        if len(new_errors) > 30:
            print(f"  ... and {len(new_errors) - 30} more")
    else:
        ok(f"{n_new} ownership/role/parte_di relationships checked, all valid")

    # sources.sec (S4): reference to the source only, never addresses
    FORBIDDEN_SEC_KEYS = {"indirizzo", "address", "indirizzi", "addresses"}

    def walk_keys(x):
        if isinstance(x, dict):
            for k, v in x.items():
                yield k
                yield from walk_keys(v)
        elif isinstance(x, list):
            for v in x:
                yield from walk_keys(v)

    sec_errors = []
    for e in entities:
        sec = (e.get("sources") or {}).get("sec")
        if sec is None:
            continue
        if not isinstance(sec, dict):
            sec_errors.append(f"{e.get('id','?')}: sources.sec must be an object")
            continue
        bad_keys = {str(k).lower() for k in walk_keys(sec)} & FORBIDDEN_SEC_KEYS
        if bad_keys:
            sec_errors.append(f"{e.get('id','?')}: sources.sec contains address fields {sorted(bad_keys)} (S4: addresses stay out of the DB)")
    for m in sec_errors:
        err(m)
        errors.append(m)
    if not sec_errors:
        ok("sources.sec blocks contain no address fields")

    # ── 12. QID removed and put back ─────────────────────────────────────────
    print("\n[12] Checking that removed wikidata_id values did not come back...")
    known = set()
    if os.path.exists(QID_BASELINE_PATH):
        with open(QID_BASELINE_PATH, encoding="utf-8") as f:
            known = set(json.load(f).get("coppie", []))
    now = set(qid_rimessi(entities))
    new_cases = sorted(now - known)
    for c in new_cases:
        m = f"{c}: wikidata_id was removed and then set again (add a 'qid_restored' validation entry only if intended)"
        err(m)
        errors.append(m)
    solved = len(known - now)
    if not new_cases:
        ok(f"no new cases ({len(now & known)} known cases from before B3 still to review in work/qid-rimessi-noti.json, {solved} solved)")

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
