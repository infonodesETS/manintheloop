# S7 — vocabolario dei ruoli e deduplicazione delle persone (decisione B1)

**Decisione S7 (Nelson, 2026-11-11): ruoli = opzione (c); persone = opzione (b).** Una regola di questo file si cambia solo con una nuova decisione registrata nel log.

## Ruoli (Release 2; la Release 1 usa solo `ownership`)

1. Ogni relazione `role` porta due campi: `role` (vocabolario controllato) e `role_text` (dicitura originale del filing, invariata).
2. Se una stringa contiene più ruoli («President and Chief Executive Officer; Director»), si creano **più relazioni, una per ruolo**, tutte con lo stesso `role_text`.
3. Il vocabolario si definisce con una **tabella di mappatura** (stringa → `role`) versionata nel repo. Ciò che non si riesce a classificare prende `role = other` ed è elencato nel report: **nessuna riga si scarta**.
4. La proposta concreta di vocabolario la prepara l'AI leggendo i dati e la approva Nelson **prima** della Release 2 (nella bozza di Andrea: founder, chair, president, ceo, director, board_member… non definita). Fino ad allora il campo `role` non si importa.
5. Campi data dei ruoli (`current`, `start_date`, `end_date` della bozza di Andrea) da decidere con la Release 2; vale S5 (storia in `history[]`, mai cancellare).

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
