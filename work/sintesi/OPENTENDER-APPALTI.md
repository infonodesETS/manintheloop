# Appalti pubblici (Opentender) → Man in the Loop

**Log delle decisioni e del metodo.** Documento di lavoro vivo: va aggiornato a ogni passo.
Obiettivo: integrare in Man in the Loop i dati sugli appalti pubblici europei (e, in prospettiva, statunitensi), per capire se e come le aziende che mappiamo ottengono contratti dalla pubblica amministrazione.

- **Avvio lavoro:** 2026-11-02
- **Stato:** prima estrazione completa 2021-2026 ✓ — 8.437 contratti per 298 aziende MITL (vedi §13)

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

## 12. Mappa CPV → settore

Usiamo i codici CPV (categoria merceologica dell'appalto) per etichettare ogni contratto. Regola applicata:

| Famiglia CPV | Settore assegnato |
|---|---|
| 353xxxxx, 354xxxxx, 355xxxxx, 356xxxxx, 357xxxxx, 358xxxxx | **difesa** (armi, munizioni, mezzi/navi/aerei/missili, sistemi elettronici, equip. militare) |
| 35120/35121/35123/35125, 32323500 | **sorveglianza** (sistemi, telecamere, videosorveglianza, identificazione) |
| 3520xxxx | **ordine pubblico** (equipaggiamento polizia) |
| 35000/35100/3510/3512 | **sicurezza** (generico) |
| 7522xxxx | **difesa (servizi)** |
| 7524xxxx | **ordine pubblico (servizi)** |
| 7971x (79710/79711/79713/79714) | **vigilanza/sicurezza (servizi)** |
| 35110xxx, 7525xxxx | soccorso/antincendio (fuori perimetro) |
| tutto il resto | altro |
| campo vuoto | senza CPV |

---

## 13. Risultati — appalti 2021-2026

Scansione completa dei file 2021-2026 (~180 GB, ~1h). Deduplica per (azienda, gara).

- **8.437 contratti** riconducibili a **298 aziende** di Man in the Loop.
- **540** in settori difesa/sicurezza/sorveglianza/ordine pubblico (dove il CPV lo indica).
- Valore complessivo dichiarato: **~151 miliardi di €**.
- Aziende in cima (contratti di difesa): Rheinmetall, BAE Systems, Indra Sistemas, FN Herstal, KNDS, Elbit Systems, Thales, Diehl Defence, General Dynamics, Airbus Defence & Space, Nammo.
- **Italia: 2.499 contratti** (Leonardo, Iveco Defence, RINA, Thales Italia, Fincantieri NexTech, GEM Elettronica, Axon, e-GEOS…).

**Scoperta importante — la copertura CPV varia molto per paese.** Germania, Austria, Spagna ecc. hanno i CPV, quindi possiamo etichettare il settore. **L'Italia NON ha CPV** nei dati Opentender: tutti i 2.499 contratti italiani risultano "senza CPV". Conseguenza: **per l'Italia la rilevanza difesa/sicurezza non si legge dal CPV**, ma dall'**identità dell'azienda** (già nota in MITL) e dal **titolo** della gara.

**Output prodotti:** `mitl-appalti-per-azienda.csv` (sintesi) e `mitl-appalti-dettaglio.csv` (ogni contratto con settore).

**Da migliorare al prossimo giro:**
- Aggiungere la colonna **titolo/oggetto** della gara (serve per "per quale servizio/prodotto", soprattutto per l'Italia senza CPV) — richiede una nuova scansione.
- Verificare se per l'Italia il CPV è presente in un **altro campo** del dato.
- Ripulire dal set le aziende non pertinenti (IT generica, una farmaceutica).
- Valutare l'estensione a paesi extra-UE e l'integrazione nel grafo MITL.

---

## 14. Fonti USA — ricognizione (estensione extra-UE futura)

Per replicare l'analisi sugli appalti pubblici statunitensi. Ricognizione fatta il 2026-11-02.

**usaspending.gov = l'equivalente di Opentender (contratti federali vinti), ma migliore per il nostro metodo:**
- **API aperta e gratuita** (`api.usaspending.gov`, nessuna chiave/registrazione).
- Si può scaricare **filtrando per azienda** (recipient / codice UEI) → *non serve scaricare tutto*. Flusso: `autocomplete/recipient` → `spending_by_award` → `download/contract` o `bulk_download/awards` (CSV zippato); `download/count` per l'anteprima delle righe.
- Campi: beneficiario + **UEI**, agenzia (es. Dept. of Defense), importo, date, e i codici **PSC + NAICS** = l'equivalente dei CPV (ben coperti).
- Alternativa massiva: *Award Data Archive* (ZIP per anno fiscale/agenzia, dal FY2008, ~830 GB non compressi).
- Caveat: è spesa **federale** (non statale/locale); le aziende UE vincono tramite **controllate USA** (es. BAE Systems Inc., Leonardo DRS) → il match va fatto su nomi/UEI delle filiali.

**sam.gov = complementare, NON è la fonte degli esiti:**
- *Entity Management* (anagrafica, UEI, gerarchie societarie) → utile per l'identità e le controllate USA.
- *Contract Opportunities* (bandi aperti, non esiti) ed *Exclusions* (aziende escluse/sanzionate — interessante).
- API su `open.gsa.gov` (Opportunities richiede una chiave gratuita; limiti di richieste sui piani free).

**Raccomandazione:** per gli USA usare **usaspending via API, guidati dalle aziende**; **sam.gov** come supporto all'identità (UEI, controllate, esclusioni). Prossimo passo: prova dal vivo dell'API su 1-2 aziende (BAE, Leonardo DRS, Rheinmetall).

**Test dal vivo (2026-11-04):**
- L'API `recipient` funziona (BAE: 162 soggetti; Rheinmetall: 28; Leonardo DRS: sotto nomi diversi, es. "DRS Network & Imaging", "DRS Sustainment"). Gli endpoint `search/*` (spending_by_award ecc.) davano 503/timeout quel giorno.
- **Soluzione adottata: Award Data Archive.** ZIP per anno fiscale, ~1,9 GB ciascuno (FY2021-2025), 7 CSV per anno, 297 colonne (include oggetto, agenzia, importo, UEI, **capogruppo**, paese, PSC, NAICS). Letti in streaming con `unzip -p`, senza decomprimere su disco; ~20 minuti per un anno.
- **FY2024 (ott 2023 – set 2024):** 6,7 mln di righe lette → **60.805 contratti distinti, 79 aziende MITL, ~117,5 mld $ obbligati**. Prime: Lockheed Martin 51,3 mld, General Dynamics 18,5, Northrop Grumman 18,4, L3Harris 9,0, BAE Systems 8,6. Aziende non USA tramite controllate: Rolls-Royce 1,0 mld, Elbit (Elbit America) 0,5, Kongsberg 0,2, Saab, Nammo, Airbus Helicopters, Safran, Rafael.
- **Match per nome destinatario o capogruppo.** Buchi noti: **Leonardo DRS = 0** e **American Rheinmetall = 3 righe** (nomi delle controllate senza il nome della capogruppo). Serve un secondo passaggio per UEI / tabella controllate.
- Dati nella cartella locale `usaspending/` (fuori dal repo) (ZIP FY2024 + `us-fy2024-per-azienda.csv`, `us-fy2024-dettaglio.csv`). Restano da fare FY2021-2023, 2025-2026.

Fonti: api.usaspending.gov · usaspending.gov/federal-spending-guide · usaspending.gov/download_center/award_data_archive · sam.gov/contracting · open.gsa.gov/api/opportunities-api · open.gsa.gov/api/entity-api

---

## 15. Portali del Global South e altri paesi — ricognizione e campioni

Origine: foglio condiviso del team (47 portali di America Latina, Asia, Africa, Asia centrale) + paesi aggiunti il 2026-11-04. Verifiche fatte dal vivo il 2026-11-04.

**Canale unico standardizzato: registro OCP** (`data.open-contracting.org`, formato OCDS, scarico JSON/CSV/Excel). 136 pubblicazioni, 70 riguardano paesi del foglio. Un solo parser servirebbe per tutti.

### Campioni misurati

| Paese | Fonte | Campione | Risultato |
|---|---|---|---|
| **Colombia** | SECOP II, API Socrata `datos.gov.co/resource/jbjy-vk9h` | marzo 2024: 74.697 contratti | Segmento sicurezza (UNSPSC 46/92) = 0,5%, quasi tutto vigilanza privata. 3 aziende MITL: Elbit Systems C4I & Cyber (Polizia investigativa), Motorola Solutions (logistica polizia), Dassault. **Utilità: buona** |
| **Cile** | ChileCompra via OCP pubbl. 144 (`2024.jsonl.gz`, 682 MB) | anno 2024: 1.437.333 procedure | 4.949 con UNSPSC 46/92. 506 aggiudicazioni a aziende MITL, ma la maggior parte è rumore (Philips 426, Microsoft 12). Rilevanti: Airbus Helicopters (17, Marina), Rheinmetall Electronics (Marina), Motorola (PDI), Telefónica Ing. de Seguridad (Gendarmeria), Thales (4, aviazione civile). **Utilità: buona** |
| **Brasile** | PNCP API `pncp.gov.br/api/consulta/v1/contratos` | marzo 2024: 62.717 su 65.217 (5 pagine su 131 fallite) | 1,8% da enti difesa/polizia (Esercito 753) ma 76% servizi (viaggi, pulizie). Fornitori quasi tutti brasiliani. 8 "match" tutti falsi (Philips medicale, omonimo "Thales…", Amazon Serviços e Construções, Microsoft). **Utilità: bassa** — gli acquisti militari veri non passano da qui |

**Lezioni dai campioni**
1. Un portale con dati aperti **non garantisce** che contenga acquisti di difesa/sorveglianza: serve sempre un campione prima di scaricare.
2. Il segmento "sicurezza" per codice di categoria è piccolo e dominato dai servizi (guardie). Meglio partire **dalle aziende** (come in Opentender) che dai codici.
3. **Importi con errori enormi** nei dati d'origine (Colombia: un contratto da 6,45×10¹⁵ COP): serve un filtro sugli outlier prima di sommare.
4. Il set aziende va **ripulito** (Philips, Microsoft, Amazon, nomi di persona come "Thales"): è la stessa pulizia già in lista per l'Europa.

### Tabella portali (priorità)

| Priorità | Paese | Fonte / come scaricare | Periodo | Note |
|---|---|---|---|---|
| **Alta** | Colombia | API Socrata SECOP II | viva | Campione OK |
| **Alta** | Cile | OCP #144, un file per anno | 2018 → mag 2026 | Campione OK |
| **Alta (da campionare)** | Ucraina | Prozorro, API aperta `public.api.openprocurement.org` | 2015 → 2026 | Verificata viva; la più interessante per la difesa |
| **Alta (da campionare)** | Moldova | MTender API OCDS + OCP #34 | 2018 → ott 2026 | Verificata viva |
| **Media (da campionare)** | Perù (OCP #135, 2003 → ott 2026), Paraguay (#63, → ago 2026), Uruguay (#43 API), Ecuador (#110), Rep. Dominicana (#22), Guatemala (#142), Honduras (#122, #123) | OCP | fino al 2026 | Siti raggiungibili in modo intermittente |
| **Media** | Sudafrica (#143), Nigeria (#64), Kenya (#147), Uganda (#130), Ghana (#85), Ruanda (#145), Tanzania (#152), Zambia (#3) | OCP | fino al 2026 | Il foglio li dava "Parziale": il registro ha dati scaricabili |
| **Media** | Singapore | data.gov.sg, dataset GeBIZ `d_acde1106003906a75c3fa052592f2fcb` (API aperta) | verificata | |
| **Media** | Corea del Sud | data.go.kr, servizio G2B (chiave gratuita) | — | Serve registrazione |
| **Media** | Georgia (#52), Taiwan (#160, AAC), Kosovo (#115), Liberia (#156), Kirghizistan (#29, fermo 2022) | OCP | vari | Aggiunti al perimetro |
| **Bassa / parziale** | Brasile | PNCP + Compras.gov (OCP #157) | → set 2026 | Campione: solo spesa corrente |
| **Bassa / parziale** | Messico (solo stati/municipi nel registro), Argentina (solo Mendoza), Panamá (OCP fermo apr 2024), Costa Rica (solo Potere Giudiziario) | — | — | Federale da verificare |
| **Da verificare** | Israele (data.gov.il, 2 dataset "tenders"), Turchia (EKAP), Arabia Saudita (Etimad), Filippine, Thailandia, Uzbekistan, El Salvador, Bolivia | — | — | Portali vivi, canale dati da capire |
| **Da riprovare** | Indonesia, Kazakistan (API `ows.goszakup.gov.kz`, forse con token), Nepal, Costa d'Avorio, Marocco, Tunisia, Vietnam, Senegal, Armenia, Mongolia, Azerbaigian | — | — | Timeout, certificati scaduti, 403 oggi |
| **Scartati** | India (GeM, CPPP), Malaysia, Pakistan, Bangladesh, Egitto, Algeria, Camerun, Etiopia, Sri Lanka | — | — | Nessun dato scaricabile (coerente con la colonna "No" del foglio) |

**Avvertenza di perimetro.** Gli acquisti militari sono spesso secretati o gestiti fuori dai portali civili: sui portali nazionali troveremo soprattutto sicurezza, sorveglianza, ordine pubblico, frontiere, e soprattutto le grandi aziende con filiali locali.

Fonti: data.open-contracting.org · datos.gov.co · pncp.gov.br · data.gov.sg · public.api.openprocurement.org

---

## 16. Schema comune dei contratti e collegamento a MARLA

Discusso il 2026-11-04. **Nessuna decisione su infrastruttura** (database, hardware): si decide dopo aver completato l'analisi dei dati disponibili. Qui si fissa solo il formato, che non impegna nulla.

### Perché
Idea: far consultare questi dati a **MARLA** (chatbot, repo `infonodesETS/MARLA`), per domande del tipo *"Palantir ha vinto contratti pubblici in paesi africani? Quando e per quanto?"*, con risposta e link alle fonti.

MARLA è già predisposta (`docs/CONTRATTO-FONTI.md`): ogni fonte è un modulo in `api/fonti/<nome>.js` con i suoi strumenti; gli strumenti restituiscono **record** (id, titolo, url, visibilità, dati), non testo; MARLA può citare **solo** ciò che gli strumenti hanno restituito (controllo vincolante, non solo prompt). Una fonte `pubblico` non può contenere materiale `interno`.

### Schema comune (un record = un contratto, uguale per tutti i portali)
| Campo | Contenuto |
|---|---|
| `company_id`, `company_name` | Azienda MITL a cui è abbinato |
| `supplier_name_raw` | Nome del fornitore come scritto nella fonte |
| `match_type` / `match_confidence` | Esatto, per prefisso, per capogruppo/UEI; livello di affidabilità. **Obbligatorio**: gli abbinamenti sono sul nome e producono falsi positivi |
| `buyer` | Ente committente |
| `country` | Paese del contratto |
| `date` | Data firma o aggiudicazione |
| `amount_original`, `currency`, `amount_normalized` | Importo come nella fonte, valuta e importo convertito |
| `object` | Oggetto / titolo del contratto |
| `sector_code`, `sector_label` | CPV / PSC-NAICS / UNSPSC e settore ricavato |
| `source`, `source_id`, `source_url` | Portale, identificativo nella fonte, **link al contratto originale** |

Link originali già disponibili: USA = pagina su usaspending.gov (dall'id `contract_award_unique_key`); Colombia = campo `urlproceso`; Ucraina = pagina Prozorro; Europa = pagina della gara.

### Condizioni per un uso corretto in MARLA
1. **Strumento "copertura"**: l'elenco di paesi, portali e anni realmente presenti. Se MARLA non trova contratti deve dire *"non risultano nei portali che abbiamo scaricato (…)"*, mai "non ci sono contratti".
2. **Abbinamento da verificare**: la risposta deve dire "risulta un fornitore con lo stesso nome", non "l'azienda ha vinto".
3. **Importi anomali**: filtro obbligatorio sugli outlier prima di qualunque somma.
4. **Dimensioni**: gli strumenti girano in una funzione serverless piccola. Opentender (8.437 righe, ~1,7 MB) ci sta; USA un solo anno (60.805 righe, ~21 MB) no. Fase 1: indice compatto (riassunti per azienda/paese/anno + contratti principali) generato da script, come `mitl-index.json`. Fase 2, se serve il dettaglio: database interrogabile (es. Supabase) — da decidere con i numeri veri.
5. **Spesa**: i limiti di spesa di MARLA sono già un punto aperto nel suo TODO; da misurare prima di allargare l'accesso.
6. **Licenze**: i dati USA sono pubblici; per gli altri portali controllare la licenza di riuso prima di mostrarli.
7. Alternativa leggera: integrare i contratti nel grafo MITL come relazioni aggregate azienda → ente (MARLA legge già MITL), evitando di appesantire `database.json` con il dettaglio.

---

## 10. Cronologia

- **2026-11-02** — Ricognizione del dataset (struttura, formato, dimensioni). Validato il lettore tollerante su file campione. Estratti e normalizzati i nomi delle aziende MITL (1.417). Misurata la velocità (~50 MB/s). Verificato che il meccanismo trova correttamente le aziende come fornitrici. Decise: Opzione A, anni dal 2021. Avviata la prima scansione di prova (2024, tutti i paesi).
- **2026-11-02 (pomeriggio)** — Completata la scansione di validazione del 2024: 2.463 contratti puliti (Italia 769). Individuato e corretto un falso positivo (nomi-sigla troppo corti). Metodo validato; pronti per la scansione 2021-2026.
- **2026-11-02 (sera)** — Completata la scansione 2021-2026: **8.437 contratti per 298 aziende MITL** (~151 mld €). Costruita e applicata la mappa CPV → settore. Scoperto che l'Italia non ha CPV nei dati. Prodotti i due CSV (per-azienda + dettaglio).
- **2026-11-02 (sera)** — Ricognizione fonti USA (§14): usaspending (API aperta, filtro per azienda, PSC/NAICS) + sam.gov (identità/UEI, bandi, esclusioni).
- **2026-11-04** — Test USA concluso su FY2024 via Award Data Archive (§14): 60.805 contratti, 79 aziende MITL, ~117,5 mld $. Identificati i buchi (Leonardo DRS, American Rheinmetall).
- **2026-11-04** — Ricognizione portali Global South e altri paesi (§15). Campioni su Colombia, Cile, Brasile. Decisione: **la scansione europea resta in stand-by**; prima si completa l'analisi dei dati disponibili, poi si discutono architettura e hardware.
- **2026-11-04** — Valutata la fattibilità di collegare i contratti a MARLA (§16): sì, l'architettura delle fonti è già predisposta; definito lo schema comune e le condizioni (copertura, match da verificare, outlier, dimensioni, licenze). Punto 2 (campioni altri paesi) rimandato al 2026-11-05.

---

## Prossima sessione — da dove ripartire

Ordine deciso dal team: **prima completare l'analisi dei dati a disposizione, poi architettura e hardware** (es. database Supabase, disco esterno, piccolo server) — nessuna decisione infrastrutturale prima.

1. **Campioni degli altri paesi promettenti (§15):** Ucraina, Moldova, Perù, Paraguay, Singapore, Corea del Sud; poi i "da verificare" e "da riprovare".
2. **USA:** secondo passaggio per UEI / controllate (Leonardo DRS, American Rheinmetall); estendere agli anni FY2021-2023 e FY2025-2026.
3. **Europa (Opentender) — in stand-by:** rilanciare la scansione aggiungendo il **titolo/oggetto**; verificare il CPV italiano; ripulire il set aziende. File dei soli anni 2021-2026 da conservare; 2001-2020 (~230 GB) cancellabili.
4. **Pulizia del set aziende** (Philips, Microsoft, Amazon, nomi di persona, IT generica, pharma), valida per tutte le fonti.
5. **Filtro sugli importi anomali** prima di qualsiasi somma.
6. **MARLA**: far consultare questi dati al chatbot — condizioni e schema comune in §16. Da fare: far produrre il formato comune a tutte le pipeline.
