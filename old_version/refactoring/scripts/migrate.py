#!/usr/bin/env python3
"""
migrate.py — One-shot migration from investments.json + startups.json → database.json (v2.0)
"""

import json
import re
import os
from datetime import date

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVESTMENTS_PATH = os.path.join(BASE, "..", "crunchbase_full", "investments.json")
STARTUPS_PATH    = os.path.join(BASE, "..", "crunchbase_scraping", "test_startup", "startups.json")
OUTPUT_PATH      = os.path.join(BASE, "data", "database.json")

TODAY = date.today().isoformat()  # 2026-03-14

# ── Known data issues ──────────────────────────────────────────────────────────
WIKIDATA_ERRORS = {
    "NVIDIA": {
        "bad_id": "Q2283",
        "desc": "wikidata_id was Q2283 (Microsoft), reset to null — needs correct ID",
    },
    "Amazon": {
        "bad_id": "Q380",
        "desc": "wikidata_id was Q380 (Meta), reset to null — needs correct ID",
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def normalize_date(raw: str) -> str | None:
    """Convert '20260307' → '2026-03-07'. Return None if not parseable."""
    raw = str(raw).strip()
    m = re.match(r"^(\d{4})(\d{2})(\d{2})$", raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # already ISO?
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return raw
    return None


def to_int_or_none(val: str) -> int | None:
    try:
        v = str(val).strip().replace(",", "")
        return int(v) if v else None
    except (ValueError, TypeError):
        return None


def split_csv(val: str) -> list[str]:
    """Split a comma-separated string, stripping whitespace."""
    if not val or not val.strip():
        return []
    return [s.strip() for s in val.split(",") if s.strip()]


def get_latest_cb_key(company_data: dict) -> str | None:
    """Return the latest numeric date key from a company dict."""
    numeric_keys = [k for k in company_data if re.match(r"^\d+$", k)]
    if not numeric_keys:
        return None
    return sorted(numeric_keys)[-1]


def get_infonodes_key(company_data: dict) -> str | None:
    """Return the infonodes key (ends with '_infonodes')."""
    for k in company_data:
        if k.endswith("_infonodes"):
            return k
    return None


# ── Investor classification ─────────────────────────────────────────────────────

GOV_KEYWORDS = [
    "darpa", "arpa-e", "arpa", "dod", "eib", "edf", "kfw", "nato", "esa",
    "department of", "ministry", "agency", "government", "commission",
    "investment fund", "innovation fund", "development bank", "us army",
    "united states air force", "united states navy", "u.s. department",
    "us department", "air force research", "scottish enterprise",
    "australian renewable energy", "natural resources canada",
    "innovation norway", "business finland", "solidium",
    "vinnova", "jare", "enova", "norwegian research",
    "canada's ocean", "african equity", "sekunjalo", "nordic investment bank",
    "maine technology", "california energy", "penndo", "nyserda",
    "uk space agency", "bnf resources", "eudis", "diana",
    "public investment fund", "ma'aden", "japan bank",
    "european union", "european commission", "government of",
    "business.gov", "hancock prospecting", "clean energy finance",
    "transition énergétique", "pim cupric", "synergy capital",
    "lg energy", "sahsen", "office of strategic capital",
    "massachusetts clean energy", "technology partners",
    "mercedez-benz group ag", "toyota motor", "panasonic",
    "industrial and commercial bank", "china merchants bank",
    "al wahada capital", "societe generale", "vantagepoint capital",
    "saudi exim",
]

BANK_KEYWORDS = [
    "bank", "banque", "capital markets", "goldman", "morgan",
    "bnp", "credit", "citi", "hsbc", "barclays", "paribas",
    "deutsche bank", "mizuho", "dbs bank", "aol",
    "intesa sanpaolo", "monte dei paschi", "banco bpm", "caixabank",
    "commerzbank", "crédit agricole", "credit agricole",
    "santander", "banco do brasil", "citibank", "commonwealth bank",
    "national australia bank", "societe generale", "jpmorgan", "jp morgan",
    "wells fargo", "banco santander",
]

INSTITUTION_KEYWORDS = [
    "university", "institute", "foundation", "trust",
]


def classify_investor(name: str) -> str:
    n = name.lower()
    for kw in GOV_KEYWORDS:
        if kw in n:
            return "government_agency"
    for kw in INSTITUTION_KEYWORDS:
        if kw in n:
            return "institution"
    for kw in BANK_KEYWORDS:
        if kw in n:
            return "bank"
    return "fund"


# ── Step 1: Load inputs ────────────────────────────────────────────────────────

def load_inputs():
    with open(INVESTMENTS_PATH, encoding="utf-8") as f:
        investments = json.load(f)
    with open(STARTUPS_PATH, encoding="utf-8") as f:
        startups = json.load(f)
    return investments, startups


# ── Step 3: Normalize a company from investments.json ─────────────────────────

def normalize_company(name: str, company_data: dict) -> dict:
    cb_key = get_latest_cb_key(company_data)
    inf_key = get_infonodes_key(company_data)

    cb = company_data.get(cb_key, {}) if cb_key else {}
    inf = company_data.get(inf_key, {}) if inf_key else {}
    raw_validation = company_data.get("validation_status", [])

    # ── Crunchbase fields ──────────────────────────────────────────────────────
    extracted_at_cb = normalize_date(cb_key) if cb_key else None

    cb_rank_raw = cb.get("CB Rank (Company)", "")
    cb_rank = to_int_or_none(cb_rank_raw)

    total_funding_usd = to_int_or_none(cb.get("Total Funding Amount (in USD)", ""))
    total_funding_native_amount = to_int_or_none(cb.get("Total Funding Amount", ""))
    total_funding_native_currency = cb.get("Total Funding Amount Currency", "") or None
    total_funding_native = None
    if total_funding_native_amount is not None and total_funding_native_currency:
        total_funding_native = {
            "amount": total_funding_native_amount,
            "currency": total_funding_native_currency,
        }

    industries = split_csv(cb.get("Industries", ""))
    industry_groups = split_csv(cb.get("Industry Groups", ""))
    founders = split_csv(cb.get("Founders", ""))

    source_cb = {
        "extracted_at": extracted_at_cb,
        "profile_url": cb.get("Organization Name URL") or None,
        "stage": cb.get("Stage") or "",
        "description": cb.get("Description") or None,
        "description_full": None,
        "headquarters": cb.get("Headquarters Location") or None,
        "website": cb.get("Website") or None,
        "cb_rank": cb_rank,
        "revenue_range": cb.get("Estimated Revenue Range") or None,
        "total_funding_usd": total_funding_usd,
        "total_funding_native": total_funding_native,
        "founders": founders,
        "industries": industries,
        "industry_groups": industry_groups,
        "primary_industry": cb.get("Primary Industry") or None,
        "primary_industry_url": cb.get("Primary Industry URL") or None,
        "investor_type": cb.get("Investor Type") or "",
        "patents_granted": None,
        "domain": None,
        "acquired_by": None,
        "acquired_by_url": None,
    }

    # ── Infonodes fields ───────────────────────────────────────────────────────
    extracted_at_inf = normalize_date(inf.get("extracting-date", "")) if inf else None
    wikidata_id = inf.get("wikidata_id", "") or None
    if wikidata_id == "":
        wikidata_id = None

    source_inf = {
        "extracted_at": extracted_at_inf,
        "sector": inf.get("sector") or None,
        "country": inf.get("country") or None,
        "tax_id": inf.get("tax_id") or None,
        "main_focus": inf.get("main_focus") or None,
        "wikipedia_url": inf.get("wikipedia_url") or None,
    }

    # ── Sector ─────────────────────────────────────────────────────────────────
    sector = source_inf.get("sector")

    # ── Roles ─────────────────────────────────────────────────────────────────
    investor_type = cb.get("Investor Type", "")
    if investor_type == "Corporate Venture Capital":
        roles = ["manufacturer", "investor"]
    else:
        roles = ["manufacturer"]

    # ── Validation ────────────────────────────────────────────────────────────
    validation = []

    # Roles needs review
    validation.append({
        "status": "needs_review",
        "description": "roles inferred from Investor Type only",
        "author": "migrate.py",
        "datestamp": TODAY,
    })

    # Known wikidata errors
    if name in WIKIDATA_ERRORS:
        err = WIKIDATA_ERRORS[name]
        if wikidata_id == err["bad_id"]:
            wikidata_id = None
            validation.append({
                "status": "flagged",
                "description": err["desc"],
                "author": "migrate.py",
                "datestamp": TODAY,
            })

    # Preserve existing validation_status entries
    for vs in raw_validation:
        normalized_vs = dict(vs)
        if "datestamp" in normalized_vs:
            normalized_vs["datestamp"] = normalize_date(str(normalized_vs["datestamp"])) or str(normalized_vs["datestamp"])
        if "validation_description" in normalized_vs:
            normalized_vs["description"] = normalized_vs.pop("validation_description")
        validation.append(normalized_vs)

    # ── History ───────────────────────────────────────────────────────────────
    history = [{
        "date": TODAY,
        "source": "migration",
        "author": "migrate.py",
        "field": "*",
        "old": None,
        "new": None,
        "description": "Initial migration from investments.json v1",
    }]

    return {
        "name": name,
        "sector": sector,
        "wikidata_id": wikidata_id,
        "sources": {
            "crunchbase": source_cb,
            "infonodes": source_inf,
            "wikidata": None,
        },
        "history": history,
        "validation": validation,
        "tags": [],
        # Keep for Step 5/6 (investor strings)
        "_top5": cb.get("Top 5 Investors", ""),
        "_lead": cb.get("Lead Investors", ""),
    }


# ── Step 4: Merge startups.json ───────────────────────────────────────────────

def merge_startups(companies: dict[str, dict], startups: dict) -> dict[str, list]:
    """
    Merge extra fields from startups.json into matching companies.
    Returns a dict: name → list of {name, is_lead} investor dicts (from startups).
    """
    startup_investors: dict[str, list] = {}

    for startup_name, startup_versions in startups.items():
        # get the latest key
        latest_key = sorted(startup_versions.keys())[-1]
        sd = startup_versions[latest_key]

        investors_list = sd.get("investors", [])

        # Find matching company (case-insensitive)
        match_key = None
        for cn in companies:
            # Also handle "Delian" → "Delian Alliance Industries"
            if cn.lower() == startup_name.lower():
                match_key = cn
                break
            if startup_name.lower() in cn.lower() or cn.lower() in startup_name.lower():
                match_key = cn
                break

        if match_key is None:
            # Not found → create new entity (assign ID later)
            print(f"  [NEW] startup not in investments.json: {startup_name}")
            companies[startup_name] = {
                "name": startup_name,
                "sector": "Startup",
                "wikidata_id": None,
                "sources": {
                    "crunchbase": {
                        "extracted_at": normalize_date(latest_key),
                        "profile_url": sd.get("cb_url") or None,
                        "stage": sd.get("stage") or "",
                        "description": sd.get("description") or None,
                        "description_full": sd.get("description_full") or None,
                        "headquarters": sd.get("hq_full") or None,
                        "website": sd.get("website") or None,
                        "cb_rank": None,
                        "revenue_range": None,
                        "total_funding_usd": None,
                        "total_funding_native": None,
                        "founders": split_csv(sd.get("founders", "")),
                        "industries": split_csv(sd.get("industries_full", "")),
                        "industry_groups": [],
                        "primary_industry": None,
                        "primary_industry_url": None,
                        "investor_type": "",
                        "patents_granted": to_int_or_none(sd.get("patents_granted", "")) ,
                        "domain": sd.get("domain") or None,
                        "acquired_by": sd.get("acquired_by") or None,
                        "acquired_by_url": sd.get("acquired_by_url") or None,
                    },
                    "infonodes": None,
                    "wikidata": None,
                },
                "history": [{
                    "date": TODAY,
                    "source": "migration",
                    "author": "migrate.py",
                    "field": "*",
                    "old": None,
                    "new": None,
                    "description": "Initial migration from startups.json (not in investments.json)",
                }],
                "validation": [{
                    "status": "needs_review",
                    "description": "roles inferred from Investor Type only",
                    "author": "migrate.py",
                    "datestamp": TODAY,
                }],
                "tags": [],
                "_top5": "",
                "_lead": "",
                "roles": ["manufacturer"],
            }
            startup_investors[startup_name] = investors_list
        else:
            # Merge extra fields into crunchbase source
            cb = companies[match_key]["sources"]["crunchbase"]
            cb["description_full"] = sd.get("description_full") or None
            cb["patents_granted"] = to_int_or_none(sd.get("patents_granted", ""))
            cb["domain"] = sd.get("domain") or None
            cb["acquired_by"] = sd.get("acquired_by") or None
            cb["acquired_by_url"] = sd.get("acquired_by_url") or None
            startup_investors[match_key] = investors_list

    return startup_investors


# ── Step 5: Extract and classify investors ────────────────────────────────────

def collect_all_investors(companies: dict, startup_investors: dict[str, list]) -> dict[str, str]:
    """
    Returns {normalized_name: original_name} — wait, let me return {lower_name: original_name}.
    Also returns the type mapping.
    We'll build: investor_map = {normalized_name: type}
    """
    all_investor_names: set[str] = set()

    for company_name, cdata in companies.items():
        top5 = split_csv(cdata.get("_top5", ""))
        lead = split_csv(cdata.get("_lead", ""))
        for n in top5 + lead:
            if n:
                all_investor_names.add(n.strip())

    for investors in startup_investors.values():
        for inv in investors:
            n = inv.get("name", "").strip()
            if n:
                all_investor_names.add(n)

    # Deduplicate case-insensitively: keep first-seen casing
    seen_lower: dict[str, str] = {}
    for n in sorted(all_investor_names):
        key = n.lower()
        if key not in seen_lower:
            seen_lower[key] = n

    return seen_lower  # lower → canonical name


# ── Step 6: Build relationships ───────────────────────────────────────────────

def build_relationships(
    companies_ordered: list[str],
    entity_id_map: dict[str, str],
    investor_id_map: dict[str, str],
    investor_lower_map: dict[str, str],
    startup_investors: dict[str, list],
) -> list[dict]:
    relationships = []
    rel_counter = 1
    seen_rels: set[tuple] = set()

    def add_rel(source_iv: str, target_in: str, lead: bool, sources_list: list[str]):
        nonlocal rel_counter
        key = (source_iv, target_in)
        if key in seen_rels:
            return
        seen_rels.add(key)
        rel_id = f"REL-{rel_counter:04d}"
        rel_counter += 1
        relationships.append({
            "id": rel_id,
            "type": "investment",
            "source": source_iv,
            "target": target_in,
            "details": {"lead": lead},
            "sources": sources_list,
            "added_at": TODAY,
            "author": "migrate.py",
        })

    for company_name in companies_ordered:
        target_in = entity_id_map.get(company_name)
        if not target_in:
            continue

        cdata = companies_ordered if isinstance(companies_ordered, dict) else None
        # We iterate company names, look up the data separately
        # Actually let's do this differently
        pass

    return relationships


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading inputs...")
    investments, startups = load_inputs()

    # ── Step 2 & 3: Build normalized companies from investments.json ───────────
    print("Normalizing companies from investments.json...")
    companies: dict[str, dict] = {}
    for name, data in investments.items():
        companies[name] = normalize_company(name, data)

    # ── Step 4: Merge startups ────────────────────────────────────────────────
    print("Merging startups.json...")
    startup_investors = merge_startups(companies, startups)

    # Assign roles to companies (done after merge so new startups also get it)
    for name, cdata in companies.items():
        if "roles" not in cdata:
            investor_type = cdata["sources"]["crunchbase"].get("investor_type", "")
            if investor_type == "Corporate Venture Capital":
                cdata["roles"] = ["manufacturer", "investor"]
            else:
                cdata["roles"] = ["manufacturer"]

    # ── Step 2: Sort alphabetically, assign IN-IDs ────────────────────────────
    sorted_company_names = sorted(companies.keys(), key=lambda n: n.lower())
    entity_id_map: dict[str, str] = {}
    for i, name in enumerate(sorted_company_names, start=1):
        entity_id_map[name] = f"IN-{i:04d}"

    # ── Step 5: Collect investors ─────────────────────────────────────────────
    print("Collecting investor names...")
    investor_lower_map = collect_all_investors(companies, startup_investors)

    # Sort alphabetically for ID assignment
    sorted_investor_lowers = sorted(investor_lower_map.keys())
    investor_id_map: dict[str, str] = {}  # lower_name → IV-ID
    for j, lower in enumerate(sorted_investor_lowers, start=1):
        investor_id_map[lower] = f"IV-{j:04d}"

    # ── Build investor entities ───────────────────────────────────────────────
    investor_entities = []
    for lower, canonical in sorted((k, v) for k, v in investor_lower_map.items()):
        iv_id = investor_id_map[lower]
        inv_type = classify_investor(canonical)
        investor_entities.append({
            "id": iv_id,
            "type": inv_type,
            "roles": ["investor"],
            "name": canonical,
            "sector": None,
            "wikidata_id": None,
            "sources": {
                "crunchbase": None,
                "infonodes": None,
                "wikidata": None,
            },
            "history": [{
                "date": TODAY,
                "source": "migration",
                "author": "migrate.py",
                "field": "*",
                "old": None,
                "new": None,
                "description": "Extracted from investor strings during migration",
            }],
            "validation": [],
            "tags": [],
        })

    # ── Step 6: Build relationships ───────────────────────────────────────────
    print("Building relationships...")
    relationships = []
    rel_counter = 1
    seen_rels: set[tuple] = set()

    def add_rel(source_iv_id: str, target_in_id: str, lead: bool, sources_list: list[str]):
        nonlocal rel_counter
        key = (source_iv_id, target_in_id)
        if key in seen_rels:
            return
        seen_rels.add(key)
        nonlocal relationships
        rel_id = f"REL-{rel_counter:04d}"
        rel_counter += 1
        relationships.append({
            "id": rel_id,
            "type": "investment",
            "source": source_iv_id,
            "target": target_in_id,
            "details": {"lead": lead},
            "sources": sources_list,
            "added_at": TODAY,
            "author": "migrate.py",
        })

    for company_name in sorted_company_names:
        cdata = companies[company_name]
        target_in = entity_id_map[company_name]

        top5 = split_csv(cdata.get("_top5", ""))
        lead_list = split_csv(cdata.get("_lead", ""))
        lead_lower = {n.lower() for n in lead_list}

        # From investments.json Top 5 Investors
        for inv_name in top5:
            lower = inv_name.lower()
            iv_id = investor_id_map.get(lower)
            if iv_id:
                is_lead = lower in lead_lower
                add_rel(iv_id, target_in, is_lead, ["crunchbase"])

        # Also add lead investors not in top 5
        for inv_name in lead_list:
            lower = inv_name.lower()
            iv_id = investor_id_map.get(lower)
            if iv_id:
                add_rel(iv_id, target_in, True, ["crunchbase"])

        # From startups.json investors list (more reliable is_lead)
        # Use company_name if in startup_investors, else try matching key
        startup_inv_list = startup_investors.get(company_name, [])
        for inv in startup_inv_list:
            inv_name = inv.get("name", "").strip()
            if not inv_name:
                continue
            lower = inv_name.lower()
            iv_id = investor_id_map.get(lower)
            if iv_id:
                # Override lead status from startups.json (more reliable)
                is_lead = inv.get("is_lead", False)
                key = (iv_id, target_in)
                if key in seen_rels:
                    # Update lead status: if startups says lead, override
                    for r in relationships:
                        if r["source"] == iv_id and r["target"] == target_in:
                            if is_lead:
                                r["details"]["lead"] = True
                            if "startups" not in r["sources"]:
                                r["sources"].append("startups")
                            break
                else:
                    add_rel(iv_id, target_in, is_lead, ["startups"])

    # ── Build company entities ────────────────────────────────────────────────
    company_entities = []
    for company_name in sorted_company_names:
        cdata = companies[company_name]
        in_id = entity_id_map[company_name]

        # Remove internal helpers
        cdata_clean = {k: v for k, v in cdata.items() if not k.startswith("_")}

        entity = {
            "id": in_id,
            "type": "company",
            "roles": cdata.get("roles", ["manufacturer"]),
            "name": cdata["name"],
            "sector": cdata.get("sector"),
            "wikidata_id": cdata.get("wikidata_id"),
            "sources": cdata["sources"],
            "history": cdata["history"],
            "validation": cdata["validation"],
            "tags": cdata.get("tags", []),
        }
        company_entities.append(entity)

    all_entities = company_entities + investor_entities

    # ── Step 8: Write output ──────────────────────────────────────────────────
    database = {
        "_schema": "2.0",
        "_updated": TODAY,
        "entities": all_entities,
        "relationships": relationships,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Migration complete.")
    print(f"  Entities (companies):  {len(company_entities)}")
    print(f"  Entities (investors):  {len(investor_entities)}")
    print(f"  Relationships:         {len(relationships)}")
    print(f"  Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
