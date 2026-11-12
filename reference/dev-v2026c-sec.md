# v.2026-c — Espansione del database con dati SEC

> **Documento di sviluppo.** Da leggere: Nelson (sviluppo/dati), il resto del team,
> e le sessioni AI che lavoreranno al branch. È la fonte di verità per questa fase.
>
> **Branch:** `v.2026-c` (partito da `main`). Si lavora qui, **non su `main`** (che è
> la versione online stabile). `git fetch && git checkout v.2026-c`.

---

## 1. Obiettivo

Espandere il database di Man in the loop con **nuove fonti** e **nuove tipologie di
dati**, a partire dai documenti del **portale SEC (EDGAR)**. In pratica introduciamo:

- le **quote di partecipazione** (chi possiede pezzi rilevanti delle aziende);
- le **persone** come nuovo tipo di soggetto (azionisti rilevanti e figure apicali).

Il lavoro è diviso in **due release**, con uno spartiacque al **15 novembre 2026**.

---

## 2. Le due release

### 🟢 Release 1 — Quote di partecipazione (entro il 15 novembre 2026)

Aggiungere al DB le **quote detenute da Fondi / Società / Persone** nelle **aziende
quotate già presenti** nel nostro database.

- Soglia: **partecipazioni rilevanti, > 5%**.
- Chi detiene (il "holder"): può essere un **fondo**, una **società** o una **persona**.
- Target: solo le **aziende quotate** che già mappiamo (quelle che depositano presso
  la SEC — tipicamente le quotate USA). Le aziende non quotate / non-USA non hanno
  filing SEC e restano fuori da questo giro.
- Effetto sul modello: nuova **relazione** "detiene quota" (vedi §4) e, per gli
  azionisti individuali, primi record del nuovo tipo entità **persona**.

### 🔵 Release 2 — Persone con ruoli apicali (dal 15 novembre 2026 in poi)

Aggiungere le **persone che ricoprono ruoli apicali** (founder, presidenti,
direttori, amministratori, CEO, membri del board…) nei soggetti mappati:
**aziende, fondi, università e ogni altro soggetto** del DB — partendo dai dati
estratti dai documenti SEC.

- Effetto sul modello: si popola a fondo il tipo entità **persona** e si aggiunge la
  **relazione** "ricopre ruolo presso" (vedi §4).

---

## 3. Fonti SEC (mappa filing → dato)

Da confermare con Nelson (esperto dati); indicazione di massima:

| Dato | Filing SEC tipici |
|---|---|
| Quote > 5% di fondi/istituzionali/persone | **Schedule 13D**, **Schedule 13G** (beneficial ownership > 5%); **Form 13F** (portafogli dei gestori istituzionali) |
| Ruoli apicali + partecipazioni degli insider | **Form 3 / 4 / 5** (Section 16: director, officer, > 10% owner); **DEF 14A** (proxy statement: elenco dirigenti/consiglieri + tabella beneficial ownership) |

---

## 4. Modello dati (bozza — da concordare PRIMA dell'import di massa)

Lo schema attuale ha **entità** (`id`, `type`, `name`, `sources`, …) e **relazioni**
(`source`, `target`, `type`, …). Tipi di entità oggi: `company`, `investor`, `fund`,
`institution`, `government_agency`, `public_fund`, `bank`, `edf_project`. Tipi di
relazione oggi: `investment`, `edf_participation`.

**Novità proposte:**

### Nuovo tipo di entità: `person`
```json
{
  "id": "PE-0001",
  "type": "person",
  "name": "Jane Doe",
  "sources": { "sec": { "cik": "0001234567", "first_seen_filing": "..." } }
}
```
> Da decidere: prefisso id (`PE-####`? le aziende sono `IN-####`, gli investitori
> `IV-####`), e come **deduplicare** la stessa persona tra filing diversi (varianti
> del nome; usare il CIK SEC quando disponibile).

### Nuova relazione (Release 1): `ownership` — detiene una quota
```json
{
  "source": "<id di chi detiene: fondo / società / persona>",
  "target": "<id azienda quotata, IN-xxxx>",
  "type": "ownership",
  "holder_type": "fund | company | person",
  "pct": 7.3,
  "shares": 1234567,
  "source_ref": "sec_sc13g",     // oppure sec_sc13d / sec_13f
  "filing_date": "2026-02-14",
  "as_of": "2025-12-31"
}
```

### Nuova relazione (Release 2): `role` — ricopre un ruolo
```json
{
  "source": "<id persona, PE-xxxx>",
  "target": "<id soggetto: azienda / fondo / università / …>",
  "type": "role",
  "role": "founder | chair | president | ceo | director | board_member | …",
  "source_ref": "sec_form4",     // oppure sec_def14a
  "current": true,
  "start_date": "...",
  "end_date": null
}
```

---

## 5. Prassi operativa (git & dati)

- Lavorare **solo su `v.2026-c`**; commit chiari; **push regolari** per restare
  allineati tra postazioni.
- I **documenti SEC grezzi** restano **fuori dal repo** (in `.gitignore`, come già
  fatto per la cartella SEC). Nel repo va **solo il dato strutturato**.
- Le entità/relazioni nuove confluiscono in `data/database.json` (o in un file di
  staging da concordare) rispettando lo schema di §4.

---

## 6. Domande aperte / decisioni da prendere insieme

1. **Schema persone**: prefisso id, chiave di deduplica (CIK?), campi minimi.
2. **Storicità**: teniamo solo la quota/ruolo *attuale* o anche lo storico (con `as_of`)?
3. **Holder già nel DB**: se un fondo/società che detiene una quota è già presente, si
   riusa il suo `id`; altrimenti si crea? Con quale tipo?
4. **Vocabolario ruoli**: lista controllata dei valori ammessi per `role`.
5. **Collocazione documenti grezzi**: cartella e naming (es. `rawdata/sec/…`).
6. **Come mostrarli in piattaforma**: le quote e le persone vanno poi resi visibili in
   Rete / schede entità — da progettare dopo il caricamento dei dati.

---

*Roadmap generale del progetto: `ROADMAP.md`. Questo file è lo specifico per la fase v.2026-c.*
