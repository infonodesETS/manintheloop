# Man in the Loop — Roadmap & To-do

Documento condiviso per tracciare le funzionalità da sviluppare, migliorare o rimuovere.
Aggiornalo dopo ogni sessione di lavoro. Per ogni voce: breve descrizione + priorità.

**Priorità**: 🔴 Alta · 🟡 Media · 🟢 Bassa · ✅ Fatto

---

## In lavorazione

> ✅ **Merge fatto (settembre 2026):** la ristrutturazione EU Funding / Global
> Investments è stata mergiata in `main`, che è ora la **versione online stabile**.
> Il nuovo sviluppo prosegue sul branch **`v.2026-c`** — si lavora lì, non su `main`.

### 🚧 v.2026-c — Espansione del database con dati SEC  *(branch `v.2026-c`)*

Nuove fonti (portale **SEC / EDGAR**) e nuovi tipi di dati. **Spec completa e schema:
[`docs/dev-v2026c-sec.md`](docs/dev-v2026c-sec.md).**

| Release | Cosa | Scadenza | Priorità |
|---|---|---|---|
| **Release 1** | Quote di partecipazione **> 5%** detenute da **Fondi / Società / Persone** nelle **aziende quotate già nel DB**. Nuova relazione `ownership`. | **entro 15 nov 2026** | 🔴 |
| **Release 2** | **Persone con ruoli apicali** (founder, presidenti, direttori, CEO, board…) in aziende, fondi, università e tutti i soggetti mappati. Nuovo tipo entità `person` + relazione `role`. | **dal 15 nov 2026** | 🔴 |

> Decisione da prendere insieme prima dell'import di massa: schema delle persone
> (id, deduplica via CIK), vocabolario dei ruoli, storicità delle quote. Dettagli
> nel documento di spec.

---

## Altre voci in lavorazione

| # | Funzionalità | Note | Priorità |
|---|---|---|---|
| — | **Check manuale aziende defence tech** | Il selettore "Perimetro" in Numeri chiave (Investimenti globali) classifica 165 aziende su 378 come defence tech, ma la classificazione è **provvisoria**: si appoggia in gran parte alle industries Crunchbase, che sono generiche. Alcune aziende chiaramente del settore hanno etichette come "Information Technology" e rientrano solo grazie ai segnali strutturali (di norma la partecipazione a progetti EDF): un'azienda analoga senza fondi europei sfuggirebbe del tutto. Serve una revisione a mano dell'elenco, correggendo i casi singoli con le liste `include` / `exclude` in `data/defence_criteria.json` (`exclude` vince su tutto). Da decidere anche se allargare il perimetro alle etichette scartate di proposito — `Robotics`, `Sensor`, `Autonomous Vehicles`, `Cyber Security` — elencate con le motivazioni nello stesso file. | 🔴 |
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

✅ **Fatto** (2026-08-21). MARLA interroga il database su `https://marlamag.vercel.app/dati/`,
accesso con codice, ad uso interno. Il codice sta nel repo MARLA: strumenti in
`api/fonti/manintheloop.js`, controllo citazioni in `api/lib/citazioni.js`, regole
comuni in `docs/CONTRATTO-FONTI.md`. Qui restano solo le due cose che ci riguardano.

| # | Funzionalità | Note | Priorità |
|---|---|---|---|
| 17 | **DOPO IL MERGE: cambiare `MITL_INDEX_URL`** | Oggi il chatbot legge l'indice dal branch: `https://raw.githubusercontent.com/infonodesETS/manintheloop/eu-funding/data/mitl-index.json`. Appena `eu-funding` è su `main`, la variabile su Vercel (progetto marlamag, Settings → Environment Variables) va cambiata in `https://infonodesets.github.io/manintheloop/data/mitl-index.json`, poi Redeploy. **Se ce ne dimentichiamo il chatbot continua a funzionare leggendo un branch fermo, quindi risponde con dati vecchi senza dare alcun segnale.** | 🔴 |
| 18 | **Rigenerare `data/mitl-index.json` a ogni modifica dei dati** | L'indice del chatbot è generato da `scripts/build_chat_index.py` e va ricostruito e committato ogni volta che cambia `data/database.json`, altrimenti MARLA risponde sul database vecchio. Oggi è manuale. MARLA ha già una GitHub Action che rigenera la sua `kb.json` a ogni push; qui non c'è nessuna Action. Da automatizzare allo stesso modo. | 🟡 |
| 15 | **Estendere MARLA all'archivio** | Il chatbot oggi vede solo Man in the Loop. Il passo successivo è il modulo per l'archivio info.nodes (report, inchieste), così può incrociare le due fonti in una sola risposta. La ricerca dell'archivio è per parole chiave e andrà rifatta su base semantica, altrimenti sarà la metà inaffidabile. | 🟡 |

---

## ✅ Completato

| Funzionalità | Data |
|---|---|
| Merge di `eu-funding` in `main`: la nuova versione EU Funding / Global Investments è ora quella online | 2026-09 |
| Fix etichette Rete illeggibili in tema light (nomi in box neri / nodi rosa bianco-su-bianco) — colori theme-aware da variabili CSS (commit `bd9233b`) | 2026-08-21 |
| Onboarding riscritto per la nuova struttura EU Funding / Global Investments — 4 blocchi, 4 lingue (`onboard.*` in `web/i18n.js`, overlay in `index.html`) | 2026-08-31 |
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
