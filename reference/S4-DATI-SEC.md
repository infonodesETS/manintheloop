# S4 — dove vivono i dati SEC (decisione B1)

**Decisione S4 (Nelson, 2026-11-11): opzione (c), ibrida.** Nel `docs/data/database.json` entrano le entità e le relazioni del modello, non la copia dei CSV. I dati grezzi restano in `rawdata/sec-edgar/` e non si modificano. Una regola di questo file si cambia solo con una nuova decisione registrata nel log.

## Cosa entra nel DB

- Entità `PER-NNNN` (persone), nuovi gestori `IV-` e società `IN-` mancanti.
- Relazioni `ownership` (S2) con `classe`, `pct`, `pct_voti`, `shares`, `holder_type`, `source_ref`, `filing_date`, `as_of`, più le regole di S3 (`id` proprio, classe nella chiave di unicità).
- Blocco `sources.sec` con solo il riferimento di fonte e i campi pubblici: `P####` (persone), release, file, riga, data del filing.
- Le persone fisiche che passano la soglia (sotto) entrano nel DB (nome, quota, voti, fonte). Decisione di Nelson: sono dati resi pubblici dalla SEC. Nel file ci sono 91 **righe** di tipo persona, che corrispondono a 58 persone distinte (`persona_id`); con la soglia: 83 righe, 57 persone.

## Soglia di importazione (decisa da Nelson, 2026-11-11, opzione b)

Una riga di `detentori-oltre-5.csv` si importa se **`percentuale` ≥ 5 oppure `percentuale_voti` ≥ 5** (5,0 incluso). Il file di Andrea si chiama «oltre il 5%» ma non rispetta quella soglia alla lettera: dentro ci sono anche righe sotto il 5%, che la regola esclude, e righe con capitale vuoto ma voti alti, che la regola include.

Conteggi sulla release 2026-10-17 (571 righe, sola lettura, ricalcolabili):
- **546 righe importate**: 529 per capitale ≥5% (di cui **6 esattamente al 5,0%**: Vanguard in AIR e DCO, Newport Trust in GD, Dimensional in KALU e WS, State Street in MOG-A) e **17 per voti ≥5%** con capitale sotto il 5% o vuoto (tra cui Zuckerberg in Meta 60,8%, Duffield e Bhusri in Workday 69,0%, Foroughi in AppLovin 61,6%, Jeff Green in The Trade Desk 49,7%, Brin in Alphabet 25,3%).
- **25 righe NON importate** (14 con capitale sotto il 5% e voti sotto il 5% o assenti, 11 con capitale vuoto e voti assenti o sotto il 5%): 8 persone e 17 entità. Restano nei `rawdata` e vanno nel report di riconciliazione con motivo «sotto la soglia di S4». Elenco al 2026-11-11: AIR (Dimensional 4,8; EARNEST 4,0), ATRO (Gundermann 2,0; Keane), DDOG (FMR 4,9), DELL (SLD Trust), FOX (LGC Holdco; L. Murdoch 1,3), HEI (Mendelson Reporting 1,16; A. Mendelson), LYV (BlackRock 4,97), METC (Yorktown ×2), MOG-A (Stock Employee 1,5), NWS (LGC Holdco; L. Murdoch), PLTR (S. Cohen, voti 3,0), SMCI (C. Liang), TTWO (JPMorgan 4,98), USAR (Inflection Point; Bowon; Alto Opportunity; Blitzer Trust; M. Blitzer 2,2), WBD (Vanguard 0).
- Percentuale **vuota** = «sotto l'1%» (asterisco nel proxy), non zero (README della release): per questo si guardano i voti.
- 110 entità distinte (`entita_id`) e 57 persone distinte entrano; i 22 casi multi-classe di S3 restano 22.
- **Da controllare a mano:** WBD, Vanguard con percentuale «0» (valore sospetto, forse errore di estrazione); AIR è un caso di collisione di ticker nella release (Airbus negli ETF, AAR Corp alla SEC), quindi le due righe AIR vanno verificate prima di decidere.
- Le persone escluse (es. L. Murdoch, C. Liang) potranno entrare con la Release 2 per il loro ruolo; la soglia riguarda solo le quote.

## Cosa NON entra nel DB (per ora)

- **Gli indirizzi** (colonna `indirizzo` di `detentori-oltre-5.csv`): restano solo nei `rawdata`. Nessuna perdita, perché sono nei CSV immutabili. Decisione di Nelson, rivedibile: se li si vuole nel DB serve una nuova decisione registrata (consigliato sentire Andrea e Davide; i dati sono già pubblici nel repo, branch `v.2026-c`, ma il DB è servito dal sito e resta nella storia git).
- Nota per chi ripubblica: la pubblicità del dato per obbligo SEC non esclude il GDPR; nome e quota hanno una finalità chiara, l'indirizzo no (minimizzazione). Non è un parere legale.

## Regole per non perdere dati

1. Ogni record del DB che viene da SEC porta il riferimento alla riga di origine (release, file, riga, `P####`): dal DB si risale sempre al CSV.
2. Lo script di import (B5) fa una **riconciliazione**: ogni riga dei CSV è importata oppure elencata in un report con il motivo dello scarto. Le righe devono tornare a zero (oggi 571 in ingresso = 546 importate + 25 scartate con motivo).
3. I `rawdata` non si modificano mai. Le correzioni vanno in `history[]` o in `controlli-manuali`.
4. Il front-end (`docs/web/app.js`, `docs/index.html`, `docs/networks.html`, `docs/key-figures.html`) si adatta **nella stessa PR dei dati**: oggi ogni relazione diversa da `edf_participation` è letta come investimento (`REL_MAP`, mappa), quindi `ownership` e `role` falserebbero il sito. Serve anche un badge/etichetta per `person`.
5. Valgono le regole R1-R6 di [`S3-CLASSI-AZIONI.md`](S3-CLASSI-AZIONI.md).

## Verifiche fatte (2026-11-11, sola lettura)

- `database.json` 13,2 MB; stima su record minimi: Release 1 circa +0,5 MB (+4%), Release 1 e 2 circa +2,6 MB (+20%). La stima contava 91 persone e 480 entità come record nuovi; in realtà sono 58 persone e 110 entità distinte, quindi la crescita reale della Release 1 è minore (stima da rifare in B5).
- Indirizzi: 70 persone su 91 ne hanno uno; 49 «c/o azienda», 21 non «c/o» (non so se siano abitazioni). 476 su 480 tra gestori e società.
- Non verificato: se il registro di `app.js` esclude le entità `PER-` (visto solo il ciclo sui `IV-`); come mappa e reti trattano entità `person` senza paese.
