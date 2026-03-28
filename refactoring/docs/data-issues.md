# Known Issues

_Permanent data limitations and unresolvable gaps. Issues moved here from `issues.md` when they cannot be fixed without external data changes (e.g. Wikidata coverage improving). Each entry here must also have a dated record in `CHANGELOG.md`._

---

## #1 EDF — Count Mismatch

**Status:** To be verified

In European Defence Fund overview, calls with projects are **63**.
In EDF Call Search, calls with projects are **64**.

To be verified.

---

## #2 EDF — Total Allocated Budget (partial coverage)

**Status:** Known limitation

The "Total Allocated Budget" stat (€5.07B) reflects only the **120 out of 201 calls** that have budget data populated in the source (`budgetTopicActionMap`). The remaining 81 calls have no budget field in the dataset.

The official EDF programme envelope for 2021–2027 is ~**€7.95B** (€5.3B development + €2.65B research). The displayed figure is consistent with partial coverage, not a calculation error.

---

## #4 Companies — Missing Wikidata IDs (18/165)

**Status:** Known limitation

18 companies have `wikidata_id: null`. All were re-searched on 2026-03-22 via SPARQL + Playwright with no confident match found. Most are either too new, too small, or too regionally niche to have a Wikidata entry:

ARX Robotics, Advanced Middle East Systems (AMES), Alcoa Warrick (US subsidiary), Alpine Eagle, Alta Ares, Arondite, C2Grid, Comand AI, Comec, Delian Alliance Industries, Intelic, Nordic Air Defence, Origin Robotics, Patricomp Oy, Roark Aerospace, Sigma Lithium (publicly listed but absent), Unmanned Defense Systems, XRF.ai.

---

## #5 Investors — Missing Wikidata IDs (105/242)

**Status:** Known limitation

105 out of 242 investor entities have no `wikidata_id`. These fall into categories that are unlikely to be resolved without manual research:

- **Niche VC funds** with no Wikidata entry (Air Street Capital, Akkadian Ventures, BSV Ventures, Coinvest Capital, Creator Fund, GoHub Ventures, HCVC, Iberis Capital, JME Ventures, K Fund, Keen Venture Partners, Marathon Venture Capital, Nebular, Robin Capital, Sahsen Ventures, Shape VC, Silicon Roundabout Ventures, SNÖ Ventures, Soma Capital, Speedinvest, Startmate, Sunfish Partners, TA Ventures, T.Capital, True Ventures, Ventura Capital, Valor Equity Partners, and others)
- **Individual angel investors** (Chris Adelsbach, Gustav Wiberg, Gytenis Galkis, Martynas Kandzeras, Mike Oliinyk, Noam Perski, Rita Sakus, Vladas Lašas)
- **Ambiguous single-word names** with no unambiguous Wikidata match (Bond, ESG, Inc, Matrix, REV, Third Point, JARE, Enova)
- **Entities where search returned wrong/partial matches** — e.g. "Santander" returns Santander Consumer Bank (Germany), not the Santander Group; "Guotai Junan" returns only subsidiaries
- **Government/institutional entities** with no direct Wikidata hit (Department of Defense's Office of Strategic Capital, NATO DIANA, NATO Innovation Fund, National Security Strategic Investment Fund, Transition énergétique Québec, Business.gov.au, Solent Local Enterprise Partnership)

6 investors were resolved on 2026-03-22 via SPARQL + Playwright search (see `CHANGELOG.md`).

---

## #6 EDF — Officina Stellare SPA budget discrepancy

**Status:** Known data gap — moved from sirogja-issues.md #9 (2026-03-24)

Filtering for Italy → Officina Stellare SPA in EDF Map shows ~€2M, while the EU portal shows €1.5M EU contribution for the same entity. The discrepancy likely stems from one of:

- (a) summing EU contribution across multiple participations in the same project (duplicate counting)
- (b) confusion between total project budget and individual EU contribution
- (c) an error in the upstream source data

Cannot be resolved without a full audit of `edf_calls.json` against the EU Funding & Tenders portal. Until then, treat individual org budget figures in EDF Map as indicative, not authoritative.

---

## #7 EDF — Projects with zero budgets (post-2024)

**Status:** Known data gap — moved from sirogja-issues.md #10 (2026-03-24)

Some organisations (e.g. Istituto Superiore di Sanità in the "Resilience" project, start date 2024) appear with all budget fields at zero. This is a known upstream data gap: the EU Funding & Tenders portal sometimes publishes project entries before financial data is finalised. Budget figures for projects starting 2024 or later should be treated as provisional.

---

## #9 Companies — Inconsistent country name values in database

**Status:** Known data quality issue

Company country fields (`sources.wikidata.country`, `sources.infonodes.country`) use inconsistent naming across records — mixing English, Italian, and abbreviated forms for the same country:

| Stored value | Canonical name |
|---|---|
| `Cina`, `People's Republic of China` | China |
| `USA` | United States |
| `Giappone` | Japan |
| `EAU (Dubai)` | United Arab Emirates |
| `Polonia` | Poland |
| `Francia` | France |
| `Norvegia` | Norway |
| `Belgio` | Belgium |
| `Germania` | Germany |
| `Cile` | Chile |
| `UK` | United Kingdom |

These aliases are currently normalised client-side in `js/tabs/overview.js` (`COUNTRY_NORM` map) for the geographic distribution chart. The underlying `database.json` records retain the original values.

**Resolution path:** Standardise all country values to English common names during the next data reconciliation pass using `scripts/validate.py` or a dedicated migration script. Until then, any new chart or filter that groups by country must apply the same normalisation.

**Partially resolved (2026-03-28):** All single-country aliases above were normalised directly in `database.json` with history entries. The following multi-country and ambiguous values were skipped and remain open:

| Stored value | Entity | Notes |
|---|---|---|
| `Australia / UK` | TBD | Dual-country — primary country unclear |
| `UK/Spagna` | TBD | Dual-country — primary country unclear |
| `USA / Mexico` | TBD | Dual-country — primary country unclear |
| `internationality` | TBD | Non-standard value — needs canonical form |

Also add: `Czech Rep.` → `Czech Republic` was normalised; `UK` → `United Kingdom` was normalised.

---

## #8 Automated Investigation — Cyrillic text artefact

**Status:** Known content issue — moved from sirogja-issues.md #19 (2026-03-24)

`automated-investigation.html` is an experimental standalone page (not linked from the main app). A section contains text in Cyrillic characters, an artefact from AI-generated content used as the basis for the page. The page is not part of the production navigation and is not indexed. No fix planned until the page is reworked.

---

## #10 Companies — Anduril: più investitori del previsto (ex infonodes-issues #05)

**Status:** Open — moved from infonodes-issues.md #05 (2026-03-28)

Su Company Search, Anduril mostra oltre 10 investitori. L'export da Crunchbase dovrebbe contenerne solo 5. Stessa anomalia osservata su iSci nel Graph (compare BlackRock non atteso).

> "noi dovremmo avere soltanto 5 investitori, su Company Search Anduril invece compaiono oltre 10, bisogna capire da dove arrivano"

**Azione:** Audit di `database.json` per verificare quante relazioni `REL-*` puntano ad Anduril e da dove provengono. Verificare se il problema è nella fase di migrazione da `investments.json` o in un import successivo.

---

## #11 Companies/Investors — Inconsistenze nomi aziende e paesi (ex infonodes-issues #06)

**Status:** Partially tracked — moved from infonodes-issues.md #06 (2026-03-28)

Nel database si trovano varianti non riconciliate dello stesso soggetto: "Leonardo" vs "Leonardo SPA" come company name; "China" vs "Cina" come country value. Necessario un passaggio sistematico di sanity check e normalizzazione.

> "alle volte c'è scritto Leonardo, alle volte Leonardo SPA [...] alle volte China con la H, alle volte Cina in italiano"

**Note:** Country aliases are already tracked in `data-issues.md #9` and normalised client-side via `COUNTRY_NORM`. Company name variants are not yet systematically addressed.

**Azione:** Eseguire `python3 scripts/validate.py` e integrare controlli di normalizzazione. Fare una passata manuale sui campi `name` e `sources.infonodes.country`.

---

## #12 Global — Disclaimer per paesi con dati limitati (Cina, Russia, Arabia Saudita) (ex infonodes-issues #58)

**Status:** Open — moved from infonodes-issues.md #58 (2026-03-28)

Structural limitation: Crunchbase coverage for countries with low corporate transparency (China, Russia, Saudi Arabia) is sparse or absent. Users who click entities from these countries find little data and no explanation.

> "le aziende da cui abbiamo preso i dati su Crunchbase a seconda del paese dove sono e della trasparenza di quel paese possiamo avere dati o no. Quindi Cina, Russia, Saudi Arabia, difficile avere dati."

**Proposta:** Add a contextual note when viewing entities from these countries, or when selecting them on the map: "Data for companies headquartered in [country] may be limited due to low public availability of corporate information." Could be a tooltip on the country name or a line in the entity card.

---

## #13 UI — Entity ID (IV-0143) non auto-esplicativo (ex infonodes-issues #59)

**Status:** ✓ Resolved — moved from infonodes-issues.md #59 (2026-03-28)

Laura ha visto l'ID "IV0143" nella scheda di un fondo e ha chiesto cosa fosse, pensando inizialmente fosse un identificatore utente. Gli ID interni del database (`IN-*`, `IV-*`) non hanno una label esplicativa nell'interfaccia.

> "IV0143? È un identificatore di utenti."

**Fix applied:** Added `title="Database ID — internal identifier for this entity"` tooltip to `.cs-hdr-id` span in `companysearch.js` (2026-03-28).

---
