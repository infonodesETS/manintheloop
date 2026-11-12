"""Costruisce tmp/sec-test/sec-test.json dai CSV SEC + join_aziende.json.
NON tocca data/database.json. Id provvisori: PER-T#### e IV-T#### (T = test)."""
import csv, json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEC = ROOT / "rawdata/sec-edgar/2026-10-17"
OUT = Path(__file__).resolve().parent
rd = lambda n: list(csv.DictReader(open(SEC / f"{n}.csv")))

db = json.load(open(ROOT / "data/database.json"))
ents = {e["id"]: e for e in db["entities"]}
join = json.load(open(OUT / "join_aziende.json"))          # ticker SEC -> [IN-]
aziende = {a["ticker"]: a for a in rd("aziende")}
SRC_DATE = "2026-10-17"

def key(name):                                              # nome gestore normalizzato
    n = re.sub(r"[^\w ]", " ", name.lower())
    n = re.sub(r"^the ", "", n.strip())
    n = re.sub(r"\b(inc|llc|lp|l p|corp|corporation|ltd|plc|co|company)\b", " ", n)
    return " ".join(n.split())

def b(v): return str(v).strip().lower() == "true"

# ---- PER- provvisori (id dataset P#### -> PER-T####) ----
per = {}
for p in rd("persone"):
    pid = p["persona_id"]
    per[pid] = {"id": "PER-T" + pid[1:], "type": "person", "name": p["nome"],
                "aliases": [x for x in p["altre_grafie"].split(";") if x.strip()] if p["altre_grafie"] else [],
                "sources": {"sec": {"persona_id": pid, "release": SRC_DATE}}}

# ---- IV- dei detentori entity: aggancio a IV- esistenti per nome, altrimenti nuovo IV-T ----
iv_exist = {}
for e in ents.values():
    if e["id"].startswith("IV-"):
        iv_exist.setdefault(key(e["name"]), e["id"])
iv_new, iv_variants = {}, defaultdict(set)
def holder_id(name):
    k = key(name); iv_variants[k].add(name)
    if k in iv_exist: return iv_exist[k], False
    if k not in iv_new:
        iv_new[k] = {"id": f"IV-T{len(iv_new)+1:04d}", "type": "investor", "name": name,
                     "sources": {"sec": {"release": SRC_DATE, "role": "holder_over_5pct"}}}
    return iv_new[k]["id"], True

rels, sec_block = [], {}
for t, a in aziende.items():
    for in_id in join[t]:                                    # doppie classi: stesso blocco su entrambe
        sec_block[in_id] = {"cik": a["cik"], "ticker": t, "proxy_filed": a["proxy_depositato_il"],
                            "proxy_url": a["proxy_url"], "shares_as_of": a["quote_al"],
                            "release": SRC_DATE}
def add(typ, src, tgt, **kw): rels.append({"type": typ, "source": src, "target": tgt, **kw})

comm = defaultdict(list)
for c in rd("comitati"):
    comm[(c["ticker"], c["persona_id"])].append({"committee": c["comitato"], "chair": b(c["presidente"])})

for c in rd("consiglieri"):
    for in_id in join[c["ticker"]]:
        add("board_membership", per[c["persona_id"]]["id"], in_id, roles=c["cariche"],
            since=c["nel_consiglio_dal"] or None, independent=b(c["indipendente"]),
            committees=comm.get((c["ticker"], c["persona_id"]), []))
for d in rd("dirigenti"):
    for in_id in join[d["ticker"]]:
        add("executive_officer", per[d["persona_id"]]["id"], in_id, roles=d["cariche"],
            age=d["eta"] or None, doc=d["fonte"])
n_unres = 0
for h in rd("detentori-oltre-5"):
    if h["tipo"] == "person" and h["persona_id"]:
        src = per[h["persona_id"]]["id"]
    elif h["tipo"] == "entity":
        src, _ = holder_id(h["nome"])
    else: n_unres += 1; continue
    for in_id in join[h["ticker"]]:
        add("shareholder_5pct", src, in_id, share_class=h["classe"], shares=h["azioni"] or None,
            pct=h["percentuale"] or None, vote_pct=h["percentuale_voti"] or None, filing=h["fonte_dichiarazione"])

out = {"_note": "TEST - non fa parte del DB. Id PER-T/IV-T provvisori.",
       "sec_blocks": sec_block, "persons": list(per.values()),
       "new_investors": list(iv_new.values()), "relationships": rels}
json.dump(out, open(OUT / "sec-test.json", "w"), ensure_ascii=False)

# ---- report ----
from collections import Counter
print("sec_blocks su IN-:", len(sec_block), "| PER-T:", len(per), "| IV-T nuovi:", len(iv_new),
      "| IV- esistenti agganciati:", len({v for k,v in iv_exist.items() if k in iv_variants}), "| detentori irrisolti:", n_unres)
print("relazioni:", dict(Counter(r["type"] for r in rels)))
print("varianti unificate sotto la stessa chiave:")
for k, v in sorted(iv_variants.items(), key=lambda x: -len(x[1])):
    if len(v) > 1: print("  ", sorted(v))
print("gestori con più IN- :", Counter(r["source"] for r in rels if r["type"]=="shareholder_5pct" and r["source"].startswith("IV")).most_common(6))
print("IV- esistenti agganciati:", [(ents[i]["id"], ents[i]["name"]) for k,i in iv_exist.items() if k in iv_variants][:10])
