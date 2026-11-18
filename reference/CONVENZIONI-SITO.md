# Convenzioni del sito e decisioni chiave

> Spostato da `STATUS.md` (stato `4c437bf`), testo invariato. Non è un punto di ripartenza: le informazioni qui possono essere datate. Prima di fidarsi di un numero o di un percorso, rimisurare.

## Routing convention (all pages)

> Rule: **every user-driven state change uses `pushState`; initial page load uses `replaceState`.**

| Action | Method | Reason |
|---|---|---|
| User changes any filter or selection | `pushState` | Back must always restore the previous state |
| Page load / URL canonicalization | `replaceState` | Avoids a duplicate history entry on first load |

**Do not use `replaceState` for user interactions**, even if the change feels like a "view setting". The browser Back button is the user's primary undo mechanism — any state that can be set by the user must be undoable.

### Implementation per page

| Page | Routing module | URL scheme |
|---|---|---|
| `docs/search.html` | `docs/web/router.js` (ES module) | `?organization=IN-XXXX&organizationName=Name[&theme=light]` |
| `docs/index.html` | Inline | `?country=840&countryname=United+States&entity=IN-XXXX&entityname=Name&type=EUfunded[&theme=light]` |
| `docs/networks.html` | Inline | `?country=France&edf=1&inv=1[&selected=EDF-0001&selectedName=ENGRT+II][&theme=light]` |

**Theme param (2026-05-11):** `theme=light` added to all pages. Dark is default (no param). Managed by `docs/web/theme.js`:
- `initTheme()`: reads URL param > localStorage > dark; `replaceState` to canonicalize
- `toggleTheme()`: `pushState` with updated param (back button undoes theme change)
- `popstate` listener: applies theme from URL on back/forward
- `updateNavLinks()`: keeps all `a.tnav-btn` and `a.brand` hrefs in sync
- `themeParam()`: returns `&theme=light` or `''` — used in dynamic cross-page link builders
- FOUC prevention: all 3 pages read URL param before DOMContentLoaded (inline `<script>` in `<head>`)

**`docs/web/router.js`** handles entity-based routing (registry lookup, compare mode). Map and Networks use inline routing because their state models (filter params) are incompatible with the entity-registry API. **Do not merge them** — the schemas are structurally different. The shared rule is the `pushState`/`replaceState` convention above.


---

## Key decisions (do not revisit without strong reason)

| Decision | Rationale |
|---|---|
| `wikidata_id` as primary bridge identifier across sources | Entity resolution: same company appears as "Leonardo" / "Leonardo SPA" / "Leonardo Società per azioni" |
| Deduplication by `name_key` (strip legal suffixes, uppercase, collapse whitespace) | Prevents duplicate entities from same company listed on different exchanges |
| EDF matching: conservative (2 auto-matched, 792 new entities) | False positives in entity matching must not happen |
| `sources.ishares` is array, not object | Same company can appear in multiple ETFs |
| ISIN not used | iShares CSVs do not contain ISIN column |
| QID false positives: must never happen | Strict label + description keyword filtering enforced in all search scripts |
| HTTP 429: must never happen | 1.5s delay (Phase 1), 2s delay (Phase 1b), backoff [4, 8, 16]s |
| SPARQL `skos:altLabel` batch queries: avoided | Too expensive on public endpoint, consistently times out |
| Disqualify keywords: word-boundary for `nation/state/sea/actor/region` | Substring match causes false positives (`"multinational"` → disqualified by `"nation"`) |
| `"video game"` removed from disqualify list | "video game **company**" is a valid org type; EA/Konami/Take-Two all have "company" in description |
| P856 SPARQL batch size: 10 entities (≤80 URL variants) | Larger batches cause HTTP 414/431 on Wikidata SPARQL endpoint |
| P856 false positives: accepted as review items | URL match is high-precision but some subsidiaries share parent's website; human reviewer corrects QID |
| `Taiwan` mapped to ISO 158 in `WD_TO_ISO` | Taiwan appears as Wikidata `P17` country for TSMC and others; ISO 158 is the standard numeric code (ISO 3166-1). Deliberate inclusion despite geopolitical ambiguity — data reflects Wikidata, not a political stance. |
| `'Internationality'` not mapped in `WD_TO_ISO` | Wikidata assigns `P17 = 'Internationality'` to supranational entities (EU, UN, etc.) — not a country, has no geographic coordinates. Mapping it to a proxy country (e.g. Belgium) would misrepresent the arc origin. Excluded: EU-as-investor arcs do not appear on the map. |
| SEC `ownership` shown in two own cards ("Shareholders ≥5% (SEC)", "Holdings ≥5% (SEC)"), not in the map, not in the networks, not in the investment Portfolio; `role` and `parte_di` not shown yet (decision of Nelson, 2026-11-17) | Otherwise every relation other than `edf_participation` reads as an investment (BlackRock would have 148 connections instead of 4). `NEW_REL_TYPES` in `index.html`, `GRAPH_ROLES` in `app.js`; `networks.html` and `key-figures.html` filter by type and need no change |
| `PER-` entities are not in the search registry and not counted as organisations; persons appear only as names in the SEC cards (decision of Nelson, 2026-11-17) | Persons are not organisations; a link to `PER-` opens an empty search without errors |
| The 93 new `IV-` managers are searchable and counted as investors; new cards are in English, translations pending (`ROADMAP.md` item 19) (decision of Nelson, 2026-11-17) | Same treatment as the other `IV-` entities; translating would block the data PR |
| The chatbot index (`docs/data/mitl-index.json`) is not regenerated with the SEC data (decision of Nelson, 2026-11-17) | The people who run MARLA must be told first; `build_chat_index.py` exports every relation as `{da, a, tipo}`, so the new types would appear |
