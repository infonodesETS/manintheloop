# Metodo agentico per controllare i dati (bozza provvisoria)

> **BOZZA PROVVISORIA (2026-11-14), provata una sola volta** (3 agenti su 3 schede già trattate, non su casi nuovi). Non è una regola vincolante. Nasce dall'idea di Nelson di riusare il metodo per controllare altri dati. Si applica insieme a [`METODO-VERIFICA-WEB.md`](METODO-VERIFICA-WEB.md) (come si verifica sul web) e alle regole di `STATUS.md` («Agenti e ricerche web»: i risultati degli agenti sono proposte e dati, non esiti; un agente non scrive nel foglio né nel repo).

## Lo schema

1. **Agenti di ricerca in sola lettura**, uno per scheda o per un gruppo piccolo, in parallelo. Ricevono la stessa istruzione scritta. Producono **un file strutturato** per scheda, in una cartella dedicata; non scrivono altro.
2. **Un controllo automatico del risultato**, fatto da uno script e non da un agente. Non si fida dell'agente: rilegge l'etichetta vera su Wikidata, riapre ogni fonte e cerca la frase citata, verifica che il verdetto sia coerente con le prove. Esiti: `PASS`, `NEEDS_HUMAN`, `FAIL`.
3. **Chi coordina** (l'AI della sessione) rilancia il controllo (non riporta quello dichiarato dall'agente), verifica con `git status` che gli agenti non abbiano scritto altro, e prepara una **tabella per gruppo**.
4. **Nelson approva la tabella**, non ogni passo. Le patch ai dati le applica il coordinatore con gli script di sempre: dry-run, `history` e `validation` lette, ok, `--history-letta --apply`, `validate.py`, `check_b3_branch.py`, un commit per scheda, una PR per gruppo.

## Cosa c'è nel repo (primo uso: QID rimessi)

- `work/verifica-qid/ISTRUZIONE-AGENTE.md`: l'istruzione da dare agli agenti, con il risultato atteso e il formato del file.
- `work/verifica-qid/check_risultato.py`: il controllo automatico. Regole: frasi di prova di almeno 25 caratteri (salvo identificativi dichiarati); un `remove_qid` con sole prove secondarie va a una persona; etichetta Wikidata riletta dall'API senza filtro di lingua (alcune etichette esistono solo in `mul`).
- `work/verifica-qid/test_check_risultato.py`: 20 prove senza rete, con errori piantati (test del test).
- `work/verifica-qid/esempi/`: una fixture fatta a mano e i tre risultati del test del 2026-11-14.

## Cosa ha provato il test del 2026-11-14

3 agenti su `IN-0863`, `IN-0865`, `IN-0600`: verdetti uguali alle decisioni già prese (2 `remove_qid`, 1 `keep_qid`); gli agenti hanno scritto solo i loro file; ciascuno ha impiegato circa 52.000 token e 7-9 minuti, in parallelo. Con le regole nuove del controllo i tre risultati non passano più automaticamente: due vanno a una persona (prove tutte secondarie) e uno è respinto (frase troppo corta).

## Limiti noti

- **Non era un test cieco:** le schede contenevano nella `history` la patch manuale del 2026-04-23 e gli agenti l'hanno citata. Il test mostra che la procedura funziona, non che il giudizio dell'agente sia indipendente.
- **Il controllo accerta che la frase sia nella pagina, non che la dimostri.** Quella lettura è di una persona, sulla tabella.
- **Le prove sono spesso secondarie** (aggregatori di registri): per questo i casi vanno alla persona. Una fonte primaria non sempre esiste o si lascia leggere (403, PDF tronchi).
- Non verificato se gli agenti abbiano rispettato i divieti di lettura dati nell'istruzione (trascrizioni non lette).
- Exa sbaglia anche con fonti dall'aspetto primario (vedi `METODO-VERIFICA-WEB.md`).
- Costo: una chiamata di agente per scheda, circa 50.000 token ciascuna; il contesto del coordinatore cresce con i riepiloghi.

**Lezioni dalla verifica dei legami di gruppo (2026-11-16, 5 agenti, 6 legami):**
- **«PASS» non dice che la frase decisiva sia stata ritrovata:** il controllo dà PASS con almeno una prova `primary` ritrovata, che può essere un'altra rispetto a quella che regge l'affermazione (per esempio il dato GLEIF invece della tabella del capogruppo). La frase che regge l'affermazione la rilegge una persona (o il coordinatore) nella fonte.
- **Nell'istruzione e nelle domande a Exa non va messa l'ipotesi del coordinatore** (regola già scritta in `work/verifica-parentela/ISTRUZIONE-PARENTELA.md`: domande descrittive e neutre, mai sì/no): rischio di conferma.
- **«Genitore diretto» di GLEIF e Exhibit 21 non provano che il legame sia diretto:** GLEIF dà una relazione di consolidamento contabile (IDV: in mezzo c'era IDV Group S.r.l.), l'Exhibit 21 elenca controllate dirette e indirette. Il campo `diretta` di `parte_di` vale `true` solo con una fonte che nomina la controllante immediata.
- **Un dettaglio che l'agente segnala può essere già noto al progetto:** prima di trattarlo come caso nuovo cercare l'ID in log, `ROADMAP.md`, `STATUS.md` e `git log` (caso `IN-1352`).

## Provenienza scritta nella scheda (regola del 2026-11-16, proposta di Nelson)

Ogni correzione fatta dopo una verifica agentica scrive nel testo della `history` e della `validation` (in inglese) due frasi: **«Decisive evidence»** e **«Weak point»**. Con `patch_qid_removed.py` si passano con `--evidence` e `--weak-point`; senza, lo script avvisa.
- **Prova decisiva:** la fonte primaria **riaperta** e la frase che regge l'affermazione (per un QID tolto: dove si vede che la scheda è un'altra entità giuridica). Non conta l'accordo con una decisione precedente letta nella `history`.
- **Punto debole:** cosa non è provato o viene solo da fonti secondarie (aggregatori, mirror GLEIF), e ogni legame con la capogruppo non provato da una pagina riaperta, che in quel caso non si scrive.
- **Le scrive chi coordina dopo aver letto il risultato**, non l'agente da solo; il controllo automatico non sa quale frase sia decisiva e non le genera.
- Le `history` sono in sola aggiunta: se il punto debole viene superato, si aggiunge una voce nuova. La regola vale dal terzo giro del pilota (2026-11-16); le 10 schede dei primi due giri non hanno le due frasi.

## Come riusarlo per altri dati

Lo schema resta; cambiano tre cose.
1. **L'istruzione:** quale domanda si pone, quali campi della scheda si leggono, quali fonti sono primarie per quel tipo di dato (per esempio registri nazionali per i codici fiscali, GLEIF per i nomi legali, filing SEC per le società quotate).
2. **Il formato del risultato e i controlli:** campi obbligatori e coerenza del verdetto (per i QID: etichetta e identificativi; per un codice fiscale: il numero e la fonte che lo contiene; per un duplicato: i due nomi e gli identificativi che li legano).
3. **I verdetti ammessi:** sempre con `unclear` come risposta valida.

Prima di estenderlo: provarlo su un gruppo di schede **mai trattate** (pilota), confrontare con una persona un campione dei `PASS`, e contare i casi che finiscono a `NEEDS_HUMAN` per capire se il risparmio di tempo regge.

## Da definire

- Soglia dei casi del pilota e criteri per dire che il metodo funziona (per esempio quanti `PASS` risultano giusti a un controllo a campione).
- Dove registrare nel database la fonte (campi della `validation`; `history` e `validation` in inglese, `UPDATE_PROTOCOL.md` principio 8).
- Se gli agenti possono usare un modello più economico per i casi semplici.
- Persone fisiche (dati personali, Release 2): metodo non definito, vedi `METODO-VERIFICA-WEB.md`.

## Lezioni del quinto giro (Ericsson, 2026-11-19)

- **Il nome legale del PIC è già nei dati EDF.** `rawdata/edf_calls.json` e `docs/data/edf_orgs.json` portano `organization_name` del Participant Portal (per esempio `ERICSSON AB`, `OY L M ERICSSON AB`): è fonte primaria. Il portale UE non restituisce testo via Exa (HTTP 500 o pagina JavaScript) e gli agenti ripiegavano su aggregatori; conviene dare all'agente il nome legale del PIC già letto lì, e dire che il legame PIC–registro nazionale resta da provare con una fonte che citi entrambi.
- **Più schede con lo stesso QID: guardare tutte e quattro insieme.** Con un solo agente per scheda emergono le differenze (qui: la scheda «canonica» era una controllata e la quotazione della capogruppo stava su un'altra). Il verdetto `unclear` con inclinazione a `remove_qid` è onesto quando la prova è solo secondaria.
- **Le note manuali di aprile non sono prova.** Su tre schede, due erano giuste nella sostanza e una sbagliata (`IN-0831`, «nome doppio»).
- **Indipendenza:** nei prompt, fonti esterne prima e `history`/`validation` dopo; non basta se il prompt contiene già la domanda («è la capogruppo?»).

## Agenti che eseguono i task del piano (codice, controlli, documenti)

> **BOZZA PROVVISORIA (2026-11-28), non ancora provata.** Decisa da Nelson il 2026-11-28: coordina l'AI della sessione principale (nessun agente orchestratore, perché ogni passo con effetti richiede l'ok di Nelson nello stesso turno); gli agenti relazionano **prima** del commit e Nelson approva. Vale per i task di `PIANO-RIORGANIZZAZIONE.md` che producono codice o testo (F5, F6); per i dati resta lo schema qui sopra.

### 1. La consegna dichiara i risultati attesi

Prima di avviare un agente, il coordinatore scrive la **scheda del task** e la mostra a Nelson. Senza risultati attesi dichiarati il task non parte. La scheda contiene:

1. **Obiettivo** e riferimento al piano (es. «F5.4, §5»).
2. **Da leggere:** i file che l'agente deve leggere per intero.
3. **Perimetro:** l'elenco esatto dei file che può creare o modificare; tutto il resto è vietato.
4. **Output attesi:** ogni file o comportamento atteso, uno per riga, con un identificativo (`O1`, `O2`…), formulato in modo che si possa dire «c'è / non c'è» (es. «`scripts/checks/check_index.py` esce con 0 sul repo pulito»).
5. **Criteri di accettazione:** i comandi da eseguire e l'esito atteso di ciascuno, compreso **almeno un test negativo** (errore piantato in una copia nello scratchpad, il controllo deve fallire).
6. **Divieti:** niente `docs/data/database.json` salvo dove detto, niente commit, niente push, niente GitHub né servizi esterni salvo dove detto; percorsi personali e segreti mai nei file.
7. **Formato del resoconto** (punto 2).

### 2. L'agente lavora e relaziona, non committa

L'agente lavora in un worktree separato (`isolation: "worktree"`), con il nome di un nano. Alla fine consegna un resoconto con: per ogni output atteso, fatto o non fatto e dove; i comandi eseguiti con l'output reale (non riassunto); i file toccati (`git status` del worktree); ciò che ha fatto in più o in modo diverso dalla scheda, e perché; dubbi e punti deboli. Non deve cambiare un test o un criterio per farlo passare: se un criterio sembra sbagliato, lo dice e si ferma.

### 3. Il coordinatore controlla l'esecuzione, non si fida del resoconto

Per ogni task il coordinatore rifà da sé, nel worktree dell'agente:

1. **Output attesi:** per ogni `O` della scheda, presente o assente, misurato.
2. **Criteri:** rilancia i comandi, compreso il test negativo; l'esito che conta è il suo.
3. **Perimetro (C3):** `git status` e `git diff --name-status` del worktree: nessun file fuori elenco; `git status` del repo principale invariato; nessun push (`git ls-remote`).
4. **Controlli generali:** `validate.py`, `check_site_refs.py`, `check_site_clean.py`, `check_secrets_paths.py`.
5. **Lettura del diff:** il codice o il testo fa ciò che dichiara.
6. **Fedeltà del resoconto:** confronto tra ciò che l'agente ha dichiarato e ciò che è stato misurato.

Poi prepara per Nelson una **tabella del task**: output atteso, esito misurato, scostamenti, punto debole. Nelson approva; solo allora il coordinatore fa il commit (con `Co-Authored-By`), e con un altro ok il push e il testo della PR. Una PR per task.

### 4. Il controllo informa il metodo

Ogni giro chiude con una riga nel **registro dei giri** qui sotto, in tre colonne: **andato bene**, **da rivedere**, **andato male** (con ciò che è accaduto durante il lavoro dell'agente: output mancanti, file fuori perimetro, test cambiati, dichiarazioni non vere, costo in token e tempo). Se una voce di «andato male» o «da rivedere» richiede di cambiare il metodo, la modifica si propone a Nelson e si scrive in questa sezione, con la data.

### Registro dei giri

| Data | Task | Agente | Output attesi raggiunti | Andato bene | Da rivedere | Andato male | Cambio al metodo |
|---|---|---|---|---|---|---|---|
| 2026-11-28 | F6.5, hook di avvio (`.claude/session-status.sh`) | Dotto (worktree, 74.000 token, circa 2,5 minuti, 11 chiamate) | 6 su 6 (O1-O6), confermati dal coordinatore su scenari propri (s1-s8, compresi HEAD staccato e `main` avanti) e su un clone del repo vero; con l'hook vecchio s4 riproduce il difetto («allineato» con `main` indietro), con il nuovo no | perimetro rispettato (un file, nessun commit né push, repo principale invariato); resoconto fedele alle misure; l'agente ha trovato da solo un caso in più (branch indietro dopo un pull fallito) e ha segnalato il contrasto con il piano invece di toccarlo | O4 come scritto nella consegna indicava F0.7, ferma dal 10 novembre: la consegna era giusta alla lettera ma poco utile (cambiato dal coordinatore con l'ok di Nelson: tutte le righe ◐ e la prima ☐); `.claude/worktrees/` non era in `.gitignore`; con HEAD staccato il messaggio dice «branch senza remoto»; costo sopra la stima (30-50.000) | niente di rilevante. Errore del coordinatore, non dell'agente: il branch della PR era partito da `main` senza il commit della #126, che tocca gli stessi documenti (rifatto sopra il branch della #126 prima di qualunque commit) | proposti a Nelson, non ancora approvati: (1) nella consegna, per un output che mostra dati del progetto, provarlo anche sui dati veri in sola lettura prima di dichiararlo atteso; (2) prima di creare il branch della PR, controllare le PR aperte che toccano gli stessi file (regola 0.3 del piano) |
