#!/usr/bin/env python3
"""
patch_iv_countries_batch2.py — Curated country assignment for 382 no-QID IV entities.

Covers recognisable investors, government funds, banks, and VC firms
where country is unambiguous from public knowledge.
Entities that are ambiguous, person-named without known domicile,
or obscure are left for Crunchbase Cycle 2 or future review.

Usage:
    python3 scripts/patch_iv_countries_batch2.py [--dry-run]
"""

import json
import sys
from datetime import date

DRY_RUN = "--dry-run" in sys.argv
TODAY = date.today().isoformat()
DB_PATH = "data/database.json"

# (entity_id, country, note)
MANUAL = [
    # --- USA ---
    ("IV-0001", "United States", "137 Ventures — Menlo Park CA VC"),
    ("IV-0009", "United States", "Acorn Campus Ventures — Silicon Valley VC"),
    ("IV-0024", "United States", "Amazon — Seattle WA"),
    ("IV-0025", "United States", "Amplify Partners — San Francisco CA VC"),
    ("IV-0074", "United States", "Bill & Melinda Gates Foundation — Seattle WA"),
    ("IV-0087", "United States", "Breakthrough Energy Ventures — Kirkland WA; Gates-backed climate fund"),
    ("IV-0103", "United States", "Capstone Partners — Boston MA investment bank"),
    ("IV-0130", "United States", "Coinbase Ventures — San Francisco CA"),
    ("IV-0146", "United States", "CRV — San Francisco/Boston USA (formerly Charles River Ventures)"),
    ("IV-0156", "United States", "Deerfield — New York NY healthcare VC"),
    ("IV-0159", "United States", "Department of Defense's Office of Strategic Capital — Washington DC USA"),
    ("IV-0623", "United States", "Durable Capital Partners — Washington DC area USA"),
    ("IV-0179", "United States", "Emergence Capital — San Mateo CA enterprise SaaS VC"),
    ("IV-0181", "United States", "Endeavor Catalyst — New York NY"),
    ("IV-0218", "United States", "FirstMark — New York NY VC"),
    ("IV-0238", "United States", "Goldman Sachs Asset Management — New York NY"),
    ("IV-0242", "United States", "Government of United States of America — Washington DC"),
    ("IV-0235", "United States", "Globespan Capital Partners — Palo Alto CA VC"),
    ("IV-0271", "United States", "ICONIQ Growth — San Francisco CA family-office VC"),
    ("IV-0288", "United States", "Inherent Group — New York NY"),
    ("IV-0301", "United States", "InterWest Partners — Menlo Park CA VC"),
    ("IV-0287", "United States", "Inflection Point Acquisition Corp. III — USA SPAC"),
    ("IV-0311", "United States", "J.P. Morgan Securities Inc. — New York NY"),
    ("IV-0320", "United States", "JobsOhio — Columbus OH USA"),
    ("IV-0335", "United States", "Kindred Ventures — San Francisco CA VC"),
    ("IV-0339", "United States", "Koch — Wichita KS USA (Koch Industries)"),
    ("IV-0372", "United States", "MassMutual Ventures — Springfield MA USA"),
    ("IV-0394", "United States", "Morgenthaler Ventures — Menlo Park CA VC"),
    ("IV-0398", "United States", "NASA — Washington DC USA"),
    ("IV-0407", "United States", "Navajo Transitional Energy Company — Farmington NM USA"),
    ("IV-0637", "United States", "Omega Advisors — New York NY (Leon Cooperman)"),
    ("IV-0434", "United States", "Opportunity Now Colorado — Denver CO USA"),
    ("IV-0441", "United States", "Peninsula Capital — Detroit MI USA"),
    ("IV-0461", "United States", "Quiet Capital — San Francisco CA VC"),
    ("IV-0466", "United States", "Rev1 Ventures — Columbus OH USA"),
    ("IV-0467", "United States", "Ridge Ventures — San Francisco CA VC"),
    ("IV-0470", "United States", "Riot Ventures — Santa Monica CA VC"),
    ("IV-0472", "United States", "RiverPark Ventures — New York NY"),
    ("IV-0646", "United States", "Sands Capital Ventures — Arlington VA USA"),
    ("IV-0647", "United States", "Slate Path Capital — New York NY USA"),
    ("IV-0553", "United States", "The Baupost Group — Boston MA USA"),
    ("IV-0555", "United States", "The Carlyle Group — Washington DC USA"),
    ("IV-0559", "United States", "The TCW Group — Los Angeles CA USA"),
    ("IV-0561", "United States", "TIN Capital — USA"),
    ("IV-0660", "United States", "TriplePoint Capital — Menlo Park CA USA"),
    ("IV-0661", "United States", "True Ventures — San Francisco CA VC"),
    ("IV-0568", "United States", "U.S. Department of Energy Advanced Manufacturing Office — Washington DC"),
    ("IV-0569", "United States", "U.S. International Development Finance Corp — Washington DC"),
    ("IV-0575", "United States", "United States Advanced Battery Consortium — Southfield MI USA"),
    ("IV-0581", "United States", "US Army — Washington DC USA"),
    ("IV-0589", "United States", "Vanguard Ventures — Palo Alto CA VC"),
    ("IV-0597", "United States", "Washington State Investment Board — Olympia WA USA"),
    ("IV-0598", "United States", "Webb Investment Network — Menlo Park CA USA"),
    ("IV-0599", "United States", "Western Digital Capital — San Jose CA USA"),
    ("IV-0600", "United States", "William Ackman — New York NY (Pershing Square)"),
    ("IV-0602", "United States", "Wynnchurch Capital — Rosemont IL USA"),
    ("IV-0603", "United States", "Y Combinator — Mountain View CA USA"),
    ("IV-0243", "United States", "GQG — Fort Lauderdale FL USA (GQG Partners)"),
    ("IV-0282", "United States", "Independent Franchise Partners — actually UK; skip — reassigned below"),
    ("IV-0273", "United States", "iD Ventures America — USA"),
    ("IV-0664", "United States", "Ventura Capital — USA"),
    ("IV-0650", "United States", "Soma Capital — San Francisco CA USA"),

    # --- Canada ---
    ("IV-0076", "Canada",        "Birch Hill Equity Partners — Toronto ON Canada"),
    ("IV-0079", "Canada",        "BMO Capital Markets — Toronto ON Canada (Bank of Montreal)"),
    ("IV-0108", "Canada",        "Celtic House Venture Partners — Ottawa ON Canada"),
    ("IV-0098", "Canada",        "Canada Growth Fund Investment Management — Ottawa Canada"),
    ("IV-0099", "Canada",        "Canada's Ocean Supercluster — Halifax NS Canada"),
    ("IV-0240", "Canada",        "Government of Canada — Ottawa ON Canada"),
    ("IV-0230", "Canada",        "Georgian — Toronto ON Canada (Georgian Partners)"),
    ("IV-0430", "Canada",        "OMERS Private Equity — Toronto ON Canada"),
    ("IV-0433", "Canada",        "Ontario Municipal Employees Retirement System — Toronto ON Canada"),
    ("IV-0491", "Canada",        "Science and Economic Development Canada — Ottawa Canada"),
    ("IV-0531", "Canada",        "Stornoway Portfolio Management — Montreal QC Canada"),
    ("IV-0406", "Canada",        "Natural Resources Canada — Ottawa Canada (note: listed under IV separately from IV-0406 parent dept)"),

    # --- United Kingdom ---
    ("IV-0018", "United Kingdom", "Air Street Capital — London UK VC (Nathan Benaich)"),
    ("IV-0089", "United Kingdom", "Bridgepoint — London UK PE"),
    ("IV-0094", "United Kingdom", "C4 Ventures — London UK VC"),
    ("IV-0104", "United Kingdom", "Cardiff Capital Region — Cardiff Wales UK"),
    ("IV-0142", "United Kingdom", "Creator Fund — London UK VC"),
    ("IV-0189", "United Kingdom", "ETF Partners — London UK sustainability VC"),
    ("IV-0214", "United Kingdom", "Fidelity International — London UK (non-US arm of Fidelity)"),
    ("IV-0308", "United Kingdom", "IQ Capital — Cambridge UK deep-tech VC"),
    ("IV-0282", "United Kingdom", "Independent Franchise Partners — London UK"),
    ("IV-0648", "United Kingdom", "Solent Local Enterprise Partnership — Southampton UK"),
    ("IV-0601", "United Kingdom", "Witan Investment — London UK investment trust"),
    ("IV-0508", "United Kingdom", "Silicon Roundabout Ventures — London UK"),

    # --- France ---
    ("IV-0016", "France",        "AGORANOV — Paris France incubator"),
    ("IV-0047", "France",        "Axeleo Capital — Lyon France VC"),
    ("IV-0037", "France",        "Arts et Métiers Business Angels — Paris France"),
    ("IV-0039", "France",        "Atlas Investissement — France"),
    ("IV-0101", "France",        "Cap Innov'Est — Franche-Comté France"),
    ("IV-0148", "France",        "Crédit Mutuel Innovation — Strasbourg France"),
    ("IV-0176", "France",        "Elaia — Paris France VC"),
    ("IV-0211", "France",        "FaDièse — France"),
    ("IV-0224", "France",        "Franche-Comté PME Gestion — Besançon France"),
    ("IV-0225", "France",        "Frst — Paris France seed VC"),
    ("IV-0281", "France",        "Incubateur Impulse — France"),
    ("IV-0280", "France",        "IncubAlliance Paris-Saclay — Orsay France"),
    ("IV-0309", "France",        "Isai — Paris France VC"),
    ("IV-0327", "France",        "Karista — Paris France VC"),
    ("IV-0403", "France",        "Natixis Corporate & Investment Banking — Paris France"),
    ("IV-0453", "France",        "Proparco — Paris France development finance"),
    ("IV-0469", "France",        "Ring Capital — Paris France VC"),
    ("IV-0510", "France",        "Siparex Groupe — Lyon France PE"),
    ("IV-0514", "France",        "Sofimac Innovation — Clermont-Ferrand France"),
    ("IV-0591", "France",        "Ventech — Paris France VC"),
    ("IV-0629", "France",        "Groupe Arnault — Paris France (LVMH / Arnault family office)"),

    # --- Germany ---
    ("IV-0060", "Germany",       "Bayern Innovativ Project — Munich Bavaria Germany"),
    ("IV-0267", "Germany",       "IBB Ventures — Berlin Germany"),
    ("IV-0332", "Germany",       "KfW IPEX Bank — Frankfurt Germany (KfW development bank arm)"),
    ("IV-0446", "Germany",       "Planet A Ventures — Berlin Germany climate VC"),
    ("IV-0452", "Germany",       "Project A Ventures — Berlin Germany VC"),

    # --- China ---
    ("IV-0113", "China",         "Changzhou Gaoxin Tou — Changzhou Jiangsu China"),
    ("IV-0115", "China",         "China Equity — China state investment arm"),
    ("IV-0116", "China",         "China Structural Reform Fund — Beijing China"),
    ("IV-0117", "China",         "Chongqing Rural Commercial Bank — Chongqing China"),
    ("IV-0120", "China",         "CID Group — Shenzhen China tech investor"),
    ("IV-0171", "China",         "EFung Capital — China"),
    ("IV-0250", "China",         "Guosheng Group — Shanghai China state enterprise"),
    ("IV-0251", "China",         "Guotai Junan Financial Holdings — Shanghai China"),
    ("IV-0255", "China",         "Harbin Venture Capital — Harbin Heilongjiang China"),
    ("IV-0259", "China",         "Houji Capital — China"),
    ("IV-0317", "China",         "Jinniu City Investment — Chengdu Sichuan China"),
    ("IV-0342", "China",         "KPCB China — Shanghai China (Kleiner Perkins China affiliate)"),
    ("IV-0358", "China",         "Longjiang Fund — Heilongjiang China"),
    ("IV-0359", "China",         "Longpan Investment — China"),
    ("IV-0374", "China",         "Matrix Partners China — Shanghai China"),
    ("IV-0422", "China",         "Nuode Asset Management — China"),
    ("IV-0494", "China",         "SDIC Unity Capital — Beijing China (State Dev. & Investment Corp.)"),
    ("IV-0551", "China",         "Tencent Music Entertainment — Shenzhen China"),
    ("IV-0565", "China",         "Tsinghua Unisplendour Venture Capital — Beijing China"),
    ("IV-0608", "China",         "Zhonghe Capital — China"),

    # --- South Korea ---
    ("IV-0277", "South Korea",   "IMM Private Equity — Seoul South Korea"),
    ("IV-0341", "South Korea",   "Korea Venture Investment Corp — Seoul South Korea"),
    ("IV-0557", "South Korea",   "The Export-Import Bank of Korea — Seoul South Korea"),

    # --- Japan ---
    ("IV-0293", "Japan",         "Innovation Network Corporation of Japan — Tokyo Japan"),
    ("IV-0388", "Japan",         "Mitsubishi UFJ Capital — Tokyo Japan"),
    ("IV-0389", "Japan",         "Mitsui & Co — Tokyo Japan"),
    ("IV-0412", "Japan",         "Nikon — Tokyo Japan"),
    ("IV-0537", "Japan",         "SunBridge — Tokyo Japan (SunBridge Global Ventures)"),

    # --- Norway ---
    ("IV-0294", "Norway",        "Innovation Norway — Oslo Norway"),
    ("IV-0420", "Norway",        "Norwegian Research Council — Oslo Norway"),
    ("IV-0421", "Norway",        "NRP Zero AS — Norway"),
    ("IV-0425", "Norway",        "Nysnø — Stavanger Norway climate VC"),

    # --- Sweden ---
    ("IV-0285", "Sweden",        "Industrifonden — Stockholm Sweden"),
    ("IV-0417", "Sweden",        "Norrland Fund — Sweden (Norrland is a Swedish region)"),
    ("IV-0511", "Sweden",        "SNÖ Ventures — Stockholm Sweden"),
    # IV-0498 SEK: QID nulled (was Finnish ad agency false positive), country set to Sweden separately

    # --- Finland ---
    ("IV-0352", "Finland",       "Lifeline Ventures — Helsinki Finland"),

    # --- Spain ---
    ("IV-0007", "Spain",         "Aciturri — Miranda de Ebro Spain aerospace"),
    ("IV-0091", "Spain",         "Bullnet Capital — Madrid Spain VC"),
    ("IV-0110", "Spain",         "Centre for the Development of Industrial Technology (CDTI) — Madrid Spain"),
    ("IV-0106", "Spain",         "CDTI Innovación's INNVIERTE program — Madrid Spain"),
    ("IV-0236", "Spain",         "GoHub Ventures — Valencia Spain VC"),
    ("IV-0268", "Spain",         "Iberis Capital — Madrid Spain VC"),
    ("IV-0346", "Spain",         "Leadwind — Madrid Spain VC"),

    # --- Italy ---
    ("IV-0522", "Italy",         "Star Capital SGR — Milan Italy"),
    ("IV-0579", "Italy",         "United Ventures — Milan Italy VC"),

    # --- Belgium ---
    ("IV-0232", "Belgium",       "Gimv — Antwerp Belgium VC/PE"),

    # --- Netherlands ---
    ("IV-0289", "Netherlands",   "Inkef — Amsterdam Netherlands (ex-ING Ventures)"),
    ("IV-0204", "Netherlands",   "EXOR N.V. — Amsterdam Netherlands (Agnelli family office, incorporated in NL)"),

    # --- Portugal ---
    ("IV-0035", "Portugal",      "Armilar Venture Partners — Lisbon Portugal"),

    # --- Ireland ---
    ("IV-0038", "Ireland",       "Atlantic Bridge — Dublin Ireland VC"),

    # --- Israel ---
    ("IV-0042", "Israel",        "Auriga Cyber Ventures — Tel Aviv Israel"),

    # --- Australia ---
    ("IV-0093", "Australia",     "Business.gov.au — Canberra Australia"),
    ("IV-0400", "Australia",     "National Reconstruction Fund Corporation — Canberra Australia"),
    ("IV-0401", "Australia",     "National Security Strategic Investment Fund — Canberra Australia"),

    # --- Saudi Arabia ---
    ("IV-0377", "Saudi Arabia",  "Ma'aden — Riyadh Saudi Arabia (Saudi Arabian Mining Company)"),
    ("IV-0485", "Saudi Arabia",  "Saudi EXIM — Riyadh Saudi Arabia"),

    # --- Brazil ---
    ("IV-0056", "Brazil",        "Banco do Brasil — Brasília Brazil"),
    ("IV-0139", "Brazil",        "Cosan — São Paulo Brazil"),

    # --- Denmark ---
    ("IV-0584", "Denmark",       "Vaekstfonden — Copenhagen Denmark (Danish Growth Fund)"),

    # --- Estonia ---
    ("IV-0328", "Estonia",       "Karma Ventures — Tallinn Estonia VC"),

    # --- Lithuania ---
    ("IV-0112", "Lithuania",     "Change Ventures — Vilnius Lithuania VC"),

    # --- Latvia ---
    ("IV-0303", "Finland",       "Inventure — Helsinki Finland VC"),  # correction: Inventure is Finnish

    # --- NATO/Intergovernmental ---
    ("IV-0558", "Belgium",       "The North Atlantic Treaty Organization — Brussels Belgium (HQ)"),
]

# Deduplicate: if same entity_id appears twice, last wins (handles the correction above)
seen = {}
for entry in MANUAL:
    seen[entry[0]] = entry
MANUAL = list(seen.values())

with open(DB_PATH) as f:
    db = json.load(f)

id_map = {e["id"]: e for e in db["entities"]}

def get_country(e):
    return (e["sources"].get("infonodes") or {}).get("country") or \
           (e["sources"].get("wikidata") or {}).get("country")

patched = 0
skipped = 0

for eid, country, note in sorted(MANUAL, key=lambda x: x[0]):
    e = id_map.get(eid)
    if e is None:
        print(f"WARN: {eid} not found in DB")
        skipped += 1
        continue

    existing = get_country(e)
    if existing:
        print(f"SKIP: {eid} {e['name']} — already has country={existing}")
        skipped += 1
        continue

    if DRY_RUN:
        print(f"  [DRY] {eid}  {e['name']} → {country}")
    else:
        if "infonodes" not in e["sources"]:
            e["sources"]["infonodes"] = {}
        e["sources"]["infonodes"]["country"] = country
        e["history"].append({
            "date": TODAY,
            "source": "infonodes",
            "author": "patch_iv_countries_batch2.py",
            "field": "sources.infonodes.country",
            "old": None,
            "new": country,
            "description": f"Country curated: {note}",
        })
        print(f"  ✓ {eid}  {e['name']} → {country}")
    patched += 1

if not DRY_RUN:
    db["_updated"] = TODAY
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"\nPatched: {patched}, skipped: {skipped}. Run validate.py to confirm.")
else:
    print(f"\n[DRY-RUN] {patched} would be patched, {skipped} skipped.")
