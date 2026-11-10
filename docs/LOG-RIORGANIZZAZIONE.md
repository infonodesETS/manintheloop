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
| F0.6 PR del piano | ◐ commit e push fatti; PR da aprire dal web | 2026-11-10 |
| F0.7 Verifiche di Nelson su GitHub/Vercel | ☐ | |

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

### 2026-11-10 — F0.6 Prima PR (piano + log + freno locale) ◐

- **Controlli prima del commit:** branch `docs/piano-repo-unico`; `git diff --name-status origin/main` = `M .claude/settings.json`, `M STATUS.md`, `A docs/LOG-RIORGANIZZAZIONE.md`, `A docs/PIANO-RIORGANIZZAZIONE.md` (solo i 4 previsti). C7 sui 4 file: le uniche corrispondenze sono testo esplicativo (esempi di pattern e `/home/x/y` come caso di test), nessun percorso o segreto reale; email presenti: solo `git@github.com` (remoto SSH) e `comunicazione@infonodes.org` (whitelist). `settings.json` JSON valido.
- **Commit:** `83b5c9d` «docs: piano di riorganizzazione a repo unico, log e freno locale su main» (4 file, +581 righe), con la riga Co-Authored-By; working tree pulito dopo il commit.
- **Push:** `git push -u origin docs/piano-repo-unico` → creato il solo branch remoto `docs/piano-repo-unico` (`83b5c9d`); l'hook `pre-push` lo ha lasciato passare. Verificato con `git ls-remote --heads origin`: `main` remoto invariato (`e14d920`), `v.2026-c` invariato (`0cfa3af`). L'upstream del branch ora è il branch stesso (non `main`).
- **Questa voce di log** è stata aggiunta dopo il push e viene pushata con un secondo commit sullo stesso branch (la PR si aggiorna da sola).
- **Da fare per chiudere F0.6:** Nelson apre la PR dal web (`https://github.com/infonodesETS/manintheloop/pull/new/docs/piano-repo-unico`) verso `main`; la valuta il primo che la vede; con il congelamento in corso vale O1 (la fonde Nelson, scrivendolo nella PR); dopo il merge: «Delete branch» dal bottone, poi in locale `git switch main && git pull --ff-only` (il hook di pull deve riuscire: `main` non sarà più divergente) e controllo che `git log` mostri il merge.
