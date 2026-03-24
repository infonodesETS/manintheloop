'use strict';

export const AppState = {
  db: null,
  companies: [],
  investors: [],
  relationships: [],
  ALL_COMPANIES: [],
  COMPANIES: [],
  INVESTORS: [],
  derived: {
    entityMap: {},
    investorMeta: {},
    raw: [],        // [companyName, investorName, isLead] tuples
    companyMap: {}, // name → entity
    invMap: {},     // name → investor meta
  },
  ui: {
    currentGroup: 'supply-chain',
    currentTab: 'overview',
    matrix: { sector: 'all' },
    companies: { sector: 'all', sort: { key: 'name', asc: true }, search: '' },
    investors: { sort: { key: 'total', asc: false }, search: '', typeFilter: null },
    relationships: { search: '' },
    graph: {
      view: 'network',
      sector: 'all',
      projFilter: 'all',
      search: '',
      leadOnly: false,
      hideIsolated: false,
      showCompanies: true,
      showInvestors: true,
      sim: null,
      simBi: null,
      simProj: null,
    },
    wikidata: {
      selectedCountry: null,
      liveMode: false,
      list: [],
      debounce: null,
    },
    edfoverview: { built: false },
    edfmap:      { built: false },
    eucalls:     { built: false },
    edfbrowse:   { built: false },
    map: {
      built: false,
      activeFilter: null,
      showArcs: true,
      zoom: null,
      svg: null,
      g: null,
      projection: null,
      countryData: {},
      arcData: [],
      centroids: {},
    },
  },
};
