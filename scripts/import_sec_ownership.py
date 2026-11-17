#!/usr/bin/env python3
"""
import_sec_ownership.py - B5, Release 1 della SEC: relazioni `ownership`.

Legge `rawdata/sec-edgar/<release>/detentori-oltre-5.csv` e le tre tabelle riviste a mano in
`work/b5-release1/` (proposta-aziende.csv, proposta-classi.csv, proposta-gestori.csv). Regole: reference/S3..S7 e
SCHEMA.md (Relationships); UPDATE_PROTOCOL.md prima di qualunque scrittura sui dati.

  - soglia S4: percentuale >= 5 oppure percentuale_voti >= 5 (5,0 incluso); le altre righe sono scartate con motivo;
  - riconciliazione S4: ogni riga e importabile, scartata (con motivo) o bloccata (decisione mancante): la somma
    deve essere il numero di righe del file;
  - un `ownership` per (titolare, azienda, classe), id REL-NNNN; indirizzi MAI portati;
  - `as_of` / `as_of_origine` (S5): data del filing -> `deposito`; «dati al ...» -> `testo`; senza fonte -> `proxy`
    con `quote_al` di aziende.csv;
  - entita nuove (`PER-` per le persone, `IV-` per i depositanti senza scheda): ID reali, il primo libero della
    classe, assegnati in ordine alfabetico del nome; le schede esistenti (aziende e depositanti gia nel DB) NON
    si toccano; `sources.sec` porta solo release, righe di origine e P####/E#### (mai indirizzi);
  - re-import (S5): stessa chiave e stessi valori = 0 modifiche; valori diversi = voce in `history[]` della
    relazione con il valore vecchio; riga scomparsa = `current: false` con voce in `history[]`, mai cancellata.

Senza `--apply` NON scrive nel database: scrive solo i report (cartella `--out`, di default
work/b5-release1/dry-run/). Con `--apply` scrive nel file indicato da `--db`; se `--db` e il database vero del repo
serve anche `--database-reale` (decisione di Nelson). Si prova SEMPRE prima su una copia fuori dal repo.
Uso, dalla radice del repo:
    python3 scripts/import_sec_ownership.py [--release 2026-10-17] [--db FILE] [--out DIR] [--apply [--database-reale]]
"""
import argparse, csv, datetime, json, pathlib, re, sys, collections

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DB = RAIZ / "docs/data/database.json"
LAV = RAIZ / "work/b5-release1"
OUT = LAV / "dry-run"
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
CAMPI_VALORI = ("pct", "pct_voti", "shares", "as_of", "as_of_origine", "filing_date")
MESI = {m: i for i, m in enumerate("january february march april may june july august september october november december".split(), 1)}
MESI.update({m: i for i, m in enumerate("gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split(), 1)})
MESI.update({"aug": 8, "sept": 9, "sep": 9, "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "oct": 10, "nov": 11, "dec": 12})
_M = "|".join(sorted(MESI, key=len, reverse=True))
# «February 5, 2025» (inglese) oppure «31 dicembre 2024» (italiano)
DATA_PROSA = re.compile(rf"(?:\b({_M})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b)|(?:\b(\d{{1,2}})\s+({_M})\s+(\d{{4}})\b)", re.I)


def date_prosa(testo):
    """[(posizione, 'AAAA-MM-GG')] delle date scritte in prosa (inglese o italiano)."""
    out = []
    for m in DATA_PROSA.finditer(testo):
        mese, g, y = (m.group(1), m.group(2), m.group(3)) if m.group(1) else (m.group(5), m.group(4), m.group(6))
        out.append((m.start(), f"{int(y):04d}-{MESI[mese.lower()]:02d}-{int(g):02d}"))
    return out


def leggi_fonte(fonte):
    """(filing_date, as_of, origine, da_controllare) dal testo della fonte; origine None se non c'e una data.
    Regole S5: data ISO o «filed ...» = deposito; «dati al / as of ...» = testo. Con piu di due date distinte
    la riga e segnata «da controllare» (la scelta resta la prima data dopo «filed»)."""
    iso = ISO.findall(fonte)
    if iso:   # regola gia in uso sulle date ISO (invariata)
        if "dati al" in fonte and len(iso) >= 2:
            return iso[0], iso[-1], "testo", False
        return iso[0], iso[0], "deposito", False
    date = date_prosa(fonte)
    if not date:
        return None, None, None, False
    low = fonte.lower()
    filing = None
    ks = [low.find(w) for w in ("filed", "depositato il") if low.find(w) >= 0]
    k = min(ks) if ks else -1
    if k >= 0:
        dopo = [d for pos, d in date if pos > k]
        filing = dopo[0] if dopo else None
    as_of = None
    for chiave in ("dati al", "as of"):
        k = low.find(chiave)
        if k >= 0:
            dopo = [d for pos, d in date if pos > k]
            if dopo:
                as_of = dopo[0]
                break
    multi = len({d for _, d in date}) > 2
    if as_of:
        return filing, as_of, "testo", multi
    if filing is None:
        filing = date[0][1]
    return filing, filing, "deposito", multi


def leggi(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


def applica(a, db, db_path, out, nuove, righe_di, rels, cambiate, scomparse, righe_tot, tot, cont, dup, oggi):
    """Scrive nel database (solo con --apply). Si ferma prima di scrivere se qualcosa non torna."""
    if tot != righe_tot or cont.get("bloccata", 0) or dup:
        sys.exit(f"STOP: riconciliazione {tot}/{righe_tot}, bloccate {cont.get('bloccata', 0)}, chiavi duplicate {len(dup)}: non scrivo")
    riga_di = lambda n: {"file": "detentori-oltre-5.csv", "row": n}
    nuove_schede = []
    for eid, e in sorted(nuove.items()):
        persona = e["prefisso"] == "PER"
        sec = {"release": a.release, "refs": [riga_di(n) for n in righe_di[eid]]}
        sec.update({k: e[k] for k in ("person_ids", "entity_ids") if k in e})
        if persona:
            fonti = {"crunchbase": None, "infonodes": None, "wikidata": None, "sec": sec}
            tipo, desc = "person", f"Person added: holder of 5% or more of capital or votes in a SEC release {a.release} filing"
        else:
            fonti = {"edf": None, "ishares": None, "crunchbase": None, "infonodes": None, "wikidata": None, "sec": sec}
            tipo, desc = "investor", f"Investor added: filer of a 5% or more holding in SEC release {a.release}; one node per filer (S6), no group link"
        nuove_schede.append({
            "id": eid, "type": tipo, "roles": ["investor"], "name": e["nome"], "sector": None, "wikidata_id": None,
            "sources": fonti,
            "history": [{"date": oggi, "source": "sec", "author": "import_sec_ownership.py", "field": "*",
                         "old": None, "new": None, "description": desc}],
            "validation": [{"status": "needs_review",
                            "description": f"Created by the SEC release {a.release} import (B5); only the name comes from the source, no country or other data",
                            "author": "import_sec_ownership.py", "datestamp": oggi}],
            "tags": []})
    for vecchio, nuovo_ in cambiate:     # S5 regola 2: il valore vecchio resta in history[]
        h = vecchio.setdefault("history", [])
        for f in CAMPI_VALORI + ("current",):
            nv = True if f == "current" else nuovo_[f]
            if vecchio.get(f) != nv:
                h.append({"date": oggi, "release": a.release, "source_ref": nuovo_["source_ref"], "field": f, "old": vecchio.get(f), "new": nv})
                vecchio[f] = nv
        vecchio["release"], vecchio["source_ref"] = a.release, nuovo_["source_ref"]
    for v in scomparse:                  # S5 regola 3: mai cancellare
        v.setdefault("history", []).append({"date": oggi, "release": a.release, "source_ref": v.get("source_ref"),
                                            "field": "current", "old": True, "new": False})
        v["current"] = False
    db["entities"].extend(nuove_schede)
    db["relationships"].extend(rels)
    if nuove_schede or rels or cambiate or scomparse:
        db["_updated"] = oggi
    with open(db_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(db, indent=2, ensure_ascii=False))
    riga = (f"apply {oggi}: {len(nuove_schede)} schede nuove ({sum(1 for e in nuove_schede if e['id'].startswith('PER'))} PER, "
            f"{sum(1 for e in nuove_schede if e['id'].startswith('IV'))} IV), {len(rels)} relazioni ownership, "
            f"{len(cambiate)} cambiate, {len(scomparse)} scomparse -> {db_path}")
    (out / "apply-report.md").write_text(riga + "\n", encoding="utf-8")
    print("\n" + riga)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--release", default="2026-10-17")
    ap.add_argument("--db", default=str(DB), help="database da leggere (e da scrivere con --apply)")
    ap.add_argument("--out", default=str(OUT), help="cartella dei report")
    ap.add_argument("--apply", action="store_true", help="scrive nel database indicato da --db")
    ap.add_argument("--database-reale", action="store_true", help="consente --apply sul database del repo")
    a = ap.parse_args()
    db_path = pathlib.Path(a.db).resolve()
    out = pathlib.Path(a.out).resolve()
    if a.apply and db_path == DB.resolve() and not a.database_reale:
        sys.exit("--apply sul database del repo richiede --database-reale (prima si prova su una copia con --db)")
    oggi = datetime.date.today().isoformat()
    raw = RAIZ / "rawdata/sec-edgar" / a.release
    righe = leggi(raw / "detentori-oltre-5.csv")
    aziende = {r["ticker"]: r for r in leggi(raw / "aziende.csv")}
    t_az = {r["ticker"]: r for r in leggi(LAV / "proposta-aziende.csv")}
    t_cl = {(r["ticker"], r["classe_nel_filing"]): r for r in leggi(LAV / "proposta-classi.csv")}
    t_ge = {r["entita_id"]: r for r in leggi(LAV / "proposta-gestori.csv")}
    db = json.load(open(db_path, encoding="utf-8"))
    ents = {e["id"]: e for e in db["entities"]}
    ritirate = {i for i, e in ents.items() if any(h.get("action") == "entity_retired" for h in e.get("history", []))}
    esistenti = {(r["source"], r["target"], r["type"], r.get("classe")): r for r in db["relationships"]}
    max_rel = max([int(r["id"].split("-")[1]) for r in db["relationships"] if str(r.get("id", "")).startswith("REL-")] or [0])

    # schede gia create da un import SEC: si riconoscono dal riferimento di fonte, mai dal nome (re-run sicuro)
    indice = {}
    for e in db["entities"]:
        sec = (e.get("sources") or {}).get("sec") or {}
        for pid in sec.get("person_ids", []):
            indice[("P", pid)] = e["id"]
        for eid in sec.get("entity_ids", []):
            indice[("E", eid)] = e["id"]

    # entita nuove: ID provvisori TMP-..., sostituiti a fine lettura con il primo ID libero in ordine alfabetico
    nuove, nuovo_id, righe_di = {}, {}, collections.defaultdict(list)

    def nuovo(chiave, prefisso, nome, extra, n):
        if chiave in indice:
            return indice[chiave]
        if chiave not in nuovo_id:
            nuovo_id[chiave] = f"TMP-{prefisso}-{len(nuovo_id) + 1:05d}"
            nuove[nuovo_id[chiave]] = {"id": nuovo_id[chiave], "prefisso": prefisso, "nome": nome, **extra}
        righe_di[nuovo_id[chiave]].append(n)
        return nuovo_id[chiave]

    esito = []          # una voce per riga del file
    rels = []
    cambiate, viste = [], set()
    da_controllare = []
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
            source = nuovo(("P", r["persona_id"]), "PER", r["nome"], {"person_ids": [r["persona_id"]]}, n)
            htype = "person"
            blocco = ""
        else:
            g = t_ge.get(r["entita_id"], {})
            pid = g.get("proposta_id", "")
            if pid.startswith("NUOVA"):
                source = nuovo(("E", r["entita_id"]), "IV", r["nome"], {"entity_ids": [r["entita_id"]]}, n)
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
        quote_al = (aziende.get(r["ticker"]) or {}).get("quote_al") or None
        filing, as_of, orig, controllare = leggi_fonte(fonte)
        if orig is None:
            filing, as_of, orig = None, quote_al, ("proxy" if quote_al else None)
        if controllare:
            da_controllare.append((n, r["ticker"], r["nome"], fonte[:110], filing, as_of))
        rel = {"id": None, "type": "ownership", "source": source, "target": target, "classe": r["classe"],
               "holder_type": htype, "pct": pct, "pct_voti": voti, "shares": az, "filing_date": filing,
               "as_of": as_of, "as_of_origine": orig, "release": a.release, "current": True,
               "source_ref": f"{a.release}/detentori-oltre-5.csv#{n}", "created_at": oggi, "history": []}
        k = (source, target, "ownership", r["classe"])
        viste.add(k)
        if k in esistenti:
            vecchio = esistenti[k]
            uguale = all(vecchio.get(f) == rel[f] for f in CAMPI_VALORI) and vecchio.get("current") is True
            if not uguale:
                cambiate.append((vecchio, rel))
            esito.append({**base, "esito": "gia nel DB (invariata)" if uguale else "gia nel DB (valori diversi: andrebbe in history)", "motivo": ""})
            continue
        rels.append(rel)
        esito.append({**base, "esito": "importabile", "motivo": "per voti >=5" if not ok_cap else ""})

    # ID reali per le entita nuove: primo libero della classe, ordine alfabetico del nome (UPDATE_PROTOCOL, principio 4)
    base = {p: max([int(i.split("-")[1]) for i in ents if i.startswith(p + "-")] or [0]) for p in ("PER", "IV")}
    mappa = {}
    for tmp, e in sorted(nuove.items(), key=lambda kv: (kv[1]["prefisso"], kv[1]["nome"].casefold(), kv[0])):
        base[e["prefisso"]] += 1
        mappa[tmp] = f"{e['prefisso']}-{base[e['prefisso']]:04d}"
    nuove = {mappa[t]: {**e, "id": mappa[t]} for t, e in nuove.items()}
    righe_di = {mappa[t]: v for t, v in righe_di.items()}
    for x in rels:
        x["source"] = mappa.get(x["source"], x["source"])

    # righe scomparse dal file (S5 regola 3): relazioni ownership correnti la cui chiave non e piu nel file
    scomparse = [r for r in db["relationships"] if r.get("type") == "ownership" and r.get("current") is True
                 and (r["source"], r["target"], "ownership", r.get("classe")) not in viste]

    # duplicati di chiave tra le relazioni da creare (atteso 0, S5)
    dup = [k for k, v in collections.Counter((x["source"], x["target"], x["classe"]) for x in rels).items() if v > 1]
    for i, x in enumerate(rels, start=1):
        x["id"] = f"REL-{max_rel + i:04d}"

    # ---- report ----
    out.mkdir(parents=True, exist_ok=True)
    cont = collections.Counter(e["esito"] for e in esito)
    with open(out / "riconciliazione.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["riga", "ticker", "titolare", "tipo", "classe", "esito", "motivo"])
        w.writeheader(); w.writerows(esito)
    with open(out / "entita-nuove.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id_provvisorio", "nome", "riferimento_fonte"])
        for e in nuove.values():
            w.writerow([e["id"], e["nome"], ",".join(e.get("person_ids", []) + e.get("entity_ids", []))])
    json.dump(rels, open(out / "relazioni-anteprima.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
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
    rep += ["", f"## Date da controllare a mano (piu di due date nella fonte): {len(da_controllare)}"]
    rep += [f"- riga {n} {t} {nome}: «{f}» -> filing {fi}, as_of {ao}" for n, t, nome, f, fi, ao in da_controllare]
    sen = [x["source_ref"] for x in rels if not x["as_of"]]
    rep += ["", f"## Righe senza as_of: {len(sen)}"] + [f"- {x}" for x in sen]
    rep += ["", "## Origine di as_of: " + ", ".join(f"{k}={v}" for k, v in sorted(collections.Counter(str(x['as_of_origine']) for x in rels).items()))]
    (out / "report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    print("\n".join(rep))
    print(f"\nReport in {out}/ (riconciliazione.csv, entita-nuove.csv, relazioni-anteprima.json, report.md)")
    print(f"\nRe-import: relazioni cambiate {len(cambiate)}, scomparse dal file {len(scomparse)} (S5: report da guardare a mano)")
    for v, n_ in cambiate[:20]:
        print("  cambiata:", v["source"], v["target"], v.get("classe"), {f: (v.get(f), n_[f]) for f in CAMPI_VALORI if v.get(f) != n_[f]})
    for v in scomparse[:20]:
        print("  scomparsa:", v["source"], v["target"], v.get("classe"), v.get("source_ref"))
    if not a.apply:
        return 0
    return applica(a, db, db_path, out, nuove, righe_di, rels, cambiate, scomparse, righe_tot, tot, cont, dup, oggi)


if __name__ == "__main__":
    sys.exit(main())
