"""
Generate statistical charts for report1.md
Run from refactoringDB/: python3 reports/generate_charts.py
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path

# --- Config ---
OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)
DB_PATH = Path(__file__).parent.parent / "data" / "database.json"

DARK_BG = "#1a1a1a"
ACCENT = "#4fa8a8"
ACCENT2 = "#e07b54"
ACCENT3 = "#7bbf6a"
GREY = "#888888"
TEXT = "#e0e0e0"
GRID = "#2e2e2e"

def style_ax(ax, title=None):
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.spines['bottom'].set_color(GRID)
    ax.spines['left'].set_color(GRID)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.label.set_color(TEXT)
    ax.xaxis.label.set_color(TEXT)
    if title:
        ax.set_title(title, color=TEXT, fontsize=11, fontweight='bold', pad=10)

def save(fig, name):
    fig.patch.set_facecolor(DARK_BG)
    fig.savefig(OUT / name, dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close(fig)
    print(f"  saved {name}")

# --- Load data ---
with open(DB_PATH) as f:
    db = json.load(f)

entities = db['entities']
rels = db['relationships']
entity_map = {e['id']: e for e in entities}

def get_country(e):
    if e is None: return None
    s = e.get('sources') or {}
    for k in ['infonodes', 'wikidata', 'edf_org']:
        v = (s.get(k) or {}).get('country')
        if v: return v
    return None

edf_rels = [r for r in rels if r['type'] == 'edf_participation']
inv_rels = [r for r in rels if r['type'] == 'investment']
edf_company_ids = {r['source'] for r in edf_rels}
ishares_ids = set(e['id'] for e in entities if (e.get('sources') or {}).get('ishares'))

print("Generating charts...")

# ---------------------------------------------------------------
# ANGOLO 1 — Chi controlla la difesa EU?
# ---------------------------------------------------------------

# 01 — Top coordinators
print("01")
coord_count = Counter(r['source'] for r in edf_rels if r['role'] == 'coordinator')
top_coords = coord_count.most_common(10)
names = [entity_map[eid]['name'].title()[:35] for eid, _ in top_coords]
values = [n for _, n in top_coords]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(names[::-1], values[::-1], color=ACCENT, height=0.6)
for bar, v in zip(bars, values[::-1]):
    ax.text(v + 0.05, bar.get_y() + bar.get_height()/2, str(v),
            va='center', color=TEXT, fontsize=9)
ax.set_xlabel("Numero di progetti coordinati", color=TEXT)
style_ax(ax, "Chi guida i consorzi EDF? — Top 10 coordinatori")
ax.set_xlim(0, max(values) + 1)
save(fig, "01-top-coordinators.png")

# 02 — Concentration: top 5 countries share of coordinator roles
print("02")
country_coord = Counter()
for r in edf_rels:
    if r['role'] == 'coordinator':
        e = entity_map.get(r['source'])
        c = get_country(e)
        if c:
            country_coord[c] += 1

top5_coord = country_coord.most_common(5)
other = sum(v for k, v in country_coord.items() if k not in dict(top5_coord))
labels = [k for k, _ in top5_coord] + ['Altro']
sizes = [v for _, v in top5_coord] + [other]
colors = [ACCENT, ACCENT2, ACCENT3, "#c488c4", "#e0c060", GREY]

fig, ax = plt.subplots(figsize=(7, 5))
wedges, texts, autotexts = ax.pie(
    sizes, labels=labels, autopct='%1.0f%%',
    colors=colors, startangle=140,
    textprops={'color': TEXT, 'fontsize': 9},
    pctdistance=0.75,
    wedgeprops=dict(linewidth=0.5, edgecolor=DARK_BG)
)
for at in autotexts:
    at.set_color(DARK_BG)
    at.set_fontsize(8)
    at.set_fontweight('bold')
ax.set_title("Distribuzione dei ruoli di coordinamento EDF per paese", color=TEXT, fontsize=11, fontweight='bold')
save(fig, "02-coordinator-countries.png")

# ---------------------------------------------------------------
# ANGOLO 2 — Dove va il soldo pubblico?
# ---------------------------------------------------------------

# 03 — EU contribution per country
print("03")
country_eu = defaultdict(float)
for r in edf_rels:
    e = entity_map.get(r['source'])
    c = get_country(e)
    if c:
        country_eu[c] += r.get('eu_contribution', 0) or 0

top_eu = sorted(country_eu.items(), key=lambda x: -x[1])[:12]
countries = [k for k, _ in top_eu]
vals = [v / 1e6 for _, v in top_eu]

fig, ax = plt.subplots(figsize=(9, 5))
bar_colors = [ACCENT if i < 5 else ACCENT2 for i in range(len(countries))]
bars = ax.bar(countries, vals, color=bar_colors, width=0.6)
for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{v:.0f}M', ha='center', color=TEXT, fontsize=8)
ax.set_ylabel("Contributo EU (M€)", color=TEXT)
ax.set_xticklabels(countries, rotation=30, ha='right', color=TEXT, fontsize=9)
style_ax(ax, "Contributo EDF per paese — Top 12 (M€)")
ax.yaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
save(fig, "03-eu-contribution-by-country.png")

# 04 — Top 15 companies by EU contribution
print("04")
comp_eu = defaultdict(float)
for r in edf_rels:
    e = entity_map.get(r['source'])
    if e:
        comp_eu[e['name']] += r.get('eu_contribution', 0) or 0

top_comp = sorted(comp_eu.items(), key=lambda x: -x[1])[:12]
cnames = [n.title()[:32] for n, _ in top_comp]
cvals = [v / 1e6 for _, v in top_comp]

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh(cnames[::-1], cvals[::-1], color=ACCENT2, height=0.6)
for bar, v in zip(bars, cvals[::-1]):
    ax.text(v + 0.5, bar.get_y() + bar.get_height()/2, f'{v:.1f}M',
            va='center', color=TEXT, fontsize=8)
ax.set_xlabel("Contributo EU ricevuto (M€)", color=TEXT)
style_ax(ax, "Top 12 aziende per contributo EDF ricevuto")
ax.xaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
save(fig, "04-top-companies-eu.png")

# 05 — Dual exposure: iShares + EDF
print("05")
dual = ishares_ids & edf_company_ids
ishares_only = ishares_ids - edf_company_ids
edf_only = edf_company_ids - ishares_ids

# Stacked bar showing universe composition
categories = ['iShares ETF\n(511 entità)', 'EDF Partecipanti\n(794 entità)']
in_both = [len(dual), len(dual)]
exclusive = [len(ishares_only), len(edf_only)]

fig, ax = plt.subplots(figsize=(7, 4))
x = np.arange(len(categories))
b1 = ax.bar(x, exclusive, color=[ACCENT, ACCENT2], width=0.5, label='Esclusivo')
b2 = ax.bar(x, in_both, bottom=exclusive, color=ACCENT3, width=0.5, label=f'Presente in entrambi ({len(dual)})')
ax.set_xticks(x)
ax.set_xticklabels(categories, color=TEXT, fontsize=10)
ax.set_ylabel("Numero di entità", color=TEXT)
ax.legend(facecolor='#2a2a2a', edgecolor=GRID, labelcolor=TEXT, fontsize=9)
style_ax(ax, "Sovrapposizione tra universo ETF e universo EDF")
ax.yaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
for bar in list(b1) + list(b2):
    h = bar.get_height()
    if h > 10:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + h/2,
                str(int(h)), ha='center', va='center', color=DARK_BG, fontsize=9, fontweight='bold')
save(fig, "05-dual-exposure-etf-edf.png")

# ---------------------------------------------------------------
# ANGOLO 3 — Chi sono i nuovi player?
# ---------------------------------------------------------------

# 06 — Funding stage for EDF companies
print("06")
stages = Counter()
for eid in edf_company_ids:
    e = entity_map.get(eid)
    if not e: continue
    cb = (e.get('sources') or {}).get('crunchbase') or {}
    stage = cb.get('funding_status') or cb.get('last_funding_type') or 'Senza dati CB'
    if not stage:
        stage = 'Senza dati CB'
    stages[stage] += 1

# Group rare categories
RENAME = {
    'M&A': 'M&A / Acquisizione',
    'IPO': 'IPO (quotate)',
    'Grant': 'Grant',
    'Seed': 'Seed',
    'Early Stage Venture': 'Early Venture',
    'Venture - Series Unknown': 'Venture',
    'Late Stage Venture': 'Late Venture',
    'Debt Financing': 'Debt',
    'Private Equity': 'Private Equity',
    'Corporate Round': 'Corporate Round',
    'Non-equity Assistance': 'Non-equity',
    'Undisclosed': 'Non-equity',
    'Senza dati CB': 'Senza dati CB',
    'Unknown': 'Senza dati CB',
}
grouped = Counter()
for k, v in stages.items():
    grouped[RENAME.get(k, k)] += v

top_stages = grouped.most_common()
sl = [s for s, _ in top_stages if s != 'Senza dati CB']
sv = [v for s, v in top_stages if s != 'Senza dati CB']
no_cb = grouped.get('Senza dati CB', 0)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
stage_colors = [ACCENT, ACCENT2, ACCENT3, "#c488c4", "#e0c060", "#60a0e0", "#e08060", GREY]
bars = ax1.barh(sl[::-1], sv[::-1], color=stage_colors[:len(sl)], height=0.6)
for bar, v in zip(bars, sv[::-1]):
    ax1.text(v + 0.5, bar.get_y() + bar.get_height()/2, str(v),
             va='center', color=TEXT, fontsize=9)
style_ax(ax1, "Fase di finanziamento (aziende EDF con dati CB)")
ax1.set_xlabel("Numero di aziende", color=TEXT)

# Pie: CB coverage
ax2.pie(
    [794 - no_cb, no_cb],
    labels=[f'Con dati CB\n({794-no_cb})', f'Senza dati CB\n({no_cb})'],
    colors=[ACCENT, GREY],
    startangle=90,
    textprops={'color': TEXT, 'fontsize': 10},
    wedgeprops=dict(linewidth=0.5, edgecolor=DARK_BG),
    autopct='%1.0f%%',
    pctdistance=0.7
)
ax2.set_title("Copertura Crunchbase\nsui partecipanti EDF", color=TEXT, fontsize=10, fontweight='bold')
for t in ax2.texts:
    if '%' in t.get_text():
        t.set_color(DARK_BG)
        t.set_fontweight('bold')

save(fig, "06-funding-stages-edf.png")

# 07 — Investor country origin for EDF companies
print("07")
inv_country_edf = Counter()
for r in inv_rels:
    if r['target'] in edf_company_ids:
        iv = entity_map.get(r['source'])
        c = get_country(iv)
        inv_country_edf[c or 'Sconosciuto'] += 1

top_ic = [(c, n) for c, n in inv_country_edf.most_common(10) if c != 'Sconosciuto']
ic_labels = [c for c, _ in top_ic]
ic_vals = [n for _, n in top_ic]

fig, ax = plt.subplots(figsize=(9, 5))
eu_countries = {'France', 'Germany', 'Belgium', 'Spain', 'Italy', 'Sweden',
                'Finland', 'Netherlands', 'Estonia', 'Poland', 'Luxembourg'}
bar_colors = [ACCENT if c in eu_countries else ACCENT2 for c in ic_labels]
bars = ax.bar(ic_labels, ic_vals, color=bar_colors, width=0.6)
for bar, v in zip(bars, ic_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(v), ha='center', color=TEXT, fontsize=9)
ax.set_xticklabels(ic_labels, rotation=30, ha='right', color=TEXT, fontsize=9)
ax.set_ylabel("Numero di relazioni di investimento", color=TEXT)
eu_patch = mpatches.Patch(color=ACCENT, label='Paese EU/EEA')
us_patch = mpatches.Patch(color=ACCENT2, label='Paese extra-EU')
ax.legend(handles=[eu_patch, us_patch], facecolor='#2a2a2a', edgecolor=GRID, labelcolor=TEXT, fontsize=9)
style_ax(ax, "Origine geografica degli investitori nelle aziende EDF")
ax.yaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
save(fig, "07-investor-countries-edf.png")

# 08 — Cross-border investment flows (top 10)
print("08")
flow = Counter()
for r in inv_rels:
    iv = entity_map.get(r['source'])
    tgt = entity_map.get(r['target'])
    sc = get_country(iv)
    tc = get_country(tgt)
    if sc and tc and sc != tc:
        flow[(sc, tc)] += 1

top_flow = flow.most_common(12)
flow_labels = [f"{sc[:14]} → {tc[:14]}" for (sc, tc), _ in top_flow]
flow_vals = [n for _, n in top_flow]

fig, ax = plt.subplots(figsize=(9, 5.5))
colors_flow = [ACCENT2 if 'United States' in fl else ACCENT for fl in flow_labels]
bars = ax.barh(flow_labels[::-1], flow_vals[::-1], color=colors_flow[::-1], height=0.6)
for bar, v in zip(bars, flow_vals[::-1]):
    ax.text(v + 0.2, bar.get_y() + bar.get_height()/2, str(v),
            va='center', color=TEXT, fontsize=9)
style_ax(ax, "Top 12 flussi di investimento cross-border")
ax.set_xlabel("Numero di relazioni di investimento", color=TEXT)
ax.xaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
save(fig, "08-crossborder-flows.png")

# 09 — GICS sector distribution (iShares)
print("09")
gics_map = {'45': 'Technology', '50': 'Comm Services', '151040': 'Mining', '201010': 'Aeros. & Defence'}
gics_count = Counter()
for e in entities:
    ish = (e.get('sources') or {}).get('ishares') or []
    seen = set()
    for i in ish:
        gc = str(i.get('gics_code', ''))
        label = gics_map.get(gc, gc)
        if label not in seen:
            gics_count[label] += 1
            seen.add(label)

fig, ax = plt.subplots(figsize=(7, 4))
glabels = list(gics_count.keys())
gvals = list(gics_count.values())
gcolors = [ACCENT, ACCENT2, ACCENT3, "#c488c4"]
bars = ax.bar(glabels, gvals, color=gcolors[:len(glabels)], width=0.5)
for bar, v in zip(bars, gvals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            str(v), ha='center', color=TEXT, fontsize=10, fontweight='bold')
ax.set_ylabel("Numero di aziende", color=TEXT)
style_ax(ax, "Distribuzione ETF iShares per settore GICS")
ax.yaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
save(fig, "09-gics-sectors.png")

# 10 — Top investors by portfolio size
print("10")
inv_portfolio = Counter(r['source'] for r in inv_rels)
top_inv = inv_portfolio.most_common(12)
inv_names = []
inv_vals = []
inv_countries = []
for iv_id, cnt in top_inv:
    iv = entity_map.get(iv_id)
    inv_names.append((iv['name'] if iv else iv_id)[:30])
    inv_vals.append(cnt)
    inv_countries.append(get_country(iv) or '?')

fig, ax = plt.subplots(figsize=(9, 5.5))
bar_cols = [ACCENT if 'Belgium' in c or 'France' in c or 'Luxembourg' in c or 'Finland' in c or 'Germany' in c
            else ACCENT2 for c in inv_countries]
bars = ax.barh(
    [f"{n}\n({c})" for n, c in zip(inv_names, inv_countries)][::-1],
    inv_vals[::-1],
    color=bar_cols[::-1], height=0.6
)
for bar, v in zip(bars, inv_vals[::-1]):
    ax.text(v + 0.2, bar.get_y() + bar.get_height()/2, str(v),
            va='center', color=TEXT, fontsize=9)
style_ax(ax, "Top 12 investitori per dimensione del portafoglio")
ax.set_xlabel("Numero di aziende in portafoglio", color=TEXT)
eu_patch = mpatches.Patch(color=ACCENT, label='Investitore EU/EEA')
us_patch = mpatches.Patch(color=ACCENT2, label='Investitore extra-EU')
ax.legend(handles=[eu_patch, us_patch], facecolor='#2a2a2a', edgecolor=GRID, labelcolor=TEXT, fontsize=9)
ax.xaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
save(fig, "10-top-investors-portfolio.png")

print("\nAll charts generated.")
