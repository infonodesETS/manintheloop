# Consigli, dirigenti e azionisti delle aziende di Man in the Loop dai documenti SEC

Release del 18 ottobre 2026, estrazione del 17 ottobre 2026. Questo file è autoconsistente: descrive cosa c'è nella cartella, da dove viene, come si legge e cosa non è affidabile.

## Indice

- [Cosa contiene](#cosa-contiene)
- [Da dove vengono i dati](#fonti)
- [Il perimetro: quali aziende](#perimetro)
- [Come sono stati estratti](#estrazione)
- [I file](#file)
- [Le persone e il loro ID](#persone)
- [Fondi e società: le entità](#entita)
- [Controlli manuali](#controlli)
- [Come si legge](#lettura)
- [Limiti noti](#limiti)
- [Costi](#costi)
- [Come si rifà](#rifare)

<a id="cosa-contiene"></a>
## Cosa contiene

Per 161 aziende quotate negli Stati Uniti:

- il consiglio di amministrazione (1.601 consiglieri) e i comitati (2.371 posti di membro);
- i dirigenti esecutivi (994);
- gli azionisti oltre il 5% (571 righe: 480 fondi o società, 91 persone);
- le azioni di dirigenti e consiglieri (2.314 righe) e il totale del gruppo;
- un'anagrafica delle persone con un ID (2.298 persone, 121 in più di un'azienda).

Gli stessi dati stanno in due forme: un JSON per azienda, e tabelle CSV piatte che si aprono in un foglio di calcolo.

<a id="fonti"></a>
## Da dove vengono i dati

La fonte è EDGAR, l'archivio dei depositi della SEC (Securities and Exchange Commission, l'autorità di vigilanza sui mercati statunitense).

- **Consiglio, comitati, azionisti**: dal proxy statement, il modulo DEF 14A che la società manda agli azionisti prima dell'assemblea annuale. Per ogni azienda si prende quello dell'ultima assemblea annuale: depositati fra il 21 ottobre 2025 e il 9 ottobre 2026.
- **Dirigenti**: dal proxy, se li elenca. Altrimenti dal rapporto annuale, il Form 10-K, nella Parte I o nell'Item 10. Dal proxy per 79 aziende, dal 10-K per 79, nessun elenco formale per 3 (CLS, RKLB, SWKS).

Ogni JSON riporta l'indirizzo del documento da cui viene (`filing.source_url`, e `filing.executive_officers_source` per il 10-K).

<a id="perimetro"></a>
## Il perimetro: quali aziende

La lista di partenza sono quattro export di ETF iShares, uno per settore: DFND (aerospazio e difesa), IXN (tecnologia), IXP (servizi di comunicazione), PICK (metalli e mining). Contengono 515 titoli.

| Esito | Titoli | Aziende |
|---|---|---|
| estraibile | 165 | 161 |
| non registrata alla SEC | 285 | - |
| registrata, nessun DEF 14A | 33 | 32 |
| collisione di ticker | 32 | 32 |

I 165 titoli diventano 161 aziende perché quattro sono doppie classi di azioni della stessa società (Fox, News Corp, Heico, Google).

Il criterio è fisso, senza modelli linguistici: un titolo si accoppia a un'azienda registrata alla SEC se il ticker coincide (anche a meno della punteggiatura, `MOGA` e `MOG-A`) o se il nome è molto simile, e solo se il nome conferma l'accoppiamento. «Collisione di ticker» vuol dire che il ticker esiste su EDGAR ma appartiene a un'altra società (`AIR` è Airbus negli ETF e AAR Corp alla SEC). Un'azienda è estraibile se ha depositato almeno un DEF 14A.

Date della fotografia: export iShares al 27 e 30 marzo 2026, indice dei registranti SEC al 5 settembre 2026, ricerca dei proxy al 7 settembre 2026.

Le 32 aziende registrate senza proxy stanno in `senza-proxy.csv` con il rapporto annuale che depositano: 17 il 20-F (estere), 6 il 40-F (canadesi), 2 il 10-K (OpenText e Paramount Skydance), 7 nessun rapporto annuale. Le aziende estere non sono tenute al DEF 14A, e il 20-F ha una struttura diversa: sono fuori da questa release.

<a id="estrazione"></a>
## Come sono stati estratti

Il proxy è un documento legale in prosa, lungo e scritto da ogni azienda a modo suo. L'estrazione:

1. scarica da EDGAR i proxy candidati di ogni azienda e il 10-K precedente; i metadati (CIK, data, numero di deposito, indirizzo) vengono da EDGAR e non passano da un modello;
2. un modello linguistico sceglie il proxy dell'assemblea annuale e, dalla mappa dei titoli del documento, le sezioni che contengono consiglio, comitati, dirigenti e azionisti;
3. il modello legge solo quelle sezioni e restituisce il JSON secondo uno schema fisso (versione 3.0);
4. se il proxy non elenca i dirigenti, lo stesso passaggio si ripete sul 10-K.

Il modello è Claude Haiku 5.5 di Anthropic. I prompt sono fissi e versionati; ogni risultato resta in cache, quindi rifare l'estrazione sugli stessi documenti dà gli stessi file senza costi.

Regole date al modello che contano per la lettura:

- **consiglio attuale**: il consiglio alla data del documento. Chi lascia all'assemblea è ancora consigliere; i candidati nuovi non lo sono ancora;
- **nomi**: grafia normale (non tutto maiuscolo), forma più completa trovata nel documento, senza titoli (Dr., Ph.D.) e senza soprannomi;
- un consigliere che detiene oltre il 5% compare sia fra le azioni dei consiglieri sia fra gli azionisti oltre il 5%;
- un amministratore delegato che siede nel consiglio compare sia fra i consiglieri sia fra i dirigenti.

<a id="file"></a>
## I file

Tutti i CSV sono in UTF-8 con intestazione. Le stesse tabelle sono in un Google Sheet, una scheda per tabella con lo stesso nome del CSV: la colonna «Foglio» apre la scheda. `ticker` collega ogni tabella ad `aziende.csv`, `persona_id` collega le tabelle delle persone a `persone.csv`.

| File | Una riga per | Note | CSV | Foglio |
|---|---|---|---|---|
| `json/<TICKER>.json` | azienda | il dato completo, schema 3.0 | - | - |
| `aziende.json` | - | i 161 JSON in una lista | - | - |
| `aziende.csv` | azienda | documento di origine, data delle quote, conteggi, da dove vengono i dirigenti | [aziende.csv](aziende.csv) | [aziende](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1789286351) |
| `consiglieri.csv` | consigliere | cariche, anno di ingresso, indipendenza | [consiglieri.csv](consiglieri.csv) | [consiglieri](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1214619418) |
| `comitati.csv` | membro di comitato | `presidente` vero per chi lo presiede; riunioni nell'anno | [comitati.csv](comitati.csv) | [comitati](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1352864428) |
| `dirigenti.csv` | dirigente | età, cariche, documento di origine (DEF 14A o 10-K) | [dirigenti.csv](dirigenti.csv) | [dirigenti](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=2136696329) |
| `detentori-oltre-5.csv` | azionista e classe di azioni | `tipo` person o entity, con `persona_id` o `entita_id`; dichiarazione SEC da cui viene la quota | [detentori-oltre-5.csv](detentori-oltre-5.csv) | [detentori-oltre-5](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1158378661) |
| `quote-dirigenti-consiglieri.csv` | persona e classe di azioni | azioni di dirigenti e consiglieri | [quote-dirigenti-consiglieri.csv](quote-dirigenti-consiglieri.csv) | [quote-dirigenti-consiglieri](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1466996604) |
| `totale-di-gruppo.csv` | azienda e classe di azioni | totale di tutti i dirigenti e consiglieri insieme | [totale-di-gruppo.csv](totale-di-gruppo.csv) | [totale-di-gruppo](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=772364741) |
| `warnings.csv` | avvertenza | note del modello sui casi dubbi, vedi sotto | [warnings.csv](warnings.csv) | [warnings](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1635574605) |
| `persone.csv` | persona | ID, nome, altre grafie trovate, aziende | [persone.csv](persone.csv) | [persone](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1328477224) |
| `persone-ruoli.csv` | persona, azienda e ruolo | consigliere, dirigente, detentore oltre il 5%, membro o presidente di comitato | [persone-ruoli.csv](persone-ruoli.csv) | [persone-ruoli](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=817831954) |
| `persone-verifica.csv` | gruppo di nomi | verifica esterna dei collegamenti fra aziende, vedi sotto | [persone-verifica.csv](persone-verifica.csv) | [persone-verifica](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=187609781) |
| `perimetro.csv` | titolo degli ETF | i 515 titoli di partenza con l'esito (`sec_esito`) | [perimetro.csv](perimetro.csv) | [perimetro](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=599937531) |
| `senza-proxy.csv` | azienda | le 32 registrate senza DEF 14A e il rapporto annuale che depositano | [senza-proxy.csv](senza-proxy.csv) | [senza-proxy](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=1413347377) |
| `entita.csv` | fondo, società o trust oltre il 5% | ID, nome, altre grafie, nome normalizzato, aziende | [entita.csv](entita.csv) | [entita](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=717843922) |
| `controlli-manuali.csv` | caso da controllare a mano | cosa controllare, verifica automatica, documenti, colonne vuote per esito e nota | [controlli-manuali.csv](controlli-manuali.csv) | [controlli-manuali](https://docs.google.com/spreadsheets/d/1-T0A9MwACJclPaZwmE-4Stro0HZ7ASarx1raZvPOvRY/edit#gid=575639502) |

Nelle tabelle delle quote un'azienda con più classi di azioni (per esempio Alphabet: A, B, C) ha una riga per classe.

<a id="persone"></a>
## Le persone e il loro ID

Nei documenti SEC una persona non ha un codice come il CIK delle aziende: c'è solo il nome, scritto da ogni azienda a modo suo. L'ID (`P0001`, `P0002`…) è assegnato qui, in quattro passi:

1. **regola sui nomi**: due nomi sono la stessa persona se coincidono primo nome e cognome e le iniziali intermedie non si contraddicono, dopo aver tolto punteggiatura, accenti, titoli e un'iniziale isolata in testa. Trattini e apostrofi uniscono le parti: Russell-Smith è un cognome solo, non Smith. Jr e Sr restano persone diverse;
2. **nomi simili**: le coppie di nomi che la regola non collega ma che potrebbero essere la stessa persona con un diminutivo: stesso cognome, nome diverso con la stessa iniziale, aziende diverse (Brad Smith in NFLX e Bradford L. Smith in MSFT). Sono 66;
3. **verifica esterna**: per ogni gruppo collegato dalla regola (123) e ogni coppia di nomi simili (66) un motore di ricerca, Exa, legge le pagine aziendali e i documenti SEC e dice se si tratta della stessa persona, con motivazione e fonti. Risultato in `persone-verifica.csv`, colonna `regola` per il tipo: 117 gruppi confermati e 6 di persone diverse (fra cui David Carter in KTOS e DCO, Robert Smith in GD e AVAV); 5 coppie simili confermate (Brad Smith, Jon Rambeau, Rob Mionis, Srini Tallapragada, Abhi Talwalkar), 61 di persone diverse;
4. **ID**: uguale per i nomi collegati e per le coppie simili confermate, separato azienda per azienda dove la verifica dice «persone diverse».

Limiti: due omonimi nella stessa azienda, o in aziende che la regola non ha avvicinato, restano sotto lo stesso ID. Due grafie che nemmeno il criterio dei nomi simili avvicina (un diminutivo con un'altra iniziale, come Bill e William, o un cognome cambiato) restano separate. Le verifiche non sono state ricontrollate a mano: i casi da controllare sono nella sezione [Controlli manuali](#controlli).

**L'ID è stabile fra un'estrazione e l'altra.** Un registro ricorda quale ID ha avuto ogni nome normalizzato in ogni azienda: a ogni nuova estrazione una persona già vista riprende il suo ID, una persona nuova prende il primo numero mai usato, e un numero non viene mai riassegnato. Quando due ID si rivelano la stessa persona resta il più basso, e l'altro viene registrato come sostituito, così chi l'ha già usato può riconciliarlo. Si può quindi conservare `persona_id` come riferimento alla fonte.

<a id="entita"></a>
## Fondi e società: le entità

Gli azionisti oltre il 5% che non sono persone (fondi, società, trust) hanno un identificativo `entita_id` (`E0001`, `E0002`…), stabile come quello delle persone. Lo stesso soggetto compare spesso scritto in modi diversi: BlackRock in 8 grafie, The Vanguard Group in 6. Un nome normalizzato li riunisce: via accenti, punteggiatura, testo fra parentesi, «The» in testa, le formule «… affiliated with» in testa e «and affiliates» in coda, le forme giuridiche finali (Inc, LLC, LP, Ltd, Corp, Co, AG, NV, SpA…). Le 129 grafie della release diventano 110 entità, elencate in `entita.csv`.

Società diverse dello stesso gruppo restano entità distinte: BlackRock Advisors LLC non è BlackRock, Inc., Vanguard Capital Management non è The Vanguard Group. Se considerarle un unico detentore è una scelta che va fatta caso per caso, e sono fra i controlli manuali.

<a id="controlli"></a>
## Controlli manuali

`controlli-manuali.csv` elenca i casi in cui le regole automatiche hanno deciso qualcosa che vale la pena guardare a mano. Ogni riga ha un `controllo_id`, il caso, gli identificativi coinvolti, cosa controllare, l'esito della verifica automatica quando c'è, i proxy da cui vengono i dati, e due colonne vuote, `esito` e `nota`, per chi controlla.

| Caso | Quanti | Cosa controllare |
|---|---|---|
| persona in più aziende | 121 | le righe con lo stesso `persona_id` in aziende diverse sono davvero la stessa persona? Se no, quali aziende vanno separate |
| stesso nome, separati come persone diverse | 6 | Exa dice che sono persone diverse: è così? Se no, quali ID vanno uniti |
| entità scritta in modi diversi | 7 | le grafie riunite sotto lo stesso `entita_id` sono tutte lo stesso soggetto? |
| entità forse dello stesso gruppo | 9 | sono società dello stesso gruppo (i Vanguard, BlackRock e BlackRock Advisors, Capital International, World e Research…)? Vanno considerate un unico detentore? |

Per le persone la colonna `verifica_automatica` riporta la risposta di Exa con la motivazione e le fonti: è il punto di partenza, e i proxy in `documenti` servono a confermare carica e azienda. Gli esiti si riportano nella scheda «controlli-manuali» del Google Sheet, che le rigenerazioni del foglio non sovrascrivono. Riportarli nel registro, così che un ID separato o unito a mano resti tale nelle estrazioni seguenti, oggi non è automatico: va fatto prima del giro successivo.

Non sono nei controlli i casi che le regole non possono vedere: due persone omonime nella stessa azienda (avrebbero lo stesso ID) e i diminutivi che cambiano iniziale (Bill e William).

<a id="lettura"></a>
## Come si legge

- **`null` o cella vuota**: il dato non è nel documento, oppure il modello non l'ha trovato. Non vuol dire zero.
- **percentuale vuota con azioni presenti**: nel documento c'è l'asterisco, cioè meno dell'1%.
- **`quote_al`** in `aziende.csv`: la data a cui il proxy riferisce le quote, di solito un paio di mesi prima del deposito.
- **`assemblea`** è vuota per 70 aziende: il modello non ha riportato il nome dell'assemblea, anche se il documento scelto è quello dell'assemblea annuale.
- **`warnings`**: ogni JSON ha una lista di avvertenze, raccolte in `warnings.csv` (2.126). Spiegano le scelte su casi dubbi: consiglieri che lasciano all'assemblea, candidati nuovi esclusi, tabelle con note a piè di pagina, dirigenti presi dal 10-K. Vanno lette prima di trarre conclusioni su una singola azienda.
- **`percentuale_voti`**: per le aziende con classi a voto plurimo, la quota dei voti, diversa dalla quota delle azioni.

<a id="limiti"></a>
## Limiti noti

- **Consiglio, casi di confine**: chi entra o esce vicino alla data del documento può essere incluso o escluso in modo diverso fra due estrazioni. Casi noti: Galovich (AA), Rainey (MSFT), Vestberg (VZ, che resta consigliere ma manca: l'informazione è nella sezione compensi).
- **Depositi congiunti fra gli azionisti oltre il 5%**: il nome di un gruppo che deposita insieme («Tom Gores, Platinum Equity…») può cambiare forma fra un'estrazione e l'altra.
- **Dirigenti**: CLS, RKLB e SWKS non pubblicano un elenco formale né nel proxy né nel 10-K; le persone con compensi dichiarati sono comunque in `quote-dirigenti-consiglieri.csv`.
- **Perimetro**: è una fotografia alle date indicate sopra. Un'azienda che deposita il primo proxy dopo il 7 settembre 2026 (per esempio dopo una fusione) qui non c'è.
- **Persone**: vedi la sezione sull'ID. I nomi sono nella forma trovata nelle sezioni lette: se la forma completa compare solo altrove nel documento, resta quella breve (Brad Smith in NFLX).
- **Azioni frazionarie**: possono essere arrotondate all'unità (STX: 93.356 invece di 93.356,25).
- Su un campione di 20 aziende estratte due volte, 17 hanno dato risultati identici.

<a id="costi"></a>
## Costi

| Passaggio | Costo |
|---|---|
| estrazione delle 161 aziende (Haiku 5.5) | 2,13 $ |
| dirigenti dal 10-K, riestrazione di 82 aziende | 0,29 $ |
| verifica delle persone (Exa, 189 domande) | 2,27 $ |
| **totale** | **4,69 $** |

I documenti EDGAR sono pubblici e gratuiti.

<a id="rifare"></a>
## Come si rifà

Questa cartella è prodotta da script che stanno in un repository di lavoro separato, `re_documenti_sec`, non pubblico, curato da Andrea Borruso: per rifarla o estenderla si passa da lì. Ogni passo è idempotente e tiene in cache documenti e risposte, quindi rilanciarlo senza modifiche non costa nulla. Gli script, nell'ordine:

1. `bin/aziende-lista`: dai 515 titoli alle 161 aziende;
2. `bin/estrai-tutte`: estrazione, un JSON per azienda (opzione `--anno` per un anno passato);
3. `bin/persone-collegate`, `bin/verifica-persone`, `bin/persone`: le persone e il loro ID;
4. `bin/senza-proxy`: le aziende registrate senza proxy;
5. `bin/release`: questa cartella.
