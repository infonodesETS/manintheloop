# Issues & pending fixes

## Frontend — map side panel

### [FIXED] Nascondere i tag `sector` del vecchio DB (eccetto Startup)

**Contesto:** 46+ aziende importate dal vecchio DB infonodes hanno il campo `sector` impostato manualmente (es. `Mining`, `Defence`) senza essere in nessun ETF iShares. La logica attuale in `companyBadges()` (`index.html`) mostra questi tag come fallback quando non ci sono dati iShares.

**Comportamento atteso:** il fallback `sector` va rimosso. Solo `Startup` va conservato (18 entità con `sector = 'Startup'`). I tag visualizzati devono provenire esclusivamente dai dati iShares (GICS → Tech / Comm / Mining / Defence).

**File da modificare:** `index.html` — funzione `companyBadges()`:

```js
// attuale (da rimuovere)
} else if (c.sector && c.sector !== 'Startup') {
  tags.push(c.sector);
}

// risultato atteso: blocco else if rimosso, rimane solo il fallback Startup
```

**Impatto:** ~46 aziende Mining e ~qualche Defence/Tech senza iShares perderanno il badge settore — comportamento corretto, i tag devono riflettere solo l'appartenenza agli ETF.

---

### [FIXED] EU Funded + Show Arcs: troppi archi visibili con paese selezionato

**Riproduzione:** aprire un paese (es. Netherlands `?country=528`) → attivare "Show investment flow arcs" → attivare "EU funded" → compaiono archi non correlati al paese.

**Causa root:** `applyMapFilter()` (`index.html` ~riga 746) sovrascrive completamente il filtro archi impostato da `showMapCountry()`. Quando EU Funded è ON, la logica:

```js
const dimEdf = edf && !mapState.edfISOs.has(d.tgt);
d3.select(this).classed('arc-dim', dimEdf || dimFilter);
```

rimuove `arc-dim` da **tutti** gli archi che puntano verso paesi EDF, ignorando `mapState.selectedIso`. Il filtro precedente di `showMapCountry` (che nascondeva gli archi non legati al paese aperto) viene perso.

**Comportamento atteso:** con EU Funded ON e paese selezionato, mostrare solo archi che:
1. coinvolgono il paese aperto (`d.src === selectedIso || d.tgt === selectedIso`)
2. E puntano verso un paese con entità EDF (`edfISOs.has(d.tgt)`)

**Fix:** in `applyMapFilter`, combinare il filtro EDF con il filtro paese, leggendo `mapState.selectedIso` e rispettando i pulsanti in/out già attivi nel panel:

```js
mapState.g.selectAll('.map-arc').each(function(d) {
    const dimEdf    = edf && !mapState.edfISOs.has(d.tgt);
    const dimFilter = f && (...);
    // rispetta il paese selezionato se non c'è entity filter attivo
    const sel = !f ? mapState.selectedIso : null;
    let dimCountry = false;
    if (sel) {
        if (d.tgt === sel) dimCountry = /* rispetta btn flow-in */ false;
        else if (d.src === sel) dimCountry = /* rispetta btn flow-out */ false;
        else dimCountry = true;
    }
    d3.select(this).classed('arc-dim', dimEdf || dimFilter || dimCountry);
});
```

**File:** `index.html` — funzione `applyMapFilter()`, blocco `selectAll('.map-arc')`.

---

## Data — enrichment

### [FIXED] IV entities: wikidata_id presente ma dati non arricchiti da enrich_wikidata.py

**Esempio:** `IV-0237` Goldman Sachs (`Q193326`) — il profilo mostra il QID e un blocco `sources.wikidata` sparso, ma mancano `official_website`, `inception`, `employees`, `instance_of`, `isin`, `wikipedia_url`.

**Causa root:** i 209 IV con `wikidata_id` hanno un blocco `sources.wikidata` creato da `import_investors_crunchbase.py --wikidata` (SPARQL base: solo label, description, country, headquarters). Poiché il blocco esiste già, `enrich_wikidata.py` li salta (skip entities già arricchite). Il full enrichment via `wbgetentities` non è mai stato eseguito su questi.

**Dati:**
- IV con `wikidata_id`: **209**
- IV con `instance_of` popolato (proxy di full enrichment): **26 / 209**
- IN con `instance_of` popolato (enriched correttamente): **704 / 710**

**Fix:** eseguire `enrich_wikidata.py --force` — il flag `--force` sovrascrive anche i blocchi già esistenti, eseguendo il full `wbgetentities` fetch per tutti i 209 IV con QID.

```bash
python3 scripts/enrich_wikidata.py --force
python3 scripts/validate.py
```

**Attenzione:** `--force` re-enrichisce anche gli IN già corretti. Valutare se aggiungere un flag `--type investor` allo script per limitare il re-enrichment ai soli IV, evitando 700+ chiamate API non necessarie.
