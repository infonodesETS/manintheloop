#!/usr/bin/env python3
"""
pilota_exa.py - B3, pilota di 10 casi di possibili duplicati (sola lettura sul database).

Per ogni caso fa una domanda a Exa (endpoint /answer) e salva risposta e fonti in un CSV.
NON scrive nel database. Il verdetto lo scrive una persona (colonne vuote nel CSV).

La chiave sta in ~/.config/infonodes/exa.env (EXA_API_KEY=...), mai nel repo e mai stampata.

Uso, dalla radice del repo:
    python3 work/b3-pilota/pilota_exa.py --solo 1        # prova su un solo caso
    python3 work/b3-pilota/pilota_exa.py                 # tutti i casi
"""
import csv, json, os, sys, time, urllib.request, urllib.error
from datetime import date

DB = "docs/data/database.json"
ENV = os.path.expanduser("~/.config/infonodes/exa.env")
OUT = "work/b3-pilota/pilota-exa-%s.csv" % date.today().isoformat()
URL = "https://api.exa.ai/answer"

# (n, tipo atteso, [id...], domanda)
CASI = [
    (1, "stessa societa", ["IN-0006", "IN-1249"],
     "Are 'Advanced Micro Devices' (ticker AMD, Nasdaq) and 'AMD' the same company? Answer yes or no first, then give the evidence."),
    (2, "stessa societa", ["IN-0242", "IN-1311"],
     "Are 'MP Materials Class A' (ticker MP, NYSE) and 'MP Materials' the same company? Answer yes or no first, then give the evidence."),
    (3, "stessa societa", ["IN-0062", "IN-1294"],
     "Are 'Business Machines' (ticker IBM) and 'IBM' (International Business Machines) the same company? Answer yes or no first, then give the evidence."),
    (4, "stessa societa", ["IN-0803", "IN-1431"],
     "Are 'Iveco Defence Vehicles' (IDV, website idvgroup.com) and 'Idv Defence Vehicles Italia' the same legal entity, or is one a subsidiary or a renamed version of the other? Answer first, then give the evidence."),
    (5, "stessa societa", ["IN-0282", "IN-1318"],
     "Are 'Palantir Technologies Class A' (ticker PLTR) and 'Palantir Technologies' the same company? Answer yes or no first, then give the evidence."),
    (6, "classi di azioni", ["IN-0017", "IN-0018", "IN-1247"],
     "Are 'Alphabet Class A' (GOOGL), 'Alphabet Class C' (GOOG) and 'Alphabet' the same company issuing different share classes? Answer first, then give the evidence."),
    (7, "classi di azioni", ["IN-0365", "IN-0366"],
     "Are 'Telecom Italia' (ticker TIT, ordinary shares) and 'Telecom Italia S.p.a' (ticker TITR, savings shares) the same company issuing two share classes? Answer first, then give the evidence."),
    (8, "azienda o investitore", ["IN-0682", "IV-0702"],
     "Fincantieri is an Italian shipbuilder. Is there a separate legal entity named 'Fincantieri' that acts as an investor or fund, or is it the same shipbuilding company? Answer first, then give the evidence."),
    (9, "sussidiaria (atteso: no)", ["IN-1290", "IN-1375"],
     "Is 'HII Mission Technologies' the same legal entity as Huntington Ingalls Industries (HII), or a separate subsidiary or division of it? Answer first, then give the evidence."),
    (10, "sussidiaria (atteso: no)", ["IN-1352", "IN-0013"],
     "Is 'Alcoa Warrick' (Warrick Operations, Indiana) the same legal entity as Alcoa Corporation, or a separate site, subsidiary or operation of it? Answer first, then give the evidence."),
]


def chiave():
    with open(ENV, encoding="utf-8") as f:
        for riga in f:
            if riga.startswith("EXA_API_KEY="):
                return riga.split("=", 1)[1].strip()
    sys.exit("EXA_API_KEY non trovata in " + ENV)


def chiedi(key, domanda):
    corpo = json.dumps({"query": domanda, "text": False}).encode()
    req = urllib.request.Request(URL, data=corpo, method="POST", headers={
        "x-api-key": key, "content-type": "application/json", "user-agent": "mitl-b3-pilota"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def main():
    solo = int(sys.argv[sys.argv.index("--solo") + 1]) if "--solo" in sys.argv else None
    db = json.load(open(DB, encoding="utf-8"))
    ent = {e["id"]: e for e in db["entities"]}
    key = chiave()
    righe = []
    for n, tipo, ids, dom in CASI:
        if solo and n != solo:
            continue
        nomi = " | ".join("%s %s" % (i, ent[i]["name"]) for i in ids)
        try:
            ris = chiedi(key, dom)
            risposta = (ris.get("answer") or "").replace("\n", " ")
            fonti = " ".join(c.get("url", "") for c in ris.get("citations", []))
            err = ""
        except urllib.error.HTTPError as e:
            risposta, fonti, err = "", "", "HTTP %s" % e.code
        except Exception as e:
            risposta, fonti, err = "", "", type(e).__name__
        righe.append([n, tipo, " ".join(ids), nomi, dom, risposta, fonti, err, "", "", "", ""])
        print("caso %s: %s" % (n, "ERRORE " + err if err else "ok, %d fonti" % len(fonti.split())))
        time.sleep(1)
    scrivi_intestazione = not os.path.exists(OUT) or not solo
    mode = "w" if not solo else "a"
    with open(OUT, mode, newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if mode == "w" or os.path.getsize(OUT) == 0:
            w.writerow(["caso", "tipo_atteso", "id", "nomi_nel_db", "domanda", "risposta_exa", "fonti", "errore",
                        "verdetto", "nota", "controllato_da", "data"])
        w.writerows(righe)
    print("scritto", OUT)


main()
