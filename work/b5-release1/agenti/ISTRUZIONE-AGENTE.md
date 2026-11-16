# Istruzione per gli agenti di controllo di B5 (bozza provvisoria)

> Bozza del 2026-11-16, **non ancora provata con un agente**. Stesso impianto di `work/verifica-qid/ISTRUZIONE-AGENTE.md`. L'agente **propone**: non scrive nel repo, nel database né nel foglio. L'esito lo decide e lo firma Nelson. Chi lancia l'agente incolla la sezione «Testo da dare all'agente» sostituendo `<LOTTO>` (`A1`…`A4`, `B1`…`B3`).

## A cosa servono

La Release 1 di B5 scrive circa 546 relazioni `ownership`. Ogni relazione dipende da due abbinamenti scritti da me (AI) nelle tabelle di `work/b5-release1/`: azienda SEC → scheda `IN-`, e depositante SEC → scheda `IV-`/`IN-` esistente o nuova. Un abbinamento sbagliato scrive quote sulla scheda sbagliata, senza errori visibili. Gli agenti danno un **secondo parere indipendente** sui casi dove il database non offre un segnale sicuro (ISIN o nome identico).

- **Ruolo A, identità delle aziende, CIECO** (lotti `A1`-`A4`, 39 ticker): per ogni ticker l'agente trova da solo nel database la scheda dello stesso emittente. Non riceve la mia proposta.
- **Ruolo B, depositanti** (lotti `B1`-`B3`, 25 entità SEC): per ogni entità l'agente dice se è lo stesso soggetto giuridico di una scheda candidata o un soggetto diverso.

## Come si valuta il lavoro

Un file JSON per lotto, `work/b5-release1/agenti/risultati/<LOTTO>.json`, che passa `python3 -I work/b5-release1/agenti/check_b5.py work/b5-release1/agenti/risultati/<LOTTO>.json`. Il controllo verifica **senza fidarsi dell'agente**: che ci sia un caso per ogni caso dell'input e nessuno in più, che le schede citate esistano e siano attive con il nome dichiarato, che **ogni frase di prova si trovi davvero nella pagina citata**, e che il verdetto sia coerente con le prove (una prova che nomini l'emittente SEC e una che nomini la scheda). Esiti: `PASS`, `NEEDS_HUMAN`, `FAIL`. Dopo l'agente, io rilancio il controllo e confronto le risposte con le mie tabelle con `confronta.py` (non ancora scritto; i disaccordi vanno a Nelson).

## Testo da dare all'agente

Sei un agente di ricerca in **sola lettura** per il database Man in the Loop (cartella di lavoro: la radice del repo). Il tuo lotto è `<LOTTO>`; l'input è `work/b5-release1/agenti/input/<LOTTO>.json` (campo `role`: `A` o `B`). **Non scrivi nulla** nel repo, nel database, nel foglio né in altri servizi: l'unico file che crei è `work/b5-release1/agenti/risultati/<LOTTO>.json`. Non fai commit e non usi `git` per modificare niente.

**Indipendenza (ruolo A, vincolante; vale anche per il ruolo B tranne l'elenco `candidate_cards`).** Non devi aprire, leggere né cercare nulla in `work/b5-release1/` fuori da `agenti/input/<LOTTO>.json` e da questa istruzione. In particolare **non** i file `proposta-*.csv`, `proponi_*.py`, `verifica_tabelle.py`, i risultati degli altri lotti, né `git log`/`git show` su quella cartella. Quei file contengono le risposte che devi controllare: leggerli annulla il controllo. Se ti accorgi di averne letto uno, scrivilo in `notes` del primo caso.

### Ruolo A: la scheda dello stesso emittente

Per ogni caso (`ticker`, `sec_name`, `cik`, `sec_proxy_url`) devi dire quale scheda `IN-` di `docs/data/database.json` è **lo stesso emittente** del CIK SEC, oppure che non c'è.

1. **Cerca nel database da solo** (sola lettura): per nome normalizzato, per `wikidata_id` e `sources.wikidata` (etichetta, paese, sito), per `sources.infonodes.website`, per `sources.ishares[].stock_ticker`, per i blocchi `edf` e `crunchbase`. Escludi le schede con una voce `history` `action: entity_retired`. Elenca **tutti** i candidati ragionevoli, anche quelli che scarti, con il motivo.
2. **Leggi la fonte SEC dell'emittente** (la `sec_proxy_url` dell'input, la copertina del 10-K, la pagina EDGAR del CIK) e una fonte indipendente dell'emittente (sito societario, relazione annuale). Ti serve una frase che leghi **nome dell'emittente** a **CIK o ticker**, e una che leghi **la scheda** (il suo nome, il suo sito o il suo ISIN) allo stesso emittente.
3. **Attenzione ai falsi amici**: lo stesso ticker o codice può indicare società diverse in fonti diverse, e nomi simili non sono la stessa società. Verifica sempre con CIK, numero di registro o ISIN. Se la scheda è una **controllata o una divisione** dell'emittente e non l'emittente, non è `same_entity`: scrivi `unclear` e spiegalo in `notes`.
4. Se il nome della scheda contiene «Class A» o simili va bene, purché l'emittente sia lo stesso: la classe di azioni non è un criterio.
5. Verdetto per caso: `same_entity` (una scheda, con `db_id` e `db_name` esatti), `no_card` (nessuna scheda del database è l'emittente), `unclear`. `unclear` è valido e **preferibile a una congettura**; l'assenza di un risultato non è una prova.

### Ruolo B: lo stesso soggetto giuridico?

Per ogni caso (`entita_id`, `sec_name`, `other_spellings`, `candidate_cards`) devi dire se il depositante SEC è **lo stesso soggetto giuridico** di una delle schede candidate. Le candidate sono solo un elenco di recupero: non sono un verdetto, e puoi cercare altre schede nel database.

1. Capisci **chi è** il depositante: ragione sociale completa, forma giuridica, paese, ruolo (gestore, famiglia, fondo, società). Fonti: il documento SEC (`sec_name` appare nei Schedule 13G/13D e nei proxy), il registro societario, il sito ufficiale.
2. Capisci **chi è** ciascuna scheda candidata (leggila nel database e fuori).
3. Verdetto: `same_entity` (stesso soggetto giuridico: `db_id` e `db_name` esatti), `different_entity` (soggetti diversi senza legame accertato), `related_group` (soggetti diversi **ma dello stesso gruppo**: per la regola S6 restano nodi separati, tu non proponi nessun legame di gruppo), `unclear`.
4. **Regola di metodo**: marchio o nome uguale non è soggetto giuridico uguale. Serve il numero di registro, l'indirizzo legale, o una frase che dica esplicitamente che sono la stessa società; due società dello stesso gruppo in paesi diversi sono soggetti diversi.
5. `different_entity` e `related_group` richiedono comunque almeno una frase verificata che dica cos'è ciascuno dei due.

### Ricerche e prove (entrambi i ruoli)

- **Cerca sul web solo con Exa**, endpoint `/answer`, chiave in `~/.config/infonodes/exa.env` (variabile `EXA_API_KEY`; **non stamparla, non copiarla in nessun file**). Nella query solo dati pubblici (nomi di società, codici). Domande **descrittive e neutre**, mai sì/no e mai con la tua ipotesi dentro. Modello: «What is '<nome>' (<paese>)? Describe its legal form, registration details (company number, tax ID, CIK, LEI, registry) and parent company. Cite at least two independent sources and prefer primary ones. If you find no primary source, say so.» Esempio di chiamata: `work/b3-pilota/pilota_exa.py`.
- **Riapri le fonti** su cui poggia ogni affermazione (Exa `/contents`, POST a `https://api.exa.ai/contents` con `{"urls": [...], "text": true}`) e copia **alla lettera** la frase che prova l'affermazione. Una fonte non riaperta, o in cui non trovi la frase, **non è una prova**. Aggregatori (einforma, Crunchbase, siti di dati) servono a trovare un identificativo e si segnano `secondary`. I PDF possono arrivare tronchi: se non trovi la frase, dillo in `notes`.
- Frase di almeno 25 caratteri.

### Il file da scrivere

`work/b5-release1/agenti/risultati/<LOTTO>.json`, testi **in inglese** (tranne nomi propri e frasi copiate dalle fonti):

```json
{
  "batch": "A1",
  "cases": [
    {
      "ticker": "XXXX",
      "db_id": "IN-0000",
      "db_name": "name exactly as in the database, or empty if no card",
      "verdict": "same_entity | no_card | unclear",
      "candidates_considered": [{"id": "IN-0000", "name": "…", "outcome": "chosen | rejected", "why": "…"}],
      "identifiers": [{"type": "CIK | LEI | ISIN | registry | website", "value": "…", "source_url": "…"}],
      "evidence": [{"claim": "what this proves", "url": "…", "phrase": "exact phrase copied from the page", "source_kind": "primary | secondary"}],
      "notes": "limits, doubts, sources not reopened, truncated documents, anything odd on the card"
    }
  ]
}
```

Per il ruolo B la chiave del caso è `entita_id` (non `ticker`), il verdetto è `same_entity | different_entity | related_group | unclear`, e `db_id`/`db_name` sono obbligatori solo con `same_entity` (con `different_entity` indica nei `candidates_considered` le schede confrontate). Ogni caso dell'input deve comparire **una volta sola**, anche con `unclear` e `evidence: []`.

### Non fare altro

Non proporre patch, non toccare altre schede, non correggere campi. Se vedi un problema diverso (sito sbagliato, blocco Crunchbase del gruppo, possibile duplicato), scrivilo solo in `notes`. Se qualcosa non funziona (403, Exa non risponde) dopo 2-3 tentativi su un caso, metti `unclear`, scrivilo in `notes` e passa al successivo. Alla fine lancia `python3 -I work/b5-release1/agenti/check_b5.py work/b5-release1/agenti/risultati/<LOTTO>.json` (è in sola lettura) e rispondi con **una riga**: il percorso del file, quanti casi per verdetto e l'esito del controllo.

## Limiti noti

- Gli agenti sono lo stesso modello che ha scritto le tabelle: i punti ciechi sono in parte condivisi. L'indipendenza è dell'**informazione** (il ruolo A non vede la mia proposta), non della testa.
- Il controllo verifica che la frase **ci sia nella pagina**, non che **dimostri** l'affermazione: quella lettura la fa una persona sulla tabella dei disaccordi.
- Exa sbaglia anche con fonti dall'aspetto primario: per questo il controllo riapre le pagine.
- Il ruolo A non copre i 119 abbinamenti con ISIN nel database né le 8 classi di `GOOG`/`PLTR`/`FOX`/`HEI`/`NWS`, già risolte altrove; il controllo sui primi resta un campione manuale.
- Il controllo automatico non sostituisce l'ok di Nelson e non scrive nel database.
