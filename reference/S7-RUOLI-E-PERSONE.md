# S7 — vocabolario dei ruoli e deduplicazione delle persone (decisione B1)

**Decisione S7 (Nelson, 2026-11-11): ruoli = opzione (c); persone = opzione (b).** Una regola di questo file si cambia solo con una nuova decisione registrata nel log.

## Ruoli (modello rivisto da Nelson il 2026-11-17; prime 57 persone con la Release 1)

**Revisione del 2026-11-17** (Nelson, nel corso del lavoro di B5): sostituisce le regole 1-2 e 4-5 della decisione dell'11 novembre. Le relazioni `role` entrano **già con la Release 1, per le 57 persone importate** (circa 95 righe di ruolo, 47 coppie persona-scheda); per le altre persone resta la Release 2.

1. **Una sola relazione `role` per (persona, scheda azienda)**: se una persona ha un legame con un'organizzazione, la connessione c'è, e i suoi ruoli stanno dentro, non in relazioni separate. Campi e esempio in `reference/SCHEMA.md` (*Relationships*, `role`).
2. Dentro la relazione, `roles` è un oggetto con **solo i ruoli presenti** (assente = falso; la tabella con vero/falso per ogni codice si produce all'esportazione). Ogni ruolo porta `role_text` (dicitura originale, invariata) e i dettagli estratti: `since_year`/`since_month`, `independent`, `fonte`, `committees`.
3. Una stringa con più ruoli («President and Chief Executive Officer; Director») dà **più chiavi in `roles`**, tutte con lo stesso `role_text`. Nessuna riga si scarta: ciò che non si classifica prende `other` ed è elencato nel report.
4. **Vocabolario provvisorio** (13 codici) ricavato dalle 95 righe, **da approvare da Nelson prima di scrivere il codice di import**: tabella di mappatura `work/b5-release1/proposta-ruoli.csv`. Si rivede con la Release 2 (2.298 persone): un cambio di vocabolario è una rimappatura, perché `role_text` resta.
5. **Doppioni:** lo stesso ruolo in due righe (per esempio CEO in `consiglieri.csv` e in `dirigenti.csv`) è **una** chiave in `roles`; le altre diciture in `role_text_alt` e tutte le righe in `source_ref` (lista).
6. **Su quale scheda:** per le società con più schede di classe (Fox, News Corp) il ruolo va sulla scheda di classe con più quote, e la scelta resta rivedibile da B3.
7. **L'età non si importa** (minimizzazione, come gli indirizzi). `since_year`/`since_month` sono interi: la fonte dà anno o anno-mese, mai il giorno.
8. Campi `current`, `as_of`: come `ownership` (S5), `as_of` = `quote_al` del proxy; storia in `history[]`, mai cancellare.

## Persone

1. `PER-NNNN` corrisponde a un `P####` del registro di Andrea; `sources.sec` conserva il riferimento (S1). Il CIK delle persone non esiste nei proxy e 10-K (solo nei Form 3/4/5, issue #33): non è chiave.
2. Il file delle unioni della release si tratta come dato: se due `P####` risultano la stessa persona, sullo stesso `PER-` restano **entrambi** come riferimenti di fonte (nessun ID perso).
3. **Le persone presenti in un controllo manuale si guardano a mano prima di creare l'ID `PER-`** (un ID permanente sbagliato è difficile da correggere). Le verifiche automatiche di Andrea (Exa) non sono state ricontrollate a mano (README della release).
4. Release 1: 57 persone distinte, di cui 4 in un controllo manuale («persona in più aziende»), da controllare prima dell'import:
- `P0551` Egon P. Durban (controllo `C027`, aziende nel controllo: DELL TKO; nel file detentori: TKO)
- `P1197` Lachlan K. Murdoch (controllo `C057`, aziende nel controllo: FOX NWS; nel file detentori: FOX, NWS)
- `P1464` Michael Blitzer (controllo `C077`, aziende nel controllo: LUNR USAR; nel file detentori: USAR)
- `P1690` Peter J. Gundermann (controllo `C089`, aziende nel controllo: ATRO MOG-A; nel file detentori: ATRO)
5. Release 2: 121 persone in «persona in più aziende» e 13 in «stesso nome, separati come persone diverse» da controllare prima di creare gli ID; da pianificare a parte.
6. Limiti noti da ricordare: omonimi nella stessa azienda restano uniti; diminutivi con un'altra iniziale (Bill/William) o cognomi cambiati restano separati.
7. Valgono le regole di S1, S3, S4, S5, S6.

## Verifiche fatte (2026-11-11, sola lettura)

- `persone-ruoli.csv`: 5.025 righe, 2.298 persone; membro di comitato 1.805, consigliere 1.601, dirigente 994, presidente di comitato 566, detentore oltre il 5% 59. Dettaglio in testo libero: 636 diciture distinte per i dirigenti, 596 per i consiglieri.
- Controlli manuali: 143 (121 «persona in più aziende», 13 persone in «stesso nome, separati come persone diverse»); sulla Release 1 solo 4 persone toccate, nessuna nella seconda categoria.
- Registro di Andrea: ID stabili tra estrazioni, numeri mai riassegnati, unioni registrate in un file.
