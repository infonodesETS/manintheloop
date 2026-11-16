# B5 Release 1: ripartenza (scritta il 2026-11-16, prima di un /clear)

> Punto di ripartenza per la sessione successiva. Non sostituisce `STATUS.md` (che parla del progetto e non è aggiornato su B5): si riscrive o si cancella a B5 finita. I numeri di git qui sotto hanno una scadenza: si rimisurano con `git status` e `git log --oneline main..HEAD`.

## Dove siamo

- **Branch locale `dati/b5-release1`** (da `main` = `2175a3c`, PR #72 fusa). **Non pushato.** Commit: `6269d21` tabella 1, `e137fdd` tabelle 2 e 3, `10c319c` verifica, `0a98eed` istruzione agenti. Non toccato `docs/data/database.json`.
- Non tracciati e da lasciare così: `work/verifica-parentela/` (primo lotto `parte_di`, deciso di aspettare il sito) e `work/verifica-qid/risultati/IN-0752.json`.
- **B5 non è iniziato come import.** Lo script `scripts/import_sec_ownership.py` del piano **non esiste**: va scritto (dry-run, idempotenza, riconciliazione 571 = 546 importate + 25 scartate con motivo). Letture obbligatorie già fatte nella sessione precedente: `S3`-`S7`, `SCHEMA.md` (sezione *Relationships*), `UPDATE_PROTOCOL.md`. **Non ancora lette:** controllo 11 di `scripts/validate.py` e come `docs/web/app.js` tratta le entità `PER-` e le relazioni diverse da `edf_participation` (`REL_MAP`).

## Cosa c'è in `work/b5-release1/`

- `proposta-aziende.csv` (161 ticker SEC → scheda `IN-`: 152 proposte, 1 debole `MOG-A`→`IN-1381`, 7 da decidere, `LOGI` senza scheda), `proposta-classi.csv` (47 righe ticker+classe, 22 aziende: 29 esistenti, 13 «attaccare», 5 «madre» per `GOOG` e `PLTR`), `proposta-gestori.csv` (110 entità SEC: 76 proposte, 9 da `S6`, 25 da decidere). Generate da `proponi_aziende.py`, `proponi_classi.py`, `proponi_gestori.py` (sola lettura).
- `verifica_tabelle.py`: controllo meccanico indipendente. Esito: nessun problema (completezza, unicità, coerenza). Non prova l'identità: il database non ha il CIK.
- `agenti/`: `ISTRUZIONE-AGENTE.md` (ruoli A e B), `input/A1-A4.json` (39 ticker) e `B1-B3.json` (25 depositanti), `prepara_input.py`, `check_b5.py` (controllo dei risultati; 8 test offline passati, non ancora provato con pagine vere), `test_check_b5.py`.

## Decisioni di Nelson ancora aperte

1. **D1:** per le 13 classi mancanti (`APP` B, `CMCSA` B, `DDOG` B, `DELL` A e B, `LUNR` C, `META` B, `METC` B, `MOG-A` B, `SATS` B, `TKO` B, `TTD` B, `WDAY` B): **attaccare** la quota alla scheda esistente della stessa società (proposta dell'AI, coerente con la regola sulle classi del 2026-11-12 e con B3) o creare una **scheda nuova per classe** (esempio A di `S3`, un diagramma).
2. Casi della tabella 1 senza proposta: `AIR` (Airbus `IN-0461` o AAR `IN-1388`), `T` (`IN-0042` o Telus `IN-0373`), `TEL` (`IN-0362` o Telenor `IN-0370`), `TKO` (`IN-0382` o Taseko `IN-0358`), `LOGI` (nessuna scheda). Il lavoro degli agenti.
3. Le 25 entità gestori «da decidere» (Vanguard ×3 contro `IV-0589`, Fidelity Management & Research contro `IV-0214`, Franklin Mutual Advisers contro `IV-0703`, BlackRock Advisors LLC che resta un nodo a sé, Leonardo contro `IN-0841`, ecc.).
4. Il sito va adattato **nella stessa PR dei dati** (`REL_MAP` in `app.js`, `index.html`, `networks.html`, `key-figures.html`, badge `person`): da proporre, non fatto.

## Prossimo passo (già approvato da Nelson il 2026-11-16, in forma di prova)

1. **Lanciare due agenti `general-purpose`**, uno per `A1` e uno per `B1` (non tutti e 7: prima si vede cosa rendono e se `check_b5.py` funziona con le pagine vere). Prompt: leggere per intero `work/b5-release1/agenti/ISTRUZIONE-AGENTE.md`, eseguire la sezione «Testo da dare all'agente» con `<LOTTO>` = `A1` (o `B1`), sola lettura, un solo file in uscita `work/b5-release1/agenti/risultati/<LOTTO>.json`, una riga di risposta. **Ruolo A cieco:** non aprire `proposta-*.csv`, `proponi_*.py`, `verifica_tabelle.py` né la storia git di quella cartella.
2. **Rilanciare io** `python3 -I work/b5-release1/agenti/check_b5.py work/b5-release1/agenti/risultati/<LOTTO>.json` e controllare con `git status` che gli agenti abbiano scritto solo il loro file. Rileggere a mano le frasi decisive di un campione.
3. Scrivere `work/b5-release1/agenti/confronta.py` (confronto tra risposte degli agenti e tabelle; solo disaccordi e `NEEDS_HUMAN`) e riferire a Nelson una tabella. Le tabelle si correggono solo con il suo ok.
4. Se la prova va bene, lanciare i lotti restanti (`A2`-`A4`, `B2`-`B3`); poi D1 e correzioni; poi lettura di `validate.py` controllo 11 e di `app.js`; poi scrivere `import_sec_ownership.py` (solo dry-run all'inizio).

## Regole da tenere (da `STATUS.md` e dalle decisioni di Nelson)

- **Domande → rispondere e fermarsi.** Nel dubbio una frase è una domanda. Ogni proposta con motivazione e costo.
- **Mai modifiche su `main`.** Il push dei **branch** lo fa l'AI (decisione di Nelson, 2026-11-16); la PR la apre Nelson dal web (`gh` non c'è). Testi da incollare in testo semplice tra «TESTO DA INCOLLARE» e «FINE TESTO DA INCOLLARE».
- **`reference/UPDATE_PROTOCOL.md` si legge per intero prima di qualunque modifica ai dati** (riletto nella nuova sessione, anche se oggi è stato letto). Dry-run, ok di Nelson, `--history-letta --apply`, `validate.py`, un commit per caso.
- Non cancellare branch o file senza ok. Agenti e ricerche web: i risultati sono **proposte**, l'esito lo firma Nelson. Ricerche con Exa (chiave in `~/.config/infonodes/exa.env`, mai stampata). Testi in `history`/`validation` in inglese.
- Commit con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Risposte in italiano con gli accenti.
- Prima di proporre lavoro su una scheda cercare il suo ID in `reference/LOG-RIORGANIZZAZIONE.md`, `ROADMAP.md`, `STATUS.md` e con `git log -S"ID"`.

## Limiti da non dimenticare

- Gli agenti sono lo stesso modello che ha scritto le tabelle: l'indipendenza è dell'informazione, non della testa. L'accordo con le mie proposte non prova l'identità.
- Il controllo cieco non è una barriera tecnica: le proposte sono nel repo.
- I 119 abbinamenti con ISIN nel database non sono verificati da agenti: restano un campione manuale (15 righe guardate, tutte coerenti per nome, ISIN e paese).
- Stime dei costi degli agenti non misurate: nel pilota ~50.000 token e 3-5 minuti per scheda.
