"""
merge_edf_calls.py — add new projects/calls from fresh EDF fetches to an archived raw file.

Why: the EDF API can stop returning older projects (June 2026 -> Oct 2026: 40 gone).
Old data is never lost: everything in the archive is kept byte-identical; only calls and
projects (by project_id) that are missing from it are added. Where a fetch differs on an
existing project, the archived value is kept.

Usage:
    # 1. keep an untouched copy of the current raw file
    cp rawdata/edf_calls.json rawdata/edf_calls_YYYY-MM-DD.json
    # 2. fetch (overwrites rawdata/edf_calls.json); optionally save each fetch as a copy
    python3 scripts/fetch_edf_bulk.py
    # 3. merge archive + fetch(es) into rawdata/edf_calls.json
    python3 scripts/merge_edf_calls.py rawdata/edf_calls_YYYY-MM-DD.json [extra_fetch.json ...] [--write]

Without --write it only checks and prints the counts (dry-run).
"""
import datetime
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT = os.path.join(BASE, "rawdata", "edf_calls.json")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(args):
    write = "--write" in args
    paths = [a for a in args if a != "--write"]
    if not paths:
        sys.exit(__doc__)
    old = load(paths[0])
    fetches = [load(p) for p in paths[1:]] + [load(CURRENT)]

    out = json.loads(json.dumps(old))
    old_ids = {p["project_id"] for c in old["calls"].values() for p in c.get("projects") or []}
    added, new_calls, differing = [], [], 0

    for src in fetches:
        for cid, call in src["calls"].items():
            if cid not in out["calls"]:
                new_call = json.loads(json.dumps(call))
                new_call["projects"] = []
                out["calls"][cid] = new_call
                new_calls.append(cid)
            tgt = out["calls"][cid]
            tgt.setdefault("projects", [])
            have = {p["project_id"]: p for p in tgt["projects"]}
            for p in call.get("projects") or []:
                if p["project_id"] not in have:
                    tgt["projects"].append(p)
                    have[p["project_id"]] = p
                    added.append((cid, p["acronym"]))
                elif p["project_id"] in old_ids and have[p["project_id"]] != p:
                    differing += 1

    out["_total_calls"] = len(out["calls"])
    out["_generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Safety checks: nothing from the archive may be lost or altered
    assert set(old["calls"]) <= set(out["calls"]), "archived calls lost"
    for cid, call in old["calls"].items():
        for p in call.get("projects") or []:
            assert p in out["calls"][cid]["projects"], ("archived project altered", cid, p["acronym"])

    total = sum(len(c["projects"]) for c in out["calls"].values())
    print(f"archive: {len(old_ids)} projects -> merged: {total} (+{len(added)} new), "
          f"+{len(new_calls)} new calls, {differing} comparisons where fetch differs (archive kept)")
    if write:
        with open(CURRENT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"✓ written {CURRENT}")
    else:
        print("[DRY RUN] no file written (pass --write)")


if __name__ == "__main__":
    main(sys.argv[1:])
