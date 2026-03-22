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
