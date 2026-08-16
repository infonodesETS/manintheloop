# Man in the Loop — Roadmap & To-do

Documento condiviso per tracciare le funzionalità da sviluppare, migliorare o rimuovere.
Aggiornalo dopo ogni sessione di lavoro. Per ogni voce: breve descrizione + priorità.

**Priorità**: 🔴 Alta · 🟡 Media · 🟢 Bassa · ✅ Fatto

---

## In lavorazione

> ⚠️ **Il lavoro in corso è sul branch `eu-funding`, non su `main`.** Ristrutturazione
> della navigazione in due sezioni (Finanziamenti EU / Investimenti globali), ognuna
> con i sotto-tab Mappa / Rete / Numeri chiave. `main` è ancora la versione online e
> non va toccato finché il branch non è pronto.

| # | Funzionalità | Note | Priorità |
|---|---|---|---|
| — | **Testo del box di benvenuto (onboarding)** | Da riscrivere: parla ancora di "Map / Search / Networks", che non esistono più come sezioni. Va adattato alla nuova struttura, in tutte e 4 le lingue (chiavi `onboard.*` in `web/i18n.js`, overlay in `index.html`). **Da fare per ultimo**, quando la ristrutturazione è stabile — è un blocco prima del merge su `main`. | 🔴 |
| — | Report per Paese | Webapp dinamica in `reports/countries/`. Da collegare alla navigazione del sito e da rifinire (i18n, tema chiaro, mobile). | 🟡 |

---

## Da fare — Frontend / UX

| # | Funzionalità | Note | Priorità |
|---|---|---|---|
| 1 | **Espansione progressiva del grafo** (Networks) | Ogni click su un nodo aggiunge le connessioni invece di sostituire la vista. Feature complessa, pianificata per release futura. Tentato breadcrumb come alternativa leggera ma accantonato — meglio affrontare l'espansione completa in una sessione dedicata. | 🟡 |
| 2 | **Classifiche / "Sfoglia"** (Search) | Top 20 beneficiari EDF, per Paese, per settore. Calcolabile client-side dal JSON esistente. | 🟡 |
| 3 | **Filtri avanzati** (Search) | Filtrare per Paese, settore, fonte dati, "ha finanziamenti EDF sì/no". | 🟡 |
| 4 | **Pagina "Scarica i dati / Come citare"** | I dati sono già pubblici ma non presentati come risorsa. CSV/JSON + licenza CC + istruzioni di citazione. | 🟡 |
| 5 | **Revisione sistematica tema chiaro** | Il design è nato dark-first. Verificare ogni pagina in modalità chiara e correggere i punti problematici rimasti. | 🟢 |
| 6 | **Accessibilità colore** (Networks) | Il tipo di nodo è codificato solo col colore. Aggiungere forma/icona per chi è daltonico (~8% degli uomini). | 🟢 |
| 7 | **Mobile** | Garantire che testi, Search e futuri dossier siano usabili da telefono. Mappa e grafi restano "best on desktop". | 🟢 |
| 8 | **Viste preimpostate** (Networks) | Es. "Mostrami i 20 maggiori beneficiari EDF", per ridurre il "gomitolo" iniziale. | 🟢 |

---

## Da fare — Contenuti

| # | Funzionalità | Note | Priorità |
|---|---|---|---|
| 9 | **Dossier pilota** | Una storia breve con mini-rete curata (dati → racconto). Il vero salto editoriale della piattaforma. | 🔴 |
| 10 | **Pagina "Perché"** | 4–5 frasi forti in homepage o About che spiegano perché mappare i finanziamenti alle armi autonome. Già parzialmente in About > Chi siamo. | 🟡 |
| 11 | **Popolare Publications** | La pagina ora legge da `data/publications.json`. Aggiungere le altre ricerche, articoli e inchieste del team o di chi ha usato la piattaforma. | 🟡 |

---

## Da fare — Dati

| # | Funzionalità | Note | Priorità |
|---|---|---|---|
| 12 | **Aggiornamento database** | Prossimo refresh Crunchbase + nuovi EDF calls. | 🔴 |
| 13 | **Aziende mancanti** | Lista "Assenti dal database" da valutare con il Senior Data Expert. | 🟡 |
| 16 | **Correzioni qualità dati** | Emerse dall'analisi Italia: MBDA España ha country Wikidata errato (IN-0863), Idv Defence Vehicles Italia è duplicato di Iveco Defence Vehicles (IN-1431 / IN-0803, stesso PIC), Telecom Italia duplicata, Fincantieri presente sia come azienda sia come investitore. | 🔴 |
| 14 | **Incrocio con OpenSanctions** | Segnalare se un'entità è sanzionata o "di interesse". Effort medio, manutenzione periodica leggera. | 🟢 |

---

## Fase 2 — Chatbot

| # | Funzionalità | Note | Priorità |
|---|---|---|---|
| 15 | **Assistente conversazionale** | Domande in linguaggio naturale sul database ("quali aziende italiane hanno ricevuto fondi EDF?"). Riusa infrastruttura MARLA. Introduce costi API ricorrenti — trattare come progetto separato. | 🟢 |

---

## ✅ Completato

| Funzionalità | Data |
|---|---|
| Report Italia + webapp report per Paese (`reports/countries/`) | 2026-08-11 |
| Publications data-driven da `data/publications.json` | 2026-08-11 |
| Hook SessionStart: git fetch+pull automatico all'apertura sessione | 2026-08-11 |
| Overlay onboarding prima visita (4 lingue) | 2026-06-30 |
| About: ristrutturazione in 4 sotto-sezioni (Chi siamo / Metodologia / Glossario / Contribuisci) | 2026-06-30 |
| About: sezione Limiti (metodologici e dei dati) | 2026-06-30 |
| Glossario data-driven da `data/glossary_terms.json` | 2026-06-30 |
| Testo "Perché" data-driven da `data/about_why.json` | 2026-06-30 |
| Data ultimo aggiornamento da `data/last_update.json` | 2026-06-30 |
| Map: modalità EDF Funding (cerchi per finanziamento, zoom EU, panel entità) | 2026-06-23 |
| Networks: tooltip informativi su checkbox EDF / Investments | 2026-06-23 |
| Export PNG su Map e Networks, PDF one-click in Search | 2026-06-23 |
| Etichette nodi Networks colorate per tipo (leggibili in tema chiaro) | 2026-06-23 |
| Fix Search: box e autocomplete visibili in tema chiaro | 2026-06-23 |
