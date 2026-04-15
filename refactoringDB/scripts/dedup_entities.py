#!/usr/bin/env python3
"""
dedup_entities.py — Merge true duplicate entities that share a wikidata_id.

Usage:
    # Dry-run a specific merge (winner keeps data, loser is retired)
    python3 scripts/dedup_entities.py --merge WINNER_ID LOSER_ID --dry-run

    # Apply a specific merge
    python3 scripts/dedup_entities.py --merge WINNER_ID LOSER_ID

    # List all wikidata_id duplicates and suggest auto-merge candidates
    python3 scripts/dedup_entities.py --list

Merge operation (tracked in history + validation):
    - sources.ishares      : loser's entries appended to winner (preserves each ETF listing)
    - sources.edf          : copied to winner if winner lacks it
    - sources.crunchbase   : copied to winner if winner lacks it
    - sources.infonodes    : field-level merge — winner fields take precedence, missing filled
    - sources.wikidata     : winner's kept (same QID → same data)
    - roles                : union of both
    - history[]            : loser's entries prepended with [from LOSER_ID] and appended
    - validation[]         : loser's entries appended (deduped by status)
    - relationships        : source/target LOSER_ID → WINNER_ID (deduped)
    - validation entry     : "merged_from: LOSER_ID" added to winner
    - history entry        : full merge record added to winner
    - loser entity         : removed from entities list
"""

import json
import sys
import re
from datetime import date
from collections import defaultdict

DB_PATH = "data/database.json"
TODAY = date.today().isoformat()

DRY_RUN = "--dry-run" in sys.argv
args = sys.argv[1:]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load():
    with open(DB_PATH) as f:
        return json.load(f)

def save(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def find(entities, eid):
    return next((e for e in entities if e["id"] == eid), None)

def data_score(e):
    """Score entity by data richness. Higher = keep as winner."""
    src = e.get("sources") or {}
    score = 0
    for k, v in src.items():
        if v:
            score += 10
    if src.get("crunchbase"):
        score += 5
    if src.get("wikidata"):
        score += 5
    score += len(e.get("history", []))
    score += len(e.get("validation", []))
    rel_count = e.get("_rel_count", 0)
    score += rel_count * 3
    return score

SHARE_CLASS_PATTERN = re.compile(
    r"\b(class [a-z]|series [a-z]|non.?voting|gdr|adr|pref|preferred|savings|risparmio"
    r"|ord|ordinary|bearer|registered|voting|rsp|nv)\b",
    re.IGNORECASE,
)

def is_share_class_variant(name_a, name_b):
    """Return True if names differ only by share class suffix — keep both."""
    def strip(n):
        return SHARE_CLASS_PATTERN.sub("", n).strip().lower()
    return strip(name_a) == strip(name_b) and strip(name_a) != name_a.lower()

def legal_suffix_strip(name):
    suffixes = r"\b(s\.?p\.?a\.?|s\.?a\.?|ag|plc|ltd|llc|gmbh|bv|nv|inc\.?|corp\.?|co\.?)\b\.?$"
    return re.sub(suffixes, "", name, flags=re.IGNORECASE).strip().rstrip(",").strip()

# ---------------------------------------------------------------------------
# --list mode
# ---------------------------------------------------------------------------

def cmd_list():
    db = load()
    entities = db["entities"]

    # Count relationships per entity
    rel_count = defaultdict(int)
    for r in db.get("relationships", []):
        rel_count[r["source"]] += 1
        rel_count[r["target"]] += 1

    qid_groups = defaultdict(list)
    for e in entities:
        qid = e.get("wikidata_id")
        if qid:
            qid_groups[qid].append(e)

    dupes = {q: g for q, g in qid_groups.items() if len(g) > 1}
    print(f"{'='*70}")
    print(f"QIDs shared by 2+ entities: {len(dupes)}  ({sum(len(g) for g in dupes.values())} entities)")
    print(f"{'='*70}\n")

    auto_candidates = []

    for qid, group in sorted(dupes.items(), key=lambda x: len(x[1]), reverse=True):
        for e in group:
            e["_rel_count"] = rel_count[e["id"]]
        group_sorted = sorted(group, key=data_score, reverse=True)
        names = [e["name"] for e in group]

        # Classify
        if len(group) == 2:
            a, b = group_sorted
            src_a = set((e.get("sources") or {}).keys())
            src_b = set((e.get("sources") or {}).keys())
            if is_share_class_variant(a["name"], b["name"]):
                tag = "SHARE_CLASS — keep both"
            elif legal_suffix_strip(a["name"]).lower() == legal_suffix_strip(b["name"]).lower():
                tag = "AUTO_MERGE candidate"
                auto_candidates.append((a["id"], b["id"], qid))
            else:
                tag = "REVIEW — parent/subsidiary or wrong QID?"
        else:
            tag = f"GROUP ({len(group)} entities) — manual review"

        print(f"  {qid}  [{tag}]")
        for e in group_sorted:
            srcs = list((e.get("sources") or {}).keys())
            rels = rel_count[e["id"]]
            print(f"    {e['id']:10} score={data_score(e):3}  rels={rels}  srcs={srcs}  {e['name']}")
        print()

    if auto_candidates:
        print(f"{'='*70}")
        print(f"AUTO_MERGE candidates ({len(auto_candidates)}):")
        print(f"  Run:  python3 scripts/dedup_entities.py --merge WINNER LOSER")
        print()
        for winner_id, loser_id, qid in auto_candidates:
            print(f"  python3 scripts/dedup_entities.py --merge {winner_id} {loser_id}")
        print()

# ---------------------------------------------------------------------------
# --merge mode
# ---------------------------------------------------------------------------

def merge_infonodes(winner_inf, loser_inf):
    """Field-level merge: winner fields take precedence, fill missing from loser."""
    merged = dict(loser_inf)
    merged.update({k: v for k, v in winner_inf.items() if v is not None})
    return merged

def cmd_merge(winner_id, loser_id):
    db = load()
    entities = db["entities"]
    relationships = db.get("relationships", [])

    winner = find(entities, winner_id)
    loser = find(entities, loser_id)

    if not winner:
        print(f"ERROR: winner {winner_id} not found"); sys.exit(1)
    if not loser:
        print(f"ERROR: loser {loser_id} not found"); sys.exit(1)
    winner_qid = winner.get("wikidata_id")
    loser_qid = loser.get("wikidata_id")
    if winner_qid != loser_qid:
        if loser_qid is None:
            # Loser has no QID — winner's QID takes over; safe for name-based merges
            print(f"NOTE: loser {loser_id} has no wikidata_id — winner's QID ({winner_qid}) will be kept.")
        elif winner_qid is None:
            # Winner has no QID but loser does — adopt loser's QID onto winner
            print(f"NOTE: winner {winner_id} has no wikidata_id — adopting loser's QID ({loser_qid}).")
            if not DRY_RUN:
                winner["wikidata_id"] = loser_qid
        else:
            # Both have different non-null QIDs — genuinely different Wikidata entities, abort
            print(f"ERROR: wikidata_ids differ — {winner_qid} vs {loser_qid}")
            if not DRY_RUN:
                print("Aborting — confirm QIDs match before merging."); sys.exit(1)

    w_src = winner.setdefault("sources", {})
    l_src = loser.get("sources") or {}
    absorbed = []

    # --- sources.ishares: append loser entries (different ticker = different ETF listing) ---
    w_ishares = w_src.get("ishares") or []
    l_ishares = l_src.get("ishares") or []
    w_tickers = {e.get("stock_ticker") for e in w_ishares}
    new_ishares = [e for e in l_ishares if e.get("stock_ticker") not in w_tickers]
    if new_ishares:
        w_src["ishares"] = w_ishares + new_ishares
        absorbed.append(f"ishares[{len(new_ishares)} new entries: {[e.get('stock_ticker') for e in new_ishares]}]")

    # --- sources.edf: copy if winner lacks it ---
    if l_src.get("edf") and not w_src.get("edf"):
        w_src["edf"] = l_src["edf"]
        absorbed.append("sources.edf")

    # --- sources.crunchbase: copy if winner lacks it ---
    if l_src.get("crunchbase") and not w_src.get("crunchbase"):
        w_src["crunchbase"] = l_src["crunchbase"]
        absorbed.append("sources.crunchbase")

    # --- sources.infonodes: field-level merge ---
    if l_src.get("infonodes"):
        w_inf = w_src.get("infonodes") or {}
        merged_inf = merge_infonodes(w_inf, l_src["infonodes"])
        if merged_inf != w_inf:
            w_src["infonodes"] = merged_inf
            absorbed.append("sources.infonodes (field-level merge)")

    # --- roles: union ---
    w_roles = set(winner.get("roles") or [])
    l_roles = set(loser.get("roles") or [])
    merged_roles = sorted(w_roles | l_roles)
    if merged_roles != sorted(w_roles):
        winner["roles"] = merged_roles
        absorbed.append(f"roles (added: {sorted(l_roles - w_roles)})")

    # --- history: append loser's entries tagged with origin ---
    l_history = loser.get("history") or []
    tagged_history = []
    for h in l_history:
        entry = dict(h)
        entry["description"] = f"[from {loser_id}] " + (entry.get("description") or "")
        tagged_history.append(entry)
    if tagged_history:
        winner.setdefault("history", []).extend(tagged_history)
        absorbed.append(f"history[{len(tagged_history)} entries from {loser_id}]")

    # --- validation: append loser's entries not already in winner (dedup by status) ---
    w_statuses = {v.get("status") for v in winner.get("validation") or []}
    l_validation = loser.get("validation") or []
    new_val = []
    for v in l_validation:
        if v.get("status") not in w_statuses:
            entry = dict(v)
            entry["description"] = f"[from {loser_id}] " + (entry.get("description") or "")
            new_val.append(entry)
            w_statuses.add(v.get("status"))
    if new_val:
        winner.setdefault("validation", []).extend(new_val)
        absorbed.append(f"validation[{len(new_val)} entries from {loser_id}]")

    # --- relationships: redirect loser_id → winner_id, deduplicate ---
    rels_redirected = 0
    seen_pairs = set()
    # First pass: collect existing winner relationships
    for r in relationships:
        if r.get("source") == winner_id or r.get("target") == winner_id:
            key = (r.get("source"), r.get("target"), r.get("type"))
            seen_pairs.add(key)

    rels_to_remove = []
    for r in relationships:
        changed = False
        src = r.get("source")
        tgt = r.get("target")
        if src == loser_id:
            r["source"] = winner_id
            src = winner_id
            changed = True
        if tgt == loser_id:
            r["target"] = winner_id
            tgt = winner_id
            changed = True
        if changed:
            key = (src, tgt, r.get("type"))
            if key in seen_pairs:
                # Duplicate after redirect — mark for removal
                rels_to_remove.append(r["id"])
            else:
                seen_pairs.add(key)
                rels_redirected += 1
                r["history"] = r.get("history") or []
                r["history"].append({
                    "date": TODAY,
                    "author": "dedup_entities.py",
                    "description": f"Entity reference redirected: {loser_id} → {winner_id} (merge)"
                })

    if rels_to_remove:
        db["relationships"] = [r for r in relationships if r["id"] not in set(rels_to_remove)]
        absorbed.append(f"relationships[{rels_redirected} redirected, {len(rels_to_remove)} deduped]")
    elif rels_redirected:
        absorbed.append(f"relationships[{rels_redirected} redirected]")

    # --- Add merge record to winner history ---
    absorbed_str = "; ".join(absorbed) if absorbed else "no new data"
    merge_basis = (
        f"same wikidata_id {winner.get('wikidata_id')}"
        if winner.get("wikidata_id") and loser_qid == winner.get("wikidata_id")
        else f"name-based match (loser {loser_id} had no wikidata_id)"
        if loser_qid is None
        else f"same wikidata_id {winner.get('wikidata_id')}"
    )
    winner.setdefault("history", []).append({
        "date": TODAY,
        "source": "manual",
        "author": "dedup_entities.py",
        "field": "entity",
        "old": None,
        "new": f"merged from {loser_id}",
        "description": (
            f"Merged and retired {loser_id} ({loser['name']}) into this entity "
            f"({merge_basis}). "
            f"Absorbed: {absorbed_str}."
        ),
    })

    # --- Add merged_from validation entry to winner ---
    winner.setdefault("validation", []).append({
        "status": "merged_from",
        "description": (
            f"Retired entity {loser_id} ({loser['name']}) merged into this entity on {TODAY}. "
            f"Retired entity had sources: {list(l_src.keys())}."
        ),
        "author": "dedup_entities.py",
        "datestamp": TODAY,
    })

    # --- Remove loser from entities ---
    db["entities"] = [e for e in entities if e["id"] != loser_id]

    # --- Report ---
    print(f"MERGE: {winner_id} ({winner['name']})  ←  {loser_id} ({loser['name']})")
    print(f"  wikidata_id:  {winner.get('wikidata_id')}")
    if absorbed:
        print(f"  absorbed:     {absorbed_str}")
    else:
        print(f"  absorbed:     nothing new (loser had no unique data)")
    if rels_redirected:
        print(f"  relationships redirected: {rels_redirected}")
    if rels_to_remove:
        print(f"  relationships deduped (removed): {len(rels_to_remove)}")
    print(f"  loser {loser_id} removed from entities")

    if DRY_RUN:
        print("\n  DRY RUN — no changes written.")
        return

    save(db)
    print(f"\n  Written: {DB_PATH}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if "--list" in args:
    cmd_list()
elif "--merge" in args:
    idx = args.index("--merge")
    try:
        winner_id = args[idx + 1]
        loser_id = args[idx + 2]
    except IndexError:
        print("Usage: --merge WINNER_ID LOSER_ID"); sys.exit(1)
    cmd_merge(winner_id, loser_id)
else:
    print(__doc__)
    sys.exit(0)
