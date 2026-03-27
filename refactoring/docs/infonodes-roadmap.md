# Roadmap di implementazione — infonodes

_Generato da: analisi delle sessioni di user test (Davide, Andrea, Laura) — 2026-03-27_
_Fonte issue: `docs/infonodes-issues.md`_

---

## Logica di clusterizzazione

Le 59 issue sono state raggruppate per **area di intervento** (non per utente), con l'obiettivo di massimizzare la coerenza degli sprint e minimizzare i conflitti tra file. Il piano di implementazione è organizzato in **fasi sequenziali** con alcune attività in parallelo.

Un vincolo strutturale domina tutta la roadmap:

> **#03 (unificazione database)** è un prerequisito per la riorganizzazione della navigazione, il merge Companies+Investors, la revisione dei colori del grafo, e la rimozione del gruppo EDF. Va pianificato come progetto separato. Tutto il resto può procedere prima o in parallelo.

---

## Cluster di intervento

### Cluster A — Bug immediati
_File toccati: `js/tabs/map.js`, `js/tabs/graph.js`, `js/tabs/eucalls.js`, `js/main.js`_

| # | Titolo | Priorità |
|---|---|---|
| #11 | Map: chiusura sidebar senza clear → stato inconsistente | High |
| #12 | Graph: tooltip persiste navigando ad altre tab | Medium |
| #47 | EDF Calls Search: label "pattern:" visibile nei risultati | Low |
| #55 | Graph: nessun auto-zoom dopo cambio filtro/modalità | Medium |

Questi bug sono indipendenti da tutto il resto e andrebbero risolti prima di qualsiasi altra cosa. #11 è il più critico perché lascia la mappa in uno stato irrecuperabile senza reload.

---

### Cluster B — Tipografia e contrasto (globale)
_File toccati: `css/base.css`_

| # | Titolo | Priorità |
|---|---|---|
| #35 | Font weight troppo thin, difficile da leggere | High |
| #36 | Light mode: contrasto testo/sfondo insufficiente | High |
| #52 | Data Issues tab: font fuori scala rispetto alle altre pagine | Low |

Un solo file (`css/base.css`), tre token da aggiustare (`--font-weight-body`, `--text-dim`, token light mode). Alto impatto, rischio quasi zero, risolve una delle lamentele più forti (Laura). Da fare subito dopo i bug.

---

### Cluster C — Company Search: UX e chiarezza dati
_File toccati: `js/tabs/companysearch.js`, `css/companysearch.css`_

| # | Titolo | Priorità |
|---|---|---|
| #23 | Empty state senza suggerimenti — onboarding bloccato | High |
| #24 | Tag industry/sector non cliccabili per filtrare | Medium |
| #33 | Link sito ufficiale azienda — decisione editoriale | Low |
| #37 | Validation flags interni ("needs review") visibili agli utenti | High |
| #38 | Tooltip Relationships hard to trigger | Low |
| #50 | Portfolio count non cliccabile / non espande la lista | Medium |
| #59 | Entity ID (IV-0143) senza label — sembra ID utente | Low |

Cluster autocontenuto in un solo modulo. Il più urgente è #37 (nascondere i flag interni): è l'unico elemento che mina attivamente la credibilità del dato agli occhi dell'utente finale.

---

### Cluster D — Supply Chain Map: interazione e visibilità
_File toccati: `js/tabs/map.js`, `css/map.css`, `css/base.css` (token light)_

| # | Titolo | Priorità |
|---|---|---|
| #07 | Legenda archi assente o incomprensibile | High |
| #08 | Colori archi troppo chiari (dark mode) | Medium |
| #09 | Mostrare una sola direzione di flusso per click paese | High |
| #10 | Testo panel paese non chiaro | Medium |
| #41 | Light mode: colori slavati, poca leggibilità | High |
| #42 | Interazione semplificata: solo sorgenti → rivela destinazioni al click | Medium |
| #43 | Click area vuota mappa per deselezionare | Low |

Il cuore del problema mappa è #09/#42: tre utenti su tre non hanno capito cosa mostrano gli archi. La direzione convergente è: default = punti sorgente visibili, click = archi in uscita verso destinazioni, toggle per invertire. #07 (legenda) è il complemento testuale di questo redesign.

---

### Cluster E — Graph: UX, toolbar, interazione
_File toccati: `js/tabs/graph.js`, `css/graph.css`, `index.html`_

| # | Titolo | Priorità |
|---|---|---|
| #13 | Colori insufficienti per distinguere tipi investitore | Medium |
| #44 | Gravity non lascia i nodi dove li trascina l'utente | Medium |
| #45 | Toolbar: nessun separatore tra tipo vista e tipo settore | Medium |
| #56 | Bipartite mode non abbastanza spiegata | Medium |
| #57 | Panel "How to explore" a destra, controlli altrove — incoerenza | Medium |

#45 è una modifica CSS/HTML di 10 minuti (un divisore + due label di gruppo) con impatto alto sulla leggibilità della toolbar. #44 richiede una modifica alla D3 force simulation. #13 dipende parzialmente da #03 (lista definitiva tipi entità).

---

### Cluster F — Navigabilità continua (entità cliccabili ovunque)
_File toccati: `js/tabs/map.js`, `js/tabs/graph.js`, `js/tabs/edfbrowse.js`, `js/tabs/relationships.js`_

| # | Titolo | Priorità |
|---|---|---|
| #25 | Map: nomi aziende nel country panel non portano alla scheda | High |
| #26 | Graph: nomi investitori nel node panel non cliccabili | High |
| #27 | Graph Projection: panel mostra contesto sbagliato | Medium |
| #28 | Graph Projection: nomi portfolio non cliccabili | Medium |
| #31 | Dead ends generali — navigazione Wikipedia-style assente | High |
| #32 | SC Overview: stat card non cliccabili per filtrare | Medium |

Questo cluster rappresenta il problema sistemico più segnalato (tutti e tre gli utenti): la navigazione si interrompe. Il pattern di fix è uniforme — ogni nome entità in qualsiasi contesto diventa un `<button data-entity-id>` che chiama `selectEntity()` di Company Search o `openCompanySidebar()`. È ripetitivo ma meccanico.

---

### Cluster G — Copy for AI: utilità e contesto
_File toccati: `js/copy-ai.js`, tutti i tab module con snapshot_

| # | Titolo | Priorità |
|---|---|---|
| #19 | Wikidata Inspector: aggiungere export/copia dati | Medium |
| #21 | Label "Copy for AI" non autoesplicativa | Medium |
| #29 | Output non contestuale alla view/filtro attivo | High |
| #34 | Rename pulsante (cross-ref #21) | Medium |

#29 è il più impattante: in questo momento Copy for AI esporta sempre un dump globale. Ogni tab deve esporre una `buildSnapshot(context)` che produce il testo rilevante per lo stato corrente (filtri applicati, entità selezionata, modalità grafo attiva).

---

### Cluster H — EDF Beneficiaries: sidebar e filtri
_File toccati: `js/tabs/edfbrowse.js`, `css/edfbrowse.css`_

| # | Titolo | Priorità |
|---|---|---|
| #16 | Sidebar difficile da leggere, layout da ripulire | Medium |
| #17/#30 | Nessun filtro capofila vs. partecipante | Medium |
| #46 | Sidebar troppo piccola → aprire come modal/area principale | Medium |
| #49 | EDF Map: click area vuota per deselezionare | Low |

#16 e #46 vanno risolti insieme: non ha senso ripulire la sidebar se si decide di trasformarla in modal. La decisione architetturale (sidebar wide vs modal) sblocca entrambe.

---

### Cluster I — Sistema sidebar: posizione globale
_File toccati: `css/components.css`, `js/detail-sidebar.js`, `css/map.css`, `css/graph.css`_

| # | Titolo | Priorità |
|---|---|---|
| #40 | Tutti i panel laterali a sinistra (convenzione Google Maps) | Medium |

Un'unica issue, ma trasversale a tutti i panel del sito. Va valutata con attenzione prima di implementare: spostare la sidebar a sinistra richiede di verificare che non copra elementi critici su ogni tab. **Proposta: fare un test A/B con due utenti prima di implementare definitivamente.**

---

### Cluster J — Sanity check dati
_File toccati: `data/database.json`, `scripts/validate.py`_

| # | Titolo | Priorità |
|---|---|---|
| #05 | Anduril e iSci: numero investitori anomalo rispetto all'export | High |
| #06 | Nomi aziende e paesi non normalizzati (Leonardo vs SPA, China vs Cina) | High |
| #58 | Disclaimer copertura dati per paesi non trasparenti | Medium |

Lavoro non tecnico (nessun JS). #05 richiede audit delle relazioni `REL-*` nel database. #06 richiede una passata manuale su `name` e `country`. #58 è un testo da aggiungere in Company Search.

---

### Cluster K — Contenuto editoriale
_File toccati: `index.html`, `docs/data-issues.md`, testi UI_

| # | Titolo | Priorità |
|---|---|---|
| #01 | Intro page: testi da riscrivere (lavoro di Davide) | High |
| #18 | About: rewrite con team, finanziatori, metodologia | Medium |
| #39 | Colori paesi: connotazione politica indesiderata (rosso Cina/Russia) | Medium |
| #51 | Investigation page: rimuovere o riproporre come sezione ricerca | Low |
| #53 | Data Quality: riscrivere per trasparenza metodologica | Low |

#01 è editoriale puro (Davide scrive i testi). #39 è una modifica CSS a una palette colori. #51 è una modifica nav + rimozione della pagina automatizzata.

---

### Cluster L — Architettura (macro, pianificare separatamente)
_File toccati: tutto — `data/`, `js/data.js`, `js/edf-data.js`, `js/main.js`, `js/state.js`, nav_

| # | Titolo | Priorità |
|---|---|---|
| #03 | Unificazione database EDF + SC in file unico | High |
| #04 | Rinominare gruppo "Supply Chain" | Low |
| #14 | Merge Companies + Investors in tab "Players" | Medium |
| #15/#48 | Matrix: tentare semplificazione, poi decidere rimozione | Low |
| #20 | Wikidata live data integrato in Company Search | Medium |
| #22 | EDF Calls Search: nascondere nella release finale | Low |
| #54 | Wikidata Inspector: portare in evidenza nel menu | Low |
| #02 | CS come landing page default (decisione da validare) | Low |

**#03 è il bloccante principale.** Una volta unificato il database, #04, #14, e la riorganizzazione della nav seguono come conseguenza diretta. Tutto il resto del cluster dipende da #03.

---

## Piano di implementazione

### Fase 0 — Bug fix (subito, ~1 giorno)
_Nessun prerequisito. Rischio minimo._

| Issue | Fix |
|---|---|
| **#12** | Cleanup tooltip in `main.js` alla navigazione |
| **#47** | Rimuovere prefisso "pattern:" da template `eucalls.js` |
| **#55** | Auto-zoom in `graph.js` dopo cambio filtro/modalità |
| **#11** | Investigare con Playwright + sync state mappa/sidebar in `map.js` |

---

### Fase 1 — Quick wins globali (~2 giorni)
_Un file (`css/base.css`) + piccole patch in `companysearch.js`._

1. **#35 + #36** — Aumentare `font-weight` body text; rivedere token contrasto light mode in `base.css`
2. **#37** — Nascondere flag `needs_review`/`flagged` in Company Search; aggiungere disclaimer generico
3. **#21/#34** — Rinominare "Copy for AI" → label più chiara + tooltip esplicativo
4. **#52** — Allineare font Data Issues tab ai token standard
5. **#59** — Aggiungere label/tooltip su Entity ID in scheda entità
6. **#39** — Sostituire colori politicamente connotati (rosso Cina/Russia) con palette per continente

---

### Fase 2 — Company Search: completamento UX (~2 giorni)
_Autocontenuto in `companysearch.js` / `companysearch.css`._

1. **#23** — Empty state con suggested companies (chip cliccabili, 4-6 esempi)
2. **#50** — Portfolio count cliccabile / inline-expandable
3. **#24** — Industry tag cliccabili → avvia ricerca filtrata
4. **#58** — Aggiungere disclaimer copertura dati per paesi con scarsa trasparenza
5. **#33** — Decisione: rimuovere link sito ufficiale, mantenere Wikipedia + Crunchbase

---

### Fase 3 — Supply Chain Map: redesign interazione (~3 giorni)
_`map.js` + `css/map.css` + token light mode in `base.css`._

1. **#09 + #42** — Nuovo modello interazione: default = solo sorgenti; click → archi in uscita + evidenzia destinazioni; toggle flowing-in/out
2. **#07** — Legenda inline permanente (non nascosta nel panel)
3. **#08 + #41** — Aumentare contrasto archi (dark e light mode)
4. **#10** — Riscrivere testo panel paese con formula chiara
5. **#43** — Click su area vuota mappa → deselect paese

---

### Fase 4 — Graph: UX e toolbar (~2 giorni)
_`graph.js` + `css/graph.css`._

1. **#45** — Aggiungere separatore visivo toolbar (Vista | Settore) — 10 minuti
2. **#57** — Riposizionare "How to explore" per coerenza spaziale con i controlli
3. **#56** — Aggiungere descrizione contestuale per Bipartite mode
4. **#44** — Implementare pin nodo on drag-end (D3 `node.fx/fy`)
5. **#27** — Chiudere panel entità al cambio modalità verso Projection

---

### Fase 5 — Navigabilità continua (~3 giorni)
_Patch distribuite su `map.js`, `graph.js`, `edfbrowse.js`, `overview.js`._

1. **#25** — Nomi aziende cliccabili nel country panel (map)
2. **#26 + #28** — Nomi investitori e portfolio cliccabili nel node panel (graph)
3. **#32** — SC Overview: stat card cliccabili → navigazione a Companies filtrata
4. **#31** — Audit sistematico: identificare tutti i contesti dove appaiono nomi entità non cliccabili

Questa fase richiede una decisione architetturale: il click su un'entità in qualsiasi contesto deve portare sempre alla stessa destinazione (Company Search `selectEntity()`). Definire questa convention prima di iniziare.

---

### Fase 6 — Copy for AI contestuale (~2 giorni)
_`js/copy-ai.js` + aggiornamenti snapshot in ogni tab module._

1. **#29** — Refactoring `buildAiSnapshot()`: ogni tab espone `buildSnapshot(context)` con filtri + stato corrente
2. **#19** — Aggiungere export dati in Wikidata Inspector

---

### Fase 7 — EDF Beneficiaries redesign (~2 giorni)
_`edfbrowse.js` + `css/edfbrowse.css`._

1. **#16 + #46** — Decidere sidebar wide vs modal → implementare il formato scelto con layout gerarchico
2. **#17** — Aggiungere filtro capofila / partecipante
3. **#49** — Click area vuota EDF Map → deselect paese

---

### Fase 8 — Sidebar a sinistra (decisione + implementazione, ~1 giorno)
_Dopo test A/B con utenti. `css/components.css`, `detail-sidebar.js`, CSS tab-specifici._

1. **#40** — Spostare tutti i panel laterali a sinistra se il test conferma la preferenza

---

### Fase 9 — Sanity check dati (parallelo, non tecnico)
_`data/database.json`, `scripts/validate.py`. Non blocca nessuna fase tecnica._

1. **#05** — Audit relazioni REL-* di Anduril e iSci; verificare origine degli investitori extra
2. **#06** — Normalizzazione nomi aziende e campi country

---

### Fase 10 — Contenuto editoriale (parallelo, non tecnico)
_Testi UI, `index.html`, `docs/`._

1. **#01** — Testi intro (Davide)
2. **#18** — About rewrite (team, finanziatori, metodologia)
3. **#51** — Rimuovere Investigation automatica / creare placeholder sezione Ricerca
4. **#53** — Revisione Data Quality per trasparenza metodologica

---

### Fase 11 — Architettura macro (progetto separato)
_Pianificare in una sessione dedicata dopo aver completato le fasi precedenti._

1. **#03** — Unificazione `database.json` + `edf_calls.json` in sorgente unica
2. **#04** — Rinomina gruppi nav (conseguenza di #03)
3. **#14** — Merge Companies + Investors → "Players"
4. **#13** — Revisione colori Graph (con lista definitiva tipi entità)
5. **#22** — Nascondere EDF Calls Search dalla nav finale
6. **#20** — Wikidata live data in Company Search
7. **#54** — Wikidata Inspector in evidenza nel menu
8. **#15/#48** — Decisione finale su Matrix
9. **#02** — Decidere landing page default

---

## Riepilogo per priorità

| Fase | Issue | Giorni stimati | Dipendenze |
|---|---|---|---|
| **0** — Bug | #11 #12 #47 #55 | ~1 | nessuna |
| **1** — Quick wins | #35 #36 #37 #21 #52 #59 #39 | ~2 | nessuna |
| **2** — Company Search | #23 #50 #24 #58 #33 | ~2 | nessuna |
| **3** — Map redesign | #09 #42 #07 #08 #41 #10 #43 | ~3 | nessuna |
| **4** — Graph UX | #45 #57 #56 #44 #27 | ~2 | nessuna |
| **5** — Navigabilità | #25 #26 #28 #32 #31 | ~3 | fase 2 (convention CS) |
| **6** — Copy for AI | #29 #19 | ~2 | fase 5 |
| **7** — EDF Beneficiaries | #16 #46 #17 #49 | ~2 | nessuna |
| **8** — Sidebar sinistra | #40 | ~1 | test A/B |
| **9** — Dati (parallelo) | #05 #06 | continuo | nessuna |
| **10** — Editoriale (parallelo) | #01 #18 #51 #53 | continuo | nessuna |
| **11** — Architettura | #03 + cascata | progetto separato | tutto il resto |

**Issue non assegnate a fasi (decisioni in sospeso):** #02 (landing page), #13 (graph colors post-DB unification).
