#!/usr/bin/env python3
"""
patch_orange_cb.py — Fix wrong CB match for IN-0279 Orange SA (2026-10-19)

Reported by an external reader of the MITL site: IN-0279 showed the CB profile of
Orange Inc. (Tokyo, AI for comics, /organization/orange-ac33) instead of Orange SA
(French telecom).

Actions:
  A) Null the wrong sources.crunchbase block of IN-0279, then set a minimal block
     holding only the CB profile URL verified by hand (/organization/orange)
  B) Remove the 5 investment relationships generated from the wrong top_investors
  C) Retire the 3 investors left with no relationships (IV-0388, IV-0391, IV-0487);
     IV-0396 MUFG Bank and IV-0390 Mizuho Bank keep their other relationships

Usage: python3 scripts/patch_orange_cb.py [--dry-run]
"""
import json, sys
from datetime import date

DRY_RUN = '--dry-run' in sys.argv
TODAY = str(date.today())
AUTHOR = 'patch_orange_cb.py'

ORANGE = 'IN-0279'
NEW_CB_URL = 'https://www.crunchbase.com/organization/orange'
ORPHANS = ['IV-0388', 'IV-0391', 'IV-0487']

with open('data/database.json') as f:
    db = json.load(f)

emap = {e['id']: e for e in db['entities']}
orange = emap[ORANGE]

# ─── A) CB BLOCK ──────────────────────────────────────────────────────────────
old_cb = (orange.get('sources') or {}).get('crunchbase') or {}
old_url = old_cb.get('profile_url')
if old_url == NEW_CB_URL:
    print(f"  [SKIP] {ORANGE}: already on {NEW_CB_URL}")
else:
    note = ('Orange SA (French telecom, Issy-les-Moulineaux) — CB /organization/orange-ac33 is Orange Inc. '
            '(Tokyo, AI models for comics). Completely different entity. Correct profile verified manually: '
            f'{NEW_CB_URL}. Investors from the wrong block (5 JP banks/VCs) removed.')
    print(f"  [CB] {ORANGE} {orange['name']}: {old_url} → {NEW_CB_URL}")
    if not DRY_RUN:
        orange['sources']['crunchbase'] = {
            'extracted_at': TODAY,
            'source_file': 'manual',
            'profile_url': NEW_CB_URL,
        }
        orange.setdefault('validation', []).append({
            'status': 'cb_wrong_entity',
            'description': note,
            'cb_url_removed': old_url,
            'author': AUTHOR,
            'datestamp': TODAY,
        })
        orange.setdefault('history', []).append({
            'action': 'field_corrected',
            'field': 'sources.crunchbase',
            'old_value': old_url,
            'new_value': NEW_CB_URL,
            'note': note,
            'author': AUTHOR,
            'datestamp': TODAY,
        })

# ─── B) RELATIONSHIPS ─────────────────────────────────────────────────────────
to_remove = [r for r in db['relationships']
             if r['target'] == ORANGE and r.get('source_ref') == 'crunchbase_top_investors']
for r in to_remove:
    print(f"  [REL] remove {r['source']} → {r['target']} ({emap[r['source']]['name']})")
if not DRY_RUN:
    removed_ids = {id(r) for r in to_remove}
    db['relationships'] = [r for r in db['relationships'] if id(r) not in removed_ids]
    for r in to_remove:
        emap[r['source']].setdefault('history', []).append({
            'action': 'relationship_removed',
            'target': ORANGE,
            'note': 'Investment in IN-0279 came from the wrong CB block (Orange Inc., Tokyo), not Orange SA.',
            'author': AUTHOR,
            'datestamp': TODAY,
        })

# ─── C) RETIRE ORPHANS ────────────────────────────────────────────────────────
for iid in ORPHANS:
    e = emap[iid]
    rels = [r for r in db['relationships']
            if iid in (r['source'], r['target']) and r not in to_remove]
    if rels:
        print(f"  [WARN] {iid} {e['name']}: still has {len(rels)} relationships — not retired")
        continue
    if any(h.get('action') == 'entity_retired' for h in e.get('history', [])):
        print(f"  [SKIP] {iid}: already retired")
        continue
    note = ('Only relationship was investment in IN-0279 Orange SA, generated from a wrong CB match '
            '(removed 2026-10-19). Archived with no valid relationships; no canonical entity. '
            'Remove this entry if a later cycle links it to other companies.')
    print(f"  [RETIRE] {iid} {e['name']}")
    if not DRY_RUN:
        e.setdefault('validation', []).append({
            'status': 'retired',
            'description': note,
            'canonical': None,
            'author': AUTHOR,
            'datestamp': TODAY,
        })
        e.setdefault('history', []).append({
            'action': 'entity_retired',
            'note': note,
            'canonical': None,
            'author': AUTHOR,
            'datestamp': TODAY,
        })

# ─── WRITE ────────────────────────────────────────────────────────────────────
if not DRY_RUN:
    db['_updated'] = TODAY
    with open('data/database.json', 'w') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print("\nWritten: data/database.json")
else:
    print("\nDRY RUN — no changes written.")
