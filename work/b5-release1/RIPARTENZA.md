# B5 Release 1: ripartenza (riscritta il 2026-11-16, fine sessione)

> Si riscrive, non si accumula. Rimisurare con `git status` e `git log --oneline main..HEAD`.

## Dove siamo

- Branch locale `dati/b5-release1`, **non pushato**. `database.json` e `docs/` **non toccati**. Non tracciati da lasciare: `work/verifica-parentela/`, `work/verifica-qid/risultati/IN-0752.json`.
- **Dry-run chiuso:** `python3 scripts/import_sec_ownership.py` (solo anteprima, nessun `--apply`): 571 righe = 546 importabili + 25 scartate, 0 bloccate; 57 `PER-`, 93 `IV-` nuovi, 546 relazioni. `validate.py` passa su una copia di prova.
- **Tabelle riviste e firmate da Nelson** (`proposta-aziende/classi/gestori.csv`): controllo agenti fatto (A1-A4, B1-B3 in `agenti/risultati/`). Scelte: classi «una scheda sola» (13), Leonardo E0061 nodo `IV-` nuovo, KTOS su `IN-1304`.
- **Report per Andrea** (bozza, inglese): `reference/B5-REPORT-IMPORT-RELEASE1.md`; va riscritto con i numeri veri dopo l'import.
- **Piano sito per Davide** (docx + pdf): `work/b5-release1/sito/` con `patch-sito.diff` (verificata con `--check`, non applicata) e screenshot. **Il sito si modifica solo quando lo dice Nelson.**

## Prossimi passi, in ordine

1. Nelson legge il piano del sito e risponde sulle 5 decisioni (mappa e reti senza `ownership`, persone solo come nomi, 93 `IV-` vuoti, lingua delle carte, avviso chatbot); eventuale invio a Davide.
2. Scrivere `--apply` di `import_sec_ownership.py` (entità `PER-`/`IV-` con `history` e `sources.sec`, relazioni, report dei cambi, re-run sicuro) e provarlo **su una copia**.
3. Stessa PR: dati + patch del sito + controlli della sezione 7 del piano. La PR la apre Nelson dal web.
4. A import fatto: riscrivere il report per Andrea con i numeri veri.

## Da non dimenticare

- 9 righe senza `as_of` ora sono 4 (SATS, Ergen): lasciate vuote. 3 righe con più date da guardare (CHTR 87, NWS 385 e 386).
- `holder_type`: solo `company` e `person`. KTOS: `IN-1377` è un duplicato da unire con B3 in una PR a parte.
- Schede sporche segnalate dagli agenti (RTX `IN-1324`, QID di TE e Standard Aero, Crunchbase di WBD, AMR, LITE, Materion): dopo l'import, caso per caso.
- Regole: domande → rispondere e fermarsi; mai modifiche su `main`; `UPDATE_PROTOCOL.md` per intero prima di toccare i dati; commit con `Co-Authored-By: Claude Sonnet 5.5`.
