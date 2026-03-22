# AI Instructions for Manintheloop Project

## 1. Source of Truth
- The primary data source is the Google Sheet accessible as CSV here:
  `https://docs.google.com/spreadsheets/d/e/2PACX-1vSg4v9OkP8ZAmUQ_AOukHt8-_jjoiZR62_aeIvay9SqLv6GVxgnZbzT9hckXN0lq8WyHcxZ3smmGvsI/pub?gid=766453961&single=true&output=csv`
- The local file `data/companies.csv` must be an up-to-date copy of this URL.
- The file `data/companies.json` is a **derived and protected artifact**.

## 2. Operational Workflow
When started, the AI agent must follow this sequence:

1.  **Fetch:** Download the latest data from the Sheet URL and save it to `data/companies.csv`.
2.  **Check Uniqueness:** Run the sync ensuring each company appears exactly once in the JSON (uniquely identified by its Wikidata ID).
3.  **Store & Merge:** Update `data/companies.json` preserving already-validated Wikidata IDs and adding new entries from the CSV.
4.  **Enrichment (Wikidata ID):** For companies that have NO ID in the CSV or JSON, run the automatic Wikidata search.
5.  **Enrichment (Country):** Retrieve the official country from Wikidata for all companies (standardisation).
6.  **Alphabetical Sort:** Save the final JSON sorted by `label` A-Z.

## 3. Safety and Integrity Rules
- **ID Protection:** NEVER overwrite an existing Wikidata ID in the JSON with a new automatically-found one, unless explicitly corrected in the CSV.
- **Cross-Validation:** If a company's name in the CSV differs greatly from the Label found on Wikidata for the associated ID, flag the anomaly.
- **App Output:** The resulting JSON must be ready for the SPARQL queries executed by `index.html`.

## 4. Scripts to Use
- `python3 scripts/sync_anagrafica.py`: Runs fetch (optional), merge, uniqueness check, country enrichment and sort.
- `python3 scripts/verify_data_integrity.py`: Verifies that IDs in the JSON actually correspond to the indicated companies.
- `python3 scripts/extract_company_data.py`: SPARQL extraction test for a single company.
