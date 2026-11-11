# S4 — dove vivono i dati SEC (decisione B1)

**Decisione S4 (Nelson, 2026-11-11): opzione (c), ibrida.** Nel `docs/data/database.json` entrano le entità e le relazioni del modello, non la copia dei CSV. I dati grezzi restano in `rawdata/sec-edgar/` e non si modificano. Una regola di questo file si cambia solo con una nuova decisione registrata nel log.

## Cosa entra nel DB

- Entità `PER-NNNN` (persone), nuovi gestori `IV-` e società `IN-` mancanti.
- Relazioni `ownership` (S2) con `classe`, `pct`, `pct_voti`, `shares`, `holder_type`, `source_ref`, `filing_date`, `as_of`, più le regole di S3 (`id` proprio, classe nella chiave di unicità).
- Blocco `sources.sec` con solo il riferimento di fonte e i campi pubblici: `P####` (persone), release, file, riga, data del filing.
- Le 91 persone fisiche tra i detentori >5% entrano nel DB (nome, quota, voti, fonte). Decisione di Nelson: sono dati resi pubblici dalla SEC.

## Cosa NON entra nel DB (per ora)

- **Gli indirizzi** (colonna `indirizzo` di `detentori-oltre-5.csv`): restano solo nei `rawdata`. Nessuna perdita, perché sono nei CSV immutabili. Decisione di Nelson, rivedibile: se li si vuole nel DB serve una nuova decisione registrata (consigliato sentire Andrea e Davide; i dati sono già pubblici nel repo, branch `v.2026-c`, ma il DB è servito dal sito e resta nella storia git).
- Nota per chi ripubblica: la pubblicità del dato per obbligo SEC non esclude il GDPR; nome e quota hanno una finalità chiara, l'indirizzo no (minimizzazione). Non è un parere legale.

## Regole per non perdere dati

1. Ogni record del DB che viene da SEC porta il riferimento alla riga di origine (release, file, riga, `P####`): dal DB si risale sempre al CSV.
2. Lo script di import (B5) fa una **riconciliazione**: ogni riga dei CSV è importata oppure elencata in un report con il motivo dello scarto. Le righe devono tornare a zero (oggi 571 detentori in ingresso: 571 gestiti o motivati).
3. I `rawdata` non si modificano mai. Le correzioni vanno in `history[]` o in `controlli-manuali`.
4. Il front-end (`docs/web/app.js`, `docs/index.html`, `docs/networks.html`, `docs/key-figures.html`) si adatta **nella stessa PR dei dati**: oggi ogni relazione diversa da `edf_participation` è letta come investimento (`REL_MAP`, mappa), quindi `ownership` e `role` falserebbero il sito. Serve anche un badge/etichetta per `person`.
5. Valgono le regole R1-R6 di [`S3-CLASSI-AZIONI.md`](S3-CLASSI-AZIONI.md).

## Verifiche fatte (2026-11-11, sola lettura)

- `database.json` 13,2 MB; stima su record minimi: Release 1 circa +0,5 MB (+4%), Release 1 e 2 circa +2,6 MB (+20%).
- Indirizzi: 70 persone su 91 ne hanno uno; 49 «c/o azienda», 21 non «c/o» (non so se siano abitazioni). 476 su 480 tra gestori e società.
- Non verificato: se il registro di `app.js` esclude le entità `PER-` (visto solo il ciclo sui `IV-`); come mappa e reti trattano entità `person` senza paese.
