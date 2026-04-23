#!/usr/bin/env python3
"""
import_edf_projects.py — Creates EDF-NNNN project entities and edf_participation
relationships from rawdata/edf_calls.json.

Source data:
  rawdata/edf_calls.json  — 201 calls, 64 with projects, 78 projects, 1657 participant slots
  data/edf_orgs.json      — PIC→db_id crosswalk for 794 EDF orgs

Output (written to data/database.json):
  - EDF-NNNN entities  (type: edf_project)
  - edf_participation relationships  (source=db_id, target=EDF-NNNN)

Re-run safe: skips existing EDF-NNNN entities and duplicate relationships.

Usage:
  python3 scripts/import_edf_projects.py [--dry-run]
"""

import json
import os
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "data", "database.json")
EDF_CALLS_PATH = os.path.join(BASE, "rawdata", "edf_calls.json")
EDF_ORGS_PATH = os.path.join(BASE, "data", "edf_orgs.json")

TODAY = date.today().isoformat()
DRY_RUN = "--dry-run" in sys.argv


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def next_edf_id(existing_ids: set[str]) -> str:
    nums = []
    for eid in existing_ids:
        if eid.startswith("EDF-"):
            try:
                nums.append(int(eid[4:]))
            except ValueError:
                pass
    n = max(nums) + 1 if nums else 1
    return f"EDF-{n:04d}"


def make_edf_entity(edf_id: str, project: dict, call_key: str, call_title: str) -> dict:
    start = project.get("start_date", "") or ""
    end = project.get("end_date", "") or ""
    return {
        "id": edf_id,
        "type": "edf_project",
        "name": project.get("title", edf_id),
        "roles": [],
        "sector": None,
        "wikidata_id": None,
        "sources": {
            "edf_project": {
                "project_id": project.get("project_id"),
                "acronym": project.get("acronym"),
                "call_id": call_key,
                "call_title": call_title,
                "status": project.get("status"),
                "start_date": start[:10] if start else None,
                "end_date": end[:10] if end else None,
                "overall_budget": project.get("overall_budget"),
                "eu_contribution": project.get("eu_contribution"),
                "url": project.get("url"),
                "type_of_action": project.get("type_of_action"),
            }
        },
        "history": [
            {
                "date": TODAY,
                "action": "created",
                "source": "edf_calls.json",
                "author": "import_edf_projects.py",
                "note": f"EDF project {project.get('acronym', project.get('project_id'))} "
                        f"from call {call_key}",
            }
        ],
        "validation": [],
        "tags": [],
    }


def make_rel(db_id: str, edf_id: str, role: str, eu_contribution) -> dict:
    return {
        "source": db_id,
        "target": edf_id,
        "type": "edf_participation",
        "role": role,
        "eu_contribution": eu_contribution,
        "created_at": TODAY,
    }


def main():
    db = load_json(DB_PATH)
    edf_calls_data = load_json(EDF_CALLS_PATH)
    edf_orgs_data = load_json(EDF_ORGS_PATH)

    calls = edf_calls_data["calls"]
    orgs = edf_orgs_data["orgs"]

    entities: list = db["entities"]
    relationships: list = db["relationships"]

    # Index existing state
    existing_entity_ids: set[str] = {e["id"] for e in entities}
    existing_rels: set[tuple] = {
        (r.get("source"), r.get("target"), r.get("type"))
        for r in relationships
    }

    # Index project_id → EDF-NNNN (for re-run safety)
    existing_project_ids: dict[str, str] = {}
    for e in entities:
        if e.get("type") == "edf_project":
            proj_src = (e.get("sources") or {}).get("edf_project") or {}
            pid = proj_src.get("project_id")
            if pid:
                existing_project_ids[pid] = e["id"]

    new_entities: list[dict] = []
    new_rels: list[dict] = []
    skipped_entities = 0
    skipped_rels = 0
    missing_pic = 0

    for call_key, call in calls.items():
        projects = call.get("projects") or []
        call_title = call.get("title", "")

        for project in projects:
            project_id = project.get("project_id")

            # Find or create EDF entity for this project
            if project_id in existing_project_ids:
                edf_id = existing_project_ids[project_id]
                skipped_entities += 1
            else:
                all_ids = existing_entity_ids | {e["id"] for e in new_entities}
                edf_id = next_edf_id(all_ids)
                entity = make_edf_entity(edf_id, project, call_key, call_title)
                new_entities.append(entity)
                existing_project_ids[project_id] = edf_id
                existing_entity_ids.add(edf_id)

            # Create relationships for each participant
            for participant in project.get("participants") or []:
                pic = str(participant.get("pic", ""))
                if pic not in orgs:
                    missing_pic += 1
                    print(f"  WARN: PIC {pic} ({participant.get('organization_name')}) "
                          f"not in edf_orgs — skipping")
                    continue

                db_id = orgs[pic].get("db_id")
                if not db_id:
                    missing_pic += 1
                    print(f"  WARN: PIC {pic} ({participant.get('organization_name')}) "
                          f"has no db_id — skipping")
                    continue

                role = participant.get("role", "participant")
                eu_contrib = participant.get("eu_contribution")
                try:
                    eu_contrib = float(eu_contrib) if eu_contrib is not None else None
                except (TypeError, ValueError):
                    eu_contrib = None

                rel_key = (db_id, edf_id, "edf_participation")
                if rel_key in existing_rels:
                    skipped_rels += 1
                    continue

                rel = make_rel(db_id, edf_id, role, eu_contrib)
                new_rels.append(rel)
                existing_rels.add(rel_key)

    print(f"\nSummary:")
    print(f"  New EDF project entities:      {len(new_entities)}")
    print(f"  Skipped (already exist):       {skipped_entities}")
    print(f"  New edf_participation rels:    {len(new_rels)}")
    print(f"  Skipped rels (duplicate):      {skipped_rels}")
    print(f"  Missing PIC / no db_id:        {missing_pic}")

    if DRY_RUN:
        print("\n[DRY RUN] No changes written.")
        return

    entities.extend(new_entities)
    relationships.extend(new_rels)
    db["_updated"] = TODAY

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {DB_PATH}")
    print(f"  Total entities:      {len(entities)}")
    print(f"  Total relationships: {len(relationships)}")
    print("\nNext step: python3 scripts/validate.py")


if __name__ == "__main__":
    main()
