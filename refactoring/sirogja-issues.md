# Sirogja User Test — Issues

_Extracted from live think-aloud session. User navigated index.html commenting out loud. Session recorded and transcribed._
_Date: 2026-03-23_

---

## Rules for AI assistants

Apply the same rules as `issues.md`: resolved issues go to `CHANGELOG.md`, permanent data gaps go to `known-issues.md`. Cross-reference with `issues.md` and `japi-issues.md` numbering where overlap exists.

---

## #1 — EDF acronym non spiegato inline: l'utente deve cercarlo ogni volta

**Section:** European Defence Fund (globale)
**Type:** UX / Content
**Status:** Resolved (2026-03-24)

L'utente dichiara esplicitamente di dover andare a ricercare cosa significa "EDF" ogni volta che torna sull'app, nonostante abbia letto la documentazione. L'acronimo compare ovunque ma non ha una spiegazione persistente o un tooltip inline.

> "ogni volta ho anche letto tutto un libro ma ogni volta devo andare a riguardare cosa vuol dire in divato su European Defense Fund"

**Proposta:** Aggiungere un tooltip `data-tooltip="European Defence Fund"` su ogni occorrenza del termine "EDF" nelle label e nei titoli delle tab. Già implementato parzialmente in altri contesti (vedi japi #12) — estendere sistematicamente.

---

## #2 — EDF Map: sidebar scompare dopo click sulla X del chip paese, richiede ricarica pagina

**Section:** European Defence Fund > Map
**Type:** Bug
**Status:** Resolved (2026-03-24)

Dopo aver cliccato sulla X accanto al nome di un paese nel chip/filtro in alto a destra, la sidebar con la spiegazione del paese scompare. Cliccando di nuovo sul paese non ritorna. L'unico modo per ripristinare il comportamento è ricaricare la pagina.

> "se clicchi sulla X accanto a un paese in alto a destra vedi una spiegazione. C'è una spiegazione. No, non c'è più. Perché? Niente, devi ricaricare la pagina."
> "l'hai cliccato di nuovo. Niente."

**Proposta:** Verificare il handler della X sul chip paese in `edfmap.js`. Il click sulla X dovrebbe resettare la selezione del paese (come il pulsante Reset), non svuotare la sidebar senza ripristinare lo stato. Probabilmente la sidebar viene svuotata ma `selectedCountry` non viene ripristinato a `null` correttamente, quindi il secondo click sul paese non triggera il re-render.

---

## #3 — EDF Map: label della pagina mostra "IDF map" invece di "EDF map"

**Section:** European Defence Fund > Map
**Type:** Bug / Typo
**Status:** Not reproducible (2026-03-24) — Playwright DOM inspection found zero "IDF" occurrences; likely one-time browser/OS autocorrect artefact

Dopo aver ricaricato la pagina sulla tab EDF Map, l'utente nota che il titolo/label riporta "IDF map" invece di "EDF map".

> "C'è scritto IDF map. Ah, ok, IDF map."

**Proposta:** Cercare occorrenze di "IDF" (case-sensitive) in `edfmap.js`, `index.html` e nei CSS. Verificare che tutti i titoli, label e `document.title` usino "EDF" correttamente.

---

## #4 — EDF Map: input "Filter Organization" poco visibile

**Section:** European Defence Fund > Map
**Type:** UI / Visual
**Status:** Resolved (2026-03-24)

Il campo di testo per filtrare le organizzazioni nella sidebar del paese selezionato è scarsamente visibile. L'utente non lo nota immediatamente.

> "si vede poco"

**Proposta:** Aumentare il contrasto del campo input (bordo, colore placeholder, background) nel contesto della sidebar EDF Map. Valutare se aggiungere un'icona lente o un label più esplicito ("Filtra organizzazioni").

---

## #5 — EDF Map: pulsante Clear non azzera la sidebar (rimane sull'org precedentemente selezionata)

**Section:** European Defence Fund > Map
**Type:** Bug
**Status:** Resolved (2026-03-24)

Quando l'utente ha selezionato un'organizzazione (es. Leonardo) e poi clicca "Clear" sul filtro partner, la sidebar non torna alla vista paese. Rimane visualizzando i dati di Leonardo. Anche se il paese (Germania) è ancora selezionato, la sidebar mostra ancora dati dell'org.

> "quando tu hai cliccato clear la sidebar non si è azzerata per bene cioè tu eri su Leonardo hai cliccato clear... mi è rimasto dentro Leonardo"
> "tu praticamente non torni, quando clicchi clear su partner nella IDF map, non... Sì, resti sull'azienda che hai selezionato precedentemente"

**Proposta:** Il click su "Clear" nel filtro partner di EDF Map deve ripristinare la sidebar alla vista paese (lista organizzazioni del paese selezionato), non lasciare la vista org attiva. Verificare il handler Clear in `edfmap.js`.

---

## #6 — EDF Map: freccia verde ("frecciona") brutta, poco chiara, porta fuori dal sito

**Section:** European Defence Fund > Map
**Type:** UX / Visual
**Status:** Resolved (2026-03-24)

Una freccia verde di grandi dimensioni è presente nella vista EDF Map (probabilmente come link al portale EU per il progetto selezionato). L'utente non capisce cosa fa; il developer stesso la definisce "un errore" da sistemare. Il problema è che porta l'utente fuori dal sito in modo inaspettato, è troppo grande e visivamente invasiva.

> "questa frecciona verde è un errore ti porto la devo sistemare meglio io perché ti porta fuori dal sito in realtà"
> "la freccia è brutta è poco chiara è troppo grande"
> "d'altronde la frecciona te lo dice questo è un mondo fuori"

**Proposta:** Sostituire la freccia con un link testuale discreto ("→ EC Portal") o un'icona standard `external-link` di dimensioni ridotte. Aggiungere un'etichetta esplicita ("Apre il portale europeo") per segnalare che porta fuori dall'app. Considerare di aprire in `target="_blank"` con un'icona "external link" riconoscibile.

---

## #7 — EDF Map: click su paese mostra totale organizzazioni ma non totale budget

**Section:** European Defence Fund > Map
**Type:** Feature / UX
**Status:** Resolved (2026-03-24)

Quando si clicca su un paese nella EDF Map, la sidebar mostra il numero di organizzazioni (es. "organizzazioni 118") ma non il totale del budget EU contribution per quel paese.

> "se io clicco su Francia c'è un totale... organizzazioni 118, non c'è un totale budget che quindi va aggiunto"
> "Lo vedo da un'altra parte, ma qua no."

**Proposta:** Aggiungere nella sidebar paese di EDF Map un riepilogo del totale EU contribution aggregato per le organizzazioni di quel paese, analogamente a quanto già mostrato nell'EDF Overview per il ranking paesi.

---

## #8 — EDF Map: archi di connessione tra paesi non spiegati

**Section:** European Defence Fund > Map
**Type:** UX / Content
**Status:** Resolved (2026-03-24)

Gli archi che collegano i paesi nella EDF Map non hanno una spiegazione inline sufficiente. L'utente non capisce immediatamente cosa rappresentano (co-partecipazione a progetti).

> "le connessioni vanno spiegate meglio, si capiscono poco"
> "le connessioni dovrebbero essere un modo per mostrare come sono le connesse le nazioni sulla base dei progetti europei"

**Proposta:** Aggiungere un tooltip sull'arco al hover che mostri "N progetti in comune tra [paese A] e [paese B]". Aggiungere una riga nella legenda: "Archi = paesi che condividono almeno un progetto finanziato". Collegato a japi #15 (già risolto per sidebar, da estendere al tooltip arco).

---

## #9 — Data: budget Officina Stellare SPA discrepante tra app e portale EU

**Section:** European Defence Fund > Map (filtro Italia → Officina Stellare SPA)
**Type:** Data / Bug
**Status:** Moved to known-issues.md #6 (2026-03-24)

Filtrando per Italia e cercando "Officina Stellare SPA" nella EDF Map, il budget mostrato nell'app (2M circa) è diverso da quello sul portale europeo (EU contribution 1,5M). La discrepanza è verificabile confrontando le due fonti.

> "c'è una divergenza tra il danaro che risulta... i soldi che ha preso questa azienda sono diversi da quelli che sono scritti sul portale europeo"
> "Un milione e mezzo. Un milione e mezzo. Sul portale europeo... Sì, lì c'è chiaramente un errore nel dato. Da capire perché."

**Proposta:** Verificare la logica di aggregazione del budget per Officina Stellare SPA in `edf_calls.json`. La discrepanza potrebbe derivare da: (a) somma di EU contribution su più partecipazioni allo stesso progetto, (b) confusione tra budget totale della call e EU contribution del singolo partecipante, (c) errore nel dato sorgente. Documentare in `known-issues.md` se non risolvibile.

---

## #10 — Data: Istituto Superiore di Sanità — progetto "Resilience" con tutti i budget a zero

**Section:** European Defence Fund > Map (filtro Italia → ISS)
**Type:** Data
**Status:** Moved to known-issues.md #7 (2026-03-24)

L'Istituto Superiore di Sanità compare in un progetto denominato "Resilience" (data di partenza 2024) in cui tutti i valori di budget sono a zero. Potenziale errore nei dati sorgente dal portale EU, o ritardo nella pubblicazione dei dati per progetti avviati recentemente.

> "questo soggetto è l'Istituto Superiore di Sanità che compare in un progetto in cui tutti i budget sono a zero"
> "la fonte dati european portal è a zero bisogna vedere perché"
> "Devi vedere qual è la data di partenza... nel 24. Allora potrebbe esserci un errore nei dati"

**Proposta:** Verificare nel portale EU il progetto "Resilience" con ISS come partecipante. Se il dato sorgente è effettivamente zero (progetto recente, budget non ancora pubblicato), documentare in `known-issues.md` come dato temporaneamente incompleto per progetti post-2024.

---

## #11 — SC Map: distinzione visiva flowing-in / flowing-out non chiara

**Section:** Supply Chain > Map
**Type:** UX / Visual
**Status:** Resolved (2026-03-24)

Nella Supply Chain Map, gli archi di investimento hanno due direzioni (flowing-in = fondi che entrano nel paese, flowing-out = fondi che escono). La distinzione visiva tra i due non è immediatamente percepibile: l'utente non riesce a capire guardando l'animazione quale arco rappresenti l'uno e quale l'altro.

> "Si vede che l'arco è un po' più chiaro e un po' più scuro. È più scuro quando è flowing in non si vede?"
> "flowing in significa che entrano, flowing out significa che entrano [sic]"

**Proposta:** Rendere la distinzione flowing-in / flowing-out più esplicita: colori diversi (es. verde per in, arancio per out), frecce direzionali sull'arco, o un indicatore testuale nella sidebar. Aggiornare la legenda per spiegare i due stati.

---

## #12 — SC Map: quando flowing-out è assente per un paese, nessun messaggio esplicito

**Section:** Supply Chain > Map
**Type:** UX / Content
**Status:** Resolved (2026-03-24)

Selezionando un paese (es. Italia) che ha solo archi flowing-in e nessun flowing-out, la UI non comunica esplicitamente questa assenza. L'utente potrebbe pensare che i dati manchino o che ci sia un errore.

> "mancando flaming out uno rimane un po' cioè tu dici quando manca flaming out bisogna scrivere non c'è niente non ci sono"

**Proposta:** Nella sidebar paese della SC Map, aggiungere una riga esplicita quando `flowingOut === 0`: "No outbound investments recorded" (o equivalente). Analogamente per flowing-in assente. Questo evita ambiguità tra dato mancante e dato effettivamente zero.

---

## #13 — SC Graph: nodi non connessi non vengono oscurati alla selezione di un nodo

**Section:** Supply Chain > Graph
**Type:** UX / Feature
**Status:** Resolved (2026-03-24)

Quando si seleziona un nodo nel grafo (es. "US Department of Defense"), il grafo mostra le connessioni dirette ma non oscura/shadowing i nodi non connessi. Il risultato è un grafo affollato dove è difficile isolare il cluster del nodo selezionato.

> "ti identifica le connessioni ma dovrebbe far scomparire o mettere tipo qualcosa di shadowing su tutti gli altri in modo da tenere evidenziate parliamo dei cluster e dei nodi"

**Proposta:** Al click su un nodo in `graph.js`, applicare `opacity: 0.1` (o `display: none`) a tutti i nodi e link non direttamente connessi al nodo selezionato. Ripristinare alla deselezione. Pattern già comune nei force graph D3.

---

## #14 — SC Graph: legenda in basso poco visibile

**Section:** Supply Chain > Graph
**Type:** UI / Visual
**Status:** Resolved (2026-03-24)

La legenda del grafo, posizionata in basso, non è sufficientemente visibile. L'utente dichiara di vederla ma con difficoltà, e deve avvicinarsi allo schermo.

> "in basso hai una leggenda che non si vede bene"

**Proposta:** Aumentare la dimensione del testo e delle icone nella legenda del grafo. Valutare se spostarla in un pannello fisso laterale o in un overlay collassabile, più vicino ai controlli del grafo.

---

## #15 — SC Map: filtro entità mostra l'entità ma non fa comparire gli archi (caso Intesa)

**Section:** Supply Chain > Map
**Type:** Bug
**Status:** Resolved (2026-03-24)

Usando il filtro entità nella SC Map e cercando "Intesa", l'entità viene individuata ma gli archi di connessione non compaiono contestualmente. Solo rimuovendo il termine e riscrivendolo gli archi diventano visibili.

> "forse qua eccola qua si non è che non c'è che non vedevo comparire il filo... il filtro non si fa apparire i fili a fa apparire solo i fili non"
> "Se tu togli intesa dal search? Se lo riscrivi ti fa apparire di nuovo intesa."

**Proposta:** Verificare in `map.js` che l'applicazione del filtro entità (entity filter) triggeri correttamente il re-render degli archi, non solo dei nodi paese. Possibile race condition tra il render del nodo e il render degli archi dipendenti.

---

## #16 — EDF Overview: top companies non cliccabili

**Section:** European Defence Fund > Overview (top companies / top investors list)
**Type:** Feature / UX
**Status:** Resolved (2026-03-24)

Nella lista delle top companies per finanziamenti EDF (es. Leonardo, Fincantieri, Elettronica SPA), cliccando su un'azienda non succede nulla. L'utente si aspetta almeno un dettaglio minimo (es. partita IVA, link al portale EU, paese).

> "Se dovresti poter cliccare, non riesci a cliccare?"
> "No, se clicco non vedo. Almeno la partita IVA ci vorrebbe."

**Proposta:** Rendere le righe della top companies list in EDF Overview cliccabili, aprendo una sidebar o modale con i dettagli dell'organizzazione (analogamente a EDF Beneficiaries). In alternativa, aggiungere un link diretto alla vista EDF Beneficiaries filtrata per quella org.

---

## #17 — Globale: font troppo piccoli nelle sidebar e pannelli informativi

**Section:** Globale (EDF Map sidebar, investigation page)
**Type:** UI / Accessibility
**Status:** Resolved (2026-03-24)

In più punti dell'interfaccia (sidebar EDF Map, pannelli con dati testuali, investigation page) il font è percepito come troppo piccolo, richiedendo all'utente di avvicinarsi allo schermo.

> "i sifonti sono troppo piccoli, no? Eh, sono piccolini, io faccio fatica, inizio a fare fatica."
> "qua fonti troppo piccoli. Sì, un pelino."

**Proposta:** Audit dei font-size nelle sidebar e nei pannelli informativi. Impostare un minimo di `14px` per il testo body nelle sidebar, `13px` per le label secondarie. Priorità: sidebar EDF Map e investigation page. Collegato al refactoring CSS già in corso.

---

## #18 — Generale: mancanza di tutorial o orientamento complessivo

**Section:** Globale
**Type:** UX / Content
**Status:** Open

L'utente commenta che l'app, pur essendo ricca di dati, manca di un orientamento complessivo che aiuti un nuovo utente a capire dove si trova, cosa può fare e come le sezioni sono collegate. La pagina intro viene saltata immediatamente (vedi anche japi #1), quindi il contesto non arriva.

> "questo andrebbe fatto un una specie di o demo complessiva o spiegazione dove sei qua, che cos'è questo, ma in maniera più chiara"
> "se uno deve farsi un'idea senza avere un contesto. In teoria il contesto era detto nella pagina iniziale, però tu l'hai cliccata subito. Subito, eh."

**Proposta:** Valutare l'aggiunta di un tour guidato (es. intro.js o shepherd.js) o di un banner "Come usare questa app" persistente e collassabile. In alternativa, un modal di benvenuto al primo accesso che mostri le 3-4 sezioni principali con una frase ciascuna. Target: utenti ricercatori, non generalisti.

---

## #19 — Investigation page: testo in cirillico

**Section:** automated-investigation.html
**Type:** Bug
**Status:** Moved to known-issues.md #8 (2026-03-24)

In una sezione della pagina `automated-investigation.html`, compare del testo in caratteri cirillici. Probabile artefatto della generazione AI (Claude ha incluso testo in russo/cirillico nella risposta usata come base per la pagina).

> "Come mai in russo? In cirillico? Oh, yeah."

**Proposta:** Aprire `automated-investigation.html` e cercare occorrenze di caratteri Unicode nel range cirillico (`\u0400–\u04FF`). Rimuovere o sostituire il testo in cirillico con l'equivalente in italiano o inglese.

---

## #20 — About / Data: fonti dati (database.json, edf_calls.json) non spiegate nell'app

**Section:** About > Data
**Type:** Content
**Status:** Resolved (2026-03-24)

Le due fonti dati principali (`database.json` per la supply chain, `edf_calls.json` per le call EDF) non sono spiegate nell'interfaccia. L'utente che vuole capire da dove vengono i dati non ha un punto di accesso chiaro dentro l'app.

> "praticamente tutto l'Ambaradan è gestito, si basa su queste due fonti, uno è Database JSON e l'altro è DF Call... qua non sono spiegati ma insomma poi questi li devo spiegare"

**Proposta:** Nella tab About > Data (già esistente secondo japi #22), aggiungere una sezione che descriva brevemente le due sorgenti: origine, frequenza di aggiornamento, script di generazione, link al file raw scaricabile. Questo è già parzialmente documentato in `readme.md` — portarlo nell'interfaccia.

---

## #21 — SC Graph: stato iniziale con tutti i nodi visibili senza filtro → incomprensibile

**Section:** Supply Chain > Graph
**Type:** UX / Visual
**Status:** Resolved (2026-03-24)

Aprendo la tab SC Graph per la prima volta, tutti i nodi (companies, investors, pubblici e privati, tutti i settori) sono visibili contemporaneamente senza nessun filtro di default. L'utente non riesce a capire da dove partire o cosa stia guardando.

> "Pubblici privati se non si filtrano però si possono filtrare da lì dall'alto però la visione iniziale è tutto insieme quindi chiaramente non si capisce niente"

Nota: il problema è distinto da #13 (assenza di dimming sui nodi non connessi alla selezione) e da #14 (legenda poco visibile). Qui si tratta dello stato default del grafo prima di qualsiasi interazione.

**Proposta:** Valutare uno stato iniziale con un filtro pre-applicato (es. solo un settore, o solo i top-N nodi per connessioni) oppure un messaggio di orientamento sovrapposto al grafo al primo caricamento ("Seleziona un settore o cerca un'entità per iniziare"). In alternativa, aprire il grafo già in modalità Bipartite con un settore selezionato come default.

---

_Total: 21 issues — 16 resolved, 1 not reproducible, 1 open, 3 moved to known-issues.md_

_Resolved: #1, #2, #4, #5, #6, #7, #8, #11, #12, #13, #14, #15, #16, #17, #20, #21_
_Not reproducible: #3_
_Open: #18_
_Moved: #9 → known-issues.md #6, #10 → known-issues.md #7, #19 → known-issues.md #8_
