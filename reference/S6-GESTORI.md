# S6 — gestori e fondi: nodi o aggregati (decisione B1)

**Decisione S6 (Nelson, 2026-11-11): opzione (c), nodi come nei filing più un legame di gruppo esplicito.** Una regola di questo file si cambia solo con una nuova decisione registrata nel log.

## Regole

1. **Un nodo per ogni soggetto che deposita** (`entita_id` della release SEC, già unificato per grafia da Andrea). Nessuna aggregazione automatica: BlackRock Inc., The Vanguard Group, Vanguard Capital Management e Vanguard Portfolio Management restano quattro nodi, come nei filing.
2. **Legame di gruppo** (`parte_di`, modello fissato il 2026-11-16, vedi sotto e `reference/SCHEMA.md`): si aggiunge solo dopo la verifica di una persona, con fonte primaria riaperta. È un dato in più, non sostituisce niente e si può correggere senza toccare le quote.
3. **Abbinamento ai gestori già nel DB con una tabella scritta e rivista a mano** (entità SEC → ID), mai per nome. Esempio di errore evitato: FMR LLC (Fidelity Investments) **non** è Fidelity International `IV-0214`.
4. **State Street resta `IN-1468`** (tipo `bank`): gli ID sono permanenti e il legame di gruppo non dipende dal prefisso. Gli altri gestori nuovi sono `IV-`.
5. I 9 casi «entità forse dello stesso gruppo» di `controlli-manuali.csv` restano controlli manuali finché una persona non li chiude (BlackRock Advisors LLC, Entities affiliated with Vanguard, Capital International/Capital Research, Citadel, Liberty Broadband/Liberty Live, Yorktown, T. Rowe Price, State Farm, Moog RSP).
6. Quando si somma tra depositanti dello stesso gruppo (es. AIR, GEN, MCHP, NTAP) si dichiara «somma dei depositanti».
7. Valgono le regole di S3, S4 e S5.

## Modello del legame di gruppo (decisione di Nelson, 2026-11-16)

- **Forma:** `parte_di` è una relazione (campi e regole in `reference/SCHEMA.md`). Figlia → **capogruppo legale** come la nomina la fonte primaria, anche se non è la scheda che tiene il QID del gruppo (esempio: `IN-0671` per `IN-0670`).
- **Campi decisi:** `forma` (`controllata`, `divisione`, `non_chiaro`), `current` obbligatorio, `as_of` obbligatorio con `current: true` (data della fonte primaria più recente), `fino_al` solo per legami conclusi, `diretta` (`true`, `false` se in mezzo c'è una società senza scheda, `null` se non accertato), `source_ref` (fonte primaria), `history`.
- **Niente percentuali** (restano in `ownership`), **niente cicli** tra i legami correnti, solo tra schede esistenti e non ritirate, **mai ricavato in automatico** (nemmeno dalle voci `qid_removed`, che non contengono ID di capogruppo).
- **Prova su 6 casi reali (su copie, 2026-11-16):** HII, IDV, Alcoa Warrick (due capogruppo, una conclusa), Nammo Raufoss, Telefonica Moviles España. Hanno mostrato che `GLEIF «direct parent»` non basta per `diretta: true` (IDV: in mezzo c'è IDV Group S.r.l.), che l'Exhibit 21 elenca controllate dirette e indirette, e che `current` senza data della fonte non si può verificare: da qui `diretta` a tre valori e `as_of` obbligatorio.
- **Sito:** finché il front-end non legge `parte_di`, mostra ogni relazione diversa da `edf_participation` come investimento (`REL_MAP` in `app.js`, `index.html`). Decisione di Nelson: l'adattamento del sito si fa per ultimo; i primi dati reali entrano solo dopo che si è deciso come gestire questa visualizzazione. Anche l'indice del chatbot (`build_chat_index.py`) esporta la relazione con `tipo: parte_di`: da rigenerare e da segnalare solo quando ci saranno dati reali.

## Verifiche fatte (2026-11-11, sola lettura)

- 110 entità SEC; concentrazione: BlackRock 143 società su 161, Vanguard Group 92, State Street 39, FMR 24, Vanguard Capital Management 17, Vanguard Portfolio Management 5; 93 entità compaiono in una sola società.
- Vanguard: 110 società con almeno un'entità Vanguard; solo 4 con più di una (AIR, GEN, MCHP, NTAP; es. MCHP 7,48% + 5,98%).
- Omonimi nel DB (per nome normalizzato, 8): BlackRock `IV-0077`, JPMorgan `IV-0324`, Morgan Stanley `IV-0393`, Invesco `IV-0719`, Baillie Gifford `IV-0051`, Durable Capital `IV-0623`, Independent Franchise `IV-0282`, Public Investment Fund `IV-0456`. Vanguard e Dimensional assenti; State Street è `IN-1468`.
- Il sito legge come investimento ogni relazione diversa da `edf_participation` (mappa, `REL_MAP`): BlackRock avrebbe 143 archi; serve l'adattamento del front-end nella stessa PR dei dati (S4).
