#!/usr/bin/env python3
"""
proponi_ruoli.py - B5, proposta dei ruoli delle persone (SOLO PROPOSTA, non scrive nel database).

Legge consiglieri.csv, dirigenti.csv e comitati.csv della release SEC per le persone che l'import ha creato
(riconosciute da `sources.sec.person_ids` in una COPIA del database, `--db`), applica la mappatura
dicitura -> `role_code` e scrive due file da rivedere a mano:
  - work/b5-release1/proposta-ruoli.csv       una riga per dicitura distinta: codici proposti, note, revisione_nelson
  - work/b5-release1/dry-run/ruoli-anteprima.json   le relazioni `role` che ne risulterebbero (una per persona e scheda)

Modello (decisione di Nelson, 2026-11-17): UNA relazione `role` per (persona, scheda azienda); dentro, `roles` con
solo i ruoli presenti (assente = false), ciascuno con i dettagli estratti. Nessuna eta (minimizzazione).
Uso:  python3 work/b5-release1/proponi_ruoli.py --db COPIA.json [--release 2026-10-17]
"""
import argparse, collections, csv, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LAV = RAIZ / "work/b5-release1"

# (codice, espressione); ordine = ordine di ricerca. Ogni match viene cancellato dal testo prima del successivo.
REGOLE = [
    ("lead_independent_director", r"lead independent director"),
    ("executive_chair", r"executive chair(?:man|woman|person)?"),
    ("co_ceo", r"co-?\s?ceo|co-chief executive officer"),
    ("ceo", r"chief executive officer|\bceo\b"),
    ("cto", r"chief technology officer|\bcto\b"),
    ("chair", r"chair(?:man|woman|person)?\b"),
    ("president", r"\bpresident\b"),
    ("founder", r"\b(?:co-)?founder\b"),
    ("secretary", r"\bsecretary\b"),
    ("senior_advisor", r"senior advisor"),
    ("director", r"\bdirector\b"),
]
# casi che la regola non puo giudicare da sola (rivisti a mano; vedi la colonna nota)
MANUALI = {
    "Co-CEO of Silver Lake": (["other"], "ruolo in un'altra societa (Silver Lake): non e un ruolo nella scheda; resta in role_text"),
    "Director; Compensation; Nominating/Governance": (["director", "other"], "i due comitati sono scritti senza dire se membro o presidente: other, da guardare"),
}


def leggi(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def codici(testo):
    """Codici trovati in una dicitura, senza ripetizioni, nell'ordine della regola."""
    if testo in MANUALI:
        return MANUALI[testo][0], MANUALI[testo][1]
    resto, trovati = testo.lower(), []
    for cod, rx in REGOLE:
        if re.search(rx, resto):
            trovati.append(cod)
            resto = re.sub(rx, " ", resto)
    nota = ""
    avanzo = re.sub(r"[\s;,\-()]|\band\b|\bof\b|\bthe\b|\bboard\b|\bdirectors\b|\bclass\b|\b[ivx]+\b|\bb\b|\bnominee\b|\bseries a preferred stock\b|\bstock\b", "", resto)
    if avanzo:
        nota = f"testo non coperto dalla regola: «{avanzo[:40]}»"
    return trovati or ["other"], nota


def anno_mese(s):
    m = re.fullmatch(r"(\d{4})(?:-(\d{1,2}))?", (s or "").strip())
    return (int(m.group(1)), int(m.group(2)) if m.group(2) else None) if m else (None, None)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--db", required=True)
    ap.add_argument("--release", default="2026-10-17")
    a = ap.parse_args()
    raw = RAIZ / "rawdata/sec-edgar" / a.release
    db = json.load(open(a.db, encoding="utf-8"))
    per = {}
    for e in db["entities"]:
        for p in ((e.get("sources") or {}).get("sec") or {}).get("person_ids", []):
            per[p] = e["id"]
    own = [r for r in db["relationships"] if r.get("type") == "ownership"]
    quote_per_scheda = collections.Counter(r["target"] for r in own)
    aziende = {r["ticker"]: r for r in leggi(raw / "aziende.csv")}
    t_az = {r["ticker"]: r["proposta_id"] for r in leggi(LAV / "proposta-aziende.csv")}
    t_cl = collections.defaultdict(set)
    for r in leggi(LAV / "proposta-classi.csv"):
        t_cl[r["ticker"]].add(r["id_proposto"])

    def scheda(ticker):
        """Scheda su cui va il ruolo: quella con piu quote tra le schede di classe; altrimenti la scheda in tabella."""
        c = sorted(t_cl.get(ticker, ()), key=lambda i: (-quote_per_scheda[i], i))
        return c[0] if c else (t_az.get(ticker) or "")

    # righe grezze (numero di riga = riga del file, intestazione = 1)
    coppie = collections.OrderedDict()   # (PER, scheda) -> dati
    dicit = collections.Counter()        # (ruolo_file, dettaglio) -> n
    nota_dic, cod_dic, impl_dic = {}, {}, {}
    senza_scheda = []

    def coppia(p, ticker):
        t = scheda(ticker)
        if not t:
            senza_scheda.append((p, ticker))
            return None
        return coppie.setdefault((per[p], t), {"ticker": ticker, "roles": collections.OrderedDict(), "refs": []})

    def aggiungi(c, cod, dett, ref):
        d = c["roles"].setdefault(cod, {"role_text": dett["role_text"]})
        d.setdefault("_testi", [])
        if dett["role_text"] not in d["_testi"]:
            d["_testi"].append(dett["role_text"])
        for k, v in dett.items():
            if k not in ("role_text", "committees"):
                d.setdefault(k, v)
        if "committees" in dett:
            d.setdefault("committees", []).extend(dett["committees"])
        if ref not in c["refs"]:
            c["refs"].append(ref)

    n_righe = collections.Counter()
    # dirigenti prima: il loro testo e il piu pulito per i ruoli da dirigente
    for n, r in enumerate(leggi(raw / "dirigenti.csv"), start=2):
        if r["persona_id"] not in per:
            continue
        c = coppia(r["persona_id"], r["ticker"])
        if c is None:
            continue
        cods, nota = codici(r["cariche"])
        dicit[("dirigente", r["cariche"])] += 1
        cod_dic[("dirigente", r["cariche"])] = cods
        nota_dic[("dirigente", r["cariche"])] = nota
        n_righe["dirigente"] += 1
        for cod in cods:
            aggiungi(c, cod, {"role_text": r["cariche"], "fonte": r["fonte"]}, f"{a.release}/dirigenti.csv#{n}")
    for n, r in enumerate(leggi(raw / "consiglieri.csv"), start=2):
        if r["persona_id"] not in per:
            continue
        c = coppia(r["persona_id"], r["ticker"])
        if c is None:
            continue
        cods, nota = codici(r["cariche"])
        implicito = "director" not in cods
        if implicito:
            cods = cods + ["director"]
        chiave = ("consigliere", r["cariche"])
        dicit[chiave] += 1
        cod_dic[chiave] = cods
        nota_dic[chiave] = nota
        impl_dic[chiave] = implicito
        n_righe["consigliere"] += 1
        y, m = anno_mese(r["nel_consiglio_dal"])
        ind = {"True": True, "False": False}.get(r["indipendente"])
        for cod in cods:
            det = {"role_text": r["cariche"]}
            if cod == "director":
                if y:
                    det["since_year"] = y
                if m:
                    det["since_month"] = m
                if ind is not None:
                    det["independent"] = ind
                if implicito:
                    det["implied_by"] = "row listed as board member in consiglieri.csv"
            aggiungi(c, cod, det, f"{a.release}/consiglieri.csv#{n}")
    for n, r in enumerate(leggi(raw / "comitati.csv"), start=2):
        if r["persona_id"] not in per:
            continue
        c = coppia(r["persona_id"], r["ticker"])
        if c is None:
            continue
        pres = r["presidente"] == "True"
        chiave = ("presidente di comitato" if pres else "membro di comitato", r["comitato"])
        dicit[chiave] += 1
        cod_dic[chiave] = ["committee_member"]
        nota_dic[chiave] = "il presidente e un dettaglio del comitato (chair: true), non un codice a parte" if pres else ""
        n_righe["comitato (presidente)" if pres else "comitato (membro)"] += 1
        com = {"name": r["comitato"], "chair": pres}
        if r["riunioni"]:
            com["meetings"] = int(r["riunioni"])
        if r["anno_riunioni"]:
            com["year"] = int(r["anno_riunioni"])
        aggiungi(c, "committee_member", {"role_text": r["comitato"], "committees": [com]}, f"{a.release}/comitati.csv#{n}")

    # relazioni risultanti
    rels = []
    for (p, t), c in coppie.items():
        roles = {}
        for cod, d in c["roles"].items():
            testi = d.pop("_testi")
            if len(testi) > 1:
                d["role_text_alt"] = [x for x in testi if x != d["role_text"]]
            roles[cod] = d
        quote_al = (aziende.get(c["ticker"]) or {}).get("quote_al") or None
        rels.append({"id": None, "type": "role", "source": p, "target": t, "current": True,
                     "as_of": quote_al, "as_of_origine": "proxy" if quote_al else None, "release": a.release,
                     "roles": roles, "source_ref": c["refs"], "created_at": None, "history": []})
    LAV.joinpath("dry-run").mkdir(exist_ok=True)
    json.dump(rels, open(LAV / "dry-run/ruoli-anteprima.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    with open(LAV / "proposta-ruoli.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ruolo_nel_file", "dettaglio", "n_righe", "codici_proposti", "director_implicito", "nota", "revisione_nelson"])
        for (ru, dett), n in sorted(dicit.items(), key=lambda kv: (kv[0][0], -kv[1], kv[0][1])):
            note = nota_dic.get((ru, dett), "")
            w.writerow([ru, dett, n, " + ".join(cod_dic[(ru, dett)]), "si" if impl_dic.get((ru, dett)) else "", note, ""])

    tot = sum(n_righe.values())
    cod_cont = collections.Counter(c for r in rels for c in r["roles"])
    print(f"persone con una scheda SEC: {len(per)}; coppie persona-scheda con ruoli: {len(rels)}; persone con ruoli: {len({r['source'] for r in rels})}")
    print(f"righe di ruolo lette: {tot} {dict(n_righe)}")
    print("diciture distinte:", len(dicit), "| codici usati:", dict(cod_cont.most_common()))
    print("righe senza scheda in tabella:", senza_scheda or "nessuna")
    print("diciture con nota:", sum(1 for k in dicit if nota_dic.get(k)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
