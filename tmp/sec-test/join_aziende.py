"""Join SEC (perimetro.csv) -> entita IN- del DB. Sola lettura sul DB.
Chiave: ticker iShares + ETF (+ paese per disambiguare). Scrive tmp/sec-test/join_aziende.json e stampa il report."""
import csv, json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEC = ROOT / "rawdata/sec-edgar/2026-10-17"
OUT = Path(__file__).resolve().parent

db = json.load(open(ROOT / "data/database.json"))
ents = {e["id"]: e for e in db["entities"]}
retired = {e["id"] for e in ents.values()
           if any(h.get("action") == "entity_retired" for h in e.get("history", []))}

by_key = defaultdict(set)      # (etf, ticker) -> ids
for e in ents.values():
    for s in e.get("sources", {}).get("ishares") or []:
        by_key[(s.get("etf_ticker"), s.get("stock_ticker"))].add(e["id"])

PAESI = {"Stati Uniti": "United States"}   # DFND e in locale italiano
def norm(s): return re.sub(r"\W", "", (s or "").lower())

az = {a["ticker"]: a for a in csv.DictReader(open(SEC / "aziende.csv"))}
cik2t = {a["cik"]: t for t, a in az.items()}   # le doppie classi condividono il CIK
rows = [r for r in csv.DictReader(open(SEC / "perimetro.csv")) if r["sec_esito"] == "estraibile"]

result, report = {}, defaultdict(list)
for r in rows:
    ids = {i for i in by_key.get((r["etf"], r["ticker"]), ()) if i not in retired}
    if len(ids) > 1:                                  # disambigua col paese iShares
        ids = {i for i in ids if any(s.get("location") == PAESI.get(r["paese_ishares"], r["paese_ishares"])
               for s in ents[i]["sources"]["ishares"])} or ids
    sec_t = cik2t[r["sec_cik"]]
    if len(ids) == 1:
        report["ok"].append((r["ticker"], r["nome"], next(iter(ids))))
        result.setdefault(sec_t, set()).add(next(iter(ids)))
    elif not ids:
        report["nessun_match"].append((r["ticker"], r["etf"], r["nome"]))
    else:
        report["ambiguo"].append((r["ticker"], r["etf"], r["nome"], sorted(ids)))

# aziende SEC con piu IN- (doppie classi) o nessuna
out = {t: sorted(v) for t, v in result.items()}
senza = [t for t in az if t not in out]
json.dump(out, open(OUT / "join_aziende.json", "w"), indent=1)
print(f"righe estraibili nel perimetro: {len(rows)}  -> aziende SEC: {len(az)}")
print(f"match univoco: {len(report['ok'])}  | nessun match: {len(report['nessun_match'])}  | ambigui: {len(report['ambiguo'])}")
print(f"aziende SEC con almeno una IN-: {len(out)}  | senza: {senza}")
print("più IN- per una azienda SEC:", {t: v for t, v in out.items() if len(v) > 1})
for k in ("nessun_match", "ambiguo"):
    for x in report[k]: print(k, x)
