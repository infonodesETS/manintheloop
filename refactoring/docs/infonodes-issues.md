# User Test Sessions — infonodes Issues

_Sessions date: 2026-03-27_
_Sources: speech-to-text transcripts, live walkthroughs_
_Users: Davide, Andrea, Laura_
_App state at sessions: full build including Company Search tab_

---

## How to read this file

Each issue is tagged with:
- **Area** — which tab/component is affected
- **Type** — Bug | UX | Content | Feature | Data | Architectural
- **Priority** — High / Medium / Low
- **Cross-ref** — reference to another issue raising the same point

Issues are grouped by user and numbered globally in the order they emerged during each session.

---

## Davide

---

### #01 — Intro page: testi da riscrivere per chiarezza orientativa

**Area:** Intro — `#tab-intro`
**Type:** Content
**Priority:** High

La pagina intro deve comunicare immediatamente: che informazioni ci sono, dove trovarle, come trovarle. I testi attuali sono strutturalmente ok ma non assolvono questa funzione orientativa. Servono testi esplicativi scritti da Davide.

> "la pagina in cui chi arriva deve capire immediatamente che informazioni può trovare, dove può trovarle e come trovarle"

**Proposta:** Testi brevi e direzionali per ciascuna delle 3 aree principali (CTA già presenti). Lavoro editoriale, non tecnico.

---

### #02 — Intro vs. Company Search come landing page default

**Area:** Routing — `js/main.js`, `js/url.js`
**Type:** Feature (da validare)
**Priority:** Low

Davide ha sollevato se abbia più senso far atterrare l'utente direttamente su Company Search ("arrivi e subito fai qualcosa") invece che su una pagina intro. Non è una decisione tecnica ma di design dell'esperienza.

> "la pagina in cui atterri potrebbe essere banalmente un'altra, tipo company search"

**Note:** Segnalata come "possibile feature da validare". Mantenere intro come default per ora; rivalutare dopo test ulteriori.

---

### #03 — Architettura: unificare EDF e Supply Chain in un unico database

**Area:** Architettura dati — `data/database.json`, `data/edf_calls.json`, `js/data.js`, `js/edf-data.js`
**Type:** Architectural
**Priority:** High

EDF non deve essere un gruppo separato nella navigazione: è una fonte di dati, non una categoria concettuale distinta. Il database deve essere unico. Per ogni entità si indica la fonte di provenienza (Crunchbase, EDF, team infonodes), ma l'utente non percepisce la separazione.

> "European Defense Fund per noi è una fonte di dati, non deve essere un gruppo separato [...] ci sarà un unico database che raccoglie tutto"

**Impatto:** Richiede:
- Fusione dei due file JSON in un database unificato con campo `source` per entità
- Riorganizzazione della navigazione (EDF non sarà più un gruppo)
- Refactoring di `js/edf-data.js` e `js/data.js`

**Note:** Questo è il cambiamento macro più impattante. Va pianificato separatamente.

---

### #04 — Rinominare il gruppo "Supply Chain"

**Area:** Nav — `index.html`, `js/main.js`
**Type:** Content / UX
**Priority:** Low

"Supply Chain" come label di gruppo non è sufficientemente esplicita per un nuovo utente. Davide suggerisce un nome più diretto tipo "Explore Supply Chain" o simile.

**Note:** Da decidere insieme al team dopo aver definito la nuova architettura informativa (#03).

---

### #05 — Data: Anduril mostra più di 5 investitori (attesi solo 5 da Crunchbase)

**Area:** Data — `data/database.json`, Company Search, Graph
**Type:** Data
**Priority:** High

Su Company Search, Anduril mostra oltre 10 investitori. L'export da Crunchbase dovrebbe contenerne solo 5. Stessa anomalia osservata su iSci nel Graph (compare BlackRock non atteso).

> "noi dovremmo avere soltanto 5 investitori, su Company Search Anduril invece compaiono oltre 10, bisogna capire da dove arrivano"

**Azione:** Audit di `database.json` per verificare quante relazioni `REL-*` puntano ad Anduril e da dove provengono. Verificare se il problema è nella fase di migrazione da `investments.json` o in un import successivo.

---

### #06 — Data: inconsistenze nei nomi aziende e paesi

**Area:** Data — `data/database.json`
**Type:** Data
**Priority:** High

Nel database si trovano varianti non riconciliate dello stesso soggetto: "Leonardo" vs "Leonardo SPA" come company name; "China" vs "Cina" come country value. Necessario un passaggio sistematico di sanity check e normalizzazione.

> "alle volte c'è scritto Leonardo, alle volte Leonardo SPA [...] alle volte China con la H, alle volte Cina in italiano"

**Azione:** Eseguire `python3 scripts/validate.py` e integrare controlli di normalizzazione. Fare una passata manuale sui campi `name` e `sources.infonodes.country`.

---

### #07 — Supply Chain Map: legenda degli archi assente o incomprensibile

**Area:** Supply Chain → Map — `js/tabs/map.js`, `css/map.css`
**Type:** UX / Content
**Priority:** High

Gli archi colorati sulla mappa non sono auto-esplicativi. Il significato del gradiente di colore (da dove parte e dove arriva l'investimento) va spiegato con una didascalia visibile, non solo nel pannello laterale dopo click.

> "bisogna lavorare a livello di didascalia per spiegare come leggerla [...] quello che è poco chiaro è la spiegazione di cosa mi dicono le linee"

**Proposta:** Aggiungere una legenda inline (non nascosta nel panel) con: pallino = paese con almeno una azienda; arco = flusso investimento; colore = direzione.

---

### #08 — Supply Chain Map: colori degli archi troppo chiari, poco leggibili

**Area:** Supply Chain → Map — `css/map.css`
**Type:** UX
**Priority:** Medium

Il colore degli archi è troppo tenue, specialmente in dark mode. L'esempio citato: l'arco Svizzera → Cina è quasi invisibile. In light mode il problema è ancora peggiore (vedi anche #42 da Laura).

> "il colore dell'arco è troppo chiaro"

**Proposta:** Aumentare l'opacità/saturazione degli archi. Verificare token `--map-arc-*` in `css/map.css` o `css/base.css`.

---

### #09 — Supply Chain Map: mostrare una sola direzione di flusso per click paese

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX / Feature
**Priority:** High

Quando si clicca un paese si vedono sia i flussi in uscita che in entrata, creando confusione visiva. Davide propone due opzioni:
- Aggiungere due pulsanti nel panel ("Mostra solo chi finanzia" / "Mostra solo chi è finanziato")
- Oppure mostrare di default solo i flussi in uscita (flowing out) e offrire toggle per flowing in

> "o si fa una sola informazione oppure una mappa con un bottone [...] avere le due direzioni su due visualizzazioni diverse della mappa, non sovrapposte"

**Files:** `js/tabs/map.js`, `css/map.css`

---

### #10 — Supply Chain Map: testo del panel paese non chiaro

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** Content / UX
**Priority:** Medium

La descrizione mostrata nel panel quando si seleziona un paese (es. "Japan showing two companies and five investors") non è immediatamente comprensibile. Non è chiaro se "investors" siano investitori che investono in Giappone o investitori giapponesi.

> "questo va spiegato meglio perché non è chiara questa descrizione"

**Proposta:** Riscrivere il testo con formula tipo: "X aziende con sede in Japan · Y investitori che finanziano aziende in Japan".

---

### #11 — Supply Chain Map bug: chiusura sidebar senza clear lascia mappa in stato inconsistente

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** Bug
**Priority:** High

Ripro: selezionare un paese → cliccare un'entità nel panel → si apre la sidebar dell'entità → chiudere sidebar con "Close" (non con "Clear") → la mappa rimane in uno stato visivamente anomalo, non è più chiaro cosa sia selezionato.

> "noi adesso vediamo una mappa strana e non capiamo che cos'è [...] va identificata con Playwright e poi capito per bene il problema"

**Azione:** Investigare con Playwright. Il problema è probabilmente che la selezione paese rimane attiva nell'AppState ma il panel è chiuso, lasciando gli archi renderizzati senza contesto.

**Files:** `js/tabs/map.js`, `js/detail-sidebar.js`

---

### #12 — Graph: tooltip persiste navigando ad altre tab

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** Bug
**Priority:** Medium

Il tooltip del nodo nel grafo rimane visibile anche dopo aver navigato ad altra tab. Non viene rimosso dal DOM o nascosto alla navigazione.

> "era rimasto il tooltip del grafo, quindi se clicchi in grafo il tooltip rimane aperto anche su altre pagine"

**Fix:** Aggiungere cleanup del tooltip nel listener di navigazione in `main.js` (o nell'uscita dal tab graph). Verificare come `tip()` in `js/helpers.js` inserisce/rimuove il tooltip.

---

### #13 — Graph: schema colori insufficiente per distinguere i tipi di investitore

**Area:** Supply Chain → Graph — `js/tabs/graph.js`, `css/graph.css`
**Type:** UX
**Priority:** Medium

Con il dataset attuale (165 aziende) i colori tono su tono funzionano visivamente ma non distinguono chiaramente `institution` da `fund`. Quando il dataset crescerà a migliaia di nodi il problema diventerà critico.

> "non è che capisci la differenza tra institution e fund perché sono rodere, le scale di colori si possono migliorare"

**Proposta:** Definire colori distinti per ciascun `type` di entità invece di scala monocromatica. Da fare dopo unificazione database (#03) per avere la lista definitiva dei tipi.

---

### #14 — Companies + Investors: unire in tab "Players" con filtro tipo

**Area:** Supply Chain → Companies, Investors — `js/tabs/companies.js`, `js/tabs/investors.js`
**Type:** Feature
**Priority:** Medium

Companies e Investors sono due tab separate con struttura quasi identica. Davide propone di unirle in un'unica tab "Players" (o nome da definire) con un filtro che permetta di vedere tutti / solo companies / solo investors.

> "si potrebbe fare un unico players con i filtri [...] inserire investors dentro l'attuale pagina companies, inserendo un ulteriore filtro"

**Files:** `js/tabs/companies.js`, `js/tabs/investors.js`, `index.html`, `js/main.js`

---

### #15 — Matrix: candidato alla rimozione nella release finale

**Area:** Supply Chain → Matrix — `js/tabs/matrix.js`
**Type:** Feature (decision)
**Priority:** Low

Matrix è un'altra visualizzazione dei dati già accessibili altrove. Con migliaia di entità la matrice diventa inutilizzabile. Davide suggerisce di rimuoverla o metterla in sandbox.

> "Matrix si può anche eliminare nella release finale [...] se non è utile la mettiamo in una qualche sandbox"

**Note:** Non rimuovere subito. Prima fare un tentativo di renderla più compatta e utile; se non funziona, rimuoverla. Vedi anche #49 (Laura).

---

### #16 — EDF Beneficiaries sidebar: difficile da leggere, da ripulire

**Area:** EDF → Beneficiaries — `js/tabs/edfbrowse.js`, `css/edfbrowse.css`
**Type:** UX
**Priority:** Medium

La sidebar che si apre cliccando un'azienda in EDF Beneficiaries è confusionaria: troppe informazioni, layout poco leggibile, informazioni non gerarchizzate.

> "la sidebar secondo me è poco chiara, bisogna un attimo sistemarla, ci sono informazioni anche, bisogna un po' ripulirla, si legge male"

**Proposta:** Gerarchizzare le informazioni: prima dati identificativi, poi lista progetti, poi dettaglio progetto selezionato. Vedi anche #47 (Laura) che propone di espandere la sidebar a modal/fullpage.

---

### #17 — EDF Beneficiaries: aggiungere filtro capofila vs. partecipante

**Area:** EDF → Beneficiaries — `js/tabs/edfbrowse.js`
**Type:** Feature
**Priority:** Medium

Nel dettaglio di un'azienda EDF si vedono tutti i progetti, ma non è possibile filtrare solo quelli in cui è capofila (coordinatore) vs. semplice partecipante.

> "non puoi filtrare capofila da partecipante, questo è rilevante"

**Cross-ref:** #31 (Andrea solleva lo stesso punto)

---

### #18 — About: riscrivere con info team, fonti di finanziamento, metodologia

**Area:** About — `index.html` (#tab-about), `js/main.js`
**Type:** Content
**Priority:** Medium

La sezione About nella release intermedia/finale deve contenere: chi è InfoNode, chi è DataPitch, biografie del team (con consenso privacy), chi ha finanziato il progetto (Privacy International), ringraziamenti ai beta tester. Non deve essere ridondante con la Intro.

> "inseriremo magari una descrizione di chi è InfoNode, chi è DataPitch e del team che ha lavorato a questo progetto [...] informazioni di trasparenza"

---

### #19 — Wikidata Inspector: aggiungere pulsante di export/copia dati

**Area:** About → Wikidata Inspector — `js/tabs/wikidata.js`
**Type:** Feature
**Priority:** Medium

Non esiste una strategia di export dei dati da Wikidata Inspector. L'utente non ha modo di portarsi fuori le informazioni visualizzate.

> "su Wikidata Inspector andrebbe aggiunto un pulsante copia per estrarre [...] non c'è una strategia di estrazione del dato"

**Cross-ref:** Vedi anche #22 (Copy for AI) e la necessità di una strategia export centralizzata.

---

### #20 — Wikidata Inspector: integrare i dati live nella scheda Company Search

**Area:** Company Search — `js/tabs/companysearch.js`, `js/tabs/wikidata.js`
**Type:** Feature
**Priority:** Medium

I dati Wikidata storati nel database sono un sottoinsieme limitato. Wikidata Inspector fa fetch live ma è una tab separata. Davide propone di aggiungere un pulsante "Wikidata" nella scheda Company Search che mostri i dati live dell'azienda visualizzata, nella stessa pagina (o in fondo alla pagina).

> "avrebbe senso integrare Wikidata Inspector dentro Company Search [...] in modo tale per un'azienda avere tutti i dati su una pagina"

**Proposta:** Aggiungere in fondo alla scheda entità un blocco "Live Wikidata Data" con lazy-fetch al click, oppure un link diretto all'Inspector pre-filtrato su quell'entità.

---

### #21 — "Copy for AI": label non autoesplicativa

**Area:** Global — tutti i tab con il pulsante Copy for AI (`js/copy-ai.js`)
**Type:** UX / Content
**Priority:** Medium

L'etichetta "Copy for AI" non comunica chiaramente cosa fa il pulsante. Un utente non sa che deve aprire un chatbot, incollarci il testo e chiedere un'analisi.

> "l'utilizzo più va spiegato meglio"

**Cross-ref:** #35 (Laura suggerisce label alternativa tipo "Export data" o "Explained with AI")

**Proposta:** Aggiungere un tooltip esplicativo al hover + eventualmente cambiare la label. Esempio: "Esporta dati → analizza con AI".

---

### #22 — EDF Calls Search: candidato alla rimozione/occultamento nella release finale

**Area:** EDF → Calls Search — `js/tabs/eucalls.js`
**Type:** Feature (decision)
**Priority:** Low

EDF Calls Search è uno strumento prevalentemente interno. Davide suggerisce di oscurarlo nella release finale, come per Matrix (#15).

> "questo secondo me è più uno strumento interno nostro, non so se vale la pena lasciarlo"

**Proposta:** Nascondere dalla nav nella release finale con una variabile di configurazione; mantenere il codice per uso interno.

---

## Andrea

---

### #23 — Company Search: stato vuoto senza suggerimenti, difficile onboarding

**Area:** Company Search — `js/tabs/companysearch.js`, `css/companysearch.css`
**Type:** UX
**Priority:** High

Arrivando su Company Search l'utente vede solo un campo di testo vuoto senza alcun indizio su cosa cercare. Chi non conosce i nomi delle aziende del settore è bloccato subito.

> "sarebbe più comodo avere sotto qualche suggerimento, perché le persone magari non hanno nessun nome in mente [...] magari le 5 o una per categoria"

**Proposta:** Mostrare sotto il campo di ricerca un set di suggested companies (es. 4-6 nomi, uno per categoria: startup, difesa, mining, fondo) come chip cliccabili. Già presente autocomplete; basta aggiungere suggestions statiche nell'empty state.

**Files:** `js/tabs/companysearch.js`, `css/companysearch.css`

---

### #24 — Company Search: tag sector/industry non cliccabili per filtrare

**Area:** Company Search — `js/tabs/companysearch.js`
**Type:** UX / Feature
**Priority:** Medium

Nella scheda entità i tag industry (es. "Artificial Intelligence", "Military") non sono cliccabili. L'utente si aspetta di poter cliccare per filtrare le aziende dello stesso settore.

> "se vado su droni non funziona [...] non è che tutti, anche per come siamo abituati noi a usare che ti fa filtrare"

**Proposta:** Rendere i badge industry/sector in Company Search cliccabili per lanciare una ricerca filtrata per quel tag.

---

### #25 — Supply Chain Map: nomi aziende nel panel paese non collegati alla scheda entità

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX / Bug
**Priority:** High

Nel panel laterale che si apre cliccando un paese sulla mappa, i nomi delle aziende elencate non sono link/button. Cliccandoci non succede nulla (o non porta alla scheda dell'azienda).

> "clicco su Maden, qua vorresti delle informazioni di Maden [...] invece almeno vedi le info [...] un piccolo ceco"

**Proposta:** Rendere i nomi azienda nel country panel cliccabili: aprire la scheda Company Search dell'entità (o un mini-popup con i dati principali, come un `openCompanySidebar()`).

**Files:** `js/tabs/map.js`, `js/detail-sidebar.js`

---

### #26 — Graph: nomi investitori nel side panel entità non cliccabili

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** UX / Feature
**Priority:** High

Nel panel di dettaglio che si apre cliccando un nodo nel grafo (es. Nordic Air Defense), i nomi degli investitori nell'elenco non sono cliccabili. L'utente vorrebbe poter navigare alla scheda dell'investitore.

> "sarebbe figo poterli cliccare ovunque [...] ogni volta che viene fuori qualcosa su cui noi abbiamo info vorrei che fosse cliccabile"

**Cross-ref:** #32 (Laura, sidebar Companies ha lo stesso problema)

**Proposta:** Rendere i nomi investitori nel graph detail panel dei link/button che aprono la scheda dell'entità in Company Search o tramite `detail-sidebar.js`.

---

### #27 — Graph Projection: side panel mostra contesto sbagliato (dettaglio entità invece di cluster)

**Area:** Supply Chain → Graph (Projection mode) — `js/tabs/graph.js`
**Type:** Bug / UX
**Priority:** Medium

In modalità Projection il panel laterale mostra ancora il dettaglio di una singola company (Nordic Air Defense rimasto aperto da Network). In Projection l'informazione rilevante è chi co-investe con chi, non il profilo di una singola azienda.

> "su projection non va bene avere Nordic Air Defense perché sarebbe un dettaglio di un'azienda [...] il side panel dovrebbe dirti chi ha investito con chi"

**Proposta:** Al cambio modalità (Network → Bipartite → Projection) chiudere il panel aperto precedentemente e mostrare il panel contestuale al modo selezionato.

---

### #28 — Graph Projection: nomi portfolio nel panel non cliccabili

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** UX
**Priority:** Medium

Nel panel che si apre cliccando un nodo investitore in Projection, i nomi delle aziende in portfolio non sono cliccabili.

> "le aziende in portafoglio, che non sono cliccabili e andrebbero cliccate"

**Cross-ref:** #26 (stesso pattern)

---

### #29 — Copy for AI: output non contestuale alla view/filtro attivo

**Area:** Global — `js/copy-ai.js`
**Type:** Feature
**Priority:** High

"Copy for AI" esporta sempre un dump generale del dataset. Non tiene conto del tab attivo, dei filtri applicati, o della selezione corrente. L'utente si aspetta che esporti esattamente ciò che sta guardando in quel momento.

> "il copy for AI dovrebbe funzionare così: dovrebbe estrarre i dati filtrati [...] se siamo in network ci dice chi è connesso con chi, se siamo in projection ci dice le connessioni tra investitori"

**Proposta:** `buildAiSnapshot()` in `copy-ai.js` deve passare il contesto attivo: tab corrente + filtri attivi + eventuale entità selezionata. Ogni tab module dovrebbe esporre una funzione `buildSnapshot(context)` che genera il testo rilevante per lo stato corrente.

**Files:** `js/copy-ai.js`, `js/tabs/graph.js`, `js/tabs/map.js`, `js/tabs/companies.js`

---

### #30 — EDF Beneficiaries: nessun filtro capofila vs. partecipante

**Area:** EDF → Beneficiaries — `js/tabs/edfbrowse.js`
**Type:** Feature
**Priority:** Medium

Vedi #17 (Davide). Andrea ha sollevato lo stesso punto.

**Cross-ref:** #17

---

### #31 — Navigazione: vicoli ciechi diffusi in tutto il sito

**Area:** Global — tutti i tab
**Type:** UX
**Priority:** High

Il problema principale identificato da Andrea: in molti punti la navigazione si interrompe. L'utente arriva su un dato ma non può proseguire cliccando elementi correlati. Manca il modello di navigazione "Wikipedia" (ogni entità menzionata è raggiungibile).

> "spesso la navigazione diventa un vicolo cieco [...] dovrebbe essere sempre costantemente navigabile, ritornabile, rigirabile"

**Proposta strutturale:**
1. Tutti i nomi di entità (company o investor) che appaiono in qualsiasi contesto (panel, tabella, grafo, mappa) devono essere cliccabili e portare alla scheda in Company Search
2. Ogni scheda deve avere un breadcrumb o back button che permette di tornare al contesto precedente

**Files:** diffuso — `js/tabs/graph.js`, `js/tabs/map.js`, `js/tabs/edfbrowse.js`, `js/tabs/relationships.js`

---

### #32 — Supply Chain Overview: stat card non cliccabili per filtrare

**Area:** Supply Chain → Overview — `js/tabs/overview.js`
**Type:** UX / Feature
**Priority:** Medium

Le stat card nell'Overview (es. "22 Tech", "65 Defense") non sono cliccabili. L'utente si aspetta di poter cliccare per filtrare la vista o essere portato alla tab Companies filtrata per quel settore.

> "se vedo 22 tech mi viene spontaneo cliccare sopra per filtrare"

**Proposta:** Rendere le stat card cliccabili con navigazione a `?research=supply-chain&tab=companies&sector=tech`.

---

## Laura

---

### #33 — Company Search: link al sito ufficiale dell'azienda — decisione editoriale

**Area:** Company Search — `js/tabs/companysearch.js`
**Type:** Content / UX (decisione)
**Priority:** Low

Laura mette in discussione l'utilità di linkare al sito ufficiale dell'azienda (es. Leonardo.com). Per entità di grandi dimensioni il sito è facilmente trovabile; per entità più piccole potrebbe avere senso. Wikipedia invece ha più valore informativo.

> "non lo so, non la metterei io, francamente [...] Wikipedia invece magari può avere più senso"

**Proposta:** Rimuovere il link al sito ufficiale, mantenere Wikipedia + Crunchbase come fonti esterne. Oppure spostarlo in fondo alla scheda come "external links" secondari.

---

### #34 — "Copy for AI": label non autoesplicativa, rinominare

**Area:** Global — `js/copy-ai.js`, tutti i tab
**Type:** UX / Content
**Priority:** Medium

**Cross-ref:** #21 (Davide ha sollevato la stessa cosa)

Laura propone label alternative più chiare: "Export data", "Explained with AI", "Esporta i dati → analizza con AI".

> "copy for AI poi non è una cosa che di solito siamo abituati a vedere [...] spiegherei che cos'è. Tipo explained by AI o qualcosa del genere"

**Proposta:** Rinominare il pulsante in qualcosa come "Esporta per AI" o "Analizza con AI" + aggiungere un breve tooltip che spiega il workflow (copia → apri chatbot → incolla).

---

### #35 — Font: peso troppo sottile (thin), difficile da leggere

**Area:** Global — `css/base.css`, font stack
**Type:** UX / Accessibility
**Priority:** High

Il font Barlow Condensed in variante thin usato per le descrizioni e il body text è troppo sottile, specialmente su schermi non ad alta risoluzione. Gli occhi "vanno insieme".

> "questo font ha thin, medium, large [...] questo è thin, e thin è troppo piccolo, troppo sottile, va insieme agli occhi"

**Proposta:** Aumentare il font-weight del body text da thin/300 a regular/400 o medium/500. Verificare `--font-weight-body` (o equivalente) in `css/base.css`. Applicare specialmente alle descrizioni e ai valori nelle schede.

**Files:** `css/base.css`

---

### #36 — Light mode: contrasto colori insufficiente per testo

**Area:** Global light mode — `css/base.css` (`[data-theme="light"]`)
**Type:** UX / Accessibility
**Priority:** High

In light mode il testo grigio su sfondo grigio chiaro ha contrasto insufficiente. Il problema è sia cromatico (poca differenza tra foreground e background) che tipografico (vedi #35).

> "il colore grigio su grigio va rivisto [...] maggiore contrasto nei colori"

**Proposta:** Rivedere i token `--text`, `--text-dim`, `--surface*` nella sezione `[data-theme="light"]` di `css/base.css` per garantire un rapporto di contrasto WCAG AA minimo (4.5:1 per testo normale).

**Files:** `css/base.css`

---

### #37 — Validation flags "needs review" visibili agli utenti finali

**Area:** Company Search — `js/tabs/companysearch.js`, schede entità
**Type:** UX / Content
**Priority:** High

I flag di validazione interna ("needs review", "roles inferred from investor type only") sono visibili nella scheda entità. Questi sono metadati interni per il team di curation e non devono essere esposti agli utenti finali, che li interpretano come errori nei dati.

> "data flex needs review roles inferred from investor type only [...] che deve fare la persona che utilizza quei dati? [...] nella versione finale questo mette un po'..."

**Proposta:**
- Nascondere completamente i flag `needs_review` e `flagged` dall'interfaccia utente in Company Search
- Sostituire con un disclaimer generico a piè di pagina: "I dati sono raccolti da fonti diverse e verificati dal team. Se trovi un errore [segnalacelo → link GitHub Issues]"
- Opzionalmente: pulsante "Segnala errore" su ogni scheda entità

**Files:** `js/tabs/companysearch.js`

---

### #38 — Supply Chain Overview: tooltip Relationships difficile da scoprire

**Area:** Supply Chain → Overview — `js/tabs/overview.js`, `js/helpers.js`
**Type:** UX
**Priority:** Low

Il tooltip sulla stat card "Relationships" richiede un movimento preciso del cursore per apparire. Non è immediatamente scopribile come le altre card.

> "devo fare veramente dei movimenti di cursore particolari per far comparire la frase [...] forse lo farei più esplicito"

**Proposta:** Rendere il trigger del tooltip meno sensibile (area più ampia) o aggiungere un'icona `?` visibile che al click/hover mostra la spiegazione.

---

### #39 — Supply Chain Overview: colori paesi — connotazione politica indesiderata

**Area:** Supply Chain → Overview (country breakdown) — `js/tabs/overview.js`, `css/components.css`
**Type:** UX / Content
**Priority:** Medium

I colori usati per il breakdown per paese (rosso per Cina e Russia, blu per paesi occidentali) hanno una connotazione politica non intenzionale.

> "non discriminerei la Cina e la Russia con questi colori rosso comunisti [...] colore unico, o differenziare per continente"

**Proposta:** Usare una palette neutrale basata su continenti (Europa, Asia, Americhe, ecc.) senza associazioni cromatiche politiche. Oppure usare un colore unico con intensità proporzionale al numero di entità.

---

### #40 — Sidebar/panel: posizionare a sinistra invece che a destra

**Area:** Global — tutti i panel laterali (`js/detail-sidebar.js`, `js/tabs/map.js`, `js/tabs/graph.js`, `js/tabs/edfbrowse.js`)
**Type:** UX
**Priority:** Medium

Tutti i panel laterali si aprono a destra. Laura (e poi confermato da tutti) preferisce sinistra per ragioni di UX consolidate: Google Maps ha il panel a sinistra, la lettura occidentale va da sinistra a destra, il braccio destro rimane libero per interagire con la mappa/grafo.

> "il pannello about dismert lo vorrei a sinistra e non a destra [...] Google Maps ce l'ha a sinistra [...] sto sulla destra per muovere la mappa"

**Proposta:** Spostare tutti i panel laterali a sinistra. Valutare se aggiungere un toggle L/R per user preference (opzionale). In alternativa: testare con due utenti prima di decidere definitivamente.

**Files:** `css/components.css`, `js/detail-sidebar.js`, `css/map.css`, `css/graph.css`, `css/edfbrowse.css`

---

### #41 — Supply Chain Map light mode: colori slavati, poco contrasto

**Area:** Supply Chain → Map — `css/map.css`, `css/base.css` (`[data-theme="light"]`)
**Type:** UX
**Priority:** High

In light mode la mappa Supply Chain ha colori "slavati" (poco contrastati). I punti sui paesi e gli archi si distinguono a malapena dallo sfondo. La dark mode regge molto meglio.

> "la mappa nella versione chiara non regge il confronto [...] i colori non mi piacciono [...] poco contrasto, si distinguono male"

**Cross-ref:** #08 (Davide, archi troppo chiari anche in dark)

**Proposta:** Rivedere `--map-bg`, `--map-land`, `--map-arc-*` nella sezione light di `css/base.css`. Portare i colori mappa in light mode ad avere almeno lo stesso livello di contrasto della dark mode.

---

### #42 — Supply Chain Map: interazione semplificata (solo paesi sorgente, click rivela destinazioni)

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX / Feature
**Priority:** Medium

Laura propone un modello di interazione più semplice e direzionale: inizialmente si vedono solo i punti dei paesi da cui **partono** investimenti; quando si clicca un paese, si illuminano i paesi destinazione e tutti gli altri punti spariscono.

> "i punti colorati sulla mappa siano unicamente quelli dei paesi da cui partono gli investimenti e una volta cliccato il punto si illuminano i paesi in cui arriva l'investimento [...] quelli che non sono collegati a quel punto spariscono"

**Cross-ref:** #09 (Davide propone toggle flowing-in / flowing-out — variante dello stesso problema)

**Note:** Le due proposte (Davide e Laura) sono compatibili. Una possibile sintesi: default = mostra solo paesi sorgente; click paese = mostra archi in uscita + evidenzia destinazioni; bottone toggle "Mostra flussi in entrata" per invertire la vista.

---

### #43 — Supply Chain Map: click area vuota per deselezionare il paese

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX
**Priority:** Low

Per deselezionare un paese bisogna cliccare la X nella sidebar. L'utente si aspetta di poter cliccare su un'area vuota della mappa per uscire dalla selezione.

> "magari sarebbe meglio cliccare sulla mappa in un posto casuale per uscire dal paese, non dover schiacciare la x della sidebar"

**Fix:** Aggiungere un listener `click` sul background SVG della mappa che chiama la funzione di deselect/clear.

**Files:** `js/tabs/map.js`

---

### #44 — Graph Projection: la gravità non lascia i nodi dove li trascina l'utente

**Area:** Supply Chain → Graph (Projection) — `js/tabs/graph.js`
**Type:** UX / Bug
**Priority:** Medium

Dopo aver trascinato un nodo manualmente, la simulazione fisica lo riporta indietro. L'utente vorrebbe poter "pinnare" un nodo in una posizione per facilitare la lettura, come avviene nei software di network analysis professionali (Gephi, ecc.).

> "quando in supply chain, graph, projection, tu sposti un quadrato nello schermo, il quadrato deve rimanere fermo lì [...] non ci deve essere la gravità"

**Proposta:** Aggiungere `pin` on drag-end: impostare `node.fx = node.x; node.fy = node.y` alla fine del drag per fissare il nodo. Doppio-click per liberarlo. Verificare implementazione drag in D3 force simulation.

**Files:** `js/tabs/graph.js`

---

### #45 — Graph: barra filtri confusa, nessun separatore tra tipo vista e tipo settore

**Area:** Supply Chain → Graph — `js/tabs/graph.js`, `css/graph.css`
**Type:** UX
**Priority:** Medium

I controlli nella toolbar del Graph (Network / Bipartite / Projection / All / Startup / Defense / Mining / Tech) sembrano tutti dello stesso tipo ma sono due categorie diverse: modalità di visualizzazione e filtri settoriali. Un nuovo utente non percepisce la differenza.

> "non si capisce più la differenza tra network, bipartite projection e startup, defense, mining, tech, all [...] sembrano sei cose uguali [...] basterebbe magari una lineetta che separa"

**Proposta:** Aggiungere un separatore visivo (divisore + label "Vista" / "Settore") nella toolbar. Oppure due gruppi di pulsanti distinti con label di gruppo.

**Files:** `css/graph.css`, `index.html`

---

### #46 — EDF Beneficiaries: sidebar troppo piccola, aprire come modal/fullpage

**Area:** EDF → Beneficiaries — `js/tabs/edfbrowse.js`, `css/edfbrowse.css`
**Type:** UX
**Priority:** Medium

**Cross-ref:** #16 (Davide, sidebar EDF Beneficiaries poco chiara)

La sidebar laterale che si apre cliccando un'azienda in EDF Beneficiaries contiene troppi dati per essere leggibile in quella dimensione. Laura propone di aprire le informazioni come elemento principale (modal fullscreen, o area inline sotto la tabella).

> "quando clicco qua non voglio più vedere una sidebar, voglio vedere una pagina grossa [...] troppa roba [...] si aprisse il dropdown qua e si apre qua, però deve essere più grosso"

**Proposta:** Valutare due alternative: (a) espandere la sidebar a larghezza `--sl-w-lg` (800px) con scroll interno; (b) aprire come modal overlay centrato. Decidere in base a test.

---

### #47 — EDF Calls Search: rimuovere label "pattern:" dai risultati

**Area:** EDF → Calls Search — `js/tabs/eucalls.js`
**Type:** Bug / Content
**Priority:** Low

Nei risultati di ricerca di EDF Calls, il nome del progetto è preceduto da "pattern:" che è chiaramente un placeholder/label tecnica rimasta visibile.

> "togliamo pattern da IDF call search [...] toglierei pattern dall'inizio del nome del progetto perché non si capisce a cosa si riferisce"

**Fix:** Cercare nel template HTML di `eucalls.js` dove viene renderizzato il campo `pattern` e rimuovere il prefisso testuale.

**Files:** `js/tabs/eucalls.js`

---

### #48 — Supply Chain Matrix: rimuovere o semplificare significativamente

**Area:** Supply Chain → Matrix — `js/tabs/matrix.js`
**Type:** Feature (decision)
**Priority:** Low

**Cross-ref:** #15 (Davide, stesso punto)

Laura: "che cazzo è? Non si capisce. Sono le stesse informazioni di prima in un'altra forma."

Consenso emerso dalla sessione: tentare prima una versione più compatta e leggibile; se non funziona, rimuoverla dalla nav finale.

---

### #49 — EDF Map: click area vuota per deselezionare il paese

**Area:** EDF → Map — `js/tabs/edfmap.js`
**Type:** UX
**Priority:** Low

Stesso problema di #43 (Supply Chain Map). Per deselezionare un paese nella EDF Map bisogna usare la X della sidebar. Laura si aspetta di poter cliccare sulla mappa vuota.

**Cross-ref:** #43

**Fix:** Stesso pattern di fix: listener `click` sul background SVG per chiamare il deselect.

**Files:** `js/tabs/edfmap.js`

---

### #50 — Company Search: scheda fondo — numero portfolio non spiega quali aziende



**Area:** Company Search — `js/tabs/companysearch.js`
**Type:** UX
**Priority:** Medium

Sulla scheda di un investitore/fondo, il campo "Portfolio: 1" non è cliccabile né espande per mostrare quale/quali aziende sono in portfolio. L'utente deve scorrere fino alla sezione "Connections" per trovarlo, e il collegamento non è ovvio.

> "uno portfolio e già direttamente direi qual è l'azienda [...] non è chiara la conseguenza"

**Proposta:** Rendere il numero di portfolio nella Key Facts section cliccabile (o inline-expandable) per mostrare la lista delle aziende. In alternativa, spostare la lista portfolio direttamente nella sezione Key Facts invece che in fondo alla pagina.

**Files:** `js/tabs/companysearch.js`

---

## Issue aggiuntive (seconda analisi dei transcript)

Le seguenti issue sono emerse da una rilettura approfondita dei transcript. Attribuite al rispettivo utente.

---

### #51 — [Davide] Investigation page: riproporre come sezione pubblicazione ricerca

**Area:** `automated-investigation.html`, nav — `index.html`, `js/main.js`
**Type:** Feature / Content
**Priority:** Low

Davide chiede esplicitamente di rimuovere la pagina Investigation nella sua forma attuale (generata automaticamente). Nella release finale quella sezione diventerà il luogo dove pubblicare inchieste, report e output di ricerca prodotti dal team infonodes.

> "Investigation è figo, ma lo togliamo [...] diventerà la sezione in cui pubblichiamo la ricerca o eventuali altri output di inchiesta, di ricerca che dal nostro progetto verranno fuori"

**Proposta:** Rimuovere `automated-investigation.html` dalla nav. Creare un placeholder per la sezione "Ricerca / Reports" nel menu principale, inizialmente vuoto o con un "coming soon".

---

### #52 — [Davide] Data Issues tab: armonizzare dimensione font con le altre pagine

**Area:** About → Data Issues — `js/tabs/knownissues.js`, `css/about.css`
**Type:** UX
**Priority:** Low

Davide ha notato che il font della tab Data Issues ha dimensioni diverse rispetto alle altre pagine. Va allineato al sistema tipografico standard.

> "si armonizzerai solo la grandezza del fondo con le altre pagine"

**Fix:** Verificare che `#tab-knownissues` usi i token `--fs-*` standard e non un override locale. Controllare il rendering del Markdown da `marked` — potrebbe applicare stili H1/H2 del browser invece dei token CSS.

**Files:** `css/about.css`, `js/tabs/knownissues.js`

---

### #53 — [Davide] Data Quality tab: tenere e risistemare per trasparenza metodologica

**Area:** About → Data Quality — `js/tabs/quality.js`
**Type:** Content / Feature
**Priority:** Low

Davide inizialmente la ritiene inutile, poi rivaluta: il valore è mostrare con trasparenza come i dati sono stati trattati. Va mantenuta e aggiornata, non rimossa.

> "il valore qual è? Che tu fai vedere con un po' di più trasparenza come hai trattato i dati [...] se vuoi la risistemiamo, ma la teniamo"

**Proposta:** Revisionare il contenuto di Data Quality con una narrativa chiara sulla metodologia di raccolta, verifica e aggiornamento dei dati. Renderla leggibile per un utente esterno, non solo per il team.

---

### #54 — [Davide] Wikidata Inspector: dare più prominenza nella navigazione

**Area:** Nav — `index.html`, `js/main.js`
**Type:** UX / Feature
**Priority:** Low

Wikidata Inspector è attualmente nascosto in fondo alla sezione About. Davide propone di dargli più visibilità nel menu principale, in vista della fusione dei gruppi (EDF + Supply Chain → unico gruppo, che libera spazio nella nav).

> "Wikidata Inspector, se lo vogliamo tenere o lo togliamo fuori [...] lo terrei, forse gli darei anche rilevanza inserendolo nel menu in alto"

**Note:** Da rivalutare dopo la riorganizzazione della nav conseguente al merge dei gruppi (#03 e #04).

---

### #55 — [Andrea] Graph: nessun auto-zoom dopo cambio filtro settore

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** UX / Bug
**Priority:** Medium

Dopo aver applicato un filtro settore (es. Startup) o cambiato modalità, il grafo non si ridimensiona automaticamente per mostrare i nodi visibili. L'utente deve zoomare manualmente per trovare i nodi.

> "poi si dovrebbe auto zoomare da solo"

**Fix:** Dopo ogni ridisegno del grafo (cambio filtro, cambio modalità), chiamare una funzione di fit/zoom automatico che adatta la viewport ai nodi visibili. In D3 force: usare `zoom.transform` con `fitExtent` dopo la stabilizzazione della simulazione.

**Files:** `js/tabs/graph.js`

---

### #56 — [Andrea] Graph Bipartite: modalità difficile da capire senza contesto

**Area:** Supply Chain → Graph (Bipartite mode) — `js/tabs/graph.js`
**Type:** UX / Content
**Priority:** Medium

La modalità Bipartite è quella meno intuitiva delle tre. Il principio (due colonne: investitori a sinistra, aziende a destra, archi = investimento) non è immediatamente chiaro dal solo titolo.

> "bipartite: difficile da capire come si usa [...] lo dividi in due, quindi fai un matching praticamente"

**Proposta:** Aggiungere nel panel "How to explore" (quando Bipartite è attivo) una descrizione specifica: "Vista bipartita: investitori a sinistra, aziende a destra. Gli archi mostrano chi ha investito in cosa." Opzionalmente, aggiungere label visive sulle due colonne.

**Files:** `js/tabs/graph.js`, eventualmente `index.html`

---

### #57 — [Andrea] Graph: panel "How to explore" a destra, controlli a sinistra/basso — incoerenza spaziale

**Area:** Supply Chain → Graph — `js/tabs/graph.js`, layout
**Type:** UX
**Priority:** Medium

Il panel "How to explore" (che spiega le modalità e come usarle) appare a destra dello schermo, ma i pulsanti di controllo effettivi (Network / Bipartite / Projection / settori) sono posizionati in basso o in un'altra zona. L'utente legge le istruzioni a destra, poi deve cercare i controlli altrove.

> "me lo spiega qua, però poi devo andare a cercarle qui sotto nella pagina [...] mi aspetto di trovare dei bottoni sulla destra e non di dover tornare sulla sinistra in basso"

**Proposta:** Spostare il panel "How to explore" nello stesso lato dei controlli, oppure spostare i controlli vicino al panel. Istruzioni e controlli che descrivono devono essere spazialmente adiacenti.

**Cross-ref:** #40 (sidebar a sinistra), #45 (separatore tra tipo vista e settore)

---

### #58 — [Laura] Disclaimer copertura dati per paesi non trasparenti (Cina, Russia, Arabia Saudita)

**Area:** Global — Company Search, Supply Chain Map, EDF Map
**Type:** Content / UX
**Priority:** Medium

Un limite strutturale del dataset: i dati Crunchbase per paesi con scarsa trasparenza societaria (Cina, Russia, Arabia Saudita) sono incompleti o assenti. L'utente che clicca su queste entità trova poco e non capisce perché.

> "c'è un grosso limite che non sta a noi [...] le aziende da cui abbiamo preso i dati su Crunchbase a seconda del paese dove sono e della trasparenza di quel paese possiamo avere dati o no. Quindi Cina, Russia, Saudi Arabia, difficile avere dati."

**Proposta:** Aggiungere una nota contestuale quando si visualizza un'entità di questi paesi, o quando si seleziona il paese sulla mappa: "I dati per aziende con sede in [paese] possono essere limitati per scarsa disponibilità pubblica di informazioni societarie." Potrebbe essere un tooltip sul nome del paese o una riga nella scheda entità.

---

### #59 — [Laura] Entity ID (IV-0143) visualizzato senza spiegazione — sembra un ID utente

**Area:** Company Search — `js/tabs/companysearch.js`
**Type:** UX / Content
**Priority:** Low

Laura ha visto l'ID "IV0143" nella scheda di un fondo e ha chiesto cosa fosse, pensando inizialmente fosse un identificatore utente. Gli ID interni del database (`IN-*`, `IV-*`) non hanno una label esplicativa nell'interfaccia.

> "IV0143? È un identificatore di utenti."

**Proposta:** Aggiungere una label o tooltip sull'ID: es. mostrare come "ID: IV-0143" con tooltip "Identificatore interno del database infonodes". In alternativa, nascondere completamente l'ID dall'interfaccia utente e tenerlo solo nel codice/export.

**Files:** `js/tabs/companysearch.js`
