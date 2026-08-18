# Man in the Loop — Sintesi della nuova versione (2026)

> Documento per il team. Descrive le **modifiche strutturali** della nuova
> versione della piattaforma (ramo `eu-funding`) rispetto alla versione
> attualmente online (ramo `main`), e — nell'ultimo capitolo — **quali dati
> vanno aggiunti e quali arricchiti**.
>
> Versione: *Prototype v.2026-b*. Stato: pronta per un deploy affiancato,
> senza toccare la piattaforma originale.

---

## In una riga

La piattaforma non è più organizzata **per tipo di grafica** (Mappa, Rete…) ma
**per tema**: due grandi sezioni — **EU Funding** (Finanziamenti EU) e **Global
Investments** (Investimenti globali) — ciascuna esplorabile in tre modi.

---

## 1. La modifica principale: navigazione per tema, non per strumento

| | Versione precedente (online) | Nuova versione |
|---|---|---|
| **Menu principale** | Map · Networks · Search · Publications · About | **EU Funding · Global Investments** · Search · Publications · About |
| **Logica** | l'utente sceglieva *lo strumento* (una mappa o un grafo) | l'utente sceglie *la domanda* (denaro pubblico UE, oppure investimenti globali) |
| **Come si esplora** | mappa e rete erano voci separate | dentro ogni sezione ci sono tre viste: **Mappa · Rete · Numeri chiave** |

Le due sezioni rispondono a due domande diverse:

- **EU Funding** — segue il flusso del **denaro pubblico europeo** nel settore
  della difesa: chi lo riceve, con chi collabora, per quali scopi. Oggi mostra
  lo **European Defence Fund (EDF)**.
- **Global Investments** — mostra gli **investimenti (privati e pubblici)** nelle
  aziende del settore e le collaborazioni tra i soggetti.

---

## 2. Nuova sezione "Numeri chiave" (Key Figures)

È una vista completamente nuova (`key-figures.html`), assente nella versione
precedente. Presenta i **dati aggregati** della sezione — classifiche e cifre
significative — invece della sola visualizzazione geografica o a rete.

Include un **selettore di perimetro** in Global Investments che permette di
passare fra *"solo defence tech"* e *"tutte le entità"* (vedi capitolo dati).

---

## 3. Mappa: nuove modalità di lettura

- **Modalità EDF Funding**: la mappa può mostrare i finanziamenti EDF paese per
  paese (cerchi dimensionati sul finanziamento, zoom sull'Europa).
- **Selettore archi in / out / both** (Global Investments): la vecchia legenda
  a tre colori è diventata un **filtro**. Si sceglie di vedere solo gli
  investimenti in **uscita** (blu), solo quelli in **entrata** (rosso) o
  **entrambi**. Le coppie di Paesi con flussi bidirezionali non sono più un
  singolo arco viola ma **due archi affiancati**, uno blu e uno rosso.
- **Pannello informativo** sui programmi di finanziamento (vedi cap. 6).

---

## 4. Onboarding e restyling

- **Box di benvenuto riscritto** per la nuova struttura: quattro blocchi (le due
  sezioni, i tre modi di leggere i dati, Search/Pubblicazioni, About), in tutte
  e quattro le lingue (IT/EN/FR/ES).
- **Titolo della piattaforma** ora interamente in verde, in font *Archivo*
  (peso 600): più sottile e leggibile.
- **Dimensione di base dei testi** leggermente ridotta, per una lettura più
  pulita e uniforme su tutte le pagine.

---

## 5. Sotto il cofano (per chi mette mano al codice)

- **`web/countries.js`** — normalizzazione centralizzata dei nomi dei Paesi
  (prima la logica era sparsa e generava incoerenze, es. "Czechia" vs "Czech
  Republic").
- **`data/defence_criteria.json`** — file di configurazione, modificabile a
  mano, che definisce quali aziende contano come *defence tech*.
- **Traduzioni** di menu e sotto-menu completate nelle quattro lingue.
- La priorità di risoluzione del Paese ora usa prima il dato EDF e poi Wikidata.

---

## 6. 📊 Dati — cosa aggiungere e cosa arricchire

Questo è il capitolo su cui serve il lavoro del team. La struttura della
piattaforma è pronta ad accogliere molti più dati di quelli oggi caricati.

### 6a. Dati da AGGIUNGERE

**Gli altri programmi di finanziamento.** Oggi in EU Funding è attivo **solo
l'EDF**. Il pannello prevede già altri **sette** programmi, presenti come
selettori ma disattivati ("work in progress"). Vanno raccolti e caricati i dati
(beneficiari e importi) di:

| Programma | Ambito | Stato |
|---|---|---|
| **EDF** — European Defence Fund | UE | ✅ caricato |
| **PESCO** — Permanent Structured Cooperation | UE | ⏳ da aggiungere |
| **HORIZON** — Horizon Europe | UE | ⏳ da aggiungere |
| **EDIP** — European Defence Industry Programme | UE | ⏳ da aggiungere |
| **EUDIS** — EU Defence Innovation Scheme | UE | ⏳ da aggiungere |
| **EIF** — European Investment Fund | UE | ⏳ da aggiungere |
| **DIANA** — Defence Innovation Accelerator | NATO | ⏳ da aggiungere |
| **NIF** — NATO Innovation Fund | NATO | ⏳ da aggiungere |

> Nota: DIANA e NIF sono programmi **NATO**, non UE — nel pannello sono già
> separati da una linea. Da decidere se e come rappresentarli nella sezione
> "EU Funding" o in un contenitore dedicato.

**Refresh generale del database.** Prossimo aggiornamento Crunchbase + nuove
call EDF.

**Aziende mancanti.** Esiste una lista di soggetti "assenti dal database" da
valutare con il Senior Data Expert.

**Dati dalla SEC (portale statunitense).** Due filoni da raccogliere dal portale
della U.S. Securities and Exchange Commission:

- dettagli sui **Fondi e i loro investimenti**;
- dettagli su **Fondi e aziende** relativi alle **persone** che vi detengono
  quote rilevanti o ricoprono posizioni apicali.

### 6b. Dati da ARRICCHIRE

**1. Definizione delle aziende "defence tech".** È la voce più delicata. Oggi la
classificazione è **provvisoria**: circa **165 aziende su 378** sono marcate come
defence tech, ma il criterio si appoggia in gran parte alle *industries* di
Crunchbase, che sono generiche. Conseguenze:

- alcune aziende chiaramente del settore hanno etichette come "Information
  Technology" e rientrano **solo** grazie ai segnali strutturali (di norma la
  partecipazione a un progetto EDF): un'azienda analoga senza fondi europei
  sfuggirebbe del tutto;
- altre potrebbero rientrare a torto.

Serve una **revisione a mano** dell'elenco, correggendo i casi singoli nelle liste
`include` / `exclude` di `data/defence_criteria.json` (dove `exclude` vince su
tutto). Va anche deciso se **allargare il perimetro** ad alcune etichette oggi
escluse di proposito — *Robotics, Sensor, Autonomous Vehicles, Cyber Security* —
scartate perché troppo generiche o dual-use.

**2. Tipologia dei finanziatori.** Oggi i soggetti che investono sono trattati in
modo indistinto. Serve **classificarli**, in particolare distinguere:

- **Fondi di Investimento** (fondi istituzionali, private equity, fondi statali…)
- **Venture Capital**

e, più in generale, separare investitori **privati** da **pubblici** (agenzie
governative, banche di sviluppo, fondi sovrani). Questa distinzione renderebbe
molto più leggibili sia le Reti sia i Numeri chiave.

**3. Natura delle entità — identificare con maggior precisione.** Oltre alla
tipologia dei finanziatori, servono due classificazioni più fini:

- per le **aziende**: distinguere **società quotate** da **start up**;
- per gli **investitori pubblici**: precisare il **tipo di istituzione**
  (ministero, banca centrale, autorità, agenzia, banca di sviluppo…).

**4. Correzioni di qualità.** Casi già individuati, da sistemare:

- **MBDA España** ha il campo *country* (Wikidata) errato (IN-0863);
- **Iveco Defence Vehicles** è duplicata come "Idv Defence Vehicles Italia"
  (IN-1431 / IN-0803, stesso PIC);
- **Telecom Italia** duplicata;
- **Fincantieri** presente sia come azienda sia come investitore.

**5. Incrocio con OpenSanctions** — segnalare se un'entità è sanzionata o "di
interesse". Effort medio, manutenzione periodica leggera.

---

## 7. Stato e prossimi passi

- **`main`** = versione **online** attuale, invariata.
- **`eu-funding`** = **nuova versione**, completa a livello di struttura, non
  ancora pubblicata.
- **Blocco prima del merge finale**: il testo di onboarding è già riscritto; il
  merge su `main` va fatto solo quando la ristrutturazione è considerata stabile
  dal team.
- **Deploy affiancato** (in corso di valutazione): pubblicare la nuova versione
  **accanto** a quella originale, senza sostituirla, per condividerla con il team
  e raccogliere feedback.

*Roadmap operativa completa e sempre aggiornata: vedi `ROADMAP.md` nel repository.*
