# QID Lookup Process

How to safely assign Wikidata QIDs to company entities in the database.

Last run: 2026-04-12 — 455/1149 companies matched (39.6% coverage).

---

## Architecture: 3 phases

### Phase 1 — Wikidata Search API

**Script:** `scripts/search_missing_qids.py --search`

- Uses `wbsearchentities` REST API (1 call per entity, 1.5s delay)
- Filters results by: label match + description keyword lists (org/disqualify)
- Writes `data/qid_candidates.json` with `status=proposed` or `status=skipped`
- Saves checkpoint every 50 entries — safe to interrupt and resume
- **No writes to database.json**

### Phase 1b — SPARQL + Reconciliation fallback

**Script:** `scripts/sparql_search_qids.py`

Handles two categories of skipped entities:

**Label-mismatch entries** (skipped because Wikidata label ≠ search name):
- Uses Wikidata SPARQL endpoint with `rdfs:label` batch lookup (15 per request, 2s delay)
- Example: "Taiwan Semiconductor Manufacturing" → search finds "TSMC" (label mismatch) → SPARQL confirms QID Q713418
- Endpoint: `https://query.wikidata.org/sparql`

**No-results entries** (skipped because search API returned nothing):
- Uses Wikidata Reconciliation API with batch POST (20 queries per request, 2s delay)
- Handles fuzzy names, aliases, truncated strings, score threshold ≥ 60
- Endpoint: `https://wikidata-reconciliation.wmcloud.org/en/api`
- Note: avoid SPARQL `skos:altLabel` queries — too expensive, times out on public endpoint

Updates `qid_candidates.json` in-place. Never overwrites `accepted` or `rejected` entries.
**No writes to database.json.**

### Phase 2 — Human review + Apply

**Review:** Open `data/qid_candidates.json`, change each `"proposed"` entry to:
- `"accepted"` — correct match, ready to apply
- `"rejected"` — wrong match, discard

**Script:** `scripts/search_missing_qids.py --apply`

- Reads only entries with `status=accepted`
- Writes `wikidata_id` to each entity in `database.json`
- Appends `history[]` and `validation[]` entries per UPDATE_PROTOCOL.md
- **Zero API calls**

---

## How to re-run

```bash
# Step 1 — Search (resumes from checkpoint if qid_candidates.json exists)
python3 scripts/search_missing_qids.py --search

# Step 2 — SPARQL + Reconciliation fallback for skipped entries
python3 scripts/sparql_search_qids.py

# Step 2b — Second-pass recovery (run after step 2, before human review)
#   Fixes disqualify false positives, P856 website lookup, P31 type confirmation,
#   results[1-4] re-search. Safe to re-run.
python3 scripts/reprocess_skipped_qids.py

# Step 3 — Human review
# Open data/qid_candidates.json
# For each status=proposed entry: change to "accepted" or "rejected"

# Step 4 — Apply accepted entries to database
python3 scripts/search_missing_qids.py --apply

# Step 5 — Validate
python3 scripts/validate.py
```

---

## Safety guarantees

| Risk | Mitigation |
|---|---|
| False positives | Strict `label_matches()` + `description_is_org()` with org/disqualify keyword lists |
| HTTP 429 rate limiting | 1.5s delay (Phase 1), 2s delay (Phase 1b), exponential backoff [4, 8, 16]s on 429 |
| SPARQL timeouts | `rdfs:label` only (indexed) — never use `skos:altLabel` batch queries |
| Reconciliation ambiguity | Score threshold ≥ 60, additionally filtered by `description_is_org()` |
| DB corruption | Human review gate before any DB write; `validate.py` must pass after apply |

### Description keyword lists (in both scripts)

**Org keywords** (at least one required):
company, corporation, firm, enterprise, group, holding, manufacturer, producer,
supplier, mining, steel, metal, semiconductor, technology, aerospace, defence,
defense, telecommunications, telecom, pharmaceutical, bank, insurance,
conglomerate, industry, association, organization, agency, contractor,
consultancy, software, hardware, multinational, robotics, space, satellite,
aviation, shipbuilding, weapons, ammunition, electronics, chemicals, energy,
research, institute, laboratory, founded, headquartered, subsidiary, division

**Disqualify keywords** (none allowed):
city, town, village, municipality, commune, region, province, country, nation,
state, island, ocean, sea, lake, river, mountain, constellation, star, planet,
galaxy, person, individual, philosopher, politician, artist, musician, actor,
author, writer, scientist, athlete, album, song, film, movie, television,
article, journal, magazine, book, school, college, university, academic,
religion, disease, disorder, syndrome, medical, chemical element, fictional,
character, disambiguation

---

## Known limitations

- **~429 companies still without QID** after the 2026-04-12 second pass — mostly
  EDF SMEs and obscure mining companies genuinely absent from Wikidata, or with
  names too ambiguous to match safely. These require manual lookup.
- **iShares truncated names**: some names are cut at ~35 chars in the source CSV
  (e.g. "China Nonferrous Mining Corporatio") — impossible to match automatically.
- **Reconciliation API**: public endpoint, can be slow under load. Batch size 20
  and 2s delay is conservative but safe.
- **SPARQL altLabel**: avoid — too expensive on the public Wikidata endpoint, times
  out consistently for batches of company names.
- **P856 subsidiary matches**: the website reverse lookup sometimes returns a
  subsidiary instead of the parent company when both share the same official URL.
  Always verify the QID during human review.
- **`"group"` false positives**: descriptions like "lattice point group" or "hill
  group" pass the org filter due to the word "group". Flag and reject these during
  review.

---

## Results log

| Date | Phase 1 proposed | Phase 1b found | Total accepted | Applied | Coverage |
|---|---|---|---|---|---|
| 2026-04-12 | 245 | 80 (34 SPARQL + 46 reconciliation) | 309 | 309 | 455/1149 (39.6%) |
| 2026-04-12 | second pass via `reprocess_skipped_qids.py`: 53 (Phase A) + 132 (Phase B P856) + 60 (Phase C P31) + 20 (Phase D re-search) = **267 proposed** | — | pending review | pending | ~722/1149 if all accepted |
