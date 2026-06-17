#!/usr/bin/env python3
"""
patch_cb_wrong_matches.py — Fix CB wrong-entity matches (2026-04-24)

Actions:
  A) Downgrade severe→subsidiary: Nintendo, Baltic Workboats, Commercial Metals
  B) Null CB block: BCE, CDW, Fortescue, Informa, Lasertec, Telia, Naval,
                    Patria IN-0951, Tecnobit, Ubitech, Nexa Technologies, United Aircraft
  C) Retire IN-1282 Fortescue Metals Group (duplicate, 0 relationships)
"""
import json, sys
from datetime import date

DRY_RUN = '--dry-run' in sys.argv
TODAY = str(date.today())

with open('data/database.json') as f:
    db = json.load(f)

emap = {e['id']: e for e in db['entities']}
stats = {'downgraded': 0, 'cb_nulled': 0, 'retired': 0}

def add_validation(e, entry):
    e.setdefault('validation', []).append(entry)

def add_history(e, entry):
    e.setdefault('history', []).append(entry)

def remove_severe_flag(e):
    e['validation'] = [v for v in e.get('validation', [])
                       if v.get('status') != 'cb_hq_mismatch_severe']

# ─── A) DOWNGRADE severe → subsidiary ────────────────────────────────────────
DOWNGRADE = {
    'IN-0256': 'CB URL /organization/nintendo matches the real company; description correct. HQ=Los Angeles is Crunchbase internal data error (or US entity address), not a wrong entity match.',
    'IN-0520': 'CB URL /organization/baltic-workboats + description match the real Estonian shipyard. HQ=Coral Gables FL is a Crunchbase data error, not a wrong entity match.',
    'IN-0096': 'CB description and profile match Commercial Metals (metals recycling/trading). HQ=Penrose Wellington NZ may reflect a NZ subsidiary, not the US parent (Irving TX).',
}

for eid, note in DOWNGRADE.items():
    e = emap.get(eid)
    if not e:
        print(f"  [WARN] {eid} not found"); continue
    print(f"  [DOWNGRADE] {eid} {e['name']}: severe → subsidiary")
    if not DRY_RUN:
        remove_severe_flag(e)
        add_validation(e, {
            'status': 'cb_hq_mismatch_subsidiary',
            'description': note,
            'author': 'patch_cb_wrong_matches.py',
            'datestamp': TODAY
        })
    stats['downgraded'] += 1

# ─── B) NULL CB BLOCKS ────────────────────────────────────────────────────────
CB_NULL = {
    'IN-0050': 'BCE (Bell Canada, Montreal) — CB /organization/bce-559b is a door automation company in Alpignano Italy. Completely different entity.',
    'IN-0069': 'CDW (US IT company, Vernon Hills IL) — CB /organization/cdw is a Dutch football sports club. Completely different entity.',
    'IN-0133': 'Fortescue Metals Group (Perth, Australia) — CB /organization/fortescue-zero matched Fortescue Zero (spinoff brand for green energy), not the parent iShares entity.',
    'IN-0172': 'Informa plc (UK multinational publishing) — CB /organization/informa-f84c is a German digital marketing agency. Completely different entity.',
    'IN-0209': 'Lasertec Corporation (Japan semiconductor inspection) — CB /organization/lasertec-d212 is a Polish laser equipment/toner company. Completely different entity.',
    'IN-0371': 'Telia Company (Swedish telecom) — CB /organization/telia-08f5 is a Greek web content management company. Completely different entity.',
    'IN-0899': 'Naval Group (French naval defence) — CB /organization/naval-71ea is Naval Válvulas (Brazilian industrial valve manufacturer). Completely different entity.',
    'IN-0951': 'Patria Group (Finnish defence) — CB /organization/patria is a Bratislava Slovakia import/export trading company. Completely different entity. Subsidiaries IN-0952/0953/0954 unaffected.',
    'IN-1117': 'Tecnobit SL (Spanish defence electronics, Alcobendas) — CB /organization/tecnobit-5639 is an Italian 2D/CAD/3D modelling software company. Completely different entity.',
    'IN-1163': 'Ubitech (Greek cybersecurity/software, Athens) — CB /organization/ubitech-ecb1 is a Chinese company (Jintan, Jiangsu). Completely different entity.',
    'IN-1315': 'Nexa Technologies (French networking/IoT, Aix-en-Provence) — CB /organization/nexa-technologies is a US trading technology provider (Richardson TX). Completely different entity.',
    'IN-1341': 'United Aircraft Corporation (Russian aerospace holding, Moscow) — CB /organization/united-aircraft-68e4 is a Chinese drone manufacturer (Shenzhen). Completely different entity.',
}

for eid, note in CB_NULL.items():
    e = emap.get(eid)
    if not e:
        print(f"  [WARN] {eid} not found"); continue
    sources = e.get('sources') or {}
    cb = sources.get('crunchbase') or {}
    old_url = cb.get('profile_url', 'unknown')
    if not cb:
        print(f"  [SKIP] {eid}: no CB block")
        continue
    print(f"  [NULL-CB] {eid} {e['name']}: nulling CB (was {old_url})")
    if not DRY_RUN:
        sources['crunchbase'] = None
        remove_severe_flag(e)
        add_validation(e, {
            'status': 'cb_wrong_entity',
            'description': note,
            'cb_url_removed': old_url,
            'author': 'patch_cb_wrong_matches.py',
            'datestamp': TODAY
        })
        add_history(e, {
            'action': 'field_corrected',
            'field': 'sources.crunchbase',
            'old_value': old_url,
            'new_value': None,
            'note': note,
            'author': 'patch_cb_wrong_matches.py',
            'datestamp': TODAY
        })
    stats['cb_nulled'] += 1

# ─── C) RETIRE IN-1282 ────────────────────────────────────────────────────────
e = emap.get('IN-1282')
if e:
    already_retired = any(v.get('status') == 'retired' for v in e.get('validation', []))
    if already_retired:
        print(f"  [SKIP] IN-1282: already retired")
    else:
        print(f"  [RETIRE] IN-1282 Fortescue Metals Group: duplicate of IN-0133")
        if not DRY_RUN:
            add_validation(e, {
                'status': 'retired',
                'description': 'Duplicate of IN-0133 (Fortescue). Migrated from old DB via import_by_wikidata.py; wikidata_id already nulled as qid_nulled_duplicate. 0 relationships. Canonical entity is IN-0133.',
                'canonical': 'IN-0133',
                'author': 'patch_cb_wrong_matches.py',
                'datestamp': TODAY
            })
            add_history(e, {
                'action': 'entity_retired',
                'note': 'Duplicate of IN-0133 (Fortescue). No relationships; wikidata_id was already nulled.',
                'canonical': 'IN-0133',
                'author': 'patch_cb_wrong_matches.py',
                'datestamp': TODAY
            })
        stats['retired'] += 1

# ─── WRITE ────────────────────────────────────────────────────────────────────
if not DRY_RUN:
    db['_updated'] = TODAY
    with open('data/database.json', 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"\nWritten: data/database.json")
else:
    print(f"\nDRY RUN — no changes written.")

print(f"\n{'DRY RUN ' if DRY_RUN else ''}Summary:")
print(f"  Downgraded severe→subsidiary: {stats['downgraded']}")
print(f"  CB blocks nulled:             {stats['cb_nulled']}")
print(f"  Entities retired:             {stats['retired']}")
