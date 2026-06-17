"""
patch_edf_objectives.py — add sources.edf_project.objective to all EDF-NNNN entities.

Reads:  rawdata/edf_calls.json, data/database.json
Writes: data/database.json (sources.edf_project.objective + history[])
Safe:   skips entities that already have objective set
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
RAW  = ROOT / "rawdata" / "edf_calls.json"
DB   = ROOT / "data" / "database.json"

DRY_RUN = "--dry-run" in sys.argv


def main():
    with open(RAW) as f:
        raw = json.load(f)
    with open(DB) as f:
        db = json.load(f)

    SKIP_PATTERNS = {"n/a", "not provided", "restricted", "included in part b"}

    def is_valid_objective(text: str) -> bool:
        if len(text) < 60:
            return False
        if len(text) < 200:
            low = text.lower()
            if any(p in low for p in SKIP_PATTERNS):
                return False
        return True

    # Build project_id → objective index
    obj_map: dict[str, str] = {}
    for call in raw["calls"].values():
        for proj in call.get("projects", []):
            if not isinstance(proj, dict):
                continue
            pid = proj.get("project_id")
            obj = proj.get("objective", "").strip()
            if pid and is_valid_objective(obj):
                obj_map[pid] = obj

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    updated = 0
    skipped = 0

    for e in db["entities"]:
        if e.get("type") != "edf_project":
            continue
        ps = e.get("sources", {}).get("edf_project", {})
        pid = ps.get("project_id")
        if not pid:
            continue
        if ps.get("objective"):
            skipped += 1
            continue
        obj = obj_map.get(pid)
        if not obj:
            print(f"  WARNING: no objective found for {e['id']} (project_id={pid})")
            continue

        if not DRY_RUN:
            ps["objective"] = obj
            e.setdefault("history", []).append({
                "date":   now,
                "action": "field_added",
                "fields": ["sources.edf_project.objective"],
                "note":   "patch_edf_objectives: added project objective from edf_calls.json",
            })

        updated += 1
        acronym = ps.get("acronym") or e["id"]
        prefix = "[DRY-RUN] " if DRY_RUN else ""
        print(f"  {prefix}{e['id']} {acronym}: objective added ({len(obj)} chars)")

    if not DRY_RUN:
        with open(DB, "w") as f:
            json.dump(db, f, ensure_ascii=False)
        print(f"\nWrote {DB}")

    print(f"\nDone — updated: {updated}, already had objective: {skipped}")
    if DRY_RUN:
        print("(dry-run — no writes)")


if __name__ == "__main__":
    main()
