# Japi User Test — Issues

_Extracted from live think-aloud session. User navigated index.html commenting out loud. Session recorded and transcribed._
_Date: 2026-03-22_

---

## Rules for AI assistants

Apply the same rules as `issues.md`: resolved issues go to `CHANGELOG.md`, permanent data gaps go to `known-issues.md`. Cross-reference with `issues.md` numbering where overlap exists.

---

## #1 — Home: nessun CTA visibile, navigazione non scoperta

**Section:** Intro
**Type:** UX / Navigation
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Presenti CTA espliciti ("→ Explore Supply Chain", "→ European Defence Fund") e link inline nel testo ("Supply Chain →", "European Defence Fund →", "Tools →"). Screenshot: `01-intro-top.png`.

L'utente ha letto l'intera home page senza capire dove andare. Si aspettava un bottone o un link visibile per "iniziare". La barra di navigazione superiore è stata inizialmente ignorata perché visivamente assomigliava alla barra del browser.

> "la prima cosa di cui sento la mancanza è qualcosa di cui partire da qui, mi aspettavo di trovare un bottone per iniziare o andare da qualche parte"
> "mi sono accorto dopo che qua sopra c'è una barra di reazione che però mi sembrava un po' quella del mio browser quindi subito non l'ho molto cagata"

**Proposta:** Aggiungere un CTA esplicito nel body dell'intro (es. "Esplora la Supply Chain →") che porti direttamente alla prima sezione. Distinguere visivamente la nav bar dal browser chrome.

---

## #2 — Home: testo intro senza link inline

**Section:** Intro
**Type:** UX
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** "Supply Chain →", "European Defence Fund →", "Tools →" sono elementi clickable (cursor=pointer) nel body dell'intro.

Anche dopo aver scoperto la nav bar, l'utente si aspetta che le sezioni menzionate nel testo (es. "Supply Chain") siano cliccabili direttamente dal corpo dell'intro.

> "magari un link nel testo non soltanto nella barra di analisi, da partire da qua così posso entrare in supply chain senza cercarlo qua sopra"

**Proposta:** Inserire link inline nel testo dell'intro che portino alle sezioni corrispondenti (Supply Chain, EDF, ecc.).

---

## #3 — Home: intro troppo povera, contenuto di About assente

**Section:** Intro / About
**Type:** Content / UX
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Aggiunta sezione "about this research" con descrizione dei settori (Defence, Mining, Tech) e bottone "→ Full context and methodology in About". Mining è ora contestualizzato.

L'utente ha trovato l'intro molto scarna. Il contesto che cercava era disponibile nella pagina About, ma non lo sapeva. La proposta emersa spontaneamente è di portare il contenuto di About dentro l'intro, o quantomeno collegarlo direttamente.

> "È molto povera qua la intro... l'about potrebbe diventare la intro"
> "Ma perché tutta questa parte di about non la metti qua sotto? Sì, questo è un fatto di user experience"
> "sì perché alla fine ti dà ancora più contesto e dopodiché uno continua e dice ok ne so abbastanza e io cerco qua dentro"

**Proposta:** Espandere il testo dell'intro con un riassunto del contesto della ricerca (cos'è il progetto, chi mappa, perché), o aggiungere un accordion/sezione "Leggi di più" che esponga il contenuto di About senza obbligare a navigare via.

---

## #4 — Supply Chain Overview: tile "Relationships" non spiegata

**Section:** Supply Chain > Overview
**Type:** UX / Content
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Verificato via JS: nessuna tile aveva `data-tooltip`. Screenshot: `02-sc-overview.png`.
**Fix 2026-03-22:** `overview.js` ora importa `GLOSSARY` da `glossary.js` e applica `data-tooltip` inline su ogni `.lbl` delle stat tile che ha un termine corrispondente: Companies, Investors, Relationships, Lead inv., Mining, Defence, Tech, Startup.

L'utente non ha capito cosa misura il numero di "relationships". Ha provato a cercarne la definizione nell'intro (assente), poi ha proposto tooltip o un glossario.

> "298 relationships, immagino sia tra l'azienda e la difesa? Non c'è scritto. Andrebbe fatto una spiegazione magari un tooltip con l'ottica ferma sopra — cosa sono le relationship — o un tooltip sulle tile o addirittura una forma di glossario"
> "un bel glossario ci starebbe bene"

**Proposta:** Aggiungere tooltip `title` o popover Bootstrap su ogni stat tile dell'Overview, con una riga di spiegazione (es. "Relationships: legami di investimento tra investor e company"). In alternativa, un glossario nella tab About o in una modale accessibile da Overview.

---

## #5 — Supply Chain Overview: settore "Mining" non contestualizzato

**Section:** Supply Chain > Overview (sector breakdown)
**Type:** Content / UX
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Il settore Mining è ora spiegato nell'intro: "Extraction of critical raw materials for defence: semiconductors, rare earths, strategic metals". Contestualizzato anche nella sezione "about this research" dell'intro.

L'utente ha espresso sorpresa nel trovare "Mining" tra i settori della difesa. Non era ovvio che si trattasse di estrazione di materie prime per la filiera della difesa. La spiegazione era disponibile solo in About.

> "in cosa sarebbero minare quelli che estraggono le materie prime... non l'avrei collegato... Quindi l'estrazione di materie prime sarebbe per la difesa... Una larga spiegazione di tutto questo in realtà è in quella pagina About"

**Proposta:** Aggiungere una riga descrittiva sotto ogni settore nel breakdown, o un glossario dei settori. Collegato a #4 (stesso glossario).

---

## #6 — Supply Chain Map: entità selezionata non evidenziata nella sidebar

**Section:** Supply Chain > Map
**Type:** UX / Bug
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato. Cliccando su un nodo paese (es. MD), il testo in alto a sinistra aggiorna il nome del paese selezionato, ma la sidebar non porta visivamente il focus sull'entità cliccata. Il pannello mostra i dati ma non c'è highlight o scroll automatico verso di esso. Screenshot: `03-map-entity-filter.png`.
**Fix 2026-03-22 (session 2):** Implementata sidebar drill-down analoga a EDF Map: cliccando su company/investor nella sidebar di un paese, il pannello si sostituisce con dettaglio entità (investors per le company, portfolio per gli investor) + pulsante "← Back" che ripristina la vista paese. Separato: filter bar mostrava "Filtering: [x Clear]" di default per cascading CSS — fixato chiamando `applyMapFilter()` a fine `drawMap()`.

Dopo aver cliccato su un nodo (es. "MD"), l'utente riusciva a vedere la selezione solo nel label in alto a sinistra, non nella sidebar. Si aspettava che la sidebar mostrasse il dato dell'entità selezionata in modo immediato e visibile.

> "qua non mi rimane illuminato, lo vedo solo qua in alto a sinistra, ma non la vedi nella sidebar, che è il luogo naturale. Sarebbe più utile lì."

**Proposta:** Verificare che il click su un nodo mappa popoli correttamente la sidebar e porti il focus dell'utente lì (es. scroll automatico, highlight del pannello).

---

## #7 — Supply Chain Graph: impossibile deselezionare un nodo

**Section:** Supply Chain > Graph
**Type:** UX / Bug
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato risolto. Cliccando su un nodo già selezionato il grafo si resetta e la sidebar scompare. Screenshot: `04-graph-default.png`.

L'utente non riusciva a capire come rimuovere la selezione di un nodo. Chiudere la sidebar non deselezionava il nodo nel grafo.

> "io qua non sto capendo come tolgo la mia selezione. Anche se chiudo questa, la selezione rimane."

**Proposta:** Click sul nodo già selezionato = deseleziona. In alternativa, aggiungere un pulsante "Clear selection" o deselezionare automaticamente alla chiusura della sidebar.

---

## #8 — Supply Chain Graph: modalità grafo (Network / Bipartite / Projection) non spiegate

**Section:** Supply Chain > Graph
**Type:** UX / Content
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato risolto. I tre pulsanti mostrano ora tooltip al hover: "Network: all nodes and links", "Bipartite: investors left, companies right", "Projection: companies linked through shared investors". Screenshot: `04-graph-default.png`.

I tre pulsanti per scegliere il tipo di grafo non avevano significato per l'utente. Solo dopo una spiegazione verbale ha capito la differenza, in particolare apprezzando il "Projection" (chi lavora con chi, tramite un soggetto comune).

> "Network, mi farà dire projection, queste tre cose qua per me non hanno significato. Vanno spiegate, questi sono i tre tipi di grafi."
> "il projection è quello più figo perché tipo io sono stato working capital, tu sei stato working capital, quindi io e te siamo connessi"

**Proposta:** Aggiungere tooltip o una riga di descrizione sotto i pulsanti di modalità. Per "Projection" in particolare: "Connette entità che condividono un investor comune — mostra chi lavora con chi."

---

## #9 — Supply Chain Graph: barra filtri senza sfondo, si confonde col contenuto

**Section:** Supply Chain > Graph
**Type:** UI / Visual
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato risolto. La toolbar del grafo ha ora `background: var(--bg)` o equivalente, ben distinta dal canvas del grafo sottostante. Screenshot: `04-graph-default.png`.

La barra dei filtri del grafo non ha uno sfondo distinto e si sovrappone visivamente al grafo stesso, rendendo difficile la lettura.

> "Mettici uno sfondo dietro questa barra, perché se no non..."

**Proposta:** Aggiungere `background: var(--bg)` o simile alla barra filtri del graph tab, con eventuale `backdrop-filter` se necessario.

---

## #10 — Supply Chain Companies sidebar: allineamento rotto senza badge "lead"

**Section:** Supply Chain > Companies > sidebar (sezione investors)
**Type:** Bug / CSS
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato risolto. Verificato via JS: gli `<li>` della lista investors in sidebar hanno `justify-content: flex-start`. I nomi degli investor si allineano a sinistra indipendentemente dalla presenza del badge LEAD. Screenshot: `10-sidebar-investors-bottom.png`.

Nella sidebar di dettaglio di una company, nella lista degli investor, quando un investor non ha il badge "lead" la label del nome scivola tutta a destra per effetto del `justify-content: space-between` del flexbox.

> "sai il flex space between che quando ti scompare questo ti fa andare la label da tutta destra, invece dovrebbe stare al centro"
> "In questa riga non c'è la capsulina lead e quindi lui te la sposta tutta destra."

**Proposta:** Sostituire `justify-content: space-between` con `gap` fisso, oppure aggiungere un elemento placeholder quando il badge lead è assente, per mantenere l'allineamento.

---

## #11 — Legend bar: non vista, sepolta tra barre di navigazione

**Section:** Globale (tutte le tab con legenda)
**Type:** UX / Layout
**Status:** Resolved — 2026-03-22 (last commit: legend moved to footer bar)

**Test 2026-03-22 (Playwright):** Confermato risolto — legenda visibile in footer bar, distinta dalla nav superiore.

L'utente non ha mai notato la barra della legenda durante tutta la navigazione, perché visivamente identica alle altre barre interattive. Ha proposto di spostarla in fondo (footer).

> "fino adesso non l'ho praticamente mai calcolata perché le barre qua sopra sono tutte interattive tranne questa, quindi gli darei un altro posto, piuttosto lo metterei in fondo, tipo footer"
> "dappertutto se posso dire mettendoci leggenda... essendo in mezzo a tutte le barre di navigazione secondo me finisce che la ignori"

**Risolto:** Legenda spostata in footer bar nel commit [2026-03-22].

---

## #12 — EDF: nessun testo introduttivo nella sezione

**Section:** European Defence Fund > Overview
**Type:** Content / UX
**Status:** Resolved — 2026-03-22

**Fix 2026-03-22:** Aggiunto header `.ov-header` in `tab-edfoverview` con `intro-prompt` (`$ man-in-the-loop --edf`), `ov-title` ("European Defence Fund") e `intro-desc` con spiegazione del fondo e glossary tooltip su "EDF". Stesso pattern del Supply Chain Overview.

L'utente è entrato nella sezione EDF senza trovare nessuna spiegazione di cosa sia il fondo, cosa significhino le statistiche, chi sono i beneficiari. Ha dovuto ricevere la spiegazione verbalmente.

> "ok adesso siamo su european defence fund questo va spiegato non c'è ancora spiegato"

**Proposta:** Aggiungere un paragrafo introduttivo nella tab EDF Overview: cos'è il fondo, periodo (2021–2027), budget totale, cosa significa "partecipazione" vs "coordinamento".

---

## #13 — EDF Map: vista iniziale non centrata sull'Europa

**Section:** European Defence Fund > Map
**Type:** Bug
**Status:** Resolved — 2026-03-22

**Fix 2026-03-22:** Rimossi i valori hardcoded `translate(-2926, -261).scale(3.647)` sia all'init che nel reset zoom. La mappa ora parte da `d3.zoomIdentity` (tx:0 ty:0 k:1) — la proiezione `geoNaturalEarth1` centrata su `[W/2-100, H/2+50]` è già calibrata per il viewport, nessun transform aggiuntivo necessario.

Al caricamento, la mappa EDF non è centrata sull'Europa dove si trovano i nodi. L'utente si è ritrovato a guardare la Russia/area vuota.

> "Qua la mappa non mi si è centrata dove ci sono i nodi. Sto guardando la Russia, credo, in questo momento. Sì, sì, questo è un bug."

**Proposta:** Verificare i parametri di `translate` e `scale` dell'initial view in `edfmap.js`. Il README documenta `translate(-2926, -261) scale(3.647)` come calibrazione target — verificare che sia applicata correttamente rispetto alle dimensioni effettive del contenitore SVG.

---

## #14 — EDF Map: intensità degli archi non visivamente distinta

**Section:** European Defence Fund > Map
**Type:** Feature / UX
**Status:** Open — non implementato, confermato 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato non implementato. Tutti i 351 elementi `.edfmap-arc` non hanno attributi `opacity`, `stroke`, o `stroke-width` inline né via `style`. La variazione di opacità in base al numero di progetti condivisi (documentata nel README: "arc opacity scales with co-project count") non è presente nel DOM corrente.

Gli archi di connessione tra paesi hanno tutti lo stesso peso visivo. L'utente ha proposto di mostrare l'intensità della collaborazione (quanti progetti in comune) tramite spessore o opacità variabile — una sorta di heatmap degli archi.

> "non c'è una differenza di intensità... è possibile ipotizzare che i soggetti italiani abbiano partnership con più con aziende francesi... tipo heatmap di quel collegamento... valorizzare il collegamento in base all'intensità"
> "l'arco andrebbe reso visibile se è più intenso con la Francia e meno intenso con la Spagna"

**Proposta:** Implementare la variazione di `opacity` o `stroke-width` sugli archi in base al numero di progetti condivisi tra le due nazioni, con un range percettibile (es. opacity 0.15–0.8).

---

## #15 — EDF Map: sidebar mostra solo le org del paese selezionato, non spiega le connessioni

**Section:** European Defence Fund > Map
**Type:** UX / Content
**Status:** Open — confermato 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato. Cliccando su Italia, la sidebar mostra l'elenco delle organizzazioni italiane ma non esplicita con quali paesi sono in connessione né quanti progetti condividono. Gli archi restano visibili ma non hanno tooltips. Screenshot: `15-edf-map-italy-sidebar.png`.

Dopo aver cliccato su un paese (Italia), l'utente ha visto nella sidebar solo le aziende italiane, ma gli archi mostravano connessioni con altri paesi. Non era chiaro cosa rappresentassero quelle connessioni.

> "non mi è chiaro perché c'è la relazione con gli altri paesi, dice che a destra vedo soltanto le compagnie italiane"
> "va spiegato, praticamente significa quali sono gli altri paesi coinvolti nello stesso progetto"

**Proposta:** Aggiungere nella sidebar del paese selezionato una sezione "Partner countries" che elenca i paesi con cui condivide più progetti, con conteggio. Aggiungere un tooltip sull'arco che spieghi cosa significa ("N progetti in comune").

---

## #16 — EDF: testo con font "code" sotto il titolo illeggibile

**Section:** European Defence Fund (sezione, tab non specificata)
**Type:** Bug / UI
**Status:** Resolved — 2026-03-22 (last commit: EDF calls readability)

**Test 2026-03-22 (Playwright):** Confermato risolto — nessun testo in font monospace con colore errato nelle tab EDF visitate.

Un testo di colore scuro con font monospace (code) appariva sotto un titolo EDF, risultando illeggibile.

> "qui sotto il titolo c'è un testo nero che ha cambiato il font code. Ok, sì, no, non si legge proprio."

**Risolto:** Corretto nel commit [2026-03-22] — EDF calls readability.

---

## #17 — EDF Calls Search: bug nella comparison view

**Section:** European Defence Fund > EDF Calls Search
**Type:** Bug
**Status:** Open — da verificare

**Test 2026-03-22 (Playwright):** Non verificato in dettaglio. La comparison view richiede la selezione di due call distinti anni — test non completato per mancanza di dati multi-anno nel flusso di test. Da rivedere manualmente.

L'utente e il conduttore hanno notato un bug attivo nella "comparison view" della ricerca EDF Calls.

> "qui c'è un bug in comparison view, va fixato"

**Proposta:** Investigare e fixare il comportamento della comparison view in `eucalls.js`.

---

## #18 — EDF Calls Search: select "topic identifier" dovrebbe essere aperta di default

**Section:** European Defence Fund > EDF Calls Search
**Type:** UX
**Status:** Open — confermato 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato. Al caricamento della tab la select dei topic identifier è chiusa. L'utente che non conosce già i codici non ha visibilità sulle opzioni disponibili prima di interagire. Screenshot: `16-eucalls-select-closed.png`.

L'utente non sapeva da dove partire nel campo di ricerca. La select dei topic identifier era chiusa e non segnalava la presenza di opzioni precaricate. Aprirla di default renderebbe immediatamente visibile all'utente cosa può cercare.

> "come esperienza utente qua la select di topic identifier dovrebbe essere aperta di default perché così l'utente vede direttamente che già ci sono delle cose che può cercare"

**Proposta:** Aprire la select (dropdown) dei topic identifier di default al caricamento della tab, o mostrare un campione delle opzioni disponibili prima dell'interazione.

---

## #19 — EDF Calls Search: ricerca limitata a topic ID e titolo, non copre description o partner

**Section:** European Defence Fund > EDF Calls Search
**Type:** Feature
**Status:** Resolved — 2026-03-22 (session 1)

**Fix 2026-03-22:** Risolto in session 1 con EDF-C-C: aggiunto campo `desc` (600 char dalla descrizione) in `edfCallsList`; `showDropFiltered` esteso per matchare anche su `c.desc`. La ricerca per keyword trova ora risultati anche nelle descrizioni dei call.

L'utente ha provato a cercare per nome di arma/tecnologia (es. "drone", "helicopter") e non ha trovato risultati, perché la ricerca copre solo il topic identifier e il titolo del call. Ha proposto di estenderla alla description del progetto e ai nomi dei partner.

> "la search viene fatta su due campi, una è sul topic identifier, l'altra è sul titolo. Forse si potrebbe inserire anche la description del progetto per essere più... Sì, forse anche per partner si potrebbe fare."

**Proposta:** Estendere la funzione di ricerca in `eucalls.js` per includere la description del progetto e/o i nomi dei partner/coordinatori.

---

## #20 — EDF Calls Search: accordion degli anni confuso, motivo non chiaro

**Section:** European Defence Fund > EDF Calls Search (risultati di ricerca)
**Type:** UX
**Status:** Open — confermato 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato. I risultati di ricerca mostrano le call raggruppate per anno in accordion. L'header mostra anno, numero progetti e partecipanti, ma l'espansione non aggiunge informazioni significativamente diverse. I tag accanto sono etichette non cliccabili. Screenshot: `19-eucalls-accordion-closed.png`, `20-eucalls-accordion-open.png`.

Nell'area dei risultati della ricerca, un elemento (es. "anno 2024, 2 progetti, 19 partecipanti") si apre e chiude come accordion, ma l'utente non capiva perché fosse espandibile né cosa aggiungesse. Si aspettava che fosse cliccabile per navigare ai dettagli.

> "questo non è cliccabile, è che si apre e si chiude l'accordo. Però allora ti chiedo, perché è espandibile? Non c'è motivo."
> "questi accanto all'accordion sono dei tag, non cliccabili"

**Proposta:** Valutare se l'accordion ha senso UX in questo contesto. Se il contenuto espanso non aggiunge informazioni rispetto all'header, rendere la riga statica. Altrimenti, rendere l'header cliccabile per navigare al dettaglio, non solo per espandere.

---

## #21 — EDF Beneficiaries: progetto in sidebar org non linkato al dettaglio progetto

**Section:** European Defence Fund > EDF Beneficiaries > sidebar org
**Type:** Feature / UX
**Status:** Open — confermato 2026-03-22

**Test 2026-03-22 (Playwright):** Confermato. Nella sidebar di un'organizzazione (es. Leonardo), i progetti elencati non sono cliccabili per navigare al dettaglio. È presente un link "EC Portal →" che apre il portale EU esterno, ma non c'è navigazione interna verso il dettaglio EDF Call Search equivalente.

Nella sidebar di dettaglio di un'organizzazione (es. Leonardo), la lista dei progetti in cui ha partecipato non è cliccabile. L'utente si aspettava di poter aprire il dettaglio del singolo progetto direttamente da lì.

> "vorresti poter cliccare su un progetto per vedere che cos'è"
> "forse qui ci potrebbe stare anche una qualche modale, o comunque un modo per accedere al dato di dettaglio del singolo progetto"
> "sarebbe praticamente la pagina che vedevo prima di EDF Call Search. Il dettaglio di quello, giusto?"

**Proposta:** Rendere cliccabili i progetti nella sidebar org di EDF Beneficiaries, aprendo una modale o navigando verso il dettaglio equivalente in EDF Calls Search.

---

## #22 — Data: Data Quality e Known Issues troppo sepolti nel menu

**Section:** Data > Data Quality / Known Issues
**Type:** Navigation / IA
**Status:** Resolved — 2026-03-22

**Test 2026-03-22 (Playwright):** Parzialmente indirizzato nel test iniziale. Poi risolto completamente.
**Fix 2026-03-22:** Gruppo "Data" rimosso dalla navbar. Known Issues, Data Quality, Wikidata Inspector spostati come sub-tab di About. Aggiunti due nuovi sub-tab: "Data" (link ai JSON scaricabili) e "Glossary" (termini del glossario). Intro area 03 aggiornata a "Data & About →".

L'utente ha notato alla fine della sessione che Data Quality e Known Issues sono dentro "Data", ma riguardano tutti i dati del progetto (Supply Chain, EDF, ecc.). Ha proposto di portarli a un livello di navigazione superiore — dentro About, o come voci di primo livello nel menu.

> "questi due non va alla fine a linkarli sempre nella home, piuttosto che averli dentro a tools, perché alla fine riguardano anche i dati che sono su supply chain european o no?"
> "Quindi tu dici data quality e non issues, metterli diciamo come primo livello nel menu. Sì, perché se fanno parte di tutto... dentro l'about, diciamo."
> "se no me ne accorgo solo alla fine, non va bene"

**Proposta:** Spostare Data Quality e Known Issues dentro About (come sezioni), o aggiungere link a queste pagine nell'intro/about così che l'utente le scopra all'inizio della navigazione, non alla fine.

---

_Total: 22 issues — 15 resolved, 7 open_

_Resolved: #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13, #16, #19, #22_
_Open: #14, #15, #17, #18, #20, #21_
_Needs verification: #17, #20_
