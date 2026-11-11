# Piano operativo — riorganizzazione in un solo repo e action points

> **Destinatario: l'AI che apre questa sessione.** Questo file è la fonte di verità per guidare Nelson, passo per passo, nella riorganizzazione. Leggilo per intero a inizio sessione, poi segui la sezione 0.
>
> Redatto il 2026-11-10. **Sostituisce** la versione del 2026-11-05 a due repo (privato `manintheloop-lab` + pubblico ripulito), abbandonata dopo la mail di Andrea Borruso del 2026-11-08: la vecchia versione resta recuperabile dal commit locale `c69aa9a` e dal backup di F0.
>
> Fonti: mail di Andrea Borruso del 2026-11-08 («Riorganizzazione Man in the Loop», file `.eml` ricevuto in `inbox/`, da archiviare in `docs/meetings/`, locale); transcript della call del 2026-10-23 (`docs/meetings/`, locale, non su git); verifiche sullo stato reale del 2026-11-10 (sezione 1).
>
> **Log puntuale dei task eseguiti: [`LOG-RIORGANIZZAZIONE.md`](LOG-RIORGANIZZAZIONE.md)** (aggiornato a ogni task).
>
> Stato: **approvato da Davide (conferma di Nelson, 2026-11-10); Andrea è l'autore della linea «un solo repo»; Nelson ha confermato il 2026-11-10 che non c'è nulla da tenere nascosto.** Nessuna fase è ancora iniziata.

---

## 0. Come usare questo file (regole per l'AI)

### 0.1 All'avvio della sessione

1. Leggi questo file, poi la tabella «Stato di avanzamento» in fondo.
2. Trova il **primo task non completato** (colonna Stato ☐ o ◐), in ordine di fase. Non saltare task, non anticipare task distruttivi o verso l'esterno.
3. Riassumi a Nelson in 5-8 righe: dove siamo, qual è il prossimo task, cosa serve da lui. Poi **fermati e aspetta**.
4. Il hook di avvio (`.claude/session-status.sh`) fa `git fetch` e `git pull --ff-only`. Se segnala un branch divergente, **non risolverlo da solo**: riferiscilo e proponi.
5. Se `inbox/` contiene file, proponi dove spostarli (non spostare prima dell'ok).

### 0.2 Come si conduce un task

In quest'ordine:

1. **Annuncia**: obiettivo, cosa farai, cosa tocca (file, GitHub), se è reversibile.
2. Esegui i **controlli preliminari** del task (sola lettura) e mostra il risultato.
3. Se il task ha effetti (scrive, committa, pusha, cancella, tocca GitHub), chiedi il via libera e **aspetta la risposta**. Eccezione: task marcati «sola lettura».
4. Esegui. Poi esegui i **Test** del task e mostra l'esito reale (comandi e output), senza arrotondare.
5. Se un test fallisce: **fermati**, riferisci l'output, non proseguire e non «aggiustare il test». Applica il **Rollback** solo con l'ok di Nelson.
6. Aggiorna **subito**, prima di passare al task successivo: (a) `docs/LOG-RIORGANIZZAZIONE.md` (log puntuale: comandi, esiti dei test, file toccati, deviazioni; regola di Nelson del 2026-11-10); (b) «Stato di avanzamento» e «Registro» qui sotto; (c) il rimando in `STATUS.md`. Proponi il commit; non committare né pushare se non richiesto.

### 0.3 Regole di condotta (vincolanti)

- **Domande → rispondi e fermati.** Se il messaggio di Nelson contiene domande, rispondi e non eseguire nulla. «Voglio che… + domande» è una richiesta di proposta, non un via libera. Nel dubbio è una domanda (regola in `~/.claude/CLAUDE.md`).
- **Testi destinati ad altri** (Davide, Andrea, GitHub, ecc.): sempre in **testo semplice**: niente citazioni `>`, grassetto, corsivo, titoli markdown. Righe vuote tra i paragrafi, elenchi con «(a)», «(b)» o numeri a inizio riga. Le tue note vanno separate dal testo da inviare.
- **Lingua:** italiano, con tutti gli accenti.
- **Regola di Andrea, vale anche per l'AI:** `main` è il sito; **in `main` si entra solo da un branch con una pull request**; mai commit o push diretti su `main` (dopo F0.3).
- **Nessuna azione distruttiva o verso l'esterno senza via libera esplicito nello stesso turno**: push (anche di branch e tag), cancellazione di branch o file, modifiche alle impostazioni GitHub, invio di testi a terzi. Un «ok» per un task non vale per gli altri.
- **No force-push, nessuna riscrittura della storia pubblica** (scelta di Andrea: i vecchi commit restano raggiungibili e si conserva la storia dei dati). Unica eccezione da discutere con Davide e Andrea: esito negativo di G2 (Crunchbase).
- **Prima di cancellare o sovrascrivere, guarda il bersaglio** (`ls`, `git log`, `git diff`) e mostralo.
- **Dry-run per default** per ogni script che scrive su `database.json` o sul repo.
- **`gh` non è installato.** Pull request, merge, impostazioni di Pages, Actions, Discussions e tag sul sito li fa Nelson dall'interfaccia web: dagli istruzioni precise, un passo alla volta. Non installare `gh` senza chiedere.
- **Riferisci i fallimenti con fedeltà**: se un test fallisce o un task viene saltato, dillo con l'output.
- **Non assumere**: se un fatto di questa pagina non coincide con lo stato reale, lo stato reale vince. Segnala la discrepanza e correggi il piano.
- **Segreti:** chiavi API (es. Exa) e token solo in variabili d'ambiente o file ignorati da git; mai nel repo, nei log, nei commit, nei testi inviati. Non stamparli.
- **Percorsi personali:** in questo file e in qualunque file tracciato non scrivere percorsi assoluti della home di nessuno (`/home/…`, `C:\Users\…`).

### 0.4 Cose da NON fare mai

- Non pushare su `main`; non fare `git push --force`/`-f`; non cancellare branch o tag sul remoto senza ok esplicito.
- Non mergiare `v.2026-c` in `main` **prima che il sito sia servito da `docs/`** (F3): contiene `rawdata/sec-edgar/` (dati su persone), che con Pages sulla root andrebbe online subito.
- Non committare `docs/meetings/`, `inbox/`, `SEC/`, `tmp/`, `issues.md`, `status-*.md`, `sitemap.md`, `IRPI-test/`, `Jon_Tassonomia/`, il backup (ignorati o fuori dal repo).
- Non rieseguire gli script «one-time build» (`build_database.py`, `build_edf_entities.py` da zero, `import_startups.py`, `import_by_wikidata.py`).
- Non lanciare `fetch_edf_bulk.py` su `rawdata/edf_calls.json` (sovrascrive e perde progetti): usare `merge_edf_calls.py`.
- Non modificare `../refactoring/` (vecchio DB, sola lettura).
- Non editare `history[]` esistenti nel DB (append-only, vedi `UPDATE_PROTOCOL.md`).
- Non modificare le fasi del sito (F3) mentre altri mergiano su `main`: durante F3 c'è un **congelamento** concordato.

---

## 1. Contesto verificato (al 2026-11-10)

### 1.1 Persone
- **Nelson** (`nelsonmau`): sviluppo e dati; conduce questa riorganizzazione; lavora con Claude Code.
- **Andrea Borruso** (`aborruso`, «Andy»): esperto dati; ha scritto la prima versione di `WORKFLOW.md` (PR #27, mergiata); ha messo al sicuro `v.2026-c` con il tag `sec-2026-10-17`; si occupa del controllo sulla struttura del JSON dentro `validate.py`.
- **Davide Del Monte**: coordinamento, test sui dati SEC/13F; ha confermato il piano; **non ha ancora detto come lavora sul repo** (VS Code, GitHub Desktop, Claude, altro): Andrea lo ha chiesto per scrivere bene `WORKFLOW.md`.

### 1.2 Repo e deploy
- Remote: `origin = git@github.com:infonodesETS/manintheloop.git`, **pubblico**, piano gratuito. `main` = `e14d920` su origin.
- Sito: `https://mitl.infonodes.org/` (file `CNAME` nella root). Pages serve la **root di `main`** (configurazione **non verificata**: `gh` assente e API senza autenticazione dà 404 su `/pages`). Verificato: 6 pagine, `data/last_update.json`, `data/mitl-index.json` rispondono 200.
- Nessuna GitHub Action (`.github/` non esiste). API pubblica: `main` **non protetto**, nessuna regola di protezione, Discussions disattivate, wiki attiva, 7 issue aperte, una sola PR (#27, chiusa), tag remoto unico `sec-2026-10-17`.
- Branch remoti: `main`, `v.2026-c` (`0cfa3af`, 11 commit avanti e 28 indietro rispetto a `main`; contiene `rawdata/sec-edgar/` 178 file, `tmp/sec-test/` 6 file, `docs/dev-v2026c-sec.md`, `scripts/export_labelling_sheets.py`, modifiche a `ROADMAP.md` e `.gitignore`). Merge simulato con `git merge-tree`: **un solo conflitto, `.gitignore`**.
- Branch locali già interamente in `main` (0 commit propri, non su origin): `edf-merge-script`, `edf-update-2026-10`, `nuovi-fondi-eu`, `status-search-keywords`.
- Stato git locale al 2026-11-10: `main` locale = 2 commit avanti (`c69aa9a` piano a due repo, `9a76648` STATUS.md) e 3 indietro (`d79b01a`, `ac98a52`, `e14d920`: solo `WORKFLOW.md`). Divergente: `git pull --ff-only` fallisce. Nessuna sovrapposizione di file.
- Versione mostrata nelle pagine: `Prototype v.2026-b` (7 occorrenze nelle 6 pagine).
- MARLA (chatbot, Vercel `marlamag`) legge `data/mitl-index.json`. URL previsto: `https://infonodesets.github.io/manintheloop/data/mitl-index.json`, che risponde 301 verso `https://mitl.infonodes.org/data/mitl-index.json`. **Questo URL non deve cambiare.** Il valore reale di `MITL_INDEX_URL` su Vercel **non è verificato** (ROADMAP voce 17).
- `data/mitl-index.json` pubblicato: `generato` 2026-08-21 (MARLA risponde su dati vecchi; ROADMAP voce 18). `data/last_update.json` è manuale (`16/06/2026`).
- Dipendenze del sito **fuori dalla futura cartella `docs/`** (trovate con grep): `web/app.js:99` fa `fetch('rawdata/edf_calls.json')` (4,3 MB); `about.html:142` linka `data/qid_candidates.json`. Tutti gli altri riferimenti sono a `web/`, `data/*.json` (`database`, `glossary`, `glossary_terms`, `edf_orgs`, `about_why`, `publications`, `last_update`, `defence_criteria`), `reports/countries/index.html` (usa `../../` verso `web/`, `data/`, `search.html`). Risorsa esterna: `cdn.jsdelivr.net/.../world-atlas@2` (fuori perimetro).
- `reports/countries/italy/index.html`: nessuna pagina del sito lo richiama (grep) → probabile materiale di lavoro (O6).
- Nel repo `docs/` oggi è documentazione tecnica ma Pages serve la root, quindi **anche `docs/*` è online** (`/docs/SCHEMA.md`, `/docs/sintesi.html`, ecc.): dopo F3 quegli URL spariranno.

### 1.3 Contenuto tracciato (circa 48 MB, ~270 file)
`old_version/` 106 file · `beta/` 53 · `scripts/` 36 · `data/` 23 · `docs/` 11 · `web/` 10 · `rawdata/` 9 · `reports/` 6 · `testi/` 2 · `.claude/` 2 · root: 6 pagine, `CNAME`, `ROADMAP.md`, `STATUS.md`, `WORKFLOW.md`, `.gitignore`.
File Crunchbase tracciati: `data/crunchbase_sandbox/` (13 file, più una copia in `beta/`). File più grandi: `data/database.json` 12,9 MB, `beta/data/database.json` 12,1 MB (diverso da quello online), `rawdata/edf_calls.json` 4,3 MB.

### 1.4 Database (`data/database.json`, schema 3.0)
2582 entità, 3490 relazioni (validate.py PASSED il 2026-10-24). `PER-NNNN` previsto ma non popolato.

### 1.5 Dati SEC (branch `v.2026-c`)
161 aziende quotate USA da DEF 14A: 1.601 consiglieri, 994 dirigenti, 571 detentori >5%, 2.298 persone (ID `P0001…` stabili dal commit `991cd7f` di Andrea; l'ordine rispetto al test `4c193e1` non è verificato: B4 lo accerta). `controlli-manuali.csv`: 143 controlli.

### 1.6 Scadenze
- **Release 1** (quote >5% in aziende già nel DB, relazione `ownership`): **2026-11-15** (sabato).
- **Release 2** (persone con ruoli apicali): dal 2026-11-15.

### 1.7 Cartelle locali non su git (da non perdere; coperte dal backup F0.2)
`tmp/` (678 MB, in gran parte `tmp/remotion`), `SEC/`, `IRPI-test/`, `Jon_Tassonomia/`, `inbox/`, `docs/meetings/`, `issues.md`, `status-*.md`, `sitemap.md`, `.playwright-mcp/`, `.claude/settings.local.json`. Totale cartella di lavoro: 775 MB (apparent size); disco: 1,3 TB liberi.

### 1.8 Strumenti disponibili
`ffmpeg`, `node 20`, `curl`, `sha256sum`, Playwright **via MCP** (`mcp__playwright__*`; Playwright per Python non installato), `python3`. `gh` non installato. Server locale: `python3 -m http.server 8001`.

### 1.9 Cosa NON è verificato (da chiudere in F1)
Sorgente e dominio configurati in Settings → Pages (e «Enforce HTTPS»); valore di `MITL_INDEX_URL` su Vercel; termini Crunchbase; se qualcuno ha condiviso link a `/docs/…`, `/beta/…`, `/old_version/…`; come lavora Davide.

---

## 2. Decisioni

| ID | Decisione | Origine |
|---|---|---|
| D1 | **Un solo repo** (`infonodesETS/manintheloop`). Niente `manintheloop-lab`, niente promozione, niente `public-candidate`. | Andrea, 2026-11-08 |
| D2 | `main` è il sito; il lavoro sta su branch; in `main` si entra sempre da un branch con PR; la PR la valuta il primo che la vede (approva chi conosce bene la parte toccata, altrimenti chiede aiuto). | Andrea |
| D3 | **Approvazione obbligatoria dalle impostazioni GitHub: rimandata.** La regola sta in `WORKFLOW.md`. | Andrea |
| D4 | **GitHub Pages dalla cartella `docs/`**: online solo ciò che sta lì dentro. La `docs/` di oggi diventa `reference/`. | Andrea |
| D5 | **Niente force-push, nessuna riscrittura della storia.** | Andrea |
| D6 | `beta/` e `old_version/` escono da `main`; `old_version/` resta raggiungibile con il tag `archivio-2026-06`; si tagga lo stato pubblicato (`v.2026-b`). | Andrea |
| D7 | Cancellare cartelle e branch che hanno finito il loro lavoro. `v.2026-c` **non si tocca** (tag `sec-2026-10-17`). | Andrea |
| D8 | I controlli girano come **GitHub Action sulla PR**. Il test nel browser delle 6 pagine resta manuale (Playwright MCP). | Andrea |
| D9 | Documento «come si lavora» = `WORKFLOW.md` (già scritto da Andrea, da adeguare). `STATUS.md` → ridotto; diario → `CHANGELOG.md`. | Andrea |
| D10 | Verificare i termini Crunchbase prima di tenere i CSV nel repo pubblico. | Andrea |
| D11 | **Nulla da tenere nascosto** → conferma il repo unico. | Nelson, 2026-11-10 |
| D12 | Backup completo prima di ogni modifica, in `~/Coding/infonodes/Manintheloop-backup-2026-11-10/` (fuori dal repo, quindi niente `.gitignore`). | Nelson |
| D13 | Ordine: **`docs/` prima del merge di `v.2026-c`** (altrimenti i dati SEC su persone vanno online). Release 1 si prepara su branch/PR in parallelo. | Claude, da confermare |
| D14 | Passaggio a `docs/` in **due PR (copia prima, rimozione dopo)** per avere zero downtime e rollback immediato. | Claude (safeguard) |
| D15 | Riordino interno degli script in sottocartelle: **rimandato** a dopo la Release 1 (Andrea: «riordinare se serve»). | Claude, da confermare |

### 2.1 Decisioni aperte

| ID | Domanda | Default proposto |
|---|---|---|
| O1 | Chi fonde le PR solo-documenti se Andrea e Davide non rispondono in 24 ore | Nelson, dopo averlo scritto nella PR |
| O2 | Link `about.html:142` a `data/qid_candidates.json` quando il file va in `work/` | Link alla pagina GitHub del file |
| O3 | `web/app.js` legge `rawdata/edf_calls.json`: come | Copia generata in `docs/data/edf_calls.json` da `scripts/sync_site_data.py`; la Action verifica che sia identica |
| O4 | `reports/countries/italy/index.html` e `reports/countries/scripts/analyze_italy.py`: dove | `work/`, salvo prova che il sito li usa |
| O5 | `docs/sintesi.html`, `synthesis-en.html`, `typography.html` oggi online: dove | `typography.html` → `reference/design-system.html`; `sintesi*` → `work/sintesi/`; Davide dice se qualcuno ha condiviso quei link |
| O6 | Dati SEC su persone (`rawdata/sec-edgar/`): si pubblicano nel repo? | Sì nel repo (D11), fuori dal sito (`docs/`) |
| O7 | Licenza e `README.md` | Da scegliere in F6 |
| O8 | Attivare Discussions sul repo per le discussioni di progettazione | Sì, dopo F6 (Andrea) |
| O9 | Dove tenere l'email di Andrea | `docs/meetings/` (locale) |
| O10 | Valore di `MITL_INDEX_URL` e chi gestisce MARLA | Nelson verifica (F0.7) |

---

## 3. Gate

| Gate | Condizione | Blocca |
|---|---|---|
| **G0** | Davide ha confermato; Andrea è l'autore della linea. Registrato il 2026-11-10. | — (soddisfatto) |
| **G1** | Backup creato **e** verificato (C2), prova di ripristino riuscita. | tutto ciò che modifica il repo (da F0.3) |
| **G2** | Termini Crunchbase verificati da una persona; esito nel Registro. Se negativo: si ferma F3 e si discute con Andrea e Davide (i file sono già nella storia). | F3 |
| **G3** | Impostazioni di Pages verificate da Nelson (sorgente, dominio `mitl.infonodes.org`, HTTPS) e annotate; istantanea del sito vivo salvata (F1.3). | F2, F3 |
| **G4** | PR 1 (pulizia) mergiata e verificata sul sito vivo. | F3 |
| **G5** | Congelamento concordato con Davide e Andrea per F3. | F3.2 |
| **G6** | Sito servito da `docs/` e verificato (C9). | F4 B2 (merge di `v.2026-c`) |
| **G7** | Decisioni di schema S1-S7 prese (B1). | B5 |

---

## 4. Test comuni

Ogni task rimanda a questi. Fino a F5 sono script usa-e-getta in `<scratchpad>` (non nel repo); in F5 diventano `scripts/checks/*.py` e girano nella Action. **Ogni controllo va provato anche in negativo**: si pianta un errore in una copia temporanea e si verifica che il test fallisca («test del test»).

| ID | Test | Come | Esito atteso |
|---|---|---|---|
| C1 | `validate.py` | `python3 scripts/validate.py` | `PASSED`; conteggi 2582 entità / 3490 relazioni, salvo task che li cambiano |
| C2 | Backup valido | `sha256sum -c SHA256SUMS`; `git bundle verify …bundle`; `git -C …mirror.git fsck`; ripristino: `git clone …bundle <scratch>/restore` + `validate.py` nel clone; estrazione del tar in `<scratch>/untar` e `diff -rq` con la cartella viva | tutto OK; `diff -rq` vuoto (a parte `.git/index` e file toccati dopo il backup) |
| C3 | Perimetro del cambiamento | `git diff --name-status origin/main...HEAD` confrontato con l'elenco atteso scritto nel task | nessun percorso fuori elenco |
| C4 | Dipendenze chiuse | script che estrae da `*.html` e `web/*.js` i riferimenti locali (`src`, `href`, `fetch('…')`, `import`, `url()` in CSS), li risolve relativamente al file e verifica che esistano nella cartella del sito | 0 mancanti. Negativo: copia con `<script src="web/non-esiste.js">` → deve riportare 1 mancante. **Attenzione:** `fetch()` in un `.js` si risolve rispetto alla pagina (radice), `import './x.js'` rispetto al modulo (provato in F1.4) |
| C5 | Parità con il sito vivo | confronta `snapshot-live-2026-11-10.tsv` (`percorso, status, sha256`) con i file locali serviti (o con il sito vivo dopo uno spostamento) | tutti uguali tranne i percorsi dichiarati nel task; **`CNAME` non è servito da Pages (404): escluderlo dal confronto** |
| C6 | JSON validi | `python3 -I -c` che apre con `json.load` ogni `*.json` della cartella del sito | 0 errori |
| C7 | Segreti e percorsi | `git grep -nIE '/home/[a-z]\|C:\\\\Users\|BEGIN (RSA\|OPENSSH\|EC) PRIVATE KEY\|(api[_-]?key\|secret\|token\|password)\s*[:=]\s*["'"'"'][A-Za-z0-9_-]{16,}'`; più email non in whitelist (`comunicazione@infonodes.org`) | 0 occorrenze nel perimetro del task (baseline F1.6 elenca le preesistenti) |
| C8 | Prova nel browser (Playwright MCP, manuale) | server da `python3 -m http.server 8001` dalla cartella del sito; per ognuna delle 6 pagine + `reports/countries/index.html`: 0 errori in console, 0 risposte 4xx su risorse locali. Specifici: `index.html` almeno un `svg circle`; `search.html?organization=<IN con progetti EDF>` e apertura di un progetto EDF (esercita `edf_calls`); `networks.html` canvas/svg presente; `key-figures.html` e `publications.html` con contenuti non vuoti | tutto OK |
| C9 | Sito vivo | `curl -sIL` su: `/`, le 6 pagine, `data/*.json` pubblicati, `data/mitl-index.json`; `infonodesets.github.io/manintheloop/data/mitl-index.json` (deve fare 301 → 200); poi C5 contro il sito vivo | tutti 200; hash uguali a quelli dichiarati |
| C10 | Indice del chatbot | `build_chat_index.py` su copia temporanea; conteggi soggetti/progetti/relazioni coerenti con `database.json` secondo la regola dello script (si legge in F1.5) | coerente, JSON valido |
| C11 | README dei rawdata | ogni file in `rawdata/` (ricorsivo) compare per nome in un README di fonte con fonte, data, licenza | 0 file senza riga |
| C12 | Smoke degli script | per ogni script: `python3 -I -m py_compile`; per quelli **offline** con `--dry-run`: output prima/dopo il cambio di percorsi e `diff` (ammesse solo differenze nelle stringhe di percorso); per quelli di rete (`enrich_wikidata`, `fetch_wikidata_websites`, `fetch_edf_bulk`, `patch_iv_countries_p159`, `import_investors_crunchbase`, `search_missing_qids`, `sparql_search_qids`, `reprocess_skipped_qids`) solo `py_compile` + grep dei percorsi | nessuna differenza non spiegata |
| C13 | Hook di avvio | `sh .claude/session-status.sh` in tre situazioni su una copia temporanea: pulita, con file modificati, divergente | messaggi corretti, nessun effetto collaterale |

---

## 5. Fasi e task

Legenda dei campi: **Cosa** · **Implementazione** · **Test** · **Rollback** · **Chi/ok**.

### F0 — Rete di sicurezza (prima di qualunque modifica al repo)

**F0.1 — Archiviare l'email di Andrea.**
Cosa: `inbox/` deve restare vuota. Implementazione: `mv "inbox/Riorganizzazione Man in the Loop.eml" docs/meetings/2026-11-08_Borruso_Riorganizzazione.eml`. Test: `ls inbox` vuoto; `ls docs/meetings` mostra il file; `git status` pulito (cartella ignorata). Rollback: rimuovere il file di nuovo in `inbox/`. Ok: Nelson.

**F0.2 — Backup completo.** Cartella: `~/Coding/infonodes/Manintheloop-backup-2026-11-10/` (non è un repo git: verificato; non va mai messa dentro `Manintheloop/`).
Implementazione (nell'ordine):
1. `git bundle create <backup>/manintheloop.bundle --all` (tutti i branch e tag locali, compresi i 2 commit non pushati).
2. `git clone --mirror git@github.com:infonodesETS/manintheloop.git <backup>/manintheloop-mirror.git` (stato del remoto; la sola lettura non modifica GitHub).
3. `tar -czf <backup>/manintheloop-cartella-completa.tar.gz -C ~/Coding/infonodes Manintheloop` (tutto, anche file ignorati e `.git`).
4. `git status --ignored --short > <backup>/ignorati.txt` e `git log --all --oneline > <backup>/log-all.txt`.
5. `cd <backup> && sha256sum manintheloop.bundle manintheloop-cartella-completa.tar.gz > SHA256SUMS`.
6. Snapshot del sito vivo: vedi F1.3 (lo salva qui).
7. Opzionale ma consigliata: copia su disco esterno (il disco di lavoro è lo stesso del backup).
Test: C2 completo. In più: `tar -tzf … | grep -c '^Manintheloop/tmp/'` > 0 (le cartelle ignorate ci sono) e `grep -c 'v.2026-c' log-all.txt` > 0. Gate **G1** a test superati.
Rollback: nessuno necessario (solo creazione di file fuori dal repo). Ok: Nelson prima di partire.

**F0.3 — Allineare `main` locale e spostare il lavoro su un branch.**
Cosa: portare `main` locale = `origin/main`, e il piano/STATUS su un branch `docs/piano-repo-unico` da `origin/main`. I 2 commit vecchi non vanno su GitHub (il piano a due repo è superato e conteneva percorsi personali).
Implementazione: (1) copiare `docs/PIANO-RIORGANIZZAZIONE.md` e `STATUS.md` in `<scratchpad>`; (2) `git branch archivio/locale-2026-11-10 main` (conserva i 2 commit localmente, mai pushato); (3) `git stash -u` solo se serve; `git switch -c docs/piano-repo-unico origin/main`; (4) ricopiare i due file; (5) `git branch -f main origin/main` (da un altro branch).
Test: `git rev-parse main origin/main` uguali; `git log --oneline origin/main..archivio/locale-2026-11-10` mostra esattamente `9a76648` e `c69aa9a`; C3 su `docs/piano-repo-unico`: `git diff --name-status origin/main` = solo `docs/PIANO-RIORGANIZZAZIONE.md` (A) e `STATUS.md` (M); `WORKFLOW.md` presente e uguale a quello di origin (190 righe).
Rollback: `git switch archivio/locale-2026-11-10` ripristina lo stato precedente. Ok: Nelson.

**F0.4 — Freno locale su `main`.**
Cosa: impedire a me (e a un errore di battitura) di pushare su `main`. Implementazione: (a) in `.claude/settings.json` (tracciato) aggiungere `permissions.deny` con `Bash(git push origin main*)`, `Bash(git push --force*)`, `Bash(git push -f*)`, `Bash(git push origin --delete*)`, `Bash(git push origin :*)`; (b) `.git/hooks/pre-push` (non versionato, per-clone) che esce con 1 se uno dei ref locali è `refs/heads/main` e stampa il motivo. Nota: le regole di permesso sono un controllo di pattern, non una garanzia; per questo c'è anche il hook di git.
Test: `echo "refs/heads/main 0000 refs/heads/main 0000" | .git/hooks/pre-push origin x; echo $?` → 1; stesso input con `refs/heads/pulizia/…` → 0; `git push --dry-run origin main` non deve poter andare a buon fine nel flusso reale (provare solo con `--dry-run`). Verificare che il `settings.json` resti JSON valido (`python3 -I -c "import json;json.load(open('.claude/settings.json'))"`).
Rollback: togliere le righe / cancellare l'hook. Ok: Nelson. (La modifica di `.claude/settings.json` entra su GitHub con una PR, non da qui.)

**F0.5 — Annuncio ad Andrea e Davide.** Testo semplice, scritto da me, inviato da Nelson: da ora branch e PR per tutto (anche per l'AI); breve calendario di F2 e F3; richiesta del **congelamento** per F3 (G5); richiesta a Davide di dire come lavora. Test: Nelson conferma di aver inviato; risposta registrata. Rollback: n/a.

**F0.6 — Prima PR (docs-only).** Branch `docs/piano-repo-unico` con questo file riscritto e il rimando aggiornato in `STATUS.md`. Test: C3 (solo i 2 file), C7 sul diff (nessun percorso personale), lettura di Nelson. Nelson apre la PR dal web (compare & pull request), la valuta il primo che la vede (O1 se nessuno risponde in 24 ore). Dopo il merge: Nelson cancella il branch dal bottone nella PR; in locale `git switch main && git pull --ff-only`. Rollback: PR di revert.

**F0.7 — Verifiche di Nelson su GitHub e Vercel (sola lettura, guida passo passo).** (a) Settings → Pages: sorgente (branch/cartella), Custom domain `mitl.infonodes.org`, Enforce HTTPS; annotare. (b) Settings → Branches / Rules: nessuna regola esistente (l'API dice `protected: false`). (c) Settings → Actions: Actions abilitate sul repo. (d) Vercel → progetto `marlamag` → Environment Variables: valore di `MITL_INDEX_URL`; chi gestisce MARLA. (e) Settings → Collaborators: chi ha permesso di scrittura. Esito nel Registro. Gate **G3** parte (a).

### F1 — Verifiche (sola lettura)

**F1.1 — Termini Crunchbase (Nelson o chi indica; G2).** Leggere i termini d'uso/licenza dell'export CSV usato (programma e data dell'export in `data/crunchbase_sandbox/CRUNCHBASE.md`). Esiti: (A) consente la pubblicazione → procedere; (B) la vieta o non è chiaro → **stop a F3**, si discute con Andrea e Davide: togliere i file da `main` non basta perché restano nella storia; l'unica via di rimozione completa sarebbe una riscrittura della storia, in contrasto con D5, e va decisa insieme. Test: esito scritto nel Registro con data, chi, fonte (link).

**F1.2 — Diff `beta/` vs `main`.** Implementazione: per ogni file tracciato in `beta/` confrontarlo con il suo corrispondente nella root (`git ls-files beta | …` e `cmp`), producendo tre liste: identici, diversi, solo in `beta/`. Il file `beta/data/database.json` è già noto come diverso. Nelson decide cosa fare dei diversi/solo-beta: ciò che serve si porta su un branch (`archivio/beta-2026-08`), il resto resta raggiungibile dal tag `v.2026-b`. Test: i tre conteggi sommano al totale dei file di `beta/` (53); la lista è nel Registro (o in file nel backup).

**F1.3 — Istantanea del sito vivo.** Implementazione: script in scratchpad che (i) costruisce l'elenco dei percorsi pubblici attesi = pagine + tutti i riferimenti trovati da C4 + `data/*.json` pubblicati + `rawdata/edf_calls.json` + `reports/countries/index.html` + `CNAME`; (ii) `curl -sL` di ciascuno su `https://mitl.infonodes.org/`; (iii) salva `snapshot-live-2026-11-10.tsv` (`percorso, status, sha256`) nella cartella del backup. Verifica anche che il sito vivo corrisponda a `origin/main`: per ogni percorso, `git show origin/main:<percorso> | sha256sum` = hash vivo. Test: tutti 200; ogni hash vivo = hash di `origin/main` (se no, c'è cache/sorgente diversa da `main`: segnalare, vale per G3). Aggiungere all'istantanea anche una lista di sonda degli URL che spariranno (`/docs/SCHEMA.md`, `/docs/sintesi.html`, `/beta/`, `/old_version/`, `/STATUS.md`, `/rawdata/…`): registra quali oggi rispondono 200.

**F1.4 — Inventario riferimenti del sito (baseline C4).** Eseguire C4 sulla root attuale. Atteso: 0 mancanti; elenco dei riferimenti che escono dal perimetro `docs/` = i 2 noti (`rawdata/edf_calls.json`, `data/qid_candidates.json`). Se ne compaiono altri, il piano si aggiorna prima di F3. Verificare anche O4: `grep -rn "countries/italy" ` nelle pagine (oggi 0).

**F1.5 — Inventario script e percorsi.** Implementazione: per i 36 script trovare *tutti* i modi in cui costruiscono percorsi (`'data/…'`, `os.path.join(RADICE,'data',…)`, `Path(__file__).parent.parent / 'data'`, `'rawdata/…'`, `'docs/…'`); produrre tabella: script · percorso · online/offline · ha `--dry-run`. Questo elenco è l'elenco esatto delle modifiche di F3.5. Punti già noti: `build_chat_index.py` righe 24 e 90 (`RADICE`/`SORGENTE`); `scripts/import_by_wikidata.py` cita `docs/`; molti script usano la stringa `'data/database.json'` (11 occorrenze in 10 script nel grep letterale). Leggere anche la regola di build di `build_chat_index.py` (per C10). Test: ogni script dei 36 compare in tabella; nessuna riga «da verificare».

**F1.6 — Baseline segreti e percorsi (C7).** Eseguire C7 su tutto il tracciato. Attesi: `docs/OPENTENDER-APPALTI.md` (un percorso Windows personale; da ripulire in F3.2 con la `reference/`), `docs/PIANO-RIORGANIZZAZIONE.md` (versione vecchia, già sostituita). Nessun segreto trovato il 2026-11-10. Test: elenco finale vuoto dopo le correzioni di F2/F3.

**F1.7 — Merge di prova di `v.2026-c` (non scrive).** `git merge-tree --write-tree --name-only origin/main origin/v.2026-c`. Atteso: conflitto solo in `.gitignore`. Se cambia (altri commit su `main`/`v.2026-c`), segnalare.

### F2 — PR 1: pulizia, senza spostare nulla (Pages resta sulla root: il sito non rischia nulla)

Prerequisiti: G1, G3, F1.2 chiuso. Branch `pulizia/beta-old-version` da `origin/main` aggiornato.

**F2.1 — Tag sullo stato pubblicato e archivio.** Nomi: `v.2026-b` (come `WORKFLOW.md` §8: la stringa nelle pagine è `Prototype v.2026-b`) sul commit di `origin/main` (da verificare con F1.3: il sito vivo = quel commit) e `archivio-2026-06` sull'ultimo commit che ha toccato `old_version/` (`git log -1 --format=%H -- old_version`). Test: `git ls-tree -r --name-only v.2026-b | grep -c '^beta/'` = 53 e `| grep -c '^old_version/'` = 106 (nello stato pre-pulizia); idem per `archivio-2026-06` su `old_version/`. Il push dei tag è un'azione verso l'esterno: ok esplicito di Nelson. Rollback: `git push origin :refs/tags/<tag>` solo con ok esplicito (i tag non modificano il sito).

**F2.2 — Rimuovere `beta/`.** Implementazione: `git rm -r beta` (commit separato, per poterlo annullare da solo). Test: C3 = solo cancellazioni sotto `beta/` (53); `grep -rn "beta/" index.html search.html networks.html key-figures.html publications.html about.html web/*.js reports/countries/index.html` vuoto; C4 sulla root: 0 mancanti.

**F2.3 — Rimuovere `old_version/`.** Implementazione: `git rm -r old_version` (commit separato). Test: C3 = solo cancellazioni sotto `old_version/` (106); stesso grep di F2.2 con `old_version/`; C4: 0 mancanti.

**F2.4 — Cancellare i 4 branch locali finiti.** Prima: `git branch --merged origin/main` li elenca tutti e 4; `git log origin/main..<branch>` vuoto. Poi `git branch -d` (rifiuta se non fusi). Mostrare l'elenco prima. Test: `git branch` mostra solo `main`, `v.2026-c` e i branch di lavoro correnti. Rollback: i commit sono già in `main`; per un branch: `git branch <nome> <sha>` (gli SHA sono nel backup `log-all.txt`).

**F2.5 — Parità e test locali (prima della PR).** C5 locale: ogni percorso dell'istantanea che non stava in `beta/`/`old_version/` ha lo stesso hash nel working tree; C1; C6; C7 sul diff.

**F2.6 — PR, merge, verifica sul sito vivo.** Nelson apre la PR dal web con la descrizione-modello (cosa, perché, test eseguiti, esito F1.2). Dopo il merge e la ripubblicazione di Pages (1-3 minuti): C9 e C5 contro il sito vivo: tutti i percorsi dell'istantanea (esclusi `/beta/`, `/old_version/`) hanno lo **stesso hash**; `/beta/` e `/old_version/` danno 404 (intenzionale, da annunciare). Gate **G4**. Cancellare il branch dal bottone della PR.
Rollback: PR di revert (`git revert -m 1 <merge>`), oppure `git checkout v.2026-b -- beta old_version` su un branch nuovo e PR.

### F3 — Il sito in `docs/` (due PR: copia, poi rimozione)

Prerequisiti: G2, G3, G4, G5 (congelamento: nessuno mergia su `main` tra F3.2 e F3.9). Decisioni O2, O3, O4, O5 prese.

**F3.1 — Branch.** `struttura/sito-docs-copia` da `main` aggiornato. Test: `git status` pulito, `git log -1` = merge di F2.

**F3.2 — PR 2a, parte 1: `docs/` → `reference/`.** Implementazione: `git mv docs reference` (commit unico, senza altre modifiche; sposta anche `PIANO-RIORGANIZZAZIONE.md`). Subito dopo, nei file di `reference/` correggere i riferimenti interni a `docs/…`, `data/database.json` e simili **solo nel testo** (non cambiano ancora i percorsi reali). Rimuovere il percorso personale da `reference/OPENTENDER-APPALTI.md` (F1.6). Nota: da questo momento gli URL `/docs/*` del sito (ancora servito dalla root) danno 404: previsto. Test: `ls reference | wc -l` = 11 (+ `meetings/` ignorata); `git diff --name-status` = 11 rinomine (R100 o R9x); nessun file in `docs/`.

**F3.3 — PR 2a, parte 2: nuovo `docs/` come copia.** Implementazione (tutto `cp -a`/`git add`, la root resta intatta):
- `docs/CNAME` (copia di `CNAME`), le 6 pagine, `docs/web/` (copia di `web/`), `docs/data/` con **solo** i 9 json pubblicati (`database`, `glossary`, `glossary_terms`, `edf_orgs`, `about_why`, `publications`, `last_update`, `defence_criteria`, `mitl-index`), `docs/reports/countries/index.html` (O4: non `italy/` né gli script), `docs/data/edf_calls.json` (copia di `rawdata/edf_calls.json`, O3).
- Nel nuovo `docs/`: `docs/web/app.js:99` → `fetch('data/edf_calls.json')`; `docs/about.html:142` → link `https://github.com/infonodesETS/manintheloop/blob/main/work/qid_candidates.json` (O2; il file ci sarà dopo F3.9: nel frattempo il link punta a una pagina che non esiste: accettabile solo perché Pages non serve ancora `docs/`).
- File sentinella `docs/pages-switch-check.txt` con un testo univoco (esiste **solo** in `docs/`: se risponde 200 sul sito, Pages serve `docs/`).
- La root (`index.html`, `web/`, `data/`, …) **non si tocca**.
Test: C3 = solo aggiunte sotto `docs/` (+ rinomine di F3.2); C4 su `docs/`: 0 mancanti; C6 su `docs/`; C7 su `docs/`; confronto: per ogni file copiato `cmp` con l'originale, uguali tranne `docs/web/app.js` e `docs/about.html` (differenza = solo le 2 righe cambiate: `diff` lo mostra); C5 con la cartella `docs/` come radice: tutti i percorsi dell'istantanea presenti e con hash uguale tranne `web/app.js`, `about.html` e `data/edf_calls.json` (nuovo, uguale a `rawdata/edf_calls.json`); `docs/data/edf_calls.json` identico a `rawdata/edf_calls.json` (`cmp`).

**F3.4 — Prova nel browser sul `docs/`.** C8 con server da `docs/` (`cd docs && python3 -m http.server 8001`). Specifico per `edf_calls`: aprire un'entità con progetti EDF e verificare in rete che `data/edf_calls.json` risponda 200 e che l'elenco dei progetti si popoli; verificare in console 0 errori. Salvare screenshot in `tmp/playwright/` (ignorata).

**F3.5 — PR 2a: apertura, merge, e poi nulla cambia online.** PR con test in descrizione. Dopo il merge Pages (ancora sulla root) serve ancora la root: verificare con C9/C5 che il sito vivo non è cambiato (stessi hash dell'istantanea, escluse le pagine `/docs/*`) e che `https://mitl.infonodes.org/docs/pages-switch-check.txt` risponde 200 (perché oggi la root contiene la cartella `docs/` con il file). Attenzione: questo 200 non dimostra ancora lo switch; lo dimostra `https://mitl.infonodes.org/pages-switch-check.txt` (senza `/docs/`), che deve dare **404 finché Pages serve la root** e 200 dopo lo switch.

**F3.6 — Switch di Pages (Nelson, Settings → Pages).** Passi: Source «Deploy from a branch» → Branch `main` → cartella **`/docs`** → Save. Attendere la ripubblicazione (controllare in Actions/Pages la build verde). Poi verificare che «Custom domain» resti `mitl.infonodes.org` e «Enforce HTTPS» sia attivo; se il dominio è sparito, reinserirlo (il `CNAME` è già in `docs/`).
Test (C9): `https://mitl.infonodes.org/pages-switch-check.txt` = 200 (ora Pages serve `docs/`); le 6 pagine 200; `data/edf_calls.json` 200; `https://mitl.infonodes.org/rawdata/edf_calls.json` = **404** (non è più servito, voluto); `https://mitl.infonodes.org/docs/…` 404; C5 contro il sito vivo: tutti uguali all'istantanea tranne le 3 differenze dichiarate; `infonodesets.github.io/manintheloop/data/mitl-index.json` → 301 → 200 con lo stesso hash (**MARLA non è toccato**); C8 sul sito vero (le 6 pagine in Playwright).
**Rollback immediato:** Settings → Pages → cartella `/ (root)` → Save. La root è intatta (F3.7 non è ancora mergiata), quindi in 1-3 minuti il sito torna com'era. Annotare nel Registro ora e orario dello switch.

**F3.7 — PR 2b: togliere le copie vecchie dalla root e riordinare.** Branch `struttura/sito-docs-rimozione`. Implementazione:
- `git rm` delle pagine, `web/`, `data/*.json` pubblicati, `reports/countries/index.html`, `CNAME` dalla root (ora solo in `docs/`) e `docs/pages-switch-check.txt` (sentinella).
- `work/`: `git mv data/qid_candidates.json work/qid_candidates.json`; `git mv data/crunchbase_sandbox work/crunchbase`; `reports/countries/italy`, `reports/countries/scripts`, `reports/pdf` → `work/`; `testi` → `work/testi`; (O5) `reference/sintesi.html`, `reference/synthesis-en.html`, `reference/SINTESI-nuova-versione-2026.md`, `reference/OPENTENDER-APPALTI.md` → `work/sintesi/`; `reference/typography.html` → `reference/design-system.html`.
- `rawdata/` resta com'è in questa PR (README per fonte e sottocartelle in F6).
- Percorsi negli script (elenco esatto di F1.5): `data/database.json` → `docs/data/database.json`; `data/mitl-index.json` → `docs/data/mitl-index.json`; `data/crunchbase_sandbox` → `work/crunchbase`; `data/qid_candidates.json` → `work/qid_candidates.json`; `data/edf_orgs.json`, `glossary*.json`, `publications.json`, ecc. → `docs/data/…`. Aggiungere `scripts/sync_site_data.py` (`--check` e `--write`: copia `rawdata/edf_calls.json` → `docs/data/edf_calls.json` e verifica identità) e chiamarlo nella procedura di aggiornamento EDF di `reference/UPDATE_PROTOCOL.md`.
- Testo di `reference/*.md`, `WORKFLOW.md` §6 e `STATUS.md` con i nuovi percorsi.
Test:
1. C3 = solo le cancellazioni/rinomine elencate sopra; nessun file nuovo salvo `scripts/sync_site_data.py` e `reference/…` rinominati.
2. `ls` della root: nessuna pagina, nessun `web/`, nessun `data/`.
3. C4 su `docs/`: 0 mancanti; C6; C7 su tutto il tracciato: lista vuota (F1.6).
4. **Percorsi negli script:** `grep -rnE "['\"]data/" scripts` senza prefisso `docs/` né `work/` → vuoto; C12 prima/dopo: per ogni script offline con `--dry-run` l'output è uguale a quello salvato prima (salvare gli output «prima» sul `main` pulito, in scratchpad); per tutti `py_compile`.
5. C1 (`validate.py`): PASSED, 2582 / 3490. `python3 scripts/sync_site_data.py --check` → OK.
6. C10: `build_chat_index.py` su copia temporanea: scrive in `docs/data/mitl-index.json`, conteggi coerenti; la copia nel repo non cambia (nessun diff inatteso).
7. C8 da `docs/` con il database spostato.
Dopo il merge: Pages (su `docs/`) non dovrebbe cambiare nulla di visibile: C9 + C5 contro il sito vivo = stessi hash di prima (F3.6). Gate **G6**. Cancellare il branch.
Rollback: revert della PR 2b (le copie in `docs/` non sono toccate); lo switch di Pages resta.

**F3.8 — Fine congelamento.** Avvisare Davide e Andrea che si può tornare a lavorare su branch da `main` aggiornato; ricordare i nuovi percorsi. Test: Registro aggiornato.

### F4 — Dati e SEC (Parte B, riscritta per un repo solo)

> B1 può partire **subito e in parallelo** a F2/F3 (è discussione). Ogni lavoro sui dati va su un branch e arriva in `main` con una PR. Dopo F3 i dati stanno in `docs/data/` e i dati grezzi in `rawdata/`.

**Definition of done**

| Task | È fatto quando |
|---|---|
| B1 | S1-S7 decise e annotate nel Registro; diff di `reference/SCHEMA.md` e `validate.py` approvato da Nelson; `validate.py` aggiornato passa |
| B2 | `main` contiene `v.2026-c` (via PR); C1 PASSED; entità invariate a 2582; `tmp/sec-test/` presente; **nessun file SEC servito dal sito**; `docs/` non contiene file SEC |
| B3 | Pilota di 10 casi con esito registrato da una persona (non dall'AI); `validate.py` PASSED; indice rigenerato |
| B4 | `sec-test` rigirato senza errori; elenco dei controlli manuali ancora aperti con conteggio reale |
| B5 | Dry-run approvato; import applicato su branch; C1 PASSED; conteggi coerenti con il report; indice rigenerato (C10); documenti aggiornati. **Consegna entro il 2026-11-15 = PR aperta con dry-run approvato** (il merge segue l'approvazione) |
| B6-B11 | Si definiscono quando si arriva lì, con una proposta approvata da Nelson |

**B1 — Decisioni di schema** (sola lettura + discussione; blocca B5). Leggere `reference/SCHEMA.md`, `reference/UPDATE_PROTOCOL.md`, `git show origin/v.2026-c:docs/dev-v2026c-sec.md`, `git show origin/v.2026-c:tmp/sec-test/test-merge.md` (§4, §11), `scripts/validate.py`. Presentare a Nelson, una alla volta, con opzioni e raccomandazione: S1 prefisso persone (raccomandato `PER-NNNN`, già previsto); S2 tipi di relazione (oggi `investment`, `board_membership`, `edf_participation`; spec `ownership`/`role`; test `board_membership`, `executive_officer`, `shareholder_5pct`); S3 doppie classi di azioni (Alphabet IN-0017/0018, Fox IN-0135/0136, Heico IN-1372/1378, News Corp IN-0250/0251: stesso blocco `sources.sec` su entrambe); S4 dove vivono i dati SEC (dentro `database.json` o staging); S5 storicità (solo attuale o anche `as_of`); S6 gestori (nodi normali o aggregati; BlackRock); S7 vocabolario dei ruoli e dedup persone (CIK, ID stabili). Esito: proposta di diff a `SCHEMA.md` e `validate.py` mostrata, non applicata. Test: ogni S1-S7 ha una riga nel Registro con la scelta; il diff di `validate.py` su un database di prova passa e **fallisce** su una relazione con tipo non ammesso (test del test).

**B2 — Portare `v.2026-c` in `main`** (dopo **G6**). Implementazione: branch `integrate-sec` da `main`; `git merge origin/v.2026-c`; risolvere il conflitto di `.gitignore` **mostrandolo a Nelson**; se `docs/dev-v2026c-sec.md` compare in `docs/` (che ora è il sito) spostarlo in `reference/` prima di committare il merge (git può segnalare un conflitto di rinomina di directory); verificare che `scripts/export_labelling_sheets.py` e `tmp/sec-test/` siano presenti (`git ls-files tmp/sec-test`: era stato aggiunto con `-f`). Test: `git log --oneline main..origin/v.2026-c` vuoto sul branch; C1 PASSED con 2582 entità; `git ls-files docs | grep -i sec` vuoto; **`ls docs`** contiene solo cose del sito; dopo il merge in `main`, `curl -sI https://mitl.infonodes.org/rawdata/sec-edgar/2026-10-17/…` → 404 e `https://mitl.infonodes.org/docs/dev-v2026c-sec.md` → 404 (cioè i dati SEC non sono online). Non toccare `v.2026-c` (resta com'è; Andrea deve riclonare/aggiornarsi). Rollback: revert della PR.

**B3 — Pulizia dei duplicati (metodo Exa di Andrea)** · prerequisito di B5. Leggere `reference/UPDATE_PROTOCOL.md` (merge/retire), `scripts/patch_orange_cb.py`, `controlli-manuali.csv`, ROADMAP voce 16. Casi noti: AMD IN-0006/IN-1249; MP Materials IN-0242/IN-1311; Palantir IN-0282/IN-1318; Alphabet IN-0017/0018 ↔ IN-1247; IBM IN-0062 ↔ IN-1294; probabili filiali Alcoa Warrick IN-1352 e HII Mission Technologies IN-1290; da ROADMAP 16: MBDA España IN-0863, Idv Defence Vehicles Italia IN-1431 = duplicato di Iveco Defence Vehicles IN-0803, Telecom Italia, Fincantieri. Procedura: chiave Exa (Nelson, solo in variabile d'ambiente); pilota su 10 casi con evidenze (URL e frase) in un CSV; **l'esito lo registra una persona**; errori del pilota mostrati prima di estendere; applicazione con `scripts/patch_duplicati_*.py` e `--dry-run`, un caso alla volta; `validate.py` dopo ogni gruppo; indice rigenerato. Test per ogni patch: dry-run mostra esattamente le modifiche attese; C1; le relazioni migrate puntano al canonico (query su `database.json`); l'entità ritirata ha `entity_retired` e `history[]` append-only (il vecchio contenuto di `history` è prefisso del nuovo); il conteggio entità attive cala di quanto previsto.

**B4 — Rilanciare `sec-test` e chiudere i controlli manuali** (dopo B2). Dalla radice: `python3 -I tmp/sec-test/join_aziende.py`, `python3 -I tmp/sec-test/build_sec_test.py`, server su 8001 e `http://localhost:8001/tmp/sec-test/`. Verificare coerenza degli ID stabili (`P####` → `PER-T####`). Contare quanti dei 143 controlli sono davvero senza `esito`. Test: i due script terminano con exit 0; nessun file scritto fuori da `tmp/sec-test/` (`git status` pulito al di fuori); il conteggio dei controlli aperti è un numero calcolato dal CSV, non assunto.

**B5 — Import Release 1 (quote >5%)** · scadenza 2026-11-15. Prerequisiti: G7, B2, B3 sui casi SEC. Implementazione: `scripts/import_sec_ownership.py` (`--dry-run`, re-run safe, nessun ID rigenerato) che legge `rawdata/sec-edgar/2026-10-17/detentori-oltre-5.csv`, `entita.csv`, `controlli-manuali.csv`, aggancia le aziende (ETF + ticker iShares, CIK per le doppie classi), crea o riusa i gestori IV secondo S6 (BlackRock = IV-0077, JPMorgan IV-0324, Morgan Stanley IV-0393, Invesco IV-0719, Vanguard assente), crea le relazioni secondo S2, aggiunge `sources.sec`. Percentuali vuote = «sotto l'1%», non zero. Test: (1) dry-run: report con entità create, relazioni, gestori riconosciuti, mostrato a Nelson; (2) applicazione su copia temporanea del database: **seconda esecuzione = 0 modifiche** (idempotenza); (3) conteggi = report; (4) C1 con `validate.py` esteso; (5) campione di 10 relazioni controllate a mano contro il CSV; (6) C10; (7) aggiornare `reference/DATABASE-E-DATI.md` e `CHANGELOG`/`STATUS`; (8) PR con il report allegato. Solo con l'ok di Nelson si applica sul branch e si apre la PR.

**B6-B11** — come nel piano precedente (Release 2 persone con ruoli apicali, equivalenti europei SEC, finanziamenti EU oltre EDF, aggregazione per gruppi, controllo struttura DB di Andrea, minori): si dettagliano quando si arriva lì, con una proposta approvata da Nelson.

### F5 — Controlli automatici (GitHub Action sulla PR)

Prerequisito: F3 chiuso. Branch `ci/controlli-pr`. Cosa: `.github/workflows/check-pr.yml` con trigger `pull_request` verso `main`; scripts in `scripts/checks/`. Task:

**F5.1 — `check_site_refs.py` (C4).** Su `docs/`. Test: sul repo pulito → verde; in una copia con riferimento rotto → rosso.
**F5.2 — `check_site_clean.py`.** In `docs/` ci sono solo: `CNAME`, le 6 pagine, `web/`, `data/`, `reports/`; in `docs/data/` solo i json dell'elenco ammesso (lista nello script). Test: aggiungere `docs/prova.md` → rosso.
**F5.3 — `check_secrets_paths.py` (C7).** Test: aggiungere in una copia `/home/x/y` → rosso; whitelist `comunicazione@infonodes.org` → verde.
**F5.4 — `check_index.py` (C10).** Indice coerente con `database.json`. Test: alterare un conteggio → rosso.
**F5.5 — `check_rawdata_readme.py` (C11).** Test: file in `rawdata/` senza riga → rosso.
**F5.6 — `check_edf_copy.py`.** `docs/data/edf_calls.json` identico a `rawdata/edf_calls.json`. Test: modificare un byte → rosso.
**F5.7 — `validate.py`** con il controllo di struttura JSON di Andrea (Andrea lo scrive; qui si integra e si prova).
**F5.8 — Workflow.** Passi: `actions/checkout`, `actions/setup-python` (versioni da verificare e fissare al momento: non ho verificato quali siano oggi le ultime), poi `python3 scripts/validate.py` e `python3 scripts/checks/run_all.py`. Nessun segreto.
Test dell'intera Action: aprire una PR di prova (draft) con un errore volontario (riferimento rotto) → la Action deve risultare **rossa** e indicare il file; correggere → **verde**; chiudere la PR di prova e cancellare il branch. Registrare i link alle esecuzioni nel Registro. Nota: finché non esiste, `WORKFLOW.md` §4 («i controlli girano a ogni PR») non è vero: dirlo nella PR.

### F6 — Documenti, hook, riordino

**F6.1 — `WORKFLOW.md` (con Andrea).** Aggiornamenti proposti: §6 `docs/` deciso (non «in discussione»); §4 i controlli reali (elenco F5); §7 aggiungere gli strumenti di Davide quando risponde; una riga: l'assistente AI non pusha su `main` e lavora sempre su un branch; §8 tag `v.2026-b` già fatto; §9 `python3 -m http.server 8001` va lanciato da `docs/`; §10 invariato. Test: lettura di Andrea; i comandi citati sono provati (`cd docs && python3 -m http.server 8001`).
**F6.2 — `README.md`** (cosa è il progetto, come si avvia in locale, dove sono le cose, i quattro punti di Andrea: cosa è online, da dove vengono i dati, come si trasformano, come si lavora). Licenza (O7).
**F6.3 — `CHANGELOG.md` e riduzione di `STATUS.md`.** `STATUS.md` → solo «punto di ripartenza» (rimando a questo piano e a `CHANGELOG.md`); il «Scripts reference» → `reference/scripts.md`; le regole dello schema → già in `reference/SCHEMA.md`; il diario delle sessioni → `CHANGELOG.md` con **una riga per cosa fatta**. Test: nessuna informazione operativa persa (confronto per sezione con la versione precedente, che resta nel git); nessun link rotto (`grep` dei riferimenti a `STATUS.md`).
**F6.4 — `rawdata/` ordinato.** Sottocartelle per fonte (`edf/`, `ishares/`, `crunchbase/`, `sec-edgar/`), ognuna con `README.md` (fonte, data, licenza); script aggiornati (stesso test di F3.7 punto 4). Test: C11 verde; C12.
**F6.5 — Hook di avvio** (`.claude/session-status.sh`): stampa il rimando a questo piano e la prima riga con ☐/◐ della tabella; il `git pull --ff-only` resta; se il branch corrente non è `main`, non tenta il pull. Test C13: tre scenari su copia temporanea.
**F6.6 — Riordino degli script in sottocartelle** (opzionale, D15; dopo la Release 1). Se si fa: un PR a sé; **sposta un livello** (`Path(__file__).parent.parent` diventa `.parent.parent.parent`); `import` fra script (c'è `from parse_ishares import …`) da sistemare; una cartella chiamata `import/` non è importabile da Python (valutare `ingest/`). Test: C12 completo prima/dopo.
**F6.7 — Discussions.** Nelson attiva «Discussions» nelle impostazioni del repo se il gruppo lo conferma (O8). Nessun test tecnico; verificare che la scheda compaia.
**F6.8 — Pulizia locale.** Dopo conferma finale: i branch `archivio/*` locali si cancellano solo con ok; il backup si conserva per almeno 30 giorni.

---

## 6. Mappa di rollback

| Se… | Si fa… | Tempo |
|---|---|---|
| Il sito si rompe dopo lo switch (F3.6) | Settings → Pages → cartella `/ (root)` → Save (la root è intatta fino a F3.7) | 1-3 minuti |
| Si rompe dopo F3.7 | Revert della PR 2b; se serve, Pages di nuovo su root dopo revert anche di 2a | pochi minuti + PR |
| Una PR sbagliata è già in `main` | Revert della PR con una nuova PR; mai force-push | pochi minuti |
| Si perde un file locale non tracciato | Dal tar del backup (F0.2) | minuti |
| Un branch/tag cancellato per errore | Dagli SHA in `log-all.txt` e dal bundle | minuti |
| Il merge SEC (B2) mette online dati sbagliati | Revert della PR e invalidazione cache: i file non sono sotto `docs/` quindi non dovrebbe succedere (test B2) | — |
| Il formato di un dato cambia per errore | `git revert` della PR di dati; il database in `v.2026-b` e nel backup è la copia di riferimento | minuti |

---

## 7. Calendario indicativo (oggi lunedì 2026-11-10; 2026-11-15 è sabato)

| Giorno | Cosa |
|---|---|
| lun 10/11 | F0 completa (backup, allineamento, freno, annuncio); PR del piano (F0.6); B1 comincia a parte |
| mar 11/11 | F0.7, F1 intera; F2 (PR 1) aperta |
| mer 12/11 | F2 mergiata e verificata; congelamento; F3.1-F3.5 |
| gio 13/11 | F3.6 switch di Pages (mai in una giornata senza margine); F3.7 |
| ven 14/11 | F3 chiusa → B2, B4, dry-run di B5 |
| sab 15/11 | scadenza Release 1: PR aperta con dry-run approvato |

Il calendario dipende da: G2 (termini Crunchbase), risposte di Andrea e Davide, chiave Exa per B3, decisioni B1. **Se F3 slitta, B5 si prepara comunque su un branch** e si consegna come PR aperta; non va mai direttamente su `main` e B2 non si fa prima di G6.

---

## Stato di avanzamento (l'AI aggiorna questa tabella)

Legenda: ☐ da fare · ◐ in corso · ☑ fatto · ✖ bloccato (motivo nelle note).

| Task | Descrizione | Stato | Data | Note |
|---|---|---|---|---|
| G0 | Davide conferma; Andrea autore della linea | ☑ | 2026-11-10 | conferma di Nelson in sessione |
| F0.1 | Archiviare l'email di Andrea | ☑ | 2026-11-10 | eseguito dopo F0.2 per includere `inbox/` nel backup; ora in `docs/meetings/2026-11-08_Borruso_Riorganizzazione.eml` |
| F0.2 | Backup completo + prova di ripristino (G1) | ☑ | 2026-11-10 | `~/Coding/infonodes/Manintheloop-backup-2026-11-10/` (329 MB); C2 superato; copia su disco esterno **non ancora fatta** |
| F0.3 | Allineare `main`, branch `docs/piano-repo-unico` | ☑ | 2026-11-10 | `main` = `origin/main` = `e14d920`; i 2 commit vecchi sono su `archivio/locale-2026-11-10` (mai pushato); upstream del nuovo branch **rimosso** (altrimenti `git push` andrebbe su `main`); `stash@{0}` conservato come rete di sicurezza |
| F0.4 | Freno locale su `main` | ☑ | 2026-11-10 | `.git/hooks/pre-push` (locale, non versionato) + 7 regole `deny` in `.claude/settings.json` (da portare su `main` con una PR: è la modifica non committata sul branch). Le regole `deny` non sono state provate in modo diretto (nessun push tentato) |
| F0.5 | Annuncio ad Andrea e Davide | ☑ | 2026-11-10 | comunicazione completata da Nelson con testo proprio (contenuto non riportato qui); considerata conclusa da Nelson |
| F0.6 | PR del piano | ☑ | 2026-11-10 | PR #28 mergiata da Nelson (`2e6ae14`); branch cancellato; `main` locale allineato |
| F0.7 | Verifiche di Nelson su GitHub/Vercel | ◐ | 2026-11-10 | (a) **fatto**: Pages = Deploy from a branch, `main`, `/ (root)`, dominio `mitl.infonodes.org`, HTTPS attivo, «DNS Check in Progress» (transitorio, DNS verificato). Restano (b) regole, (c) Actions, (d) Vercel (lo guarda Davide), (e) collaboratori e ruolo |
| F1.1 | Termini Crunchbase (G2) | ◐ | 2026-11-10 | esito «incerto, tendente a consentito» deciso da Nelson; sbloccato con riserva; verifica di dettaglio da fare (vedi LOG) |
| F1.2 | Diff `beta/` vs `main` | ☑ | 2026-11-10 | 0 file solo in `beta/`; 6 CSV differiscono solo per fine-riga; 8 file sono versioni più vecchie. Si può rimuovere (tag `v.2026-b`) |
| F1.3 | Istantanea del sito vivo | ☑ | 2026-11-10 | 29 percorsi, 28 con hash = `origin/main`; `CNAME` non servito (normale). Sonda: oggi online anche script, note, rawdata, Crunchbase. G3 soddisfatto |
| F1.4 | Baseline dipendenze del sito | ☑ | 2026-11-10 | 0 mancanti; 2 riferimenti fuori perimetro (`data/qid_candidates.json`, `rawdata/edf_calls.json`); `italy/` non referenziato; script C4 provato in negativo |
| F1.5 | Inventario script e percorsi | ☑ | 2026-11-10 | 36 script: 8 di rete, 27 con dry-run; 8 usano percorsi relativi alla cwd; destinazioni esatte nel LOG |
| F1.6 | Baseline segreti e percorsi | ☑ | 2026-11-10 | 1 solo problema reale: percorso Windows personale in `docs/OPENTENDER-APPALTI.md:181`; nessun segreto |
| F1.7 | Merge di prova di `v.2026-c` | ☑ | 2026-11-10 | 1 solo conflitto (`.gitignore`) |
| F2.1 | Tag `v.2026-b`, `archivio-2026-06` | ☑ | 2026-11-10 | creati **in locale** (non pushati): `v.2026-b`=`2e6ae14` (53 `beta/`, 106 `old_version/`), `archivio-2026-06`=`5e9b411` (106). Push in attesa di ok |
| F2.2 | Rimuovere `beta/` | ☑ | 2026-11-10 | commit `f5b8024`: 53 sole cancellazioni; grep riferimenti vuoto |
| F2.3 | Rimuovere `old_version/` | ☑ | 2026-11-10 | commit `6b0237c`: 106 sole cancellazioni; restano 71 file **non tracciati** in locale (vedi LOG) |
| F2.4 | Cancellare 4 branch locali finiti | ☑ | 2026-11-10 | `git branch -d` su `edf-merge-script` (be975c4), `edf-update-2026-10` (e6050b7), `nuovi-fondi-eu` (53cfd50), `status-search-keywords` (22eaffe); tutti con 0 commit oltre `origin/main` |
| F2.5 | Test locali di parità | ☑ | 2026-11-10 | 28/28 percorsi dell'istantanea con hash uguale; C4 0 mancanti; `validate.py` 2582/3490 |
| F2.6 | PR 1, merge, verifica sul sito (G4) | ☑ | 2026-11-10 | PR #29 mergiata da Nelson (`f4edd71`); sito vivo: 28/28 hash uguali, `/beta/` e `/old_version/` 404. **G4 soddisfatto** |
| F3.1 | Branch `struttura/sito-docs-copia` | ☑ | 2026-11-10 | creato da `main` + 1 commit di log |
| F3.2 | `docs/` → `reference/` | ☑ | 2026-11-10 | 12 rinomine R100 (`63aa00d`); riferimenti testuali; tolto percorso personale |
| F3.3 | Nuovo `docs/` come copia | ☑ | 2026-11-10 | 29 file; `cmp` ok salvo le 2 righe volute; C4 0 mancanti; JSON validi |
| F3.4 | Prova nel browser su `docs/` | ☑ | 2026-11-10 | 8 pagine, 0 errori; `loadEdf()` è codice morto (vedi LOG) |
| F3.5 | PR 2a mergiata | ☑ | 2026-11-10 | PR #30 mergiata (`f318bb1`); sito vivo: 28/28 hash uguali, `/docs/pages-switch-check.txt` 200, `/pages-switch-check.txt` 404, `/docs/SCHEMA.md` 404 |
| F3.6 | Switch di Pages + verifiche | ☑ | 2026-11-10 | Pages su `main` `/docs` (Nelson, account `infonodes`, ~11:00); sentinella in root 200, `rawdata/` 404, `/docs/` 404, 6 pagine 200, `mitl-index.json` 200 su dominio e su `infonodesets.github.io` (301), cert fino al 2026-12-21; 24 hash ok + 4 differenze attese |
| F3.7 | PR 2b: rimozione copie e riordino | ☑ | 2026-11-10 | PR #31 mergiata (`f21ca8c`); sito vivo = `docs/` (27/27 hash uguali, sentinella in root 404, 6 pagine e dati 200, `mitl-index.json` 200). **G6 soddisfatto** |
| F3.8 | Fine congelamento | ☑ | 2026-11-10 | chiuso da Nelson; testo preparato da me (fine congelamento, nuovi percorsi, URL che spariscono); invio e contenuto effettivo non verificati da me |
| B1 | Decisioni di schema S1-S7 (G7) | ◐ | 2026-11-11 | S1 ☑ (`PER-NNNN` + `P####` in `sources.sec`; `validate.py` a `\d{4,}` da applicare). S2 ☑ opzione (a) (`ownership` + `role`), confermata con un «sì» riferito da Nelson. Restano S3-S7 |
| B2 | `v.2026-c` in `main` | ☐ | | dopo G6 |
| B3 | Pulizia duplicati | ☐ | | serve chiave Exa |
| B4 | `sec-test` e controlli manuali | ☐ | | |
| B5 | Import Release 1 | ☐ | | scadenza 2026-11-15 |
| B6-B11 | Release 2 e altri | ☐ | | |
| F5.1-F5.8 | Controlli automatici + Action | ☐ | | |
| F6.1-F6.8 | Documenti, hook, riordino | ☐ | | |

## Registro (l'AI aggiunge una riga per ogni evento rilevante)

| Data | Evento | SHA / riferimenti |
|---|---|---|
| 2026-11-08 | Mail di Andrea Borruso (cc Davide): un solo repo, `main` = sito, PR sempre, Pages da `docs/`, no force-push, controlli come Action, proposta di struttura delle cartelle. | file `.eml` in `inbox/` |
| 2026-11-10 | Nelson: Davide conferma; si segue la linea di Andrea; nulla da nascondere; backup in `~/Coding/infonodes/`; lavora con Claude. | — |
| 2026-11-10 | Verifiche in sola lettura: sito 200 (6 pagine + json); indice generato 2026-08-21; `main` non protetto, nessuna Action, Discussions off, 7 issue, 1 PR (#27); 4 branch locali interamente in `main`; `v.2026-c` 11 avanti/28 indietro, merge simulato con 1 conflitto (`.gitignore`); `web/app.js:99` e `about.html:142` dipendono da file fuori da `docs/`; `main` locale divergente da origin (2 avanti, 3 indietro); nessun segreto nel tracciato. | `e14d920`, `9a76648`, `c69aa9a` |
| 2026-11-10 | Piano riscritto per repo unico (questo file). Vecchia versione a due repo: `c69aa9a`. | — |
| 2026-11-10 | **F0.2 backup eseguito e verificato (G1).** Contenuto: `manintheloop.bundle` (21 MB; 6 branch locali, `origin/*`, tag `sec-2026-10-17`), `manintheloop-mirror.git` (main `e14d920`, `v.2026-c` `0cfa3af`, `refs/pull/27`, tag), `manintheloop-cartella-completa.tar.gz` (298 MB, 26.963 voci, include `tmp/`, `inbox/`, `.git`), `SHA256SUMS`, `log-all.txt`, `ignorati.txt`, `modifiche-non-committate.txt`, `sha-riferimento.txt`. Test C2: `sha256sum -c` OK; `git bundle verify` OK; `git fsck` del mirror senza errori; clone dal bundle → `validate.py` PASSED (2582 entità, 3490 relazioni); estrazione del tar e `diff -rq` con la cartella viva: nessuna differenza. Il bundle non contiene le modifiche non committate (`STATUS.md`, questo file): sono nel tar. | `e14d920`, `9a76648` |
| 2026-11-10 | F0.1: email di Andrea spostata da `inbox/` a `docs/meetings/`; `inbox/` vuota. | — |
| 2026-11-10 | **F0.3 eseguito.** Copie dei 2 file salvate e verificate con sha256 prima di toccare i branch; `git branch archivio/locale-2026-11-10 main`; `git stash push`; `git switch -c docs/piano-repo-unico origin/main`; `git branch --unset-upstream`; file ricopiati; `git branch -f main origin/main`. Test: `main` e `origin/main` stesso SHA `e14d920`; `git log origin/main..archivio/locale-2026-11-10` = `9a76648`, `c69aa9a`; `git diff --name-status origin/main` = `M STATUS.md`, `A docs/PIANO-RIORGANIZZAZIONE.md`; `WORKFLOW.md` identico a origin. | `e14d920` |
| 2026-11-10 | **F0.4 eseguito.** Nessun hook git preesistente e `core.hooksPath` non impostato. Creato `.git/hooks/pre-push` (esce con 1 se il ref locale o remoto è `refs/heads/main`). Test con input simulato su stdin: main→main exit 1; branch di lavoro exit 0; cancellazione di `refs/heads/main` exit 1; branch locale→`refs/heads/main` remoto exit 1. `.claude/settings.json`: aggiunto `permissions.deny` (7 regole), JSON valido, hook `SessionStart` intatto. | — |
| 2026-11-10 | **F0.5 parziale.** Nelson ha inviato ad Andrea e Davide un avviso breve («procedo così»; a Davide: niente modifiche su GitHub in questi giorni; «vi avviso quando ho finito»). Dettagli rimandati alla fine. Congelamento in atto, senza date. Dettaglio nel LOG. | — |
| 2026-11-10 | **F0.6 chiuso.** PR #28 fusa da Nelson (merge commit `2e6ae14`, 4 file). `main` locale allineato con `--ff-only`. Sito online invariato. Osservazione: `/docs/PIANO-RIORGANIZZAZIONE.md` risponde 200 online ⇒ Pages serve la root di `main` (da confermare in Settings, F0.7a). | `2e6ae14` |
| 2026-11-10 | **F0.7a Pages verificato** da screenshot di Nelson: Source «Deploy from a branch», branch `main`, cartella `/ (root)`; dominio `mitl.infonodes.org`; Enforce HTTPS attivo; stato «DNS Check in Progress». Controlli miei: CNAME → `infonodesets.github.io`, A = IP di Pages, certificato valido fino al 2026-12-21, http→https 301. Conferma l'ipotesi del piano (Pages sulla root di `main`). Restano F0.7 (b)-(e). | — |
| 2026-11-10 | **F1.2-F1.7 eseguiti (sola lettura).** `beta/`: nulla di esclusivo (39 identici, 14 diversi di cui 6 solo fine-riga e 8 più vecchi). Istantanea del sito: 28/29 hash = `origin/main` (G3 soddisfatto). C4: 0 mancanti, 2 riferimenti fuori da `docs/`. Script: 8 usano percorsi relativi alla cwd; destinazioni esatte registrate. C7: un percorso personale reale (`docs/OPENTENDER-APPALTI.md:181`). Merge di prova SEC: 1 conflitto (`.gitignore`). Dettagli nel LOG. | `2e6ae14` |
| 2026-11-11 | `MITL_INDEX_URL`: Davide indica `https://infonodesets.github.io/manintheloop/data/mitl-index.json` (valore non leggibile su Vercel, variabile sensibile). Verificato: 301 → 200, hash = `docs/data/mitl-index.json`. Chiuso con riserva (O10). | — |
| | | |
