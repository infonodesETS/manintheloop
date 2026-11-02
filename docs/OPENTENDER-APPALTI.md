# Appalti pubblici (Opentender) → Man in the Loop

**Log delle decisioni e del metodo.** Documento di lavoro vivo: va aggiornato a ogni passo.
Obiettivo: integrare in Man in the Loop i dati sugli appalti pubblici europei, per capire se e come le aziende che mappiamo ottengono contratti dalla pubblica amministrazione.

- **Avvio lavoro:** 2026-11-02
- **Stato:** validazione completata sul 2024 ✓ — pronti per la scansione completa (2021-2026)

---

## 1. La domanda a cui vogliamo rispondere

> Per una azienda presente in Man in the Loop: **ha ottenuto contratti pubblici in Europa? Se sì, da quale istituzione/amministrazione pubblica, per fornire quale servizio o prodotto, per quale importo complessivo, in quale anno?**

---

## 2. Perimetro (decisioni)

| Dimensione | Scelta | Note |
|---|---|---|
| **Settori di interesse** | Difesa, sicurezza, sorveglianza, ordine pubblico, controllo frontiere | Non solo difesa in senso stretto |
| **Paesi** | Tutti (UE); in prospettiva anche extra-UE | Per i primi test si parte comunque da tutti i paesi di un anno |
| **Anni** | **Dal 2021 in poi** | Scartati gli anni precedenti al 2021. File 2027/2028 inclusi (minuscoli); file "year-unavailable" escluso per ora |

---

## 3. La fonte dei dati

- **Origine:** [Opentender](https://opentender.eu/all?lang=en) — download "all", in formato JSON.
- **Dimensione:** ~600 GB, scaricati in locale.
- **Struttura:** 29 file, **uno per anno** (2001→2028 + "year-unavailable"). I file dal 2011 pesano 15–36 GB ciascuno.
- **Formato:** ogni file è **un unico, enorme array JSON su una riga**. Due accortezze tecniche:
  - non è JSON perfettamente standard (contiene elementi "fuori posto"): va letto con un **lettore tollerante in streaming**, non con strumenti normali;
  - la codifica è **latin-1** e gli accenti risultano **già corrotti alla fonte** (compaiono come `�`); per il confronto dei nomi togliamo comunque gli accenti, quindi non è un problema.
- **Cosa contiene un record:** una gara d'appalto, con oggetto, paese, **committente pubblico (buyer)**, **lotti → offerte → aziende (bidders/supplier)**, **importo** (anche in euro), **codici CPV** (categoria merceologica), date, link alle fonti, indicatori di trasparenza.

---

## 4. L'approccio

- **Guidato dalle aziende** (non dai 600 GB): prendiamo i nomi delle aziende di Man in the Loop e cerchiamo dove compaiono come **fornitori** negli appalti. Caricare tutto il dataset sarebbe inutile e ingestibile (sono decine di milioni di gare di ogni settore).
- **Opzione A (scelta):** teniamo la **lista aziende ampia** ed **etichettiamo ogni contratto trovato con il suo settore CPV** (difesa / sicurezza / sorveglianza / ordine pubblico / altro). Così non perdiamo casi di confine e il filtro per rilevanza si fa a valle.
  - *Alternativa scartata (B):* restringere subito ai soli CPV di difesa/sicurezza — più pulito ma rischia di perdere, ad es., una società di sorveglianza che vende "telecamere" con un CPV generico.

---

## 5. Decisioni prese (sintesi)

| # | Decisione | Perché |
|---|---|---|
| 1 | Non integrare i 600 GB grezzi | 99,9% è rumore per noi; ingestibile |
| 2 | Ricerca **guidata dalle aziende MITL** | Risponde direttamente alla domanda |
| 3 | **Opzione A**: lista ampia + etichetta CPV | Non perdere casi di confine |
| 4 | Anni **dal 2021** | Focus sul recente |
| 5 | Validare la qualità su **un anno (2024)** prima della scansione completa | Non sprecare ore di calcolo su un metodo non verificato |
| 6 | Matching **prudente** sui nomi (vedi §6) | Ridurre i falsi positivi |

---

## 6. Come confrontiamo i nomi (regole di matching)

I nomi delle aziende (MITL e fornitori Opentender) vengono **normalizzati**: minuscolo, senza accenti, senza punteggiatura, spazi compattati.

Un fornitore è associato a un'azienda MITL se:
- il nome normalizzato **coincide esattamente**, **oppure**
- il nome MITL (se di **almeno 2 parole**) è il **prefisso** del nome fornitore (es. MITL "Eviden Austria" ⟶ fornitore "Eviden Austria GmbH").
- I nomi di **una sola parola** (es. "apple", "asm") vengono accettati **solo con coincidenza esatta**, per evitare falsi positivi.

> Limite noto: è un confronto per nome, non perfetto. Possiamo perdere varianti (nomi legali diversi) o, raramente, generare falsi positivi. Per i primi test privilegiamo la **precisione** (meglio pochi e giusti).

Insieme di aziende usato: le ~**968** aziende MITL con un segnale di pertinenza (partecipazione a progetti EDF, ETF difesa DFND, settore interno "Defence", o industrie Crunchbase di difesa/sicurezza/sorveglianza). Da rifinire per togliere il rumore tech generico.

---

## 7. Fattibilità (misurata)

- **Velocità di scansione:** ~50 MB/s sul PC in uso.
- **Un file-anno (36 GB):** ~12 minuti.
- **Anni 2021-2026 (~180 GB):** ~1 ora di elaborazione totale.
- *Costo in token del lavoro con l'assistente:* basso — gli script fanno il lavoro pesante e restituiscono solo sintesi/conteggi, non i dati.

---

## 8. Cosa estraiamo per ogni contratto trovato

`azienda MITL` · `fornitore` · `vincitore (sì/no)` · `committente pubblico` · `paese` · `anno` · `tipo (servizi/forniture/lavori)` · `CPV (categoria)` · `importo in €` · `id gara`.

Output finale previsto: **aggregazione per azienda** (elenco committenti, oggetti, importo complessivo, anni) + etichetta settore.

---

## 9. Punti aperti / da rifinire

- Ripulire l'insieme aziende dal **rumore tech generico** (es. Eviden/Atos, Cisco, Intel che vincono gare IT non legate a difesa/sicurezza) — oppure lasciarlo e distinguere solo via CPV.
- Costruire e validare la **mappa CPV → settore** (famiglia CPV 35 = difesa/sicurezza/armi; servizi 75.24 = ordine pubblico; sorveglianza, ecc.).
- Decidere se contare **solo i vincitori** o anche i semplici partecipanti.
- Gestire eventuali **duplicati** (stessa gara presente più volte) e la **conversione valute** (usiamo già l'importo in euro fornito da Opentender).
- Se l'esperimento funziona: **estendere a paesi extra-UE** e valutare come **integrare** i risultati nel grafo MITL (nuova relazione: azienda → ha vinto appalto → committente pubblico).

---

## 11. Prima validazione — anno 2024 (tutti i paesi)

Scansione completa del file 2024 (~34 GB, ~10 minuti, 1,95 milioni di gare esaminate).

- **2.463 contratti** associati ad aziende MITL (dopo correzione dei falsi positivi), di cui **2.301 vinti**, per un valore dichiarato complessivo di **~44,8 miliardi di €**.
- **Italia: 769 contratti.** Tra le aziende trovate: Leonardo, Iveco Defence Vehicles, RINA, Thales Italia, Fincantieri NexTech, Axon Enterprise, e-GEOS, IDS Ingegneria dei Sistemi, GEM Elettronica.
- **Casi difesa "puri"** (CPV famiglia 35 = armi/munizioni/equipaggiamenti): es. Rheinmetall, KNDS, Nammo, con committenti = Ministeri dell'Interno/Difesa.
- **Esito:** risultati coerenti e verificabili → il metodo funziona.

**Falso positivo individuato e corretto:** l'azienda MITL registrata come "A S" (nome-sigla, da EDF) pescava a strascico qualsiasi fornitore che iniziasse per "A.S." (525 match errati, es. "A.S. di Andreatta", "A.S.A. Ortoclinic"). **Correzione applicata:** i nomi troppo corti non fanno più match "per prefisso", solo coincidenza esatta.

**Ancora da rifinire:** sono presenti aziende non legate a difesa/sicurezza (IT generica come Almaviva, Sopra Steria; una farmaceutica). Verranno distinte dall'**etichetta CPV** (Opzione A) e, se serve, rimosse dal set aziende.

---

## 10. Cronologia

- **2026-11-02** — Ricognizione del dataset (struttura, formato, dimensioni). Validato il lettore tollerante su file campione. Estratti e normalizzati i nomi delle aziende MITL (1.417). Misurata la velocità (~50 MB/s). Verificato che il meccanismo trova correttamente le aziende come fornitrici. Decise: Opzione A, anni dal 2021. Avviata la prima scansione di prova (2024, tutti i paesi).
- **2026-11-02 (pomeriggio)** — Completata la scansione di validazione del 2024: 2.463 contratti puliti (Italia 769). Individuato e corretto un falso positivo (nomi-sigla troppo corti). Metodo validato; pronti per la scansione 2021-2026.
