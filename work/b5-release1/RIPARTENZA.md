# B5 Release 1: ripartenza (riscritta il 2026-11-17, dopo la PR #73)

> Si riscrive, non si accumula. Questo file basta da solo per ripartire. Per iniziare, Nelson scrive «`@STATUS.md` e ripartenza». Riscritta il 2026-11-17 dopo la PR #73 e la prova della patch del sito su copia.

## 1. Come ripartire (in quest'ordine)

1. **Leggi** `STATUS.md` (per intero), questo file, `reference/UPDATE_PROTOCOL.md` (per intero: serve prima di scrivere sui dati). Prima di toccare l'import o i ruoli leggi anche `reference/S3`-`S7`, `SCHEMA.md` (*Relationships*), `scripts/validate.py` (controllo 11).
2. **Rimisura:** `git status`; `git log --oneline origin/main..HEAD`; `md5sum docs/data/database.json` (deve essere `459dfc004aaf8a8a15cc52eda51dcedd`, quello di `main`, finché l'import vero non è fatto); `python3 scripts/validate.py`; `python3 scripts/import_sec_ownership.py --out /tmp/dry` (solo anteprima; atteso: 571 = 546 importabili + 25 scartate, 0 bloccate, 57 `PER-`, 93 `IV-`, 546 `ownership`, 47 `role`).
3. **Riassumi** a Nelson in 5-8 righe cosa hai letto e **cosa non hai letto**, poi **fermati** e aspetta il suo via libera.

## 2. Dove siamo

- **PR #73 fusa in `main`** (2026-11-17, `717afa3`, solo documentazione e script, nessun dato, nessun file di `docs/`): script di import, `validate.py` con il ramo `role`, tabelle firmate, documenti per Andrea e Davide. Il branch `dati/b5-release1` è stato cancellato su GitHub (in locale resta, fuso: si cancella solo con ok di Nelson). Gli URL dei documenti ora puntano a `main`: report per Andrea `reference/B5-REPORT-IMPORT-RELEASE1.md`; piano per Davide `work/b5-release1/sito/PIANO-ADATTAMENTO-SITO.pdf` (e `.docx`, `patch-sito.diff`, `screenshot/`). Nelson li ha già inviati ad Andrea e Davide (confermato il 2026-11-17).
- **Database vero non toccato:** md5 `459dfc004aaf8a8a15cc52eda51dcedd`. **Import completo provato solo su una copia pulita** (fuori dal repo): `python3 scripts/import_sec_ownership.py --db COPIA.json --out DIR --apply`: 150 schede nuove (57 `PER-0001..0057`, 93 `IV-0758..0850`), 546 `ownership` (`REL-0001..0546`), 47 `role` (`REL-0547..0593`); seconda esecuzione identica; `validate.py` passa. Sul database vero serve `--database-reale` (non lanciato, decide Nelson).
- **Patch del sito: provata su copia il 2026-11-17 (vedi sezione 4): tutti i controlli superati.** La patch (`patch-sito.diff`: `docs/web/app.js` +55/−5, `docs/index.html` +2/−1) **non è nel repo**: entra solo nella PR unica con i dati.

## 3. Decisioni di Nelson (2026-11-17), da non rimettere in discussione

**Sito:** (1) mappa e reti senza le quote SEC (`NEW_REL_TYPES` in `index.html`; `networks.html` e `key-figures.html` non si toccano); (2) persone solo come nomi, senza scheda né ricerca (`PER-` fuori dal registro); (3) i 93 nuovi `IV-` cercabili e contati in «investors»; (4) carte nuove in inglese, traduzioni in sospeso (`ROADMAP.md` voce 19); (5) indice del chatbot MARLA **non** rigenerato, spiegato nel piano per Davide (sezione 5.5).
**Ruoli** (S7 rivisto, `reference/S7-RUOLI-E-PERSONE.md`): una relazione `role` per (persona, scheda) con `roles` dentro, solo i ruoli presenti; dettagli ok; `source_ref` come lista; età non importata; ruoli già con la Release 1 per le 57 persone. Le raccomandazioni di Claude sui punti aperti (director implicito, Silver Lake `other`, comitati senza ruolo `other`, `roles` dell'entità `["investor"]`) sono state adottate con la delega «ricontrolla tu, se modifiche proponi, sennò andiamo avanti»: Nelson può ancora correggerle.

## 4. Patch del sito su una copia: eseguita il 2026-11-17 (esiti)

Copie fuori dal repo (tre `docs/` servite su porte locali): **ora** (codice e database attuali), **ingenuo** (codice attuale, database con import completo), **dopo** (codice con la patch, stesso database). `git apply --check` e applicazione sulla copia riusciti. `validate.py` sul database della copia: PASSED (2732 entità, 4016 relazioni).

| Controllo | Ora | Ingenuo | Dopo |
|---|---|---|---|
| BlackRock `IV-0077`: Portfolio / connessioni | 4 / 4 | 148 / 148 | 4 / 4, più carta «Holdings ≥5% (SEC)» con 144 righe |
| AppLovin `IN-0034`: connessioni | 5 | 10 (misura del 2026-11-16) | 5, più carta «Shareholders ≥5% (SEC)» con 5 righe |
| Ramaco `IN-0298` (con `role`): connessioni | 5 (dal database, non aperta nel browser) | 21 | 5, più 13 righe di quote; nessun ruolo mostrato |
| Link con `PER-0001` | n/a | scheda come azienda (misura del 2026-11-16) | ricerca vuota, 0 errori in console |
| Contatore orgs · companies · investors | 2.545 · 1.408 · 733 | 2.695 · 1.408 · 826 | 2.638 · 1.408 · 826 |
| Mappa: archi / peso / relazioni caricate | 159 / 388 / 3.423 | 161 / 405 / 4.016 | 159 / 388 / 3.423 |
| Compare (AppLovin con BlackRock) | n/a | n/a | le due carte nuove compaiono, 0 errori |
| Cifre chiave (testo) | identico | non misurato | identico a «ora» (2.366 caratteri, stesso hash) |
| Reti (nodi / archi) | 486 / 517 | non misurato | 486 / 517 (testo identico) |
| Tema chiaro e 390 px | n/a | n/a | carta leggibile, nessuno scroll orizzontale (385 su 390) |

Novità confermata: il tipo `role` (47) è ignorato dal sito con la patch (Ramaco 21 → 5 connessioni). Console: solo il 404 di `favicon.ico`. **Non fatto:** screenshot nuovi; Cifre chiave e Reti non aperte con «ingenuo»; Compare provato su una sola coppia; nessuna prova con lingue diverse dall'inglese.

**Da aggiornare nel piano per Davide** (docx e pdf, a fine lavoro): le misure della sezione 4 (ora includono i `role`: «ingenuo» mappa 161 / 405 / 4.016, Ramaco 21) e lo stato «verificato su copia con `role`». Non è urgente: il piano già dichiara che le misure sono precedenti ai `role`.

## 5. Dopo, nell'ordine (ognuno con ok di Nelson)

1. **Le 25 righe scartate** (sotto soglia S4): tabella riga per riga (titolare, percentuali, testo della fonte, motivo), divisa tra «capitale <5» e «capitale vuoto»; Nelson decide; se cambia la soglia va riscritta S4. Si può fare in parallelo. **Stato (2026-11-18): in attesa di Andrea.** Nelson ha deciso di non verificare Liang e di chiedere ad Andrea un controllo sulla fonte originale dei valori NULL; testo della issue e dettaglio in `work/b5-release1/DOMANDA-ANDREA-SOGLIA-E-NULL.md` (nuova scoperta: 4 righe RKLB già importate per i voti con capitale NULL). Documento fuso con la PR #75; **issue #76 aperta il 2026-11-18 e assegnata ad `aborruso`** (risposta attesa; quando arriva, correggere i valori e, se serve, re-import); l'import delle 546 righe non aspetta la risposta.
2. **PR dei dati + sito** (stessa PR, regola S4), su un branch nuovo da `main`: `--apply --database-reale` sul database vero, `validate.py`, `git apply` di `patch-sito.diff` sul repo, controlli della sezione 7 del piano (già provati su copia), verifica a mano che il diff tocchi solo entità e relazioni nuove (`check_b3_branch.py` non vale per B5). La PR la apre Nelson. Testo in testo semplice tra «TESTO DA INCOLLARE» e «FINE TESTO DA INCOLLARE».
3. A import fatto: riscrivere il report per Andrea con i numeri veri, rigenerare il PDF, avvisare chi gestisce MARLA (via Davide) prima di una futura rigenerazione dell'indice, riallineare il piano per Davide.

## 6. Da non dimenticare

- 4 righe senza `as_of` (SATS, Ergen) lasciate vuote; 3 righe con più date da guardare (CHTR 87, NWS 385 e 386).
- `holder_type`: solo `company` e `person`. KTOS: `IN-1377` è un duplicato di `IN-1304`, da unire con B3 in una PR a parte.
- Schede sporche segnalate dagli agenti (RTX `IN-1324`, QID di TE e Standard Aero, Crunchbase di WBD, AMR, LITE, Materion): dopo l'import, caso per caso.
- `merge_entities.py` e `check_b3_branch.py` usano ancora `role_code` nella chiave: per le `role` nuove è `None`, quindi due `role` sulla stessa coppia fermano l'operazione (prudente; da rivedere se servirà unire schede con ruoli).
- Piano per Davide e report per Andrea già inviati da Nelson (2026-11-17, URL su `main`). Il report è una bozza e il piano ha le misure precedenti ai `role`: quando li riscrivi, avvisa che sono nuove versioni.
- Regole: domande → rispondere e fermarsi; mai modifiche o push su `main`; `UPDATE_PROTOCOL.md` per intero prima di toccare i dati; ricerche web con Exa; ogni riepilogo con gli URL locali delle schede toccate; commit con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
