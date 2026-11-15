# refactoringDB — Project Status

> Punto di ripartenza per il lavoro assistito da AI. Si **riscrive**, non si accumula: quando un lavoro finisce, una riga nel log e la voce sparisce da qui.
> Ultimo aggiornamento: 2026-11-15 (ripartenza eseguita). Lo stato di git e del database **non è scritto qui**: si misura (sezione «Come si misura lo stato»). Ripartire da «Dove siamo» e «Prossimi lavori».

## Dove siamo

- **B3 (pulizia duplicati):** pilota di 10 casi in `main`; **non chiuso** (casi aperti sotto). Controlli A/B sul foglio compilati con esiti approvati da Nelson; restano tre «Dubbia»/«Dubbio» (B3-04, B3-10, B3-11) e la decisione su Wsense (B3-09). Metodo, tabella dei casi e regola sulle classi: [`reference/B3-METODO.md`](reference/B3-METODO.md).
- **B5 (import Release 1)** non iniziato; scadenza 2026-11-15, **che non è un criterio**. I **4 controlli a mano** della Release 1 sono **firmati da Nelson il 2026-11-15** (tutte «stessa persona»): vedi `work/controlli-release1/foglio-4-controlli.csv`.
- **Foglio di controllo B3** (Google Sheets, id `1u5hWbQa0p3V53YPBWC27iMk2bWG8EWg-RPMxzBQl-7c`): proprietario Nelson; condivisione «chiunque ha il link» = Lettore (Editor: un altro account); copia dei valori del 2026-11-13 in `~/Coding/infonodes/Manintheloop-backup-2026-11-10/foglio-controllo-b3-2026-11-13/` (fuori dal repo).
- **Fatto:** F0 (backup in `~/Coding/infonodes/Manintheloop-backup-2026-11-10/`, freno locale su `main`, PR #28), F1 (verifiche), F2 (PR #29: tolti `beta/` e `old_version/`, tag `v.2026-b` e `archivio-2026-06`), F3 (PR #30 e #31: il sito sta in `docs/`; Pages servito da `main` `/docs`; gate G6 soddisfatto), F3.8 (fine congelamento), B1 (PR #34, schema e `validate.py`), B2 (PR #36, dati SEC in `main` ma non sul sito), B4 (PR #38, percorsi di `tmp/sec-test/`).
- **B1 — decisioni di schema (G7): S1-S7 prese il 2026-11-10/11; diff di schema e `validate.py` applicato il 2026-11-12 (vedi il log del 2026-11-12).** Una riga per decisione; le regole complete stanno nei file indicati e **vanno rispettate**:
  - **S1** persone: `PER-NNNN` permanente, `P####` della release SEC come riferimento di fonte in `sources.sec` (Andrea, 2026-11-10). Il CIK delle persone non esiste nei proxy/10-K (issue #33).
  - **S2** tipi di relazione: opzione (a), `ownership` (quote) + `role` (ruoli). Esito riferito da Nelson come «sì»; chi ha risposto e quando non è registrato.
  - **S3** doppie classi: opzione (c), nessun merge in B1, `classe` nella relazione, tabella ticker+classe → entità, scheda ritirata `entity_retired` se un giorno si unisce → [`reference/S3-CLASSI-AZIONI.md`](reference/S3-CLASSI-AZIONI.md).
  - **S4** dove vivono i dati: opzione (c), entità e relazioni nel DB, **indirizzi delle persone fuori dal DB**, **soglia «capitale o voti ≥5%», 5,0 incluso (546 righe su 571, 25 scartate con motivo)**, riconciliazione riga per riga, front-end adattato nella stessa PR → [`reference/S4-DATI-SEC.md`](reference/S4-DATI-SEC.md).
  - **S5** storicità: opzione (c), valori correnti + cambi in `history[]` della relazione, `as_of` con `as_of_origine`, righe scomparse `current: false` mai cancellate, report dei cambi prima di ogni re-import → [`reference/S5-STORICITA.md`](reference/S5-STORICITA.md).
  - **S6** gestori: opzione (c), un nodo per ogni depositante, legame di gruppo solo dopo verifica di una persona, abbinamenti con tabella rivista a mano, **State Street resta `IN-1468`**; FMR LLC non è Fidelity International `IV-0214` → [`reference/S6-GESTORI.md`](reference/S6-GESTORI.md).
  - **S7** ruoli e persone: `role` controllato + `role_text` originale (una relazione per ruolo, nessuna riga scartata); persone con registro di Andrea e controllo a mano dei casi nei controlli manuali (4 in Release 1: Durban `P0551`, L. Murdoch `P1197`, Blitzer `P1464`, Gundermann `P1690`) → [`reference/S7-RUOLI-E-PERSONE.md`](reference/S7-RUOLI-E-PERSONE.md).

Memo delle scelte di schema di B1 (oltre a S1-S7; testo completo in `reference/SCHEMA.md` e nel log del 2026-11-12): relazioni reali **senza `id`**; `id` proprio (`REL-NNNN`, 4 cifre o più) solo per le nuove `ownership`, `role`, `parte_di`; campi di `ownership` al livello superiore, chiave `(source, target, type, classe)`; **`role_code`** (non `role`) + `role_text`; `sources.sec` senza indirizzi (`validate.py` lo impone); `validate.py [file]` con percorso opzionale.

**Da confermare in B5:** nomi dei campi di `sources.sec` (`release`, `refs`, `person_ids`), valori di `holder_type` (`fund`, `company`, `person`), vocabolario di `role_code` (prima della Release 2).

## Prossimi lavori (ognuno con ok di Nelson, un passo alla volta)

- **Sequenza proposta dall'AI il 2026-11-14** (ogni passo con ok di Nelson, motivazione e costo): (i) PR di sola documentazione con i commit non pushati del branch di documentazione: **a fine giornata o insieme alla prossima PR di dati**; (ii) **pilota agentico** su 5-6 schede mai trattate del gruppo A dei 41 QID (`IN-0863`, `IN-0599`, `IN-0600` sono fatte: vedi il log del 2026-11-14), una PR per gruppo; per ogni scheda: `history` e `validation` lette, risultato dell'agente controllato con `work/verifica-qid/check_risultato.py`, dry-run di `scripts/patch_qid_removed.py`, ok di Nelson; **Pilota eseguito il 2026-11-15** su 6 schede (`IN-0670`, `IN-0897`, `IN-0980`, `IN-1019`, `IN-1122`, `IN-1194`): vedi il log del 2026-11-15; i risultati degli agenti sono in `work/verifica-qid/risultati/` (non tracciata). Procedura: lanciare gli agenti con `work/verifica-qid/ISTRUZIONE-AGENTE.md` (uno per scheda, sola lettura, non senza l'ok di Nelson), rilanciare **personalmente** `check_risultato.py`, verificare con `git status` che gli agenti non abbiano scritto altro, riferire a Nelson una tabella, e solo con il suo ok applicare le patch (dry-run, `--history-letta --apply`, un commit per scheda, una PR per gruppo; testi in inglese). (iii) la conferma definitiva dei metodi `reference/METODO-VERIFICA-WEB.md` e `reference/METODO-AGENTICO.md` dopo il pilota.
- **Parentela come dato strutturato (decisione di Nelson, 2026-11-15, da fare):** oggi che una scheda sia controllata di un'altra sta solo nel testo di `history` e `validation` (stati `qid_nulled_subsidiary` e `qid_nulled_sibling_subsidiary`, 43 voci, più le patch di `patch_qid_removed.py`); relazioni `parte_di` nel database: 0. Da decidere il modello (`parte_di` di S6 o un campo sulla scheda), adattare il sito nella stessa PR (oggi `app.js` legge come investimento ogni relazione diversa da `edf_participation`) e ricavare i legami dalle `validation` esistenti. Attenzione: la scheda che tiene il QID non è sempre la proprietaria legale (`IN-0671` per `IN-0670`, `IN-1020` per `IN-1019`).
- **Tabella «Retired IDs» di `UPDATE_PROTOCOL.md` non coincide con i dati (2026-11-15):** 34 righe, solo 4 erano schede ritirate, 30 erano schede attive. **Lotto 2 (branch `dati/b3-lotto2`, vedi log del 2026-11-15):** unite Saab, Indra, Arafura, PLS (4 schede ritirate nuove, `merge_entities.py` ora con `--prefer-winner`/`--prefer-loser`). **Lotto 3 (PR #49 fusa in `main`, `bc94b79`):** Vale unita (`IN-0401`→`IN-1344`). **Lotto 4 (PR #50 fusa in `main`, `c0063ab`; 11 coppie `IV-`/`IN-` omonime, regola «doppio ruolo: vince la scheda `IN-`» già in uso dal 2026-04-15):** unite NVIDIA, Apple, Intel, Oracle, Glencore, IBM, Zijin, Agnico-Eagle, Amazon, Ma'aden, Kaitseministeerium (11 schede ritirate nuove; `merge_entities.py` ora con `--drop-self-loop`, `check_b3_branch.py` lo riconosce). **Import investitori corretto (2026-11-15):** `import_investors_crunchbase.py` ricreava `IV-` doppie e 32 relazioni verso schede ritirate dopo le unioni (Ma'aden 2026-06-18, Kaitseministeerium dopo l'unione di aprile); ora segue `canonical`, non crea anelli e non crea una `IV-` con lo stesso nome di una `IN-` attiva (la elenca per la revisione). Dry-run: da 39 a 7 relazioni nuove, tutte verso investitori non ritirati, da verificare prima di scrivere. **Lotto 5 (branch `dati/b3-lotto5`, 8 coppie `IV-`/`IN-` omonime con lo stesso QID su entrambe le schede):** unite Softbank, South32, Tencent, Vodafone, Telefonica, Microsoft, Samsung Electronics, Tianqi Lithium (QID condivisi tra attive da 35 a 29; schede ritirate 37). Non restano coppie `IV-`/`IN-` omonime attive (misura del 2026-11-15, nome normalizzato). **Da chiudere:** (a) `IN-1335`/`IN-1150` TKMS: **non unite**; la partita IVA DE811124479 di `IN-1335` non è della TKMS GmbH (DE 221174497, HRB 6960 KI Kiel) né di thyssenkrupp AG (DE 812 656 084), titolare non identificato, `tax_id` messo a `null`; da decidere se `IN-1335` è la società, il gruppo o la holding quotata TKMS AG & Co. KGaA (senza scheda); (b) **non sono duplicati** (società nazionali distinte, nomi legali dei PIC): Airbus Operations `IN-0473`/`IN-0472`, Arianegroup `IN-0502`/`IN-0501`, Integrasys `IN-0784`/`IN-0783`, UMS `IN-1168`/`IN-1167`, Tekever `IN-1118`/`IN-1241`: il QID condiviso va trattato col metodo dei QID; (c) 18 investitori `IV-` con lo stesso nome di una società `IN-` (11 senza nota: Apple, Amazon, NVIDIA, Intel, Oracle, Glencore, IBM, Zijin, Agnico-Eagle, Ma'aden, Kaitseministeerium): serve prima una decisione di principio (unire o ruoli diversi); gli ID `IV-` della tabella sono vecchi (rinumerati il 2026-04-22, interpretazione non verificata). Nulla di (a)-(c) è scritto nei dati.
- **B3-09 Wsense (decisione di Nelson, 2026-11-14):** il database rappresenta l'acquisizione di Wsense da parte di Fincantieri solo se Wsense si occupa di armi autonome ed è nella filiera difesa. Verifica Exa (proposta, non esito): nessuna fonte indica armi, la filiera difesa sì (beneficiaria EDF). Closing e quota iniziale (61,95% solo di startupbusiness.it) **non confermati**: non si scrive nulla finché non si conoscono. Dettagli nel log del 2026-11-14.
- **`IN-1352` Alcoa Warrick, residuo:** QID e EIN senza fonte sono già stati tolti (PR #41 e #43; vedi il log del 2026-11-14). Il profilo Crunchbase `alcoa-warrick-operations` è stato letto con Claude in Chrome il 2026-11-14 (Alcoa Warrick LLC, sub-organization di Alcoa, acquisita da Kaiser: annuncio 2020-11-30, cessione al 2021-03-31 secondo l'8-K); la nota è sulla scheda (`validation`, PR #45) e sul foglio B3-11. Resta da decidere se la scheda descrive ancora Alcoa (nome, sito, paese) e se va corretta.
- **41 entità attive con QID rimesso** (baseline `work/qid-rimessi-noti.json`): caso per caso, a gruppi piccoli; lo stesso metodo di `IN-1352` (verificare l'etichetta del QID su Wikidata prima di tutto: due errori su tre trovati finora avevano etichetta vuota o della madre). **Valutazione del 2026-11-14** (sola lettura, proposte non esiti) in `work/verifica-web-test-2026-11-14.md`: gruppo A 20 schede con sospetto QID della casa madre, B 1 errore chiaro (`IN-0863`, **risolto con la PR #44**: il QID resta su `IN-0865`, dove è giusto), C 6 probabilmente a posto, D 14 con più schede per lo stesso QID. Quanti restano: `python3 scripts/validate.py`, controllo 12.
- **Metodo agentico (bozza provvisoria, provato su 3 schede già trattate):** agenti in sola lettura, controllo automatico del risultato, tabella per Nelson; da provare su 5-6 schede mai trattate del gruppo A dei 41 QID (pilota). Nota e limiti in [`reference/METODO-AGENTICO.md`](reference/METODO-AGENTICO.md), istruzione e controllo in `work/verifica-qid/`.
- **Metodo di verifica web con Exa:** bozza **provvisoria** in `reference/METODO-VERIFICA-WEB.md`, da provare su casi reali (fase successiva) e poi confermare.
- **4 controlli a mano della Release 1:** fatti, firmati da Nelson il 2026-11-15 (vedi il log del 2026-11-15); non servono più prima di B5.
- **Casi aperti di B3** (`IN-0863` chiuso con la PR #44; `IN-0683`/`IN-1553` non toccare, Ericsson B `IN-0123`, Grupo Mexico B `IN-0151`, Samsung Non Voting Pref `IN-0313`, `IN-1352` residuo); chiave Exa da rigenerare a B3 finita; nome «IDV Defence Vehicles Italia» da riverificare su GLEIF (il cambio di nome è del 2026-08-07 per GLEIF, vedi B3-04 sul foglio); `search_missing_qids.py` ha ora la guardia sui QID tolti, ma non va lanciato senza controllare le schede ritirate.
- **B5, import Release 1** (scadenza del 2026-11-15; **la scadenza non è un criterio**, criteri: qualità dei dati, nessuna perdita, impatto su DB e sito). Prima delle letture obbligatorie per B5 (sezione «Letture obbligatorie», punto 3): `S3`-`S7` per intero, `SCHEMA.md` (sezione *Relationships*), `validate.py` controllo 11; dry-run approvato prima di qualunque scrittura; PR aperta con dry-run approvato = consegna.
- **Poi, nell'ordine:** finire B3, B5 (import Release 1; front-end adattato **nella stessa PR dei dati**: `REL_MAP` in `app.js`, `index.html`, `networks.html`, `key-figures.html`, badge `person`), F5 (GitHub Action), F6. Da verificare quando capita: se il bug delle etichette Rete in tema chiaro (riga in `ROADMAP.md`) esiste ancora.
- **Reindirizzamento dalle schede ritirate** sul sito (`docs/web/app.js`, dove si tolgono le entità con `entity_retired` al caricamento): decisione separata, è una modifica al sito.
- **Backlog dati** (patch P159, Crunchbase Cycle 3, investitori senza paese, entità forse controllate, ecc.): vedi «Da fare — Dati» in [`ROADMAP.md`](ROADMAP.md).

**Foglio dei 4 controlli a mano della Release 1** (Durban `P0551`, L. Murdoch `P1197`, Blitzer `P1464`, Gundermann `P1690`): `work/controlli-release1/foglio-4-controlli.csv`, colonne `esito`, `nota`, `controllato_da`, `data` **compilate il 2026-11-15, firma di Nelson**: «stessa persona» per tutte e quattro, con le frasi lette nelle fonti primarie riaperte (log del 2026-11-15). Sono quindi unibili sotto lo stesso `PER-NNNN` in B5.

### Scoperta del 2026-11-13: 41 entità attive con QID tolto e rimesso

Su 41 entità attive il QID era stato tolto con `qid_removed` il 2026-04-23 e fu rimesso il 2026-06-18 da `search_missing_qids.py --apply` (le voci `accepted` di `work/qid_candidates.json` erano più vecchie della rimozione). Esempi: i quattro «Airbus Defence And Space», Beyond Gravity Austria e Svezia, MBDA España `IN-0863` e Italia `IN-0865`, `IN-0287`, `IN-0401`, `IN-1253`. **Non verificati uno per uno, non sono B3**: da rivedere caso per caso (il QID rimesso è giusto o è ancora quello della casa madre?). L'elenco delle 41 coppie è la baseline di `work/qid-rimessi-noti.json`; il controllo 12 di `validate.py` fallisce solo su casi NUOVI. La guardia in `search_missing_qids.py` (`is_retired`, `removed_qid_dates`, `qid_is_blocked`) impedisce ora un nuovo rientro (`--apply` stampa BLOCKED; per ripristinare di proposito serve una validation `status=qid_restored` con `wikidata_id`).

## Regole che valgono sempre

- **Domande → rispondere e fermarsi.** «Voglio che… + domande» è una richiesta di proposta, non un via libera. Nel dubbio è una domanda.
- **Mai push né modifiche su `main`** (in `main` si entra solo da un branch con PR). Push e PR li fa Nelson dal web (`gh` non c'è). Titolo, descrizione e ogni testo da inviare: testo semplice (niente markdown) tra «TESTO DA INCOLLARE» e «FINE TESTO DA INCOLLARE».
- **Quante PR (Nelson, 2026-11-13; Andrea ha risposto via mail il 2026-11-14; testo in piano §0.3):** documenti nella PR del lavoro a cui si riferiscono; PR di sola documentazione solo a fine giornata o se serve a un altro; dati una PR per caso o gruppo piccolo omogeneo.
- **`reference/UPDATE_PROTOCOL.md` si legge per intero prima di qualunque modifica ai dati** (regola di Nelson, 2026-11-15), anche per una sola scheda. Nel riassunto iniziale si dice se è stato letto.
- **Per ogni modifica ai dati:** dry-run, history e validation lette (di entrambe, per le unioni), mostrare, ok di Nelson, `--history-letta --apply`, `validate.py`, `check_b3_branch.py`, un commit per caso.
- **Ogni riepilogo** con gli URL locali o del sito delle schede toccate, forma `http://localhost:8001/search.html?lang=en&organization=IN-1318&organizationName=Palantir+Technologies` (server: `cd docs && python3 -m http.server 8001`).
- **Ricerche web sempre con Exa** (regola di Nelson, 2026-11-14): endpoint `/answer`, chiave in `~/.config/infonodes/exa.env` (mai stampata), nella query solo dati pubblici (nomi di società, codici); esempio in `work/b3-pilota/pilota_exa.py`. Le fonti che Exa cita si riaprono prima di darle per buone. Metodo in bozza provvisoria: [`reference/METODO-VERIFICA-WEB.md`](reference/METODO-VERIFICA-WEB.md).
- **Agenti e ricerche web:** i risultati sono **proposte e dati**, non esiti. L'esito lo decide e lo firma Nelson (formula: «Nelson (proposto da agente Claude, approvato il AAAA-MM-GG)»). Un agente non scrive nel foglio né nel repo.
- **Non cancellare** branch, stash o file senza ok. Risposte in italiano con gli accenti. Commit con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` e, per questo file, messaggio `docs(refactoringDB): update STATUS.md`.
- **I numeri sullo stato di git hanno una scadenza** (piano §0.3): si rimisurano a inizio task. **In questo file non si scrivono SHA di `main`, numeri di PR in corso né conteggi del database**: per restare veri richiederebbero un'altra PR. Si scrive il comando che li misura. **Prima di operare su `main`** controllare con git cosa contiene (`git log --merges --oneline main`): la PR #32 era in `main` senza voce nel registro (errore di processo, 2026-11-12).
- **Chiudere un lavoro = cancellarlo da qui**: una riga nel log (e la riga del piano, se c'è), e la voce sparisce da «Dove siamo» e «Prossimi lavori».

## Non verificato

**Non verificato al momento della scrittura:** se la nota O1 era nelle PR #39-#45 (il tipo di merge è misurabile: `git log --merges` mostra «Merge pull request #N» per #40-#45); ruolo della condivisione del foglio; menu a tendina, colori e link cliccabili del foglio dopo le mie scritture; data esatta della cessione di Alcoa Warrick a Kaiser (annuncio 2020-11-30 contro 8-K 2021-03-31: stessa operazione?); profilo Crunchbase `business-machines` di `IN-0062` (403); data del cambio di nome IDV; conversione delle azioni di risparmio TIM del 2026-05-21; cartella `.playwright-mcp/` (circa 358 file, ignorata da git, creata dall'agente).

## ⚠️ Letture obbligatorie (per tipo di lavoro)

1. **Sempre:** `~/.claude/CLAUDE.md` e questo file **per intero** (sta in una lettura; se la lettura si interrompe, continuare con `offset`).
2. **Riorganizzazione, B3, B5 e a inizio sessione:** **`reference/PIANO-RIORGANIZZAZIONE.md` e `reference/LOG-RIORGANIZZAZIONE.md` per intero.** Se la lettura si interrompe, continuare con `offset` fino alla fine; non basta la coda.
3. **Per B5 (import), per intero:** `reference/S3-CLASSI-AZIONI.md`, `S4-DATI-SEC.md`, `S5-STORICITA.md`, `S6-GESTORI.md`, `S7-RUOLI-E-PERSONE.md` (regole vincolanti), poi `reference/SCHEMA.md` (sezione *Relationships*) e `scripts/validate.py` (controllo 11). Il riassunto qui sopra non basta: le regole precise (chiave `(source, target, type, classe)`, `as_of_origine`, niente indirizzi, soglia) stanno in quei file.
4. **Per B3 (duplicati), per intero:** **`reference/B3-METODO.md`** (metodo vincolante, regola unica sulle classi di azioni, tabella dei 10 casi), `scripts/merge_entities.py` (lo script da usare, non `dedup_entities.py --merge`), `work/b3-pilota/pilota-exa-2026-11-12.csv` (verdetti), e la sezione *Merging a duplicate entity* di `reference/UPDATE_PROTOCOL.md`, `scripts/dedup_entities.py` (merge e schede ritirate), `scripts/patch_orange_cb.py` (esempio di patch con scheda ritirata), `reference/S3-CLASSI-AZIONI.md` (regole R1-R6, casi noti), `reference/S6-GESTORI.md`, `rawdata/sec-edgar/2026-10-17/controlli-manuali.csv` e `README.md` della release, voce 16 di `ROADMAP.md`. Casi noti nel piano (B3): AMD `IN-0006`/`IN-1249`, MP Materials `IN-0242`/`IN-1311`, Palantir `IN-0282`/`IN-1318`, Alphabet `IN-0017`/`IN-0018` ↔ `IN-1247`, IBM `IN-0062` ↔ `IN-1294`, filiali Alcoa Warrick `IN-1352` e HII Mission Technologies `IN-1290`, più quelli di ROADMAP 16.
5. **Per modifiche al sito (front-end), anche dentro B5:** `reference/CONVENZIONI-SITO.md` (routing con `pushState`/`replaceState`, decisioni chiave) e `reference/design-system.html`. Prima di rieseguire una pipeline di dati: `reference/SCRIPTS.md` (comandi, ripetibilità, script una tantum da non rilanciare).
6. **Per una correzione di dati su una singola scheda:** **`reference/UPDATE_PROTOCOL.md` per intero (sempre, regola di Nelson 2026-11-15)**, scheda, `history` e `validation` dell'entità, lo script di patch che si usa (`patch_qid_removed.py`, `patch_clear_infonodes.py`, `merge_entities.py`); se la verifica passa dal web, anche `reference/METODO-VERIFICA-WEB.md` (bozza provvisoria); non serve il resto.
7. **Nel riassunto iniziale a Nelson elencare i file letti con le righe lette** **e dire esplicitamente cosa NON è stato letto.** Serve a Nelson per verificare che il contesto sia completo prima di dare l'ok.

## ⚠️ PIANO IN CORSO

Riorganizzazione in **un solo repo** (linea di Andrea Borruso, mail del 2026-11-08: `main` = sito, branch + PR sempre, nessun force-push, controlli come GitHub Action) e import dei dati SEC. **Il piano operativo è in [`reference/PIANO-RIORGANIZZAZIONE.md`](reference/PIANO-RIORGANIZZAZIONE.md)**, il log dettagliato di ogni task in [`reference/LOG-RIORGANIZZAZIONE.md`](reference/LOG-RIORGANIZZAZIONE.md).

**Regola per l'AI a inizio sessione:** leggere per intero piano e log (e `~/.claude/CLAUDE.md`), poi il primo task non completato nella tabella «Stato di avanzamento» (in fondo al piano); riassumere a Nelson in 5-8 righe dove siamo e **fermarsi in attesa**; aggiornare il log, la tabella e questo puntatore **dopo ogni task**; nessuna azione verso l'esterno (push, tag, impostazioni GitHub, testi inviati) senza ok esplicito di Nelson nello stesso turno. Se il messaggio di Nelson contiene domande: rispondere e fermarsi, senza modificare file. Mai push su `main`; PR e merge li fa Nelson dal web (`gh` non è installato).

**Criteri di Nelson per le decisioni di schema (2026-11-11):** (1) qualità dei dati; (2) nessuna perdita di informazioni, nemmeno «strada facendo»; (3) impatto sul database; (4) impatto sul sito. **La scadenza del 15 novembre non è un criterio.** Prima di consigliare, verificare sui dati e sul codice (sola lettura) e mostrare i numeri.

## Come si misura lo stato (non scrivere i valori qui)

```
git status; git branch --show-current; git fetch --prune; git ls-remote --heads origin
git log --oneline origin/main..HEAD; git log --merges --oneline -4 origin/main; git branch --list
python3 scripts/validate.py; python3 -I scripts/check_b3_branch.py
```

- Su GitHub restano solo `main` e `v.2026-c` (non si tocca; tag `sec-2026-10-17`). Branch locali da non toccare senza ok: `main`, `v.2026-c`, `archivio/locale-2026-11-10` (i 2 commit del vecchio piano a due repo, mai pushato), `docs/stato-pre-ripartenza`; `stash@{0}` «f03-modifiche-piano-status».
- L'hook di avvio può dire «Pull non riuscito / no tracking information» su un branch non pushato: è normale, non risolverlo con `git pull` o `--set-upstream`.
- Il database **non contiene ancora nessun dato SEC**: sono solo in `rawdata/sec-edgar/` (nel repo pubblico, non servito dal sito). Il database è `docs/data/database.json` e in `main` entra solo con una PR; `docs/data/mitl-index.json` **non** va rigenerato senza decisione separata e avviso a Davide.

## Aperti dopo B1

- **GDPR:** Nelson ritiene non problematico trattare dati pubblici per obbligo SEC (nome, quota, voti); gli indirizzi restano fuori «per il momento». Non è stato chiesto un parere ad Andrea e Davide né a chi cura la parte legale; la pubblicità del dato non esclude il GDPR (nota dell'AI, non parere legale).
- **Sito:** `app.js` (`REL_MAP`) e `index.html` leggono come investimento ogni relazione diversa da `edf_participation` (BlackRock avrebbe 143 archi sulla mappa); `networks.html` e `key-figures.html` filtrano per tipo e ignorerebbero le nuove. `typeBadge` non conosce `person`. **Non verificato:** se il registro di `app.js` esclude le entità `PER-` (visto solo il ciclo sui `IV-`); come mappa e reti trattano una `person` senza paese; se un link `?organization=<ID ritirato>` possa reindirizzare al vincitore (serve per B3).
- **Schema:** `parte_di` è una relazione (deciso nel diff di B1); `validate.py` controlla `history[]` solo sulle nuove relazioni. **Non verificato:** se il sito gestisce `current: false`.
- **Dati da controllare a mano:** WBD, Vanguard con percentuale «0»; AIR (collisione di ticker Airbus/AAR Corp); Alphabet Class C (DB) contro Class B (SEC); le 143 voci di `controlli-manuali.csv` (121 + 13 persone toccano la Release 2).
- **Release 2:** vocabolario dei ruoli da proporre e far approvare prima di importare; campi `current`, `start_date`, `end_date` dei ruoli.
- **Crescita del DB:** stima iniziale +0,5 MB per la Release 1 e +2,6 MB con la 2, sovrastimata (persone distinte 58, entità 110): rifarla in B5.
- **Infrastruttura:** F0.7 (b) regole su `main`, (c) permessi Actions, (e) ruolo Admin (account `infonodes`); `MITL_INDEX_URL` (Vercel, progetto `marlamag`): Davide non può leggere la variabile ma dice «dovrebbe essere» `https://infonodesets.github.io/manintheloop/data/mitl-index.json`, l'URL risponde (301 → 200), chiuso con riserva, **l'URL non va cambiato**; termini Crunchbase: «incerto, tendente a consentito», verifica di dettaglio da fare (G2 sbloccato con riserva); indice MARLA `docs/data/mitl-index.json` più vecchio del database (2226 contro 2449 soggetti), rigenerarlo è una decisione separata.

## Da sapere

**Trabocchetti incontrati (2026-11-12):** (a) `tmp/` è in `.gitignore` ma i file di `tmp/sec-test/` sono tracciati (aggiunti con `-f`): `git add <file di tmp/…>` può dare un avviso/errore e, in una catena `&&`, far saltare il commit successivo; controllare sempre con `git status` e `git diff --cached --name-only` cosa è in stage prima di committare. (b) I file di `tmp/sec-test/` sono un banco di prova con il **modello vecchio** (`board_membership`, `executive_officer`, `shareholder_5pct`, senza soglia S4): non sono il modello di B5. (c) Tutti gli script lavorano dalla radice del repo e il database sta in `docs/data/database.json`. (d) I messaggi di commit finiscono con la riga `Co-Authored-By` richiesta dal sistema; i testi per PR e messaggi a terzi si danno in testo semplice, tra «TESTO DA INCOLLARE» e «FINE TESTO DA INCOLLARE» (richiesta di Nelson).

Gli script si lanciano **dalla radice** del repo; `import_crunchbase_csv.py --dry-run` scrive comunque file di report; il sito è `docs/` (server locale: `cd docs && python3 -m http.server 8001`); transcript della call ed email di Andrea sono in `reference/meetings/` (locale, non su git); i dati SEC grezzi sono nel branch `v.2026-c` in `rawdata/sec-edgar/2026-10-17/` (git show origin/v.2026-c:… per leggerli senza fare checkout); i conteggi di S3-S7 sono ricalcolabili dai CSV di quella release.

**Chiave Exa:** salvata da Nelson in locale in `~/.config/infonodes/exa.env` (cartella `700`, file `600`, variabile `EXA_API_KEY`); **mai nei file del repo, nei log, nei commit, nelle risposte**; non stamparla. La chiave è stata incollata una volta in chiaro nella chat: Nelson valuti di rigenerarla a B3 finita.

**Rischio da ricordare:** `search_missing_qids.py` ha rimesso il 2026-06-18 un QID su un'entità già dichiarata duplicata (`IN-0366`), ricreando il QID doppio. Una scheda ritirata non protegge da un nuovo lancio dello script. Non lanciarlo senza prima controllare le schede ritirate.

## Session protocol

- **A inizio sessione**: se in testa esiste una sezione «Ripartenza», eseguirla per prima; poi leggere «Dove siamo» e «Prossimi lavori» e rimisurare lo stato con i comandi della sezione «Come si misura lo stato». Il `git pull` dell'hook funziona solo su un branch con remoto; negli altri casi non va forzato.
- **A inizio sessione, controllare anche `inbox/`** (ignorata da git, solo locale): se contiene file, leggerli e proporre dove spostarli (cartella o documento giusto), così che `inbox/` finisca vuota. Non spostare né cancellare nulla prima dell'ok.
- **A fine sessione** (o dopo un progresso importante): aggiornare questo file (riscrivendo, non aggiungendo) e committare. Messaggio: `docs(refactoringDB): update STATUS.md`.
- **Prima di ogni commit sui dati**: `python3 scripts/validate.py` deve passare. `issues.md` è ignorato da git (solo locale; scelta provvisoria).

## Project goal

Build a graph database integrating three data universes:

1. **iShares ETF holdings** — Mining (GICS 151040), Tech (GICS 45), Comm Services (GICS 50), Aerospace & Defense (GICS 201010)
2. **EDF (European Defence Fund) beneficiaries** — from `rawdata/edf_calls.json`
3. **Companies/startups** — migrated from `../refactoring/data/database.json` (old DB, read-only)

The old DB (`../refactoring/`) is **read-only** — never modify it. All work is inside this repo (root `Manintheloop/`) only.

## Schema

Regole e campi stanno in [`reference/SCHEMA.md`](reference/SCHEMA.md) (versione 3.0, aggiornata con B1) e in [`reference/UPDATE_PROTOCOL.md`](reference/UPDATE_PROTOCOL.md): ID permanenti, `history[]` solo in aggiunta, `sources.wikidata` gestito dagli script, tipi di relazione e blocchi `sources.*`. Non ricopiarle qui.

## Struttura del repo

- `docs/` — il sito pubblicato (GitHub Pages da `main` `/docs`): pagine, `web/`, `data/` (`database.json`, `edf_orgs.json`, `mitl-index.json`, ecc.)
- `reference/` — manuali e documenti di progetto (schema, protocolli, piano, log, storia, convenzioni)
- `work/` — lavoro interno, **non pubblicato** (Crunchbase, `qid_candidates.json`, pilota B3, controlli Release 1, report)
- `rawdata/` — dati grezzi, non si modificano (`edf_calls.json`, CSV iShares, `sec-edgar/`)
- `scripts/` — script, da lanciare **dalla radice**; elenco e uso in [`reference/SCRIPTS.md`](reference/SCRIPTS.md)
- `tmp/sec-test/` — banco di prova con il modello vecchio, non è il modello di B5
- radice: `STATUS.md`, `WORKFLOW.md` (come si lavora, di Andrea), `ROADMAP.md`

## Esperimenti (cartelle locali)

Cartelle di lavoro locali, tutte in `.gitignore`: **non vanno committate**. Servono per provare cose senza toccare `docs/data/database.json`.

| Cartella | Contenuto |
|---|---|
| `tmp/` | Esperimenti generici e screenshot Playwright (`tmp/playwright/`) |
| `IRPI-test/` | Indagine IRPI sugli appalti EU (xlsx e output) |
| `SEC/` | Workspace del branch di sicurezza |
| `Jon_Tassonomia/` | Classificazione dei tipi di investitore di Jon: CSV di partenza, `investors_taxonomy.json` (entità clonate dal DB + blocco `investor-type`) e `readme_jon.md` con i dettagli |

## Reference docs (read before modifying the DB)

| File | Purpose |
|---|---|
| `reference/SCHEMA.md` | Full schema v3.0 spec: entity types, ID prefixes, sources blocks, relationship types, history/validation format |
| `reference/UPDATE_PROTOCOL.md` | Rules for every DB modification: IDs permanent, history append-only, dry-run protocol, commit formats, merge/retire procedures |
| `reference/QID_LOOKUP_PROCESS.md` | How to run the 3-phase QID pipeline (search → SPARQL+Reconciliation fallback → human review → apply) |
| `reference/NETWORKS_LAYOUT.md` | Cytoscape cose layout parameter reference for `docs/networks.html`: what each param does, current values, tuning guide, node size constants |
| `work/crunchbase/CRUNCHBASE.md` | Crunchbase enrichment cycle: step-by-step process, reconciliation strategy (4-tier matching), Cycle 1 stats, 21 unresolved entities categorised |
| `status-graph.md` | Graph visualization design analysis — ego graph cases, global network scale problem, library options, open questions. **Not committed** (in .gitignore). |
| `status-map.md` | Map visualization analysis — architecture, data coverage, Playwright observations, 2 bugs, 10 UX problems, improvement backlog. **Not committed** (in .gitignore). |
| `status-search.md` | Search/profile visualization analysis — architecture (REGISTRY, REL_MAP, scoring), data coverage, Playwright observations, 2 bugs, 4 search quality gaps, 8 UX problems, improvement backlog. **Not committed** (in .gitignore). |
| `reference/design-system.html` | **Design system reference** — complete typography rules for all pages. Any new page or component must conform to this. Covers: font families, size scale (fs-xs→fs-stat), weights, line heights, text colors, grey palette, entity color palette, nav chrome, badges, sidebar tokens, stat cards, tables, search hero, networks page specifics, light theme rules, and 10 hard constraints. Open in browser from the repo root. |
| `reference/SCRIPTS.md` | Pipeline e comandi degli script (ex «Scripts reference» di questo file) |
| `reference/STORIA-LAVORI.md` | Cronologia dei lavori su database e sito fino a ottobre 2026 (ex «Completed work» e «Pending work») |
| `reference/CONVENZIONI-SITO.md` | Convenzione di routing delle pagine e decisioni chiave |
| `reference/B3-METODO.md` | B3: tabella dei 10 casi del pilota, metodo vincolante, regola sulle classi di azioni |
| `reference/PIANO-RIORGANIZZAZIONE.md`, `reference/LOG-RIORGANIZZAZIONE.md` | Piano operativo e diario di ogni task |
| `ROADMAP.md` | Backlog (anche «Da fare — Dati aperti» e «EU Funding map: da cercare») |

