#!/usr/bin/env python3
"""
patch_investor_countries.py — Assign known countries to well-known IV-* investors.

For the top-frequency investors whose country is unambiguous (major banks,
EU/US institutions, well-known VC firms), this avoids the 600+ Wikidata SPARQL
queries by using a curated lookup table. The result is stored as
sources.infonodes.country so the map arc logic picks it up immediately.

Run after import_investors_crunchbase.py:
  python3 scripts/patch_investor_countries.py [--dry-run]
"""

import json, os, sys
from datetime import date

BASE          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE, "data", "database.json")
TODAY         = date.today().isoformat()
DRY_RUN       = "--dry-run" in sys.argv

# name (exact, case-sensitive) → country string matching WD_TO_ISO keys in index.html
KNOWN = {
    # EU / European institutions
    "European Investment Bank":     "Luxembourg",
    "European Innovation Council":  "Belgium",
    "European Commission":          "Belgium",
    "EISMEA":                       "Belgium",
    "Nordic Investment Bank":       "Finland",
    "NATO DIANA":                   "United Kingdom",
    "Bpifrance":                    "France",
    "HTGF (High-Tech Gruenderfonds)": "Germany",
    "KfW":                          "Germany",
    "KfW Capital":                  "Germany",
    "EIC Fund":                     "Belgium",
    "EIC Accelerator":              "Belgium",
    "Invest-NL":                    "Netherlands",
    "Innovate UK":                  "United Kingdom",
    "British Business Bank":        "United Kingdom",
    "Scottish Enterprise":          "United Kingdom",
    "Business Finland":             "Finland",
    "Vinnova":                      "Sweden",
    "Innovation Fund Denmark":      "Denmark",
    "Wallonie Entreprendre":        "Belgium",
    "SRIW":                         "Belgium",
    "Seventure Partners":           "France",
    "Eurazeo":                      "France",
    "Societe Generale":             "France",
    "Société Générale":             "France",
    "BNP Paribas":                  "France",
    "AXA":                          "France",
    "Credit Agricole":              "France",
    "Crédit Agricole":              "France",
    "Deutsche Bank":                "Germany",
    "Commerzbank":                  "Germany",
    "Munich Re Ventures":           "Germany",
    "Allianz":                      "Germany",
    "Siemens":                      "Germany",
    "Bosch":                        "Germany",
    "Airbus Ventures":              "France",
    "Leonardo":                     "Italy",
    "Intesa Sanpaolo":              "Italy",
    "UniCredit":                    "Italy",
    "CDP Venture Capital":          "Italy",
    "Cassa Depositi e Prestiti":    "Italy",
    "Finindus":                     "Belgium",
    "SFPI":                         "Belgium",
    "MUFG Bank":                    "Japan",
    "Sumitomo Mitsui":              "Japan",
    "SoftBank":                     "Japan",
    "HSBC":                         "United Kingdom",
    "Barclays":                     "United Kingdom",
    "Lloyds":                       "United Kingdom",
    "NatWest":                      "United Kingdom",
    "Standard Chartered":           "United Kingdom",
    "Arm":                          "United Kingdom",
    "KB Securities":                "South Korea",
    "Samsung Ventures":             "South Korea",
    "SK Group":                     "South Korea",
    # US institutions
    "US Department of Energy":              "USA",
    "U.S. Department of Energy":            "USA",
    "U.S. Department of Defense":           "USA",
    "U.S. Department of Commerce":          "USA",
    "US Department of Defense":             "USA",
    "DARPA":                                "USA",
    "In-Q-Tel":                             "USA",
    "NYSERDA":                              "USA",
    "Export-Import Bank of the United States": "USA",
    "Biomedical Advanced Research and Development Authority (BARDA)": "USA",
    "National Science Foundation":          "USA",
    # US VC / banks
    "Sequoia Capital":              "USA",
    "Andreessen Horowitz":          "USA",
    "a16z":                         "USA",
    "Accel":                        "USA",
    "Greylock":                     "USA",
    "Bessemer Venture Partners":    "USA",
    "Kleiner Perkins":              "USA",
    "General Catalyst":             "USA",
    "Lightspeed Venture Partners":  "USA",
    "IVP":                          "USA",
    "New Enterprise Associates":    "USA",
    "NEA":                          "USA",
    "Founders Fund":                "USA",
    "Tiger Global Management":      "USA",
    "Coatue Management":            "USA",
    "Greenoaks":                    "USA",
    "BDT & MSD Partners":           "USA",
    "Kohlberg Kravis Roberts & Co.": "USA",
    "KKR":                          "USA",
    "Goldman Sachs":                "USA",
    "Morgan Stanley":               "USA",
    "JPMorgan":                     "USA",
    "Bank of America":              "USA",
    "Citibank":                     "USA",
    "BlackRock":                    "USA",
    "Vanguard":                     "USA",
    "Fidelity":                     "USA",
    "T. Rowe Price":                "USA",
    "Elliott Management Corp.":     "USA",
    "Third Point":                  "USA",
    "Insight Partners":             "USA",
    "Salesforce Ventures":          "USA",
    "Microsoft":                    "USA",
    "Google Ventures":              "USA",
    "GV":                           "USA",
    "Intel Capital":                "USA",
    "Qualcomm Ventures":            "USA",
    "Lockheed Martin Ventures":     "USA",
    "Boeing HorizonX":              "USA",
    "Raytheon":                     "USA",
    "L3Harris":                     "USA",
    "General Dynamics":             "USA",
    "Northrop Grumman":             "USA",
    "Palantir":                     "USA",
    "Export Development Canada":    "Canada",
    "BDC Capital":                  "Canada",
    "Export Finance Australia":     "Australia",
    # UK
    "Seraphim Space":               "United Kingdom",
    "Standard Chartered Bank":      "United Kingdom",
    "Advanced Propulsion Centre UK":"United Kingdom",
    "UK Government":                "United Kingdom",
    "Department for Science":       "United Kingdom",
    "Innovate UK":                  "United Kingdom",
    # France
    "Kima Ventures":                "France",
    "Starburst Accelerator":        "France",
    "Supernova Invest":             "France",
    "Credit Agricole CIB":          "France",
    "Idinvest Partners":            "France",
    # Germany
    "Bayern Kapital":               "Germany",
    "HV Capital":                   "Germany",
    "Join Capital":                 "Germany",
    "HTGF":                         "Germany",
    "Mercedes-Benz Group AG":       "Germany",
    # USA — banks/finance
    "JP Morgan":                    "USA",
    "JP Morgan Chase":              "USA",
    "JPMorgan Chase & Co.":         "USA",
    "Citi":                         "USA",
    "Citigroup":                    "USA",
    "Wells Fargo":                  "USA",
    "Truist":                       "USA",
    # USA — VC / PE
    "ARK Investment Management":    "USA",
    "Redpoint":                     "USA",
    "Silver Lake":                  "USA",
    "Apollo":                       "USA",
    "Blackstone Group":             "USA",
    "TCV":                          "USA",
    "Third Point":                  "USA",
    "Valor Equity Partners":        "USA",
    "Matrix":                       "USA",
    "Dolby Family Ventures":        "USA",
    "Felicis":                      "USA",
    "Enova":                        "USA",
    "HCVC":                         "USA",
    "Starburst Accelerator":        "France",
    # USA — tech / corporate
    "NVIDIA":                       "USA",
    "Apple":                        "USA",
    # USA — gov / public
    "California Energy Commission": "USA",
    "Massachusetts Clean Energy Center": "USA",
    # Canada
    "CIBC":                         "Canada",
    "CPP Investments":              "Canada",
    "Agnico-Eagle Mines Limited":   "Canada",
    "Canaccord Genuity Group":      "Canada",
    "La Caisse":                    "Canada",
    "Canadian Government":          "Canada",
    "Transition énergétique Québec":"Canada",
    # Other
    "African Equity Empowerment Investments (AEEI)": "South Africa",
    "Absa":                         "South Africa",
    "K Fund":                       "Spain",
    "Legend Capital":               "China",
    "Ma'aden":                      "Saudi Arabia",
    "Mirae Asset":                  "South Korea",
    "Riksgälden":                   "Sweden",
    "Startmate":                    "Australia",
    "Technology Venture Investors": "Australia",
    "The Brazilian Development Bank(BNDES)": "Brazil",
    "NATO Innovation Fund":         "Belgium",
    "EUDIS Business Accelerator":   "Belgium",
    "Europe's Just Transition Fund":"Belgium",
    "Industrial and Commercial Bank of China": "China",
    "China Merchants Bank":         "China",
    "Toyota Motor":                 "Japan",
    "Solidium":                     "Finland",
    "Banco Santander-Chile":        "Chile",
}


def main():
    with open(DATABASE_PATH, encoding="utf-8") as f:
        db = json.load(f)

    patched = 0
    for e in db["entities"]:
        if not e["id"].startswith("IV-"):
            continue
        country = KNOWN.get(e["name"])
        if not country:
            continue
        src = e.setdefault("sources", {}).setdefault("infonodes", {})
        if src.get("country") == country:
            continue  # already set
        old = src.get("country")
        src["country"] = country
        e.setdefault("history", []).append({
            "date":        TODAY,
            "source":      "infonodes",
            "author":      "patch_investor_countries.py",
            "field":       "sources.infonodes.country",
            "old":         old,
            "new":         country,
            "description": "Country assigned from curated known-investor lookup table",
        })
        patched += 1
        print(f"  {e['id']}  {e['name']!r:45s} → {country}")

    print(f"\nPatched: {patched} investors")

    if DRY_RUN:
        print("[DRY RUN] No changes written.")
        return

    db["_updated"] = TODAY
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("DB updated.")


if __name__ == "__main__":
    main()
