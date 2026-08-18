import json
from collections import Counter, defaultdict

db = json.load(open('data/database.json'))
ents = db['entities']
rels = db['relationships']
by_id = {e['id']: e for e in ents}

def getcountry(e):
    s = e.get('sources', {})
    inf = s.get('infonodes', {}) or {}
    if inf.get('country'):
        return inf['country']
    wd = s.get('wikidata', {}) or {}
    if wd.get('country'):
        return wd['country']
    edf = s.get('edf', {}) or {}
    if edf.get('country'):
        return edf['country']
    cb = s.get('crunchbase', {}) or {}
    hq = cb.get('headquarters')
    if hq:
        parts = [p.strip() for p in hq.split(',')]
        if parts:
            return parts[-1]
    return None

IT_NAMES = {'italy', 'italia', 'it'}
italians = [e for e in ents if (getcountry(e) or '').strip().lower() in IT_NAMES]
it_ids = {e['id'] for e in italians}

# Known data-quality corrections (see reports/italy/index.html caveats):
# - IN-0863 MBDA Espana Sl: wrong wikidata country (EDF source says Spain)
# - IN-1431 Idv Defence Vehicles Italia: duplicate of IN-0803 Iveco Defence
#   Vehicles (same PIC 898895121, same 5 EDF relationships)
it_ids_corrected = it_ids - {'IN-0863', 'IN-1431'}

print(f"=== ORGANIZZAZIONI ITALIANE: {len(italians)} su {len(ents)} totali ({len(italians)/len(ents)*100:.1f}%) ===\n")

# Type breakdown
type_counter = Counter(e['type'] for e in italians)
print("--- Per tipo ---")
for t, c in type_counter.most_common():
    print(f"  {t}: {c}")

# Roles breakdown
role_counter = Counter()
for e in italians:
    for r in (e.get('roles') or []):
        role_counter[r] += 1
print("\n--- Per ruolo ---")
for r, c in role_counter.most_common():
    print(f"  {r}: {c}")

# Sector breakdown
sector_counter = Counter(e.get('sector') or 'N/A' for e in italians)
print("\n--- Per settore ---")
for s, c in sector_counter.most_common():
    print(f"  {s}: {c}")

# Source coverage
src_counter = Counter()
for e in italians:
    s = e.get('sources', {})
    if s.get('ishares'): src_counter['iShares'] += 1
    if s.get('crunchbase'): src_counter['Crunchbase'] += 1
    if s.get('edf'): src_counter['EDF'] += 1
    if s.get('wikidata'): src_counter['Wikidata'] += 1
    if e.get('wikidata_id'): src_counter['has_QID'] += 1
print("\n--- Copertura fonti ---")
for s, c in src_counter.most_common():
    print(f"  {s}: {c}")

# EDF participation - count relationships
edf_rels = [r for r in rels if r['type'] == 'edf_participation' and (r['source'] in it_ids or r['target'] in it_ids)]
print(f"\n--- Partecipazioni EDF (relazioni che coinvolgono entita italiane): {len(edf_rels)} ---")

# distinct EDF projects involving Italy
edf_projects = set()
for r in edf_rels:
    proj = r['source'] if r['source'].startswith('EDF-') else r['target']
    edf_projects.add(proj)
print(f"  Progetti EDF distinti con partecipazione italiana: {len(edf_projects)}")

# Coordinator role check
coord_count = 0
for r in edf_rels:
    if r.get('role') == 'coordinator' or r.get('source_ref','').find('coordinator')>=0:
        coord_count += 1
print(f"  (di cui come coordinator, se marcato nel rel): {coord_count}")

# Investment relationships: Italian companies receiving investment (IN- target)
inv_in = [r for r in rels if r['type'] == 'investment' and r['target'] in it_ids]
print(f"\n--- Investimenti ricevuti da aziende italiane: {len(inv_in)} relazioni ---")
investors_in_italy = Counter(r['source'] for r in inv_in)
print("  Top 10 investitori attivi in Italia:")
for inv_id, c in investors_in_italy.most_common(10):
    name = by_id.get(inv_id, {}).get('name', inv_id)
    print(f"    {name} ({inv_id}): {c} investimenti")

# Italian investors (IV- entities that are italian) investing abroad
it_investors = [e for e in italians if e['type'] in ('investor', 'public_fund')]
print(f"\n--- Investitori italiani nel DB: {len(it_investors)} ---")
it_investor_ids = {e['id'] for e in it_investors}
inv_out = [r for r in rels if r['type'] == 'investment' and r['source'] in it_investor_ids]
print(f"  Investimenti effettuati da investitori italiani: {len(inv_out)}")
targets = Counter(r['target'] for r in inv_out)
print("  Top target (aziende) di investitori italiani:")
for tid, c in targets.most_common(10):
    name = by_id.get(tid, {}).get('name', tid)
    country = getcountry(by_id.get(tid, {}))
    print(f"    {name} ({tid}, {country}): {c}")

# Companies with most investors (Italian companies)
in_companies = [e for e in italians if e['type'] in ('company', 'institution')]
inv_count_per_company = Counter(r['target'] for r in inv_in)
print(f"\n--- Top 10 aziende italiane per numero di investitori ---")
for cid, c in inv_count_per_company.most_common(10):
    name = by_id.get(cid, {}).get('name', cid)
    print(f"    {name} ({cid}): {c} investitori")

# List all italian entities grouped by type for reference
print("\n--- Elenco completo (per tipo) ---")
by_type = defaultdict(list)
for e in italians:
    by_type[e['type']].append(e['name'])
for t, names in by_type.items():
    print(f"\n[{t}] ({len(names)})")
    for n in sorted(names):
        print(f"  - {n}")

# ============================================================
# Chi incassa i fondi EDF: analisi finanziaria (usa it_ids_corrected)
# ============================================================
print("\n\n=== FONDI EDF INCASSATI DA ORGANIZZAZIONI ITALIANE (corretto) ===\n")

edf_rels = [r for r in rels if r['type'] == 'edf_participation' and r['source'] in it_ids_corrected]
total_eu = sum(r.get('eu_contribution') or 0 for r in edf_rels)
n_orgs = len(set(r['source'] for r in edf_rels))
print(f"Totale eu_contribution: EUR {total_eu:,.2f} su {len(edf_rels)} relazioni, {n_orgs} organizzazioni")

per_org = defaultdict(float)
per_org_count = Counter()
for r in edf_rels:
    per_org[r['source']] += r.get('eu_contribution') or 0
    per_org_count[r['source']] += 1

rows = sorted(per_org.items(), key=lambda x: -x[1])
print("\n--- Top 15 beneficiari ---")
cum = 0
for i, (oid, amt) in enumerate(rows[:15]):
    cum += amt
    name = by_id[oid]['name']
    city = (by_id[oid].get('sources', {}).get('edf') or {}).get('city', 'N/D')
    print(f"  {i+1:2d}. {name:45s} {city:20s} EUR {amt:>13,.0f}  ({amt/total_eu*100:4.1f}%)  cum {cum/total_eu*100:5.1f}%  [{per_org_count[oid]} proj]")

# Geographic concentration by city
def norm_city(c):
    if not c:
        return 'N/D'
    c = c.strip().title()
    if c.startswith('Rome') or c.startswith('Roma'):
        return 'Roma'
    return c

city_amount = defaultdict(float)
city_orgs = defaultdict(set)
for r in edf_rels:
    e = by_id[r['source']]
    edf = e.get('sources', {}).get('edf') or {}
    city = norm_city(edf.get('city'))
    city_amount[city] += r.get('eu_contribution') or 0
    city_orgs[city].add(e['name'])

print("\n--- Concentrazione geografica (per citta) ---")
for c, amt in sorted(city_amount.items(), key=lambda x: -x[1])[:10]:
    print(f"  {c:25s} EUR {amt:>13,.0f}  ({amt/total_eu*100:4.1f}%)  [{len(city_orgs[c])} org]")

# SME vs large
sme_amt = defaultdict(float)
for r in edf_rels:
    e = by_id[r['source']]
    edf = e.get('sources', {}).get('edf') or {}
    sme_amt[edf.get('sme')] += r.get('eu_contribution') or 0
print("\n--- PMI (SME) vs grandi imprese ---")
for k, v in sme_amt.items():
    label = 'PMI (SME=True)' if k else 'Grandi imprese/enti (SME=False)'
    print(f"  {label:35s} EUR {v:>13,.0f}  ({v/total_eu*100:4.1f}%)")

# Leonardo as coordinator (flagship projects)
print("\n--- Progetti coordinati da Leonardo (IN-0841) ---")
leo_coord = [r for r in rels if r['source'] == 'IN-0841' and r['type'] == 'edf_participation' and r['role'] == 'coordinator']
for r in leo_coord:
    proj = by_id[r['target']]
    edfp = proj['sources']['edf_project']
    print(f"  {edfp.get('acronym'):10s} {proj['name']:55s} EUR {edfp.get('eu_contribution'):>12}  ({edfp.get('call_title')})")
