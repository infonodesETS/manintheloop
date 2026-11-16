#!/usr/bin/env python3
"""
confronta.py - confronta le risposte degli agenti di B5 con le tabelle di proposta (sola lettura).

Ruolo A (A1-A4): ticker -> proposta_id di proposta-aziende.csv.
Ruolo B (B1-B3): entita_id -> proposta_id di proposta-gestori.csv.
Stampa solo i casi che richiedono una persona: disaccordo, tabella senza proposta, verdetto non
`same_entity`, `unclear`. Non scrive nulla. Uso, dalla radice del repo:
    python3 -I work/b5-release1/agenti/confronta.py [lotto ...]     (default: tutti i risultati)
"""
import csv, json, pathlib, sys

B = pathlib.Path(__file__).resolve().parents[1]
RIS = B / "agenti" / "risultati"


def carica(nome, chiave):
    with open(B / nome, newline="", encoding="utf-8") as f:
        return {r[chiave]: r for r in csv.DictReader(f)}


def main(argv):
    lotti = argv or sorted(p.stem for p in RIS.glob("*.json"))
    az, ge = carica("proposta-aziende.csv", "ticker"), carica("proposta-gestori.csv", "entita_id")
    conta = {}
    for lotto in lotti:
        d = json.load(open(RIS / f"{lotto}.json", encoding="utf-8"))
        for c in d["cases"]:
            v = c["verdict"]
            conta[v] = conta.get(v, 0) + 1
            if "ticker" in c:
                k, t = c["ticker"], az.get(c["ticker"], {})
            else:
                k, t = c["entita_id"], ge.get(c["entita_id"], {})
            mia = t.get("proposta_id", "")
            ag = c.get("db_id", "") if v == "same_entity" else ""
            if v == "same_entity" and mia == ag:
                continue
            if v == "same_entity" and not mia:
                tipo = "TABELLA SENZA PROPOSTA"
            elif v == "same_entity":
                tipo = "DISACCORDO"
            else:
                tipo = v.upper()
            print(f"{lotto:3} {k:8} {tipo:24} agente={ag or '-':8} tabella={mia or '-':8} {c.get('db_name','')}")
    print("\nVerdetti:", dict(sorted(conta.items())))


if __name__ == "__main__":
    main(sys.argv[1:])
