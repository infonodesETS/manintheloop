# Database e dati di Man in the Loop

Inventario delle fonti di dati della piattaforma: **cosa visualizziamo oggi** e **cosa vogliamo integrare in futuro**.
Documento di lavoro interno — da aggiornare quando cambiano i dati o la roadmap.

- **Ultimo aggiornamento di questo documento:** 2026-11-27
- **Fotografia dei dati (`database.json`):** schema 3.0, aggiornato al 2026-11-22 (re-import della release SEC 2026-11-21)

---

## 1. In sintesi

| | |
|---|---|
| Nodi nel grafo | **2.734**, di cui **2.691 attivi** e 43 schede ritirate (duplicati uniti in B3) |
| Relazioni totali | **3.994** |
| Fonti di dati attive | **6** (iShares, Crunchbase, infonodes, Wikidata, EDF, SEC-EDGAR) |
| Dati SEC nel grafo | quote oltre il 5% (Release 1) e ruoli delle persone che le detengono; il resto della release SEC è raccolto ma non ancora importato (§5) |

---

## 2. Il database attuale (il grafo)

Il cuore della piattaforma è un **database a grafo** in `docs/data/database.json`: nodi (entità) collegati da archi (relazioni). Lo schema è descritto in dettaglio in [`reference/SCHEMA.md`](SCHEMA.md).

### Entità (i nodi) — 2.691 attive

Conteggi sulle entità attive: le 43 schede ritirate (unioni di duplicati, con `entity_retired` nella `history`) restano nel file ma non sono mostrate.

| Tipo | Numero | Cosa rappresenta |
|---|---:|---|
| `company` | 1.404 | Aziende: produttori, startup, aziende tech, minerarie |
| `investor` | 463 | Soggetti che investono (93 creati dall'import SEC: i gestori che dichiarano quote oltre il 5%) |
| `fund` | 290 | Fondi: VC, private equity, family office, corporate VC, acceleratori |
| `institution` | 248 | Università, think tank, fondazioni |
| `edf_project` | 129 | Progetti del Fondo Europeo per la Difesa |
| `person` | 59 | Persone (`PER-`) con una quota oltre il 5% in un'azienda quotata USA, dalla SEC |
| `public_fund` | 52 | Fondi pubblici |
| `government_agency` | 42 | Agenzie governative (EDF, BEI, NATO, agenzie nazionali…) |
| `bank` | 4 | Banche commerciali/d'investimento |

### Relazioni (gli archi) — 3.994

| Tipo | Numero | Cosa collega |
|---|---:|---|
| `edf_participation` | 2.239 | Aziende/enti ⇄ progetti EDF a cui partecipano |
| `investment` | 1.158 | Investitore ⇄ azienda partecipata (Crunchbase) |
| `ownership` | 548 | Titolare (gestore, azienda o persona) ⇄ azienda di cui ha almeno il 5% del capitale o dei voti (SEC, proxy) |
| `role` | 49 | Persona ⇄ azienda in cui ha cariche (consigliere, dirigente), una relazione per coppia con le cariche dentro (SEC) |

Le quote che vengono dalla stessa riga del documento SEC (una posizione congiunta, come Charles Liang e Sara Liu in SMCI, o un titolare con più classi di azioni) portano `riga_documento` e si contano una volta sola: regola in [`SCHEMA.md`](SCHEMA.md). Le relazioni `parte_di` (legame di gruppo) sono previste dallo schema ma non ancora nei dati.

---

## 3. Le fonti dei dati (da dove vengono)

Ogni entità porta con sé la provenienza dei suoi dati, nel blocco `sources`. Le fonti oggi attive:

| Fonte | Cosa fornisce | Entità coperte | Come si aggiorna |
|---|---|---:|---|
| **iShares (ETF)** | Universo di partenza: le aziende presenti in 4 ETF settoriali di BlackRock/iShares, con settore GICS, peso, borsa, Paese | 509 | Export CSV degli ETF |
| **Crunchbase** | Profilo azienda: descrizione, settori/industrie, sede, fondatori, round e importi di finanziamento, principali investitori | 922 | Import da export CSV (`scripts/import_crunchbase_csv.py`) |
| **infonodes** | Arricchimento interno/manuale: settore, Paese, identificativo fiscale e note del team | 2.057 | A mano, dal team |
| **Wikidata** | Identificativo univoco (QID) e collegamenti all'anagrafica aperta | 899 blocchi (894 entità con QID) | Lookup su Wikidata |
| **EDF** | Partecipazione ai progetti del Fondo Europeo per la Difesa + anagrafica dei progetti (acronimo, obiettivo, call, budget, link ufficiale) | 1.056 + 129 progetti | Dati EDF |
| **SEC-EDGAR** | Quote oltre il 5% e ruoli delle persone che le detengono, dai proxy (DEF 14A) di 161 aziende quotate USA; CIK delle persone dai Form 3, 4 e 5 | 152 (59 persone, 93 gestori) | Release di Andrea in `rawdata/sec-edgar/<data>/`, import con `scripts/import_sec_ownership.py` (release 2026-10-17 il 2026-11-18, release 2026-11-21 il 2026-11-22) |

Entità coperte = entità attive con il blocco della fonte non vuoto (misura del 2026-11-27).

**Gli ETF iShares usati come universo di partenza:**

| ETF | Settore | Aziende |
|---|---|---:|
| PICK | Metalli & mining | 243 |
| IXN | Tecnologia | 126 |
| DFND | Aerospazio & difesa | 77 |
| IXP | Servizi di comunicazione | 65 |

---

## 4. Cosa visualizza la piattaforma (le pagine)

| Pagina | Cosa mostra | Dati usati |
|---|---|---|
| **Map** (`docs/index.html`) | Il grafo navigabile, in due modalità: **Finanziamenti EU** (chi partecipa a quali progetti EDF) e **Investimenti globali** (chi investe in chi) | `database.json` (relazioni `edf_participation` e `investment`; `ownership` e `role` escluse per scelta, S4 regola 4) |
| **Networks** (`docs/networks.html`) | Viste di rete/connessioni tra gli attori | `database.json` |
| **Key Figures** (`docs/key-figures.html`) | Numeri e cifre chiave della mappatura | `database.json` |
| **Search** (`docs/search.html`) | Ricerca libera tra entità; nella scheda di un'azienda i riquadri SEC «Shareholders ≥5%» e «Holdings ≥5%» | `database.json`; le persone non hanno una scheda propria e non compaiono nella ricerca; nei riquadri SEC i nomi non si aprono ancora con un clic (issue #118) |
| **Publications** (`docs/publications.html`) | Articoli, inchieste e report prodotti con/su la piattaforma | `docs/data/publications.json` |
| **About** (`docs/about.html`) | Metodo, scopo e contesto del progetto | `docs/data/about_why.json` |

**Dati di supporto** (non una vista a sé): `defence_criteria.json` (perimetro "defence tech"), `glossary.json` / `glossary_terms.json` (glossario), `edf_orgs.json`, `last_update.json` (data dei dati mostrata in About: 22/11/2026), `mitl-index.json` (indice del chatbot MARLA, rigenerato il 2026-11-27 con `scripts/build_chat_index.py`; le quote e i ruoli vi compaiono senza percentuali né cariche).

---

## 5. Dati raccolti ma non ancora visualizzati

| Dataset | Cosa contiene | Dove si trova | Stato |
|---|---|---|---|
| **SEC-EDGAR, Release 2** | Per 161 aziende quotate negli USA: consigli di amministrazione (1.601 consiglieri), comitati, dirigenti (994), azioni di dirigenti/consiglieri; delle circa 2.300 persone ne sono importate solo le 59 con una quota oltre il 5% | `rawdata/sec-edgar/2026-11-21/` (in `main`, non servito dal sito) | Raccolto; da importare dopo l'approvazione del vocabolario dei ruoli |
| **SEC-EDGAR, transazioni degli insider** | 57.528 transazioni su azioni dai Form 4 e 5, dal quarto trimestre 2024 al terzo del 2026 (`transazioni-insider.csv`, issue #25) | `rawdata/sec-edgar/2026-11-21/` | Raccolto; serve una decisione di schema prima di importarle |

---

## 6. Da integrare in futuro (roadmap dati)

> Sezione da completare con le priorità del team. Le prime due voci sono già in lavorazione o pronte; le righe `[…]` sono da riempire con le tue idee.

| Database / dato | Cosa aggiungerebbe alla piattaforma | Fonte | Stato | Priorità |
|---|---|---|---|---|
| **Consigli, dirigenti e azionisti USA** | Collega persone (board, manager) e azionisti >5% alle aziende → relazioni `role` e `ownership` | SEC-EDGAR (vedi §5) | Azionisti oltre il 5% importati (Release 1); consigli e dirigenti da importare (Release 2) | — |
| **Partecipazioni rilevanti in Europa** | Quote dei grandi investitori (es. BlackRock) nelle aziende europee della difesa, che il 13F USA non copre | Registri di trasparenza delle autorità nazionali UE/SEE/UK/CH | Fonti mappate | — |
| **Finanziamenti EU** | Finanziamenti da fondi/programmi pubblici europei | Horizon Europe | in corso | alta |
| **Finanziamenti EU** | Finanziamenti da fondi/programmi pubblici europei | PESCO | idea | media |
| **Finanziamenti EU** | Finanziamenti da fondi/programmi pubblici europei | EDIP (European Defence Industry Programme) | idea | media |
| **Finanziamenti EU** | Finanziamenti da fondi/programmi pubblici europei | EUDIS (EU Defence Innovation Scheme) | idea | media |
| **Finanziamenti EU** | Finanziamenti da fondi/programmi pubblici europei | EIF (European Investment Fund) | idea | media |
| **Finanziamenti NATO** | Finanziamenti da fondi NATO | DIANA (Defence Innovation Accelerator for the North Atlantic) | idea | media |
| **Finanziamenti NATO** | Finanziamenti da fondi NATO | NIF (NATO Innovation Fund) | idea | media |
| **Contratti con PA italiana** | Contratti o finanziamenti ricevuti in Italia | Banca Dati Nazionale dei Contratti Pubblici (ANAC) | idea | media |
| **Contratti con PA europee** | Contratti o finanziamenti ricevuti in Europa | Opentender | idea | media |
| **Contratti negli USA** | Contratti pubblici siglati negli USA | USAspending.gov | idea | bassa |
| **Contratti negli USA** | Contratti militari siglati negli USA | SAM.gov | idea | bassa |

---

## 7. Note

- **Conteggi**: riferiti alla fotografia di `database.json` del 2026-11-22, misurati il 2026-11-27 (`validate.py`: 2.734 entità, 3.994 relazioni). Vanno ricalcolati a ogni aggiornamento dei dati.
- **Provenienza**: ogni entità conserva in `sources` da dove viene ciascun dato; questo permette di verificare e citare le fonti.
- **Schema completo**: [`reference/SCHEMA.md`](SCHEMA.md). Protocollo di aggiornamento: [`reference/UPDATE_PROTOCOL.md`](UPDATE_PROTOCOL.md).
