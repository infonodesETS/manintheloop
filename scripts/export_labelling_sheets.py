# -*- coding: utf-8 -*-
"""
Genera i due fogli di lavoro per l'etichettatura manuale (Fasi 1 e 2 del piano
per l'intern):

    docs/privato/aziende-defence-tech.csv
    docs/privato/investitori-tipologia.csv

Tre scelte da spiegare, perché non sono ovvie:

1. La PRIMA colonna è l'id, non il nome. Il lavoro finito va reimportato nel
   database, e senza id l'aggancio si farebbe per nome — ma i nomi collidono:
   "Vanguard Ventures" non è The Vanguard Group, "Fidelity International" non è
   Fidelity Investments, Iveco Defence Vehicles è duplicata, Telecom Italia due
   volte. Reimportare per nome assegnerebbe etichette al soggetto sbagliato in
   silenzio.

2. La classificazione ATTUALE viaggia col foglio, insieme al segnale che l'ha
   prodotta. Una colonna vuota costringerebbe a riclassificare da zero e
   perderebbe l'informazione più utile: dove il giudizio umano si discosta da
   quello automatico.

3. Le righe sono ORDINATE per impatto, non alfabeticamente. Sono più di mille
   aziende: il lavoro non si finirà tutto, quindi deve valere qualcosa anche se
   si ferma a metà. In cima ci sono le aziende che compaiono nelle classifiche
   pubblicate, dove un'etichetta sbagliata si vede sul sito.

Uso:  py -3 scripts/export_labelling_sheets.py
"""
import csv
import io
import json
import os

RADICE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USCITA  = os.path.join(RADICE, 'docs', 'privato')

ALIAS_PAESI = {
    'usa': 'United States', 'u.s.a.': 'United States',
    'united states of america': 'United States',
    'uk': 'United Kingdom', 'great britain': 'United Kingdom',
    'the netherlands': 'Netherlands', 'holland': 'Netherlands',
    'czech republic': 'Czechia', 'czech rep.': 'Czechia',
    "people's republic of china": 'China', 'russian federation': 'Russia',
    'slovakia (slovak republic)': 'Slovakia', 'republic of korea': 'South Korea',
    'internationality': None,
}


def normalizza_paese(v):
    if not v:
        return ''
    t = str(v).strip()
    if t.lower() in ALIAS_PAESI:
        return ALIAS_PAESI[t.lower()] or ''
    return t


def paese(e):
    s = e.get('sources') or {}
    for k in ('infonodes', 'edf', 'wikidata'):
        v = (s.get(k) or {}).get('country')
        if v:
            return normalizza_paese(v)
    hq = (s.get('crunchbase') or {}).get('headquarters')
    return normalizza_paese(hq.split(',')[-1]) if hq else ''


def sito(e):
    s = e.get('sources') or {}
    for chiave, campo in (('infonodes', 'website'),
                          ('crunchbase', 'website'),
                          ('wikidata', 'official_website')):
        v = (s.get(chiave) or {}).get(campo)
        if v:
            return str(v).strip()
    # Ripiego: il profilo Crunchbase è meglio di niente per iniziare a cercare
    return str((s.get('crunchbase') or {}).get('profile_url') or '').strip()


def industrie(e):
    cb = (e.get('sources') or {}).get('crunchbase') or {}
    v = cb.get('industries') or []
    if isinstance(v, str):
        v = v.split(',')
    return [x.strip() for x in v if str(x).strip()]


def carica():
    db = json.load(io.open(os.path.join(RADICE, 'data', 'database.json'), encoding='utf-8'))
    criteri = json.load(io.open(os.path.join(RADICE, 'data', 'defence_criteria.json'), encoding='utf-8'))
    ritirate = {e['id'] for e in db['entities']
                if any(h.get('action') == 'entity_retired' for h in (e.get('history') or []))}
    ent = [e for e in db['entities'] if e['id'] not in ritirate]
    rel = [r for r in db['relationships']
           if r['source'] not in ritirate and r['target'] not in ritirate]
    return ent, rel, criteri


def scrivi(nome, intestazioni, righe):
    percorso = os.path.join(USCITA, nome)
    # utf-8-sig: senza BOM Excel e Google Sheets sbagliano gli accenti
    with io.open(percorso, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(intestazioni)
        w.writerows(righe)
    print('  %-34s %5d righe' % (nome, len(righe)))
    return percorso


def main():
    os.makedirs(USCITA, exist_ok=True)
    ent, rel, criteri = carica()
    byid = {e['id']: e for e in ent}

    investimenti = [r for r in rel if r['type'] == 'investment']
    partecipate  = {r['target'] for r in investimenti}
    edf_partec   = {r['source'] for r in rel if r['type'] == 'edf_participation'}

    n_investimenti = {}
    for r in investimenti:
        n_investimenti[r['source']] = n_investimenti.get(r['source'], 0) + 1

    industrie_difesa = set(criteri.get('industries') or [])
    esclusi  = {x.get('id') for x in (criteri.get('exclude') or []) if isinstance(x, dict)}
    inclusi  = {x.get('id') for x in (criteri.get('include') or []) if isinstance(x, dict)}

    def segnale(e):
        """Perché il sistema considera (o no) questa azienda defence tech."""
        if e['id'] in esclusi:
            return 'no', 'escluso a mano'
        if e['id'] in inclusi:
            return 'yes', 'incluso a mano'
        if e['id'] in edf_partec:
            return 'yes', 'partecipa a progetti EDF'
        if e.get('sector') == 'Defence':
            return 'yes', 'settore interno = Defence'
        ish = (e.get('sources') or {}).get('ishares') or []
        if any(x.get('gics_code') == '201010' for x in (ish if isinstance(ish, list) else [ish])):
            return 'yes', 'ETF Aerospace & Defence'
        trovate = sorted(set(industrie(e)) & industrie_difesa)
        if trovate:
            return 'yes', 'industria Crunchbase: ' + ', '.join(trovate)
        return 'no', 'nessun segnale'

    # ── Aziende ───────────────────────────────────────────────────────────────
    aziende = [e for e in ent if e.get('type') == 'company']
    righe = []
    for e in aziende:
        flag, perche = segnale(e)
        nelle_classifiche = e['id'] in partecipate
        if nelle_classifiche:
            gruppo = '1 - nelle classifiche (partecipata)'
        elif e['id'] in edf_partec:
            gruppo = '2 - partecipa a progetti EDF'
        else:
            gruppo = '3 - nessuna relazione (da ETF)'
        righe.append([
            e['id'], e.get('name', ''), paese(e), sito(e),
            gruppo, flag, perche,
            '', '', '',                       # <- colonne da compilare
        ])
    # Priorità: prima le classifiche, e dentro ogni gruppo prima le già marcate
    ordine = {'1': 0, '2': 1, '3': 2}
    righe.sort(key=lambda r: (ordine[r[4][0]], 0 if r[5] == 'yes' else 1, r[1].lower()))

    print('\nScritti in docs/privato/ :')
    scrivi('aziende-defence-tech.csv',
           ['id', 'name', 'country', 'website',
            'group (priority)', 'current flag', 'why current flag',
            'DEFENCE TECH? yes/no/unsure', 'SOURCE (link)', 'NOTES'],
           righe)

    # ── Investitori ───────────────────────────────────────────────────────────
    finanziatori = [byid[i] for i in n_investimenti if i in byid]
    righe_inv = []
    for e in finanziatori:
        righe_inv.append([
            e['id'], e.get('name', ''), paese(e), sito(e),
            e.get('type', ''), n_investimenti[e['id']],
            '', '', '', '',                   # <- colonne da compilare
        ])
    righe_inv.sort(key=lambda r: (-r[5], r[1].lower()))

    scrivi('investitori-tipologia.csv',
           ['id', 'name', 'country', 'website', 'current type in db',
            'n. investments',
            'TYPE?', 'IF PUBLIC, WHICH KIND?', 'SOURCE (link)', 'NOTES'],
           righe_inv)

    # ── Riepilogo ─────────────────────────────────────────────────────────────
    senza_sito = sum(1 for r in righe_inv if not r[3])
    print('\nAziende: %d totali' % len(righe))
    for g in sorted({r[4] for r in righe}):
        n = sum(1 for r in righe if r[4] == g)
        s = sum(1 for r in righe if r[4] == g and r[5] == 'yes')
        print('  %-38s %4d  (gia marcate defence tech: %d)' % (g, n, s))
    print('\nInvestitori: %d totali' % len(righe_inv))
    print('  senza sito web nel database: %d (%.0f%%) - va cercato a mano'
          % (senza_sito, senza_sito / len(righe_inv) * 100))
    print('  con 2 o piu investimenti:    %d' % sum(1 for r in righe_inv if r[5] >= 2))


if __name__ == '__main__':
    main()
