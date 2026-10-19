# Test di incrocio dati SEC ↔ DB Man in the Loop

Registro dei passaggi fatti il 2026-10-19 sul branch `v.2026-c`. Il test **non modifica** `data/database.json`: legge il DB e i dati SEC e scrive solo in `tmp/sec-test/`.

## Indice

1. [Punto di partenza](#1-punto-di-partenza)
2. [Quali sono i dati SEC](#2-quali-sono-i-dati-sec)
3. [Idee scartate o corrette](#3-idee-scartate-o-corrette)
4. [Decisioni prese](#4-decisioni-prese)
5. [Passo 1 – join aziende](#5-passo-1--join-aziende)
6. [Passo 2 – file di test](#6-passo-2--file-di-test)
7. [Passo 3 – pagine HTML](#7-passo-3--pagine-html)
8. [Cosa ha mostrato il test](#8-cosa-ha-mostrato-il-test)
9. [Entità duplicate nel DB](#9-entità-duplicate-nel-db)
10. [Come rifare il test](#10-come-rifare-il-test)
11. [Punti aperti](#11-punti-aperti)

## 1. Punto di partenza

- Branch di lavoro: `v.2026-c` (era solo remoto; checkout con tracking di `origin/v.2026-c`, allineato, 0 commit avanti/indietro).
- Rispetto a `main` il branch è divergente: 8 commit suoi, 6 di `main` che non ha. Non è stato fatto nessun merge.
- Il branch contiene l'estrazione SEC: commit `ec9ce08` (DEF 14A per 161 aziende, 2026-10-17) e `57616a0` (link ai CSV e al Google Sheet).
- Non esiste un branch con "sec" nel nome. La cartella `SEC/` citata in `STATUS.md` è un workspace locale ignorato da git.

## 2. Quali sono i dati SEC

Cartella: `rawdata/sec-edgar/2026-10-17/` (README autoconsistente nella stessa cartella).

- Fonte: proxy statement **DEF 14A** depositati su EDGAR; dirigenti dal proxy (79 aziende) o dal 10-K (79), nessun elenco per 3 (CLS, RKLB, SWKS).
- **161 aziende quotate negli USA**, perimetro dato dai quattro ETF iShares già usati dal DB: DFND, IXN, IXP, PICK (515 titoli di partenza: 165 estraibili, 285 non registrate alla SEC, 33 senza DEF 14A, 32 collisioni di ticker).
- Estrazione fatta con Claude Haiku 5.5 su schema fisso 3.0; il README dichiara limiti noti e 2.126 avvertenze (`warnings.csv`).

| Tabella | Righe | Contenuto |
|---|---|---|
| `consiglieri.csv` | 1.601 | CdA: cariche, anno di ingresso, indipendenza |
| `comitati.csv` | 2.371 | membri e presidenti dei comitati |
| `dirigenti.csv` | 994 | dirigenti esecutivi, età, cariche |
| `detentori-oltre-5.csv` | 571 | azionisti oltre il 5% (480 fondi/società, 91 persone) |
| `quote-dirigenti-consiglieri.csv` | 2.314 | azioni di dirigenti e consiglieri |
| `persone.csv`, `persone-ruoli.csv` | 2.298 persone | ID `P0001…` assegnati dal dataset; 121 persone in più di un'azienda |

Gli ID persona `P0001…` valgono **solo dentro quella release**: una nuova estrazione rinumera (README, sezione «Le persone e il loro ID»). Questa è un'informazione del README; la proposta di un `PER-` permanente con `P0001` come riferimento di fonte è una deduzione nostra, non descritta in nessun documento. `docs/SCHEMA.md` e `docs/UPDATE_PROTOCOL.md` non sono stati riletti per questo test.

## 3. Idee scartate o corrette

| Cosa | Esito |
|---|---|
| Incrociare i dati SEC con **EDF** (European Defence Fund) | **Ritirata.** Le aziende SEC sono americane quotate; l'EDF finanzia organizzazioni europee. Verificato sul DB: 0 relazioni `edf_participation` sulle entità americane agganciate. Era un'ipotesi non fondata. |
| «BlackRock non esiste come `IV-` nel DB» | **Sbagliato.** Avevo cercato il nome esatto «BlackRock, Inc.»; nel DB si chiama «BlackRock» (**IV-0077**). Vanguard invece non c'è. |
| «159 aziende su 161 agganciate» | **Sbagliato.** Era un errore di metodo (join per solo ticker). Con ETF + ticker iShares e CIK: 161 su 161. |
| Test sul solo sottoinsieme DFND | Scartato su indicazione di Andrea: il test copre tutte le 161 aziende. |
| Test solo a grafo | Messo in discussione: il grafo regge per persone e aziende, non per gli hub (vedi §8). |

## 4. Decisioni prese

- **Etichetta di fonte `SEC`**, accanto a CB, EDF, iShares, WD, INF. Nel test è un `sources.sec` sulle entità agganciate e un colore dedicato (azzurro). Per il DB vero servirebbero anche una voce in `data/glossary.json` e lo stile in `search.html`.
- **Doppie classi di azioni** (Fox, Alphabet, Heico, News Corp: due `IN-` per azienda): decisione di default, **lo stesso blocco `sources.sec` su entrambe** le entità. Da confermare.
- **Cartella temporanea** `tmp/sec-test/`, nessuna scrittura su `data/database.json`.
- **Tipi di relazione nel test**: `board_membership` (già nello schema), più `executive_officer` e `shareholder_5pct`, che **non esistono** nello schema (che ammette solo `investment`, `board_membership`, `edf_participation`).
- Id provvisori: `PER-T####` (da `P####`) e `IV-T####`.

## 5. Passo 1 – join aziende

Script: `join_aziende.py` → `join_aziende.json` (ticker SEC → lista di `IN-`).

Chiave: coppia **(ETF, ticker iShares)** presa da `perimetro.csv` contro `sources.ishares[].stock_ticker/etf_ticker` del DB; entità ritirate (`entity_retired`) escluse; le doppie classi unite per **CIK**.

Risultato: 165 righe estraibili → 165 agganciate, nessuna ambigua o mancante; **161 aziende SEC su 161** hanno almeno una `IN-`; 4 hanno due `IN-` (Fox IN-0135/0136, Alphabet IN-0017/0018, Heico IN-1372/1378, News Corp IN-0250/0251).

Trappole trovate:
- `AIR` è sia AAR Corp (USA, IN-1388) sia Airbus (Francia, IN-0461) nel DB: si distinguono solo per paese.
- Nel perimetro il paese di DFND è in italiano («Stati Uniti»); servito un dizionario di normalizzazione.
- Ticker SEC e iShares possono differire (`HEI-A`/`HEIA`, `ECHO`/`SATS`): per le doppie classi la chiave è il CIK.

## 6. Passo 2 – file di test

Script: `build_sec_test.py` → `sec-test.json` (≈1,1 MB).

- `sources.sec` su **165 `IN-`**: CIK, ticker, data e URL del proxy, data delle quote.
- **2.298 persone** `PER-T`.
- **3.248 relazioni**: 1.633 `board_membership` (ruoli, anno, indipendenza, comitati), 1.012 `executive_officer`, 603 `shareholder_5pct`.
- **Gestori**: nomi normalizzati (maiuscole, punteggiatura, «The», suffissi Inc/LLC/LP…); 9 agganciati a `IV-` già presenti (fra cui BlackRock = IV-0077, JPMorgan IV-0324, Morgan Stanley IV-0393, Invesco IV-0719), **104 nuovi `IV-T`** (fra cui The Vanguard Group = IV-T0001).
- La normalizzazione unifica le grafie dello stesso gestore («The Vanguard Group, Inc.» ecc.) e tiene separate società diverse con nome simile (Vanguard Portfolio Management, Vanguard Capital Management). **Non unifica** «Entities Affiliated with BlackRock»: resta da decidere se è BlackRock.

## 7. Passo 3 – pagine HTML

`index.html`, un'unica pagina con quattro viste, legge `../../data/database.json` e `sec-test.json` (grafi con `web/cytoscape.min.js`).

| Vista | URL | Contenuto |
|---|---|---|
| Home | `index.html` | persone in più aziende (121), gestori con più partecipazioni, ricerca |
| Azienda | `?view=company&id=IN-0006` | CdA con comitati, dirigenti, azionisti >5%, investitori Crunchbase, grafo a un salto |
| Persona | `?view=person&id=PER-T…` | aziende e ruoli, grafo |
| Gestore | `?view=holder&id=IV-0077` | partecipazioni >5%, grafo |

Per aprirla: `python3 -m http.server 8001` dalla root del repository, poi `http://localhost:8001/tmp/sec-test/`. Verificata con Playwright su home, AMD (IN-0006) e BlackRock (IV-0077); console senza errori JavaScript (solo il favicon mancante). Screenshot in `tmp/playwright/` (non committati).

## 8. Cosa ha mostrato il test

- La label **SEC** si affianca bene alle altre.
- Il **profilo azienda** è la vista più efficace; sul grafo di AMD (19 nodi) le etichette sono leggibili.
- Il **grafo di un gestore non regge**: BlackRock ha 140 aziende, 143 nodi, raggiera con etichette sovrapposte. Per i gestori meglio una tabella o un grafico a barre.
- Colonna «Cariche» del CdA troppo stretta: allargata (`min-width`), **non ricontrollata** a schermo dopo la modifica.
- Le percentuali vuote significano «sotto l'1%» (asterisco nel documento), non zero. Le persone che sono sia consiglieri sia dirigenti (es. Lisa Su) hanno due archi verso la stessa azienda.
- Delle 121 persone «in più aziende» nessuna è stata riverificata a mano.

## 9. Entità duplicate nel DB

Il test mostrava «Investitori Crunchbase: 0» per AMD. Verificato: nel DB AMD esiste **due volte**.

| | IN-0006 «Advanced Micro Devices» | IN-1249 «AMD» |
|---|---|---|
| Origine | import iShares (IXN, ticker AMD, USA) | migrazione dal vecchio DB (2026-03-14) |
| `sources.crunchbase` | `null` | presente (importato 2026-04-24) |
| Investitori Crunchbase | nessuno | 3: OpenAI, KB Securities, Daniel Loeb |
| QID Wikidata | nessuno | Q128896 |

Il join SEC aggancia IN-0006 (giusto, passa dal ticker iShares), mentre le relazioni `investment` stanno su IN-1249. Non è un errore del test. IN-0489 «Amdc» è un'azienda tedesca dell'EDF e non c'entra.

Estensione (ricerca di altre `IN-` con lo stesso QID o dominio web sulle 165 entità SEC): **14 su 165** hanno almeno un'entità gemella. Il numero è un **minimo**, perché non vede i gemelli senza QID né sito.

- **Investitori Crunchbase solo sul gemello (3):** AMD (IN-0006 ↔ IN-1249), MP Materials (IN-0242 ↔ IN-1311), Palantir (IN-0282 ↔ IN-1318).
- **Gemello senza investitori:** Alphabet (IN-0017/0018 ↔ IN-1247), IBM/Business Machines (IN-0062 ↔ IN-1294).
- **Probabilmente filiali, non duplicati:** Alcoa Warrick (IN-1352), HII Mission Technologies (IN-1290).

Nessuna correzione è stata applicata al DB. I casi non sono stati controllati uno per uno a mano.

## 10. Come rifare il test

Dalla root del repository (nessuno script scrive fuori da `tmp/sec-test/`):

```bash
python3 -I tmp/sec-test/join_aziende.py     # join aziende → join_aziende.json
python3 -I tmp/sec-test/build_sec_test.py   # file di test → sec-test.json
python3 -m http.server 8001                  # poi http://localhost:8001/tmp/sec-test/
```

## 11. Punti aperti

1. **Duplicati nel DB** (§9): collegare i gemelli solo nella pagina di test, o pulire il DB a parte prima di importare i dati SEC.
2. **Doppie classi**: confermare «stesso blocco su entrambe le `IN-`».
3. **ID persone**: `PER-` permanenti e riconciliazione con le estrazioni future (gli ID del dataset si rinumerano).
4. **Schema**: `executive_officer` e `shareholder_5pct` non sono nello schema; decidere se aggiungerli o ricondurli a tipi esistenti. Richiede la lettura di `docs/SCHEMA.md` e `docs/UPDATE_PROTOCOL.md`.
5. **Gestori**: nodi normali o aggregati; vista a tabella/barre al posto del grafo; «Entities Affiliated with BlackRock» è BlackRock?
6. **Dove vivono i dati SEC**: nel DB principale o in un file separato.
7. **Verifiche a mano**: persone «in più aziende», duplicati, la colonna «Cariche» dopo la modifica.
8. **`STATUS.md`** non è stato aggiornato in questa sessione.
