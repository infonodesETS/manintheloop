#!/usr/bin/env python3
"""B5 Release 1: prepara gli INPUT degli agenti di controllo (sola scrittura in agenti/input/).

Ruolo A (identita aziende, CIECO): per i ticker senza ISIN nel database (l'ISIN e gia un
segnale indipendente), piu i ticker senza proposta. L'input NON contiene la scheda proposta:
l'agente la cerca da solo nel database. Contiene solo cio che dice la release SEC.
Ruolo B (gestori): per le entita SEC «da decidere», con le schede candidate del database
come elenco di recupero (non come verdetto).

Uso: python3 -I work/b5-release1/agenti/prepara_input.py
"""
import csv, json, pathlib, collections

RAIZ = pathlib.Path(__file__).resolve().parents[3]
REL = RAIZ / "rawdata/sec-edgar/2026-10-17"
W = RAIZ / "work/b5-release1"
OUT = W / "agenti/input"
N_A, N_B = 4, 3  # numero di agenti per ruolo


def leggi(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def ripartisci(lista, n):
    lotti = [[] for _ in range(n)]
    for i, x in enumerate(lista):
        lotti[i % n].append(x)
    return lotti


def main():
    db = json.load(open(RAIZ / "docs/data/database.json", encoding="utf-8"))
    E = {e["id"]: e for e in db["entities"]}
    az = {a["ticker"]: a for a in leggi(REL / "aziende.csv")}
    t1 = leggi(W / "proposta-aziende.csv")
    t2_tickers = {r["ticker"] for r in leggi(W / "proposta-classi.csv")}
    OUT.mkdir(parents=True, exist_ok=True)

    casi_a = []
    for r in t1:
        t = r["ticker"]
        i = r["proposta_id"]
        if i:
            w = (E[i].get("sources", {}).get("wikidata") or {})
            if w.get("isin"):
                continue  # ISIN nel DB: segnale indipendente, non serve l'agente
        if t in ("FOX", "HEI", "NWS"):
            continue  # decisi per classe nella tabella 2
        casi_a.append({"ticker": t, "sec_name": az[t]["azienda"], "cik": az[t]["cik"],
                       "sec_proxy_url": az[t]["proxy_url"]})
    casi_a.sort(key=lambda c: c["ticker"])
    for k, lotto in enumerate(ripartisci(casi_a, N_A), 1):
        json.dump({"role": "A", "batch": f"A{k}", "cases": lotto},
                  open(OUT / f"A{k}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    casi_b = []
    for r in leggi(W / "proposta-gestori.csv"):
        if r["stato"].startswith("da decidere"):
            cands = []
            for blocco in (r["candidati_uguali"], r["candidati_simili"]):
                for c in blocco.split(" | "):
                    if "=" in c:
                        i, n = c.split("=", 1)
                        if i not in {x["id"] for x in cands}:
                            cands.append({"id": i, "name": n})
            casi_b.append({"entita_id": r["entita_id"], "sec_name": r["nome_sec"],
                           "other_spellings": r["altre_grafie"], "n_companies": r["n_aziende"],
                           "tickers": r["tickers"], "candidate_cards": cands})
    for k, lotto in enumerate(ripartisci(casi_b, N_B), 1):
        json.dump({"role": "B", "batch": f"B{k}", "cases": lotto},
                  open(OUT / f"B{k}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"A: {len(casi_a)} casi in {N_A} lotti; B: {len(casi_b)} casi in {N_B} lotti; scritto in {OUT.relative_to(RAIZ)}")
    print("A:", [c["ticker"] for c in casi_a])


if __name__ == "__main__":
    main()
