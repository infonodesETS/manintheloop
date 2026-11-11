# Log puntuale della riorganizzazione

> Diario operativo di **tutto** ciò che viene eseguito per il piano in [`PIANO-RIORGANIZZAZIONE.md`](PIANO-RIORGANIZZAZIONE.md). Una voce per task: cosa è stato fatto, comandi, esito dei test, file toccati, deviazioni dal piano.
>
> **Regola (Nelson, 2026-11-10):** questo file si aggiorna **a ogni task**, subito dopo i test e prima di passare al task successivo. Se un task fallisce o viene saltato, si scrive anche quello, con l'output. Non si cancellano voci: si aggiunge una voce di correzione.
>
> Il «Registro» in fondo al piano resta la sintesi; qui sta il dettaglio. Percorsi: `<backup>` = `~/Coding/infonodes/Manintheloop-backup-2026-11-10/`; `<scratch>` = cartella temporanea di sessione (fuori dal repo).
>
> Orari: indicati solo dove noti (data/ora dei file); altrimenti solo la data. Fuso locale.

## Stato in sintesi

| Task | Stato | Data |
|---|---|---|
| Analisi preliminare (sola lettura) | ☑ | 2026-11-10 |
| F0.2 Backup completo (G1) | ☑ | 2026-11-10 |
| F0.1 Email di Andrea archiviata | ☑ | 2026-11-10 |
| F0.3 `main` allineato, branch del piano | ☑ | 2026-11-10 |
| F0.4 Freno locale su `main` | ☑ | 2026-11-10 |
| Creazione di questo log | ☑ | 2026-11-10 |
| F0.5 Annuncio ad Andrea e Davide | ◐ avviso breve inviato (congelamento); dettagli da inviare alla fine | 2026-11-10 |
| F0.6 PR del piano | ☑ PR #28 mergiata (`2e6ae14`) | 2026-11-10 |
| F1.2-F1.7 Verifiche in sola lettura (tutte tranne F1.1) | ☑ | 2026-11-10 |
| F1.1 Termini Crunchbase (Nelson) | ☐ | |
| F0.7 Verifiche di Nelson su GitHub/Vercel | ◐ (a) Pages fatto; (b) regole, (c) Actions, (d) Vercel, (e) collaboratori ancora da fare | 2026-11-10 |

---

## Voci

### 2026-11-10 — Analisi preliminare (sola lettura)

- **Cosa:** lettura di `STATUS.md`, del piano a due repo del 2026-11-05, della mail di Andrea Borruso (`.eml` in `inbox/`), di `WORKFLOW.md` di `origin/main`; verifica dello stato reale. Nessun file modificato.
- **Comandi/controlli:** `git status`/`git log` (locale vs origin); `git ls-remote` (tag e branch remoti); `git branch --merged`; `git merge-tree --write-tree` (merge simulato di `v.2026-c`); `git ls-files`; `du`/`df`; `curl -sIL` su 6 pagine e json del sito; API pubblica GitHub via `curl` (repo, branch protetto, PR); grep dei riferimenti locali in pagine e `web/*.js`; grep di percorsi e segreti nel tracciato; lettura Parte B del piano.
- **Esito (fatti verificati):**
  - Sito: tutte le URL controllate rispondono 200; `mitl-index.json` con `generato` 2026-08-21.
  - `main` locale divergente da origin (2 avanti: `c69aa9a`, `9a76648`; 3 indietro: `d79b01a`, `ac98a52`, `e14d920`, solo `WORKFLOW.md`).
  - `main` non protetto; nessuna GitHub Action; Discussions off; una sola PR (#27, chiusa); tag remoto unico `sec-2026-10-17`.
  - I 4 branch locali (`edf-merge-script`, `edf-update-2026-10`, `nuovi-fondi-eu`, `status-search-keywords`) sono interamente in `main`, non su origin.
  - `v.2026-c`: 11 commit avanti, 28 indietro; merge simulato: 1 solo conflitto (`.gitignore`); aggiunge `rawdata/sec-edgar/` (178 file), `tmp/sec-test/`, `docs/dev-v2026c-sec.md`, `scripts/export_labelling_sheets.py`.
  - Dipendenze del sito fuori dalla futura `docs/`: `web/app.js:99` (`rawdata/edf_calls.json`) e `about.html:142` (`data/qid_candidates.json`).
  - Nessun segreto nel tracciato; due percorsi personali (in `docs/OPENTENDER-APPALTI.md` e nel vecchio piano).
  - `gh` non installato; `~/Coding/infonodes/` non è un repo git.
- **Non verificato:** sorgente di Pages, `MITL_INDEX_URL` su Vercel, termini Crunchbase, modo di lavoro di Davide.
- **Decisioni di Nelson raccolte in sessione:** Davide conferma; si segue la linea di Andrea (un solo repo); nulla da nascondere; backup in `~/Coding/infonodes/`; si lavora con Claude; l'ordine delle fasi lo valuta l'AI seguendo Andrea; massima cautela.

### 2026-11-10 — Stesura del piano (locale)

- **Cosa:** riscrittura di `docs/PIANO-RIORGANIZZAZIONE.md` per il repo unico (431 righe: regole, contesto, decisioni D1-D15, aperte O1-O10, gate G0-G7, test C1-C13, fasi F0-F6, rollback, calendario, tabella di avanzamento, registro). Aggiornato il rimando in `STATUS.md`.
- **File toccati:** `docs/PIANO-RIORGANIZZAZIONE.md` (riscritto), `STATUS.md` (sezione «PIANO IN CORSO»).
- **Test:** lettura di coerenza; grep di percorsi personali nel piano: 2 corrispondenze, entrambe il testo del pattern del test C7 (non percorsi reali).
- **Nota:** il test C7, applicato al piano stesso, lo segnala per via del pattern scritto; da escludere il file o riformulare il pattern quando C7 diventa script (F5.3).

### 2026-11-10 — F0.2 Backup completo (G1) ☑

- **Deviazione dall'ordine del piano:** eseguito **prima** di F0.1, perché l'archivio catturasse anche `inbox/` com'era.
- **Cosa:** cartella `<backup>` creata (non esisteva: controllato); contenuto:
  1. `manintheloop.bundle` ← `git bundle create … --all` (21 MB).
  2. `manintheloop-mirror.git` ← `git clone --mirror git@github.com:infonodesETS/manintheloop.git` (sola lettura su GitHub).
  3. `manintheloop-cartella-completa.tar.gz` ← `tar -czf` della cartella `Manintheloop` (298 MB; 26.963 voci).
  4. `log-all.txt` (`git log --all --oneline`), `ignorati.txt` (`git status --ignored --short`), `modifiche-non-committate.txt`, `sha-riferimento.txt` (HEAD, main, origin/main).
  5. `SHA256SUMS` (bundle e tar).
- **Test (C2):**
  - `git bundle verify` → «The bundle records a complete history».
  - `sha256sum -c SHA256SUMS` → bundle OK, tar OK.
  - `git fsck` sul mirror → nessun errore; riferimenti del mirror: `main` `e14d920`, `v.2026-c` `0cfa3af`, `refs/pull/27/head` `d79b01a`, tag `sec-2026-10-17`.
  - Tar: contiene `tmp/` (22.821 voci), `inbox/` (2), `.git/` (3.338 voci).
  - Ripristino: clone dal bundle in `<scratch>/restore` (508 commit) → `python3 scripts/validate.py` → exit 0, «VALIDATION PASSED», 2582 entità, 3490 relazioni.
  - Estrazione del tar in `<scratch>/untar` e `diff -rq` con la cartella viva → nessuna differenza.
  - Bundle: contiene i 6 branch locali, `origin/*`, il tag; **non** contiene le modifiche non committate (`STATUS.md`, piano) → sono nel tar.
  - Cartelle di prova in `<scratch>` rimosse.
- **Limiti noti:** il tar è stato fatto prima delle modifiche di tracciamento successive (`STATUS.md` e piano); copia su disco esterno **non ancora fatta** (stesso disco della cartella di lavoro). `<backup>` pesa 329 MB.
- **Orari:** bundle 06:37, tar 06:39.

### 2026-11-10 — F0.1 Email di Andrea archiviata ☑

- **Cosa:** `mv "inbox/Riorganizzazione Man in the Loop.eml" docs/meetings/2026-11-08_Borruso_Riorganizzazione.eml` (destinazione controllata: non esisteva).
- **Test:** `ls -A inbox` vuoto; il file è in `docs/meetings/` con 30.613 byte (stessa dimensione dell'originale); `git status` invariato (cartella ignorata); sha256 del file: `e69d1552e5e5…ce05`.
- **Rollback:** rimettere il file in `inbox/`.

### 2026-11-10 — F0.3 `main` allineato, branch del piano ☑

- **Cosa e comandi (nell'ordine):**
  1. Copie dei due file modificati in `<scratch>/f03/` con verifica sha256 (identiche: `PIANO` `4ccdd409…`, `STATUS` `d7568fc0…`).
  2. `git branch archivio/locale-2026-11-10 main` (conserva `9a76648` e `c69aa9a`, mai pushati).
  3. `git stash push -m "f03-modifiche-piano-status"` (stash@{0} **conservato** come rete di sicurezza).
  4. `git switch -c docs/piano-repo-unico origin/main`.
  5. **`git branch --unset-upstream`**: git aveva impostato `origin/main` come upstream del nuovo branch, quindi un `git push` senza argomenti sarebbe andato su `main`.
  6. Ricopiati i due file.
  7. `git branch -f main origin/main` (da un altro branch).
- **Test:**
  - `git rev-parse main origin/main` → entrambi `e14d9204…` (uguali).
  - `git log --oneline origin/main..archivio/locale-2026-11-10` → `9a76648`, `c69aa9a`.
  - `git diff --name-status origin/main` → `M STATUS.md`, `A docs/PIANO-RIORGANIZZAZIONE.md` (solo questi due).
  - `STATUS.md`: il diff rispetto a origin è solo la sezione «PIANO IN CORSO» (+6 righe).
  - `WORKFLOW.md` identico a `origin/main` (190 righe).
- **Stato dopo il task:** branch corrente `docs/piano-repo-unico`; `main` locale = origin; `stash@{0}` presente; nessun commit nuovo.
- **Rollback:** `git switch archivio/locale-2026-11-10` (e `git branch -f main <sha>` con lo SHA in `sha-riferimento.txt`).

### 2026-11-10 — F0.4 Freno locale su `main` ☑

- **Controlli preliminari:** nessun hook git attivo in `.git/hooks`; `core.hooksPath` non impostato.
- **Cosa:**
  1. Creato `.git/hooks/pre-push` (locale, non versionato, `chmod +x`): esce con 1 se il ref locale o remoto è `refs/heads/main`, con messaggio.
  2. `.claude/settings.json`: aggiunto `permissions.deny` con 7 regole: `git push origin main*`, `git push*:main*`, `git push*refs/heads/main*`, `git push*--force*`, `git push* -f*`, `git push*--delete*`, `git push origin :*`.
- **Test:**
  - `python3 -I -c json.load(...)` su `settings.json` → valido, 7 regole, hook `SessionStart` presente.
  - Hook con input simulato su stdin: `refs/heads/main → refs/heads/main` exit 1; `refs/heads/docs/piano-repo-unico → stesso` exit 0; `(delete) → refs/heads/main` exit 1; `refs/heads/docs/x → refs/heads/main` exit 1.
  - **Non provate:** le regole `deny` (richiederebbero un push).
- **Pendente:** la modifica a `.claude/settings.json` è nel working tree del branch (non committata); arriva su GitHub con la PR di F0.6.
- **Rollback:** rimuovere il blocco `permissions` e cancellare `.git/hooks/pre-push`.

### 2026-11-10 — Creazione di questo log ☑

- **Cosa:** creato `docs/LOG-RIORGANIZZAZIONE.md` su richiesta di Nelson («log puntuale in .md con tutti i task eseguiti, da aggiornare a ogni task»); aggiunta nel piano (§0.2 punto 6) la regola di aggiornarlo a ogni task e il rimando in testa al piano.
- **File toccati:** `docs/LOG-RIORGANIZZAZIONE.md` (nuovo), `docs/PIANO-RIORGANIZZAZIONE.md`.
- **Nota:** il file sta in `docs/` come il piano; a F3.2 (`docs/` → `reference/`) si sposta insieme.

### 2026-11-10 — F0.5 Annuncio ad Andrea e Davide ◐ (parziale)

- **Cosa:** preparato il testo completo (testo semplice) nella conversazione; **Nelson ha scelto di inviare invece un avviso breve** (canale e ora non registrati) e di mandare «i dettagli alla fine». Testo effettivamente inviato, riportato da Nelson: «Grazie Andy, procedo così allora. @Davide: in questi gg please non fare modifiche su github sennò rischiamo conflitti nei file. Vi avviso quando ho finito».
- **Comunicato:** adesione alla linea di Andrea («procedo così»); **richiesta di non fare modifiche su GitHub** ai collaboratori (congelamento, senza date né fine definita: «vi avviso quando ho finito»).
- **NON ancora comunicato (rimandato da Nelson alla fine):** le regole branch + PR anche per l'AI; il calendario di F2/F3; la domanda a Davide su come lavora sul repo (serve ad Andrea per `WORKFLOW.md`); la richiesta di link condivisi a pagine che spariranno (`/docs/…`, `/beta/…`, `/old_version/…`); le attività assegnate (Crunchbase, STATUS, README rawdata; JSON in `validate.py` ad Andrea).
- **Conseguenze da tenere presenti:**
  1. Il congelamento oggi è aperto e senza date: copre anche le PR di altri. Gli altri non risponderanno alle PR di F0.6 e F2 mentre dura → vale O1 (le fonde Nelson, scrivendolo nella PR).
  2. Davide non sa ancora di dover lavorare solo con branch e PR, né che `beta/` e `old_version/` spariscono: va avvisato **prima di F2.6** (merge della pulizia).
  3. La domanda a Davide resta aperta e blocca solo la rifinitura di `WORKFLOW.md` (F6.1).
- **Per chiudere F0.5:** Nelson invia i dettagli (testo già pronto in conversazione) e si annota data e canale.

### 2026-11-10 — F0.6 Prima PR (piano + log + freno locale) ☑

- **Controlli prima del commit:** branch `docs/piano-repo-unico`; `git diff --name-status origin/main` = `M .claude/settings.json`, `M STATUS.md`, `A docs/LOG-RIORGANIZZAZIONE.md`, `A docs/PIANO-RIORGANIZZAZIONE.md` (solo i 4 previsti). C7 sui 4 file: le uniche corrispondenze sono testo esplicativo (esempi di pattern e `/home/x/y` come caso di test), nessun percorso o segreto reale; email presenti: solo `git@github.com` (remoto SSH) e `comunicazione@infonodes.org` (whitelist). `settings.json` JSON valido.
- **Commit:** `83b5c9d` «docs: piano di riorganizzazione a repo unico, log e freno locale su main» (4 file, +581 righe), con la riga Co-Authored-By; working tree pulito dopo il commit.
- **Push:** `git push -u origin docs/piano-repo-unico` → creato il solo branch remoto `docs/piano-repo-unico` (`83b5c9d`); l'hook `pre-push` lo ha lasciato passare. Verificato con `git ls-remote --heads origin`: `main` remoto invariato (`e14d920`), `v.2026-c` invariato (`0cfa3af`). L'upstream del branch ora è il branch stesso (non `main`).
- **Questa voce di log** è stata aggiunta dopo il push e viene pushata con un secondo commit sullo stesso branch (la PR si aggiorna da sola).
- **Da fare per chiudere F0.6:** Nelson apre la PR dal web (`https://github.com/infonodesETS/manintheloop/pull/new/docs/piano-repo-unico`) verso `main`; la valuta il primo che la vede; con il congelamento in corso vale O1 (la fonde Nelson, scrivendolo nella PR); dopo il merge: «Delete branch» dal bottone, poi in locale `git switch main && git pull --ff-only` (il hook di pull deve riuscire: `main` non sarà più divergente) e controllo che `git log` mostri il merge.

- **Esito (chiusura F0.6):** Nelson ha aperto la PR **#28** «Piano di riorganizzazione a repo unico, log e freno locale su main» e l'ha fusa (merge commit `2e6ae14`, 2 commit, 4 file, +589 righe), poi ha cancellato il branch remoto dal bottone. Nessuna review (congelamento in corso, O1).
- **Verifiche dopo il merge:** `git fetch --prune` → `origin/main` = `2e6ae14`, branch remoti rimasti `main` e `v.2026-c`, tag `sec-2026-10-17` invariato; `git diff --name-status e14d920 origin/main` = i 4 file previsti. Sito online: `/`, le 5 pagine e `data/mitl-index.json` → 200; hash di `mitl-index.json` online uguale a quello del repo (`714c0f04…`).
- **Allineamento locale:** `git stash push` (solo la riga di tabella del piano) → `git switch main` → `git pull --ff-only` (4 file, +589) → `main` = `origin/main` = `2e6ae14` → `git switch -c docs/avanzamento-f0` → `git stash pop` (stash rimosso; la modifica è tornata nel working tree). Upstream non impostato sul nuovo branch. `git branch -d docs/piano-repo-unico` (fuso, rimosso).
- **Osservazione importante (risponde al dubbio di Nelson su Pages):** subito dopo il merge `https://mitl.infonodes.org/docs/PIANO-RIORGANIZZAZIONE.md` e `…/docs/LOG-RIORGANIZZAZIONE.md` rispondono **200**. Quindi Pages serve la **root di `main`** (non `/docs`, non una Action): consistente con l'ipotesi del piano, ma la conferma in Settings → Pages (F0.7a) resta da fare. Conseguenza: piano e log sono pubblici online fino a F3 (contengono solo il testo del piano e nessun dato sensibile: controllo C7 fatto in F0.6).
- **Stato locale dopo il task:** branch `docs/avanzamento-f0` (da `main`), con una modifica non committata a `docs/PIANO-RIORGANIZZAZIONE.md` + questo aggiornamento del log e di `STATUS.md`. `stash@{0}` (F0.3 `f03-modifiche-piano-status`) ancora presente. Branch locali rimasti: `archivio/locale-2026-11-10`, `edf-merge-script`, `edf-update-2026-10`, `nuovi-fondi-eu`, `status-search-keywords`, `v.2026-c`, `main`.
- **Regola per gli aggiornamenti successivi del log:** viaggiano con il branch del task in corso e arrivano su `main` con la PR di quel task (non una PR per ogni riga).

### 2026-11-10 — F0.7 Verifiche su GitHub e Vercel ◐ (solo parte (a): Pages)

- **Cosa:** Nelson ha guardato Settings → Pages e ha fornito uno screenshot (`inbox/c81c95cb-b135-4a3a-8969-e2fc28eef38e.png`, ancora in `inbox/`: da proporre dove archiviarlo). Letto da me con lo strumento di lettura immagini. Sola lettura: nessun «Save» premuto.
- **Dati letti (F0.7a):**
  - Source: **Deploy from a branch**; Branch: **`main`**, cartella **`/ (root)`** → conferma che Pages serve la root di `main` (non una Action, non `/docs`).
  - «Your site is live at https://mitl.infonodes.org/»; ultimo deploy da `nelsonmau`, «8 minutes ago» (= il merge della PR #28), tramite il workflow `pages build and deployment` (ambiente `github-pages`).
  - Custom domain: **`mitl.infonodes.org`**; stato **«DNS Check in Progress»** (pallino arancione) nonostante il sito risponda.
  - **Enforce HTTPS: spuntato** (nello screenshot compare due volte: probabile effetto di rendering durante il caricamento).
  - Sezione «Visibility» → è la pubblicità di GitHub Enterprise (non rilevante).
- **Controlli miei, in sola lettura:** `dig`: `mitl.infonodes.org` → CNAME `infonodesets.github.io.`, A `185.199.108.153`/`.109.153`/`.110.153`/`.111.153` (IP di GitHub Pages); `curl -I https://mitl.infonodes.org/` → HTTP/2 200, `server: GitHub.com`; `http://` → 301 verso `https://`; certificato `CN=mitl.infonodes.org`, scadenza **2026-12-21**. Conclusione: DNS corretto e HTTPS valido; il «DNS Check in Progress» è con ogni probabilità transitorio (compare dopo un deploy).
- **Baseline per F3.6:** prima dello switch di Pages lo stato è «DNS Check in Progress» + HTTPS attivo + certificato fino al 2026-12-21. Se dopo lo switch il messaggio persiste, non va attribuito automaticamente allo switch. In F3.6 ricontrollare dominio e HTTPS (e il certificato: scade fra ~6 settimane, GitHub lo rinnova da solo se il DNS check passa).
- **Discrepanza da chiarire (minore):** nello screenshot la barra del repo mostra la scheda **Discussions**, ma l'API pubblica dice `has_discussions: false` (anche prima). Da verificare in Settings → General → Features; non blocca niente.
- **Non ancora fatti:** (b) Rulesets e Branches (solo l'API pubblica dice `protected: false`); (c) Actions → General; (d) valore di `MITL_INDEX_URL` su Vercel (**lo deve guardare Davide**: Nelson non ha accesso in modifica; testo per Davide già preparato nella conversazione); (e) Collaborators e ruolo di Nelson (serve **Admin** per cambiare Pages in F3.6).
- **Gate G3:** la parte «Pages verificato» è soddisfatta; G3 si chiude con l'istantanea del sito vivo (F1.3).

### 2026-11-10 — F0.7(d) Richiesta a Davide su Vercel ◐

- **Cosa:** Nelson ha scritto a Davide chiedendo, in sola lettura, il valore di `MITL_INDEX_URL` nel progetto Vercel `marlamag` (e se punta a `https://infonodesets.github.io/manintheloop/data/mitl-index.json` o altrove, es. un branch su `raw.githubusercontent.com`). Messaggio inviato (canale e ora non registrati). **Senza** la domanda sull'ultimo deploy (versione ridotta rispetto alla mia bozza).
- **Stato:** in attesa della risposta di Davide. Non blocca F1, F2, F3; va chiusa entro B5 (Release 1).
- **Nota:** la domanda a Davide su come lavora sul repo (per `WORKFLOW.md`) non è stata fatta in questo messaggio: resta in F0.5.

### 2026-11-10 — F1 Verifiche in sola lettura (F1.2-F1.7) ☑ — F1.1 resta a Nelson

Tutto in sola lettura (nessuna modifica a repo, GitHub o servizi). Script e risultati salvati **fuori dal repo** in `<backup>/F1-verifiche/` (`beta_diff.py/.txt`, `check_refs.py`, `refs_baseline.txt`, `snapshot.py`, `inv_scripts.py/.txt`, `inv_targets.py/.txt`, `snapshot-live-2026-11-10.tsv.sonda`) e `<backup>/snapshot-live-2026-11-10.tsv`. Riferimento git: `origin/main` = `HEAD` = `2e6ae14`.

**F1.2 — `beta/` vs root.** 53 file in `beta/`: **39 identici** alla root, **14 con lo stesso percorso ma contenuto diverso**, **0 presenti solo in `beta/`**. Dei 14: 6 sono i CSV di `crunchbase_sandbox/` che differiscono **solo per il fine-riga** (CRLF in root, LF in `beta/`; confermato con `git diff --ignore-space-at-eol` vuoto e con `file`); gli altri 8 (`data/database.json`, `data/edf_orgs.json`, `data/publications.json`, `index.html`, `publications.html`, `reports/countries/index.html`, `web/countries.js`, `web/i18n.js`) hanno in root un ultimo commit **successivo** a quello di `beta/` (root: 2026-09-03, 10-19, 10-26; `beta/`: 2026-08-18; ultimo commit su `beta/`: `7d5f83a` 2026-08-31). Esempio: `beta/index.html` contiene inline le tabelle Paese→ISO che in root sono state spostate in `web/countries.js`. **Conclusione:** `beta/` non contiene nulla che manchi in `main`; è una copia più vecchia. Resta raggiungibile dal tag `v.2026-b` (F2.1). Da confermare da Nelson in F2.

**F1.3 — Istantanea del sito vivo** (2026-11-10 ~06:29 UTC; `<backup>/snapshot-live-2026-11-10.tsv`, 29 percorsi). **28 su 29 con sha256 identico a `origin/main`.** Unico non uguale: `CNAME` → 404 (Pages non lo pubblica: normale). Nota per i test: **C5 non deve aspettarsi `CNAME`**. Quindi il sito vivo coincide con `main`. **Sonda degli URL oggi pubblici che spariranno** (tutti 200 tranne l'ultimo): `/beta/`, `/beta/index.html`, `/old_version/`, `/old_version/Intro-Manintheloop.pdf`, `/docs/SCHEMA.md`, `/docs/sintesi.html`, `/docs/synthesis-en.html`, `/docs/typography.html`, `/docs/PIANO-RIORGANIZZAZIONE.md`, `/STATUS.md`, `/ROADMAP.md`, `/WORKFLOW.md`, `/rawdata/edf_calls.json`, `/rawdata/edf_calls_2026-06-17.json`, `/data/qid_candidates.json`, `/data/crunchbase_sandbox/matches.csv`, `/scripts/validate.py`, `/testi/text`, `/reports/countries/italy/index.html`; `/sitemap.md` → 404 (ignorato da git). Cioè **oggi il sito pubblica anche script, note, dati grezzi e Crunchbase**: dopo F3 scompariranno dal sito (restano nel repo). Da comunicare (F0.5 dettagli). Gate **G3 soddisfatto** (Pages verificato + istantanea).

**F1.4 — Baseline C4 (dipendenze chiuse).** 16 file scansionati (6 pagine, `reports/countries/index.html`, 8 `web/*.js`/`*.css` esclusa `cytoscape.min.js`), 27 riferimenti locali unici, **0 mancanti**. Riferimenti **fuori dal perimetro futuro `docs/`**: esattamente 2, come previsto: `data/qid_candidates.json` (da `about.html`) e `rawdata/edf_calls.json` (da `web/app.js`). `reports/countries/italy/index.html`: **nessun riferimento** → O4 (va in `work/`) confermata. Test del test: copia temporanea con `<script src="web/non-esiste.js">` → rilevato 1 mancante; senza → 0. **Lezioni di metodo (vanno nello script di F5.1):** (1) in un `.js` i `fetch()` si risolvono rispetto alla **pagina** che lo carica (radice), mentre gli `import './x.js'` dei moduli ES rispetto al **file** (`web/`): la prima versione dello script dava 6 falsi positivi per averli trattati allo stesso modo; (2) i riferimenti con `${…}` o concatenazioni vanno ignorati.

**F1.5 — Inventario script (36).** 8 di rete (`enrich_wikidata`, `fetch_edf_bulk`, `fetch_wikidata_websites`, `import_investors_crunchbase`, `patch_iv_countries_p159`, `reprocess_skipped_qids`, `search_missing_qids`, `sparql_search_qids`); 27 con `--dry-run`. Due stili di percorso: (a) **27 script calcolano la radice da `__file__`** (`BASE = dirname(dirname(abspath(__file__)))`, 2 con `Path(__file__).parent.parent`: `import_mintl_companies`, `patch_edf_objectives`) → indipendenti dalla cartella da cui si lanciano, ma **dipendenti dalla profondità dello script** (rilevante per F6.6); (b) **8 usano `data/database.json` relativo alla cartella corrente** (`audit_quality`, `dedup_entities`, `patch_cb_wrong_matches`, `patch_hq_conflicts`, `patch_hq_conflicts2`, `patch_iv_countries_batch2`, `patch_iv_countries_manual`, `patch_orange_cb`) + `parse_ishares.py` con `rawdata/ishares_…csv`: **vanno lanciati dalla radice**. **Destinazioni esatte** (script che le usano): `data/database.json` **32**; `rawdata/edf_calls.json` 5 (`build_edf_entities`, `fetch_edf_bulk`, `import_edf_projects`, `merge_edf_calls`, `patch_edf_objectives`); `data/edf_orgs.json` 3 (`build_edf_entities`, `import_edf_projects`, `import_edf_websites`); `data/qid_candidates.json` 3 (`reprocess_skipped_qids`, `search_missing_qids`, `sparql_search_qids`); `data/crunchbase_sandbox` 2 (`import_crunchbase_csv`, `regenerate_export`); `data/mitl-index.json` 1 (`build_chat_index`); `rawdata/ishares_metals_mining_gics151040.csv`, `rawdata/ishare_aerospace_defense_GICS201010_en.csv`, `rawdata/mintl-update-companies-20260618-foglio1-csv6-18-2026.csv`: 1 ciascuno; `../refactoring/data/database.json` 3 (`import_by_wikidata`, `import_startups`, `migrate_old_db_investors`: script una tantum, il vecchio DB non è nel repo). **Questa è la lista esatta delle modifiche di F3.7.** `build_chat_index.py`: `SITO = 'https://infonodesets.github.io/manintheloop'` (URL dentro l'indice; fa 301 verso `mitl.infonodes.org`: non toccare in F3).
 **Regola di C10** (letta da `build_chat_index.py`): `soggetti` = entità non `EDF-` e non ritirate; `progetti` = entità `EDF-` non ritirate; `relazioni` = relazioni non ritirate. Indice attuale: `generato` 2026-08-21, 2226 soggetti, 84 progetti, 2990 relazioni; database: 2582 entità, 3490 relazioni. Il test C10 deve ricontare queste tre quantità in modo indipendente.

**F1.6 — Baseline C7 (percorsi, segreti, email).** Su `origin/main` (escluse `beta/`, `old_version/`, `cytoscape.min.js`, piano e log): **un solo problema reale**: `docs/OPENTENDER-APPALTI.md:181` contiene un **percorso Windows personale** (`C:\Users\<utente>\Downloads\usaspending\…`) → da correggere in F3.2. Falsi positivi: `data/database.json:263901` (URL `…/particular/home/…` di CaixaBank) e 4 righe di `docs/typography.html` (attributi `data-token=…`): lo script di F5.3 deve evitarli (es. richiedere che `/home/` stia all'inizio di un percorso, non dentro un URL; `token` non seguito da `=` dentro un attributo HTML). **Nessun segreto.** Email: solo `comunicazione@infonodes.org` (33 occorrenze, in whitelist).

**F1.7 — Merge di prova `v.2026-c` su `origin/main`** (`git merge-tree --write-tree --name-only`): invariato, **un solo conflitto: `.gitignore`**.

**Pendente:** F1.1 (termini Crunchbase, Nelson). Nessun task di F1 ha modificato qualcosa.

### 2026-11-10 — F2.1-F2.5 Pulizia su branch `pulizia/f2-beta-old-version` (locale, non pushato) ☑ / F2.1 ◐

- **Branch:** `pulizia/f2-beta-old-version` da `origin/main` (`2e6ae14`), con 3 commit: `412c7c7` (log F0/F1), `f5b8024` (rimuove `beta/`), `6b0237c` (rimuove `old_version/`). Il vecchio branch locale `docs/avanzamento-f0` (senza commit propri) è stato cancellato dopo aver spostato le modifiche.
- **F2.1 Tag locali (non pushati):** `v.2026-b` = `2e6ae14` (53 file `beta/`, 106 `old_version/`); `archivio-2026-06` = `5e9b411` (106 `old_version/`, 0 `beta/` come atteso). Il push dei tag attende l'ok esplicito di Nelson.
- **F2.2/F2.3:** solo cancellazioni, 53 e 106 file; grep di `beta/` e `old_version/` nei file del sito: vuoto.
- **F2.4:** i 4 branch avevano 0 commit oltre `origin/main`; `git branch -d` li ha cancellati (SHA sopra e in `log-all.txt` del backup).
- **F2.5:** 28/28 percorsi con stato 200 dell'istantanea (esclusi `beta/`, `old_version/`) hanno hash uguale nel working tree; C4: 0 mancanti; `scripts/validate.py` OK (2582 entità, 3490 relazioni).
- **Attenzione:** in `old_version/` restano in locale **71 file non tracciati** (non fanno parte del repo; sono nella copia completa del backup `.tar.gz`). Non cancellati. Decisione a Nelson.
- **Prossimo:** F2.6 (push branch e tag, PR dal web). Prima serve F0.5 (dettagli ad Andrea e Davide) e l'ok esplicito al push.

### 2026-11-10 — F0.5 Annuncio ad Andrea e Davide ☑ (chiusa da Nelson)

- Nelson ha inviato la comunicazione completa con parole proprie e la dichiara conclusa. Il testo non è registrato qui. Nessuna verifica mia sul contenuto: se non coprisse la sparizione degli URL pubblici (`/beta/`, `/old_version/`, `scripts/`, `rawdata/`, ecc.), va integrata prima di F3.

### 2026-11-10 — Spostati i 71 file non tracciati di `old_version/`

- Spostati (non cancellati) in `<backup>/old_version-non-tracciati/` (71 file, 5,7 MB; erano anche nel `.tar.gz`). Nel repo `old_version/` non esiste più sul disco.

### 2026-11-10 — F2.6 PR #29, merge e verifica sul sito vivo ☑ (gate G4)

- Push (con ok esplicito di Nelson): branch `pulizia/f2-beta-old-version` (`fb378f3`) e tag `v.2026-b` (`2e6ae14`), `archivio-2026-06` (`5e9b411`). F2.1 completata. PR #29 aperta e mergiata da Nelson con merge commit `f4edd71`; branch remoto cancellato dal bottone; branch locale cancellato con `-d`. `main` locale allineata.
- Sito vivo (dopo circa un minuto dal merge): `/beta/index.html` 404; 28/28 percorsi dell'istantanea con hash identico. **G4 soddisfatto.**

### 2026-11-10 — F1.1 / G2 Termini Crunchbase: esito «incerto, tendente a consentito» (decisione di Nelson)

- **Letto** (lettura di `https://about.crunchbase.com/terms-of-service`, testo che riporta «Last Updated: September 30, 2026»; metadati pagina `dateModified` 2024-11-26; pagine collegate non lette). Il testo **non** prevede eccezioni per l'uso non profit; consente solo «insubstantial excerpts» con attribuzione e senza concorrenza al servizio; vieta copia/conservazione di «any significant portion of the Content», download/export e scraping automatici, rivendita e opere derivate; per «any other uses» richiede «prior written consent». Crunchbase può chiedere la cancellazione dei dati posseduti. Snapshot 2013 e Crunchbase Basic sono CC BY 4.0. Non è detto quale accesso abbiamo usato per gli export.
- **Valutazione mia (non consulenza legale):** dal solo testo l'esito non è «consentito»; sarebbe incerto/tendente a vietato per i CSV grezzi e per la ridistribuzione in `database.json` (929 entità con `sources.crunchbase`).
- **Decisione di Nelson:** classificare come **incerto ma tendente a consentito**, proseguire con tutto il piano e fare una verifica di dettaglio più avanti. Il rischio è accettato da Nelson; G2 è considerato **sbloccato con riserva**. **Da fare più avanti:** (a) identificare account/programma degli export; (b) leggere Data Use Addendum, Attribution Instructions e termini del programma; (c) decidere con Andrea e Davide su CSV e campi derivati; (d) se serve, chiedere consenso scritto a Crunchbase.

### 2026-11-10 — F3.1-F3.4 Branch `struttura/sito-docs-copia` (locale, non pushato) ☑

- **Gate:** G2 sbloccato con riserva (decisione di Nelson, vedi sopra). G5 (congelamento): F0.5 è stata fatta da Nelson a modo suo e dichiarata conclusa; non mi risulta verificato che includa il congelamento. Il lavoro è solo locale; **prima del merge della PR 2a chiedere a Nelson conferma del congelamento.**
- **F3.1:** branch creato dal branch di log (main + 1 commit di log), non da `main` pura.
- **F3.2:** `git mv docs reference` (12 rinomine R100, `63aa00d`; la cartella ignorata `meetings/` si è spostata con la directory). `.gitignore`: `reference/meetings/`. Riferimenti testuali corretti in `reference/DATABASE-E-DATI.md`, `STATUS.md`, `WORKFLOW.md`; percorso personale di `reference/OPENTENDER-APPALTI.md:181` sostituito con «cartella locale `usaspending/` (fuori dal repo)». Invariati: i `docs/…` storici in LOG e PIANO e `docs/CONTRATTO-FONTI.md` (file del repo MARLA, esterno).
- **F3.3:** nuovo `docs/` con 29 file: `CNAME`, 6 pagine, `web/` (10), 9 JSON, `data/edf_calls.json` (copia identica di `rawdata/edf_calls.json`, 4,3 MB), `reports/countries/index.html`, `pages-switch-check.txt`. Modifiche: `docs/web/app.js:99` → `fetch('data/edf_calls.json')`; `docs/about.html:142` → link GitHub a `work/qid_candidates.json`. `cmp`: uguali tranne queste due. C5: 24 ok, 2 diversi attesi, 2 fuori da `docs/`. C4: 0 mancanti. C6: 10 JSON validi. C7: nessun percorso personale.
- **F3.4:** server da `docs/` su porta 8001 (poi spento): 8 pagine (home, modalità EDF, scheda Leonardo `IN-0841`, search, networks, key-figures, publications, about, reports/countries) con 0 errori e 0 risposte ≥400, salvo `favicon.ico` 404. **Scoperta:** `loadEdf()` in `web/app.js` non è chiamata da nessuna parte: il sito non scarica `edf_calls.json`. La copia in `docs/data/` (O3) è quindi preventiva (4,3 MB); il test «elenco progetti EDF» non è applicabile. Da decidere con Nelson: tenerla o toglierla.
- **Errore mio:** `pkill -f "http.server 8001"` ha ucciso anche la mia shell (il pattern era nel comando); nessun danno. Server poi terminato.
- **Prossimo:** F3.5 (push, PR 2a dal web; serve ok esplicito).

### 2026-11-10 — F3.5 PR #30 mergiata e verifica del sito vivo ☑

- Push del branch con ok esplicito di Nelson; congelamento (G5) confermato da Nelson («Andrea e Davide avvisati»). PR #30 mergiata da Nelson (`f318bb1`), branch remoto cancellato; in locale `main` allineata e i branch `struttura/sito-docs-copia` e `docs/log-f2-6` cancellati con `-d`.
- Sito vivo dopo il merge: 28/28 percorsi dell'istantanea con hash identico; `/docs/pages-switch-check.txt` = 200 (atteso, la root contiene il nuovo `docs/`); `/pages-switch-check.txt` = **404** (Pages serve ancora la root); `/docs/SCHEMA.md` = 404 (atteso).
- **Prossimo:** F3.6, switch di Pages a `/docs` fatto da Nelson con l'account `infonodes` (Admin). Il branch `struttura/sito-docs-rimozione` è già creato per F3.7, con la sola modifica di questo log.

### 2026-11-10 — F3.6 Switch di Pages a `/docs` ☑ (eseguito da Nelson con l'account `infonodes`)

- **Screenshot di Nelson** (verificato): «Your site is live at https://mitl.infonodes.org/», Source «Deploy from a branch», Branch `main` + cartella `/docs`, Custom domain `mitl.infonodes.org` (ancora «DNS Check in Progress», com'era prima), Enforce HTTPS attivo, ultimo deploy da `infonodesETS` 4 minuti prima dello scatto.
- **Verifica sul sito vivo (C9/C5):** `/pages-switch-check.txt` **200** (Pages serve `docs/`); `/docs/pages-switch-check.txt` 404; `/rawdata/edf_calls.json` 404 (voluto); 6 pagine, `reports/countries/` e `data/edf_calls.json` 200; `/data/mitl-index.json` 200; `https://infonodesets.github.io/manintheloop/data/mitl-index.json` → 200 dopo redirect a `https://mitl.infonodes.org/data/mitl-index.json` (**MARLA non toccato**); `http://` → 301; certificato valido fino al 2026-12-21. Hash contro l'istantanea: 24 uguali, 4 diversi, tutti attesi: `about.html` e `web/app.js` (le 2 righe volute), `rawdata/edf_calls.json` e `data/qid_candidates.json` (non più serviti; il secondo e il primo restituiscono ora 404 o pagina diversa, da `sha256` del corpo).
- **Screenshot in `inbox/`:** quello dello switch è stato cancellato (come chiesto); quello di prima dello switch (`c81c95cb…png`) è stato **spostato**, non cancellato, in `<backup>/screenshot-pages-prima-switch-2026-11-10.png`. `inbox/` vuota.
- **Rollback non necessario.** Registrato: switch ~11:00 del 2026-11-10 (ora indicativa, dallo screenshot).
- **Prossimo:** F3.7 (PR 2b: rimozione delle copie dalla root, `work/`, percorsi negli script, `scripts/sync_site_data.py`). Prima di iniziare, salvare gli output `--dry-run` «prima» sul `main` pulito (C12).

### 2026-11-10 — F3.7 PR 2b: rimozione copie dalla root, `work/`, percorsi negli script ◐ (locale, non pushato)

- **Baseline C12 «prima»** salvata **prima** di toccare nulla, in una copia temporanea (`git archive HEAD`) fuori dal repo: 23 output di `--dry-run` + `validate.py`. Lezione: `import_crunchbase_csv.py --dry-run` **scrive** `import_report_<data>.json` e `unresolved_<data>.csv` anche in dry-run: va lanciato solo su copie. 5 script usciti con errore già «prima» (3 vogliono `../refactoring/`, 2 un CSV come argomento: per questi ho passato un CSV).
- **Rimozioni (28 D):** dalla root `CNAME`, 6 pagine, `reports/countries/index.html`, `web/` (10), 9 JSON pubblicati di `data/`, e `docs/pages-switch-check.txt`. Tutti esistono identici in `docs/`.
- **Spostamenti in `work/` (26 R):** `data/qid_candidates.json` → `work/qid_candidates.json`; `data/crunchbase_sandbox/` → `work/crunchbase/`; `reports/countries/italy`, `reports/countries/scripts`, `reports/pdf` → `work/reports/countries/italy`, `…/scripts`, `work/reports/pdf`; `testi/` → `work/testi/`; `reference/{sintesi.html, synthesis-en.html, SINTESI-nuova-versione-2026.md, OPENTENDER-APPALTI.md}` → `work/sintesi/`; `reference/typography.html` → `reference/design-system.html`. `rawdata/` invariato. `.gitignore`: `reports/charts/` → `work/reports/pdf/charts/`, pdf sotto `work/` (la cartella locale `reports/charts` spostata a mano in `work/reports/pdf/charts`, ignorata). Cartelle `data/` e `reports/` ormai vuote rimosse dal disco.
- **Percorsi negli script (33 file):** `data/database.json`, `edf_orgs.json`, `mitl-index.json` → `docs/data/…`; `data/qid_candidates.json` → `work/qid_candidates.json`; `data/crunchbase_sandbox` → `work/crunchbase` (anche nei testi d'uso). Non toccati: `../refactoring/…` (3 script una tantum), `build_chat_index.py` `SITO` (URL), `rawdata/`. `work/reports/pdf/generate_charts.py` e `work/reports/countries/scripts/analyze_italy.py` aggiornati (il primo era già rotto da prima: `parent.parent`).
- **Nuovo `scripts/sync_site_data.py`** (`--check`, `--write`, solo `rawdata/edf_calls.json` → `docs/data/edf_calls.json`); provato in copia: identico → 0; file alterato → `--check` esce 1, `--write` ripristina, `--check` 0; opzione errata → 2. Passo aggiunto a `reference/UPDATE_PROTOCOL.md` (Step 5).
- **Testi aggiornati:** `STATUS.md` (albero rifatto a mano + percorsi), `WORKFLOW.md` (§6 «Dal 2026-11-10 Pages pubblica solo `docs/`»; §9 server da `docs/`), `ROADMAP.md`, `reference/*.md`, `work/**/*.md`. Restano invariati i `docs/…` storici di LOG e PIANO.
- **Test (tutti sul working tree prima del commit):** C3: 28 D + 26 R + 41 M + 1 A (`scripts/sync_site_data.py`); radice senza pagine, `web/`, `data/`; C4 su `docs/` 0 mancanti; C6 10 JSON validi; C7 nessun percorso personale; `grep` di `data/` negli script senza `docs/`/`refactoring` vuoto; `py_compile` su tutti gli script ok; C1 `validate.py` PASSED 2582/3490; **C12: 23 su 23 output identici** (confronto dopo normalizzazione dei nuovi percorsi nei testi stampati; exit code uguali); **C10:** `build_chat_index.py` su copia: soggetti 2449, progetti 129, relazioni 3490 = ricalcolo indipendente; il file nel repo non è stato toccato.
- **Osservazione:** l'indice nel repo (`docs/data/mitl-index.json`, `generato` 2026-08-21: 2226 soggetti) è **più vecchio** del database; rigenerarlo cambia ciò che vede MARLA: decisione separata (STATUS punto 18).
- **C8 (browser):** non rifatto: il contenuto di `docs/` è identico a quello provato in F3.4 (cambia solo la rimozione della sentinella).
- **Prossimo:** ok esplicito al push; PR 2b dal web; dopo il merge verifica del sito (G6: stessi hash di F3.6) e F3.8.

### 2026-11-10 — F3.7 PR #31 mergiata e verifica sul sito vivo ☑ (gate G6)

- Push del branch con ok esplicito di Nelson (con l'account `nelsonmau`); PR #31 mergiata da Nelson (`f21ca8c`), branch remoto cancellato, `main` locale allineata, branch locale cancellato con `-d`. La root del repo ora contiene solo `docs/`, `reference/`, `work/`, `rawdata/`, `scripts/`, `STATUS.md`, `WORKFLOW.md`, `ROADMAP.md` e le cartelle locali ignorate.
- **Sito vivo (circa un minuto dopo il merge):** `/pages-switch-check.txt` 404 (sentinella rimossa); 6 pagine, `reports/countries/`, `data/database.json`, `data/edf_calls.json`, `data/mitl-index.json`, `web/app.js` tutti 200; **27/27 file di `docs/` con hash identico a quello online** (escluso `CNAME`, non servito); `https://infonodesets.github.io/manintheloop/data/mitl-index.json` → 200 dopo redirect a `https://mitl.infonodes.org/data/mitl-index.json` (MARLA non toccato). **G6 soddisfatto** (sblocca B2, il merge di `v.2026-c`).
- **F3.8:** resta da Nelson avvisare Andrea e Davide che il congelamento è finito e dei nuovi percorsi (`docs/` = sito, `work/`, `reference/`, script dalla radice).

### 2026-11-10 — B1 Decisioni di schema: S1 presentata, risposta in attesa ◐

- **Letti** (sola lettura): `git show origin/v.2026-c:docs/dev-v2026c-sec.md`, `…:tmp/sec-test/test-merge.md` (§4, §11), `reference/SCHEMA.md`, `scripts/validate.py`.
- **Trovato:** `reference/SCHEMA.md` prevede già `PER-NNNN` (persone) e il tipo di relazione `board_membership`; `validate.py` ha `PER_ID_RE = ^PER-\d{4}$`, `VALID_REL_TYPES = {investment, board_membership, edf_participation}`, `VALID_ROLES = {manufacturer, investor, board_member}`. Il documento di sviluppo di `v.2026-c` propone `PE-####` (come domanda aperta) e le relazioni `ownership`/`role`; il test SEC usa `PER-T####`, `board_membership`, `executive_officer`, `shareholder_5pct` (gli ultimi due non nello schema). Gli ID persona del dataset SEC (`P0001…`) si rinumerano a ogni estrazione. 2.298 persone nel test; `\d{4}` arriva a 9999.
- **S1 proposta a Nelson:** (a) `PER-NNNN` permanente + `P####` come riferimento di fonte in `sources.sec` [raccomandata]; (b) `PE-####`; (c) ID derivato dal CIK. Riconciliazione tra estrazioni: CIK se presente, altrimenti nome normalizzato + azienda con controllo manuale. **Nessuna risposta ancora.** S2-S7 da presentare una alla volta.
- **Sessione:** Nelson interrompe qui e riparte con `/clear` leggendo `STATUS.md`; il puntatore di `STATUS.md` è stato corretto (rimandava a `docs/PIANO-RIORGANIZZAZIONE.md`, spostato in `reference/` da PR #30) e aggiornato con «Dove siamo».

### 2026-11-10 — F3.8 Fine congelamento ☑ (chiuso da Nelson)

- Preparato il testo per Andrea e Davide (fine congelamento, lavoro su branch da `main` aggiornato con PR, nuovi percorsi `docs/`, `work/`, `reference/`, tag `v.2026-b` e `archivio-2026-06`, script dalla radice, vecchi URL `/docs/…`, `/rawdata/…`, `/scripts/…` non più online). Nelson ha approvato la prima parte; la frase finale su S1 è stata scartata e sostituita con un rimando a un indirizzo mai indicato; poi ha detto «skippiamo, segna come fatto».
- Registrato come fatto su decisione di Nelson. Non so se e con quale testo sia stato inviato.
- **B1:** S1 (prefisso persone) resta senza risposta.

### 2026-11-10 — B1 S1: parere chiesto ad Andrea, in pausa

- Su richiesta di Nelson ho scritto un messaggio per Andrea Borruso con la proposta S1 (`PER-NNNN` permanente, `P####` come riferimento di fonte in `sources.sec`, riconciliazione via CIK o nome normalizzato più azienda) e le alternative `PE-####` e ID da CIK. Invio non verificato da me.
- Nelson sospende B1 finché Andrea non risponde. S2-S7 non presentate. Alla ripresa: leggere la risposta di Andrea, registrare la scelta di S1 e passare a S2.
- Il branch `docs/log-f3-8` contiene questi aggiornamenti di log (F3.8 e B1), non ancora committati né pushati.

### 2026-11-11 — MITL_INDEX_URL: risposta di Davide, chiuso con riserva

- Davide non può recuperare il valore da Vercel (variabile sensibile); dice che dovrebbe essere `https://infonodesets.github.io/manintheloop/data/mitl-index.json`. Nelson aggiunge che la GitHub Page funziona regolarmente.
- **Verifica (sola lettura):** quell'URL risponde 301 verso `https://mitl.infonodes.org/data/mitl-index.json`, poi 200; sha256 del corpo = sha256 di `docs/data/mitl-index.json` (`714c0f04…c446f`). Quindi MARLA legge il file del repo, che è il vecchio (`generato` 2026-08-21, 2226 soggetti contro 2449 nel database).
- Il valore effettivo su Vercel resta non verificato direttamente. Regola: l'URL non cambia. Rigenerare l'indice è una decisione separata e va comunicata a Davide (cambiano le risposte di MARLA).
