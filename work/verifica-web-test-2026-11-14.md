# Verifica web: risultati dei test e valutazione dei 41 QID rimessi (2026-11-14)

> Materiale di lavoro (non pubblicato) a supporto della **bozza provvisoria** [`reference/METODO-VERIFICA-WEB.md`](../reference/METODO-VERIFICA-WEB.md). Tutto in sola lettura: nessun dato del DB è stato modificato. Le risposte complete di Exa del primo test sono in `work/verifica-web-test-2026-11-14-risposte.csv`. **Le risposte di Exa e la valutazione dei gruppi sono proposte, non esiti**; l'esito lo decide e lo firma Nelson.

## 1. Primo test: 6 domande sì/no (con l'ipotesi dell'AI nella domanda)

| Caso | Atteso | Exa | Note |
|---|---|---|---|
| `IN-0863` MBDA España | NO | NO, NIF B86093689 | BOE riaperto: conferma «MBDA ESPAÑA, SL» e il NIF; **non** dice nulla su MBDA Italia né su Wikidata. «Nessun QID trovato» = assenza di prova, non prova di assenza |
| `IN-0599` Damen Naval | NO | NO, «divisione, non entità separata» | **Motivazione falsa**: la pagina Damen citata non contiene «division» né la forma giuridica (riaperta); il secondo test mostra una B.V. a sé |
| `IN-0824` KNDS France Robotics | NO | NO, SAS (RCS Versailles 538 115 684), controllata di KNDS France | fonti knds.com e bilancio 2025 del gruppo, non riaperte |
| `IN-1019` Safran AI | NO | NO, ex Preligens, controllata di Safran Electronics & Defense | fonti safran-group.com, non riaperte |
| `IN-1352` Alcoa Warrick | NO | NO: Alcoa Warrick LLC ceduta a Kaiser Aluminum il 2021-03-31 | 8-K di Alcoa riaperto: conferma la cessione di Alcoa Warrick LLC e del laminatoio al 2021-03-31; «Kaiser titolare **oggi**» è dedotto, non nel testo. Nel pilota B3 Exa aveva sbagliato questo stesso caso |
| `IN-1014` Saab | SÌ | SÌ, org. nr 556036-0793 | certificato di registrazione riaperto: «SAAB Aktiebolag», società per azioni pubblica; «Saab AB» e «Saab Group» non compaiono nel documento |

Esito: 6 su 6 verdetti come atteso, **ma** 1 motivazione falsa (Damen). Domande suggestive: possibile effetto sulla risposta.

## 2. Secondo test: 3 domande descrittive e neutre

- **MBDA España S.L.:** coerente. SL del 2010, NIF B86093689, Registro Mercantile di Madrid (fonte: aggregatore `filings.es`), controllata del gruppo MBDA.
- **Safran.AI:** coerente. SASU francese, SIREN 818 503 146 (aggregatori `pappers.fr`, `verif.com`), ex Preligens, controllata di Safran Electronics & Defense.
- **Damen Naval:** **la risposta cambia.** «Damen Naval B.V.», B.V. olandese, numero di stabilimento 000054916437, Vlissingen, controllata da «Damen Naval Schelde Holding B.V.» (aggregatore `companyinfo.nl`). Il QID del gruppo (`Q950580`) su `IN-0599` somiglia al caso HII; **ipotesi da verificare**.

Lezioni (riportate nella bozza del metodo): domande descrittive meglio di sì/no; una citazione non garantisce la frase; i registri passano da aggregatori (secondari); riaprire le fonti su cui si agisce.

## 3. Valutazione dei 41 QID rimessi (sola lettura, API di Wikidata)

Per ogni coppia della baseline `work/qid-rimessi-noti.json` ho confrontato l'etichetta inglese del QID con il nome della scheda. Il confronto automatico dei nomi è grossolano: i gruppi sotto sono una mia classificazione a mano, **non verificata** (non ho aperto le schede né controllato paese e sito, né se su Wikidata il QID sia della società o del gruppo).

- **A (20): sospetto forte,** controllata o scheda con il QID della casa madre (come HII): Damen (`IN-0599`, `IN-0600`), KNDS (`IN-0824`, `IN-0820`), Safran (`IN-1019`, `IN-1021`), Ericsson Magyarország `IN-0657`, `IN-0752`, `IN-0897`, `IN-0980`, `IN-1122`, `IN-1194`, Beyond Gravity (`IN-0527`, `IN-0528`), Bittium (`IN-0532`, `IN-0533`), `IN-1126`, `IN-0670`, `IN-0952`, `IN-1118`.
- **B (1): errore chiaro:** `IN-0863` MBDA España ha `Q131887361`, che su Wikidata è «MBDA Italia SpA» (senza descrizione né pagina Wikipedia); lo stesso QID è su `IN-0865` MBDA Italia (scheda giusta).
- **C (6): probabilmente a posto** (nome cambiato o uguale): `IN-0287` PLS = Pilbara Minerals, `IN-0401` Vale do Rio Doce = Vale, `IN-1014` Saab Aktiebolag = Saab Group, `IN-1253` Arafura Resources = Arafura Rare Earths, `IN-0831` L M Ericsson = Ericsson, `IN-1150` Tkms = TKMS.
- **D (14): più schede con lo stesso QID,** probabilmente partecipanti EDF dello stesso gruppo con paesi diversi (non verificato): Airbus Defence And Space ×4 (`IN-0464`-`IN-0467`), Airbus Operations ×2 (`IN-0472`, `IN-0473`, QID di Airbus Operations Limited UK), ArianeGroup ×2 (`IN-0501`, `IN-0502`), Integrasys ×2 (`IN-0783`, `IN-0784`), United Monolithic Semiconductors ×2 (`IN-1167`, `IN-1168`, QID della sede tedesca), `IN-0818` Knds Ammo France, `IN-0865` MBDA Italia.

### Tabella completa (gruppo | scheda | nome | QID | etichetta Wikidata | descrizione | pagina en.wikipedia)

| Gr. | Scheda | Nome | QID | Etichetta | Descrizione | enwiki |
|---|---|---|---|---|---|---|
| A | `IN-0527` | Beyond Gravity Austria | `Q663885` | Beyond Gravity | Swiss aerospace business | sì |
| A | `IN-0528` | Beyond Gravity Sweden | `Q663885` | Beyond Gravity | Swiss aerospace business | sì |
| A | `IN-0532` | Bittium Safemove | `Q30302789` | Bittium | company | sì |
| A | `IN-0533` | Bittium Wireless | `Q30302789` | Bittium | company | sì |
| A | `IN-0599` | Damen Naval | `Q950580` | Damen Group | shipbuilding company | sì |
| A | `IN-0600` | Damen Research Development Innovation | `Q950580` | Damen Group | shipbuilding company | sì |
| A | `IN-0657` | Ericsson Magyarorszag Kommunikacios Rendszerek Kft | `Q52618` | Ericsson | Swedish provider of communications technology | sì |
| A | `IN-0670` | Eviden Austria | `Q117442701` | Eviden |  | no |
| A | `IN-0752` | Indra Espacio Slu | `Q1661823` | Indra Sistemas | Spanish defense and information tech company | sì |
| A | `IN-0820` | Knds Belgium | `Q19966744` | KNDS | European defence company | sì |
| A | `IN-0824` | Knds France Robotics | `Q19966744` | KNDS | European defence company | sì |
| A | `IN-0897` | Nammo Raufoss As | `Q1964355` | Nammo | Norwegian-Finnish defence company | sì |
| A | `IN-0952` | Patria Aerostructures | `Q613116` | Patria | Finnish defence and aviation company | sì |
| A | `IN-0980` | Renk Magnet Motor | `Q2144015` | Renk | German defence company | sì |
| A | `IN-1019` | Safran Ai | `Q773875` | Safran Aircraft Engines | aircraft and rocket engine manufacturer based | sì |
| A | `IN-1021` | Safran Data Systems | `Q3461386` | Safran Electronics & Defense | company in the Safran Group | sì |
| A | `IN-1118` | Tekever Uas | `Q24293069` | Tekever | communications and defense company based in L | sì |
| A | `IN-1122` | Telefonica Moviles Espana | `Q160229` | Telefónica | telecommunications company based in Madrid, S | sì |
| A | `IN-1126` | Telespazio France | `Q662824` | Telespazio | Italian company | sì |
| A | `IN-1194` | Valneva Austria | `Q20663010` | Valneva SE | French vaccine producer | sì |
| B | `IN-0863` | Mbda Espana Sl | `Q131887361` | MBDA Italia SpA |  | no |
| C | `IN-0287` | PLS | `Q56064089` | Pilbara Minerals | Australian lithium mining company | sì |
| C | `IN-0401` | VALE DO RIO DOCE | `Q583268` | Vale | multinational diversified metals and mining c | sì |
| C | `IN-0831` | L M Ericsson | `Q52618` | Ericsson | Swedish provider of communications technology | sì |
| C | `IN-1014` | Saab Aktiebolag | `Q219501` | Saab Group | Swedish aerospace and defense company | sì |
| C | `IN-1150` | Tkms | `Q551068` | TKMS | German naval vessel company | sì |
| C | `IN-1253` | Arafura Resources | `Q16829889` | Arafura Rare Earths | Australian mining company | sì |
| D | `IN-0464` | Airbus Defence And Space | `Q15529123` | Airbus Defence and Space | division of Airbus Group (SE) specialised in  | sì |
| D | `IN-0465` | Airbus Defence And Space | `Q15529123` | Airbus Defence and Space | division of Airbus Group (SE) specialised in  | sì |
| D | `IN-0466` | Airbus Defence And Space | `Q15529123` | Airbus Defence and Space | division of Airbus Group (SE) specialised in  | sì |
| D | `IN-0467` | Airbus Defence And Space | `Q15529123` | Airbus Defence and Space | division of Airbus Group (SE) specialised in  | sì |
| D | `IN-0472` | Airbus Operations | `Q4698478` | Airbus Operations Limited | subsidiary of Airbus in United Kingdom | sì |
| D | `IN-0473` | Airbus Operations | `Q4698478` | Airbus Operations Limited | subsidiary of Airbus in United Kingdom | sì |
| D | `IN-0501` | Arianegroup | `Q19951610` | ArianeGroup | European space company | sì |
| D | `IN-0502` | Arianegroup | `Q19951610` | ArianeGroup | European space company | sì |
| D | `IN-0783` | Integrasys | `Q30254805` | Integrasys | company in Madrid, Spain | no |
| D | `IN-0784` | Integrasys | `Q30254805` | Integrasys | company in Madrid, Spain | no |
| D | `IN-0818` | Knds Ammo France | `Q571665` | KNDS France | French weapons manufacturer | sì |
| D | `IN-0865` | Mbda Italia | `Q131887361` | MBDA Italia SpA |  | no |
| D | `IN-1167` | United Monolithic Semiconductors | `Q30285570` | United Monolithic Semiconductors (Germany) | company in Ulm, Germany | no |
| D | `IN-1168` | United Monolithic Semiconductors | `Q30285570` | United Monolithic Semiconductors (Germany) | company in Ulm, Germany | no |
