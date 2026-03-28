# Known Issues

_Permanent data limitations and unresolvable gaps. Issues moved here from `issues.md` when they cannot be fixed without external data changes (e.g. Wikidata coverage improving). Each entry here must also have a dated record in `CHANGELOG.md`._

---

## #1 EDF — Count Mismatch

**Status:** ✓ Resolved — root cause identified (2026-03-28)

In European Defence Fund overview, calls with projects are **63**.
In EDF Call Search, calls with projects are **64**.

**Root cause:** The two tabs use different filters:
- `edfoverview.js` counts calls where at least one project has `eu_contribution > 0` → **63**
- `eucalls.js` counts calls where `projects.length > 0` regardless of contribution → **64**

The 1-call discrepancy is `EDF-2022-FPA-MCBRN-MCM` ("European defence medical countermeasures alliance"), which has 1 project entry but `eu_contribution` is null/empty in the source data.

**Not a bug.** The overview stat is labelled "Calls with Funded Projects" (eu_contribution filter is intentional). The call search shows all calls with project entries. The discrepancy is consistent with the data gap in #7 (projects with zero/null budgets). No code change needed — the labels are accurate.

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

## #5 Investors — Missing Wikidata IDs (103/240)

**Status:** Known limitation

103 out of 240 investor entities have no `wikidata_id`. These fall into categories that are unlikely to be resolved without manual research:

- **Niche VC funds** with no Wikidata entry (Air Street Capital, Akkadian Ventures, BSV Ventures, Coinvest Capital, Creator Fund, GoHub Ventures, HCVC, Iberis Capital, JME Ventures, K Fund, Keen Venture Partners, Marathon Venture Capital, Nebular, Robin Capital, Sahsen Ventures, Shape VC, Silicon Roundabout Ventures, SNÖ Ventures, Soma Capital, Speedinvest, Startmate, Sunfish Partners, TA Ventures, T.Capital, True Ventures, Ventura Capital, Valor Equity Partners, and others)
- **Individual angel investors** (Chris Adelsbach, Gustav Wiberg, Gytenis Galkis, Martynas Kandzeras, Mike Oliinyk, Noam Perski, Rita Sakus, Vladas Lašas)
- **Ambiguous single-word names** with no unambiguous Wikidata match (Bond, ESG, Matrix, REV, Third Point, JARE, Enova) — note: `Inc` was removed as a parse error entity (2026-03-28)
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

**Status:** ✓ Fully resolved (2026-03-28)

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

**Fully resolved (2026-03-28):** All country aliases normalised directly in `database.json` with full provenance history entries. Multi-country and ambiguous values resolved as follows:

| Old value | Entity | New value | Evidence |
|---|---|---|---|
| `UK/Spagna` | IN-0059 Ferroglobe | `United Kingdom` | Q125144368 — HQ London, UK incorporation |
| `Australia / UK` | IN-0131 Rio Tinto | `United Kingdom` | Q821293 — primary legal entity is Rio Tinto plc (UK) |
| `USA / Mexico` | IN-0143 Southern Copper Corporation | `United States` | Q7569806 — Delaware corporation, HQ Phoenix AZ |
| `internationality` | IV-0088 European Union | `European Union` | Q458 — supranational entity; canonical geographic grouping |

Also: `Czech Rep.` → `Czech Republic` and `UK` → `United Kingdom` were normalised (2026-03-28).

---


## #13 UI — Entity ID (IV-0143) non auto-esplicativo (ex infonodes-issues #59)

**Status:** ✓ Resolved — moved from infonodes-issues.md #59 (2026-03-28)

Laura ha visto l'ID "IV0143" nella scheda di un fondo e ha chiesto cosa fosse, pensando inizialmente fosse un identificatore utente. Gli ID interni del database (`IN-*`, `IV-*`) non hanno una label esplicativa nell'interfaccia.

> "IV0143? È un identificatore di utenti."

**Fix applied:** Added `title="Database ID — internal identifier for this entity"` tooltip to `.cs-hdr-id` span in `companysearch.js` (2026-03-28).

---
