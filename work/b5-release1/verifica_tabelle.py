#!/usr/bin/env python3
"""B5 Release 1: controllo INDIPENDENTE delle tre tabelle di proposta.

Non importa gli script di proposta: rilegge i CSV grezzi della release e il database.
Sola lettura, non scrive nulla. Esce con codice 1 se trova un problema.
Uso: python3 -I work/b5-release1/verifica_tabelle.py [--campione N] [--seme S]
"""
import csv, json, pathlib, random, sys, collections

RAIZ = pathlib.Path(__file__).resolve().parents[2]
REL = RAIZ / "rawdata/sec-edgar/2026-10-17"
W = RAIZ / "work/b5-release1"
problemi = []


def leggi(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def p(msg):
    problemi.append(msg)
    print("  PROBLEMA:", msg)


def main():
    arg = sys.argv[1:]
    n_camp = int(arg[arg.index("--campione") + 1]) if "--campione" in arg else 15
    seme = int(arg[arg.index("--seme") + 1]) if "--seme" in arg else 20261116

    db = json.load(open(RAIZ / "docs/data/database.json", encoding="utf-8"))
    E = {e["id"]: e for e in db["entities"]}

    def attiva(i):
        e = E.get(i)
        return bool(e) and not any(h.get("action") == "entity_retired" for h in e.get("history", []))

    det = leggi(REL / "detentori-oltre-5.csv")
    t1 = leggi(W / "proposta-aziende.csv")
    t2 = leggi(W / "proposta-classi.csv")
    t3 = leggi(W / "proposta-gestori.csv")
    az = {a["ticker"]: a for a in leggi(REL / "aziende.csv")}

    print("1. COMPLETEZZA")
    tk_det = {r["ticker"] for r in det}
    tk_t1 = {r["ticker"] for r in t1}
    for t in sorted(tk_det - tk_t1):
        p(f"ticker nei detentori ma non nella tabella 1: {t}")
    for t in sorted(tk_t1 - tk_det):
        p(f"ticker nella tabella 1 senza detentori: {t}")
    if len(t1) != len(tk_t1):
        p("ticker duplicati nella tabella 1")
    for r in t1:
        if az[r["ticker"]]["cik"] != r["cik"]:
            p(f"CIK diverso da aziende.csv per {r['ticker']}")
    classi = collections.defaultdict(collections.Counter)
    for r in det:
        classi[r["ticker"]][r["classe"]] += 1
    multi = {t for t, c in classi.items() if len(c) > 1}
    coppie_det = {(t, c): n for t in multi for c, n in classi[t].items()}
    coppie_t2 = {(r["ticker"], r["classe_nel_filing"]): int(r["n_righe"]) for r in t2}
    if coppie_det != coppie_t2:
        for k in sorted(set(coppie_det) ^ set(coppie_t2)):
            p(f"coppia ticker+classe non allineata: {k}")
        for k in set(coppie_det) & set(coppie_t2):
            if coppie_det[k] != coppie_t2[k]:
                p(f"numero di righe diverso per {k}")
    ent_det = {r["entita_id"] for r in det if r["tipo"] == "entity"}
    ent_t3 = {r["entita_id"] for r in t3}
    for e in sorted(ent_det - ent_t3):
        p(f"entita nei detentori ma non nella tabella 3: {e}")
    for e in sorted(ent_t3 - ent_det):
        p(f"entita nella tabella 3 senza righe nei detentori: {e}")
    tot_righe_t3 = sum(int(r["n_righe"]) for r in t3)
    n_ent = sum(1 for r in det if r["tipo"] == "entity")
    if tot_righe_t3 != n_ent:
        p(f"righe di entita: tabella 3 = {tot_righe_t3}, detentori = {n_ent}")
    print(f"   aziende {len(tk_t1)}/{len(tk_det)}; coppie multi-classe {len(coppie_t2)}; entita {len(ent_t3)}/{len(ent_det)}; righe entita {tot_righe_t3}/{n_ent}")

    print("2. SCHEDE PROPOSTE: esistono, attive, senza doppioni")
    uso1 = collections.defaultdict(list)
    for r in t1:
        i = r["proposta_id"]
        if i:
            uso1[i].append(r["ticker"])
            if not attiva(i):
                p(f"tabella 1: {i} per {r['ticker']} non esiste o e ritirata")
    for i, ts in uso1.items():
        if len(ts) > 1:
            p(f"tabella 1: {i} proposta per piu ticker {ts}")
    for r in t2:
        i = r["id_proposto"]
        if r["azione_proposta"] == "NON MAPPATA":
            p(f"tabella 2: riga non mappata {r['ticker']} {r['classe_nel_filing']}")
        elif i and not attiva(i):
            p(f"tabella 2: {i} per {r['ticker']} non esiste o e ritirata")
        elif not i:
            p(f"tabella 2: nessun ID per {r['ticker']} {r['classe_nel_filing']}")
    uso3 = collections.defaultdict(list)
    for r in t3:
        i = r["proposta_id"]
        if i and i != "NUOVA IV-":
            uso3[i].append(r["entita_id"])
            if not attiva(i):
                p(f"tabella 3: {i} per {r['entita_id']} non esiste o e ritirata")
    for i, es in uso3.items():
        if len(es) > 1:
            p(f"tabella 3: {i} proposto per piu entita SEC {es} (S6: un nodo per depositante)")
    print(f"   ID proposti: t1 {len(uso1)}, t3 {len(uso3)}")

    print("3. COERENZA TRA LE TABELLE")
    id2 = collections.defaultdict(set)
    for r in t2:
        if r["id_proposto"]:
            id2[r["ticker"]].add(r["id_proposto"])
    for r in t1:
        if r["ticker"] in id2 and r["proposta_id"] and r["proposta_id"] not in id2[r["ticker"]]:
            p(f"{r['ticker']}: tabella 1 propone {r['proposta_id']}, tabella 2 usa {sorted(id2[r['ticker']])}")
    aperti = [r["ticker"] for r in t1 if not r["proposta_id"] and r["ticker"] not in id2]
    print(f"   ticker senza proposta e non risolti dalla tabella 2: {aperti}")

    print("4. GESTORI: tipo delle schede S6 e nodi che non devono confluire")
    for r in t3:
        i = r["proposta_id"]
        if i and i != "NUOVA IV-":
            e = E[i]
            if e["id"].startswith("IV-") is False and i != "IN-1468" and "S6" in r["stato"]:
                p(f"S6: {i} non e una IV- (solo State Street IN-1468 e previsto)")
    for r in t3:
        if "advisors" in r["nome_sec"].lower() and r["proposta_id"] in ("IV-0077",):
            p(f"{r['entita_id']} {r['nome_sec']} non deve confluire su {r['proposta_id']}")

    print(f"5. CAMPIONE di {n_camp} righe della tabella 1 (seme {seme}), da guardare a mano")
    rnd = random.Random(seme)
    prop = [r for r in t1 if r["proposta_id"]]
    for r in rnd.sample(prop, min(n_camp, len(prop))):
        e = E[r["proposta_id"]]
        w = (e.get("sources", {}).get("wikidata") or {})
        print(f"   {r['ticker']:6} CIK {r['cik']} | SEC: {r['azienda_sec'][:34]:34} | DB {r['proposta_id']}: {e['name'][:30]:30} | wikidata: {(w.get('label') or '')[:24]} {w.get('country') or ''} {w.get('isin') or ''}")

    print()
    print("ESITO:", "OK, nessun problema meccanico" if not problemi else f"{len(problemi)} PROBLEMI")
    sys.exit(1 if problemi else 0)


if __name__ == "__main__":
    main()
