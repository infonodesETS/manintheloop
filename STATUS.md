# refactoringDB — Project Status

> Authoritative resume point for AI-assisted work.
> Last updated: 2026-11-13 sera (ripartenza eseguita). `origin/main` = `ac78b5a` (PR #42 fusa; prima #39 `1a041a9` e #41 `1565fae` di B3, #40 `61812b0` solo documentazione). Foglio di controllo compilato con gli esiti A/B approvati da Nelson; QID di `IN-1352` tolto. DB su `main`: 2582 entità (2569 attive, 13 lapidi), 3485 relazioni. **Ripartire dal «Prompt di ripartenza» qui sotto (poi `IN-1352`)**

## ⚠️ PROSSIMO PASSO — leggere prima di tutto

**B1 e B2 sono chiusi e in `main`.** B1: PR #34 (`78d67f5`), schema e `validate.py`. B2: PR #36 (`fc38f14`), merge di `v.2026-c` con i dati SEC 2026-10-17, `tmp/sec-test/` e `scripts/export_labelling_sheets.py`; conflitti risolti `.gitignore` e `ROADMAP.md`; `docs/dev-v2026c-sec.md` spostato in `reference/`. **Verificato sul sito vivo il 2026-11-12:** `/rawdata/sec-edgar/…`, `/docs/dev-v2026c-sec.md`, `/reference/…`, `/tmp/sec-test/…`, `/scripts/…`, `/STATUS.md` danno 404; home, `data/database.json`, `data/mitl-index.json` danno 200; 27/27 file di `docs/` con hash uguale a `main`. Dettagli nel [log](reference/LOG-RIORGANIZZAZIONE.md).

**B4 è chiuso e in `main`** (PR #38, `357507c`, 2026-11-12): i 3 file di `tmp/sec-test/` leggevano il vecchio percorso del database, corretto; script provati in una copia, output identici a quelli nel repo; **controlli manuali aperti: 143 su 143** (calcolati dal CSV `controlli-manuali.csv`, colonne `esito` e `nota` vuote).

## ⚠️ Prompt di ripartenza da eseguire (cancellare questa sezione dopo l'esecuzione)

Nelson azzera il contesto (`/clear`) la sera del 2026-11-13 e vuole ripartire in modo preciso. Valori sotto = ultimo stato misurato, da **rimisurare** (piano §0.3): `origin/main` = `ac78b5a` (PR #42); branch locale **`docs/stato-ripartenza-eseguita`** con 4 commit di sola documentazione **non pushati** (`25304fb` prompt cancellato e stato; `7296afe` testi del foglio corretti, log; `d2e6481` regola sul numero di PR in piano §0.3 e qui sotto; più il commit di questo prompt): **non aprire una PR a parte, confluiscono nella prossima PR di dati** (regola di Nelson); branch locali anche `main`, `v.2026-c`, `archivio/locale-2026-11-10` e `docs/stato-pre-ripartenza` (non toccare; cancellare solo con ok); `stash@{0}` non toccare. L'hook di avvio può dire «Pull non riuscito» se il branch corrente non ha remoto: normale.

**Fare, nell'ordine:**

1. Leggere `~/.claude/CLAUDE.md`, questo file **fino a «Da sapere»**, `reference/PIANO-RIORGANIZZAZIONE.md` e `reference/LOG-RIORGANIZZAZIONE.md` **per intero** (`allow_large`). Per toccare il foglio: skill `anthropic-skills:google-workspace` e `references/sheets.md`; `update_values` si carica con ToolSearch.
2. Rimisurare in sola lettura: `git status`, `git branch --show-current`, `git fetch --prune`, `git ls-remote --heads origin`, `git log --oneline origin/main..HEAD`, `git log --merges --oneline -4 origin/main`, `python3 scripts/validate.py`, `python3 -I scripts/check_b3_branch.py`, `git branch --list`; rileggere il foglio (`get_values` su `Controlli!A1:P13`).
3. **Chiedere a Nelson** (non assumere): (a) la PR #42 l'ha fusa lui, con «Create a merge commit»? (b) qualcuno ha cambiato il foglio dopo il 2026-11-13? il link «chiunque ha il link» è Lettore: va bene o serve Editor? (c) i 4 controlli a mano della Release 1 sono compilati? (d) il DB deve rappresentare l'acquisizione di Wsense da parte di Fincantieri (B3-09)? (e) ha mandato ad Andrea il testo sul numero di PR (sotto)? risposta?
4. Riassumere in 5-8 righe, **con i file letti e le righe, e cosa NON è stato letto**, e **fermarsi in attesa dell'ok**.
5. Dopo l'ok: cancellare questa sezione e committare con `docs(refactoringDB): update STATUS.md` **sul branch `docs/stato-ripartenza-eseguita`** (mai su `main`).

**Poi: `IN-1352` Alcoa Warrick** (punto (2) sotto), un passo alla volta con ok di Nelson: (i) sola lettura di scheda, `history`, `validation` di `IN-1352`, mostrare a Nelson; (ii) EIN 81-1153200 sulla scheda (EIN di Alcoa Corp: 81-1789115; l'agente non lo ha trovato) e profilo Crunchbase `alcoa-warrick-operations` (403 ai nostri strumenti: li apre Nelson nel browser); (iii) se l'EIN è sbagliato: `scripts/patch_clear_infonodes.py` in dry-run, mostrare, `--history-letta --apply`, `validate.py`, `check_b3_branch.py`, un commit. Una sola PR di dati; porta con sé i commit di documentazione. **Prima di proporre la PR dire quante PR sono già state aperte nella giornata** (piano §0.3, regola di Nelson del 2026-11-13). Dopo: (3) 41 QID rimessi, (4) 4 controlli Release 1 (li compila Nelson, in parallelo), (6) B5.

**Testo per Andrea sul numero di PR** (preparato il 2026-11-13, in testo semplice; invio non verificato; i conteggi: 14 PR dal 10 novembre, dalla #28 alla #42 senza la #33, di cui almeno 5 solo documenti: #32, #35, #37, #40, #42): vedi il log del 2026-11-13 sera. Il link al piano in `main` mostra il testo vecchio finché la regola non entra con la prossima PR di dati.

## ⚠️ Ripartenza eseguita il 2026-11-13 (sera)

Misurato: `origin/main` = `ac78b5a` (merge della PR #42 `docs/foglio-controllo-b3`, fusa; branch locale omonimo non più presente); `validate.py` PASSED 2582/3485; `check_b3_branch.py` superato (0 differenze). Foglio di controllo (id `1u5hWbQa0p3V53YPBWC27iMk2bWG8EWg-RPMxzBQl-7c`): colonne L-P uguali agli esiti approvati il 2026-11-13; condivisione «chiunque ha il link» = **Lettore** (Editor: account `ddelmonte79`; proprietario Nelson). **Non risposte da Nelson (da richiedere):** PR #42 fusa da lui e tipo di merge; modifiche di terzi al foglio; ruolo desiderato per il link; compilazione dei 4 controlli Release 1. Testi del foglio ancora da correggere (vedi punto (1) sotto), solo con ok di Nelson. Backup del foglio: `~/Coding/infonodes/Manintheloop-backup-2026-11-10/foglio-controllo-b3-2026-11-13/` (stato prima delle compilazioni L-P).

**Poi, nell'ordine del piano (ognuno con ok di Nelson, un passo alla volta):**

- **(1) FATTO il 2026-11-13 sera, con ok di Nelson: testi del foglio corretti** (celle `Controlli!D5`, `K5`, `K10`, `N10`, `D11`, `N11`, `B12`, `D12`, `G12`, `K12`, `N12`, riletto con `get_values`; esiti L-M, «Controllato da» e data non toccati; la nota `N5` di B3-04 non toccata; backup non aggiornato; aspetto nel browser non verificato). Restano: Nelson riesamina «Dubbia»/«Dubbio»; B3-09: decidere se il DB deve rappresentare l'acquisizione di Wsense. Testo originale del punto, tenuto per riferimento: (solo con ok): B3-11 non è più «Nessuna modifica» (QID tolto con la #41, PR da citare); B3-04: GLEIF registra il cambio di nome il 2026-08-07, non il 2026-01-28 di lei.report (nome attuale «IDV DEFENCE VEHICLES ITALIA S.P.A.», precedente «IVECO DEFENCE VEHICLES S.P.A.», capogruppo diretta Leonardo); B3-09: l'acquisizione di Wsense (61,95%, SPV, con condizioni) è riportata da startupbusiness.it del 2026-07-07, il testo «non confermata da altre fonti» va corretto, e resta da decidere se il DB debba rappresentarla; B3-10: sulla scheda `IN-1290` il sito non c'è (il link viene da Crunchbase), il testo «sito, settore e paese restano» va corretto; il profilo Crunchbase abbinato è una divisione di HII, non verificato. Poi Nelson riesamina «Dubbia»/«Dubbio». Aggiornare anche il backup solo se Nelson lo chiede (non sovrascriverlo: la copia di partenza resta com'è).
- **(2) `IN-1352` Alcoa Warrick:** verificare l'EIN 81-1153200 sulla scheda (l'agente non l'ha trovato; EIN di Alcoa Corp 81-1789115) e il profilo Crunchbase `alcoa-warrick-operations` (Crunchbase dà 403 ai nostri strumenti: serve un browser di Nelson). Se l'EIN è sbagliato: `scripts/patch_clear_infonodes.py` (dry-run, mostrare, `--history-letta --apply`, PR a parte).
- **(3) Punto (c): 41 entità attive con QID rimesso** (baseline `work/qid-rimessi-noti.json`): caso per caso, a gruppi piccoli; lo stesso metodo di `IN-1352` (verificare l'etichetta del QID su Wikidata prima di tutto: due errori su tre trovati finora avevano etichetta vuota o della madre).
- **(4) Punto (e): 4 controlli a mano della Release 1** (`work/controlli-release1/foglio-4-controlli.csv`): li compila Nelson, servono prima di B5.
- **(5) Punto (h):** casi aperti di B3 (MBDA España `IN-0863`, `IN-0683`/`IN-1553` non toccare, Ericsson B `IN-0123`, Grupo Mexico B `IN-0151`, Samsung Non Voting Pref `IN-0313`, `IN-1352` residuo); chiave Exa da rigenerare a B3 finita.
- **(6) B5, import Release 1** (scadenza del 2026-11-15; **la scadenza non è un criterio**, criteri: qualità dei dati, nessuna perdita, impatto su DB e sito). Prima delle letture obbligatorie per B5 (sezione «LETTURA OBBLIGATORIA», punto 3): `S3`-`S7` per intero, `SCHEMA.md` (sezione *Relationships*), `validate.py` controllo 11; dry-run approvato prima di qualunque scrittura; PR aperta con dry-run approvato = consegna.

**Regole che valgono sempre (promemoria):** **quante PR (Nelson, 2026-11-13; testo in piano §0.3): documenti nella PR del lavoro a cui si riferiscono, PR di sola documentazione solo a fine giornata o se serve a un altro, dati una PR per caso o gruppo piccolo omogeneo, e prima di proporre una PR dire quante già aperte oggi;** domande → rispondere e fermarsi; niente push né modifiche su `main`; push e PR li fa Nelson (`gh` non c'è): dare titolo e descrizione in testo semplice tra «TESTO DA INCOLLARE» e «FINE TESTO DA INCOLLARE»; per ogni modifica ai dati: dry-run, history e validation lette, ok, `--history-letta --apply`, `validate.py`, `check_b3_branch.py`, un commit per caso; ogni riepilogo con gli URL locali o del sito delle schede toccate; i risultati di agenti e di ricerche web sono **proposte e dati**, non esiti: l'esito lo decide e lo firma Nelson (formula usata: «Nelson (proposto da agente Claude, approvato il AAAA-MM-GG)»); un agente non scrive nel foglio né nel repo; non cancellare branch, stash o file senza ok.

**Non verificato al momento della scrittura:** tipo di merge delle PR #39, #40, #41 («Create a merge commit»?) e se la nota O1 era nelle PR; ruolo della condivisione del foglio; menu a tendina, colori e link cliccabili del foglio dopo le mie scritture; EIN e profilo Crunchbase di `IN-1352`; profilo Crunchbase `business-machines` di `IN-0062` (403); data del cambio di nome IDV; conversione delle azioni di risparmio TIM del 2026-05-21; cartella `.playwright-mcp/` (circa 358 file, ignorata da git, creata dall'agente).

## Cose da fare (ordine proposto; ognuna con ok di Nelson). Stato al 2026-11-13: (a) e (b) fatti

(a) **FATTO il 2026-11-13: PR #39 di B3 fusa in `main`** (merge `1a041a9`; fusa da Nelson dal web; se con «Create a merge commit» e se nella PR è scritto che non c'è stata revisione di Andrea e Davide, O1: **non verificato da me**). Verificato dopo il merge: `validate.py` PASSED 2582/3485; `docs/data/database.json` e `docs/data/mitl-index.json` sul sito vivo con sha256 uguale a `main`; 6 pagine e `data/mitl-index.json` 200; nel merge nulla sotto `docs/web`, `mitl-index.json` non toccato. **Foglio:** condiviso da Nelson con «chiunque ha il link» (Drive lo segna `UNLISTED`; il ruolo, Visualizzatore o Editor, non è verificato da me). **Copia di sicurezza dei valori** (scheda «Controlli» e «Legenda», letta con `get_values` il 2026-11-13 prima di modifiche altrui; non è un export byte per byte: niente formattazione, menu, colori, link cliccabili) in `~/Coding/infonodes/Manintheloop-backup-2026-11-10/foglio-controllo-b3-2026-11-13/foglio-controlli-b3.json` (fuori dal repo, sola lettura, sha256 in `SHA256SUMS` nella stessa cartella). Da usare per confrontare il foglio quando sarà compilato: ogni cella di Esito, Nota, Controllato da e Data cambiata rispetto alla copia è una compilazione. Un agente di sola lettura ha proposto gli esiti A e B (vedi log del 2026-11-13); **Nelson li ha approvati e li ho scritti nel foglio il 2026-11-13** (colonne L-P: «Corretta»/«Corretto» su B3-01, 02, 03, 05, 06, 07, 08, 09; «Dubbia»/«Dubbio» su B3-04 (data del cambio di nome IDV), B3-10 (sito assente e profilo Crunchbase), B3-11 (QID, ora tolto); «Controllato da»: «Nelson (proposto da agente Claude, approvato il 2026-11-13)»). **Da fare sul foglio, con ok di Nelson:** aggiornare la riga B3-11 (il QID è stato tolto, non è «nessuna modifica») e correggere i testi di B3-04 (data 2026-08-07 di GLEIF), B3-09 (acquisizione di Wsense riportata da startupbusiness.it) e B3-10 («il sito resta» non è vero sulla scheda). **Restano:** i controlli A e B sul foglio; se l'esito è «Sbagliata»: nuova PR di correzione o revert della #39. Il branch locale `dati/b3-unione-amd` si cancella con `git branch -d` solo con ok di Nelson.
(b) **FATTO il 2026-11-13, sullo stesso file, riletto con `get_values` e con la lettura della griglia** (nuova colonna G «Cosa c'era sulla scheda ritirata», dati ricavati dalla scheda su `origin/main`; testi di «Come si controlla» e «Legenda» passati a «dopo il rilascio»; nuova riga «Se l'esito è Sbagliata»; riga B3-10 aggiornata con i campi `infonodes` tolti; formule di avanzamento ora su L e M, menu a tendina spostati, 11/11/0/11/0 corretti). **Non verificati:** larghezze e aspetto nel browser, link cliccabili; la condivisione resta a Nelson. Testo originale del punto: **Foglio di controllo** (https://docs.google.com/spreadsheets/d/1u5hWbQa0p3V53YPBWC27iMk2bWG8EWg-RPMxzBQl-7c/edit , id `1u5hWbQa0p3V53YPBWC27iMk2bWG8EWg-RPMxzBQl-7c`): va aggiornato **sullo stesso file** (stesso link). Serve il connettore Google Sheets: il 2026-11-13 nella sessione c'erano solo gli strumenti Drive (che non modificano); verificare con ToolSearch «google sheets update», altrimenti dire a Nelson di abilitarlo (`/mcp` o riavvio) e **non** creare un secondo file. Regole di modifica: skill `anthropic-skills:google-workspace` e `references/sheets.md` (field mask senza parentesi, indici da 0, apice `'` per il testo). Da cambiare: (1) la scheda «Come si controlla» e la «Legenda» dicono che il controllo A si fa «prima della pubblicazione» e che i dubbi bloccano la pubblicazione: **non è più vero**, si controlla dopo il rilascio; (2) nuova colonna «Cosa c'era sulla scheda ritirata» nella scheda «Controlli»; (3) una riga su cosa fare se l'esito è «Sbagliata»: correggere con una nuova PR o con un revert della PR di B3. Nelson condivide il foglio da sé con chi controlla (ha un account Google). Poi rileggere il foglio via Drive per verificare.
(c) **41 entità attive con QID rimesso** (vedi «Scoperta del 2026-11-13» sotto): lavoro a parte, caso per caso.
(d) **Reindirizzamento dalle lapidi** sul sito (`docs/web/app.js` righe 90-94): decisione separata, è una modifica al sito.
(e) **4 controlli a mano della Release 1** (`work/controlli-release1/foglio-4-controlli.csv`): li compila Nelson; servono prima di B5.
(f) **B5** (import Release 1) dopo B3; front-end adattato nella stessa PR dei dati.
(g) **Chiave Exa** in `~/.config/infonodes/exa.env`: Nelson la rigenera a B3 finita; non stamparla mai.
(h) Altri aperti di B3: MBDA España `IN-0863` (paese Wikidata errato), `IN-0683` e `IN-1553` (Fincantieri, non toccare), Ericsson B `IN-0123`, Grupo Mexico B `IN-0151`, Samsung Non Voting Pref `IN-0313`; nome «IDV Defence Vehicles Italia» da riverificare su GLEIF; `IN-1352`: QID tolto con la PR #41, restano da verificare EIN e profilo Crunchbase (vedi tabella dei casi); `search_missing_qids.py` può ancora proporre un QID a `IN-1290` (ora bloccato dalla guardia, ma non lanciarlo senza controllare le lapidi); `docs/data/mitl-index.json` NON va rigenerato senza decisione separata e avviso a Davide.

**Regole di Nelson sempre valide:** se il messaggio contiene domande, rispondere e fermarsi; testi da inviare in testo semplice (niente markdown) tra «TESTO DA INCOLLARE» e «FINE TESTO DA INCOLLARE»; risposte in italiano con gli accenti; commit con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`; mai push né modifiche su `main`; in ogni riepilogo gli URL locali delle schede, forma `http://localhost:8001/search.html?lang=en&organization=IN-1318&organizationName=Palantir+Technologies` (server: `cd docs && python3 -m http.server 8001`); per ogni unione leggere prima history e validation di entrambe, dry-run, mostrare, `--history-letta --apply` solo dopo l'ok, `validate.py`, un commit per caso.

## ⚠️ Scoperta del 2026-11-13: 41 entità ATTIVE con QID tolto il 2026-04-23 e rimesso il 2026-06-18

Su 41 entità attive il QID era stato tolto con `qid_removed` il 2026-04-23 e fu rimesso il 2026-06-18 da `search_missing_qids.py --apply` (le voci `accepted` di `work/qid_candidates.json` erano più vecchie della rimozione). Esempi: i quattro «Airbus Defence And Space», Beyond Gravity Austria e Svezia, MBDA España `IN-0863` e Italia `IN-0865`, `IN-0287`, `IN-0401`, `IN-1253`. **Non verificati uno per uno, non sono B3**: da rivedere caso per caso (il QID rimesso è giusto o è ancora quello della casa madre?). L'elenco delle 41 coppie è la baseline di `work/qid-rimessi-noti.json`; il controllo 12 di `validate.py` fallisce solo su casi NUOVI. La guardia in `search_missing_qids.py` (`is_retired`, `removed_qid_dates`, `qid_is_blocked`) impedisce ora un nuovo rientro (`--apply` stampa BLOCKED; per ripristinare di proposito serve una validation `status=qid_restored` con `wikidata_id`).

## ⚠️ B3: PILOTA APPLICATO E IN `main` (PR #39, `1a041a9`); CONTROLLI A MANO DOPO IL RILASCIO (2026-11-13)

> Spostato in `reference/B3-METODO.md` (testo invariato).

**Foglio dei 4 controlli a mano della Release 1** (Durban `P0551`, L. Murdoch `P1197`, Blitzer `P1464`, Gundermann `P1690`): `work/controlli-release1/foglio-4-controlli.csv`, colonne `esito`, `nota`, `controllato_da`, `data` **vuote: le compila Nelson**. Exa dice «stessa persona» per tutte e quattro, ma le verifiche di Andrea non sono state ricontrollate a mano (README della release). Serve prima di B5 per creare i `PER-NNNN`.

**Chiave Exa:** salvata da Nelson in locale in `~/.config/infonodes/exa.env` (cartella `700`, file `600`, variabile `EXA_API_KEY`); **mai nei file del repo, nei log, nei commit, nelle risposte**; non stamparla. La chiave è stata incollata una volta in chiaro nella chat: Nelson valuti di rigenerarla a B3 finita.

**Rischio da ricordare:** `search_missing_qids.py` ha rimesso il 2026-06-18 un QID su un'entità già dichiarata duplicata (`IN-0366`), ricreando il QID doppio. Una lapide non protegge da un nuovo lancio dello script. Non lanciarlo senza prima controllare le lapidi.


**Regola (piano §0.3):** i numeri sullo stato di git qui scritti sono previsioni con data; si rimisurano con git all'inizio di ogni task. **Prima di operare su `main` controllare con git cosa contiene** (`git log --merges --oneline main`), non fidarsi solo di questo file: la PR #32 era in `main` senza voce nel registro (errore di processo rilevato il 2026-11-12). PR fuse finora: #27 `ac98a52`, #28 `2e6ae14`, #29 `f4edd71`, #30 `f318bb1`, #31 `f21ca8c`, #32 `7ef916a`, #34 `78d67f5`, #35 `ec7f190`, #36 `fc38f14`, #37 `f9a00db`, #38 `357507c`, #39 `1a041a9` (il #33 è un'issue). Il registro può essere indietro di una PR: contare sempre con `git log --merges`.

Memo delle scelte di schema di B1 (oltre a S1-S7; testo completo in `reference/SCHEMA.md` e nel log del 2026-11-12): relazioni reali **senza `id`**; `id` proprio (`REL-NNNN`, 4 cifre o più) solo per le nuove `ownership`, `role`, `parte_di`; campi di `ownership` al livello superiore, chiave `(source, target, type, classe)`; **`role_code`** (non `role`) + `role_text`; `sources.sec` senza indirizzi (`validate.py` lo impone); `validate.py [file]` con percorso opzionale.

**Da confermare in B5:** nomi dei campi di `sources.sec` (`release`, `refs`, `person_ids`), valori di `holder_type` (`fund`, `company`, `person`), vocabolario di `role_code` (prima della Release 2).

**Poi, nell'ordine:** finire B3 (e i 4 controlli a mano, che compila Nelson), B5 (import Release 1; front-end adattato **nella stessa PR dei dati**: `REL_MAP` in `app.js`, `index.html`, `networks.html`, `key-figures.html`, badge `person`), F5 (GitHub Action), F6. Da verificare quando capita: se il bug delle etichette Rete in tema chiaro (riga in `ROADMAP.md`) esiste ancora.

## ⚠️ LETTURA OBBLIGATORIA prima di agire (nell'ordine)

1. **Questo file solo fino a «Da sapere».** Il resto (da «Session protocol» in poi, circa 900 righe: script, stato del DB, lavoro passato) è storico e di riferimento: leggerlo solo se serve al compito. Una lettura di un file così lungo viene troncata: non dedurne di aver letto tutto.
2. **`reference/PIANO-RIORGANIZZAZIONE.md` e `reference/LOG-RIORGANIZZAZIONE.md` per intero.** Se la lettura si interrompe, continuare con `offset` fino alla fine; non basta la coda.
3. **Per B5 (import), per intero:** `reference/S3-CLASSI-AZIONI.md`, `S4-DATI-SEC.md`, `S5-STORICITA.md`, `S6-GESTORI.md`, `S7-RUOLI-E-PERSONE.md` (regole vincolanti), poi `reference/SCHEMA.md` (sezione *Relationships*) e `scripts/validate.py` (controllo 11). Il riassunto qui sopra non basta: le regole precise (chiave `(source, target, type, classe)`, `as_of_origine`, niente indirizzi, soglia) stanno in quei file.
4. **Per B3 (duplicati), per intero:** `scripts/merge_entities.py` (lo script da usare, non `dedup_entities.py --merge`), `work/b3-pilota/pilota-exa-2026-11-12.csv` (verdetti), e la sezione *Merging a duplicate entity* di `reference/UPDATE_PROTOCOL.md`, `scripts/dedup_entities.py` (merge e lapidi), `scripts/patch_orange_cb.py` (esempio di patch con lapide), `reference/S3-CLASSI-AZIONI.md` (regole R1-R6, casi noti), `reference/S6-GESTORI.md`, `rawdata/sec-edgar/2026-10-17/controlli-manuali.csv` e `README.md` della release, voce 16 di `ROADMAP.md`. Casi noti nel piano (B3): AMD `IN-0006`/`IN-1249`, MP Materials `IN-0242`/`IN-1311`, Palantir `IN-0282`/`IN-1318`, Alphabet `IN-0017`/`IN-0018` ↔ `IN-1247`, IBM `IN-0062` ↔ `IN-1294`, filiali Alcoa Warrick `IN-1352` e HII Mission Technologies `IN-1290`, più quelli di ROADMAP 16.
5. **Nel riassunto iniziale a Nelson elencare i file letti con le righe lette** (al 2026-11-12: piano 449, log 406, `STATUS.md` fino a «Da sapere» riga 66 su 1043) **e dire esplicitamente cosa NON è stato letto.** Serve a Nelson per verificare che il contesto sia completo prima di dare l'ok.

## ⚠️ PIANO IN CORSO

Riorganizzazione in **un solo repo** (linea di Andrea Borruso, mail del 2026-11-08: `main` = sito, branch + PR sempre, nessun force-push, controlli come GitHub Action) e import dei dati SEC. **Il piano operativo è in [`reference/PIANO-RIORGANIZZAZIONE.md`](reference/PIANO-RIORGANIZZAZIONE.md)**, il log dettagliato di ogni task in [`reference/LOG-RIORGANIZZAZIONE.md`](reference/LOG-RIORGANIZZAZIONE.md).

**Regola per l'AI a inizio sessione:** leggere per intero piano e log (e `~/.claude/CLAUDE.md`), poi il primo task non completato nella tabella «Stato di avanzamento» (in fondo al piano); riassumere a Nelson in 5-8 righe dove siamo e **fermarsi in attesa**; aggiornare il log, la tabella e questo puntatore **dopo ogni task**; nessuna azione verso l'esterno (push, tag, impostazioni GitHub, testi inviati) senza ok esplicito di Nelson nello stesso turno. Se il messaggio di Nelson contiene domande: rispondere e fermarsi, senza modificare file. Mai push su `main`; PR e merge li fa Nelson dal web (`gh` non è installato).

**Criteri di Nelson per le decisioni di schema (2026-11-11):** (1) qualità dei dati; (2) nessuna perdita di informazioni, nemmeno «strada facendo»; (3) impatto sul database; (4) impatto sul sito. **La scadenza del 15 novembre non è un criterio.** Prima di consigliare, verificare sui dati e sul codice (sola lettura) e mostrare i numeri.

## Stato del repo (2026-11-12)

- `main` = `origin/main` = `357507c` (merge della PR #38) al momento della scrittura. **Branch di lavoro attuale: `dati/b3-unione-amd`** (vedi «B3 IN CORSO»; contiene anche, via cherry-pick `8b8a134`, l'aggiornamento di STATUS/log/piano del vecchio branch `docs/stato-pre-ripartenza`, che resta in locale e si può cancellare con `-d` solo dopo il merge, con ok di Nelson). Vecchio branch di lavoro: `docs/stato-pre-ripartenza` (questo aggiornamento, non ancora pushato: il push e la PR spettano a Nelson; se la PR non è ancora fusa quando si apre la sessione, il branch corrente è questo e va bene così). Il hook di avvio può segnalare «Pull non riuscito / no tracking information» su un branch non ancora pushato: è normale, non risolverlo con `git pull` o `--set-upstream`.
- Su GitHub restano solo `main` e `v.2026-c` (non si tocca; tag `sec-2026-10-17`).
- Branch locali: `main`, `v.2026-c`, `archivio/locale-2026-11-10` (conserva i 2 commit del vecchio piano a due repo; mai pushato; cancellare solo con ok), più il branch di lavoro. `stash@{0}` «f03-modifiche-piano-status» (cancellare solo con ok).
- **Sul branch `dati/b3-unione-amd` il database è cambiato** (pilota B3 applicato, 3485 relazioni, 13 lapidi in tutto, 2569 entità attive); su `main` resta com'era dopo F3.7: 2582 entità, 3490 relazioni. `validate.py` PASSED su entrambi.
- **Da non dimenticare:** il database non contiene ancora nessun dato SEC; i dati SEC sono solo in `rawdata/sec-edgar/` (nel repo pubblico, non sul sito).

## Dove siamo

- **Fatto:** F0 (backup in `~/Coding/infonodes/Manintheloop-backup-2026-11-10/`, freno locale su `main`, PR #28), F1 (verifiche), F2 (PR #29: tolti `beta/` e `old_version/`, tag `v.2026-b` e `archivio-2026-06`), F3 (PR #30 e #31: il sito sta in `docs/`; Pages servito da `main` `/docs`; gate G6 soddisfatto), F3.8 (fine congelamento), B1 (PR #34, schema e `validate.py`), B2 (PR #36, dati SEC in `main` ma non sul sito), B4 (PR #38, percorsi di `tmp/sec-test/`).
- **B1 — decisioni di schema (G7): S1-S7 prese il 2026-11-10/11; diff di schema e `validate.py` applicato il 2026-11-12 (vedi «PROSSIMO PASSO»).** Una riga per decisione; le regole complete stanno nei file indicati e **vanno rispettate**:
  - **S1** persone: `PER-NNNN` permanente, `P####` della release SEC come riferimento di fonte in `sources.sec` (Andrea, 2026-11-10). Il CIK delle persone non esiste nei proxy/10-K (issue #33).
  - **S2** tipi di relazione: opzione (a), `ownership` (quote) + `role` (ruoli). Esito riferito da Nelson come «sì»; chi ha risposto e quando non è registrato.
  - **S3** doppie classi: opzione (c), nessun merge in B1, `classe` nella relazione, tabella ticker+classe → entità, lapide `entity_retired` se un giorno si unisce → [`reference/S3-CLASSI-AZIONI.md`](reference/S3-CLASSI-AZIONI.md).
  - **S4** dove vivono i dati: opzione (c), entità e relazioni nel DB, **indirizzi delle persone fuori dal DB**, **soglia «capitale o voti ≥5%», 5,0 incluso (546 righe su 571, 25 scartate con motivo)**, riconciliazione riga per riga, front-end adattato nella stessa PR → [`reference/S4-DATI-SEC.md`](reference/S4-DATI-SEC.md).
  - **S5** storicità: opzione (c), valori correnti + cambi in `history[]` della relazione, `as_of` con `as_of_origine`, righe scomparse `current: false` mai cancellate, report dei cambi prima di ogni re-import → [`reference/S5-STORICITA.md`](reference/S5-STORICITA.md).
  - **S6** gestori: opzione (c), un nodo per ogni depositante, legame di gruppo solo dopo verifica di una persona, abbinamenti con tabella rivista a mano, **State Street resta `IN-1468`**; FMR LLC non è Fidelity International `IV-0214` → [`reference/S6-GESTORI.md`](reference/S6-GESTORI.md).
  - **S7** ruoli e persone: `role` controllato + `role_text` originale (una relazione per ruolo, nessuna riga scartata); persone con registro di Andrea e controllo a mano dei casi nei controlli manuali (4 in Release 1: Durban `P0551`, L. Murdoch `P1197`, Blitzer `P1464`, Gundermann `P1690`) → [`reference/S7-RUOLI-E-PERSONE.md`](reference/S7-RUOLI-E-PERSONE.md).

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

---

## Session protocol

- **At session start**: run `git fetch && git pull` first, list any changes pulled (commits received, files changed), then read this file before taking any action.
- **At session start, also check `inbox/`** (gitignored, local only): if it contains files, read them and propose where each one should be moved (the right folder or doc), so that `inbox/` always ends up empty. Never move or delete anything before the user approves the proposal.
- **At session end** (or after significant progress): update this file, then commit.
- **Commit rule**: every STATUS.md update must be committed with message `docs(refactoringDB): update STATUS.md`.
- **Note:** `issues.md` is gitignored (local only) — temporary choice, may be revisited.
- **Validate before any data commit**: `python3 scripts/validate.py` must pass.

---

## ⚠️ PRIORITÀ 1 — analizzare il transcript della call

Arriveranno aggiornamenti presi dal transcript di una call, relativi a tutto il lavoro in corso (DB, dati SEC su `v.2026-c`, demo `tmp/sec-test/`, EU Funding map). **Primo compito**: analizzare il transcript e valutare gli action points (fattibilità, impatto, ordine) prima di toccare altro. Stato: transcript arrivato (file del 2026-10-23 in `inbox/`), da analizzare.

---

## ⚠️ PRIORITÀ — da cercare (EU Funding map)

La mappa EU Funding (`docs/index.html`, modalità EU Funding) oggi copre solo **EDF**. Gli altri strumenti di finanziamento europeo compaiono nei selettori come «work in progress»: **dobbiamo cercare i dati** (beneficiari, importi per paese ed entità) per ciascuno.

| Strumento | Stato nella mappa |
|---|---|
| EDF | attivo |
| HORIZON | work in progress → **da cercare** |
| PESCO | work in progress → **da cercare** |
| EDIP | work in progress → **da cercare** |
| EUDIS | work in progress → **da cercare** |
| EIF | work in progress → **da cercare** |
| DIANA | work in progress → **da cercare** |
| NIF | work in progress → **da cercare** |

**Search keywords** (per filtrare i bandi/progetti HORIZON che interessano):

autonomous weapons, unmanned, UAV, UAS, drone, FPV, VTOL, UGV, USV, UUV, AUV, robotic combat vehicle, unmanned ground vehicle, unmanned surface vessel, loitering munition, kamikaze drone, collaborative autonomy, MUM-T, automatic target recognition, ATR, target acquisition, targeting, kill chain, sensor-to-shooter, terminal guidance, autonomous navigation, GPS-denied, GNSS-denied, visual navigation, last-mile autonomy, fire control, weapon system, engagement, counter-UAS, C-UAS, counter-drone, interceptor, artificial intelligence, AI, machine learning, deep learning, neural network, computer vision, object detection, object recognition, image recognition, edge AI, edge computing, sensor fusion, data fusion, multi-sensor, decision support, decision advantage, surveillance, defense, defence, military, warfighter, battlefield, combat, tactical, lethality, command and control, C2, C4ISR, C5ISR, ISR, intelligence surveillance reconnaissance, situational awareness, battle management, common operating picture, mission planning, reconnaissance, persistent surveillance, wide-area, border security, border control, electronic warfare, EW, jamming, signal intelligence, SIGINT, dual-use, dual use

Testo di presentazione della mappa (così com'è oggi, da tenere allineato quando i selettori si attivano):

> This map shows the European funding for weapons development granted to individual EU States and, in detail, to which of their companies, universities or other public and private entities. The diameter of each circle is proportional to the total funding received by the State. Clicking on the circle for a country opens the list of all the individual entities that have received European funding, with the amount each one received. You can click on the name of any entity to open its detail page, containing all the information we have been able to collect. Using the selectors, you can choose to view all types of European public funding (EDF, Horizon, PESCO, etc.) or only the one(s) you are interested in.

---

## Scripts reference

> Spostato in `reference/SCRIPTS.md` (testo invariato).
---

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
| `reference/design-system.html` | **Design system reference** — complete typography rules for all pages. Any new page or component must conform to this. Covers: font families, size scale (fs-xs→fs-stat), weights, line heights, text colors, grey palette, entity color palette, nav chrome, badges, sidebar tokens, stat cards, tables, search hero, networks page specifics, light theme rules, and 10 hard constraints. Open in browser from `refactoringDB/` root. |

---

## Project goal

Build a graph database integrating three data universes:

1. **iShares ETF holdings** — Mining (GICS 151040), Tech (GICS 45), Comm Services (GICS 50), Aerospace & Defense (GICS 201010)
2. **EDF (European Defence Fund) beneficiaries** — from `rawdata/edf_calls.json`
3. **Companies/startups** — migrated from `../refactoring/data/database.json` (old DB, read-only)

The old DB (`../refactoring/`) is **read-only** — never modify it. All work is inside `refactoringDB/` only.

---

## Schema v3.0 — key rules

- Entity IDs: `IN-NNNN` (company), `IV-NNNN` (investor), `PER-NNNN` (person), `REL-NNNN` (relationship)
- IDs are permanent, zero-padded to 4 digits, assigned alphabetically within each batch
- `sources.ishares` is an **array** (one element per ETF appearance)
- `history[]` is append-only — never delete or edit existing entries
- `wikidata_id` format: `Q\d+` or `null`
- Relationship types allowed: `investment`, `board_membership`, `edf_participation`
- `sources.wikidata` is script-managed — never edit manually
- See `reference/SCHEMA.md` for full spec, `reference/UPDATE_PROTOCOL.md` for update rules

---

## Folder structure

```
manintheloop/
├── docs/                          ← IL SITO (GitHub Pages serve questa cartella)
│   ├── CNAME                      ← dominio mitl.infonodes.org
│   ├── index.html                 ← Map page (D3 SVG world map + investor arcs)
│   ├── search.html                ← Org search + profile viewer
│   ├── networks.html, key-figures.html, publications.html, about.html
│   ├── web/                       ← app.js, router.js, theme.js, i18n.js, graph.js, countries.js, css (single source of truth)
│   ├── reports/countries/index.html
│   └── data/
│       ├── database.json          ← main DB (schema v3.0) — primary artifact
│       ├── edf_orgs.json          ← PIC-keyed index of 794 EDF orgs with db_id crosswalk
│       ├── edf_calls.json         ← copia di rawdata/edf_calls.json (tenerla allineata con scripts/sync_site_data.py)
│       ├── glossary.json, glossary_terms.json, about_why.json, publications.json, last_update.json, defence_criteria.json
│       └── mitl-index.json        ← indice del chatbot MARLA (generato da scripts/build_chat_index.py)
├── work/                          ← lavoro interno, NON pubblicato dal sito
│   ├── qid_candidates.json        ← QID review file (1003 entries: 566 accepted, 65 rejected, 372 skipped)
│   ├── crunchbase/
│   │   ├── CRUNCHBASE.md         ← process + reconciliation log (read before touching anything here)
│   │   ├── companies_export.csv  ← full export (1149 rows: name + website)
│   │   ├── matches.csv           ← 812 rows uploaded to Crunchbase (Cycle 1)
│   │   ├── non_matches.csv       ← 337 rows excluded from Crunchbase upload
│   │   ├── crunchbase-export-matches-csv-4-13-2026.csv ← 724 rows from Crunchbase (Cycle 1)
│   │   └── unresolved_2026-04-13.csv ← 21 CB rows not matched to DB entity
│   ├── reports/                   ← report Italia, grafici e PDF
│   ├── sintesi/                   ← sintesi, traduzione EN, OpenTender
│   └── testi/                     ← testi della piattaforma
├── rawdata/
│   ├── edf_calls.json         ← EDF raw data (source of truth for EDF beneficiaries)
│   ├── ISHARES.md             ← metadata registry for all 4 iShares ETFs (ETF name, ticker, GICS, date)
│   ├── ishares_metals_mining_gics151040.csv
│   ├── ishares_tech_gics45.csv
│   ├── ishares_comm_services_gics50.csv
│   ├── ishare_aerospace_defense_GICS201010.csv        ← original Italian-locale file
│   └── ishare_aerospace_defense_GICS201010_en.csv     ← normalised (dot decimal) version used for import
├── scripts/
│   ├── parse_ishares.py       ← parses iShares CSVs → normalized dicts
│   ├── build_database.py      ← builds DB from iShares CSVs (dedup by name_key)
│   ├── build_edf_entities.py  ← imports EDF orgs, writes edf_orgs.json
│   ├── import_startups.py     ← migrates startups from old DB
│   ├── import_by_wikidata.py  ← migrates companies from old DB by wikidata_id
│   ├── search_missing_qids.py ← QID Phase 1 (Wikidata API) + --apply
│   ├── sparql_search_qids.py  ← QID Phase 1b (SPARQL + Reconciliation API fallback)
│   ├── enrich_wikidata.py     ← populates sources.wikidata for all QID-bearing entities
│   ├── import_crunchbase_csv.py ← imports Crunchbase export → sources.crunchbase (4-tier matching)
│   ├── regenerate_export.py   ← regenerates work/crunchbase/companies_export.csv from DB
│   ├── import_investors_crunchbase.py ← creates IV-NNNN entities + relationships from top_investors
│   ├── patch_investor_countries.py    ← assigns known countries to well-known IV-* investors (~90 curated)
│   ├── patch_iv_countries_p159.py     ← SPARQL P159/P17 fallback for QID-bearing IV with no country
│   ├── migrate_old_db_investors.py    ← migrates funds/banks from legacy refactoring/ DB
│   ├── import_edf_projects.py         ← creates EDF-NNNN project entities + edf_participation rels
│   └── validate.py            ← 10-check validation (always run before committing)
├── reference/
│   ├── SCHEMA.md
│   ├── UPDATE_PROTOCOL.md
│   ├── QID_LOOKUP_PROCESS.md
│   ├── NETWORKS_LAYOUT.md
│   └── design-system.html         ← Design system reference (open in browser)
└── STATUS.md                  ← this file
```

> **Serving the web UI locally:** `cd docs && python3 -m http.server 8001`, then open `http://localhost:8001/`. Run scripts always from the repo root.

---

## Esperimenti (cartelle locali)

Cartelle di lavoro locali, tutte in `.gitignore`: **non vanno committate**. Servono per provare cose senza toccare `docs/data/database.json`.

| Cartella | Contenuto |
|---|---|
| `tmp/` | Esperimenti generici e screenshot Playwright (`tmp/playwright/`) |
| `IRPI-test/` | Indagine IRPI sugli appalti EU (xlsx e output) |
| `SEC/` | Workspace del branch di sicurezza |
| `Jon_Tassonomia/` | Classificazione dei tipi di investitore di Jon: CSV di partenza, `investors_taxonomy.json` (entità clonate dal DB + blocco `investor-type`) e `readme_jon.md` con i dettagli |

---

## Current DB state

> Exact counts change as data evolves — run `python3 scripts/validate.py` and the enrichment analysis script for live figures.

| Aspect | Status |
|---|---|
| Schema | 3.0 |
| Entity prefixes | `IN-NNNN` (companies, institutions, gov agencies) · `IV-NNNN` (investors, funds) · `EDF-NNNN` (projects) · `PER-NNNN` (persons — not yet built) |
| Relationships | `investment` (Crunchbase + old DB) · `edf_participation` |
| Last validate.py | PASSED (2026-10-24) — 2582 entities, 3490 rels (unchanged since the 2026-10-19 EDF refresh) |
| iShares coverage | 4 ETFs: Tech (45) · Comm Services (50) · Mining (151040) · Aerospace & Defence (201010) |
| EDF coverage | All EDF calls from `rawdata/edf_calls.json`; all participants matched via PIC crosswalk |
| Crunchbase coverage | Cycle 2 complete; some entities still unmatched — see `work/crunchbase/CYCLE2.md` |
| Wikidata coverage | IN entities: partial (many EDF SMEs absent from Wikidata) · IV entities: fully enriched for all QID-bearing |
| QID pipeline | All proposals reviewed; remaining skipped entries are EDF SMEs genuinely absent from Wikidata |
| validation: cb_wrong_entity | 5 remaining — Fortescue, Telia, Tecnobit Sl, Nexa Technologies, United Aircraft |
| validation: cb_hq_mismatch_subsidiary | Several — CB matched regional subsidiary, not parent (Nintendo, Canon USA, Dentsu Americas, Thales USA, etc.) |
| validation: wikidata_country_corrected | 4 entities where WD P17 was wrong and nulled (Airbus Helicopters, STmicro Grenoble 2, Comec, RIO Tinto) |
| retired entities | IN-1282 Fortescue Metals Group — duplicate of IN-0133 |

---

## Completed work

> Spostato in `reference/STORIA-LAVORI.md` (testo invariato).
---

## Pending work (priority order)

> Spostato in `reference/STORIA-LAVORI.md` (testo invariato).
---

## Branch convention

> Rule: **never commit directly to `main`**. All work happens on the page branch, then merges to `main` when done.

**Remote policy (2026-05-11):** only `main` is pushed to `origin`. Feature branches are local only. `origin/graph` deleted — remote is now `origin/main` only.

| Branch | Scope |
|---|---|
| `map` | `docs/index.html` (D3 map) |
| `search` | `docs/search.html` + `docs/web/app.js`, `docs/web/router.js` |
| `graph` | `docs/networks.html` + `docs/web/graph.js` |
| `designfix` | `docs/web/base.css`, `docs/web/components.css`, `docs/web/companysearch.css`, `tmp/typography.html` |
| `datacleaning` | DB data quality work (scripts, database.json patches) |
| `main` | Merge target only — receives merges from all branches |

**Workflow:** checkout the relevant branch → make changes → commit → merge to `main` → push `main` only.

---

## Routing convention (all pages)

> Spostato in `reference/CONVENZIONI-SITO.md` (testo invariato).
---

## Key decisions (do not revisit without strong reason)

> Spostato in `reference/CONVENZIONI-SITO.md` (testo invariato).
