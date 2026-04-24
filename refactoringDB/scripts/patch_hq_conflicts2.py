#!/usr/bin/env python3
"""
patch_hq_conflicts2.py — Second-pass HQ conflict resolution (2026-04-24)

Actions:
  A) Fix WD.country errors (WD.headquarters city is in wrong country)
  B) Resolve Chemring's re-flagged field_conflict (already resolved 2026-04-23)
  C) Mark legitimate dual-location cases as compatible_sources
  D) Flag clear CB wrong-entity matches (cb_hq_mismatch_severe)
  E) Flag CB sub-entity matches (cb_hq_mismatch_subsidiary)
"""
import json, sys
from datetime import date

DRY_RUN = '--dry-run' in sys.argv
TODAY = str(date.today())

with open('data/database.json') as f:
    db = json.load(f)

entities = {e['id']: e for e in db['entities']}

stats = {'wd_country_fixed': 0, 'chemring_resolved': 0,
         'dual_location': 0, 'cb_wrong_entity': 0, 'cb_subsidiary': 0}

def add_validation(e, entry):
    e.setdefault('validation', []).append(entry)

def add_history(e, entry):
    e.setdefault('history', []).append(entry)

# ─── A) WD COUNTRY ERRORS ─────────────────────────────────────────────────────
WD_COUNTRY_FIXES = {
    'IN-0468': {
        'wrong': 'Germany', 'hq': 'Marignane', 'correct': 'France',
        'note': 'Marignane is in Bouches-du-Rhône, France — not Germany. Wikidata P17 error.'
    },
    'IN-1097': {
        'wrong': 'Netherlands', 'hq': 'Plan-les-Ouates', 'correct': 'Switzerland',
        'note': 'Plan-les-Ouates is in Canton of Geneva, Switzerland — not Netherlands. Wikidata P17 error.'
    },
    'IN-1354': {
        'wrong': 'China', 'hq': 'Guangzhou', 'correct': None,
        'note': 'Comec is an Italian EDF participant (Ciano d\'Enza, Emilia-Romagna). Wikidata matched wrong Chinese entity. WD country nulled.'
    },
    'IN-0306': {
        'wrong': 'United Kingdom', 'hq': 'Melbourne', 'correct': 'Australia',
        'note': 'Rio Tinto HQ is Melbourne, Australia. Wikidata P17=UK reflects London legal registration but operational HQ is Australia. Nulled WD country to avoid misleading country-level data.'
    },
}

for eid, fix in WD_COUNTRY_FIXES.items():
    e = entities.get(eid)
    if not e:
        print(f"  [WARN] {eid} not found")
        continue
    wd = (e.get('sources') or {}).get('wikidata') or {}
    if wd.get('country') != fix['wrong']:
        print(f"  [SKIP] {eid}: WD.country is already '{wd.get('country')}' (expected '{fix['wrong']}')")
        continue
    print(f"  [WD-FIX] {eid} {e['name']}: WD.country '{fix['wrong']}' → None")
    if not DRY_RUN:
        wd['country'] = None
        add_validation(e, {
            'status': 'wikidata_country_corrected',
            'description': f"sources.wikidata.country='{fix['wrong']}' nulled — {fix['note']}",
            'canonical_country': fix['correct'],
            'author': 'patch_hq_conflicts2.py',
            'datestamp': TODAY
        })
        add_history(e, {
            'action': 'field_corrected',
            'field': 'sources.wikidata.country',
            'old_value': fix['wrong'],
            'new_value': None,
            'note': fix['note'],
            'author': 'patch_hq_conflicts2.py',
            'datestamp': TODAY
        })
    stats['wd_country_fixed'] += 1

# ─── B) CHEMRING: resolve re-flagged field_conflict ──────────────────────────
e = entities.get('IN-1262')
if e:
    # Find the new (2026-04-24) field_conflict entry and upgrade it to resolved
    for v in e.get('validation', []):
        if v.get('status') == 'field_conflict' and v.get('datestamp') == TODAY:
            print(f"  [CHEMRING] Resolving re-flagged field_conflict for IN-1262")
            if not DRY_RUN:
                v['status'] = 'field_conflict_resolved'
                v['resolution'] = 'wikidata_country_error'
                v['resolved'] = TODAY
                v['resolved_note'] = (
                    'Chemring Group plc is headquartered in Fareham, Hampshire, UK (LSE-listed). '
                    'Wikidata P17=Germany is a known Wikidata error — confirmed resolved 2026-04-23. '
                    'HQ conflict: WD=Fareham vs CB=Romsey, Hampshire — both Hampshire UK, compatible.'
                )
            stats['chemring_resolved'] += 1

# ─── C) LEGITIMATE DUAL-LOCATION → compatible_sources ───────────────────────
DUAL_LOCATION = {
    'IN-0028': 'Anglo American: London (registered) + Johannesburg (operational HQ) — both valid for dual-listed mining company',
    'IN-0214': 'Logitech SA: Lausanne (parent entity) vs Logitech Inc. San Jose (US entity) — CB matched US subsidiary; both correct',
    'IN-0342': 'Southern Copper: Phoenix AZ (US parent SCCO) vs Mexico City (main mining operations) — both valid',
    'IN-0347': 'STmicroelectronics: dual HQ Geneva CH + Montrouge FR — CB has Geneva entity, WD has French entity; both correct',
    'IN-0403': 'Valterra Platinum: Tourrettes FR (registered) + Johannesburg SA (primary operations) — both valid for SA-focused miner',
    'IN-0472': 'Airbus Operations: Bristol UK + Hamburg DE — two legitimate Airbus Operations sites; both are real entity addresses',
    'IN-0473': 'Airbus Operations: Bristol UK + Hamburg DE — two legitimate Airbus Operations sites; both are real entity addresses',
    'IN-1126': 'Telespazio France: WD=Rome (parent Telespazio Italy) vs CB=Toulouse (French subsidiary correct HQ) — CB is canonical for this entity',
    'IN-1167': 'United Monolithic Semiconductors: Ulm DE + Villebon-sur-Yvette FR — UMS is Franco-German JV; both sites are real',
    'IN-1168': 'United Monolithic Semiconductors: Ulm DE + Villebon-sur-Yvette FR — UMS is Franco-German JV; both sites are real',
    'IN-1249': 'AMD: Sunnyvale/Santa Clara (global HQ) vs Cologne DE (AMD EU entity) — CB matched EU entity; both valid',
    'IN-1300': 'KGHM International: Lubin PL (parent KGHM) vs Vancouver BC (KGHM International Ltd Canadian subsidiary) — CB correct for this entity',
    'IN-1338': 'TSMC Arizona: Hsinchu TW (parent TSMC) vs Phoenix AZ (TSMC Arizona fab) — CB correct for this US entity',
    'IN-1298': 'Indra: Alcobendas ES (parent Indra Sistemas) vs Bhiwandi IN (Indra India subsidiary) — CB matched Indian entity',
}

for eid, note in DUAL_LOCATION.items():
    e = entities.get(eid)
    if not e:
        continue
    # Check if already has a compatible_sources entry
    already = any(v.get('status') == 'compatible_sources' for v in e.get('validation', []))
    if already:
        print(f"  [SKIP] {eid}: already has compatible_sources")
        continue
    print(f"  [DUAL-LOC] {eid} {e['name']}: marking compatible_sources")
    if not DRY_RUN:
        add_validation(e, {
            'status': 'compatible_sources',
            'description': f'headquarters dual-location: {note}',
            'author': 'patch_hq_conflicts2.py',
            'datestamp': TODAY
        })
    stats['dual_location'] += 1

# ─── D) CLEAR CB WRONG-ENTITY MATCHES → cb_hq_mismatch_severe ───────────────
CB_WRONG_ENTITY = {
    'IN-0050':  'BCE (Bell Canada, Montreal) — CB matched an Italian entity in Alpignano (Piemonte); no corporate link',
    'IN-0069':  'CDW (Vernon Hills IL, US IT company) — CB matched a Dutch entity in Wijk bij Duurstede; no corporate link',
    'IN-0096':  'Commercial Metals Company (Irving TX) — CB matched a New Zealand entity in Penrose Wellington; no corporate link',
    'IN-0133':  'Fortescue (Perth, Australian iron ore) — CB matched a UK entity in Kidlington Oxfordshire; no corporate link',
    'IN-0172':  'Informa (London, UK media) — CB matched a Gütersloh entity (Bertelsmann territory); no Informa presence in Gütersloh',
    'IN-0209':  'Lasertec (Shin-Yokohama, Japan semiconductor) — CB matched a Polish entity in Tychy; no corporate link',
    'IN-0256':  'Nintendo (Kyoto Japan) — CB matched a Los Angeles entity; Nintendo of America HQ is Redmond WA, not LA',
    'IN-0371':  'Telia (Stockholm, Swedish telco) — CB matched an Athens Greece entity; Telia has no Greek operations',
    'IN-0520':  'Baltic Workboats (Nasva, Estonian shipyard) — CB matched a Coral Gables FL entity; no corporate link',
    'IN-0899':  'Naval (Naval Group, Paris France) — CB matched a Brazilian entity in Água Branca SP; no corporate link',
    'IN-0951':  'Patria (Kluuvi, Finnish defense) — CB matched a Bratislava Slovakia entity; no corporate link',
    'IN-1117':  'Tecnobit (Alcobendas, Spanish defense) — CB matched a Vicenza Italy entity; no corporate link',
    'IN-1163':  'Ubitech (Athens, Greek software) — CB matched a Jintan China entity; no corporate link',
    'IN-1315':  'Nexa Technologies (Aix-en-Provence, French IoT) — CB matched a Richardson TX entity; no corporate link',
    'IN-1341':  'United Aircraft Corporation (Moscow, Russian aerospace) — CB matched a Shenzhen entity; no corporate link',
}

for eid, note in CB_WRONG_ENTITY.items():
    e = entities.get(eid)
    if not e:
        continue
    already = any(v.get('status') == 'cb_hq_mismatch_severe' for v in e.get('validation', []))
    if already:
        print(f"  [SKIP] {eid}: already flagged")
        continue
    print(f"  [CB-WRONG] {eid} {e['name']}: flagging cb_hq_mismatch_severe")
    if not DRY_RUN:
        add_validation(e, {
            'status': 'cb_hq_mismatch_severe',
            'description': f'CB headquarters is for a completely different entity: {note}',
            'action_required': 'Verify whether entire sources.crunchbase block should be nulled',
            'author': 'patch_hq_conflicts2.py',
            'datestamp': TODAY
        })
    stats['cb_wrong_entity'] += 1

# ─── E) CB SUB-ENTITY MATCHES → cb_hq_mismatch_subsidiary ───────────────────
CB_SUBSIDIARY = {
    'IN-0032':  ('CB=Saitama Japan', 'Apple Inc. HQ is Cupertino CA — CB likely matched Apple Japan or local reseller entity'),
    'IN-0038':  ('CB=Brentwood TN', 'ASE Technology HQ is Kaohsiung Taiwan — CB likely matched ASE US subsidiary'),
    'IN-0055':  ('CB=London UK', 'Boliden HQ is Stockholm Sweden — CB likely matched Boliden London metals trading desk'),
    'IN-0064':  ('CB=Melville NY', 'Canon HQ is Ota Tokyo — CB matched Canon USA Inc. (Melville NY is Canon USA HQ)'),
    'IN-0108':  ('CB=Beverly MA', 'Delta Electronics HQ is Taipei Taiwan — CB likely matched Delta Electronics US entity'),
    'IN-0109':  ('CB=New York NY', 'Dentsu HQ is Tokyo Japan — CB matched Dentsu Americas (New York)'),
    'IN-0114':  ('CB=Yogyakarta Indonesia', 'DOWA Holdings HQ is Tokyo Japan — CB matched DOWA Indonesia subsidiary'),
    'IN-0246':  ('CB=São Paulo Brazil', 'NEC Corporation HQ is Tokyo Japan — CB matched NEC Brazil subsidiary'),
    'IN-0248':  ('CB=Tokyo Japan', 'NetEase HQ is Hangzhou China — CB matched NetEase Japan gaming entity'),
    'IN-0264':  ('CB=Singapore', 'Nomura Research Institute HQ is Tokyo Japan — CB matched NRI Singapore branch'),
    'IN-0274':  ('CB=Puteaux France', 'Omnicom Group HQ is New York City — CB matched BBDO or Omnicom France entity'),
    'IN-0275':  ('CB=Langenfeld Germany', 'Omron HQ is Shimogyō-ku Kyoto — CB matched Omron Electronics GmbH (Germany)'),
    'IN-0276':  ('CB=Tokyo Japan', 'ON Semiconductor HQ is Scottsdale AZ — CB matched onsemi Japan entity'),
    'IN-0277':  ('CB=Madrid Spain', 'OpenText HQ is Waterloo Canada — CB matched OpenText Spain office'),
    'IN-0279':  ('CB=Akasaka Tokyo', 'Orange SA HQ is Issy-les-Moulineaux France — CB matched Orange Japan business'),
    'IN-0350':  ('CB=s-Hertogenbosch Netherlands', 'Super Micro Computer HQ is San Jose CA — CB matched SMCI Netherlands entity'),
    'IN-0361':  ('CB=Murfreesboro TN', 'TDK HQ is Minato Tokyo — CB matched TDK US entity (Tennessee has TDK plant)'),
    'IN-0388':  ('CB=Pune India', 'The Trade Desk HQ is Ventura CA — CB matched Trade Desk India office'),
    'IN-0424':  ('CB=Levallois-perret France', 'WPP HQ is London UK — CB matched WPP France entity'),
    'IN-0503':  ('CB=Singapore', 'Arianespace HQ is Évry-Courcouronnes France — CB matched Arianespace Singapore office'),
    'IN-0514':  ('CB=Neuss Germany', 'AVL List HQ is Graz Austria — CB matched AVL Germany entity'),
    'IN-0643':  ('CB=Delft Netherlands', 'Elwave HQ is Carquefou France — CB may have matched a Netherlands spinoff or unrelated entity'),
    'IN-0746':  ('CB=London UK', 'Iknowhow HQ is Athens Greece — CB may have matched a London branch'),
    'IN-0887':  ('CB=Irvine CA', 'Mirion Technologies (MGPI) HQ is Lamanon France — CB matched Mirion Technologies Inc. (US entity, Irvine CA)'),
    'IN-0911':  ('CB=Espoo Finland', 'Nokia Networks France HQ is Massy France — CB matched Nokia parent entity (Espoo = Nokia global HQ)'),
    'IN-1008':  ('CB=Anhausen Germany', 'Rosenbauer HQ is Leonding Austria — CB matched Rosenbauer Germany entity'),
    'IN-1020':  ('CB=Sedziszow Malopolski Poland', 'Safran Aircraft Engines HQ is Courcouronnes France — CB matched a Polish entity (possibly wrong entity entirely)'),
    'IN-1021':  ('CB=Grand Prairie TX', 'Safran Data Systems HQ is Paris France — CB matched US entity in Grand Prairie TX'),
    'IN-1044':  ('CB=Kortrijk Belgium', 'Scioteq HQ is Toulouse France — CB matched a Belgian entity (possible wrong match)'),
    'IN-1087':  ('CB=Stockholm Sweden', 'Spinverse HQ is Espoo Finland — CB matched Stockholm branch or Swedish partner entity'),
    'IN-1132':  ('CB=Austin TX', 'Thales HQ is Meudon France — CB matched Thales USA Austin entity'),
}

for eid, (cb_val, note) in CB_SUBSIDIARY.items():
    e = entities.get(eid)
    if not e:
        continue
    already = any(v.get('status') in ('cb_hq_mismatch_subsidiary', 'cb_hq_mismatch_severe') for v in e.get('validation', []))
    if already:
        print(f"  [SKIP] {eid}: already flagged")
        continue
    print(f"  [CB-SUB] {eid} {e['name']}: {cb_val}")
    if not DRY_RUN:
        add_validation(e, {
            'status': 'cb_hq_mismatch_subsidiary',
            'description': f'CB headquarters ({cb_val}) is for a subsidiary/regional entity, not the parent. {note}',
            'author': 'patch_hq_conflicts2.py',
            'datestamp': TODAY
        })
    stats['cb_subsidiary'] += 1

# ─── WRITE ────────────────────────────────────────────────────────────────────
if not DRY_RUN:
    db['_updated'] = TODAY
    with open('data/database.json', 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"\nWritten: data/database.json")
else:
    print(f"\nDRY RUN — no changes written.")

print(f"\n{'DRY RUN ' if DRY_RUN else ''}Summary:")
print(f"  WD country errors fixed:      {stats['wd_country_fixed']}")
print(f"  Chemring conflict resolved:   {stats['chemring_resolved']}")
print(f"  Dual-location (compatible):   {stats['dual_location']}")
print(f"  CB wrong entity (severe):     {stats['cb_wrong_entity']}")
print(f"  CB subsidiary mismatch:       {stats['cb_subsidiary']}")
