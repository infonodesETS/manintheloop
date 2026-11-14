# Istruzione per l'agente di ricerca: QID rimessi (bozza provvisoria)

> Bozza del 2026-11-14, **non ancora provata con un agente**. Fa parte del metodo provvisorio [`reference/METODO-VERIFICA-WEB.md`](../../reference/METODO-VERIFICA-WEB.md). L'agente **propone**: non scrive nel repo, nel database né nel foglio. L'esito lo decide e lo firma Nelson. Chi lancia l'agente incolla la sezione «Testo da dare all'agente» sostituendo `<ID>` (uno o pochi casi per agente).

## Risultato atteso (come si valuta il lavoro)

Un file JSON per scheda, `work/verifica-qid/risultati/<ID>.json`, nel formato sotto. Il file passa il controllo automatico `python3 -I work/verifica-qid/check_risultato.py work/verifica-qid/risultati/<ID>.json`, che verifica **senza fidarsi dell'agente**: che il QID sia quello della scheda, che l'etichetta Wikidata dichiarata sia quella vera, che ogni frase di prova si trovi davvero nella pagina citata, e che il verdetto sia coerente con le prove. Esiti del controllo: `PASS` (si porta a Nelson in tabella), `NEEDS_HUMAN` (caso non chiaro, lo guarda una persona), `FAIL` (l'agente rifà o il caso si scarta).

## Testo da dare all'agente

Sei un agente di ricerca in **sola lettura** per il database Man in the Loop (cartella di lavoro: la radice del repo). Devi dire, per la scheda `<ID>`, se il suo codice Wikidata (QID) è giusto o è quello di un'altra entità (di solito la casa madre). **Non scrivi nulla** nel repo, nel database, nel foglio di controllo né in altri servizi: l'unico file che crei è `work/verifica-qid/risultati/<ID>.json`. Non fai commit, non lanci script che scrivono, non usi `git` per modificare niente.

**1. Leggi la scheda** (sola lettura, `docs/data/database.json`): nome, tipo, `wikidata_id`, blocchi `sources.edf` (PIC, paese, città, sito), `sources.infonodes`, `sources.crunchbase`, e per intero `history` e `validation`. Cerca le voci su `wikidata_id` (rimosso e rimesso: date e autori). Elenca anche le altre schede con lo stesso QID.

**2. Leggi Wikidata** per il QID: `https://www.wikidata.org/w/api.php?action=wbgetentities&ids=<QID>&props=labels|descriptions|claims|sitelinks&format=json` (con un `User-Agent` descrittivo; **senza** il parametro `languages`, oppure includendo `mul`: certe etichette esistono solo in lingua `mul`, per esempio `Q131887361`, e un filtro `en|nl|it` le farebbe sembrare vuote). Annota l'etichetta inglese (o la prima disponibile, e in che lingua), la descrizione, `instance of` (P31), paese (P17), sede (P159), sito (P856). Se non c'è nessuna etichetta in nessuna lingua, dillo.

**3. Cerca sul web solo con Exa** (regola del progetto), endpoint `/answer`, chiave in `~/.config/infonodes/exa.env` (variabile `EXA_API_KEY`; **non stamparla, non copiarla in nessun file**). Nella query solo dati pubblici (nomi di società, codici). Domande **descrittive e neutre**, mai sì/no e mai con la tua ipotesi dentro. Modello: «What is '<nome>' (<città, paese>)? Describe its legal form, registration details (company number, tax ID, registry) and parent company. Cite at least two independent sources and prefer primary ones (company registry, official website, annual report, regulatory filing). If you find no primary source, say so.» Esempio di chiamata: `work/b3-pilota/pilota_exa.py`.

**4. Riapri le fonti su cui poggia ogni affermazione** (Exa `/contents`, POST a `https://api.exa.ai/contents` con `{"urls": [...], "text": true}`), e copia **alla lettera** la frase che prova l'affermazione. Una fonte non riaperta, o in cui non trovi la frase, **non è una prova**: non metterla in `evidence`. I registri passano spesso da aggregatori (secondari): vanno bene per trovare l'identificativo, e li segni `secondary`. I PDF possono arrivare tronchi: se non trovi la frase, dillo in `notes`.

**5. Scrivi il file** `work/verifica-qid/risultati/<ID>.json` esattamente così (tutti i testi **in inglese**, tranne i nomi propri e le frasi copiate dalle fonti, che restano come sono):

```json
{
  "entity_id": "IN-0000",
  "entity_name": "nome come nella scheda",
  "qid": "Q000000",
  "wikidata_label": "etichetta letta su Wikidata (stringa vuota se non c'è)",
  "wikidata_label_lang": "en",
  "wikidata_description": "descrizione o stringa vuota",
  "verdict": "remove_qid | keep_qid | unclear",
  "verdict_reason": "one or two sentences: what the QID is, what the entity is",
  "entity_is": "what the entity actually is (legal form, parent, place), or empty if not found",
  "identifiers": [
    {"type": "KvK | NIF | SIREN | CIK | LEI | other", "value": "...", "source_url": "..."}
  ],
  "evidence": [
    {"claim": "what this proves", "url": "...", "phrase": "exact phrase copied from the page", "source_kind": "primary | secondary"}
  ],
  "other_entities_with_same_qid": ["IN-0000"],
  "notes": "limits, doubts, sources not reopened, truncated documents, anything odd on the entity (for example a wrong Crunchbase block)"
}
```

**Regole del verdetto.**
- `remove_qid`: il QID è di un'altra entità (etichetta e descrizione Wikidata lo mostrano) **e** hai almeno un identificativo di registro (o una prova di fonte riaperta) che dice cos'è davvero la scheda.
- `keep_qid`: l'etichetta Wikidata è la stessa entità della scheda (anche con nome cambiato: spiegalo) **e** una fonte riaperta lo conferma.
- `unclear`: in tutti gli altri casi. È una risposta valida e preferibile a una congettura. L'assenza di un risultato **non** è prova (per esempio «nessun QID di X trovato»).
- Più schede con lo stesso QID (stesso gruppo, paesi diversi): non decidere per tutte; descrivi la tua scheda e segnala le altre in `other_entities_with_same_qid`.

**6. Non fare altro.** Non proporre patch, non toccare altre schede, non correggere altri campi. Se vedi un problema diverso (profilo Crunchbase del gruppo, sito sbagliato, possibile duplicato), scrivilo solo in `notes`. Se qualcosa non funziona (403, Exa non risponde) dopo 2-3 tentativi, fermati e scrivilo in `notes` con `verdict: unclear`. Alla fine rispondi con una sola riga: il percorso del file e il verdetto.

## Limiti noti

- Exa sbaglia anche con fonti dall'aspetto primario (Alcoa Warrick, Damen Naval): per questo il controllo automatico riapre le fonti e cerca la frase.
- Il controllo verifica che la frase **ci sia nella pagina**, non che **dimostri** l'affermazione: quella lettura la fa una persona sulla tabella del gruppo.
- Il controllo automatico non sostituisce l'ok di Nelson e non scrive nel database.
