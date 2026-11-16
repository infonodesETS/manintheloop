#!/usr/bin/env python3
"""B5 Release 1, passo 2c: PROPOSTA della tabella gestori (entita SEC -> scheda del DB), S6.

Sola lettura. Per ognuna delle 110 entita di rawdata/sec-edgar/2026-10-17/entita.csv
cerca nel database schede IV- e IN- ATTIVE:
 - «uguale»: stesso nome dopo aver tolto solo suffissi legali (inc, llc, lp, ltd, plc, corp, co...)
 - «simile»: stessa prima parola (4+ lettere) ma nome diverso: NON e una proposta,
   e un avviso (esempio S6: FMR LLC non e Fidelity International IV-0214).
Senza «uguale» la proposta e «nuova IV-» (S6 regola 1: un nodo per ogni depositante),
salvo la tabella S6 sotto, scritta dalla decisione S6 e dalle verifiche del 2026-11-11.
Scrive solo work/b5-release1/proposta-gestori.csv.
Uso: python3 -I work/b5-release1/proponi_gestori.py
"""
import csv, json, re, pathlib, unicodedata, collections

RAIZ = pathlib.Path(__file__).resolve().parents[2]
REL = RAIZ / "rawdata/sec-edgar/2026-10-17"
OUT = RAIZ / "work/b5-release1/proposta-gestori.csv"

LEGALI = {"inc", "llc", "lp", "l", "p", "ltd", "limited", "plc", "corp", "corporation", "co",
          "company", "the", "and", "affiliates", "sa", "nv", "ag", "llp", "na", "n", "a", "trust", "pty", "s", "v"}

# Decisione S6 (Nelson, 2026-11-11) e verifiche del 2026-11-11: nome normalizzato -> ID gia nel DB
S6 = {"blackrock": "IV-0077", "jpmorgan chase": "IV-0324", "morgan stanley": "IV-0393",
      "invesco": "IV-0719", "state street": "IN-1468", "baillie gifford": "IV-0051",
      "durable capital partners": "IV-0623", "independent franchise partners": "IV-0282",
      "public investment fund": "IV-0456"}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(w for w in s.split() if w not in LEGALI)


def ritirata(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def main():
    db = json.load(open(RAIZ / "docs/data/database.json", encoding="utf-8"))
    ents = [e for e in db["entities"] if e["id"][:3] in ("IV-", "IN-") and not ritirata(e)]
    per_norm = collections.defaultdict(list)
    per_prima = collections.defaultdict(list)
    for e in ents:
        n = norm(e["name"])
        per_norm[n].append(e)
        if n:
            per_prima[n.split()[0]].append(e)
    S = list(csv.DictReader(open(REL / "entita.csv", encoding="utf-8")))
    det = list(csv.DictReader(open(REL / "detentori-oltre-5.csv", encoding="utf-8")))
    righe_per_e = collections.Counter(r["entita_id"] for r in det)

    out = []
    for s in S:
        n = norm(s["nome"])
        uguali = per_norm.get(n, [])
        # tabella S6: la decisione vince sul nome, ma il nome deve coincidere
        s6 = S6.get(n, "")   # solo nome identico: BlackRock Advisors LLC NON e IV-0077 (S6: un nodo per depositante)
        prima = n.split()[0] if n else ""
        simili = [e for e in per_prima.get(prima, []) if len(prima) >= 4 and e not in uguali]
        if s6:
            prop, stato = s6, "S6 (decisione di Nelson, gia nel DB)"
        elif len(uguali) == 1:
            prop, stato = uguali[0]["id"], "proposta: nome uguale a una scheda attiva"
        elif len(uguali) > 1:
            prop, stato = "", "da decidere: piu schede con lo stesso nome"
        elif simili:
            prop, stato = "", "da decidere: nome simile nel DB, verificare se e lo stesso soggetto giuridico | ATTENZIONE"
        else:
            prop, stato = "NUOVA IV-", "proposta: nuova IV- (nessuna scheda con nome uguale o simile)"
        out.append({
            "entita_id": s["entita_id"], "nome_sec": s["nome"], "altre_grafie": s["altre_grafie"],
            "n_aziende": s["aziende"], "n_righe": righe_per_e.get(s["entita_id"], 0),
            "tickers": s["tickers"][:80],
            "candidati_uguali": " | ".join(f"{e['id']}={e['name']}" for e in uguali),
            "candidati_simili": " | ".join(f"{e['id']}={e['name']}" for e in simili[:6]),
            "proposta_id": prop, "stato": stato, "revisione_nelson": "", "nota": "",
        })
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    c = collections.Counter(r["stato"].split(":")[0].split(" |")[0].split(" (")[0] for r in out)
    att = sum(1 for r in out if "ATTENZIONE" in r["stato"])
    print(f"{len(out)} entita SEC; scritto {OUT.relative_to(RAIZ)}; con avviso di nomi simili: {att}")
    for k, v in c.most_common():
        print(f"  {v:4d}  {k}")


if __name__ == "__main__":
    main()
