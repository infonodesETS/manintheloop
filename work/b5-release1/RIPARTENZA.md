# B5 Release 1: ripartenza (riscritta il 2026-11-17)

> Si riscrive, non si accumula. Rimisurare con `git status` e `git log --oneline main..HEAD`.

## Dove siamo

- Branch `dati/b5-release1`, **pushato il 2026-11-17** (non era indietro rispetto a `main`, PR #72); nessuna PR aperta. `database.json` e `docs/` **non toccati**. File del lavoro QID/parentela committati a parte.
- **`--apply` scritto e provato su una copia** (2026-11-17): `python3 scripts/import_sec_ownership.py --db COPIA.json --out DIR --apply`; sul database vero serve `--database-reale` (non lanciato). Esito: 150 schede nuove (57 `PER-0001..0057`, 93 `IV-0758..0850`, ID reali in ordine alfabetico), 546 `ownership` da `REL-0001` a `REL-0546`, le schede esistenti identiche; seconda esecuzione = file identico; valore cambiato → `history[]`, riga scomparsa → `current: false` (provato su un'altra copia); `validate.py` passa. Scelte da confermare: `roles: ["investor"]` sulle persone, `entity_ids` in `sources.sec` degli `IV-`.
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

1. (fatto) Commit e push; piano per Davide aggiornato; `--apply` scritto e provato su copia.
2. Patch del sito su una copia di `docs/` e controlli della sezione 7 del piano.
3. **Le 25 righe scartate** (sotto soglia S4): tabella riga per riga (titolare, percentuali, testo della fonte, motivo), divisa tra «capitale <5» e «capitale vuoto»; Nelson decide, se cambia la soglia va riscritta S4. Si può fare in parallelo.
4. Stessa PR: dati + patch del sito + controlli. La PR la apre Nelson dal web.
5. A import fatto: riscrivere il report per Andrea con i numeri veri e rigenerare il PDF del piano.

## Da non dimenticare

- 4 righe senza `as_of` (SATS, Ergen): lasciate vuote. 3 righe con più date da guardare (CHTR 87, NWS 385 e 386).
- `holder_type`: solo `company` e `person`. KTOS: `IN-1377` è un duplicato da unire con B3 in una PR a parte.
- Schede sporche segnalate dagli agenti (RTX `IN-1324`, QID di TE e Standard Aero, Crunchbase di WBD, AMR, LITE, Materion): dopo l'import, caso per caso.
- Regole: domande → rispondere e fermarsi; mai modifiche su `main`; `UPDATE_PROTOCOL.md` per intero prima di toccare i dati; commit con `Co-Authored-By: Claude Sonnet 5.5`.
