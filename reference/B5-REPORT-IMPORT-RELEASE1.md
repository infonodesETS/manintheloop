# SEC Release 1 import: report and feedback on the data

> **DRAFT, written 2026-11-16, before the import.** Every number below comes from the dry-run of `scripts/import_sec_ownership.py` (it writes nothing to the database) and from the files of release 2026-10-17. After the import this file is rewritten with the real figures. The sections marked **Feedback** are meant for the maintainer of the SEC data set.

## 1. Summary

- Input: `rawdata/sec-edgar/2026-10-17/detentori-oltre-5.csv`, **571 rows** (480 entities, 91 persons) from 161 companies.
- Rule (decision S4): a row is imported if **capital ≥ 5% or votes ≥ 5%** (5.0 included).
- Dry-run result: **546 rows importable, 25 not imported, 0 blocked.** The reconciliation closes: 571 = 546 + 25.
- Would create: **546 `ownership` relationships**, **47 `role` relationships** (the roles of the 57 persons, see below), **57 `PER-` persons** and **93 new `IV-` holders**. Everything else matches an existing card.
- Not imported by design: addresses (S4) and age. Roles of board members, officers and committee members are imported **only for the 57 persons** (95 source rows from `consiglieri.csv`, `dirigenti.csv`, `comitati.csv`, one `role` relationship per person and company, 43 persons have at least one role); the roles of the other persons stay for Release 2.
- Nothing was written to `docs/data/database.json` yet. The raw files are never modified.

## 2. What is imported, exactly

| Item | Rule |
|---|---|
| One relationship per (holder, company, share class) | type `ownership`, own id `REL-NNNN`, key `(source, target, type, classe)` |
| Fields | `classe` as written in the filing, `pct`, `pct_voti`, `shares`, `holder_type`, `filing_date`, `as_of`, `as_of_origine`, `release`, `current`, `source_ref` (`2026-10-17/detentori-oltre-5.csv#<row>`), `history[]` |
| Empty percentage | means "below 1%" (README of the release), **not zero**; such rows are kept only if the votes reach 5% |
| Persons | one `PER-NNNN` per `P####`; the `P####` is kept in `sources.sec.person_ids`; person addresses never enter the database |
| Re-import | same key and same values: no change; different values: the old value goes to `history[]`; a row that disappears is marked `current: false`, never deleted |

**Rows not imported (25):** 14 with capital below 5% and votes below 5% or missing, 11 with capital empty and votes missing or below 5%. All are listed with the reason in `work/b5-release1/dry-run/riconciliazione.csv`.

**Dates (`as_of`).** The source text of each row was read in three formats. Result on the 546 rows: `deposito` (date of the filing) 350, `testo` (date written in the text, "data as of …") 98, `proxy` (date the proxy gives for the shares) 94, **no date** 4 (SATS, Charles and Cantey Ergen: no source and no `quote_al`). Three rows hold more than two dates and are flagged for a manual look (CHTR row 87, NWS rows 385 and 386).

## 3. How the matching was done

The data set identifies companies by ticker and CIK, the database by its own ids. Every link is a row in a table reviewed by hand (`work/b5-release1/proposta-*.csv`), never a name match done by the script.

1. **161 tickers → company cards.** 150 proposed from iShares ticker and name, 3 by hand through the share-class table, 8 settled after the independent check below.
2. **47 ticker + share class rows → cards (22 multi-class companies).** 29 already had a card for that class; for 13 missing classes the quota is written on the **existing card of the same company**, with the class inside the relationship (decision of 2026-11-16); 5 rows (GOOG, PLTR) go to the parent card.
3. **110 SEC holders → cards.** 17 matched an existing card, **93 new `IV-` cards** (S6: one node per filer; no group link without a person checking a primary source).

**Independent check.** For the cases where the database gave no sure signal (a shared ticker, similar names), AI agents with read-only access gave a second opinion. Role A (39 tickers) was **blind**: the agent did not see the proposal and searched for the card alone. Role B (25 holders) judged whether a holder is the same legal entity as a candidate card. Every claimed quote was reopened by a script and had to appear in the cited page; the verdicts that were not plain `same_entity` were read by a person.
- Role A: 33 of 39 agreed with the table; 5 tickers that had no proposal were resolved (AIR → AAR Corp, T → AT&T, TEL → TE Connectivity, TKO → TKO Group, LOGI → Logitech International, whose card carries the Swiss ticker LOGN); 1 disagreement (KTOS, see section 6).
- Role B: 1 same entity (Saudi Arabian Mining Company, Ma'aden), 13 different, 6 same group but different legal entities, 5 unclear. The 13 different, 6 same-group and 5 unclear holders all became new nodes (no group link is written, S6).

## 4. Checks on the result

- `reconciliation`: 571 = 546 + 25, no duplicate key among the relationships to create.
- `python3 scripts/validate.py` on a copy with the new entities and relationships added: all 12 checks pass; check 11 reports "546 ownership relationships checked, all valid".
- The four persons that Andrea's file flagged as possibly the same across companies (Durban, L. Murdoch, Blitzer, Gundermann) were reopened in primary sources and confirmed as the same person (2026-11-15).

## 5. Feedback on the data (for the maintainer)

**What worked well**
- The README is self-contained and every number in it could be recomputed from the CSV files (571, 480 + 91, 161).
- Stable `P####` and `E####` ids made a clean mapping possible, and the manual-check file caught real ambiguities.
- Each company carries the source URL of the proxy, so every claim can be reopened.

**Observations** (each with the count measured on the 2026-10-17 files)
1. **Missing sources.** 103 of 571 rows have an empty `fonte_dichiarazione` (75 persons, 28 entities, measured 2026-11-11). 6 companies have an empty `quote_al`: SATS, JBL, MPWR, NOW, TMUS, WS. For SATS the four rows have neither a source nor a date.
2. **Dates in three formats.** 333 rows have an ISO date, 135 have a date written in English or Italian prose ("filed February 5, 2025 (dati al 31 dicembre 2024)", "depositato il …"), 103 have none. The import had to parse all three; a single ISO column (`filing_date`, `as_of`) would remove the guesswork.
3. **One row, several parties.** Some holder names are not one legal entity: "Leonardo S.p.A. and Leonardo US Holding LLC", "Abrams Capital Management, L.P. and affiliates", "State Farm Mutual Automobile Insurance Company and related entities", "AE Industrial Partners and affiliates", "Tom Gores, Platinum Equity, LLC and the other reporting persons …". They cannot be matched to a single legal entity, so each became its own node.
4. **Share-class labels.** 18 different labels for what are a few classes ("Class A Common Stock" 72 rows, "Class A common stock" 16, "Common Stock", "Common Shares", "Ordinary Shares"). A normalised class column next to the original text would help.
5. **Alphabet.** The data lists Class A and Class B for GOOG; our database has Class A and Class C cards. We did not verify which one the filing means.
6. **A suspicious value.** The Vanguard Group in WBD has percentage `0` (below the threshold, so not imported). It looks like an extraction error rather than a real zero.
7. **Rows with nothing to filter on.** 10 rows have both capital and votes empty (in the not-imported group).
8. **Shared tickers.** AIR, T, TEL, TKO and LOGI are shared with other issuers or listed under another ticker (LOGN). The CIK in `aziende.csv` settled each case; we suggest keeping the CIK as the primary key everywhere, as it already is.
9. **Persons have no CIK.** As known (issue #33), so the `P####` id is the only key; it worked, but any future change of the registry needs a stable mapping file.

**Questions**
- Does an empty percentage always mean "below 1%" (asterisk in the proxy), or can it also be an extraction gap?
- Is the Vanguard Group row in WBD an error?
- For SATS, which proxy table and date do the Ergen holdings come from?
- Will Release 2 keep the same ids for holders and persons?

## 6. What we found in our own database while matching (not data problems)

- A duplicate card for the same issuer: Kratos (`IN-1304` with QID and tax id, `IN-1377` bare iShares import). The relationships go on `IN-1304`; the merge is a separate step.
- A mixed card for RTX (`IN-1324`: RTX QID and tax id, the subsidiary's Crunchbase block).
- Wrong or old identifiers on some cards (Wikidata of a predecessor for TE Connectivity and for Standard Aero, Crunchbase blocks of a subsidiary or predecessor on WBD, AMR, LITE and Materion).
All of these are handled card by card, outside this import.

## 7. Limits

- The independent check is done by a model of the same family that wrote the tables: it checks the information, not the judgement. Agreement does not prove an identity; the opposite happened only twice (KTOS, LOGI).
- The script checks that a quoted phrase exists in the cited page, not that it proves the claim; a person read the cases with weaker evidence (Nomura, E0084).
- The 119 matches already confirmed by an ISIN in our database were not re-checked by the agents (a sample of 15 was).
- `holder_type` is `company` or `person` only: the CSV does not say whether a holder is a fund.
- Date columns were parsed from free text: 98 `testo` and 131 prose-dated rows rest on this parser; 22 were spot-checked.

## 8. How to reproduce

```
python3 scripts/import_sec_ownership.py            # dry-run, writes only work/b5-release1/dry-run/
python3 work/b5-release1/verifica_tabelle.py        # mechanical check of the three tables
python3 scripts/validate.py                         # on the real database after the import
```
Files: `work/b5-release1/proposta-aziende.csv`, `proposta-classi.csv`, `proposta-gestori.csv` (the reviewed tables), `work/b5-release1/agenti/` (instructions, inputs, results, checker), `work/b5-release1/dry-run/` (reconciliation, new entities, preview of the relationships).
