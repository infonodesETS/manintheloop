# B5 Release 1: ripartenza (riscritta il 2026-11-17)

> Si riscrive, non si accumula. Rimisurare con `git status` e `git log --oneline main..HEAD`.

## Dove siamo

- Branch locale `dati/b5-release1` (a inizio sessione 2026-11-17 non era indietro rispetto a `main`, PR #72). `database.json` e `docs/` **non toccati**. Non tracciati da trattare a parte: `work/verifica-parentela/`, `work/verifica-qid/risultati/IN-0752.json` (lavoro QID, non B5).
- **Dry-run chiuso:** `python3 scripts/import_sec_ownership.py` (solo anteprima): 571 righe = 546 importabili + 25 scartate, 0 bloccate; 57 `PER-`, 93 `IV-` nuovi, 546 relazioni. `validate.py` passa su una copia di prova.
- **Tabelle riviste e firmate da Nelson** (`proposta-aziende/classi/gestori.csv`): controllo agenti fatto (A1-A4, B1-B3 in `agenti/risultati/`). Scelte: classi «una scheda sola» (13), Leonardo E0061 nodo `IV-` nuovo, KTOS su `IN-1304`.
- **Report per Andrea** (bozza, inglese): `reference/B5-REPORT-IMPORT-RELEASE1.md`; va riscritto con i numeri veri dopo l'import.
- **Piano sito per Davide** (docx + pdf): `work/b5-release1/sito/` con `patch-sito.diff` (verificata con `--check`, non applicata) e screenshot. Il sito si modifica solo quando lo dice Nelson.

## Decisioni di Nelson sul sito (2026-11-17)

1. Mappa e reti **senza** le quote SEC (filtro `NEW_REL_TYPES` in `index.html`; `networks.html` e `key-figures.html` non si toccano).
2. Le 57 persone sono **solo nomi** nelle carte degli azionisti, senza scheda né ricerca (`PER-` fuori dal registro).
3. I 93 nuovi `IV-` restano **cercabili** e contano nel totale «investors».
4. Carte nuove in **inglese**; le traduzioni (EN/IT/FR/ES in `docs/web/i18n.js`) restano **in sospeso**: voce in `ROADMAP.md`.
5. Chatbot MARLA (Vercel, `marlamag`): l'indice `docs/data/mitl-index.json` **non si rigenera** in questa PR; la questione, con i punti in sospeso, sta nel piano per Davide (sezione 5.5 e decisione 5).

## Prossimi passi, in ordine (ognuno con ok di Nelson)

1. Commit e push del branch (mai di `main`): PDF del piano e due non tracciati del lavoro QID da decidere con Nelson.
2. Aggiornare il piano per Davide (docx e pdf) con le decisioni e il chatbot.
3. Leggere `S3`-`S7`, `SCHEMA.md` (*Relationships*), `validate.py` (controllo 11) e il codice dello script; scrivere `--apply` di `import_sec_ownership.py` e provarlo **su una copia fuori dal repo** (ID reali primo libero, `history`, `sources.sec` senza indirizzi, relazioni da `REL-0001`, report dei cambi, seconda esecuzione = 0 modifiche, `validate.py`).
4. Patch del sito su una copia di `docs/` e controlli della sezione 7 del piano.
5. **Le 25 righe scartate** (sotto soglia S4): tabella riga per riga (titolare, percentuali, testo della fonte, motivo), divisa tra «capitale <5» e «capitale vuoto»; Nelson decide, se cambia la soglia va riscritta S4. Si può fare in parallelo.
6. Stessa PR: dati + patch del sito + controlli. La PR la apre Nelson dal web.
7. A import fatto: riscrivere il report per Andrea con i numeri veri e rigenerare il PDF del piano.

## Da non dimenticare

- 4 righe senza `as_of` (SATS, Ergen): lasciate vuote. 3 righe con più date da guardare (CHTR 87, NWS 385 e 386).
- `holder_type`: solo `company` e `person`. KTOS: `IN-1377` è un duplicato da unire con B3 in una PR a parte.
- Schede sporche segnalate dagli agenti (RTX `IN-1324`, QID di TE e Standard Aero, Crunchbase di WBD, AMR, LITE, Materion): dopo l'import, caso per caso.
- Regole: domande → rispondere e fermarsi; mai modifiche su `main`; `UPDATE_PROTOCOL.md` per intero prima di toccare i dati; commit con `Co-Authored-By: Claude Sonnet 5.5`.
