'use strict';

// ── Man in the Loop — i18n system ─────────────────────────────────────────────
// Supported languages: it (default), en, fr, es
// Storage key: 'mitl-lang'
// Usage:
//   t('key')          → translated string (current lang)
//   t('key', {a: 1}) → translated string with {a} placeholders replaced
//   setLang('en')     → switch language, save to localStorage, re-apply DOM
// ─────────────────────────────────────────────────────────────────────────────

const TRANSLATIONS = {
  it: {
    // Navigation
    'nav.map':          'Map',
    'nav.networks':     'Networks',
    'nav.search':       'Search',
    'nav.publications': 'Publications',
    'nav.about':        'About',

    // MAP — default panel
    'map.section_title':  'Cosa trovi in questa sezione',
    'map.intro':          'In questa pagina è possibile tracciare alcuni dei finanziamenti più rilevanti dal Paese di origine alle società di un Paese terzo.',
    'map.dataset_stats':  'Il dataset copre {countries} Paesi e {entities} soggetti, con {arcs} connessioni transnazionali.',
    'map.circle_explanation': 'Ogni cerchio rappresenta un Paese con almeno un soggetto nel database. Il diametro riflette il numero di relazioni (in entrata e in uscita). Selezionando un Paese, appariranno degli archi di connessione.',
    'map.how_to_read':    'Come leggere le informazioni',
    'map.arc_colors':     'Gli archi possono essere di tre colori:',
    'map.arc_blue':       '<strong>Blu</strong>: un soggetto del Paese selezionato ha finanziato una società dell\'altro Paese.',
    'map.arc_red':        '<strong>Rosso</strong>: una società del Paese selezionato ha ricevuto finanziamenti da un soggetto dell\'altro Paese.',
    'map.arc_purple':     '<strong>Viola</strong>: tra i due Paesi si sono registrati finanziamenti sia in entrata che in uscita.',
    'map.arc_click':      'Cliccando sull\'arco, il box a sinistra mostrerà il dettaglio delle relazioni tra i soggetti.',
    'map.our_data':       'I nostri dati',
    'map.data_source':    'I dati sono stati raccolti da Crunchbase, sulla base delle società della filiera del settore delle armi autonome. {investors} soggetti dispongono di dati sugli investitori.',

    // MAP — toolbar
    'map.all_entities':   'All Entities',
    'map.eu_funded':      'EU Funded Only',
    'map.reset_zoom':        'Reset zoom',
    'map.about_this_map':    'About this map',
    'map.investments_title': 'Investments',
    'map.edf_title':         'Finanziamenti EU',
    'map.wip':               'work in progress',
    'map.edf_mode_desc':     'Questa mappa mostra i finanziamenti europei per lo sviluppo di armamenti erogati ai singoli Stati dell\'Unione Europea e, in dettaglio, a quali delle loro aziende, università o altri soggetti pubblici e privati.<br><br>Il diametro dei cerchi è proporzionato al totale dei finanziamenti ricevuti dallo Stato.<br><br>Cliccando sul cerchio corrispondente a un paese si aprirà l\'elenco di tutti i singoli soggetti che hanno beneficiato di finanziamenti europei con il dettaglio della cifra incassata. È possibile cliccare sul nome del soggetto che ti interessa e aprire la sua scheda di dettaglio, contenente tutte le informazioni che siamo riusciti a raccogliere.<br><br>Grazie ai selettori, puoi scegliere di visualizzare tutte le tipologie di finanziamento pubblico europeo (EDF, Horizon, PESCO etc...) o solo quella o quelle che ti interessano.',
    'fin.info.EDF':     'L\'EDF (Fondo europeo per la difesa) sostiene le aziende dei diversi Stati membri nello sviluppo di progetti di difesa competitivi e collaborativi, capaci di produrre tecnologie ed equipaggiamenti militari innovativi e interoperabili. Offre supporto e consulenza ai partecipanti lungo l\'intero ciclo di ricerca e sviluppo.',
    'fin.info.HORIZON': 'Horizon Europe è il principale programma di finanziamento dell\'UE per la ricerca e l\'innovazione. Favorisce la collaborazione e rafforza l\'impatto della ricerca e dell\'innovazione nello sviluppo e nell\'attuazione delle politiche europee, affrontando al contempo le sfide globali. Sostiene la creazione e la diffusione di conoscenze e tecnologie d\'eccellenza.',
    'fin.info.PESCO':   'La PESCO (Cooperazione strutturata permanente) è un quadro fondato sui trattati che consente ai 26 Stati membri partecipanti di pianificare, sviluppare e investire congiuntamente nello sviluppo collaborativo di capacità militari, e di rafforzare la prontezza operativa e il contributo delle forze armate.',
    'fin.info.EDIP':    'L\'EDIP (Programma per l\'industria europea della difesa) è un\'iniziativa dell\'UE da 1,5 miliardi di euro per rafforzare e modernizzare l\'industria europea della difesa, aumentare la capacità produttiva e garantire tecnologie all\'avanguardia, resilienza e un approvvigionamento costante di equipaggiamenti militari alle forze armate degli Stati membri.',
    'fin.info.EUDIS':   'L\'EUDIS (Programma dell\'UE per l\'innovazione nella difesa) è uno strumento reso possibile dal Fondo europeo per la difesa (EDF) per rafforzare l\'innovazione nel settore della difesa nell\'Unione europea.',
    'fin.info.EIF':     'Il Defence Equity Facility fornisce finanziamenti a fondi privati che investono in aziende impegnate nello sviluppo di tecnologie e prodotti innovativi per la difesa. L\'iniziativa mira a stimolare lo sviluppo di un ecosistema di investitori europei della difesa.',
    'fin.info.DIANA':   'DIANA (Acceleratore di innovazione per la difesa del Nord Atlantico) è un\'organizzazione creata dalla NATO per individuare e accelerare l\'innovazione, allo scopo di fornire capacità di difesa e sicurezza all\'Alleanza.',
    'fin.info.NIF':     'Il NIF (NATO Innovation Fund) è un fondo di venture capital autonomo sostenuto da 24 alleati della NATO, che investe oltre 1 miliardo di euro in tecnologie deep tech.',
    'map.loading':           'Loading map data…',

    // NAV — menu e sottomenu ('Search' e 'About' restano in inglese ovunque)
    'nav.eu_funding':   'Finanziamenti EU',
    'nav.investments':  'Investimenti globali',
    'nav.publications': 'Pubblicazioni',
    'nav.map':          'Mappa',
    'nav.network':      'Rete',
    'nav.key_figures':  'Numeri chiave',

    // KEY FIGURES
    'kf.heading':             'I numeri chiave',
    'kf.heading_sub':         'I finanziamenti europei allo sviluppo di armamenti, in sintesi.',
    'kf.unit_projects':       'progetti',
    'kf.t_countries_fund':    'Top 5 Paesi per finanziamenti ricevuti',
    'kf.t_companies_fund':    'Top 5 aziende per finanziamenti ricevuti',
    'kf.t_companies_proj':    'Top 5 aziende per numero di progetti',
    'kf.t_universities_fund': 'Top 5 università e centri di ricerca per finanziamenti ricevuti',
    'kf.t_universities_proj': 'Top 5 università e centri di ricerca per numero di progetti',
    // KEY FIGURES — sezione Investimenti globali
    'kf.heading_sub_inv':      'Chi mette i capitali nelle aziende della difesa e della sicurezza, in sintesi.',
    'kf.unit_holdings':        'partecipazioni',
    'kf.unit_investors':       'investitori',
    'kf.t_top_investors':      'Top 5 investitori per numero di partecipazioni',
    'kf.t_public_investors':   'Top 5 investitori pubblici per numero di partecipazioni',
    'kf.t_most_backed':        'Top 5 aziende per numero di investitori',
    'kf.t_investor_countries': 'Top 5 Paesi di origine dei capitali',
    'kf.t_dual_funded':        'Doppio finanziamento: le prime 5 fra le {n} aziende che ricevono sia fondi EDF sia investimenti privati',
    'kf.scope_label':          'Perimetro',
    'kf.scope_defence':        'Solo defence tech',
    'kf.scope_all':            'Tutte le entità',
    'kf.scope_count':          '{n} aziende defence tech su {tot} partecipate',
    'kf.caveat_scope':         'Il perimetro "defence tech" è provvisorio. Un\'azienda vi rientra se partecipa a progetti EDF, se è classificata come difesa nel database o nell\'ETF Aerospace & Defence, oppure se Crunchbase le assegna un settore militare, aerospaziale, satellitare o di sicurezza nazionale. Le etichette Crunchbase sono generiche, quindi qualche azienda sfugge: Helsing risulta solo "Information Technology" e rientra unicamente perché partecipa a progetti EDF. I criteri sono in data/defence_criteria.json.',
    'kf.caveat_inv':           'Le relazioni di investimento nel database registrano il legame fra investitore e azienda, non l\'importo versato. Tutte le classifiche di questa pagina contano quindi partecipazioni, non capitali: dicono chi è più presente, non chi ha speso di più. Il conteggio riflette inoltre solo ciò che è documentato nel database, non l\'intero portafoglio di un investitore.',

    // NETWORKS — sidebar
    'net.title':          'Defence Network',
    'net.find_entity':    'Find entity',
    'net.search_placeholder': 'Search organisations…',
    'net.country':        'Country',
    'net.relationships':  'Mostra dati relativi a:',
    'net.actors':         'Actors',
    'net.connections':    'Connections',
    'net.note':           'In questa sezione è possibile esplorare le relazioni economiche tra i soggetti presenti nel database.<br><br>È possibile visualizzare i soli progetti finanziati attraverso EDF (European Defence Funds).<br><br>Dimensione del rombo = bilancio UE. I cerchi sono uniformi.<br>Clicca sul nodo → dettagli + collegamenti transnazionali.<br>Clicca sullo sfondo → ripristina.',
    'net.note_edf':       'In questa sezione è possibile esplorare le relazioni economiche tra i soggetti presenti nel database che hanno ricevuto dei finanziamenti europei.<br><br>Al momento è disponibile il dettaglio dei soli fondi EDF, ma stiamo lavorando per integrare anche altri programmi di finanziamento europeo al settore della difesa e, in particolare, delle armi autonome.<br><br>La dimensione del rombo indica la dimensione del budget previsto per il progetto.',
    'net.in_view':        'In this view',
    'net.selected_node':  'Selected node',
    'net.select_country': 'Select a country to see stats.',
    'net.edf_tip':        'Flaggando "EDF projects" il sistema mostrerà tutti i soggetti che hanno ricevuto finanziamenti attraverso il programma EDF (European Defence Fund), le relazioni fra loro e le informazioni di ogni singolo progetto.',
    'net.inv_tip':        'Flaggando "Investments" il sistema mostrerà tutti i soggetti economici (società quotate, start-up, fondi, etc...) che abbiamo inserito nel database e le relazioni fra loro in termini di investimento.',

    // ABOUT — content
    'about.title':        'About',
    'about.intro':        'La piattaforma Man in the Loop è sviluppata da info.nodes, organizzazione no-profit italiana fondata nel 2019, grazie al supporto economico di <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, nell\'ambito del programma globale "Militarisation of Tech".',
    'about.nav_about':      'Chi siamo',
    'about.nav_data':       'Metodologia e dati',
    'about.nav_glossary':   'Glossario',
    'about.nav_contribute': 'Contribuisci',
    'about.glossary_intro': 'I termini chiave usati nella piattaforma, spiegati in modo semplice.',
    'about.last_update_label': 'Ultimo aggiornamento dati',
    'about.team_lead':    'L\'attuale prototipo è stato sviluppato da:',
    'about.team_list':    '<li>Davide Del Monte — Coordinatore e Lead Researcher</li><li>Laura Carrer — Researcher</li><li>Andrea Daniele Signorelli — Researcher</li>',
    'about.collab':       'in collaborazione con DATAPITCH:',
    'about.datapitch_list': '<li>Andrea Nelson Mauro — Developer e Data expert</li><li>Emma Besseghini — Junior Researcher</li>',
    'about.contribute_label': 'Contribuisci',
    'about.contribute_intro': 'Abbiamo fatto il possibile per verificare l\'accuratezza dei dati inseriti nella piattaforma, ma è un lavoro molto complicato e il nostro team ha risorse limitate. Per questo ti chiediamo di darci una mano nei seguenti modi, se ti va:',
    'about.contribute_list': '<li>Segnalaci gli <strong>errori nei dati o i bug</strong> che riscontri utilizzando la piattaforma, scrivendoci a <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>Segnalaci una o più <strong>società</strong> che ti interessano e che al momento non sono presenti nel database. Scrivi a <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a> indicandoci il nome della società e possibilmente il suo codice identificativo e l\'url del suo sito internet ufficiale.</li><li>Segnalaci una tua <strong>pubblicazione</strong>, se hai utilizzato Man in the loop per una tua ricerca o inchiesta. Se ti fa piacere la aggiungeremo nella sezione "Pubblicazioni". Invia la tua pubblicazione a <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>Se ti piace il lavoro che stiamo facendo e vuoi vederlo sopravvivere ed espandersi in futuro, fai una donazione a info.nodes utilizzando il tasto "dona" nel footer del sito <a href="https://www.infonodes.org" target="_blank" rel="noopener" style="color: var(--accent); text-decoration: none;">www.infonodes.org</a></li>',
    'about.data_label':   'I dati di Man in the Loop',
    'about.data_p1':      'Il progetto di ricerca sperimentale open data ha lo scopo di mappare le aziende e gli investitori nel settore delle armi autonome, lungo tutta la catena di approvvigionamento globale.',
    'about.data_p2':      'Per lo sviluppo di questo prototipo abbiamo costruito un database inserendo le seguenti società quotate alla borsa di Wall Street e identificate per settore utilizzando i codici GICS:',
    'about.data_sectors': '<li>Settore Minerario: Materials, con focus su Metals &amp; Mining (Codice GICS 151040).</li><li>Settore Tech: Information Technology (Codice GICS 45), Communication Services (Codice GICS 50).</li><li>Settore della difesa: Aerospace &amp; Defence (Codice GICS 201010).</li>',
    'about.data_p3':      'Abbiamo inoltre aggiunto 18 start-up europee ritenute rilevanti nel settore. Creato il database, abbiamo ricavato i dati relativi ai Lead Investors e ai Top Investors dalla piattaforma a pagamento Crunchbase.',
    'about.data_nota':    'NOTA: tutte le informazioni presenti nelle sezioni della piattaforma sono la fotografia alla data in cui abbiamo scaricato le informazioni da Crunchbase (aprile 2026).',
    'about.eu_funding_label': 'I finanziamenti pubblici alla difesa',
    'about.eu_funding_p1':    'Abbiamo raccolto e inserito nel database tutte le entità (società, università, centri di ricerca, istituzioni pubbliche) che hanno partecipato a progetti EDF (European Defence Fund) e che quindi hanno ricevuto, direttamente o indirettamente, dei fondi dall\'Unione Europea per fare ricerca, sviluppare, produrre e commercializzare dei sistemi d\'arma autonomi.',
    'about.eu_funding_p2':    'L\'EDF però non è l\'unico canale attraverso cui il denaro pubblico arriva a questo settore. Nella sezione <a href="./?mode=edf" style="color: var(--accent); text-decoration: none;">Finanziamenti EU</a> trovi un selettore con otto programmi: oltre all\'EDF ci sono Horizon Europe, PESCO, EDIP, EUDIS e il Defence Equity Facility. Al momento sono disponibili <strong>soltanto i dati EDF</strong>: gli altri sono contrassegnati come "work in progress" perché stiamo lavorando per integrarli. Li abbiamo elencati fin da subito perché la dimensione del fenomeno si coglie guardando l\'insieme dei canali di finanziamento, non uno solo.',
    'about.eu_funding_p3':    'Due delle voci del selettore — DIANA e il NATO Innovation Fund — non sono programmi dell\'Unione Europea ma della NATO, e per questo sono separate dalle altre da una linea. Le includiamo perché finanziano gli stessi soggetti con obiettivi tecnologici analoghi, pur rispondendo a una governance diversa e a un perimetro politico più ampio di quello comunitario.',
    'about.limits_method_label': 'Limiti metodologici',
    'about.limits_method': '<li><strong>Assenza di una definizione universalmente condivisa di "arma autonoma"</strong> — il confine tra sistema autonomo, semi-autonomo e teleoperato è tuttora oggetto di dibattito politico e scientifico. Le aziende incluse operano in settori contigui a quello delle armi autonome, ma non tutte producono esclusivamente sistemi autonomi. Il nostro team di ricerca ha identificato quella ritenuta più corretta e coerente. Per approfondire il tema "terminologico" ti suggeriamo di leggere il nostro report "AI: Seek &amp; Destroy" che trovi nella sezione <a href="publications.html" style="color: var(--accent); text-decoration: none;">Pubblicazioni</a> di questa piattaforma.</li><li><strong>Selezione per settore borsistico (GICS)</strong> — il database include principalmente società quotate a Wall Street identificate tramite codici GICS. Questo implica una sovrarappresentazione delle grandi aziende quotate e una possibile sottorappresentazione di attori rilevanti non quotati in borsa.</li><li><strong>Catena di approvvigionamento parziale</strong> — la filiera delle armi autonome è molto lunga e ramificata. Il database copre una selezione significativa ma non esaustiva dei soggetti coinvolti. Il nostro obiettivo, con release successive, è di avvicinarci il più possibile alla completezza ed esaustività dei dati. Per questo servirà anche il contributo di altri esperti e organizzazioni: se vuoi darci una mano, visita la sezione <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribuisci</a> per scoprire cosa puoi fare.<li><strong>Perimetro "defence tech" nelle classifiche</strong> — nei Numeri chiave della sezione Investimenti globali le classifiche mostrano di default solo le aziende classificate come defence tech: 165 delle 378 aziende partecipate. La classificazione unisce segnali certi (partecipazione a progetti EDF, presenza nell&#39;ETF Aerospace &amp; Defence, classificazione interna) alle etichette di settore di Crunchbase, che però sono generiche: Helsing, per esempio, vi risulta solo come "Information Technology" e rientra unicamente perché partecipa a progetti EDF. Il perimetro è quindi provvisorio e tende a escludere per difetto. Il selettore permette in ogni momento di passare a "Tutte le entità" e vedere il database completo.</li></li>',
    'about.limits_data_label': 'Limiti dei dati',
    'about.limits_data': '<li><strong>Dati Crunchbase: fotografia statica</strong> — le informazioni su round di finanziamento, investitori e struttura societaria sono aggiornate ad aprile 2026. Operazioni successive non sono riflesse nel database. Una delle nostre ambizioni per il futuro è di raccogliere risorse sufficienti per poter accedere alle API di Crunchbase.</li><li><strong>Dati Crunchbase: copertura non uniforme</strong> — Crunchbase ha copertura eccellente sulle aziende tech/VC statunitensi, ma più lacunosa su aziende europee tradizionali del settore difesa, che spesso non pubblicano dati dettagliati sugli investitori.</li><li><strong>Solo Lead Investor e Top Investor</strong> — non vengono mappati tutti gli investitori di ogni round, ma solo quelli classificati da Crunchbase come lead o top. Investitori minori o anonimi non compaiono nel nostro database.</li><li><strong>Dati EDF</strong> — per alcuni partecipanti ai progetti EDF il contributo UE ricevuto non è disponibile nelle fonti ufficiali della Commissione Europea e risulta quindi assente o parziale.</li><li><strong>Società private non quotate</strong> — le start-up e le PMI non quotate in borsa sono presenti solo se inserite manualmente dal team o se partecipanti a progetti EDF. La loro copertura è inevitabilmente più limitata. Anche per questo chiediamo l\'aiuto di esperti ed organizzazioni nel segnalarci altre entità interessanti da inserire nel nostro database. Nella sezione <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribuisci</a> puoi scoprire come fare.</li><li><strong>Dati sulla sede (paese) derivati da terze parti</strong> — la sede di alcune entità è stata ricavata da Crunchbase o Wikidata e potrebbe non riflettere la struttura legale effettiva (holding, sussidiarie, sede fiscale vs. operativa).</li><li><strong>Investimenti senza importo</strong> — le relazioni di investimento nel database registrano il legame fra un investitore e un’azienda, non la cifra versata. Le classifiche della sezione Investimenti globali contano quindi partecipazioni, non capitali: dicono chi è più presente, non chi ha investito di più. Gli importi di raccolta disponibili su Crunchbase non sono utilizzabili allo scopo, perché misurano il capitale raccolto complessivamente da un’azienda e non la quota riconducibile alla difesa.</li>',

    // PUBLICATIONS
    'pub.title':          'Research',
    'pub.desc':           'Ricerche, articoli e inchieste prodotti dal team del progetto Man in the Loop o da ricercatori, ricercatrici, giornalisti e giornaliste che hanno utilizzato la piattaforma per il loro lavoro.',
    'pub.contact':        'Se vuoi segnalarci la tua pubblicazione, fatta anche grazie a MAN IN THE LOOP, per inserirla in questa sezione, scrivici a:',

    // ONBOARDING overlay
    'onboard.subtitle':  'Un database open data sulle aziende, gli investitori e i soggetti pubblici coinvolti nella ricerca e produzione di armi autonome.',
    'onboard.1_title':   '① Esplora la Mappa',
    'onboard.1_desc':    'Ogni cerchio è un paese. Clicca per scoprire le connessioni finanziarie tra investitori e aziende, o passa alla modalità EDF per vedere i finanziamenti dello European Defence Fund paese per paese.',
    'onboard.2_title':   '② Cerca un\'entità',
    'onboard.2_desc':    'Nella sezione Search trovi le schede di tutte le entità presenti nel database: società, università, investitori, etc.',
    'onboard.3_title':   '③ Analizza le Reti',
    'onboard.3_desc':    'La sezione Networks visualizza le relazioni tra tutti i soggetti: investimenti e collaborazioni. Se spunti EDF, vedrai tutte le connessioni e le entità finanziate dallo European Defence Fund con il dettaglio di ogni singolo progetto.',
    'onboard.cta':       'Inizia a esplorare →',

    // Common — export buttons
    'common.print':       'Stampa',
  },

  en: {
    // Navigation
    'nav.map':          'Map',
    'nav.networks':     'Networks',
    'nav.search':       'Search',
    'nav.publications': 'Publications',
    'nav.about':        'About',

    // MAP — default panel
    'map.section_title':  'What this section shows',
    'map.intro':          'This page maps key cross-border investments from a source country to companies in third countries.',
    'map.dataset_stats':  'The dataset covers {countries} countries and {entities} entities, with {arcs} cross-border connections.',
    'map.circle_explanation': 'Each circle represents a country with at least one entity in the database. Circle size reflects the number of cross-border connections. Select a country to see the investment arcs.',
    'map.how_to_read':    'How to read the map',
    'map.arc_colors':     'Arcs can be of three colours:',
    'map.arc_blue':       '<strong>Blue</strong>: an entity from the selected country has invested in a company in the other country.',
    'map.arc_red':        '<strong>Red</strong>: a company in the selected country has received investment from an entity in the other country.',
    'map.arc_purple':     '<strong>Purple</strong>: investments flow in both directions between the two countries.',
    'map.arc_click':      'Click on an arc to see the detailed relationships between entities in the side panel.',
    'map.our_data':       'Our data',
    'map.data_source':    'Data was collected from Crunchbase, based on companies in the autonomous weapons supply chain. {investors} entities have investor data.',

    // MAP — toolbar
    'map.all_entities':   'All Entities',
    'map.eu_funded':      'EU Funded Only',
    'map.reset_zoom':     'Reset zoom',
    'map.about_this_map':    'About this map',
    'map.investments_title': 'Investments',
    'map.edf_title':         'EU Funding',
    'map.wip':               'work in progress',
    'map.edf_mode_desc':     'This map shows the European funding for weapons development granted to individual EU States and, in detail, to which of their companies, universities or other public and private entities.<br><br>The diameter of each circle is proportional to the total funding received by the State.<br><br>Clicking on the circle for a country opens the list of all the individual entities that have received European funding, with the amount each one received. You can click on the name of any entity to open its detail page, containing all the information we have been able to collect.<br><br>Using the selectors, you can choose to view all types of European public funding (EDF, Horizon, PESCO, etc.) or only the one(s) you are interested in.',
    'fin.info.EDF':     'The EDF supports companies across Member States develop competitive and collaborative defence projects that will deliver innovative and interoperable defence technologies and equipment. It offers support and advice to participants throughout the entire cycle of research and development.',
    'fin.info.HORIZON': 'Horizon Europe is the EU\'s key funding programme for research and innovation. The programme facilitates collaboration and strengthens the impact of research and innovation in developing, supporting and implementing EU policies while tackling global challenges. It supports creating and better dispersing of excellent knowledge and technologies.',
    'fin.info.PESCO':   'PESCO is a treaty-based framework for the 26 participating Member States to jointly plan, develop, and invest in collaborative capability development and to enhance the operational readiness and contribution of armed forces.',
    'fin.info.EDIP':    'The European Defence Industry Programme (EDIP) is a €1.5 billion EU-wide initiative to strengthen and modernise Europe\'s defence industry, ramp-up production capacity, and ensure cutting-edge technology, resilience, and steady supply of military equipment to the armed forces of the Member States.',
    'fin.info.EUDIS':   'The EU Defence Innovation Scheme (EUDIS) is an instrument enabled by the European Defence Fund (EDF) to strengthen defence innovation in the European Union.',
    'fin.info.EIF':     'The Defence Equity Facility provides financing to private funds investing in companies developing innovative defence technologies and products. This initiative aims to stimulate the development of an ecosystem of European defence investors.',
    'fin.info.DIANA':   'DIANA is the Defence Innovation Accelerator for the North Atlantic, an organisation established by NATO to find and accelerate innovation to provide defence and security effects for the Alliance.',
    'fin.info.NIF':     'A standalone venture capital fund backed by 24 NATO allies, deploying €1 billion+ in deep tech.',
    'map.loading':           'Loading map data…',

    // NAV — menu and sub-menu ('Search' and 'About' stay in English everywhere)
    'nav.eu_funding':   'EU Funding',
    'nav.investments':  'Global Investments',
    'nav.publications': 'Publications',
    'nav.map':          'Map',
    'nav.network':      'Network',
    'nav.key_figures':  'Key Figures',

    // KEY FIGURES
    'kf.heading':             'Key figures',
    'kf.heading_sub':         'European funding for weapons development, at a glance.',
    'kf.unit_projects':       'projects',
    'kf.t_countries_fund':    'Top 5 countries by funding received',
    'kf.t_companies_fund':    'Top 5 companies by funding received',
    'kf.t_companies_proj':    'Top 5 companies by number of projects',
    'kf.t_universities_fund': 'Top 5 universities and research centres by funding received',
    'kf.t_universities_proj': 'Top 5 universities and research centres by number of projects',
    // KEY FIGURES — Global Investments section
    'kf.heading_sub_inv':      'Who puts capital into defence and security companies, at a glance.',
    'kf.unit_holdings':        'holdings',
    'kf.unit_investors':       'investors',
    'kf.t_top_investors':      'Top 5 investors by number of holdings',
    'kf.t_public_investors':   'Top 5 public investors by number of holdings',
    'kf.t_most_backed':        'Top 5 companies by number of investors',
    'kf.t_investor_countries': 'Top 5 countries the capital comes from',
    'kf.t_dual_funded':        'Double funding: the top 5 of the {n} companies receiving both EDF money and private investment',
    'kf.scope_label':          'Scope',
    'kf.scope_defence':        'Defence tech only',
    'kf.scope_all':            'All entities',
    'kf.scope_count':          '{n} defence tech companies out of {tot} funded',
    'kf.caveat_scope':         'The "defence tech" scope is provisional. A company falls inside it if it takes part in EDF projects, if it is classified as defence in the database or in the Aerospace & Defence ETF, or if Crunchbase assigns it a military, aerospace, satellite or national security sector. Crunchbase labels are generic, so some companies slip through: Helsing is listed only as "Information Technology" and is included solely because it takes part in EDF projects. The criteria live in data/defence_criteria.json.',
    'kf.caveat_inv':           'Investment relationships in the database record the link between an investor and a company, not the amount invested. Every ranking on this page therefore counts holdings, not capital: it shows who is most present, not who spent the most. The count also reflects only what is documented in the database, not an investor\'s full portfolio.',

    // NETWORKS — sidebar
    'net.title':          'Defence Network',
    'net.find_entity':    'Find entity',
    'net.search_placeholder': 'Search organisations…',
    'net.country':        'Country',
    'net.relationships':  'Show data related to:',
    'net.actors':         'Actors',
    'net.connections':    'Connections',
    'net.note':           'This section lets you explore economic relationships between entities in the database.<br><br>You can filter to show only projects funded through EDF (European Defence Fund).<br><br>Diamond size = EU budget. Circles are uniform.<br>Click node → details + cross-country connections.<br>Click background → reset.',
    'net.note_edf':       'In this section you can explore the economic relationships between the entities in the database that have received European funding.<br><br>At the moment only EDF funds are detailed, but we are working to integrate other European funding programmes for the defence sector and, in particular, autonomous weapons.<br><br>The size of the diamond indicates the size of the budget planned for the project.',
    'net.in_view':        'In this view',
    'net.selected_node':  'Selected node',
    'net.select_country': 'Select a country to see stats.',
    'net.edf_tip':        'By checking "EDF projects" the system will show all entities that have received funding through the EDF programme (European Defence Fund), the relationships between them and the details of each individual project.',
    'net.inv_tip':        'By checking "Investments" the system will show all economic entities (listed companies, start-ups, funds, etc.) included in the database and the investment relationships between them.',

    // ABOUT — content
    'about.title':        'About',
    'about.intro':        'The Man in the Loop platform is developed by info.nodes, an Italian non-profit organisation founded in 2019, with financial support from <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, as part of the global programme "Militarisation of Tech".',
    'about.nav_about':      'About us',
    'about.nav_data':       'Methodology & data',
    'about.nav_glossary':   'Glossary',
    'about.nav_contribute': 'Contribute',
    'about.glossary_intro': 'The key terms used across the platform, explained in plain language.',
    'about.last_update_label': 'Last data update',
    'about.team_lead':    'The current prototype was developed by:',
    'about.team_list':    '<li>Davide Del Monte — Coordinator and Lead Researcher</li><li>Laura Carrer — Researcher</li><li>Andrea Daniele Signorelli — Researcher</li>',
    'about.collab':       'in collaboration with DATAPITCH:',
    'about.datapitch_list': '<li>Andrea Nelson Mauro — Developer and Data expert</li><li>Emma Besseghini — Junior Researcher</li>',
    'about.contribute_label': 'Contribute',
    'about.contribute_intro': 'We have done our best to verify the accuracy of the data on the platform, but it is a very complex task and our team has limited resources. That is why we ask you to help us in the following ways, if you would like to:',
    'about.contribute_list': '<li>Report any <strong>errors in the data or bugs</strong> you encounter while using the platform by writing to us at <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>Let us know about one or more <strong>companies</strong> you are interested in that are not currently in the database. Write to <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a> giving us the company name and, if possible, its identifier code and the URL of its official website.</li><li>Tell us about a <strong>publication</strong> of yours, if you used Man in the loop for your research or investigation. If you like, we will add it to the "Publications" section. Send your publication to <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>If you like the work we are doing and want to see it survive and grow in the future, make a donation to info.nodes using the "donate" button in the footer of <a href="https://www.infonodes.org" target="_blank" rel="noopener" style="color: var(--accent); text-decoration: none;">www.infonodes.org</a></li>',
    'about.data_label':   'The Man in the Loop data',
    'about.data_p1':      'This experimental open-data research project aims to map companies and investors in the autonomous weapons sector along the entire global supply chain.',
    'about.data_p2':      'For this prototype, we built a database of Wall Street-listed companies identified by sector using GICS codes (Global Industry Classification Standard):',
    'about.data_sectors': '<li>Mining sector: Materials, with focus on Metals &amp; Mining (GICS code 151040).</li><li>Tech sector: Information Technology (GICS code 45), Communication Services (GICS code 50).</li><li>Defence sector: Aerospace &amp; Defence (GICS code 201010).</li>',
    'about.data_p3':      'We also added 18 European start-ups deemed relevant in the sector. From this database, we extracted Lead Investor and Top Investor data from the paid platform Crunchbase.',
    'about.data_nota':    'NOTE: all information on the platform reflects the state at the time we downloaded data from Crunchbase (April 2026).',
    'about.eu_funding_label': 'Public funding for defence',
    'about.eu_funding_p1':    'We collected and added to the database all entities (companies, universities, research centres, public institutions) that participated in EDF (European Defence Fund) projects and therefore received, directly or indirectly, EU funds to research, develop, produce and commercialise autonomous weapon systems.',
    'about.eu_funding_p2':    'The EDF, however, is not the only channel through which public money reaches this sector. The <a href="./?mode=edf" style="color: var(--accent); text-decoration: none;">EU Funding</a> section carries a selector with eight programmes: alongside the EDF there are Horizon Europe, PESCO, EDIP, EUDIS and the Defence Equity Facility. For now <strong>only EDF data is available</strong>: the others are marked "work in progress" while we work on integrating them. We listed them from the outset because the scale of the phenomenon only becomes clear when you look at the funding channels together rather than one at a time.',
    'about.eu_funding_p3':    'Two entries in the selector — DIANA and the NATO Innovation Fund — are not EU programmes but NATO ones, which is why a line separates them from the rest. We include them because they fund the same actors towards comparable technological goals, even though they answer to a different governance and to a political perimeter wider than the EU\'s.',
    'about.limits_method_label': 'Methodological limitations',
    'about.limits_method': '<li><strong>No universally shared definition of "autonomous weapon"</strong> — the boundary between autonomous, semi-autonomous and remote-operated systems is still the subject of political and scientific debate. The companies included operate in sectors adjacent to that of autonomous weapons, but not all of them produce exclusively autonomous systems. Our research team identified what it considers the most correct and coherent definition. To explore the "terminology" question further, we suggest reading our report "AI: Seek &amp; Destroy", available in the <a href="publications.html" style="color: var(--accent); text-decoration: none;">Publications</a> section of this platform.</li><li><strong>Selection by stock-market sector (GICS)</strong> — the database primarily includes companies listed on Wall Street identified through GICS codes. This implies an over-representation of large listed companies and a possible under-representation of relevant actors not listed on the stock exchange.</li><li><strong>Partial supply chain</strong> — the autonomous-weapons supply chain is very long and branching. The database covers a significant but not exhaustive selection of the actors involved. Our goal, with successive releases, is to get as close as possible to completeness and exhaustiveness of the data. This will also require contributions from other experts and organisations: if you want to help, visit the <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribute</a> section to find out what you can do.<li><strong>The "defence tech" scope in the rankings</strong> — in the Key Figures of the Global Investments section the rankings show, by default, only the companies classified as defence tech: 165 of the 378 funded companies. The classification combines hard signals (participation in EDF projects, presence in the Aerospace &amp; Defence ETF, our own classification) with Crunchbase sector labels, which are generic: Helsing, for instance, appears there only as "Information Technology" and qualifies solely because it takes part in EDF projects. The scope is therefore provisional and errs on the side of leaving companies out. The selector lets you switch to "All entities" at any time and see the full database.</li></li>',
    'about.limits_data_label': 'Data limitations',
    'about.limits_data': '<li><strong>Crunchbase data: static snapshot</strong> — information on funding rounds, investors and corporate structure is updated to April 2026. Subsequent operations are not reflected in the database. One of our ambitions for the future is to raise sufficient resources to be able to access the Crunchbase API.</li><li><strong>Crunchbase data: uneven coverage</strong> — Crunchbase has excellent coverage of US tech/VC companies, but patchier coverage of traditional European defence companies, which often do not publish detailed data on investors.</li><li><strong>Lead Investor and Top Investor only</strong> — not all investors in every round are mapped, but only those classified by Crunchbase as lead or top. Minor or anonymous investors do not appear in our database.</li><li><strong>EDF data</strong> — for some participants in EDF projects the EU contribution received is not available in the official sources of the European Commission and therefore appears absent or partial.</li><li><strong>Unlisted private companies</strong> — start-ups and SMEs not listed on the stock exchange are included only if manually entered by the team or if they are participants in EDF projects. Their coverage is inevitably more limited. This is also why we ask the help of experts and organisations to flag other interesting entities to add to our database. In the <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribute</a> section you can find out how.</li><li><strong>Registered-office (country) data derived from third parties</strong> — the registered office of some entities was obtained from Crunchbase or Wikidata and may not reflect the actual legal structure (holding companies, subsidiaries, registered vs. operational office).</li><li><strong>Investments without amounts</strong> — investment relationships in the database record the link between an investor and a company, not the sum invested. The rankings in the Global Investments section therefore count holdings, not capital: they show who is most present, not who invested the most. The fundraising totals available on Crunchbase cannot be used for this, because they measure the capital a company raised overall and not the share attributable to defence.</li>',

    // PUBLICATIONS
    'pub.title':          'Research',
    'pub.desc':           'Research papers, articles and investigations produced by the Man in the Loop team or by researchers and journalists who used the platform in their work.',
    'pub.contact':        'If you want to share a publication made possible with MAN IN THE LOOP, write to us at:',

    // ONBOARDING overlay
    'onboard.subtitle':  'An open data database on the companies, investors and public bodies involved in the research and production of autonomous weapons.',
    'onboard.1_title':   '① Explore the Map',
    'onboard.1_desc':    'Every circle is a country. Click to discover the financial connections between investors and companies, or switch to EDF mode to see European Defence Fund financing country by country.',
    'onboard.2_title':   '② Search for an entity',
    'onboard.2_desc':    'The Search section contains profiles of all entities in the database: companies, universities, investors, etc.',
    'onboard.3_title':   '③ Analyse the Networks',
    'onboard.3_desc':    'The Networks section visualises the relationships between all actors: investments and collaborations. Check EDF to see all connections and entities funded by the European Defence Fund, with details of each individual project.',
    'onboard.cta':       'Start exploring →',

    // Common — export buttons
    'common.print':       'Print',
  },

  fr: {
    // Navigation
    'nav.map':          'Carte',
    'nav.networks':     'Réseaux',
    'nav.search':       'Recherche',
    'nav.publications': 'Publications',
    'nav.about':        'À propos',

    // MAP — default panel
    'map.section_title':  'Que trouver dans cette section',
    'map.intro':          'Cette page cartographie les principaux investissements transfrontaliers depuis un pays d\'origine vers des sociétés de pays tiers.',
    'map.dataset_stats':  'Le jeu de données couvre {countries} pays et {entities} entités, avec {arcs} connexions transfrontalières.',
    'map.circle_explanation': 'Chaque cercle représente un pays avec au moins une entité dans la base de données. La taille reflète le nombre de connexions. Sélectionnez un pays pour voir les arcs.',
    'map.how_to_read':    'Comment lire la carte',
    'map.arc_colors':     'Les arcs peuvent être de trois couleurs :',
    'map.arc_blue':       '<strong>Bleu</strong> : une entité du pays sélectionné a financé une société dans l\'autre pays.',
    'map.arc_red':        '<strong>Rouge</strong> : une société du pays sélectionné a reçu des financements d\'une entité de l\'autre pays.',
    'map.arc_purple':     '<strong>Violet</strong> : des flux financiers ont été enregistrés dans les deux sens entre les deux pays.',
    'map.arc_click':      'Cliquez sur un arc pour voir le détail des relations entre entités dans le panneau.',
    'map.our_data':       'Nos données',
    'map.data_source':    'Les données ont été collectées depuis Crunchbase, basées sur les sociétés de la filière des armes autonomes. {investors} entités disposent de données sur les investisseurs.',

    // MAP — toolbar
    'map.all_entities':   'Toutes les entités',
    'map.eu_funded':      'Financées UE seulement',
    'map.reset_zoom':     'Réinitialiser zoom',
    'map.about_this_map':    'À propos de la carte',
    'map.investments_title': 'Investments',
    'map.edf_title':         'Financements UE',
    'map.wip':               'work in progress',
    'map.edf_mode_desc':     'Cette carte montre les financements européens pour le développement d\'armements accordés à chaque État de l\'Union européenne et, en détail, à quelles de leurs entreprises, universités ou autres acteurs publics et privés.<br><br>Le diamètre des cercles est proportionnel au total des financements reçus par l\'État.<br><br>En cliquant sur le cercle correspondant à un pays, la liste de tous les acteurs ayant bénéficié de financements européens s\'affiche, avec le détail du montant perçu. Vous pouvez cliquer sur le nom de l\'acteur qui vous intéresse pour ouvrir sa fiche détaillée, contenant toutes les informations que nous avons pu collecter.<br><br>Grâce aux sélecteurs, vous pouvez choisir d\'afficher tous les types de financement public européen (EDF, Horizon, PESCO, etc.) ou seulement celui ou ceux qui vous intéressent.',
    'fin.info.EDF':     'Le FED (Fonds européen de la défense) aide les entreprises des différents États membres à développer des projets de défense compétitifs et collaboratifs, destinés à produire des technologies et des équipements militaires innovants et interopérables. Il offre soutien et conseil aux participants tout au long du cycle de recherche et développement.',
    'fin.info.HORIZON': 'Horizon Europe est le principal programme de financement de l\'UE pour la recherche et l\'innovation. Il favorise la collaboration et renforce l\'impact de la recherche et de l\'innovation dans l\'élaboration et la mise en œuvre des politiques européennes, tout en relevant les défis mondiaux. Il soutient la création et une meilleure diffusion de connaissances et de technologies d\'excellence.',
    'fin.info.PESCO':   'La CSP (Coopération structurée permanente, PESCO) est un cadre fondé sur les traités qui permet aux 26 États membres participants de planifier, développer et investir conjointement dans le développement collaboratif de capacités et de renforcer la disponibilité opérationnelle et la contribution des forces armées.',
    'fin.info.EDIP':    'L\'EDIP (Programme pour l\'industrie européenne de la défense) est une initiative de l\'UE de 1,5 milliard d\'euros visant à renforcer et moderniser l\'industrie européenne de la défense, à accroître la capacité de production et à garantir des technologies de pointe, la résilience et un approvisionnement constant en équipements militaires aux forces armées des États membres.',
    'fin.info.EUDIS':   'L\'EUDIS (Programme d\'innovation de défense de l\'UE) est un instrument rendu possible par le Fonds européen de la défense (FED) pour renforcer l\'innovation de défense dans l\'Union européenne.',
    'fin.info.EIF':     'Le Defence Equity Facility fournit des financements à des fonds privés qui investissent dans des entreprises développant des technologies et des produits de défense innovants. Cette initiative vise à stimuler le développement d\'un écosystème d\'investisseurs européens de la défense.',
    'fin.info.DIANA':   'DIANA (Accélérateur d\'innovation de défense pour l\'Atlantique Nord) est une organisation créée par l\'OTAN pour repérer et accélérer l\'innovation afin de fournir des capacités de défense et de sécurité à l\'Alliance.',
    'fin.info.NIF':     'Le NIF (NATO Innovation Fund) est un fonds de capital-risque autonome soutenu par 24 alliés de l\'OTAN, qui investit plus d\'un milliard d\'euros dans les deep tech.',
    'map.loading':           'Chargement des données…',

    // NAV — menu et sous-menu (« Search » et « About » restent en anglais partout)
    'nav.eu_funding':   'Financements UE',
    'nav.investments':  'Investissements mondiaux',
    'nav.publications': 'Publications',
    'nav.map':          'Carte',
    'nav.network':      'Réseau',
    'nav.key_figures':  'Chiffres clés',

    // KEY FIGURES
    'kf.heading':             'Les chiffres clés',
    'kf.heading_sub':         'Les financements européens au développement d\'armements, en résumé.',
    'kf.unit_projects':       'projets',
    'kf.t_countries_fund':    'Top 5 des pays par financements reçus',
    'kf.t_companies_fund':    'Top 5 des entreprises par financements reçus',
    'kf.t_companies_proj':    'Top 5 des entreprises par nombre de projets',
    'kf.t_universities_fund': 'Top 5 des universités et centres de recherche par financements reçus',
    'kf.t_universities_proj': 'Top 5 des universités et centres de recherche par nombre de projets',
    // KEY FIGURES — section Investissements mondiaux
    'kf.heading_sub_inv':      'Qui apporte les capitaux aux entreprises de la défense et de la sécurité, en résumé.',
    'kf.unit_holdings':        'participations',
    'kf.unit_investors':       'investisseurs',
    'kf.t_top_investors':      'Top 5 des investisseurs par nombre de participations',
    'kf.t_public_investors':   'Top 5 des investisseurs publics par nombre de participations',
    'kf.t_most_backed':        'Top 5 des entreprises par nombre d\'investisseurs',
    'kf.t_investor_countries': 'Top 5 des pays d\'origine des capitaux',
    'kf.t_dual_funded':        'Double financement : les 5 premières des {n} entreprises cumulant fonds EDF et investissements privés',
    'kf.scope_label':          'Périmètre',
    'kf.scope_defence':        'Defence tech uniquement',
    'kf.scope_all':            'Toutes les entités',
    'kf.scope_count':          '{n} entreprises defence tech sur {tot} financées',
    'kf.caveat_scope':         'Le périmètre « defence tech » est provisoire. Une entreprise y entre si elle participe à des projets EDF, si elle est classée dans la défense dans la base ou dans l\'ETF Aerospace & Defence, ou si Crunchbase lui attribue un secteur militaire, aérospatial, satellitaire ou de sécurité nationale. Les étiquettes Crunchbase sont génériques, donc certaines entreprises échappent au filtre : Helsing n\'est référencée que comme « Information Technology » et n\'est retenue que parce qu\'elle participe à des projets EDF. Les critères se trouvent dans data/defence_criteria.json.',
    'kf.caveat_inv':           'Les relations d\'investissement de la base enregistrent le lien entre un investisseur et une entreprise, pas le montant investi. Tous les classements de cette page comptent donc des participations, pas des capitaux : ils montrent qui est le plus présent, pas qui a le plus dépensé. Ce décompte ne reflète en outre que ce qui est documenté dans la base, et non l\'intégralité du portefeuille d\'un investisseur.',

    // NETWORKS — sidebar
    'net.title':          'Réseau de défense',
    'net.find_entity':    'Trouver une entité',
    'net.search_placeholder': 'Rechercher des organisations…',
    'net.country':        'Pays',
    'net.relationships':  'Afficher les données relatives à :',
    'net.actors':         'Acteurs',
    'net.connections':    'Connexions',
    'net.note':           'Cette section permet d\'explorer les relations économiques entre les entités de la base de données.<br><br>Vous pouvez filtrer pour n\'afficher que les projets financés par l\'EDF (Fonds européen de défense).<br><br>Taille du losange = budget UE. Les cercles sont uniformes.<br>Cliquez sur un nœud → détails + connexions transnationales.<br>Cliquez sur le fond → réinitialiser.',
    'net.note_edf':       'Dans cette section, vous pouvez explorer les relations économiques entre les acteurs présents dans la base de données qui ont reçu des financements européens.<br><br>Pour l\'instant, seul le détail des fonds EDF est disponible, mais nous travaillons à intégrer d\'autres programmes de financement européen du secteur de la défense et, en particulier, des armes autonomes.<br><br>La taille du losange indique la taille du budget prévu pour le projet.',
    'net.in_view':        'Dans cette vue',
    'net.selected_node':  'Nœud sélectionné',
    'net.select_country': 'Sélectionnez un pays pour voir les statistiques.',
    'net.edf_tip':        'En cochant "EDF projects", le système affichera toutes les entités ayant reçu des financements dans le cadre du programme EDF (Fonds européen de défense), les relations entre elles et les informations de chaque projet.',
    'net.inv_tip':        'En cochant "Investments", le système affichera toutes les entités économiques (sociétés cotées, start-ups, fonds, etc.) présentes dans la base de données et les relations d\'investissement entre elles.',

    // ABOUT — content
    'about.title':        'À propos',
    'about.intro':        'La plateforme Man in the Loop est développée par info.nodes, organisation à but non lucratif italienne fondée en 2019, grâce au soutien financier de <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, dans le cadre du programme mondial « Militarisation of Tech ».',
    'about.nav_about':      'Qui sommes-nous',
    'about.nav_data':       'Méthodologie et données',
    'about.nav_glossary':   'Glossaire',
    'about.nav_contribute': 'Contribuez',
    'about.glossary_intro': 'Les termes clés utilisés sur la plateforme, expliqués simplement.',
    'about.last_update_label': 'Dernière mise à jour des données',
    'about.team_lead':    'Le prototype actuel a été développé par :',
    'about.team_list':    '<li>Davide Del Monte — Coordinateur et chercheur principal</li><li>Laura Carrer — Chercheuse</li><li>Andrea Daniele Signorelli — Chercheur</li>',
    'about.collab':       'en collaboration avec DATAPITCH :',
    'about.datapitch_list': '<li>Andrea Nelson Mauro — Développeur et expert en données</li><li>Emma Besseghini — Chercheuse junior</li>',
    'about.contribute_label': 'Contribuez',
    'about.contribute_intro': 'Nous avons fait notre possible pour vérifier l\'exactitude des données présentes sur la plateforme, mais c\'est un travail très complexe et notre équipe dispose de ressources limitées. C\'est pourquoi nous vous demandons de nous aider des manières suivantes, si vous le souhaitez :',
    'about.contribute_list': '<li>Signalez-nous les <strong>erreurs dans les données ou les bugs</strong> que vous rencontrez en utilisant la plateforme, en nous écrivant à <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>Signalez-nous une ou plusieurs <strong>sociétés</strong> qui vous intéressent et qui ne figurent pas actuellement dans la base de données. Écrivez à <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a> en nous indiquant le nom de la société et, si possible, son code identifiant et l\'URL de son site internet officiel.</li><li>Signalez-nous une de vos <strong>publications</strong>, si vous avez utilisé Man in the loop pour une recherche ou une enquête. Si vous le souhaitez, nous l\'ajouterons à la section « Publications ». Envoyez votre publication à <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>Si vous appréciez le travail que nous menons et souhaitez le voir survivre et se développer à l\'avenir, faites un don à info.nodes en utilisant le bouton « faire un don » dans le pied de page du site <a href="https://www.infonodes.org" target="_blank" rel="noopener" style="color: var(--accent); text-decoration: none;">www.infonodes.org</a></li>',
    'about.data_label':   'Les données de Man in the Loop',
    'about.data_p1':      'Ce projet de recherche expérimental en open data vise à cartographier les entreprises et les investisseurs dans le secteur des armes autonomes, tout au long de la chaîne d\'approvisionnement mondiale.',
    'about.data_p2':      'Pour ce prototype, nous avons constitué une base de données comprenant les sociétés cotées à la Bourse de Wall Street, identifiées par secteur à l\'aide des codes GICS :',
    'about.data_sectors': '<li>Secteur minier : Materials, avec focus sur Metals &amp; Mining (Code GICS 151040).</li><li>Secteur Tech : Information Technology (Code GICS 45), Communication Services (Code GICS 50).</li><li>Secteur de la défense : Aerospace &amp; Defence (Code GICS 201010).</li>',
    'about.data_p3':      'Nous avons également ajouté 18 start-ups européennes jugées pertinentes dans le secteur. À partir de cette base de données, nous avons extrait les données relatives aux Lead Investors et Top Investors depuis la plateforme payante Crunchbase.',
    'about.data_nota':    'NOTE : toutes les informations présentes sur la plateforme reflètent l\'état au moment du téléchargement depuis Crunchbase (avril 2026).',
    'about.eu_funding_label': 'Les financements publics à la défense',
    'about.eu_funding_p1':    'Nous avons collecté et ajouté à la base de données toutes les entités (sociétés, universités, centres de recherche, institutions publiques) ayant participé à des projets EDF (Fonds européen de défense) et ayant donc reçu, directement ou indirectement, des fonds de l\'Union européenne pour la recherche, le développement, la production et la commercialisation de systèmes d\'armes autonomes.',
    'about.eu_funding_p2':    'Le FED n\'est cependant pas le seul canal par lequel l\'argent public parvient à ce secteur. La section <a href="./?mode=edf" style="color: var(--accent); text-decoration: none;">Financements UE</a> propose un sélecteur avec huit programmes : outre le FED, on y trouve Horizon Europe, la CSP (PESCO), l\'EDIP, l\'EUDIS et le Defence Equity Facility. Pour l\'instant, <strong>seules les données EDF sont disponibles</strong> : les autres portent la mention « work in progress », car nous travaillons à les intégrer. Nous les avons listés dès maintenant parce que l\'ampleur du phénomène n\'apparaît qu\'en regardant l\'ensemble des canaux de financement, et non un seul.',
    'about.eu_funding_p3':    'Deux entrées du sélecteur — DIANA et le NATO Innovation Fund — ne sont pas des programmes de l\'Union européenne mais de l\'OTAN, d\'où la ligne qui les sépare des autres. Nous les incluons parce qu\'ils financent les mêmes acteurs avec des objectifs technologiques comparables, tout en relevant d\'une gouvernance différente et d\'un périmètre politique plus large que celui de l\'UE.',
    'about.limits_method_label': 'Limites méthodologiques',
    'about.limits_method': '<li><strong>Absence de définition universellement partagée de « arme autonome »</strong> — la frontière entre système autonome, semi-autonome et téléopéré est encore au cœur d\'un débat politique et scientifique. Les entreprises incluses opèrent dans des secteurs contigus à celui des armes autonomes, mais toutes ne produisent pas exclusivement des systèmes autonomes. Notre équipe de recherche a identifié la définition qu\'elle juge la plus correcte et la plus cohérente. Pour approfondir la question « terminologique », nous vous suggérons de lire notre rapport « AI : Seek &amp; Destroy », disponible dans la section <a href="publications.html" style="color: var(--accent); text-decoration: none;">Publications</a> de cette plateforme.</li><li><strong>Sélection par secteur boursier (GICS)</strong> — la base de données comprend principalement des sociétés cotées à Wall Street identifiées au moyen de codes GICS. Cela implique une surreprésentation des grandes sociétés cotées et une possible sous-représentation d\'acteurs pertinents non cotés en bourse.</li><li><strong>Chaîne d\'approvisionnement partielle</strong> — la chaîne d\'approvisionnement des armes autonomes est très longue et ramifiée. La base de données couvre une sélection significative, mais non exhaustive, des acteurs impliqués. Notre objectif, avec les versions successives, est de nous rapprocher le plus possible de l\'exhaustivité des données. Cela nécessitera également la contribution d\'autres experts et organisations : si vous souhaitez nous aider, consultez la section <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribuer</a> pour découvrir ce que vous pouvez faire.<li><strong>Le périmètre « defence tech » dans les classements</strong> — dans les Chiffres clés de la section Investissements mondiaux, les classements n&#39;affichent par défaut que les entreprises classées defence tech : 165 des 378 entreprises financées. La classification combine des signaux sûrs (participation à des projets EDF, présence dans l&#39;ETF Aerospace &amp; Defence, classement interne) et les étiquettes sectorielles de Crunchbase, qui sont génériques : Helsing, par exemple, n&#39;y figure que comme "Information Technology" et n&#39;est retenue que parce qu&#39;elle participe à des projets EDF. Le périmètre est donc provisoire et pèche par défaut. Le sélecteur permet à tout moment de basculer sur « Toutes les entités » et de voir la base complète.</li></li>',
    'about.limits_data_label': 'Limites des données',
    'about.limits_data': '<li><strong>Données Crunchbase : photographie statique</strong> — les informations sur les tours de financement, les investisseurs et la structure sociétaire sont mises à jour en avril 2026. Les opérations postérieures ne sont pas reflétées dans la base de données. L\'une de nos ambitions pour l\'avenir est de rassembler des ressources sufficiantes pour pouvoir accéder aux API de Crunchbase.</li><li><strong>Données Crunchbase : couverture non uniforme</strong> — Crunchbase offre une excellente couverture des entreprises tech/VC américaines, mais une couverture plus lacunaire des entreprises de défense européennes traditionnelles, qui publient souvent peu de données détaillées sur leurs investisseurs.</li><li><strong>Lead Investor et Top Investor uniquement</strong> — tous les investisseurs de chaque tour ne sont pas cartographiés, seulement ceux classés par Crunchbase comme lead ou top. Les investisseurs mineurs ou anonymes n\'apparaissent pas dans notre base de données.</li><li><strong>Données EDF</strong> — pour certains participants aux projets EDF, la contribution de l\'UE reçue n\'est pas disponible dans les sources officielles de la Commission européenne et apparaît donc absente ou partielle.</li><li><strong>Sociétés privées non cotées</strong> — les start-up et PME non cotées en bourse ne sont présentes que si elles ont été saisies manuellement par l\'équipe ou si elles participent à des projets EDF. Leur couverture est inévitablement plus limitée. C\'est aussi pourquoi nous sollicitons l\'aide d\'experts et d\'organisations pour nous signaler d\'autres entités intéressantes à ajouter à notre base de données. Dans la section <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribuer</a>, vous pouvez découvrir comment procéder.</li><li><strong>Données relatives au siège (pays) issues de tiers</strong> — le siège de certaines entités a été obtenu auprès de Crunchbase ou de Wikidata et peut ne pas refléter la structure juridique effective (holdings, filiales, siège fiscal vs. siège opérationnel).</li><li><strong>Des investissements sans montant</strong> — les relations d’investissement de la base enregistrent le lien entre un investisseur et une entreprise, pas la somme versée. Les classements de la section Investissements mondiaux comptent donc des participations, pas des capitaux : ils indiquent qui est le plus présent, pas qui a le plus investi. Les montants de levée disponibles sur Crunchbase ne peuvent pas servir à cela, car ils mesurent le capital levé globalement par une entreprise et non la part imputable à la défense.</li>',

    // PUBLICATIONS
    'pub.title':          'Recherche',
    'pub.desc':           'Recherches, articles et enquêtes produits par l\'équipe du projet Man in the Loop ou par des chercheurs et journalistes ayant utilisé la plateforme.',
    'pub.contact':        'Si vous souhaitez nous signaler une publication réalisée grâce à MAN IN THE LOOP, écrivez-nous à :',

    // ONBOARDING overlay
    'onboard.subtitle':  'Une base de données open data sur les entreprises, les investisseurs et les organismes publics impliqués dans la recherche et la production d\'armes autonomes.',
    'onboard.1_title':   '① Explorer la Carte',
    'onboard.1_desc':    'Chaque cercle représente un pays. Cliquez pour découvrir les connexions financières entre investisseurs et entreprises, ou passez en mode EDF pour voir les financements du Fonds européen de défense pays par pays.',
    'onboard.2_title':   '② Rechercher une entité',
    'onboard.2_desc':    'La section Search contient les fiches de toutes les entités de la base de données : sociétés, universités, investisseurs, etc.',
    'onboard.3_title':   '③ Analyser les Réseaux',
    'onboard.3_desc':    'La section Networks visualise les relations entre tous les acteurs : investissements et collaborations. Cochez EDF pour voir toutes les connexions et les entités financées par le Fonds européen de défense, avec le détail de chaque projet.',
    'onboard.cta':       'Commencer à explorer →',

    // Common — export buttons
    'common.print':       'Imprimer',
  },

  es: {
    // Navigation
    'nav.map':          'Mapa',
    'nav.networks':     'Redes',
    'nav.search':       'Búsqueda',
    'nav.publications': 'Publicaciones',
    'nav.about':        'Acerca de',

    // MAP — default panel
    'map.section_title':  'Qué encontrar en esta sección',
    'map.intro':          'Esta página muestra las inversiones transfronterizas más relevantes desde el país de origen hacia empresas de terceros países.',
    'map.dataset_stats':  'El conjunto de datos cubre {countries} países y {entities} entidades, con {arcs} conexiones transfronterizas.',
    'map.circle_explanation': 'Cada círculo representa un país con al menos una entidad en la base de datos. El tamaño refleja el número de conexiones. Seleccione un país para ver los arcos.',
    'map.how_to_read':    'Cómo leer el mapa',
    'map.arc_colors':     'Los arcos pueden ser de tres colores:',
    'map.arc_blue':       '<strong>Azul</strong>: una entidad del país seleccionado ha financiado una empresa en el otro país.',
    'map.arc_red':        '<strong>Rojo</strong>: una empresa del país seleccionado ha recibido inversión de una entidad del otro país.',
    'map.arc_purple':     '<strong>Morado</strong>: se han registrado flujos de inversión en ambas direcciones entre los dos países.',
    'map.arc_click':      'Haga clic en un arco para ver el detalle de las relaciones entre entidades en el panel.',
    'map.our_data':       'Nuestros datos',
    'map.data_source':    'Los datos fueron recopilados de Crunchbase, basados en empresas de la cadena de suministro de armas autónomas. {investors} entidades disponen de datos de inversores.',

    // MAP — toolbar
    'map.all_entities':   'Todas las entidades',
    'map.eu_funded':      'Solo financiadas UE',
    'map.reset_zoom':     'Restablecer zoom',
    'map.about_this_map':    'Acerca del mapa',
    'map.investments_title': 'Investments',
    'map.edf_title':         'Financiación UE',
    'map.wip':               'work in progress',
    'map.edf_mode_desc':     'Este mapa muestra la financiación europea para el desarrollo de armamento concedida a cada Estado de la Unión Europea y, en detalle, a qué empresas, universidades u otros actores públicos y privados suyos.<br><br>El diámetro de los círculos es proporcional al total de la financiación recibida por el Estado.<br><br>Al hacer clic en el círculo correspondiente a un país se abrirá la lista de todos los actores que han recibido financiación europea, con el detalle del importe recibido. Puedes hacer clic en el nombre del actor que te interese para abrir su ficha de detalle, con toda la información que hemos podido recopilar.<br><br>Gracias a los selectores, puedes elegir ver todos los tipos de financiación pública europea (EDF, Horizon, PESCO, etc.) o solo el que o los que te interesen.',
    'fin.info.EDF':     'El FED (Fondo Europeo de Defensa) apoya a las empresas de los distintos Estados miembros en el desarrollo de proyectos de defensa competitivos y colaborativos, capaces de generar tecnologías y equipos militares innovadores e interoperables. Ofrece apoyo y asesoramiento a los participantes a lo largo de todo el ciclo de investigación y desarrollo.',
    'fin.info.HORIZON': 'Horizon Europe es el principal programa de financiación de la UE para la investigación y la innovación. Favorece la colaboración y refuerza el impacto de la investigación y la innovación en el desarrollo y la aplicación de las políticas europeas, afrontando al mismo tiempo los desafíos globales. Apoya la creación y una mejor difusión de conocimientos y tecnologías de excelencia.',
    'fin.info.PESCO':   'La PESCO (Cooperación Estructurada Permanente) es un marco basado en los tratados que permite a los 26 Estados miembros participantes planificar, desarrollar e invertir conjuntamente en el desarrollo colaborativo de capacidades y reforzar la preparación operativa y la contribución de las fuerzas armadas.',
    'fin.info.EDIP':    'El EDIP (Programa de la Industria Europea de Defensa) es una iniciativa de la UE de 1.500 millones de euros para reforzar y modernizar la industria europea de defensa, aumentar la capacidad de producción y garantizar tecnología de vanguardia, resiliencia y un suministro constante de equipos militares a las fuerzas armadas de los Estados miembros.',
    'fin.info.EUDIS':   'El EUDIS (Programa de Innovación en Defensa de la UE) es un instrumento habilitado por el Fondo Europeo de Defensa (FED) para reforzar la innovación en defensa en la Unión Europea.',
    'fin.info.EIF':     'El Defence Equity Facility proporciona financiación a fondos privados que invierten en empresas que desarrollan tecnologías y productos de defensa innovadores. Esta iniciativa pretende estimular el desarrollo de un ecosistema de inversores europeos de defensa.',
    'fin.info.DIANA':   'DIANA (Acelerador de Innovación en Defensa para el Atlántico Norte) es una organización creada por la OTAN para detectar y acelerar la innovación con el fin de proporcionar capacidades de defensa y seguridad a la Alianza.',
    'fin.info.NIF':     'El NIF (NATO Innovation Fund) es un fondo de capital riesgo autónomo respaldado por 24 aliados de la OTAN, que invierte más de 1.000 millones de euros en tecnologías deep tech.',
    'map.loading':           'Cargando datos del mapa…',

    // NAV — menú y submenú («Search» y «About» permanecen en inglés en todas las lenguas)
    'nav.eu_funding':   'Financiación UE',
    'nav.investments':  'Inversiones globales',
    'nav.publications': 'Publicaciones',
    'nav.map':          'Mapa',
    'nav.network':      'Red',
    'nav.key_figures':  'Cifras clave',

    // KEY FIGURES
    'kf.heading':             'Las cifras clave',
    'kf.heading_sub':         'La financiación europea al desarrollo de armamento, en síntesis.',
    'kf.unit_projects':       'proyectos',
    'kf.t_countries_fund':    'Top 5 países por financiación recibida',
    'kf.t_companies_fund':    'Top 5 empresas por financiación recibida',
    'kf.t_companies_proj':    'Top 5 empresas por número de proyectos',
    'kf.t_universities_fund': 'Top 5 universidades y centros de investigación por financiación recibida',
    'kf.t_universities_proj': 'Top 5 universidades y centros de investigación por número de proyectos',
    // KEY FIGURES — sección Inversiones globales
    'kf.heading_sub_inv':      'Quién aporta capital a las empresas de defensa y seguridad, en síntesis.',
    'kf.unit_holdings':        'participaciones',
    'kf.unit_investors':       'inversores',
    'kf.t_top_investors':      'Top 5 inversores por número de participaciones',
    'kf.t_public_investors':   'Top 5 inversores públicos por número de participaciones',
    'kf.t_most_backed':        'Top 5 empresas por número de inversores',
    'kf.t_investor_countries': 'Top 5 países de origen de los capitales',
    'kf.t_dual_funded':        'Doble financiación: las 5 primeras de las {n} empresas que reciben fondos EDF e inversión privada',
    'kf.scope_label':          'Perímetro',
    'kf.scope_defence':        'Solo defence tech',
    'kf.scope_all':            'Todas las entidades',
    'kf.scope_count':          '{n} empresas defence tech de {tot} participadas',
    'kf.caveat_scope':         'El perímetro «defence tech» es provisional. Una empresa entra en él si participa en proyectos EDF, si está clasificada como defensa en la base o en el ETF Aerospace & Defence, o si Crunchbase le asigna un sector militar, aeroespacial, satelital o de seguridad nacional. Las etiquetas de Crunchbase son genéricas, así que alguna empresa se escapa: Helsing figura solo como «Information Technology» y entra únicamente porque participa en proyectos EDF. Los criterios están en data/defence_criteria.json.',
    'kf.caveat_inv':           'Las relaciones de inversión de la base registran el vínculo entre un inversor y una empresa, no el importe invertido. Todas las clasificaciones de esta página cuentan por tanto participaciones, no capitales: muestran quién está más presente, no quién ha gastado más. El recuento refleja además solo lo documentado en la base, no la cartera completa de un inversor.',

    // NETWORKS — sidebar
    'net.title':          'Red de defensa',
    'net.find_entity':    'Buscar entidad',
    'net.search_placeholder': 'Buscar organizaciones…',
    'net.country':        'País',
    'net.relationships':  'Mostrar datos relativos a:',
    'net.actors':         'Actores',
    'net.connections':    'Conexiones',
    'net.note':           'Esta sección permite explorar las relaciones económicas entre los sujetos de la base de datos.<br><br>Es posible visualizar solo los proyectos financiados a través del EDF (Fondo Europeo de Defensa).<br><br>Tamaño del rombo = presupuesto UE. Los círculos son uniformes.<br>Haz clic en el nodo → detalles + conexiones transnacionales.<br>Haz clic en el fondo → restablecer.',
    'net.note_edf':       'En esta sección puedes explorar las relaciones económicas entre los actores presentes en la base de datos que han recibido financiación europea.<br><br>Por el momento solo está disponible el detalle de los fondos EDF, pero estamos trabajando para integrar también otros programas de financiación europea del sector de la defensa y, en particular, de las armas autónomas.<br><br>El tamaño del rombo indica el tamaño del presupuesto previsto para el proyecto.',
    'net.in_view':        'En esta vista',
    'net.selected_node':  'Nodo seleccionado',
    'net.select_country': 'Seleccione un país para ver estadísticas.',
    'net.edf_tip':        'Al marcar "EDF projects", el sistema mostrará todas las entidades que han recibido financiación a través del programa EDF (Fondo Europeo de Defensa), las relaciones entre ellas y la información de cada proyecto.',
    'net.inv_tip':        'Al marcar "Investments", el sistema mostrará todas las entidades económicas (empresas cotizadas, start-ups, fondos, etc.) incluidas en la base de datos y las relaciones de inversión entre ellas.',

    // ABOUT — content
    'about.title':        'Acerca de',
    'about.intro':        'La plataforma Man in the Loop es desarrollada por info.nodes, organización sin ánimo de lucro italiana fundada en 2019, gracias al apoyo económico de <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, en el marco del programa global «Militarisation of Tech».',
    'about.nav_about':      'Quiénes somos',
    'about.nav_data':       'Metodología y datos',
    'about.nav_glossary':   'Glosario',
    'about.nav_contribute': 'Contribuye',
    'about.glossary_intro': 'Los términos clave utilizados en la plataforma, explicados de forma sencilla.',
    'about.last_update_label': 'Última actualización de datos',
    'about.team_lead':    'El prototipo actual fue desarrollado por:',
    'about.team_list':    '<li>Davide Del Monte — Coordinador e investigador principal</li><li>Laura Carrer — Investigadora</li><li>Andrea Daniele Signorelli — Investigador</li>',
    'about.collab':       'en colaboración con DATAPITCH:',
    'about.datapitch_list': '<li>Andrea Nelson Mauro — Desarrollador y experto en datos</li><li>Emma Besseghini — Investigadora junior</li>',
    'about.contribute_label': 'Contribuye',
    'about.contribute_intro': 'Hemos hecho todo lo posible por verificar la exactitud de los datos incluidos en la plataforma, pero es un trabajo muy complejo y nuestro equipo dispone de recursos limitados. Por eso te pedimos que nos eches una mano de las siguientes maneras, si te apetece:',
    'about.contribute_list': '<li>Avísanos de los <strong>errores en los datos o de los bugs</strong> que encuentres al usar la plataforma, escribiéndonos a <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>Indícanos una o más <strong>empresas</strong> que te interesen y que actualmente no estén en la base de datos. Escribe a <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a> indicándonos el nombre de la empresa y, si es posible, su código identificativo y la URL de su sitio web oficial.</li><li>Cuéntanos una <strong>publicación</strong> tuya, si has utilizado Man in the loop para una investigación o reportaje. Si te apetece, la añadiremos a la sección "Publicaciones". Envía tu publicación a <a href="mailto:comunicazione@infonodes.org" style="color: var(--accent); text-decoration: none;">comunicazione@infonodes.org</a></li><li>Si te gusta el trabajo que estamos haciendo y quieres verlo sobrevivir y crecer en el futuro, haz una donación a info.nodes utilizando el botón "donar" en el pie de página del sitio <a href="https://www.infonodes.org" target="_blank" rel="noopener" style="color: var(--accent); text-decoration: none;">www.infonodes.org</a></li>',
    'about.data_label':   'Los datos de Man in the Loop',
    'about.data_p1':      'Este proyecto de investigación experimental de datos abiertos tiene como objetivo mapear las empresas e inversores en el sector de las armas autónomas a lo largo de toda la cadena de suministro global.',
    'about.data_p2':      'Para este prototipo, hemos construido una base de datos con sociedades cotizadas en la bolsa de Wall Street, identificadas por sector mediante los códigos GICS:',
    'about.data_sectors': '<li>Sector minero: Materials, con foco en Metals &amp; Mining (Código GICS 151040).</li><li>Sector Tech: Information Technology (Código GICS 45), Communication Services (Código GICS 50).</li><li>Sector de la defensa: Aerospace &amp; Defence (Código GICS 201010).</li>',
    'about.data_p3':      'También añadimos 18 start-ups europeas consideradas relevantes en el sector. A partir de esta base de datos, extrajimos los datos de Lead Investors y Top Investors de la plataforma de pago Crunchbase.',
    'about.data_nota':    'NOTA: toda la información presente en las secciones de la plataforma refleja el estado en el momento en que descargamos los datos de Crunchbase (abril de 2026).',
    'about.eu_funding_label': 'La financiación pública a la defensa',
    'about.eu_funding_p1':    'Hemos recopilado e introducido en la base de datos todas las entidades (empresas, universidades, centros de investigación, instituciones públicas) que han participado en proyectos EDF (Fondo Europeo de Defensa) y que por tanto han recibido, directa o indirectamente, fondos de la Unión Europea para investigar, desarrollar, producir y comercializar sistemas de armas autónomas.',
    'about.eu_funding_p2':    'El EDF, sin embargo, no es el único canal por el que el dinero público llega a este sector. En la sección <a href="./?mode=edf" style="color: var(--accent); text-decoration: none;">Financiación UE</a> hay un selector con ocho programas: además del EDF están Horizon Europe, PESCO, EDIP, EUDIS y el Defence Equity Facility. Por ahora <strong>solo están disponibles los datos del EDF</strong>: los demás aparecen como «work in progress» porque estamos trabajando para integrarlos. Los hemos enumerado desde el principio porque la dimensión del fenómeno solo se capta mirando el conjunto de los canales de financiación, no uno solo.',
    'about.eu_funding_p3':    'Dos de las entradas del selector — DIANA y el NATO Innovation Fund — no son programas de la Unión Europea sino de la OTAN, y por eso una línea las separa de las demás. Las incluimos porque financian a los mismos actores con objetivos tecnológicos análogos, aunque respondan a una gobernanza distinta y a un perímetro político más amplio que el comunitario.',
    'about.limits_method_label': 'Limitaciones metodológicas',
    'about.limits_method': '<li><strong>Ausencia de una definición universalmente compartida de «arma autónoma»</strong> — la frontera entre sistema autónomo, semiautónomo y teledirigido sigue siendo objeto de debate político y científico. Las empresas incluidas operan en sectores contiguos al de las armas autónomas, pero no todas producen exclusivamente sistemas autónomos. Nuestro equipo de investigación ha identificado la que considera más correcta y coherente. Para profundizar en la cuestión «terminológica», le sugerimos que lea nuestro informe «AI: Seek &amp; Destroy», disponible en la sección <a href="publications.html" style="color: var(--accent); text-decoration: none;">Publicaciones</a> de esta plataforma.</li><li><strong>Selección por sector bursátil (GICS)</strong> — la base de datos incluye principalmente empresas cotizadas en Wall Street identificadas mediante códigos GICS. Esto implica una sobrerrepresentación de las grandes empresas cotizadas y una posible infrarrepresentación de actores relevantes no cotizados en bolsa.</li><li><strong>Cadena de suministro parcial</strong> — la cadena de suministro de las armas autónomas es muy larga y ramificada. La base de datos cubre una selección significativa pero no exhaustiva de los actores implicados. Nuestro objetivo, con versiones sucesivas, es acercarnos lo más posible a la exhaustividad de los datos. Para ello también será necesaria la contribución de otros expertos y organizaciones: si deseas ayudarnos, visita la sección <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribuye</a> para descubrir qué puedes hacer.<li><strong>El perímetro «defence tech» en las clasificaciones</strong> — en las Cifras clave de la sección Inversiones globales las clasificaciones muestran por defecto solo las empresas clasificadas como defence tech: 165 de las 378 empresas participadas. La clasificación combina señales seguras (participación en proyectos EDF, presencia en el ETF Aerospace &amp; Defence, clasificación interna) con las etiquetas sectoriales de Crunchbase, que son genéricas: Helsing, por ejemplo, figura allí solo como "Information Technology" y entra únicamente porque participa en proyectos EDF. El perímetro es por tanto provisional y tiende a excluir por defecto. El selector permite en cualquier momento pasar a «Todas las entidades» y ver la base completa.</li></li>',
    'about.limits_data_label': 'Limitaciones de los datos',
    'about.limits_data': '<li><strong>Datos de Crunchbase: fotografía estática</strong> — la información sobre rondas de financiación, inversores y estructura societaria está actualizada a abril de 2026. Las operaciones posteriores no se reflejan en la base de datos. Una de nuestras ambiciones para el futuro es reunir recursos suficientes para poder acceder a las API de Crunchbase.</li><li><strong>Datos de Crunchbase: cobertura no uniforme</strong> — Crunchbase tiene una cobertura excelente de las empresas tech/VC estadounidenses, pero más deficiente en el caso de las empresas europeas tradicionales del sector defensa, que a menudo no publican datos detallados sobre sus inversores.</li><li><strong>Solo Lead Investor y Top Investor</strong> — no se mapean todos los inversores de cada ronda, sino únicamente los clasificados por Crunchbase como lead o top. Los inversores menores o anónimos no aparecen en nuestra base de datos.</li><li><strong>Datos EDF</strong> — para algunos participantes en proyectos EDF, la contribución de la UE recibida no está disponible en las fuentes oficiales de la Comisión Europea y, por lo tanto, aparece ausente o parcial.</li><li><strong>Empresas privadas no cotizadas</strong> — las start-ups y pymes no cotizadas en bolsa solo están presentes si han sido introducidas manualmente por el equipo o si participan en proyectos EDF. Su cobertura es inevitablemente más limitada. También por ello pedimos la ayuda de expertos y organizaciones para que nos indiquen otras entidades interesantes que añadir a nuestra base de datos. En la sección <a href="about.html#contribute" style="color: var(--accent); text-decoration: none;">Contribuye</a> puedes descubrir cómo hacerlo.</li><li><strong>Datos sobre la sede (país) obtenidos de terceros</strong> — la sede de algunas entidades se ha obtenido de Crunchbase o Wikidata y puede no reflejar la estructura jurídica efectiva (holdings, filiales, sede fiscal frente a sede operativa).</li><li><strong>Inversiones sin importe</strong> — las relaciones de inversión de la base registran el vínculo entre un inversor y una empresa, no la cantidad aportada. Las clasificaciones de la sección Inversiones globales cuentan por tanto participaciones, no capitales: indican quién está más presente, no quién ha invertido más. Los importes de captación disponibles en Crunchbase no sirven para ello, porque miden el capital captado en total por una empresa y no la parte atribuible a la defensa.</li>',

    // PUBLICATIONS
    'pub.title':          'Investigación',
    'pub.desc':           'Investigaciones, artículos e informes producidos por el equipo del proyecto Man in the Loop o por investigadores y periodistas que han utilizado la plataforma.',
    'pub.contact':        'Si quieres compartir una publicación realizada gracias a MAN IN THE LOOP, escríbenos a:',

    // ONBOARDING overlay
    'onboard.subtitle':  'Una base de datos open data sobre las empresas, los inversores y los organismos públicos involucrados en la investigación y producción de armas autónomas.',
    'onboard.1_title':   '① Explorar el Mapa',
    'onboard.1_desc':    'Cada círculo es un país. Haz clic para descubrir las conexiones financieras entre inversores y empresas, o cambia al modo EDF para ver la financiación del Fondo Europeo de Defensa país por país.',
    'onboard.2_title':   '② Buscar una entidad',
    'onboard.2_desc':    'La sección Search contiene las fichas de todas las entidades de la base de datos: empresas, universidades, inversores, etc.',
    'onboard.3_title':   '③ Analizar las Redes',
    'onboard.3_desc':    'La sección Networks visualiza las relaciones entre todos los actores: inversiones y colaboraciones. Marca EDF para ver todas las conexiones y las entidades financiadas por el Fondo Europeo de Defensa, con el detalle de cada proyecto.',
    'onboard.cta':       'Empezar a explorar →',

    // Common — export buttons
    'common.print':       'Imprimir',
  },
};

// ── State ─────────────────────────────────────────────────────────────────────
const _LANG_KEY = 'mitl-lang';
const _SUPPORTED = ['it', 'en', 'fr', 'es'];
let _currentLang = 'it';

// ── Core helpers ──────────────────────────────────────────────────────────────

function t(key, vars) {
  const dict = TRANSLATIONS[_currentLang] || TRANSLATIONS['it'];
  let str = dict[key] ?? TRANSLATIONS['it'][key] ?? key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      str = str.replaceAll(`{${k}}`, v);
    }
  }
  return str;
}

function setLang(lang) {
  if (!_SUPPORTED.includes(lang)) return;
  _currentLang = lang;
  localStorage.setItem(_LANG_KEY, lang);
  _updateURL(lang);
  _applyDOM();
  _syncLangBtns();
  _patchNavLinks();
  document.dispatchEvent(new CustomEvent('mitl-lang-change', { detail: { lang } }));
}

// ── URL helpers ───────────────────────────────────────────────────────────────

function _getLangFromURL() {
  const p = new URLSearchParams(location.search);
  const v = p.get('lang');
  return _SUPPORTED.includes(v) ? v : null;
}

function _updateURL(lang) {
  const url = new URL(location.href);
  url.searchParams.set('lang', lang);
  history.replaceState(history.state, '', url);
}

// Keep lang param on all tabnav and subnav links so navigation preserves the language
function _patchNavLinks() {
  document.querySelectorAll('a.tnav-btn, a.snav-btn').forEach(a => {
    const href = a.getAttribute('href');
    if (!href || href.startsWith('#')) return;
    const url = new URL(href, location.href);
    url.searchParams.set('lang', _currentLang);
    a.setAttribute('href', url.pathname + url.search);
  });
}

// ── DOM application ───────────────────────────────────────────────────────────

function _applyDOM() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    el.innerHTML = t(el.getAttribute('data-i18n-html'));
  });
  document.querySelectorAll('[data-i18n-attr]').forEach(el => {
    for (const pair of el.getAttribute('data-i18n-attr').split(',')) {
      const [attr, key] = pair.trim().split(':');
      if (attr && key) el.setAttribute(attr, t(key));
    }
  });
}

function _syncLangBtns() {
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-lang') === _currentLang);
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────

function _initLang() {
  const fromURL     = _getLangFromURL();
  const fromStorage = localStorage.getItem(_LANG_KEY);
  _currentLang = fromURL || (_SUPPORTED.includes(fromStorage) ? fromStorage : 'it');
  if (fromURL) localStorage.setItem(_LANG_KEY, _currentLang);
  _updateURL(_currentLang);
  _applyDOM();
  _syncLangBtns();
  _patchNavLinks();
}

document.addEventListener('DOMContentLoaded', _initLang);
