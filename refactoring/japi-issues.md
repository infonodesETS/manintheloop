# User Test Issues — "Japi" session

_Source: live user test, recorded verbal feedback, transcribed via Mistral._
_Logged: 2026-03-22_

---

## Rules

These issues follow the same protocol as `issues.md`:
- Resolved issues → `CHANGELOG.md`
- Permanent data gaps → `known-issues.md`
- This file tracks active issues only

---

## Area: Intro & Navigazione globale

### I-A · Intro: nessun CTA visibile e nav bar non riconosciuta

**Status: Resolved — 2026-03-22**

L'utente non ha trovato un modo immediato per "iniziare". La barra di navigazione superiore non è stata riconosciuta come tale — sembrava la barra del browser e non è stata cliccata. Solo dopo ha scoperto i link di navigazione.

Richieste esplicite:
- Un bottone o link "Esplora Supply Chain →" nel corpo del testo dell'intro
- Link contestuali nel testo (non solo nella barra in alto) per entrare nelle sezioni principali

> *"mi aspettavo di trovare un bottone per iniziare o andare da qualche parte"*
> *"la barra di navigazione mi sembrava un po' quella del mio browser quindi subito non l'ho molto cagata"*
> *"un link nel testo non soltanto nella barra di navigazione"*

---

### I-B · Intro troppo povera di contesto; About dovrebbe essere accessibile dall'intro

**Status: Open**

L'utente ha trovato l'intro insufficiente per capire cosa fa l'app. Il contenuto della pagina About (cos'è la ricerca, perché il mining, i settori, il contesto geopolitico) dovrebbe essere accessibile direttamente dall'intro — linkato con evidenza o integrato sotto. Proposta utente: About come estensione naturale dell'intro, in modo che uno possa continuare a leggere senza cercare altro.

> *"È molto povera qua la intro"*
> *"Ma perché tutta questa parte di about non la metti qua sotto?"*
> *"l'about potrebbe diventare la intro"*
> *"così alla fine uno continua e dice ok ne so abbastanza, mi interessano, e cerco qua dentro"*

---

### I-C · Glossario / tooltip sui termini chiave

**Status: Open**

Termini come "Relationships", "Mining", i nomi dei settori non sono autoesplicativi per utenti non specialisti. L'utente ha proposto diverse soluzioni alternative:
- Tooltip al hover sulle stat card (es. cosa sono le "298 Relationships")
- Tooltip sulle celle della tabella
- Un glossario centralizzato che possa alimentare anche i tooltip e la sezione About

Il caso "mining" è emblematico: l'utente non ha collegato l'estrazione di materie prime al contesto difesa senza spiegazione esplicita.

> *"andrebbe fatto una spiegazione magari un tooltip... cosa sono le relationship"*
> *"un bel glossario ci starebbe bene"*
> *"ma in cosa sarebbero minare quelli che estraggono le materie prime... non l'avrei collegato"*

---

### I-D · Data Quality e Known Issues: troppo nascosti sotto Tools

**Status: Resolved — 2026-03-22**

Attualmente Data Quality e Known Issues sono sub-tab di Tools. L'utente ha notato che riguardano tutti i dati dell'app (supply chain + EDF), non solo i Tools. Proposta: portarli a primo livello di navigazione oppure integrarli nell'About, in modo che siano visibili prima di iniziare a esplorare i dati.

> *"non va alla fine a linkarli sempre nella home, piuttosto che averli dentro a tools"*
> *"riguardano anche i dati che sono su supply chain european o no?"*
> *"metterli come primo livello nel menu... dentro l'about, diciamo"*
> *"se no me ne accorgo alla fine, non va bene"*

---

## Area: Supply Chain — Map

### M-A · Entità selezionata non evidenziata nella sidebar

**Status: Resolved — 2026-03-22**

Quando si clicca su un'entità (es. "MD") per filtrare la mappa, il nome appare evidenziato solo in alto a sinistra dell'interfaccia. Non risulta visibile nel pannello laterale, che è il luogo naturale e atteso dall'utente.

> *"vedo solo qua in alto a sinistra MD evidenziato, ma non la vedo nella sidebar, che è il luogo naturale. Sarebbe più utile lì."*

---

### M-B · Nessun modo chiaro per rimuovere il filtro sulla mappa

**Status: Resolved — 2026-03-22**

L'utente ha attivato un filtro entità per errore senza accorgersene, poi ha tentato di ricliccare per toglierlo — ma il click cambiava la selezione invece di azzerarla. Non è chiaro come tornare alla vista neutra.

Serve un meccanismo esplicito per resettare il filtro: pulsante "reset" visibile, click su area vuota, o tasto ESC.

> *"mi è venuto il filtro, non me ne ero accorto"*
> *"ci ricliccavo sopra per toglierlo e in realtà stavo solo cambiando il filtro"*

---

## Area: Supply Chain — Graph

### G-A · Deselezionare un nodo non è intuitivo

**Status: Resolved — 2026-03-22**

Dopo aver cliccato un nodo, chiudere la sidebar non rimuove la selezione. L'utente non ha trovato come tornare alla vista neutra del grafo. Serve un meccanismo chiaro: click su area vuota, tasto ESC, o pulsante reset visibile nella toolbar.

> *"io qua non sto capendo come tolgo la mia selezione"*
> *"Anche se chiudo questa, la selezione rimane"*

---

### G-B · Barra filtri del grafo: nessun background

**Status: Resolved — 2026-03-22**

La toolbar dei filtri del grafo non ha sfondo e si confonde con il contenuto visivo retrostante. Va aggiunto un background che la separi visivamente dal grafo sottostante.

> *"Mettici uno sfondo dietro questa barra, perché se no non..."*

---

### G-C · Modalità Network / Bipartite / Projection: etichette non spiegate

**Status: Resolved — 2026-03-22**

Le tre modalità di visualizzazione del grafo non hanno spiegazione contestuale. L'utente non ne ha compreso il significato senza spiegazione verbale. Servono tooltip o una riga descrittiva sotto le label. Nota: l'utente ha apprezzato molto la modalità Projection una volta capita.

> *"Network, Bipartite, Projection... per me non hanno significato"*
> *"queste tre cose qua per me non hanno significato"*

---

## Area: Supply Chain — Companies / Investors

### C-A · Sidebar Companies: allineamento label quando manca il badge "lead"

**Status: Resolved — 2026-03-22**

Nella sidebar di un'azienda, nella sezione investitori, quando il badge "lead" è assente in una riga il layout flexbox `space-between` sposta la label tutta a destra. L'utente ha proposto di centrare o allineare diversamente in assenza del badge.

> *"Qua sai il flex space between che quando ti scompare questo ti fa andare la label da tutta destra, invece dovrebbe stare al centro"*

---

## Area: Navigazione globale — Legenda settori

### L-A · Legenda settori: posizione ambigua, scambiata per elemento non interattivo

**Status: Resolved — 2026-03-22**

La barra della legenda dei settori si trova tra barre di navigazione interattive. L'utente non l'ha mai notata e calcolata durante tutta la navigazione, perché visivamente si confonde con gli altri elementi. Essendo non interattiva tra elementi interattivi, viene ignorata.

Proposta utente: spostarla in un footer o in un'area semanticamente separata, con etichetta "Legenda" esplicita.

> *"fino adesso non l'ho praticamente mai calcolata perché le barre qua sopra sono tutte interattive tranne questa"*
> *"gli darei un altro posto, piuttosto lo metterei in fondo, tipo footer"*
> *"mettendoci leggenda così almeno uno vede tutto"*

---

## Area: Supply Chain — Matrix

### SC-MX-A · Matrix: legenda assente

**Status: Resolved — 2026-03-22**

La tab Matrix non ha una legenda che spieghi il significato delle celle (lead investment vs follow investment). L'utente non capisce la differenza senza aiuto esterno.

> *"qua manca anche la legend, perché lead..."*

---

## Area: European Defence Fund — Map

### EDF-M-A · Mappa EDF non centrata sull'Europa all'avvio

**Status: Resolved — già presente in edfmap.js (line 314). Confermato 2026-03-22.**

All'apertura della tab EDF Map, la vista non è centrata sull'area densa di nodi (Europa). L'utente si è trovato a guardare la Russia. Il `translate/scale` iniziale va ricalibrato.

> *"qua la mappa non mi si è centrata dove ci sono i nodi"*
> *"Sto guardando la Russia, credo, in questo momento. Sì, sì, questo è un bug."*

---

### EDF-M-B · Archi tra paesi: significato non spiegato + mancanza di ponderazione

**Status: Open**

L'utente non ha capito cosa rappresentano le linee tra paesi nella EDF Map (co-partecipazione agli stessi progetti). Va aggiunto testo esplicativo o tooltip sugli archi.

Suggerimento correlato: rendere gli archi ponderati per intensità — più progetti condivisi tra due paesi = arco più spesso/opaco. Permetterebbe di vedere a colpo d'occhio le partnership più forti (es. Italia–Francia vs Italia–Spagna).

> *"non mi è chiaro perché c'è la relazione con gli altri paesi"*
> *"va spiegato, praticamente significa quali sono gli altri paesi coinvolti nello stesso progetto"*
> *"valorizzare il collegamento in base all'intensità... se è più intenso con la Francia e meno intenso con la Spagna"*

---

## Area: European Defence Fund — EDF Calls Search

### EDF-C-A · Testo sotto il titolo: font e leggibilità

**Status: Resolved — 2026-03-22**

Il testo descrittivo sotto il titolo della sezione EDF Calls usa un font diverso (monospace/code) e risulta illeggibile. Da correggere.

> *"qui sotto il titolo c'è un testo nero che ha cambiato il font code. Ok, sì, non si legge proprio."*

---

### EDF-C-B · Select "topic identifier" chiusa di default: utente non capisce cosa cercare

**Status: Resolved — 2026-03-22**

L'utente non capisce da dove iniziare la ricerca finché non apre il dropdown manualmente. La proposta è aprire la select di default, oppure mostrare un placeholder con esempi concreti, così che l'utente capisca immediatamente che ci sono opzioni selezionabili.

> *"da questo qua sopra non capivo bene, non ho capito"*
> *"perché dice type identifier, non saprei neanche dove partire con questi numeri"*
> *"la select di topic identifier dovrebbe essere aperta di default"*

---

### EDF-C-C · Search: scope troppo ristretto

**Status: Resolved — 2026-03-22**

La ricerca copre solo topic identifier e titolo. L'utente ha proposto di includere anche la descrizione del progetto e i nomi dei partner, per permettere ricerche più naturali e contestuali.

> *"Forse si potrebbe inserire anche la description del progetto"*
> *"forse anche per partner si potrebbe fare"*

---

### EDF-C-D · Accordion anno/progetti: comportamento confuso

**Status: Resolved — 2026-03-22**

Il riassunto per anno (es. "Anno 2024 · 2 progetti · 19 partecipanti") apre e chiude un accordion. L'utente lo ha interpretato come un link per "entrare" nei dati e si è confuso quando invece si è aperto/chiuso. Ha poi messo in discussione l'utilità stessa dell'accordion: se il contenuto non è cliccabile, perché è espandibile?

> *"Quando lo clicco però si chiude"*
> *"perché è espandibile? Cioè non è fisso? Chi se ne importa di averlo?"*

---

### EDF-C-E · Comparison view: bug

**Status: Open — bug**

Bug segnalato durante la navigazione nella sezione EDF Calls Search, comparison view. Nessun dettaglio aggiuntivo nel feedback trascritto.

> *"qua c'è un bug in comparison view, va fixato"*

---

### EDF-C-F · Ricerca per termini comuni non restituisce risultati

**Status: Resolved — 2026-03-22** (coperta da EDF-C-C)

Cercando termini generici del dominio (es. "drone") la ricerca non restituisce risultati, perché la search è limitata a topic identifier e titolo. All'utente la ricerca appare rotta. Il owner stesso ha confermato che si tratta di un limite/errore.

Correlato a EDF-C-C (estensione dello scope), ma distinto: il problema immediato è che la search appare non funzionante su termini ovvi per il dominio.

> *"prova a scrivere il nome di un'arma in inglese, droni tipo... non c'è, non compare niente"*
> *"No, no, questo è un errore"*

---

## Area: European Defence Fund — EDF Beneficiaries

### EDF-B-A · Nessun accesso al dettaglio progetto dalla sidebar beneficiario

**Status: Open**

Dall'elenco dei progetti nella sidebar di un'organizzazione (es. Leonardo), l'utente vorrebbe poter cliccare su un progetto per vederne il dettaglio completo — corrispondente alla vista già esistente in EDF Calls Search. Il collegamento tra le due sezioni è assente.

> *"vorresti poter cliccare su un progetto per vedere che cos'è"*
> *"una qualche modale, o comunque un modo per accedere al dato di dettaglio del singolo progetto"*
> *"sarebbe praticamente la pagina che vedevo prima di EDF Call Search"*

---

### EDF-B-B · Riga cliccabile non evidente nella tabella

**Status: Resolved — 2026-03-22**

L'indicatore visivo che segnala la riga come cliccabile (la freccia) è troppo piccolo e non viene notato dall'utente. L'interazione non è scoperta spontaneamente.

> *"qua c'è solo la vostra freccina piccolissima"*
> *"se no, non fa niente se si clicca"*
