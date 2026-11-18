# Domanda ad Andrea: valori NULL in `detentori-oltre-5.csv` e righe sotto soglia (B5, Release 1)

> Documento di dettaglio della issue omonima. Bozza del 2026-11-18. Nessun indirizzo: solo dati già pubblici in `rawdata/sec-edgar/2026-10-17/` (release `sec-2026-10-17`). I numeri di riga sono i numeri di riga del file CSV (la riga 1 è l'intestazione).

## 1. Cosa chiediamo

**Un controllo dei dati sulla fonte originale (i proxy e i depositi SEC), prima di decidere altro.** Nel file `detentori-oltre-5.csv` ci sono celle vuote (NULL) nelle colonne `percentuale` e `percentuale_voti`, e non sappiamo, riga per riga, se il vuoto voglia dire «sotto l'1%» o «il modello non ha trovato il dato».

Non chiediamo di rifare l'estrazione: chiediamo di guardare le righe elencate sotto nel documento originale e dirci il valore vero (o che il documento non lo riporta).

## 2. Perché il vuoto è un problema per noi

Per l'import della Release 1 (B5) la soglia deciderebbe così (regola S4, `reference/S4-DATI-SEC.md`): una riga entra se `percentuale` ≥ 5 **oppure** `percentuale_voti` ≥ 5 (5,0 incluso). Su 571 righe: 546 entrano, 25 no.

Il vuoto pesa perché il README della release dice due cose diverse:

- «percentuale vuota con azioni presenti: nel documento c'è l'asterisco, cioè meno dell'1%» (README, sezione sui valori mancanti);
- «`null` o cella vuota: il dato non è nel documento, oppure il modello non l'ha trovato. Non vuol dire zero.»

Con la prima lettura, una percentuale vuota è già sotto soglia e lo scarto è corretto. Con la seconda, è un dato mancante e lo scarto potrebbe far sparire un azionista rilevante. Il file ha 24 righe con `percentuale` vuota; in alcune i numeri non sembrano coerenti con «meno dell'1%» (sezione 3, gruppo B).

## 3. Le righe da controllare

### Gruppo A: scartate, `percentuale` vuota, azioni molte (il sospetto più forte)

| Riga | Società | Titolare | Classe | Azioni | Voti % |
|---|---|---|---|---|---|
| 446 | SMCI | Charles Liang (persona) | Common Stock | 81.398.640 | vuoto |
| 147 | DELL | SLD Trust | Class C Common Stock | 1.380.000 | vuoto |
| 529 | USAR | Inflection Point Fund I, LP | Common Stock | 1.229.463 | vuoto |
| 535 | USAR | Michael Blitzer 2012 Revocable Living Trust | Common Stock | 1.646.404 | vuoto |
| 533 | USAR | Alto Opportunity Master Fund, SPC (Segregated Master Portfolio B) | Common Stock | 400.920 | vuoto |

Liang è il caso più netto: 81 milioni di azioni non sembrano compatibili con «meno dell'1%» (non l'abbiamo verificato sulla fonte: è proprio quello che chiediamo). Per gli altri quattro non abbiamo il totale delle azioni in circolazione, quindi non sappiamo se superino il 5%.

### Gruppo B: importate per i voti, ma con `percentuale` vuota e azioni molte

Entrano perché i voti sono ≥5, ma la percentuale di capitale resta NULL nel database. In una società con una sola classe di azioni, voti e capitale coincidono, quindi qui il vuoto non sembra «meno dell'1%».

| Riga | Società | Titolare | Classe | Azioni | Voti % |
|---|---|---|---|---|---|
| 426 | RKLB | Entities Affiliated with Khosla Ventures | Common Stock | 34.888.272 | 6,1 |
| 427 | RKLB | Entities Affiliated with BlackRock, Inc. | Common Stock | 30.222.153 | 5,2 |
| 424 | RKLB | Peter Beck (persona) | Series A Preferred Stock | 45.951.250 | 7,5 |
| 425 | RKLB | Peter Beck (persona) | Common Stock | 491.930 | 7,5 |

(Le altre righe con `percentuale` vuota e voti alti sono società a doppia classe — Meta, Workday, AppLovin, Alphabet, Datadog, Palantir, Intuitive Machines — dove capitale basso e voti alti sono normali; non le mettiamo in dubbio.)

### Gruppo C: scartate, percentuale presente ma vicina alla soglia

| Riga | Società | Titolare | Percentuale | Fonte indicata |
|---|---|---|---|---|
| 139 | DDOG | FMR LLC | 4,9 (voti 2,8) | Schedule 13G/A, 2025-11-05 |
| 303 | LYV | BlackRock, Inc. | 4,97 | Schedule 13G, 2025-07-17 |
| 513 | TTWO | JPMorgan Chase & Co. | 4,98 | Schedule 13G, 2025-07-30 |

Domanda: sono i valori riportati nel documento, o sono arrotondamenti nostri/del modello? Per noi la soglia 5,0 è inclusiva e senza arrotondamenti, ma vogliamo essere sicuri che nel documento non ci sia scritto «5%».

### Gruppo D: scartate, uscita dichiarata o ticker ambiguo

- **Riga 554, WBD, The Vanguard Group:** 0 azioni, 0% (13G/A del 2026-03-27). S4 lo segnalava già come valore sospetto. Domanda: è un'uscita dichiarata (Vanguard è sceso a zero) o un errore di estrazione?
- **Righe 24 e 25, AIR, Dimensional Fund Advisors (4,8) ed EARNEST Partners (4,0):** S4 segnala la collisione di ticker nella release (Airbus negli ETF, AAR Corp alla SEC). Domanda: queste due righe riguardano AAR Corp? Se sì non sono comunque importabili come Airbus; lo chiediamo per chiudere il dubbio.

### Righe scartate senza dubbio (per completezza, nessun controllo richiesto)

Percentuale presente e chiaramente sotto soglia: righe 52 Gundermann 2,0; 179 L. Murdoch 1,3; 215 Mendelson Reporting Group 1,16; 332 Moog Stock Employee Compensation Trust 1,5; 312 Yorktown IX 4,5; 314 Yorktown X 3,6; 531 Bowon M&P 1,0; 537 M. Blitzer 2,2. Percentuale vuota e azioni poche: righe 54 Keane (13.934); 173 e 387 LGC Holdco (19.000 e 14.250); 217 A. Mendelson (18.380); 390 L. Murdoch (14.364); 409 Cohen (592, voti 3,0).

Totale: gruppi A (5) + C (3) + D (3: 554, 24, 25) + senza dubbio (14) = 25 righe scartate. Il gruppo B (4 righe) non è tra le scartate.

## 4. Che cosa farà la risposta

- Se un valore risulta ≥5%: la riga entra; la nostra regola S4 resta com'è, cambiano solo le righe da importare. Un re-import aggiunge solo righe nuove (S5).
- Se il vuoto è «meno dell'1%» o il dato non esiste nel documento: lo scarto resta; nel gruppo B scriviamo il valore vero di capitale se il documento lo riporta, altrimenti lasciamo NULL con nota.
- Se il vuoto è un errore di estrazione sistematico: ce lo dici e decidiamo se rivedere l'estrazione a monte (`re_documenti_sec`) prima di importare altri dati (Release 2).

## 5. Cosa non dipende dalla risposta

L'import delle 546 righe e la patch del sito non aspettano: le righe in questione sono già escluse (gruppi A, C, D) o importate per i voti (gruppo B). Se arriva una correzione, si aggiunge dopo.

## 6. Riferimenti

- Regola e conteggi: `reference/S4-DATI-SEC.md` (sezione «Soglia di importazione»).
- Valori mancanti: `rawdata/sec-edgar/2026-10-17/README.md` (sezione sui valori `null` e vuoti).
- Elenco completo delle 25 righe con motivo: `riconciliazione.csv` dell'anteprima (`python3 scripts/import_sec_ownership.py --out <cartella>`, colonna `esito = scartata`).
