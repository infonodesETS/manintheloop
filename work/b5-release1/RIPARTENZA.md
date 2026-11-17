# B5 Release 1: ripartenza (riscritta il 2026-11-17, chiusura sessione)

> Si riscrive, non si accumula. Questo file basta da solo per ripartire. Per iniziare, Nelson scrive «`@STATUS.md` e ripartenza».

## 1. Come ripartire (in quest'ordine)

1. **Leggi** `STATUS.md` (per intero), questo file, `reference/UPDATE_PROTOCOL.md` (per intero: serve prima di scrivere sui dati). Prima di toccare l'import o i ruoli leggi anche `reference/S3`-`S7`, `SCHEMA.md` (*Relationships*), `scripts/validate.py` (controllo 11).
2. **Rimisura:** `git status`; `git log --oneline origin/main..HEAD`; `md5sum docs/data/database.json` (deve essere `459dfc004aaf8a8a15cc52eda51dcedd`, quello di `main`, finché l'import vero non è fatto); `python3 scripts/validate.py`; `python3 scripts/import_sec_ownership.py --out /tmp/dry` (solo anteprima; atteso: 571 = 546 importabili + 25 scartate, 0 bloccate, 57 `PER-`, 93 `IV-`, 546 `ownership`, 47 `role`).
3. **Riassumi** a Nelson in 5-8 righe cosa hai letto e **cosa non hai letto**, poi **fermati** e aspetta il suo via libera.

## 2. Dove siamo

- Branch `dati/b5-release1`, **pushato**, mai `main`. `database.json` e `docs/` **non toccati**. Nessuna PR aperta (la apre Nelson dal web).
- **Import completo provato solo su una copia pulita** del database (fuori dal repo): `python3 scripts/import_sec_ownership.py --db COPIA.json --out DIR --apply`. Esito: 150 schede nuove (57 `PER-0001..0057`, 93 `IV-0758..0850`, ID reali in ordine alfabetico), 546 `ownership` (`REL-0001..0546`), 47 `role` (`REL-0547..0593`) per 43 persone; schede e relazioni esistenti identiche; seconda esecuzione = file identico; `validate.py` passa. Sul database vero serve `--database-reale` (non lanciato, decide Nelson).
- Tabelle di abbinamento (aziende, classi, gestori) e **tabella dei ruoli** (`proposta-ruoli.csv`, 75 diciture → 13 codici) riviste e firmate da Nelson. Report per Andrea: `reference/B5-REPORT-IMPORT-RELEASE1.md` (bozza, inglese, da riscrivere con i numeri veri dopo l'import). Piano del sito per Davide: `work/b5-release1/sito/` (docx, pdf, `patch-sito.diff`, screenshot).

## 3. Decisioni di Nelson (2026-11-17), da non rimettere in discussione

**Sito:** (1) mappa e reti senza le quote SEC (`NEW_REL_TYPES` in `index.html`; `networks.html` e `key-figures.html` non si toccano); (2) persone solo come nomi, senza scheda né ricerca (`PER-` fuori dal registro); (3) i 93 nuovi `IV-` cercabili e contati in «investors»; (4) carte nuove in inglese, traduzioni in sospeso (`ROADMAP.md` voce 19); (5) indice del chatbot MARLA **non** rigenerato, spiegato nel piano per Davide (sezione 5.5).
**Ruoli** (S7 rivisto, `reference/S7-RUOLI-E-PERSONE.md`): una relazione `role` per (persona, scheda) con `roles` dentro, solo i ruoli presenti; dettagli ok; `source_ref` come lista; età non importata; ruoli già con la Release 1 per le 57 persone. Le raccomandazioni di Claude sui punti aperti (director implicito, Silver Lake `other`, comitati senza ruolo `other`, `roles` dell'entità `["investor"]`) sono state adottate con la delega «ricontrolla tu, se modifiche proponi, sennò andiamo avanti»: Nelson può ancora correggerle.

## 4. Prossimo passo (uno solo): patch del sito su una copia

1. Copia pulita del database fuori dal repo, `--apply` (comando sopra).
2. Copia di `docs/` fuori dal repo con quel database; `git apply --check work/b5-release1/sito/patch-sito.diff` e poi applicazione **sulla copia**.
3. Rifare i controlli della sezione 7 del piano (mappa, scheda investitore, scheda con classi, link `PER-`, contatore, Compare, Cifre chiave e Reti, tema chiaro, `validate.py`). **Novità rispetto al piano:** ora c'è anche il tipo `role` (47 relazioni, `PER-` → scheda): verificare che mappa, ricerca e conteggi lo ignorino come `ownership`.
4. Riferire a Nelson una tabella ora/dopo. Il piano per Davide (docx e pdf) e il report per Andrea sono già stati corretti il 2026-11-17 (ID dalla copia: `PER-0004` è `PER-0001`; `REL-0041` resta `REL-0041`; `role` = 47; frase finale rifatta); le schermate hanno ancora gli ID provvisori, e le misure della sezione 4 del piano sono precedenti ai `role`.

## 5. Dopo, nell'ordine (ognuno con ok di Nelson)

1. **Le 25 righe scartate** (sotto soglia S4): tabella riga per riga (titolare, percentuali, testo della fonte, motivo), divisa tra «capitale <5» e «capitale vuoto»; Nelson decide; se cambia la soglia va riscritta S4. Si può fare in parallelo al passo 4.
2. **PR dei dati + sito** (stessa PR, regola S4): sul branch, `--apply --database-reale` sul database vero, `validate.py`, patch del sito, controlli della sezione 7. `check_b3_branch.py` non vale per B5: verificare a mano che il diff tocchi solo entità e relazioni nuove. La PR la apre Nelson. Testo di titolo e descrizione in testo semplice tra «TESTO DA INCOLLARE» e «FINE TESTO DA INCOLLARE».
3. A import fatto: riscrivere il report per Andrea con i numeri veri; rigenerare il PDF; avvisare chi gestisce MARLA (via Davide) prima di una futura rigenerazione dell'indice.

## 6. Da non dimenticare

- 4 righe senza `as_of` (SATS, Ergen) lasciate vuote; 3 righe con più date da guardare (CHTR 87, NWS 385 e 386).
- `holder_type`: solo `company` e `person`. KTOS: `IN-1377` è un duplicato di `IN-1304`, da unire con B3 in una PR a parte.
- Schede sporche segnalate dagli agenti (RTX `IN-1324`, QID di TE e Standard Aero, Crunchbase di WBD, AMR, LITE, Materion): dopo l'import, caso per caso.
- `merge_entities.py` e `check_b3_branch.py` usano ancora `role_code` nella chiave: per le `role` nuove è `None`, quindi due `role` sulla stessa coppia fermano l'operazione (prudente; da rivedere se servirà unire schede con ruoli).
- Non è verificato se Nelson ha già inviato il piano a Davide e il report ad Andrea: chiedere, non presumere.
- Regole: domande → rispondere e fermarsi; mai modifiche o push su `main`; `UPDATE_PROTOCOL.md` per intero prima di toccare i dati; ricerche web con Exa; ogni riepilogo con gli URL locali delle schede toccate; commit con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
