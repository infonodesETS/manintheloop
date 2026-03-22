#!/usr/bin/env python3
"""
EDF Explorer — lookup, filter and analyse EDF calls that have projects.

Usage:
  python scripts/edf_explorer.py participants --by-country
  python scripts/edf_explorer.py participants --by-org [--top 20]
  python scripts/edf_explorer.py participants --coordinators [--top 20]
  python scripts/edf_explorer.py participants --sme
  python scripts/edf_explorer.py participants --activity-type

  python scripts/edf_explorer.py filter --domain AIR
  python scripts/edf_explorer.py filter --call-type DA
  python scripts/edf_explorer.py filter --keyword hypersonic
  python scripts/edf_explorer.py filter --country France
  python scripts/edf_explorer.py filter --sme-only
  python scripts/edf_explorer.py filter --show-call EDF-2023-DA-AIR-NGWS
  python scripts/edf_explorer.py filter --show-project ENGRT
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "edf_calls.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_data() -> dict:
    with DATA_FILE.open() as f:
        return json.load(f)


def calls_with_projects(data: dict) -> list[dict]:
    """Return only calls that have at least one project."""
    return [c for c in data["calls"].values() if c.get("projects")]


def all_projects(calls: list[dict]) -> list[dict]:
    """Flatten all projects from the given calls, injecting call identifier."""
    out = []
    for call in calls:
        for proj in call.get("projects", []):
            out.append({**proj, "_call_id": call["identifier"]})
    return out


def all_participants(projects: list[dict]) -> list[dict]:
    """Flatten all participants, injecting project info."""
    out = []
    for proj in projects:
        for p in proj.get("participants", []):
            out.append({
                **p,
                "_project_title": proj.get("title", ""),
                "_project_acronym": proj.get("acronym", ""),
                "_project_id": proj.get("project_id", ""),
                "_call_id": proj.get("_call_id", ""),
            })
    return out


def parse_identifier(identifier: str) -> dict:
    """Extract year, call_type, domain from an EDF call identifier."""
    parts = identifier.split("-")
    return {
        "year": parts[1] if len(parts) > 1 else "",
        "call_type": parts[2] if len(parts) > 2 else "",
        "domain": parts[3] if len(parts) > 3 else "",
    }


def fmt_eur(value) -> str:
    try:
        return f"€{float(value):>16,.0f}"
    except (TypeError, ValueError):
        return "              N/A"


def col(text, width, align="left") -> str:
    text = str(text)
    if align == "right":
        return text[:width].rjust(width)
    return text[:width].ljust(width)


def hr(width=80) -> str:
    return "─" * width


# ---------------------------------------------------------------------------
# Participants / Organisations
# ---------------------------------------------------------------------------

def cmd_participants(args, data):
    calls = calls_with_projects(data)
    projects = all_projects(calls)
    participants = all_participants(projects)

    if args.by_country:
        _participants_by_country(participants)
    elif args.by_org:
        _participants_by_org(participants, args.top)
    elif args.coordinators:
        _coordinators(participants, args.top)
    elif args.sme:
        _sme_breakdown(participants)
    elif args.activity_type:
        _activity_type(participants)
    else:
        print("Specify one of: --by-country, --by-org, --coordinators, --sme, --activity-type")
        sys.exit(1)


def _participants_by_country(participants: list[dict]):
    country_count: dict[str, int] = defaultdict(int)
    country_eu: dict[str, float] = defaultdict(float)
    country_sme: dict[str, int] = defaultdict(int)

    for p in participants:
        c = p.get("country") or "Unknown"
        country_count[c] += 1
        try:
            country_eu[c] += float(p.get("eu_contribution") or 0)
        except (TypeError, ValueError):
            pass
        if p.get("sme"):
            country_sme[c] += 1

    rows = sorted(country_count.items(), key=lambda x: -x[1])
    total = len(participants)

    print(f"\n{'PARTICIPANTS BY COUNTRY':^80}")
    print(hr())
    print(f"{'Country':<25} {'Parts':>6}  {'%':>5}  {'SMEs':>5}  {'EU Contribution':>17}")
    print(hr())
    for country, count in rows:
        pct = count / total * 100
        print(
            f"{col(country, 25)} {count:>6}  {pct:>5.1f}%  {country_sme[country]:>5}  "
            f"{fmt_eur(country_eu[country])}"
        )
    print(hr())
    print(f"{'TOTAL':<25} {total:>6}  {'100%':>6}  {sum(country_sme.values()):>5}  "
          f"{fmt_eur(sum(country_eu.values()))}")


def _participants_by_org(participants: list[dict], top: int):
    org_count: dict[str, int] = defaultdict(int)
    org_eu: dict[str, float] = defaultdict(float)
    org_country: dict[str, str] = {}
    org_sme: dict[str, bool] = {}

    for p in participants:
        name = p.get("organization_name") or "Unknown"
        org_count[name] += 1
        try:
            org_eu[name] += float(p.get("eu_contribution") or 0)
        except (TypeError, ValueError):
            pass
        org_country[name] = p.get("country", "")
        org_sme[name] = p.get("sme", False)

    rows = sorted(org_count.items(), key=lambda x: -x[1])[:top]

    print(f"\n{'TOP ' + str(top) + ' ORGANISATIONS BY PARTICIPATIONS':^90}")
    print(hr(90))
    print(f"{'Organisation':<40} {'Country':<18} {'Parts':>5}  {'SME':>4}  {'EU Contribution':>17}")
    print(hr(90))
    for name, count in rows:
        sme_flag = "yes" if org_sme.get(name) else "no"
        print(
            f"{col(name, 40)} {col(org_country.get(name,''), 18)} {count:>5}  "
            f"{sme_flag:>4}  {fmt_eur(org_eu[name])}"
        )


def _coordinators(participants: list[dict], top: int):
    coord_projects: dict[str, set] = defaultdict(set)
    coord_country: dict[str, str] = {}
    coord_eu: dict[str, float] = defaultdict(float)

    for p in participants:
        if p.get("role", "").lower() == "coordinator":
            name = p.get("organization_name") or "Unknown"
            coord_projects[name].add(p.get("_project_id", ""))
            coord_country[name] = p.get("country", "")
            try:
                coord_eu[name] += float(p.get("eu_contribution") or 0)
            except (TypeError, ValueError):
                pass

    rows = sorted(coord_projects.items(), key=lambda x: -len(x[1]))[:top]

    print(f"\n{'TOP ' + str(top) + ' COORDINATORS BY PROJECTS LED':^90}")
    print(hr(90))
    print(f"{'Organisation':<40} {'Country':<18} {'Projects':>8}  {'EU Contribution':>17}")
    print(hr(90))
    for name, project_ids in rows:
        print(
            f"{col(name, 40)} {col(coord_country.get(name,''), 18)} {len(project_ids):>8}  "
            f"{fmt_eur(coord_eu[name])}"
        )


def _sme_breakdown(participants: list[dict]):
    total = len(participants)
    sme = sum(1 for p in participants if p.get("sme"))
    non_sme = total - sme

    country_sme: dict[str, list] = defaultdict(lambda: [0, 0])  # [sme, total]
    for p in participants:
        c = p.get("country") or "Unknown"
        country_sme[c][1] += 1
        if p.get("sme"):
            country_sme[c][0] += 1

    print(f"\n{'SME BREAKDOWN':^60}")
    print(hr(60))
    print(f"  Total participants : {total}")
    print(f"  SMEs               : {sme}  ({sme/total*100:.1f}%)")
    print(f"  Non-SMEs           : {non_sme}  ({non_sme/total*100:.1f}%)")
    print()

    rows = [(c, v[0], v[1]) for c, v in country_sme.items() if v[0] > 0]
    rows.sort(key=lambda x: -x[1])

    print(f"{'Country':<25} {'SMEs':>5}  {'Total':>6}  {'SME %':>6}")
    print(hr(60))
    for country, n_sme, n_total in rows:
        print(f"{col(country, 25)} {n_sme:>5}  {n_total:>6}  {n_sme/n_total*100:>5.1f}%")


def _activity_type(participants: list[dict]):
    atype_count: dict[str, int] = defaultdict(int)
    atype_eu: dict[str, float] = defaultdict(float)

    for p in participants:
        at = p.get("activity_type") or "Unknown"
        atype_count[at] += 1
        try:
            atype_eu[at] += float(p.get("eu_contribution") or 0)
        except (TypeError, ValueError):
            pass

    total = len(participants)
    rows = sorted(atype_count.items(), key=lambda x: -x[1])

    print(f"\n{'PARTICIPANTS BY ACTIVITY TYPE':^80}")
    print(hr(80))
    print(f"{'Activity Type':<45} {'Count':>6}  {'%':>5}  {'EU Contribution':>17}")
    print(hr(80))
    for at, count in rows:
        print(
            f"{col(at, 45)} {count:>6}  {count/total*100:>5.1f}%  {fmt_eur(atype_eu[at])}"
        )


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------

def cmd_filter(args, data):
    calls = calls_with_projects(data)

    if args.show_call:
        _show_call(args.show_call, data)
    elif args.show_project:
        _show_project(args.show_project, calls)
    elif args.domain:
        _filter_by_domain(args.domain, calls)
    elif args.call_type:
        _filter_by_call_type(args.call_type, calls)
    elif args.keyword:
        _filter_by_keyword(args.keyword, calls)
    elif args.country:
        _filter_by_country(args.country, calls)
    elif args.sme_only:
        _filter_sme_only(calls)
    else:
        print("Specify one of: --domain, --call-type, --keyword, --country, --sme-only, --show-call, --show-project")
        sys.exit(1)


def _print_call_row(call: dict):
    meta = parse_identifier(call["identifier"])
    n_projects = len(call.get("projects", []))
    print(
        f"  {col(call['identifier'], 40)} "
        f"{col(meta['domain'], 10)} "
        f"{col(meta['call_type'], 5)} "
        f"{n_projects:>3} projects  {call.get('title','')[:50]}"
    )


def _filter_by_domain(domain: str, calls: list[dict]):
    domain = domain.upper()
    matched = [c for c in calls if parse_identifier(c["identifier"])["domain"] == domain]
    print(f"\nCalls with domain '{domain}': {len(matched)}\n")
    print(f"  {'Identifier':<40} {'Domain':<10} {'Type':<5} {'Projects'}")
    print(hr(90))
    for c in matched:
        _print_call_row(c)


def _filter_by_call_type(call_type: str, calls: list[dict]):
    call_type = call_type.upper()
    matched = [c for c in calls if parse_identifier(c["identifier"])["call_type"] == call_type]
    print(f"\nCalls with type '{call_type}': {len(matched)}\n")
    print(f"  {'Identifier':<40} {'Domain':<10} {'Type':<5} {'Projects'}")
    print(hr(90))
    for c in matched:
        _print_call_row(c)


def _filter_by_keyword(keyword: str, calls: list[dict]):
    kw = keyword.lower()
    matched = []
    for c in calls:
        title = (c.get("title") or "").lower()
        desc = re.sub(r"<[^>]+>", " ", c.get("description") or "").lower()
        if kw in title or kw in desc:
            matched.append(c)

    print(f"\nCalls matching keyword '{keyword}': {len(matched)}\n")
    print(f"  {'Identifier':<40} {'Domain':<10} {'Type':<5} {'Projects'}")
    print(hr(90))
    for c in matched:
        _print_call_row(c)
        # Show which project titles also match
        for proj in c.get("projects", []):
            if kw in (proj.get("title") or "").lower() or kw in (proj.get("objective") or "").lower():
                print(f"      -> {proj.get('acronym','')} — {proj.get('title','')[:60]}")


def _filter_by_country(country: str, calls: list[dict]):
    country_lower = country.lower()
    results = []  # (call, project, participant_count)
    for call in calls:
        for proj in call.get("projects", []):
            country_parts = [
                p for p in proj.get("participants", [])
                if (p.get("country") or "").lower() == country_lower
            ]
            if country_parts:
                results.append((call["identifier"], proj, country_parts))

    print(f"\nProjects with participants from '{country}': {len(results)}\n")
    print(f"  {'Call':<35} {'Acronym':<12} {'Title':<40} {'Parts':>5}")
    print(hr(100))
    for call_id, proj, parts in results:
        print(
            f"  {col(call_id, 35)} {col(proj.get('acronym',''), 12)} "
            f"{col(proj.get('title',''), 40)} {len(parts):>5}"
        )
        for p in parts:
            role = p.get("role", "")
            sme = " [SME]" if p.get("sme") else ""
            print(f"      {col(p.get('organization_name',''), 45)} {role}{sme}")


def _filter_sme_only(calls: list[dict]):
    results = []
    for call in calls:
        for proj in call.get("projects", []):
            smes = [p for p in proj.get("participants", []) if p.get("sme")]
            if smes:
                results.append((call["identifier"], proj, smes))

    total_sme_parts = sum(len(s) for _, _, s in results)
    print(f"\nProjects with at least one SME: {len(results)}  (total SME participations: {total_sme_parts})\n")
    print(f"  {'Call':<35} {'Acronym':<12} {'Title':<40} {'SMEs':>4}")
    print(hr(100))
    for call_id, proj, smes in results:
        print(
            f"  {col(call_id, 35)} {col(proj.get('acronym',''), 12)} "
            f"{col(proj.get('title',''), 40)} {len(smes):>4}"
        )


def _show_call(identifier: str, data: dict):
    call = data["calls"].get(identifier)
    if not call:
        # try case-insensitive
        for k, v in data["calls"].items():
            if k.lower() == identifier.lower():
                call = v
                break
    if not call:
        print(f"Call '{identifier}' not found.")
        sys.exit(1)

    print(f"\n{'CALL DETAIL':^80}")
    print(hr())
    print(f"  Identifier : {call['identifier']}")
    print(f"  Title      : {call.get('title','')}")
    print(f"  ccm2Id     : {call.get('ccm2Id','')}")
    print(f"  Status     : {call.get('status') or '(empty)'}")
    print(f"  Deadline   : {call.get('deadline') or '(empty)'}")
    print()

    # Budget
    bmap = call.get("budget_overview", {}).get("budgetTopicActionMap", {})
    for ccm2, actions in bmap.items():
        for a in actions:
            if a.get("action", "").startswith(call["identifier"]):
                year_map = a.get("budgetYearMap", {})
                budget_str = ", ".join(f"{y}: {fmt_eur(v)}" for y, v in year_map.items())
                print(f"  Budget     : {budget_str}")
                print(f"  Deadline(s): {', '.join(a.get('deadlineDates', []))}")
                print(f"  Model      : {a.get('deadlineModel','')}")
                break

    print()
    desc_clean = re.sub(r"<[^>]+>", " ", call.get("description") or "")
    desc_clean = re.sub(r"\s+", " ", desc_clean).strip()
    print(f"  Description (stripped):\n  {desc_clean[:600]}{'...' if len(desc_clean) > 600 else ''}")

    projects = call.get("projects", [])
    print(f"\n  Projects ({len(projects)}):")
    print(hr())
    for proj in projects:
        print(f"    [{proj.get('acronym','')}] {proj.get('title','')}")
        print(f"      Status   : {proj.get('status','')}  |  Type: {proj.get('type_of_action','')}")
        print(f"      Dates    : {proj.get('start_date','')[:10]} → {proj.get('end_date','')[:10]}")
        print(f"      Budget   : overall {fmt_eur(proj.get('overall_budget'))}  |  EU contrib {fmt_eur(proj.get('eu_contribution'))}")
        print(f"      Participants: {len(proj.get('participants', []))}")
        print()


def _show_project(query: str, calls: list[dict]):
    query_lower = query.lower()
    found = []
    for call in calls:
        for proj in call.get("projects", []):
            if (
                query_lower in (proj.get("acronym") or "").lower()
                or query_lower in (proj.get("title") or "").lower()
                or str(proj.get("project_id", "")) == query
            ):
                found.append((call["identifier"], proj))

    if not found:
        print(f"No project matching '{query}' found.")
        sys.exit(1)

    for call_id, proj in found:
        print(f"\n{'PROJECT DETAIL':^90}")
        print(hr(90))
        print(f"  Call       : {call_id}")
        print(f"  Title      : {proj.get('title','')}")
        print(f"  Acronym    : {proj.get('acronym','')}")
        print(f"  Project ID : {proj.get('project_id','')}")
        print(f"  Status     : {proj.get('status','')}")
        print(f"  Type       : {proj.get('type_of_action','')}")
        print(f"  Dates      : {proj.get('start_date','')[:10]} → {proj.get('end_date','')[:10]}")
        print(f"  Budget     : overall {fmt_eur(proj.get('overall_budget'))}  |  EU contrib {fmt_eur(proj.get('eu_contribution'))}")
        print(f"  URL        : {proj.get('url','')}")
        print()
        obj = re.sub(r"\s+", " ", (proj.get("objective") or "")).strip()
        print(f"  Objective:\n  {obj[:600]}{'...' if len(obj) > 600 else ''}")
        print()

        participants = proj.get("participants", [])
        print(f"  Participants ({len(participants)}):")
        print(hr(90))
        print(f"  {'Organisation':<40} {'Country':<18} {'Role':<12} {'SME':>4}  {'EU Contribution':>17}")
        print(hr(90))
        for p in sorted(participants, key=lambda x: (x.get("order") or 999)):
            sme_flag = "yes" if p.get("sme") else "no"
            print(
                f"  {col(p.get('organization_name',''), 40)} "
                f"{col(p.get('country',''), 18)} "
                f"{col(p.get('role',''), 12)} "
                f"{sme_flag:>4}  {fmt_eur(p.get('eu_contribution'))}"
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EDF Explorer — analyse EDF calls with projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--data", metavar="PATH", help=f"Path to edf_calls.json (default: {DATA_FILE})"
    )

    sub = parser.add_subparsers(dest="command")

    # --- participants ---
    p_parts = sub.add_parser("participants", help="Analyse participants and organisations")
    group = p_parts.add_mutually_exclusive_group(required=True)
    group.add_argument("--by-country", action="store_true", help="Count + EU contribution by country")
    group.add_argument("--by-org", action="store_true", help="Top organisations by participations")
    group.add_argument("--coordinators", action="store_true", help="Coordinators ranked by projects led")
    group.add_argument("--sme", action="store_true", help="SME vs non-SME breakdown")
    group.add_argument("--activity-type", action="store_true", help="Breakdown by activity type")
    p_parts.add_argument("--top", type=int, default=20, metavar="N", help="Limit results to top N (default: 20)")

    # --- filter ---
    p_filter = sub.add_parser("filter", help="Filter calls and projects")
    fgroup = p_filter.add_mutually_exclusive_group(required=True)
    fgroup.add_argument("--domain", metavar="DOMAIN", help="Filter calls by domain (e.g. AIR, NAVAL, SPACE)")
    fgroup.add_argument("--call-type", metavar="TYPE", help="Filter by call type (e.g. DA, RA, CSA)")
    fgroup.add_argument("--keyword", metavar="WORD", help="Keyword search in title and description")
    fgroup.add_argument("--country", metavar="COUNTRY", help="Projects with participants from a country")
    fgroup.add_argument("--sme-only", action="store_true", help="Projects with at least one SME participant")
    fgroup.add_argument("--show-call", metavar="ID", help="Full detail for a call by identifier")
    fgroup.add_argument("--show-project", metavar="QUERY", help="Full detail for a project by acronym, title or ID")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    global DATA_FILE
    if args.data:
        DATA_FILE = Path(args.data)

    data = load_data()

    if args.command == "participants":
        cmd_participants(args, data)
    elif args.command == "filter":
        cmd_filter(args, data)


if __name__ == "__main__":
    main()
