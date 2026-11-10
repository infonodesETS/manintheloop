# Database e dati di Man in the Loop

Inventario delle fonti di dati della piattaforma: **cosa visualizziamo oggi** e **cosa vogliamo integrare in futuro**.
Documento di lavoro interno — da aggiornare quando cambiano i dati o la roadmap.

- **Ultimo aggiornamento di questo documento:** 2026-10-26
- **Fotografia dei dati (`database.json`):** schema 3.0, aggiornato al 2026-10-19

---

## 1. In sintesi

| | |
|---|---|
| Nodi totali nel grafo | **2.582** |
| Relazioni totali | **3.490** |
| Fonti di dati attive | **5** (iShares, Crunchbase, infonodes, Wikidata, EDF) |
| Dataset raccolti ma non ancora visualizzati | **1** (SEC-EDGAR) |

---

## 2. Il database attuale (il grafo)

Il cuore della piattaforma è un **database a grafo** in `data/database.json`: nodi (entità) collegati da archi (relazioni). Lo schema è descritto in dettaglio in [`docs/SCHEMA.md`](SCHEMA.md).

### Entità (i nodi) — 2.582

| Tipo | Numero | Cosa rappresenta |
|---|---:|---|
| `company` | 1.422 | Aziende: produttori, startup, aziende tech, minerarie |
| `investor` | 393 | Soggetti che investono |
| `fund` | 292 | Fondi: VC, private equity, family office, corporate VC, acceleratori |
| `institution` | 248 | Università, think tank, fondazioni |
| `edf_project` | 129 | Progetti del Fondo Europeo per la Difesa |
| `public_fund` | 52 | Fondi pubblici |
| `government_agency` | 42 | Agenzie governative (EDF, BEI, NATO, agenzie nazionali…) |
| `bank` | 4 | Banche commerciali/d'investimento |

### Relazioni (gli archi) — 3.490

| Tipo | Numero | Cosa collega |
|---|---:|---|
| `edf_participation` | 2.313 | Aziende/enti ⇄ progetti EDF a cui partecipano |
| `investment` | 1.177 | Investitore ⇄ azienda partecipata |

---

## 3. Le fonti dei dati (da dove vengono)

Ogni entità porta con sé la provenienza dei suoi dati, nel blocco `sources`. Le fonti oggi attive:

| Fonte | Cosa fornisce | Entità coperte | Come si aggiorna |
|---|---|---:|---|
| **iShares (ETF)** | Universo di partenza: le aziende presenti in 4 ETF settoriali di BlackRock/iShares, con settore GICS, peso, borsa, Paese | 511 | Export CSV degli ETF |
| **Crunchbase** | Profilo azienda: descrizione, settori/industrie, sede, fondatori, round e importi di finanziamento, principali investitori | 929 | Import da export CSV (`scripts/import_crunchbase_csv.py`) |
| **infonodes** | Arricchimento interno/manuale: settore, Paese, identificativo fiscale e note del team | 2.226 | A mano, dal team |
| **Wikidata** | Identificativo univoco (QID) e collegamenti all'anagrafica aperta | 961 | Lookup su Wikidata |
| **EDF** | Partecipazione ai progetti del Fondo Europeo per la Difesa + anagrafica dei progetti (acronimo, obiettivo, call, budget, link ufficiale) | 1.059 + 129 progetti | Dati EDF |

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
| **Map** (`index.html`) | Il grafo navigabile, in due modalità: **Finanziamenti EU** (chi partecipa a quali progetti EDF) e **Investimenti globali** (chi investe in chi) | `database.json` (relazioni `edf_participation` e `investment`) |
| **Networks** (`networks.html`) | Viste di rete/connessioni tra gli attori | `database.json` |
| **Key Figures** (`key-figures.html`) | Numeri e cifre chiave della mappatura | `database.json` |
| **Search** (`search.html`) | Ricerca libera tra entità | `database.json` / indice di ricerca |
| **Publications** (`publications.html`) | Articoli, inchieste e report prodotti con/su la piattaforma | `data/publications.json` |
| **About** (`about.html`) | Metodo, scopo e contesto del progetto | `data/about_why.json` |

**Dati di supporto** (non una vista a sé): `defence_criteria.json` (perimetro "defence tech"), `glossary.json` / `glossary_terms.json` (glossario), `edf_orgs.json`, `last_update.json`, `mitl-index.json`.

---

## 5. Dati raccolti ma non ancora visualizzati

| Dataset | Cosa contiene | Dove si trova | Stato |
|---|---|---|---|
| **SEC-EDGAR** | Per 161 aziende quotate negli USA: consigli di amministrazione (1.601 consiglieri), comitati, dirigenti (994), azionisti oltre il 5% (571), azioni di dirigenti/consiglieri | ramo `v.2026-c`, cartella `rawdata/sec-edgar/2026-10-17/` | Raccolto e sistematizzato; **da integrare nel grafo e nelle viste** |

---

## 6. Da integrare in futuro (roadmap dati)

> Sezione da completare con le priorità del team. Le prime due voci sono già in lavorazione o pronte; le righe `[…]` sono da riempire con le tue idee.

| Database / dato | Cosa aggiungerebbe alla piattaforma | Fonte | Stato | Priorità |
|---|---|---|---|---|
| **Consigli, dirigenti e azionisti USA** | Collega persone (board, manager) e azionisti >5% alle aziende → nuove relazioni "siede nel consiglio di", "è azionista di" | SEC-EDGAR (vedi §5) | Dati pronti su `v.2026-c` | — |
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

- **Conteggi**: riferiti alla fotografia di `database.json` del 2026-10-19. Vanno ricalcolati a ogni aggiornamento dei dati.
- **Provenienza**: ogni entità conserva in `sources` da dove viene ciascun dato; questo permette di verificare e citare le fonti.
- **Schema completo**: [`docs/SCHEMA.md`](SCHEMA.md). Protocollo di aggiornamento: [`docs/UPDATE_PROTOCOL.md`](UPDATE_PROTOCOL.md).
