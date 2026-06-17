# Last Updates - Wikidata Inspector

### 1. New Data Management
*   **Remote Source**: The project now uses the CSV published via Google Sheets (gid=766453961) as the "source of truth".
*   **Local Mirror (`data/companies.csv`)**: Downloaded and updated locally during enrichment.
*   **App Dataset (`data/companies.json`)**: Expanded to **111 verified companies** (up from the initial 55).

### 2. Enrichment Script (`enrich_data.py`)
Created a script for retrieving and validating missing Wikidata IDs:
*   **Semantic Validation**: Verifies via the Wikidata API that the entity is an **instance of a company** (property `P31` = *business enterprise*, *public company*, etc.).
*   **Anti-False Positives**: Prevents incorrect association of company names to countries (e.g. Czechoslovakia), people, or fruits (e.g. Apple).
*   **Special Case Handling**: Manual mapping added for ambiguous entities (e.g. *Czechoslovak Group* -> `Q27350567`).

### 3. Backend Proxy Update (`proxy.js`)
*   **Dynamic CORS**: The proxy now accepts requests from any port on `localhost`, eliminating blocks during local development.
*   **Logging**: Improved error diagnostics (500, Rate Limiting) with detailed terminal logs.

### 4. Update Workflow
The new command to sync and enrich data from the cloud is:
```bash
python3 enrich_data.py
```
This automates the cycle: **Download → ID Search → "Instance of" Verification → JSON Generation.**

### 5. Dataset Alignment Fix
Fixed an ID "drift" issue in the original dataset, restoring the correct association between company names and their respective Wikidata codes (e.g. fix for Nvidia, Microsoft, Apple).
