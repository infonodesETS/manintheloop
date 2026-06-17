#!/usr/bin/env python3
"""
build_edf_orgs.py — Build data/edf_orgs.json from data/edf_calls.json.

What it does
------------
1. Reads all participants from edf_calls.json, deduplicates by PIC.
2. Aggregates per-org stats (EU contribution, project/call/coordinator counts).
3. Auto-matches against database.json entities via name normalisation.
4. Preserves any existing db_id / match_confidence from a previous run.
5. Saves data/edf_orgs.json.

The crosswalk fields on each org record:
  db_id            — IN-* or IV-* from database.json, or null
  match_method     — "auto_name" | "manual" | null
  match_confidence — "suggested" | "confirmed" | null

To confirm a suggested match: set match_confidence to "confirmed" in
edf_orgs.json manually. It will survive all future regenerations.

Usage
-----
  python3 scripts/build_edf_orgs.py               # full rebuild, preserve confirmed mappings
  python3 scripts/build_edf_orgs.py --reset        # rebuild from scratch (clears all db_id)
  python3 scripts/build_edf_orgs.py --stats        # print summary only, do not write
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDF_PATH     = os.path.join(BASE, "data", "edf_calls.json")
DB_PATH      = os.path.join(BASE, "data", "database.json")
OUTPUT_PATH  = os.path.join(BASE, "data", "edf_orgs.json")

# Legal suffixes to strip during name normalisation (order matters: longer first)
LEGAL_SUFFIXES = [
    "aktiebolag", "aktiengesellschaft", "societa per azioni",
    "sociedad anonima", "naamloze vennootschap",
    "gesellschaft mit beschrankter haftung",
    "limited liability company", "limited liability partnership",
    "public limited company",
    "gmbh & co kg", "gmbh & co. kg",
    "s.p.a.", "s.a.s.", "s.r.l.", "s.a.", "n.v.", "b.v.", "a.s.",
    "spa", "sas", "srl", "gmbh", "nv", "bv", "ag", "as", "ab",
    "oy", "oyj", "plc", "llc", "corp", "ltd", "inc", "sa",
    "group", "holding", "holdings",
]

STOPWORDS = {"the", "of", "and", "for", "de", "du", "la", "le", "les", "di", "dei"}


def norm(s: str) -> str:
    """Normalise a company name for matching."""
    s = s.lower()
    # Collapse dotted abbreviations like S.A., S.p.A., A.S., G.m.b.H. → remove dots
    s = re.sub(r"\b([a-z])\.([a-z])\.([a-z])\.", r"\1\2\3", s)  # X.Y.Z. → xyz
    s = re.sub(r"\b([a-z])\.([a-z])\.", r"\1\2", s)              # X.Y. → xy
    s = re.sub(r"\b([a-z])\.", r"\1", s)                         # X. → x
    # Strip legal suffixes (longest first)
    for suffix in LEGAL_SUFFIXES:
        pattern = r"\b" + re.escape(suffix) + r"\b\.?\s*$"
        s = re.sub(pattern, "", s).strip().rstrip(",").strip()
    # Remove punctuation, collapse whitespace
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Remove residual single-character tokens (artefacts of legal abbreviations)
    s = " ".join(t for t in s.split() if len(t) > 1)
    return s


def token_overlap_ratio(a: str, b: str) -> float:
    """
    Subsidiary-aware overlap: the shorter name's tokens must ALL appear in the longer name.
    Only considers tokens of length >= 3 to avoid matching on abbreviation residues.
    Returns 1.0 if shorter ⊆ longer (and shorter has ≥2 tokens), else 0.0.
    This correctly matches "BAE Systems" ⊆ "BAE Systems Hagglunds" while rejecting
    "MTU Aero Engines" vs "ULPower Aero Engines" (MTU ∉ ULPower tokens).
    """
    ta = {t for t in a.split() if len(t) >= 3} - STOPWORDS
    tb = {t for t in b.split() if len(t) >= 3} - STOPWORDS
    if not ta or not tb:
        return 0.0
    shorter, longer = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if len(shorter) < 2:
        return 0.0
    return 1.0 if shorter.issubset(longer) else 0.0


# ── Phase 1: Load sources ──────────────────────────────────────────────────────

def load_edf() -> dict:
    with open(EDF_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_database() -> dict:
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_existing_orgs() -> dict:
    """Load existing edf_orgs.json; return {pic: {db_id, match_method, match_confidence}}."""
    if not os.path.exists(OUTPUT_PATH):
        return {}
    try:
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        preserved = {}
        for pic, rec in (data.get("orgs") or {}).items():
            if rec.get("db_id") is not None:
                preserved[pic] = {
                    "db_id":            rec["db_id"],
                    "match_method":     rec.get("match_method"),
                    "match_confidence": rec.get("match_confidence"),
                }
        print(f"  Loaded {len(preserved)} existing db_id mappings from {OUTPUT_PATH}")
        return preserved
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [warn] Could not read existing edf_orgs.json: {e}", file=sys.stderr)
        return {}


# ── Phase 2: Build unique org registry ────────────────────────────────────────

def build_org_registry(edf: dict) -> dict:
    """
    Returns {pic: record} with deduplicated org data and aggregated stats.
    """
    orgs: dict[str, dict] = {}
    # Per-PIC aggregation helpers
    eu_contrib:   dict[str, float] = defaultdict(float)
    project_ids:  dict[str, set]   = defaultdict(set)
    call_ids:     dict[str, set]   = defaultdict(set)
    coord_count:  dict[str, int]   = defaultdict(int)

    calls = edf.get("calls") or {}
    for call_id, call in calls.items():
        for proj in (call.get("projects") or []):
            proj_id = proj.get("project_id") or ""
            for p in (proj.get("participants") or []):
                pic = str(p.get("pic") or "").strip()
                if not pic:
                    continue

                # First time we see this PIC: store base fields
                if pic not in orgs:
                    orgs[pic] = {
                        "pic":           pic,
                        "legal_name":    p.get("organization_name") or "",
                        "country":       p.get("country") or "",
                        "country_code":  p.get("country_code") or "",
                        "city":          p.get("city") or "",
                        "activity_type": p.get("activity_type") or "",
                        "org_type":      p.get("type") or "",
                        "sme":           p.get("sme"),
                        "web_link":      p.get("web_link") or "",
                        "eu_url":        p.get("eu_url") or "",
                    }

                # Aggregate stats
                try:
                    eu_contrib[pic] += float(p.get("eu_contribution") or 0)
                except (TypeError, ValueError):
                    pass

                if proj_id:
                    project_ids[pic].add(proj_id)
                call_ids[pic].add(call_id)

                if (p.get("role") or "").lower() == "coordinator":
                    coord_count[pic] += 1

    # Attach stats
    for pic, rec in orgs.items():
        rec["stats"] = {
            "total_eu_contribution": round(eu_contrib[pic], 2),
            "project_count":         len(project_ids[pic]),
            "call_count":            len(call_ids[pic]),
            "coordinator_count":     coord_count[pic],
        }

    print(f"  Built registry: {len(orgs)} unique orgs (by PIC)")
    return orgs


# ── Phase 3: Auto name-matching ────────────────────────────────────────────────

def build_db_norm_map(db: dict) -> dict[str, str]:
    """Returns {norm(entity.name): entity.id} for all database.json entities."""
    result = {}
    for e in db.get("entities") or []:
        name = e.get("name") or ""
        eid  = e.get("id") or ""
        if name and eid:
            result[norm(name)] = eid
    return result


def auto_match(orgs: dict, db: dict) -> dict[str, tuple[str, str]]:
    """
    Returns {pic: (db_id, match_tier)} for PICs that have a confident auto-match.

    Three tiers (applied in order, first match wins):
      Tier 1 — exact_norm     : norm(edf_name) == norm(db_name)
      Tier 2 — subset_tokens  : all ≥2 tokens of the shorter name are in the longer name
                                 (catches subsidiaries like "BAE Systems Hagglunds" → "BAE Systems")
      Tier 3 — prefix_brand   : db name has exactly 1 significant token of length ≥5,
                                 and that token is the first token of the EDF name
                                 (catches "LEONARDO - SOCIETA PER AZIONI" → "Leonardo")
    """
    db_norm_map  = build_db_norm_map(db)
    db_norm_list = list(db_norm_map.items())

    # Pre-build: single-token brand names (for tier 3)
    # {brand_token: db_id} — only tokens of length ≥5 to avoid noise
    brand_map: dict[str, str] = {}
    for db_norm_name, db_id in db_norm_list:
        tokens = [t for t in db_norm_name.split() if len(t) >= 3 and t not in STOPWORDS]
        if len(tokens) == 1 and len(tokens[0]) >= 5:
            brand_map[tokens[0]] = db_id

    matches: dict[str, tuple[str, str]] = {}

    for pic, rec in orgs.items():
        legal = rec.get("legal_name") or ""
        if not legal:
            continue
        n = norm(legal)

        # Tier 1: exact normalised match
        if n in db_norm_map:
            matches[pic] = (db_norm_map[n], "exact_norm")
            continue

        # Tier 2: subset token match (subsidiary detection)
        edf_sig_tokens = [t for t in n.split() if len(t) >= 3 and t not in STOPWORDS]
        edf_token_set  = set(edf_sig_tokens)

        best_id: str | None = None
        for db_norm_name, db_id in db_norm_list:
            if token_overlap_ratio(n, db_norm_name) == 1.0:
                best_id = db_id
                break

        if best_id:
            matches[pic] = (best_id, "subset_tokens")
            continue

        # Tier 3: prefix brand match
        # The first significant token of the EDF name must match a single-brand DB entity
        if edf_sig_tokens:
            first_token = edf_sig_tokens[0]
            if first_token in brand_map:
                matches[pic] = (brand_map[first_token], "prefix_brand")

    return matches


# ── Phase 4: Apply matches and preserved mappings ──────────────────────────────

def apply_matches(
    orgs: dict,
    auto_matches: dict[str, tuple[str, str]],
    preserved: dict[str, dict],
) -> tuple[dict, int, int, int]:
    """
    Merges auto-matches and preserved mappings onto org records.
    Returns (orgs, newly_matched, preserved_count, total_matched).
    """
    newly_matched = 0
    preserved_count = 0

    for pic, rec in orgs.items():
        # Initialise crosswalk fields
        rec["db_id"]            = None
        rec["match_method"]     = None
        rec["match_confidence"] = None

        # Apply auto-match first
        if pic in auto_matches:
            db_id, tier = auto_matches[pic]
            rec["db_id"]            = db_id
            rec["match_method"]     = "auto_name"
            rec["match_confidence"] = "suggested"
            newly_matched += 1

        # Preserved mapping always wins (may override auto-match)
        if pic in preserved:
            prev = preserved[pic]
            rec["db_id"]            = prev["db_id"]
            rec["match_method"]     = prev.get("match_method") or "manual"
            rec["match_confidence"] = prev.get("match_confidence") or "confirmed"
            preserved_count += 1
            if pic not in auto_matches:
                newly_matched -= 0  # was not auto-matched anyway

    total_matched = sum(1 for r in orgs.values() if r.get("db_id"))
    return orgs, newly_matched, preserved_count, total_matched


# ── Phase 5: Save ──────────────────────────────────────────────────────────────

def save(orgs: dict) -> None:
    total   = len(orgs)
    matched = sum(1 for r in orgs.values() if r.get("db_id"))
    output  = {
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_source":       "edf_calls.json",
        "_total_orgs":   total,
        "_matched_orgs": matched,
        "orgs":          orgs,
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved {total} orgs ({matched} with db_id) → {OUTPUT_PATH}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Rebuild from scratch — clears all existing db_id mappings",
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Print match summary only, do not write output file",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("EDF Orgs Builder")
    if args.reset:
        print("Mode : reset (all db_id mappings cleared)")
    elif args.stats:
        print("Mode : stats only (no file written)")
    else:
        print("Mode : full rebuild (preserving confirmed mappings)")
    print("=" * 60)

    # ── Load ─────────────────────────────────────────────────────────────────
    print("\n[1] Loading sources…")
    edf = load_edf()
    db  = load_database()
    preserved = {} if args.reset else load_existing_orgs()

    # ── Build registry ────────────────────────────────────────────────────────
    print("\n[2] Building org registry from edf_calls.json…")
    orgs = build_org_registry(edf)

    # ── Auto-match ────────────────────────────────────────────────────────────
    print("\n[3] Auto-matching against database.json…")
    auto_matches = auto_match(orgs, db)
    print(f"  Auto-matches found: {len(auto_matches)}")
    for pic, (db_id, tier) in sorted(auto_matches.items(), key=lambda x: x[1][0]):
        legal = orgs[pic].get("legal_name", "")
        print(f"  [{tier}]  {db_id}  ←  {legal}")

    # ── Merge preserved ───────────────────────────────────────────────────────
    print("\n[4] Merging preserved mappings…")
    orgs, newly_matched, preserved_count, total_matched = apply_matches(
        orgs, auto_matches, preserved
    )
    print(f"  Preserved from previous run : {preserved_count}")
    print(f"  Total matched               : {total_matched} / {len(orgs)}")

    # ── Save or stats ─────────────────────────────────────────────────────────
    if args.stats:
        print("\n[stats mode] No file written.")
        return

    print("\n[5] Saving…")
    save(orgs)
    print("\nDone.")


if __name__ == "__main__":
    main()
