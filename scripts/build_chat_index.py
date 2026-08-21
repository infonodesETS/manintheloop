# -*- coding: utf-8 -*-
"""
Genera data/mitl-index.json: la vista compatta del database che il chatbot
MARLA interroga.

database.json sta sui 12 MB perché porta tutto lo storico e tutti i campi
grezzi delle quattro fonti. Una funzione serverless che lo scarica a ogni
avvio a freddo è lenta e costosa, e comunque il chatbot ne usa una frazione.
Qui si estrae solo quello che serve a rispondere: chi è un soggetto, di che
Paese, chi ha investito in chi, quali progetti EDF esistono e cosa dicono.

Ogni record porta il proprio `url`: è il pezzo che rende possibile citare le
fonti, e senza il quale il chatbot non ha modo di rimandare alla piattaforma.

Uso:  py -3 scripts/build_chat_index.py
"""
import io
import json
import os
from datetime import date

RADICE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORGENTE = os.path.join(RADICE, 'data', 'database.json')
USCITA   = os.path.join(RADICE, 'data', 'mitl-index.json')

SITO = 'https://infonodesets.github.io/manintheloop'

# Stesse regole di web/countries.js: le fonti scrivono lo stesso Paese in modi
# diversi, e EDF precede Wikidata perché descrive la singola entità giuridica
# che ha incassato i fondi, non la capogruppo.
ALIAS_PAESI = {
    'usa': 'United States',
    'u.s.a.': 'United States',
    'united states of america': 'United States',
    'uk': 'United Kingdom',
    'great britain': 'United Kingdom',
    'the netherlands': 'Netherlands',
    'holland': 'Netherlands',
    'czech republic': 'Czechia',
    'czech rep.': 'Czechia',
    "people's republic of china": 'China',
    'russian federation': 'Russia',
    'slovakia (slovak republic)': 'Slovakia',
    'republic of korea': 'South Korea',
    'internationality': None,   # valore Wikidata per l'Unione Europea
}


def normalizza_paese(grezzo):
    if not grezzo:
        return None
    testo = str(grezzo).strip()
    if not testo:
        return None
    chiave = testo.lower()
    if chiave in ALIAS_PAESI:
        return ALIAS_PAESI[chiave]
    return testo


def paese_di(entita, usa_sede=False):
    s = entita.get('sources') or {}
    grezzo = ((s.get('infonodes') or {}).get('country')
              or (s.get('edf') or {}).get('country')
              or (s.get('wikidata') or {}).get('country'))
    if not grezzo and usa_sede:
        sede = (s.get('crunchbase') or {}).get('headquarters')
        if sede:
            grezzo = str(sede).split(',')[-1]
    return normalizza_paese(grezzo)


def settori_di(entita):
    cb = (entita.get('sources') or {}).get('crunchbase') or {}
    grezzo = cb.get('industries') or []
    if isinstance(grezzo, str):
        grezzo = grezzo.split(',')
    return [x.strip() for x in grezzo if str(x).strip()]


def ritirate(db):
    """Entità marcate come ritirate: vanno escluse da conteggi e relazioni."""
    return {
        e['id'] for e in db['entities']
        if any(h.get('action') == 'entity_retired' for h in (e.get('history') or []))
    }


def costruisci():
    db = json.load(io.open(SORGENTE, encoding='utf-8'))
    fuori = ritirate(db)

    soggetti, progetti = [], []

    for e in db['entities']:
        if e['id'] in fuori:
            continue

        if e['id'].startswith('EDF-'):
            p = (e.get('sources') or {}).get('edf_project') or {}
            progetti.append({
                'id': e['id'],
                'acronimo': p.get('acronym'),
                'titolo': e.get('name'),
                'bando': p.get('call_title'),
                'bando_id': p.get('call_id'),
                'stato': p.get('status'),
                'inizio': p.get('start_date'),
                'fine': p.get('end_date'),
                'budget_totale': p.get('overall_budget'),
                'contributo_ue': p.get('eu_contribution'),
                'tipo_azione': p.get('type_of_action'),
                'obiettivo': p.get('objective'),
                # Il portale della Commissione è la fonte primaria; la scheda
                # sulla piattaforma è la nostra vista sugli stessi dati.
                'url_commissione': p.get('url'),
                'url': '%s/networks.html?selected=%s' % (SITO, e['id']),
            })
            continue

        edf = (e.get('sources') or {}).get('edf') or {}
        soggetti.append({
            'id': e['id'],
            'nome': e.get('name'),
            'tipo': e.get('type'),
            'paese': paese_di(e, usa_sede=True),
            'settori': settori_di(e),
            'edf_contributo': edf.get('total_eu_contribution') or 0,
            'edf_progetti': edf.get('project_count') or 0,
            'pic': edf.get('pic'),
            'url': '%s/search.html?organization=%s' % (SITO, e['id']),
        })

    relazioni = []
    for r in db['relationships']:
        if r['source'] in fuori or r['target'] in fuori:
            continue
        voce = {'da': r['source'], 'a': r['target'], 'tipo': r['type']}
        dettagli = r.get('details') or {}
        if dettagli.get('lead'):
            voce['lead'] = True
        relazioni.append(voce)

    return {
        'generato': date.today().isoformat(),
        'fonte': 'manintheloop',
        'visibilita': 'pubblico',
        'sito': SITO,
        'soggetti': soggetti,
        'progetti': progetti,
        'relazioni': relazioni,
    }


if __name__ == '__main__':
    indice = costruisci()
    io.open(USCITA, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(indice, ensure_ascii=False, separators=(',', ':')) + '\n')

    con_obiettivo = sum(1 for p in indice['progetti'] if p.get('obiettivo'))
    print('scritto %s' % os.path.relpath(USCITA, RADICE))
    print('  soggetti:  %d' % len(indice['soggetti']))
    print('  progetti:  %d (con testo obiettivo: %d)' % (len(indice['progetti']), con_obiettivo))
    print('  relazioni: %d' % len(indice['relazioni']))
    print('  peso:      %.2f MB (database.json: %.2f MB)' % (
        os.path.getsize(USCITA) / 1e6, os.path.getsize(SORGENTE) / 1e6))
