// ── Nomi dei Paesi: normalizzazione condivisa ────────────────────────────────
//
// Le quattro fonti del database scrivono lo stesso Paese in modi diversi:
// EDF usa "Czechia" e "Netherlands", Crunchbase "Czech Republic" e "The
// Netherlands", Wikidata a volte "Russian Federation". Senza questa mappa lo
// stesso Paese si spezza in due voci e nessuna delle due arriva in cima alle
// classifiche: gli Stati Uniti risultavano 117 + 56 investitori invece di 173.
//
// La forma canonica è quella usata dai dati EDF, che sono la fonte principale
// della piattaforma.
//
// Per aggiungere una variante: chiave in minuscolo, valore nella forma
// canonica. Se compare un valore che non è un Paese, mappalo a null.

(function (global) {
  'use strict';

  var ALIASES = {
    // Stati Uniti
    'usa':                        'United States',
    'u.s.a.':                     'United States',
    'united states of america':   'United States',
    // Regno Unito
    'uk':                         'United Kingdom',
    'great britain':              'United Kingdom',
    // Paesi Bassi
    'the netherlands':            'Netherlands',
    'holland':                    'Netherlands',
    // Cechia
    'czech republic':             'Czechia',
    'czech rep.':                 'Czechia',
    // Altri
    "people's republic of china": 'China',
    'russian federation':         'Russia',
    'slovakia (slovak republic)': 'Slovakia',
    'republic of korea':          'South Korea',

    // Non sono Paesi: vanno scartati, non conteggiati.
    // 'Internationality' è il valore che Wikidata assegna all'Unione Europea.
    'internationality':           null
  };

  // Restituisce la forma canonica di un nome di Paese, oppure null se il
  // valore è vuoto o non è un Paese.
  function normalizeCountry(raw) {
    if (!raw) return null;
    var trimmed = String(raw).trim();
    if (!trimmed) return null;
    var key = trimmed.toLowerCase();
    if (Object.prototype.hasOwnProperty.call(ALIASES, key)) return ALIASES[key];
    return trimmed;
  }

  // Ricava il Paese di un'entità dalle sue fonti, in ordine di affidabilità:
  //
  //   1. infonodes  — verifiche fatte a mano dalla redazione, hanno la meglio
  //   2. edf        — dichiarato dal beneficiario nel record del progetto
  //   3. wikidata   — ultima risorsa
  //
  // EDF precede Wikidata perché descrive la singola entità giuridica che ha
  // incassato i fondi, mentre Wikidata associa spesso il nome alla capogruppo:
  // su 43 entità le due fonti divergono e il pattern è sempre questo. Airbus
  // Defence and Space risultava in Spagna anche per le controllate tedesca,
  // francese e finlandese; Beyond Gravity Austria in Svizzera (sede RUAG);
  // MBDA España in Italia. In tutti questi casi il dato EDF è quello giusto.
  // Con { useHeadquarters: true } ricade sull'ultimo pezzo della sede
  // Crunchbase ("Menlo Park, California, United States"): serve per gli
  // investitori, che spesso esistono solo su Crunchbase e non hanno il campo
  // country. Le viste che elencano solo entità EDF non ne hanno bisogno.
  function entityCountry(entity, options) {
    if (!entity) return null;
    var s = entity.sources || {};
    var raw = (s.infonodes || {}).country ||
              (s.edf       || {}).country ||
              (s.wikidata  || {}).country || null;

    if (!raw && options && options.useHeadquarters) {
      var hq = (s.crunchbase || {}).headquarters;
      if (hq) raw = String(hq).split(',').pop();
    }
    return normalizeCountry(raw);
  }

  // ── Country name → ISO 3166-1 numeric code ──────────────────────────────────
  //
  // Used by index.html (map arcs, country nodes) and reports/countries/index.html
  // (link to the map for a given country). Keys must be canonical forms as
  // returned by normalizeCountry() above, plus a few common raw aliases seen
  // directly in source data (e.g. 'USA', 'Germania').
  var WD_TO_ISO = {
    'United States': 840, 'USA': 840,
    'Germany': 276, 'Germania': 276,
    'United Kingdom': 826, 'UK': 826,
    'France': 250, 'Francia': 250,
    'Israel': 376,
    'Sweden': 752,
    'Norway': 578, 'Norvegia': 578,
    'Finland': 246,
    'Denmark': 208,
    'Netherlands': 528,
    'Belgium': 56, 'Belgio': 56,
    'Switzerland': 756,
    'Austria': 40,
    'Italy': 380,
    'Spain': 724,
    'Poland': 616, 'Polonia': 616,
    'Czech Republic': 203, 'Czech Rep.': 203, 'Czechia': 203,
    'Romania': 642,
    'Estonia': 233,
    'Latvia': 428,
    'Lithuania': 440,
    'Ukraine': 804,
    'Russia': 643,
    'Turkey': 792,
    'India': 356,
    'China': 156, 'Cina': 156, "People's Republic of China": 156,
    'Taiwan': 158,
    'Japan': 392, 'Giappone': 392,
    'South Korea': 410,
    'Australia': 36,
    'Canada': 124,
    'Brazil': 76,
    'South Africa': 710,
    'Singapore': 702,
    'United Arab Emirates': 784, 'EAU (Dubai)': 784,
    'Saudi Arabia': 682,
    'Portugal': 620,
    'Greece': 300,
    'Hungary': 348,
    'Slovakia': 703,
    'Luxembourg': 442,
    'Ireland': 372,
    'Cyprus': 196,
    'Malta': 470,
    'Croatia': 191,
    'Slovenia': 705,
    'Serbia': 688,
    'Bulgaria': 100,
    'North Macedonia': 807,
    'Albania': 8,
    'Moldova': 498,
    'Belarus': 112,
    'Kazakhstan': 398,
    'Mexico': 484,
    'Argentina': 32,
    'Chile': 152, 'Cile': 152,
    'Colombia': 170,
    'Peru': 604,
    'New Zealand': 554,
    'Indonesia': 360,
    'Malaysia': 458,
    'Thailand': 764,
    'Vietnam': 704,
    'Philippines': 608,
    'Pakistan': 586,
    'Bangladesh': 50,
    'Egypt': 818,
    'Nigeria': 566,
    'Kenya': 404,
    'Morocco': 504,
    'Tunisia': 788,
    'Ethiopia': 231,
  };

  var ISO_TO_NAME = {};
  for (var _name in WD_TO_ISO) {
    if (!Object.prototype.hasOwnProperty.call(WD_TO_ISO, _name)) continue;
    var _iso = WD_TO_ISO[_name];
    if (!(_iso in ISO_TO_NAME)) ISO_TO_NAME[_iso] = _name;
  }

  global.MITL = global.MITL || {};
  global.MITL.normalizeCountry = normalizeCountry;
  global.MITL.entityCountry    = entityCountry;
  global.MITL.COUNTRY_ALIASES  = ALIASES;
  global.MITL.WD_TO_ISO        = WD_TO_ISO;
  global.MITL.ISO_TO_NAME      = ISO_TO_NAME;
})(this);
