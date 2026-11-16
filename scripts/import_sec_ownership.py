#!/usr/bin/env python3
"""
import_sec_ownership.py - B5, Release 1 della SEC: relazioni `ownership` (BOZZA, SOLO DRY-RUN).

Legge `rawdata/sec-edgar/<release>/detentori-oltre-5.csv` e le tre tabelle riviste a mano in
`work/b5-release1/` (proposta-aziende.csv, proposta-classi.csv, proposta-gestori.csv) e calcola, senza
scrivere nel database, cosa entrerebbe. Regole: reference/S3..S7 e SCHEMA.md (Relationships).

  - soglia S4: percentuale >= 5 oppure percentuale_voti >= 5 (5,0 incluso); le altre righe sono scartate con motivo;
  - riconciliazione S4: ogni riga e importabile, scartata (con motivo) o bloccata (decisione mancante): la somma
    deve essere il numero di righe del file;
  - un `ownership` per (titolare, azienda, classe), con id REL-NNNN provvisorio; indirizzi MAI portati;
  - `as_of` / `as_of_origine` (S5): data del filing -> `deposito`; «dati al ...» -> `testo`; senza fonte -> `proxy`
    con `quote_al` di aziende.csv;
  - idempotenza: una relazione con la stessa chiave gia nel database non e ricreata (stessi valori = 0 modifiche).

NON scrive in docs/data/database.json. Non esiste `--apply`: l'applicazione si scrive solo dopo l'ok di Nelson al
dry-run. Scrive i soli report in work/b5-release1/dry-run/. Uso, dalla radice del repo:
    python3 scripts/import_sec_ownership.py [--release 2026-10-17]
"""
import argparse, csv, json, pathlib, re, sys, collections

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DB = RAIZ / "docs/data/database.json"
LAV = RAIZ / "work/b5-release1"
OUT = LAV / "dry-run"
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def leggi(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--release", default="2026-10-17")
    a = ap.parse_args()
    raw = RAIZ / "rawdata/sec-edgar" / a.release
    righe = leggi(raw / "detentori-oltre-5.csv")
    aziende = {r["ticker"]: r for r in leggi(raw / "aziende.csv")}
    t_az = {r["ticker"]: r for r in leggi(LAV / "proposta-aziende.csv")}
    t_cl = {(r["ticker"], r["classe_nel_filing"]): r for r in leggi(LAV / "proposta-classi.csv")}
    t_ge = {r["entita_id"]: r for r in leggi(LAV / "proposta-gestori.csv")}
    db = json.load(open(DB, encoding="utf-8"))
    ents = {e["id"]: e for e in db["entities"]}
    ritirate = {i for i, e in ents.items() if any(h.get("action") == "entity_retired" for h in e.get("history", []))}
    esistenti = {(r["source"], r["target"], r["type"], r.get("classe")): r for r in db["relationships"]}
    max_rel = max([int(r["id"].split("-")[1]) for r in db["relationships"] if str(r.get("id", "")).startswith("REL-")] or [0])

    # ID provvisori per le entita nuove (assegnati in ordine di prima comparsa, deterministici)
    prox = {p: max([int(i.split("-")[1]) for i in ents if i.startswith(p + "-")] or [0]) for p in ("PER", "IV", "IN")}
    nuove, nuovo_id = {}, {}

    def nuovo(chiave, prefisso, nome, extra):
        if chiave not in nuovo_id:
            prox[prefisso] += 1
            nuovo_id[chiave] = f"{prefisso}-{prox[prefisso]:04d}"
            nuove[nuovo_id[chiave]] = {"id": nuovo_id[chiave], "nome": nome, **extra}
        return nuovo_id[chiave]

    esito = []          # una voce per riga del file
    rels = []
    for n, r in enumerate(righe, start=2):   # n = numero di riga del file (intestazione = 1)
        pct, voti, az = num(r["percentuale"]), num(r["percentuale_voti"]), num(r["azioni"])
        ok_cap = pct is not None and pct >= 5
        ok_voti = voti is not None and voti >= 5
        base = {"riga": n, "ticker": r["ticker"], "titolare": r["nome"], "tipo": r["tipo"], "classe": r["classe"]}
        if not (ok_cap or ok_voti):
            motivo = "sotto la soglia di S4 (capitale <5 o vuoto, voti <5 o assenti)"
            esito.append({**base, "esito": "scartata", "motivo": motivo})
            continue
        # azienda / classe
        c = t_cl.get((r["ticker"], r["classe"]))
        if c:
            target = c["id_proposto"]
        else:
            target = (t_az.get(r["ticker"]) or {}).get("proposta_id", "")
        # titolare
        if r["tipo"] == "person":
            source = nuovo(("P", r["persona_id"]), "PER", r["nome"], {"person_ids": [r["persona_id"]]})
            htype = "person"
            blocco = ""
        else:
            g = t_ge.get(r["entita_id"], {})
            pid = g.get("proposta_id", "")
            if pid.startswith("NUOVA"):
                source = nuovo(("E", r["entita_id"]), "IV", r["nome"], {"entita_id": r["entita_id"]})
            elif re.fullmatch(r"(IV|IN)-\d{4,}", pid):
                source = pid
            else:
                source, blocco = "", f"titolare {r['entita_id']} senza decisione ({g.get('stato','non in tabella')[:40]})"
            htype = "company"   # S2: fund/company non distinguibili dal CSV; da confermare
        blocchi = []
        if not target:
            blocchi.append(f"azienda {r['ticker']} / {r['classe']} senza scheda in tabella")
        elif target in ritirate or target not in ents:
            blocchi.append(f"scheda {target} ritirata o inesistente")
        if r["tipo"] != "person" and not source:
            blocchi.append(blocco)
        if blocchi:
            esito.append({**base, "esito": "bloccata", "motivo": "; ".join(blocchi)})
            continue
        fonte = r["fonte_dichiarazione"]
        m = ISO.findall(fonte)
        quote_al = (aziende.get(r["ticker"]) or {}).get("quote_al") or None
        if "dati al" in fonte and len(m) >= 2:
            filing, as_of, orig = m[0], m[-1], "testo"
        elif m:
            filing, as_of, orig = m[0], m[0], "deposito"
        else:
            filing, as_of, orig = None, quote_al, ("proxy" if quote_al else None)
        rel = {"id": None, "type": "ownership", "source": source, "target": target, "classe": r["classe"],
               "holder_type": htype, "pct": pct, "pct_voti": voti, "shares": az, "filing_date": filing,
               "as_of": as_of, "as_of_origine": orig, "release": a.release, "current": True,
               "source_ref": f"{a.release}/detentori-oltre-5.csv#{n}", "created_at": None, "history": []}
        k = (source, target, "ownership", r["classe"])
        if k in esistenti:
            vecchio = esistenti[k]
            uguale = all(vecchio.get(f) == rel[f] for f in ("pct", "pct_voti", "shares", "as_of", "as_of_origine", "filing_date"))
            esito.append({**base, "esito": "gia nel DB (invariata)" if uguale else "gia nel DB (valori diversi: andrebbe in history)", "motivo": ""})
            continue
        rels.append(rel)
        esito.append({**base, "esito": "importabile", "motivo": "per voti >=5" if not ok_cap else ""})

    # duplicati di chiave tra le relazioni da creare (atteso 0, S5)
    dup = [k for k, v in collections.Counter((x["source"], x["target"], x["classe"]) for x in rels).items() if v > 1]
    for i, x in enumerate(rels, start=1):
        x["id"] = f"REL-{max_rel + i:04d}"

    # ---- report ----
    OUT.mkdir(parents=True, exist_ok=True)
    cont = collections.Counter(e["esito"] for e in esito)
    with open(OUT / "riconciliazione.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["riga", "ticker", "titolare", "tipo", "classe", "esito", "motivo"])
        w.writeheader(); w.writerows(esito)
    with open(OUT / "entita-nuove.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id_provvisorio", "nome", "riferimento_fonte"])
        for e in nuove.values():
            w.writerow([e["id"], e["nome"], ",".join(e.get("person_ids", [])) or e.get("entita_id", "")])
    json.dump(rels, open(OUT / "relazioni-anteprima.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    blocc = collections.Counter(e["motivo"] for e in esito if e["esito"] == "bloccata")
    righe_tot = len(righe)
    tot = sum(cont.values())
    rep = [f"# Dry-run import SEC, release {a.release} (nessuna scrittura nel database)\n",
           f"Righe nel file: {righe_tot}", *[f"- {k}: {v}" for k, v in sorted(cont.items())],
           f"Riconciliazione: {tot} = {righe_tot} -> {'OK' if tot == righe_tot else 'NON TORNA'}",
           f"Attese da S4: 546 importate (somma importabili + bloccate + gia nel DB) e 25 scartate; "
           f"trovate: {tot - cont.get('scartata', 0)} e {cont.get('scartata', 0)}",
           f"Chiavi duplicate tra le relazioni da creare: {len(dup)}",
           f"Entita nuove (ID provvisori): PER {sum(1 for i in nuove if i.startswith('PER'))}, IV {sum(1 for i in nuove if i.startswith('IV'))}",
           f"Relazioni `ownership` da creare: {len(rels)} (da REL-{max_rel + 1:04d})", "", "## Righe bloccate (motivi)"]
    rep += [f"- {v:3} x {k}" for k, v in blocc.most_common()]
    (OUT / "report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    print("\n".join(rep))
    print(f"\nReport in {OUT.relative_to(RAIZ)}/ (riconciliazione.csv, entita-nuove.csv, relazioni-anteprima.json, report.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
