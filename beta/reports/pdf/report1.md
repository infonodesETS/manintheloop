# Report 1 — Indicatori statistici: Man in the Loop
> Dati: `data/database.json` — 2.157 entità, 2.647 relazioni  
> Generato: 2026-05-21

---

## Premessa metodologica

I dati integrano tre universi: **iShares ETF** (511 aziende quotate in 4 settori GICS), **EDF** (European Defence Fund, 794 partecipanti a 78 progetti), **Crunchbase + investitori** (667 IV, 990 relazioni di investimento). La sovrapposizione è limitata — solo 6 entità appaiono sia in ETF sia in EDF — il che rende interessante l'analisi delle differenze tra questi mondi.

---

## Angolo 1 — Chi controlla la difesa EU?

### Domande di ricerca
- Quali aziende hanno il maggior potere contrattuale nell'EDF, misurato dal numero di progetti in cui ricoprono il ruolo di coordinatore?
- Esiste una concentrazione geografica nel controllo dei consorzi EDF, o il coordinamento è distribuito tra i paesi membri?
- Le aziende che coordinano più progetti sono le stesse che ricevono più contributi finanziari?

---

### Chi guida i consorzi?

I 78 progetti EDF hanno ciascuno un coordinatore: la responsabilità tecnica e gestionale del consorzio ricade su un'unica azienda. Indra Sistemas e Airbus Defence & Space guidano la classifica con 4 progetti coordinati ciascuna, seguite da Leonardo, Navantia e Thales con 3. La concentrazione è significativa: 9 aziende raccolgono oltre il 40% dei ruoli di coordinamento. Tutte appartengono al nucleo storico dell'industria della difesa europea — nessuna startup o PMI compare tra i top coordinator.

![Top 10 coordinatori EDF](charts/01-top-coordinators.png)

---

### Dove si concentra il potere di coordinamento?

La distribuzione geografica dei ruoli di coordinamento rivela una triade dominante: Spagna, Francia e Italia raccolgono insieme oltre il 60% dei coordinamenti EDF. La Spagna emerge sorprendentemente in testa — trainata da Indra, Navantia e GMV — davanti alla Francia (Thales, Airbus) e all'Italia (Leonardo). La Germania, pur essendo la prima economia EU, risulta sottorappresentata nel controllo dei consorzi rispetto al suo peso economico.

![Distribuzione coordinamenti per paese](charts/02-coordinator-countries.png)

---

## Angolo 2 — Dove va il soldo pubblico?

### Domande di ricerca
- Quali paesi membri ricevono la quota maggiore del contributo europeo attraverso l'EDF, e quanto è squilibrata questa distribuzione?
- Esistono aziende che concentrano una quota sproporzionata del finanziamento totale?
- Quante delle aziende finanziate con denaro pubblico EU sono già quotate in borsa e presenti negli ETF globali?

---

### Il miliardo EU: chi lo prende?

Sui €2,3 miliardi di contributo EU distribuiti attraverso le relazioni di partecipazione EDF nel database, i primi quattro paesi — Francia, Spagna, Italia, Germania — raccolgono il 65% del totale. Francia e Spagna sono praticamente pari (€284M ciascuna), seguite dall'Italia (€243M). Norvegia, Svezia e Belgio completano la top 7. I paesi dell'Est Europa (Estonia, Polonia, Lettonia) partecipano attivamente ma con contributi molto inferiori, sollevando una questione di equità distributiva nel programma.

![Contributo EDF per paese](charts/03-eu-contribution-by-country.png)

---

### Pochi vincitori, molti partecipanti

La distribuzione dei contributi per singola azienda mostra un'alta concentrazione. Leonardo riceve €172M — quasi il doppio del secondo classificato. I top 5 (Leonardo, Bundesministerium der Verteidigung, Indra, Airbus D&S, Saab) raccolgono da soli €570M, circa il 25% del totale. La presenza del Ministero della Difesa tedesco come secondo beneficiario è significativa: l'EDF finanzia direttamente strutture governative, non solo industria privata.

![Top 12 aziende per contributo EU](charts/04-top-companies-eu.png)

---

### I due mondi quasi non si toccano

Solo 6 entità appaiono contemporaneamente negli ETF iShares e tra i partecipanti EDF. La quasi-totale assenza di sovrapposizione rivela che gli ETF globali seguono le grandi cap quotate (Boeing, Lockheed, Rheinmetall, Leonardo come azienda pubblica), mentre l'EDF finanza prevalentemente PMI, istituti di ricerca, e aziende non quotate. Due ecosistemi con logiche di accesso al capitale radicalmente diverse, che raramente si incrociano.

![Sovrapposizione ETF-EDF](charts/05-dual-exposure-etf-edf.png)

---

## Angolo 3 — Chi sono i nuovi player?

### Domande di ricerca
- Le aziende che partecipano all'EDF sono prevalentemente aziende mature o startup in fase early-stage? Il programma raggiunge davvero le PMI innovative?
- Quale quota del finanziamento privato nelle aziende EDF-funded proviene da investitori extra-EU, e da quali paesi?
- Esistono pattern di co-investimento che collegano il capitale privato americano o asiatico all'ecosistema della difesa europea?

---

### L'EDF raggiunge le startup?

Tra le 794 aziende partecipanti all'EDF con dati Crunchbase disponibili, emergono 27 aziende che hanno raggiunto la fase IPO, 37 in M&A, e 18 in fase seed. La maggioranza (circa 80%) non ha dati CB — sono PMI europee, università, enti di ricerca non tracciati da Crunchbase. Tra chi ha dati, il profilo dominante è quello di aziende mature. Le startup in fase early (30 tra seed ed early venture) rappresentano un segnale interessante: l'EDF sta iniziando a raggiungere l'ecosistema innovativo, ma non è ancora il suo terreno principale.

![Fase di finanziamento aziende EDF](charts/06-funding-stages-edf.png)

---

### Il capitale americano nell'industria della difesa EU

Gli USA sono il primo paese di origine degli investitori privati nelle aziende EDF-funded, con 37 relazioni di investimento — più del doppio della Francia (27) e quasi il triplo della Germania (12). Il Belgio, con 28 relazioni, è trainato principalmente dall'EIB e da fondi europei con sede lussemburghese. La penetrazione del capitale americano in aziende che ricevono finanziamento pubblico EU per la difesa è una questione di politica industriale che i dati rendono misurabile.

![Origine investitori per aziende EDF](charts/07-investor-countries-edf.png)

---

### I flussi cross-border: l'asse transatlantico domina

Il flusso di investimento più intenso nel database è USA → Germania (19 relazioni), seguito da flussi Australia → USA e Giappone → USA — questi ultimi legati alle grandi mining companies nel portafoglio degli ETF. I flussi verso l'Europa (USA → UK, USA → France, USA → Canada) mostrano la pervasività del capitale americano. In direzione inversa, solo la Francia mantiene un flusso significativo verso gli USA (6 relazioni), suggerendo che il capitale europeo investe poco fuori dai propri confini.

![Flussi cross-border](charts/08-crossborder-flows.png)

---

## Appendice — Distribuzione ETF per settore

Il portafoglio iShares nel database è dominato dal settore Mining (243 aziende, 48%), seguito da Technology (126), Aerospace & Defence (77) e Comm Services (65). L'inserimento del quarto ETF (GICS 201010, Aerospace & Defence) ha modificato l'equilibrio precedente, avvicinando l'universo ETF all'ecosistema EDF — ma la sovrapposizione rimane marginale perché le aziende quotate nel Defence ETF sono per lo più grandi cap globali (Boeing, Lockheed), non le PMI europee che l'EDF privilegia.

![Distribuzione settori GICS](charts/09-gics-sectors.png)

---

## Appendice — I grandi investitori dell'ecosistema

L'European Investment Bank (21 portfolio companies) è il singolo investitore più attivo nel database, davanti a EISMEA (14) e al Dipartimento dell'Energia USA (12). La presenza dominante di istituzioni pubbliche — EU e USA — tra i top investor riflette la natura del dataset: le aziende della difesa e dell'industria pesante ricevono principalmente capitale istituzionale, non VC. Sequoia Capital è il primo investitore privato puro in classifica (10 aziende), a conferma che i grandi fondi americani hanno già individuato opportunità nel settore.

![Top investitori per portafoglio](charts/10-top-investors-portfolio.png)

---

## Note sui dati

| Limite | Impatto |
|---|---|
| ~80% delle aziende EDF senza dati Crunchbase | Indicatori funding stage sottostimati per il segmento PMI/ricerca |
| 69 relazioni investimento senza paese investitore | Flussi cross-border parziali |
| `eu_contribution` a livello di relazione, non di progetto aggregato | Totali per azienda = somma di tutti i progetti a cui partecipa |
| Solo 4 ETF iShares, nessun ETF europeo | Universo ETF sbilanciato verso mining e tech US |
