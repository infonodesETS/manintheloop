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



### #07 — Supply Chain Map: legenda degli archi assente o incomprensibile

**Area:** Supply Chain → Map — `js/tabs/map.js`, `css/map.css`
**Type:** UX / Content
**Priority:** High

Gli archi colorati sulla mappa non sono auto-esplicativi. Il significato del gradiente di colore (da dove parte e dove arriva l'investimento) va spiegato con una didascalia visibile, non solo nel pannello laterale dopo click.

> "bisogna lavorare a livello di didascalia per spiegare come leggerla [...] quello che è poco chiaro è la spiegazione di cosa mi dicono le linee"

**Proposta:** Aggiungere una legenda inline (non nascosta nel panel) con: pallino = paese con almeno una azienda; arco = flusso investimento; colore = direzione.

---

### #08 — Supply Chain Map: colori degli archi troppo chiari, poco leggibili ✅ RESOLVED

**Area:** Supply Chain → Map — `css/map.css`
**Type:** UX
**Priority:** Medium

Il colore degli archi è troppo tenue, specialmente in dark mode. L'esempio citato: l'arco Svizzera → Cina è quasi invisibile. In light mode il problema è ancora peggiore (vedi anche #42 da Laura).

> "il colore dell'arco è troppo chiaro"

**Proposta:** Aumentare l'opacità/saturazione degli archi. Verificare token `--map-arc-*` in `css/map.css` o `css/base.css`.

**Status:** ✓ Resolved — 2026-03-28 — Arc color boosted: dark mode `#68ccd1` → `#40e8f0`, light mode `#0a5080` → `#0d6aaa`. Stroke range `[1,4]` → `[1.5,5]`. Opacity range `[0.55,0.9]` → `[0.75,1.0]`. Faint end `0.07` → `0.18`. Gradient direction effect preserved.

---

### #09 — Supply Chain Map: mostrare una sola direzione di flusso per click paese ✅ RESOLVED

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX / Feature
**Priority:** High

Quando si clicca un paese si vedono sia i flussi in uscita che in entrata, creando confusione visiva. Davide propone due opzioni:
- Aggiungere due pulsanti nel panel ("Mostra solo chi finanzia" / "Mostra solo chi è finanziato")
- Oppure mostrare di default solo i flussi in uscita (flowing out) e offrire toggle per flowing in

> "o si fa una sola informazione oppure una mappa con un bottone [...] avere le due direzioni su due visualizzazioni diverse della mappa, non sovrapposte"

**Files:** `js/tabs/map.js`, `css/map.css`

**Status:** ✓ Resolved — 2026-03-28 — On country click, only outbound arcs shown (`d.src === iso`). Covered by #42 implementation.

---

### #10 — Supply Chain Map: testo del panel paese non chiaro ✅ RESOLVED

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** Content / UX
**Priority:** Medium

La descrizione mostrata nel panel quando si seleziona un paese (es. "Japan showing two companies and five investors") non è immediatamente comprensibile. Non è chiaro se "investors" siano investitori che investono in Giappone o investitori giapponesi.

> "questo va spiegato meglio perché non è chiara questa descrizione"

**Proposta:** Riscrivere il testo con formula tipo: "X aziende con sede in Japan · Y investitori che finanziano aziende in Japan".

**Status:** ✓ Resolved — 2026-03-28 — Rewritten to concise two-line format: `"X companies · Y local investors headquartered in [Country].<br>↓ N foreign investors funding companies here · ↑ M from [Country] investing abroad (…)"`.

---

### #11 — Supply Chain Map bug: chiusura sidebar senza clear lascia mappa in stato inconsistente ✅ RESOLVED

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** Bug
**Priority:** High

Ripro: selezionare un paese → cliccare un'entità nel panel → si apre la sidebar dell'entità → chiudere sidebar con "Close" (non con "Clear") → la mappa rimane in uno stato visivamente anomalo, non è più chiaro cosa sia selezionato.

> "noi adesso vediamo una mappa strana e non capiamo che cos'è [...] va identificata con Playwright e poi capito per bene il problema"

**Azione:** Investigare con Playwright. Il problema è probabilmente che la selezione paese rimane attiva nell'AppState ma il panel è chiuso, lasciando gli archi renderizzati senza contesto.

**Files:** `js/tabs/map.js`, `js/detail-sidebar.js`

**Status:** ✓ Resolved — 2026-03-28 — Added `setSidebarCloseHook(fn)` to `detail-sidebar.js`; map sets `clearMapFilter` as hook before opening any entity sidebar, so closing the sidebar restores clean map state.

---

### #12 — Graph: tooltip persiste navigando ad altre tab ✅ RESOLVED

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** Bug
**Priority:** Medium

Il tooltip del nodo nel grafo rimane visibile anche dopo aver navigato ad altra tab. Non viene rimosso dal DOM o nascosto alla navigazione.

> "era rimasto il tooltip del grafo, quindi se clicchi in grafo il tooltip rimane aperto anche su altre pagine"

**Fix:** Aggiungere cleanup del tooltip nel listener di navigazione in `main.js` (o nell'uscita dal tab graph). Verificare come `tip()` in `js/helpers.js` inserisce/rimuove il tooltip.

**Status:** ✓ Resolved — 2026-03-28 — `hideTip()` imported and called on graph exit in `js/main.js`.

---

### #13 — Graph: schema colori insufficiente per distinguere i tipi di investitore

**Area:** Supply Chain → Graph — `js/tabs/graph.js`, `css/graph.css`
**Type:** UX
**Priority:** Medium

Con il dataset attuale (165 aziende) i colori tono su tono funzionano visivamente ma non distinguono chiaramente `institution` da `fund`. Quando il dataset crescerà a migliaia di nodi il problema diventerà critico.

> "non è che capisci la differenza tra institution e fund perché sono rodere, le scale di colori si possono migliorare"

**Proposta:** Definire colori distinti per ciascun `type` di entità invece di scala monocromatica. Da fare dopo unificazione database (#03) per avere la lista definitiva dei tipi.

---

### #15 — Matrix: candidato alla rimozione nella release finale ✅ RESOLVED

**Area:** Supply Chain → Matrix — `js/tabs/matrix.js`
**Type:** Feature (decision)
**Priority:** Low

Matrix è un'altra visualizzazione dei dati già accessibili altrove. Con migliaia di entità la matrice diventa inutilizzabile. Davide suggerisce di rimuoverla o metterla in sandbox.

> "Matrix si può anche eliminare nella release finale [...] se non è utile la mettiamo in una qualche sandbox"

**Status:** ✓ Resolved — 2026-03-28 — Matrix tab removed from navigation, tab pane removed from `index.html`, `css/matrix.css` unlinked, `initMatrix`/`setMatrixSector`/`closeMxDetail` import and all wiring removed from `main.js`. Files `js/tabs/matrix.js` and `css/matrix.css` retained as archive only.

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

### #21 — "Copy for AI": label non autoesplicativa ✅ RESOLVED

**Area:** Global — tutti i tab con il pulsante Copy for AI (`js/copy-ai.js`)
**Type:** UX / Content
**Priority:** Medium

L'etichetta "Copy for AI" non comunica chiaramente cosa fa il pulsante. Un utente non sa che deve aprire un chatbot, incollarci il testo e chiedere un'analisi.

> "l'utilizzo più va spiegato meglio"

**Cross-ref:** #35 (Laura suggerisce label alternativa tipo "Export data" o "Explained with AI")

**Proposta:** Aggiungere un tooltip esplicativo al hover + eventualmente cambiare la label. Esempio: "Esporta dati → analizza con AI".

**Status:** ✓ Resolved — 2026-03-28 — Label → "Export in .md format"; title → "Export data filtered here to paste into Mistral, Claude, ChatGPT to ask for an explanation". Export is now fully contextual per tab: map exports selected country + flows, graph exports selected node or visible companies, EDF tabs use dedicated snapshot builders.

---


## Andrea

---

### #23 — Company Search: stato vuoto senza suggerimenti, difficile onboarding ✅ RESOLVED

**Area:** Company Search — `js/tabs/companysearch.js`, `css/companysearch.css`
**Type:** UX
**Priority:** High

Arrivando su Company Search l'utente vede solo un campo di testo vuoto senza alcun indizio su cosa cercare. Chi non conosce i nomi delle aziende del settore è bloccato subito.

> "sarebbe più comodo avere sotto qualche suggerimento, perché le persone magari non hanno nessun nome in mente [...] magari le 5 o una per categoria"

**Proposta:** Mostrare sotto il campo di ricerca un set di suggested companies (es. 4-6 nomi, uno per categoria: startup, difesa, mining, fondo) come chip cliccabili. Già presente autocomplete; basta aggiungere suggestions statiche nell'empty state.

**Files:** `js/tabs/companysearch.js`, `css/companysearch.css`

**Status:** ✓ Resolved — 2026-03-28 — `renderSuggestions()` shows 20 random entities in the existing `#cs-ac` dropdown on input focus (empty state). Also extended search to match descriptions: `_desc` field added to entity index; description matches score 15 with inline snippet shown. `.cs-ac-desc` CSS added.

---

### #24 — Company Search: tag sector/industry non cliccabili per filtrare ✅ RESOLVED

**Area:** Company Search — `js/tabs/companysearch.js`
**Type:** UX / Feature
**Priority:** Medium

Nella scheda entità i tag industry (es. "Artificial Intelligence", "Military") non sono cliccabili. L'utente si aspetta di poter cliccare per filtrare le aziende dello stesso settore.

> "se vado su droni non funziona [...] non è che tutti, anche per come siamo abituati noi a usare che ti fa filtrare"

**Proposta:** Rendere i badge industry/sector in Company Search cliccabili per lanciare una ricerca filtrata per quel tag.

**Status:** ✓ Resolved — 2026-03-28 — Industries, industry groups, and entity tags converted to `<button class="cs-tag" data-query="...">`. Click populates search input and opens dropdown. Tags also added to `_key` in search index so results are accurate.

---

### #25 — Supply Chain Map: nomi aziende nel panel paese non collegati alla scheda entità ✅ RESOLVED

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX / Bug
**Priority:** High

Nel panel laterale che si apre cliccando un paese sulla mappa, i nomi delle aziende elencate non sono link/button. Cliccandoci non succede nulla (o non porta alla scheda dell'azienda).

> "clicco su Maden, qua vorresti delle informazioni di Maden [...] invece almeno vedi le info [...] un piccolo ceco"

**Proposta:** Rendere i nomi azienda nel country panel cliccabili: aprire la scheda Company Search dell'entità (o un mini-popup con i dati principali, come un `openCompanySidebar()`).

**Files:** `js/tabs/map.js`, `js/detail-sidebar.js`

**Status:** ✓ Resolved — 2026-03-28 — Added `↗` button to each entity row in map country panel; wires to `openCompanySidebar` / `openInvestorSidebar`. Hover-reveal via `.map-item-open` CSS.

---

### #26 — Graph: nomi investitori nel side panel entità non cliccabili ✅ RESOLVED

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** UX / Feature
**Priority:** High

Nel panel di dettaglio che si apre cliccando un nodo nel grafo (es. Nordic Air Defense), i nomi degli investitori nell'elenco non sono cliccabili. L'utente vorrebbe poter navigare alla scheda dell'investitore.

> "sarebbe figo poterli cliccare ovunque [...] ogni volta che viene fuori qualcosa su cui noi abbiamo info vorrei che fosse cliccabile"

**Cross-ref:** #32 (Laura, sidebar Companies ha lo stesso problema)

**Proposta:** Rendere i nomi investitori nel graph detail panel dei link/button che aprono la scheda dell'entità in Company Search o tramite `detail-sidebar.js`.

**Status:** ✓ Resolved — 2026-03-28 — Entity names in graph panel (portfolio companies, investors, co-investors) converted to `.gv-entity-link` buttons with event delegation → `openCompanySidebar` / `openInvestorSidebar`.

---

### #27 — Graph Projection: side panel mostra contesto sbagliato (dettaglio entità invece di cluster) ✅ RESOLVED

**Area:** Supply Chain → Graph (Projection mode) — `js/tabs/graph.js`
**Type:** Bug / UX
**Priority:** Medium

In modalità Projection il panel laterale mostra ancora il dettaglio di una singola company (Nordic Air Defense rimasto aperto da Network). In Projection l'informazione rilevante è chi co-investe con chi, non il profilo di una singola azienda.

> "su projection non va bene avere Nordic Air Defense perché sarebbe un dettaglio di un'azienda [...] il side panel dovrebbe dirti chi ha investito con chi"

**Proposta:** Al cambio modalità (Network → Bipartite → Projection) chiudere il panel aperto precedentemente e mostrare il panel contestuale al modo selezionato.

**Status:** ✓ Resolved — 2026-03-28 — `closeGraphDetail()` called at the top of `setGraphView()` in `js/tabs/graph.js`.

---

### #28 — Graph Projection: nomi portfolio nel panel non cliccabili ✅ RESOLVED

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** UX
**Priority:** Medium

Nel panel che si apre cliccando un nodo investitore in Projection, i nomi delle aziende in portfolio non sono cliccabili.

> "le aziende in portafoglio, che non sono cliccabili e andrebbero cliccate"

**Cross-ref:** #26 (stesso pattern)

**Status:** ✓ Resolved — 2026-03-28 — Same fix as #26; `graphShowPanel` is shared across all modes including Projection.

---

### #29 — Copy for AI: output non contestuale alla view/filtro attivo ✅ RESOLVED

**Area:** Global — `js/copy-ai.js`
**Type:** Feature
**Priority:** High

**Status:** ✓ Resolved — 2026-03-28 — `buildAiSnapshot()` now dispatches per active tab. Map exports selected country + flows; graph exports selected node detail (portfolio or investors) or filtered company list; companies/investors/relationships export active filters + search; EDF tabs use dedicated `buildSnapshot()` functions from `edfbrowse.js` and `edfmap.js`. Button renamed "Export in .md format".

"Copy for AI" esporta sempre un dump generale del dataset. Non tiene conto del tab attivo, dei filtri applicati, o della selezione corrente. L'utente si aspetta che esporti esattamente ciò che sta guardando in quel momento.

> "il copy for AI dovrebbe funzionare così: dovrebbe estrarre i dati filtrati [...] se siamo in network ci dice chi è connesso con chi, se siamo in projection ci dice le connessioni tra investitori"

**Proposta:** `buildAiSnapshot()` in `copy-ai.js` deve passare il contesto attivo: tab corrente + filtri attivi + eventuale entità selezionata. Ogni tab module dovrebbe esporre una funzione `buildSnapshot(context)` che genera il testo rilevante per lo stato corrente.

**Files:** `js/copy-ai.js`, `js/tabs/graph.js`, `js/tabs/map.js`, `js/tabs/companies.js`

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

**Partial progress — 2026-03-28:**
- EDF Browse: clicking an org row now opens its detail drawer and syncs URL (`?entity=KEY&entity-name=slug`). Closing the drawer removes entity from URL. Page load with entity param restores the open drawer. Cross-tab navigation from EDF Overview "Top Participants" chart opens the drawer directly via `pendingOrgKey` (not via search field).

---

### #32 — Supply Chain Overview: stat card non cliccabili per filtrare ✅ RESOLVED

**Area:** Supply Chain → Overview — `js/tabs/overview.js`
**Type:** UX / Feature
**Priority:** Medium

Le stat card nell'Overview (es. "22 Tech", "65 Defense") non sono cliccabili. L'utente si aspetta di poter cliccare per filtrare la vista o essere portato alla tab Companies filtrata per quel settore.

> "se vedo 22 tech mi viene spontaneo cliccare sopra per filtrare"

**Proposta:** Rendere le stat card cliccabili con navigazione a `?research=supply-chain&tab=companies&sector=tech`.

---

## Laura

---


### #34 — "Copy for AI": label non autoesplicativa, rinominare ✅ RESOLVED

**Area:** Global — `js/copy-ai.js`, tutti i tab
**Type:** UX / Content
**Priority:** Medium

**Cross-ref:** #21 (Davide ha sollevato la stessa cosa)

Laura propone label alternative più chiare: "Export data", "Explained with AI", "Esporta i dati → analizza con AI".

> "copy for AI poi non è una cosa che di solito siamo abituati a vedere [...] spiegherei che cos'è. Tipo explained by AI o qualcosa del genere"

**Proposta:** Rinominare il pulsante in qualcosa come "Esporta per AI" o "Analizza con AI" + aggiungere un breve tooltip che spiega il workflow (copia → apri chatbot → incolla).

**Status:** ✓ Resolved — 2026-03-28 — Same fix as #21.

---

### #35 — Font: peso troppo sottile (thin), difficile da leggere ✅ RESOLVED

**Area:** Global — `css/base.css`, font stack
**Type:** UX / Accessibility
**Priority:** High

Il font Barlow Condensed in variante thin usato per le descrizioni e il body text è troppo sottile, specialmente su schermi non ad alta risoluzione. Gli occhi "vanno insieme".

> "questo font ha thin, medium, large [...] questo è thin, e thin è troppo piccolo, troppo sottile, va insieme agli occhi"

**Proposta:** Aumentare il font-weight del body text da thin/300 a regular/400 o medium/500. Verificare `--font-weight-body` (o equivalente) in `css/base.css`. Applicare specialmente alle descrizioni e ai valori nelle schede.

**Files:** `css/base.css`

**Status:** ✓ Resolved — 2026-03-28 — `--fs-xs` bumped to `.70rem`; `body { font-weight: 400; }` set in `css/base.css`.

---

### #36 — Light mode: contrasto colori insufficiente per testo ✅ RESOLVED

**Area:** Global light mode — `css/base.css` (`[data-theme="light"]`)
**Type:** UX / Accessibility
**Priority:** High

In light mode il testo grigio su sfondo grigio chiaro ha contrasto insufficiente. Il problema è sia cromatico (poca differenza tra foreground e background) che tipografico (vedi #35).

> "il colore grigio su grigio va rivisto [...] maggiore contrasto nei colori"

**Proposta:** Rivedere i token `--text`, `--text-dim`, `--surface*` nella sezione `[data-theme="light"]` di `css/base.css` per garantire un rapporto di contrasto WCAG AA minimo (4.5:1 per testo normale).

**Files:** `css/base.css`

**Status:** ✓ Resolved — 2026-03-28 — `--text-faint` light darkened to `#6c6966` (WCAG AA), `--dim` light raised to `rgba(0,0,0,0.60)` for nav buttons.

---

### #37 — Validation flags "needs review" visibili agli utenti finali ✅ RESOLVED

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

**Status:** ✓ Resolved — 2026-03-28 — Validation flags card hidden (`display:none`) in `companysearch.js`.

---

### #38 — Supply Chain Overview: tooltip Relationships difficile da scoprire ✅ RESOLVED

**Area:** Supply Chain → Overview — `js/tabs/overview.js`, `js/helpers.js`
**Type:** UX
**Priority:** Low

Il tooltip sulla stat card "Relationships" richiede un movimento preciso del cursore per apparire. Non è immediatamente scopribile come le altre card.

> "devo fare veramente dei movimenti di cursore particolari per far comparire la frase [...] forse lo farei più esplicito"

**Proposta:** Rendere il trigger del tooltip meno sensibile (area più ampia) o aggiungere un'icona `?` visibile che al click/hover mostra la spiegazione.

**Status:** ✓ Resolved — 2026-03-28 — `cursor: help` added to `.stat-card[title]` in `css/components.css`; Portfolio stat card in Company Search made clickable to jump to connections section.

---

### #39 — Supply Chain Overview: colori paesi — connotazione politica indesiderata ✅ RESOLVED

**Area:** Supply Chain → Overview (country breakdown) — `js/tabs/overview.js`, `css/components.css`
**Type:** UX / Content
**Priority:** Medium

I colori usati per il breakdown per paese (rosso per Cina e Russia, blu per paesi occidentali) hanno una connotazione politica non intenzionale.

> "non discriminerei la Cina e la Russia con questi colori rosso comunisti [...] colore unico, o differenziare per continente"

**Proposta:** Usare una palette neutrale basata su continenti (Europa, Asia, Americhe, ecc.) senza associazioni cromatiche politiche. Oppure usare un colore unico con intensità proporzionale al numero di entità.

**Status:** ✓ Resolved — 2026-03-28 — Replaced political coloring with continent palette (Europe/Americas/Asia-Pacific/MENA/Africa) in `js/tabs/overview.js`.

---

### #40 — Sidebar/panel: posizionare a sinistra invece che a destra ✅ RESOLVED

**Area:** Global — tutti i panel laterali (`js/detail-sidebar.js`, `js/tabs/map.js`, `js/tabs/graph.js`, `js/tabs/edfbrowse.js`)
**Type:** UX
**Priority:** Medium

**Status:** ✓ Resolved — 2026-03-28 — All panels moved to left. Inline panels (`#map-panel`, `#edfmap-panel`, `#graph-detail`, `#mx-detail`) reordered in DOM before main content and changed `border-left` → `border-right`. Fixed overlay sidebars (`.entity-sidebar`, `.ec-part-sidebar`) moved to left with `translateX(-100%)` slide animation and `border-right`. Overlay wrappers fixed to start at `calc(nav-h + tab-h + subtab-h)` to stop covering navbar. Width harmonized: `ec-part-sidebar` changed from `--sl-w-sm` to `--sl-w-inline` (450px) across all panels.

Tutti i panel laterali si aprono a destra. Laura (e poi confermato da tutti) preferisce sinistra per ragioni di UX consolidate: Google Maps ha il panel a sinistra, la lettura occidentale va da sinistra a destra, il braccio destro rimane libero per interagire con la mappa/grafo.

> "il pannello about dismert lo vorrei a sinistra e non a destra [...] Google Maps ce l'ha a sinistra [...] sto sulla destra per muovere la mappa"

**Proposta:** Spostare tutti i panel laterali a sinistra. Valutare se aggiungere un toggle L/R per user preference (opzionale). In alternativa: testare con due utenti prima di decidere definitivamente.

**Files:** `css/components.css`, `js/detail-sidebar.js`, `css/map.css`, `css/graph.css`, `css/edfbrowse.css`

---

### #41 — Supply Chain Map light mode: colori slavati, poco contrasto ✅ RESOLVED

**Area:** Supply Chain → Map — `css/map.css`, `css/base.css` (`[data-theme="light"]`)
**Type:** UX
**Priority:** High

In light mode la mappa Supply Chain ha colori "slavati" (poco contrastati). I punti sui paesi e gli archi si distinguono a malapena dallo sfondo. La dark mode regge molto meglio.

> "la mappa nella versione chiara non regge il confronto [...] i colori non mi piacciono [...] poco contrasto, si distinguono male"

**Cross-ref:** #08 (Davide, archi troppo chiari anche in dark)

**Proposta:** Rivedere `--map-bg`, `--map-land`, `--map-arc-*` nella sezione light di `css/base.css`. Portare i colori mappa in light mode ad avere almeno lo stesso livello di contrasto della dark mode.

**Status:** ✓ Resolved — 2026-03-28 — Added `--map-bg`, `--map-land`, `--map-data`, `--map-selected` light overrides + new `--map-arc-color` token read by SC Map JS at draw time via `getComputedStyle`.

---

### #42 — Supply Chain Map: interazione semplificata (solo paesi sorgente, click rivela destinazioni) ✅ RESOLVED

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX / Feature
**Priority:** Medium

Laura propone un modello di interazione più semplice e direzionale: inizialmente si vedono solo i punti dei paesi da cui **partono** investimenti; quando si clicca un paese, si illuminano i paesi destinazione e tutti gli altri punti spariscono.

> "i punti colorati sulla mappa siano unicamente quelli dei paesi da cui partono gli investimenti e una volta cliccato il punto si illuminano i paesi in cui arriva l'investimento [...] quelli che non sono collegati a quel punto spariscono"

**Cross-ref:** #09 (Davide propone toggle flowing-in / flowing-out — variante dello stesso problema)

**Note:** Le due proposte (Davide e Laura) sono compatibili. Una possibile sintesi: default = mostra solo paesi sorgente; click paese = mostra archi in uscita + evidenzia destinazioni; bottone toggle "Mostra flussi in entrata" per invertire la vista.

**Status:** ✓ Resolved — 2026-03-28 — Arcs hidden by default (`showArcs: false`, arc layer `display:none` on init, checkbox unchecked). On country click, arc layer shown with only outbound arcs (`d.src === iso`). On deselect/close, arc layer hides again unless global toggle is checked. Mirrors EDF Map interaction pattern.

---

### #43 — Supply Chain Map: click area vuota per deselezionare il paese ✅ RESOLVED

**Area:** Supply Chain → Map — `js/tabs/map.js`
**Type:** UX
**Priority:** Low

Per deselezionare un paese bisogna cliccare la X nella sidebar. L'utente si aspetta di poter cliccare su un'area vuota della mappa per uscire dalla selezione.

> "magari sarebbe meglio cliccare sulla mappa in un posto casuale per uscire dal paese, non dover schiacciare la x della sidebar"

**Fix:** Aggiungere un listener `click` sul background SVG della mappa che chiama la funzione di deselect/clear.

**Files:** `js/tabs/map.js`

**Status:** ✓ Resolved — 2026-03-28 — SVG click handler added in `js/tabs/map.js` using `classList.contains` check.

---

### #44 — Graph Projection: la gravità non lascia i nodi dove li trascina l'utente ✅ RESOLVED

**Area:** Supply Chain → Graph (Projection) — `js/tabs/graph.js`
**Type:** UX / Bug
**Priority:** Medium

Dopo aver trascinato un nodo manualmente, la simulazione fisica lo riporta indietro. L'utente vorrebbe poter "pinnare" un nodo in una posizione per facilitare la lettura, come avviene nei software di network analysis professionali (Gephi, ecc.).

> "quando in supply chain, graph, projection, tu sposti un quadrato nello schermo, il quadrato deve rimanere fermo lì [...] non ci deve essere la gravità"

**Proposta:** Aggiungere `pin` on drag-end: impostare `node.fx = node.x; node.fy = node.y` alla fine del drag per fissare il nodo. Doppio-click per liberarlo. Verificare implementazione drag in D3 force simulation.

**Files:** `js/tabs/graph.js`

**Status:** ✓ Resolved — 2026-03-28 — Drag `on('end')` handler now sets `d.fx = d.x; d.fy = d.y` instead of `d.fx = null; d.fy = null` across all three views (network, bipartite, projection). Nodes stay pinned at drop position; simulation cools down normally.

---

### #45 — Graph: barra filtri confusa, nessun separatore tra tipo vista e tipo settore ✅ RESOLVED

**Area:** Supply Chain → Graph — `js/tabs/graph.js`, `css/graph.css`
**Type:** UX
**Priority:** Medium

I controlli nella toolbar del Graph (Network / Bipartite / Projection / All / Startup / Defense / Mining / Tech) sembrano tutti dello stesso tipo ma sono due categorie diverse: modalità di visualizzazione e filtri settoriali. Un nuovo utente non percepisce la differenza.

> "non si capisce più la differenza tra network, bipartite projection e startup, defense, mining, tech, all [...] sembrano sei cose uguali [...] basterebbe magari una lineetta che separa"

**Proposta:** Aggiungere un separatore visivo (divisore + label "Vista" / "Settore") nella toolbar. Oppure due gruppi di pulsanti distinti con label di gruppo.

**Files:** `css/graph.css`, `index.html`

**Status:** ✓ Resolved — 2026-03-28 — Added `<span class="ctrl-group-lbl">` labels ("View" / "Sector") and `.ctrl-sep` divider in `index.html`; `.ctrl-group-lbl` utility added to `css/base.css`.

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

### #47 — EDF Calls Search: rimuovere label "pattern:" dai risultati ✅ RESOLVED

**Area:** EDF → Calls Search — `js/tabs/eucalls.js`
**Type:** Bug / Content
**Priority:** Low

Nei risultati di ricerca di EDF Calls, il nome del progetto è preceduto da "pattern:" che è chiaramente un placeholder/label tecnica rimasta visibile.

> "togliamo pattern da IDF call search [...] toglierei pattern dall'inizio del nome del progetto perché non si capisce a cosa si riferisce"

**Fix:** Cercare nel template HTML di `eucalls.js` dove viene renderizzato il campo `pattern` e rimuovere il prefisso testuale.

**Files:** `js/tabs/eucalls.js`

**Status:** ✓ Resolved — 2026-03-28 — Removed `"Pattern: "` prefix from `ec-patternTitle` in `js/tabs/eucalls.js` line 836.

---

### #48 — Supply Chain Matrix: rimuovere o semplificare significativamente ✅ RESOLVED

**Area:** Supply Chain → Matrix — `js/tabs/matrix.js`
**Type:** Feature (decision)
**Priority:** Low

**Cross-ref:** #15 (Davide, stesso punto)

Laura: "che cazzo è? Non si capisce. Sono le stesse informazioni di prima in un'altra forma."

**Status:** ✓ Resolved — 2026-03-28 — Matrix removed. See #15.

---

### #49 — EDF Map: click area vuota per deselezionare il paese ✅ RESOLVED

**Area:** EDF → Map — `js/tabs/edfmap.js`
**Type:** UX
**Priority:** Low

Stesso problema di #43 (Supply Chain Map). Per deselezionare un paese nella EDF Map bisogna usare la X della sidebar. Laura si aspetta di poter cliccare sulla mappa vuota.

**Cross-ref:** #43

**Fix:** Stesso pattern di fix: listener `click` sul background SVG per chiamare il deselect.

**Files:** `js/tabs/edfmap.js`

**Status:** ✓ Resolved — 2026-03-28 — SVG click handler added in `js/tabs/edfmap.js`, mirroring the SC Map fix.

---

### #50 — Company Search: scheda fondo — numero portfolio non spiega quali aziende ✅ RESOLVED

**Area:** Company Search — `js/tabs/companysearch.js`
**Type:** UX
**Priority:** Medium

**Status:** ✓ Resolved — already implemented. Portfolio (and Investors) stat cards are `.cs-stat--link` with `cursor:pointer`, accent hover border, and a `scrollIntoView` click handler targeting `#cs-rel-card` (the Connections section). Implementation confirmed in `js/tabs/companysearch.js` lines 260–270 and `css/companysearch.css`.

Sulla scheda di un investitore/fondo, il campo "Portfolio: 1" non è cliccabile né espande per mostrare quale/quali aziende sono in portfolio. L'utente deve scorrere fino alla sezione "Connections" per trovarlo, e il collegamento non è ovvio.

> "uno portfolio e già direttamente direi qual è l'azienda [...] non è chiara la conseguenza"

**Proposta:** Rendere il numero di portfolio nella Key Facts section cliccabile (o inline-expandable) per mostrare la lista delle aziende. In alternativa, spostare la lista portfolio direttamente nella sezione Key Facts invece che in fondo alla pagina.

**Files:** `js/tabs/companysearch.js`

---

## Issue aggiuntive (seconda analisi dei transcript)

Le seguenti issue sono emerse da una rilettura approfondita dei transcript. Attribuite al rispettivo utente.

---


### #52 — [Davide] Data Issues tab: armonizzare dimensione font con le altre pagine ✅ RESOLVED

**Area:** About → Data Issues — `js/tabs/knownissues.js`, `css/about.css`
**Type:** UX
**Priority:** Low

Davide ha notato che il font della tab Data Issues ha dimensioni diverse rispetto alle altre pagine. Va allineato al sistema tipografico standard.

> "si armonizzerai solo la grandezza del fondo con le altre pagine"

**Fix:** Verificare che `#tab-knownissues` usi i token `--fs-*` standard e non un override locale. Controllare il rendering del Markdown da `marked` — potrebbe applicare stili H1/H2 del browser invece dei token CSS.

**Files:** `css/about.css`, `js/tabs/knownissues.js`

**Status:** ✓ Resolved — 2026-03-28 — `.ki-body p` font-size reduced from `--fs-lg` to `--fs-body` in `css/base.css`.

---


### #55 — [Andrea] Graph: nessun auto-zoom dopo cambio filtro settore ✅ RESOLVED

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** UX / Bug
**Priority:** Medium

Dopo aver applicato un filtro settore (es. Startup) o cambiato modalità, il grafo non si ridimensiona automaticamente per mostrare i nodi visibili. L'utente deve zoomare manualmente per trovare i nodi.

> "poi si dovrebbe auto zoomare da solo"

**Fix:** Dopo ogni ridisegno del grafo (cambio filtro, cambio modalità), chiamare una funzione di fit/zoom automatico che adatta la viewport ai nodi visibili. In D3 force: usare `zoom.transform` con `fitExtent` dopo la stabilizzazione della simulazione.

**Files:** `js/tabs/graph.js`

**Status:** ✓ Resolved — 2026-03-28 — Added `svgFit(nodes)` helper that always re-reads live `clientWidth`/`clientHeight` from `#graph-svg`. All three views now use `svgFit` in simulation `on('end')` callbacks (animated re-center). Initial bounding-box fit wrapped in `requestAnimationFrame` so the SVG has its final dimensions before the transform is applied.

---

### #56 — [Andrea] Graph Bipartite: modalità difficile da capire senza contesto ✅ RESOLVED

**Area:** Supply Chain → Graph (Bipartite mode) — `js/tabs/graph.js`
**Type:** UX / Content
**Priority:** Medium

**Status:** ✓ Resolved — already implemented. `setGraphView()` calls `closeGraphDetail()` → `showGraphHelp()` on every view switch, which always opens the detail panel with "How to explore" content (including the Bipartite description). The panel resets to help on Network/Bipartite/Projection switches regardless of prior state.

La modalità Bipartite è quella meno intuitiva delle tre. Il principio (due colonne: investitori a sinistra, aziende a destra, archi = investimento) non è immediatamente chiaro dal solo titolo.

> "bipartite: difficile da capire come si usa [...] lo dividi in due, quindi fai un matching praticamente"

**Proposta:** Aggiungere nel panel "How to explore" (quando Bipartite è attivo) una descrizione specifica: "Vista bipartita: investitori a sinistra, aziende a destra. Gli archi mostrano chi ha investito in cosa." Opzionalmente, aggiungere label visive sulle due colonne.

**Files:** `js/tabs/graph.js`, eventualmente `index.html`

---

### #57 — [Andrea] Graph: panel "How to explore" a destra, controlli a sinistra/basso — incoerenza spaziale ✅ RESOLVED

**Area:** Supply Chain → Graph — `js/tabs/graph.js`, layout
**Type:** UX
**Priority:** Medium

Il panel "How to explore" (che spiega le modalità e come usarle) appare a destra dello schermo, ma i pulsanti di controllo effettivi (Network / Bipartite / Projection / settori) sono posizionati in basso o in un'altra zona. L'utente legge le istruzioni a destra, poi deve cercare i controlli altrove.

> "me lo spiega qua, però poi devo andare a cercarle qui sotto nella pagina [...] mi aspetto di trovare dei bottoni sulla destra e non di dover tornare sulla sinistra in basso"

**Proposta:** Spostare il panel "How to explore" nello stesso lato dei controlli, oppure spostare i controlli vicino al panel. Istruzioni e controlli che descrivono devono essere spazialmente adiacenti.

**Cross-ref:** #40 (sidebar a sinistra), #45 (separatore tra tipo vista e settore)

**Status:** ✓ Resolved — 2026-03-28 — "How to explore" panel moved to left (#40). Sector + Search filters moved into `#graph-filter-float` floating box anchored top-right of `#graph-pane`. View controls remain in `#graph-controls` bottom-left. Companies/Investors toggles hidden (`display:none`). Legend moved to bottom-right (fit-content). Result: controls spatially cluster in two logical zones (filters top-right, view mode bottom-left) with the help panel on the left.

---


### #60 — Graph: clicking a node does not update URL routing ✅ RESOLVED

**Area:** Supply Chain → Graph — `js/tabs/graph.js`
**Type:** Bug
**Priority:** Medium

Clicking a node in the graph opens the detail panel but does not update the URL (`?entity=...` or similar). Navigating via the sidepanel works correctly. This means direct links to a graph + selected node are not shareable, and the Export button cannot reflect the selected node unless the user arrived via the sidebar.

> Reported during Export-for-AI session 2026-03-28.

**Files:** `js/tabs/graph.js`, `js/url.js`

**Status:** ✓ Resolved — 2026-03-28 — `graphShowPanel()` now calls `setParams()` with `entity=<id>&entity-name=<slug>` after opening the panel. `closeGraphDetail()` removes both params. `selectGraphEntity(id)` exported from `graph.js`; `restoreFromUrl()` case `'graph'` calls it when `p.entity` is present. Import `getParams`/`setParams` added to `graph.js`.
