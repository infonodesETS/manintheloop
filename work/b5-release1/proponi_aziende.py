#!/usr/bin/env python3
"""B5 Release 1, passo 2a: PROPOSTA della tabella ticker SEC -> schede IN- del database.

Sola lettura: legge rawdata/sec-edgar/2026-10-17/ e docs/data/database.json,
scrive solo work/b5-release1/proposta-aziende.csv. Non modifica il database.
La tabella e una proposta: la rivede una persona (S3 R3). Dove non e certa
la proposta e vuota e la riga e segnata «da decidere».
Uso: python3 -I work/b5-release1/proponi_aziende.py
"""
import csv, json, re, collections, pathlib, unicodedata

RAIZ = pathlib.Path(__file__).resolve().parents[2]
REL = RAIZ / "rawdata/sec-edgar/2026-10-17"
OUT = RAIZ / "work/b5-release1/proposta-aziende.csv"

SUFFISSI = {"inc", "corp", "corporation", "co", "company", "ltd", "limited", "plc", "llc", "lp",
            "holdings", "holding", "group", "class", "a", "b", "c", "the", "sa", "nv", "ag",
            "technologies", "technology", "inc.", "incorporated", "de", "cl"}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(w for w in s.split() if w not in SUFFISSI)


def ritirata(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def main():
    db = json.load(open(RAIZ / "docs/data/database.json", encoding="utf-8"))
    ents = [e for e in db["entities"] if e["id"].startswith("IN-") and not ritirata(e)]
    per_ticker = collections.defaultdict(list)
    per_nome = collections.defaultdict(list)
    for e in ents:
        for x in (e.get("sources", {}).get("ishares") or []):
            t = (x.get("stock_ticker") or "").strip().upper()
            if t:
                per_ticker[t].append(e["id"])
        per_nome[norm(e["name"])].append(e["id"])
    nome_di = {e["id"]: e["name"] for e in ents}

    aziende = list(csv.DictReader(open(REL / "aziende.csv", encoding="utf-8")))
    det = list(csv.DictReader(open(REL / "detentori-oltre-5.csv", encoding="utf-8")))
    classi = collections.defaultdict(collections.Counter)
    for r in det:
        classi[r["ticker"]][r["classe"]] += 1

    righe = []
    for a in aziende:
        t = a["ticker"]
        if t not in classi:      # nessun detentore oltre soglia: non serve alla Release 1
            continue
        cand_t = sorted(set(per_ticker.get(t.upper(), [])))
        cand_n = sorted(set(per_nome.get(norm(a["azienda"]), [])))
        tutti = sorted(set(cand_t) | set(cand_n))
        if len(cand_t) == 1 and (not cand_n or cand_t == cand_n):
            prop, stato = cand_t[0], "proposta (ticker iShares" + (" + nome)" if cand_n else ")")
        elif len(cand_t) == 0 and len(cand_n) == 1:
            prop, stato = cand_n[0], "proposta debole (solo nome): da confermare"
        elif not tutti:
            prop, stato = "", "nessuna scheda trovata: nuova entita o da cercare a mano"
        else:
            prop, stato = "", "da decidere: candidati multipli o in disaccordo"
        righe.append({
            "ticker": t, "azienda_sec": a["azienda"], "cik": a["cik"],
            "classi_nel_sec": "; ".join(f"{c} ({n})" for c, n in classi[t].most_common()),
            "n_classi": len(classi[t]),
            "candidati_per_ticker": " ".join(cand_t),
            "candidati_per_nome": " ".join(cand_n),
            "nomi_candidati": " | ".join(f"{i}={nome_di[i]}" for i in tutti),
            "proposta_id": prop, "stato": stato,
            "revisione_nelson": "", "nota": "",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)
    c = collections.Counter(r["stato"].split(" (")[0].split(":")[0] for r in righe)
    print(f"{len(righe)} aziende con detentori; scritto {OUT.relative_to(RAIZ)}")
    for k, v in c.most_common():
        print(f"  {v:4d}  {k}")


if __name__ == "__main__":
    main()
