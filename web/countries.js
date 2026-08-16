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

  // Ricava il Paese di un'entità dalle sue fonti, in ordine di affidabilità.
  // Con { useHeadquarters: true } ricade sull'ultimo pezzo della sede
  // Crunchbase ("Menlo Park, California, United States"): serve per gli
  // investitori, che spesso esistono solo su Crunchbase e non hanno il campo
  // country. Le viste che elencano solo entità EDF non ne hanno bisogno.
  function entityCountry(entity, options) {
    if (!entity) return null;
    var s = entity.sources || {};
    var raw = (s.infonodes || {}).country ||
              (s.wikidata  || {}).country ||
              (s.edf       || {}).country || null;

    if (!raw && options && options.useHeadquarters) {
      var hq = (s.crunchbase || {}).headquarters;
      if (hq) raw = String(hq).split(',').pop();
    }
    return normalizeCountry(raw);
  }

  global.MITL = global.MITL || {};
  global.MITL.normalizeCountry = normalizeCountry;
  global.MITL.entityCountry    = entityCountry;
  global.MITL.COUNTRY_ALIASES  = ALIASES;
})(this);
