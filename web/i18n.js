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
    'map.reset_zoom':     'Reset zoom',
    'map.about_this_map': 'About this map',
    'map.loading':        'Loading map data…',

    // NETWORKS — sidebar
    'net.title':          'Defence Network',
    'net.find_entity':    'Find entity',
    'net.search_placeholder': 'Search organisations…',
    'net.country':        'Country',
    'net.relationships':  'Relationships',
    'net.actors':         'Actors',
    'net.connections':    'Connections',
    'net.note':           'In questa sezione è possibile esplorare le relazioni economiche tra i soggetti presenti nel database.<br><br>È possibile visualizzare i soli progetti finanziati attraverso EDF (European Defence Funds).<br><br>Dimensione del rombo = bilancio UE. I cerchi sono uniformi.<br>Clicca sul nodo → dettagli + collegamenti transnazionali.<br>Clicca sullo sfondo → ripristina.',
    'net.in_view':        'In this view',
    'net.selected_node':  'Selected node',
    'net.select_country': 'Select a country to see stats.',
    'net.edf_tip':        'Flaggando "EDF projects" il sistema mostrerà tutti i soggetti che hanno ricevuto finanziamenti attraverso il programma EDF (European Defence Fund), le relazioni fra loro e le informazioni di ogni singolo progetto.',
    'net.inv_tip':        'Flaggando "Investments" il sistema mostrerà tutti i soggetti economici (società quotate, start-up, fondi, etc...) che abbiamo inserito nel database e le relazioni fra loro in termini di investimento.',

    // ABOUT — content
    'about.title':        'About',
    'about.intro':        'La piattaforma Man in the Loop è sviluppata da info.nodes, organizzazione no-profit italiana fondata nel 2019, grazie al supporto economico di <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, nell\'ambito del programma globale "Militarisation of Tech".',
    'about.last_update':  'Ultimo aggiornamento dati: 16/06/2026',
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
    'about.edf_label':    'Il Focus EDF',
    'about.edf_text':     'Abbiamo raccolto e inserito nel database tutte le entità (società, università, centri di ricerca, istituzioni pubbliche) che hanno partecipato a progetti EDF (European Defence Fund) e che quindi hanno ricevuto, direttamente o indirettamente, dei fondi dall\'Unione Europea per fare ricerca, sviluppare, produrre e commercializzare dei sistemi d\'arma autonomi.',

    // PUBLICATIONS
    'pub.title':          'Research',
    'pub.desc':           'Ricerche, articoli e inchieste prodotti dal team del progetto Man in the Loop o da ricercatori, ricercatrici, giornalisti e giornaliste che hanno utilizzato la piattaforma per il loro lavoro.',
    'pub.contact':        'Se vuoi segnalarci la tua pubblicazione, fatta anche grazie a MAN IN THE LOOP, per inserirla in questa sezione, scrivici a:',
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
    'map.about_this_map': 'About this map',
    'map.loading':        'Loading map data…',

    // NETWORKS — sidebar
    'net.title':          'Defence Network',
    'net.find_entity':    'Find entity',
    'net.search_placeholder': 'Search organisations…',
    'net.country':        'Country',
    'net.relationships':  'Relationships',
    'net.actors':         'Actors',
    'net.connections':    'Connections',
    'net.note':           'This section lets you explore economic relationships between entities in the database.<br><br>You can filter to show only projects funded through EDF (European Defence Fund).<br><br>Diamond size = EU budget. Circles are uniform.<br>Click node → details + cross-country connections.<br>Click background → reset.',
    'net.in_view':        'In this view',
    'net.selected_node':  'Selected node',
    'net.select_country': 'Select a country to see stats.',
    'net.edf_tip':        'By checking "EDF projects" the system will show all entities that have received funding through the EDF programme (European Defence Fund), the relationships between them and the details of each individual project.',
    'net.inv_tip':        'By checking "Investments" the system will show all economic entities (listed companies, start-ups, funds, etc.) included in the database and the investment relationships between them.',

    // ABOUT — content
    'about.title':        'About',
    'about.intro':        'The Man in the Loop platform is developed by info.nodes, an Italian non-profit organisation founded in 2019, with financial support from <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, as part of the global programme "Militarisation of Tech".',
    'about.last_update':  'Last data update: 16/06/2026',
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
    'about.edf_label':    'EDF Focus',
    'about.edf_text':     'We collected and added to the database all entities (companies, universities, research centres, public institutions) that participated in EDF (European Defence Fund) projects and therefore received, directly or indirectly, EU funds to research, develop, produce and commercialise autonomous weapon systems.',

    // PUBLICATIONS
    'pub.title':          'Research',
    'pub.desc':           'Research papers, articles and investigations produced by the Man in the Loop team or by researchers and journalists who used the platform in their work.',
    'pub.contact':        'If you want to share a publication made possible with MAN IN THE LOOP, write to us at:',
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
    'map.about_this_map': 'À propos de la carte',
    'map.loading':        'Chargement des données…',

    // NETWORKS — sidebar
    'net.title':          'Réseau de défense',
    'net.find_entity':    'Trouver une entité',
    'net.search_placeholder': 'Rechercher des organisations…',
    'net.country':        'Pays',
    'net.relationships':  'Relations',
    'net.actors':         'Acteurs',
    'net.connections':    'Connexions',
    'net.note':           'Cette section permet d\'explorer les relations économiques entre les entités de la base de données.<br><br>Vous pouvez filtrer pour n\'afficher que les projets financés par l\'EDF (Fonds européen de défense).<br><br>Taille du losange = budget UE. Les cercles sont uniformes.<br>Cliquez sur un nœud → détails + connexions transnationales.<br>Cliquez sur le fond → réinitialiser.',
    'net.in_view':        'Dans cette vue',
    'net.selected_node':  'Nœud sélectionné',
    'net.select_country': 'Sélectionnez un pays pour voir les statistiques.',
    'net.edf_tip':        'En cochant "EDF projects", le système affichera toutes les entités ayant reçu des financements dans le cadre du programme EDF (Fonds européen de défense), les relations entre elles et les informations de chaque projet.',
    'net.inv_tip':        'En cochant "Investments", le système affichera toutes les entités économiques (sociétés cotées, start-ups, fonds, etc.) présentes dans la base de données et les relations d\'investissement entre elles.',

    // ABOUT — content
    'about.title':        'À propos',
    'about.intro':        'La plateforme Man in the Loop est développée par info.nodes, organisation à but non lucratif italienne fondée en 2019, grâce au soutien financier de <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, dans le cadre du programme mondial « Militarisation of Tech ».',
    'about.last_update':  'Dernière mise à jour des données : 16/06/2026',
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
    'about.edf_label':    'Focus EDF',
    'about.edf_text':     'Nous avons collecté et ajouté à la base de données toutes les entités (sociétés, universités, centres de recherche, institutions publiques) ayant participé à des projets EDF (Fonds européen de défense) et ayant donc reçu, directement ou indirectement, des fonds de l\'Union européenne pour la recherche, le développement, la production et la commercialisation de systèmes d\'armes autonomes.',

    // PUBLICATIONS
    'pub.title':          'Recherche',
    'pub.desc':           'Recherches, articles et enquêtes produits par l\'équipe du projet Man in the Loop ou par des chercheurs et journalistes ayant utilisé la plateforme.',
    'pub.contact':        'Si vous souhaitez nous signaler une publication réalisée grâce à MAN IN THE LOOP, écrivez-nous à :',
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
    'map.about_this_map': 'Acerca del mapa',
    'map.loading':        'Cargando datos del mapa…',

    // NETWORKS — sidebar
    'net.title':          'Red de defensa',
    'net.find_entity':    'Buscar entidad',
    'net.search_placeholder': 'Buscar organizaciones…',
    'net.country':        'País',
    'net.relationships':  'Relaciones',
    'net.actors':         'Actores',
    'net.connections':    'Conexiones',
    'net.note':           'Esta sección permite explorar las relaciones económicas entre los sujetos de la base de datos.<br><br>Es posible visualizar solo los proyectos financiados a través del EDF (Fondo Europeo de Defensa).<br><br>Tamaño del rombo = presupuesto UE. Los círculos son uniformes.<br>Haz clic en el nodo → detalles + conexiones transnacionales.<br>Haz clic en el fondo → restablecer.',
    'net.in_view':        'En esta vista',
    'net.selected_node':  'Nodo seleccionado',
    'net.select_country': 'Seleccione un país para ver estadísticas.',
    'net.edf_tip':        'Al marcar "EDF projects", el sistema mostrará todas las entidades que han recibido financiación a través del programa EDF (Fondo Europeo de Defensa), las relaciones entre ellas y la información de cada proyecto.',
    'net.inv_tip':        'Al marcar "Investments", el sistema mostrará todas las entidades económicas (empresas cotizadas, start-ups, fondos, etc.) incluidas en la base de datos y las relaciones de inversión entre ellas.',

    // ABOUT — content
    'about.title':        'Acerca de',
    'about.intro':        'La plataforma Man in the Loop es desarrollada por info.nodes, organización sin ánimo de lucro italiana fundada en 2019, gracias al apoyo económico de <a href="https://privacyinternational.org/" target="_blank" rel="noopener" style="font-weight:bold;color:inherit;">Privacy International</a>, en el marco del programa global «Militarisation of Tech».',
    'about.last_update':  'Última actualización de datos: 16/06/2026',
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
    'about.edf_label':    'El foco EDF',
    'about.edf_text':     'Hemos recopilado e introducido en la base de datos todas las entidades (empresas, universidades, centros de investigación, instituciones públicas) que han participado en proyectos EDF (Fondo Europeo de Defensa) y que por tanto han recibido, directa o indirectamente, fondos de la Unión Europea para investigar, desarrollar, producir y comercializar sistemas de armas autónomas.',

    // PUBLICATIONS
    'pub.title':          'Investigación',
    'pub.desc':           'Investigaciones, artículos e informes producidos por el equipo del proyecto Man in the Loop o por investigadores y periodistas que han utilizado la plataforma.',
    'pub.contact':        'Si quieres compartir una publicación realizada gracias a MAN IN THE LOOP, escríbenos a:',
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

// Keep lang param on all tabnav links so navigation preserves the language
function _patchNavLinks() {
  document.querySelectorAll('a.tnav-btn').forEach(a => {
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
