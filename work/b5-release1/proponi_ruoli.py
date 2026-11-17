#!/usr/bin/env python3
"""
proponi_ruoli.py - B5, proposta della tabella dei ruoli (NON scrive nel database).

Applica le regole dicitura -> `role_code` alle righe di dirigenti.csv, consiglieri.csv e comitati.csv delle persone
che l'import ha creato (riconosciute da `sources.sec.person_ids` in una COPIA del database, `--db`) e scrive
`work/b5-release1/proposta-ruoli.csv`: una riga per dicitura distinta, da rivedere a mano (colonna `revisione_nelson`).
L'import (scripts/import_sec_ownership.py) legge poi QUELLA tabella, mai le regole di questo file, e si ferma se una
riga non e rivista. Per non cancellare una revisione fatta, se la tabella esiste lo script si rifiuta di riscriverla
senza `--riscrivi`.

Modello (decisione di Nelson, 2026-11-17, reference/S7-RUOLI-E-PERSONE.md): una relazione `role` per (persona, scheda);
`director` implicito quando una riga di consiglieri.csv non lo nomina; l'eta non si importa.
Uso:  python3 work/b5-release1/proponi_ruoli.py --db COPIA.json [--release 2026-10-17] [--riscrivi]
"""
import argparse, collections, csv, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LAV = RAIZ / "work/b5-release1"
sys.path.insert(0, str(RAIZ / "scripts"))
import import_sec_ownership as imp   # noqa: E402  (stesso costruttore di relazioni dell'import)

# (codice, espressione); ogni match viene cancellato dal testo prima della regola successiva
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
# casi che la regola non puo giudicare da sola (rivisti a mano)
MANUALI = {
    "Co-CEO of Silver Lake": (["other"], "ruolo in un'altra societa (Silver Lake): non e un ruolo nella scheda; resta in role_text"),
    "Director; Compensation; Nominating/Governance": (["director", "other"], "i due comitati sono scritti senza dire se membro o presidente: other, da guardare"),
}
# parole che non contano quando si cerca testo non coperto dalle regole
NEUTRE = r"[\s;,\-()]|\band\b|\bof\b|\bthe\b|\bboard\b|\bdirectors\b|\bclass\b|\b[ivx]+\b|\bb\b|\bnominee\b|\bseries a preferred stock\b|\bstock\b|\bastronics corporation\b"


def codici(testo):
    if testo in MANUALI:
        return list(MANUALI[testo][0]), MANUALI[testo][1]
    resto, trovati = testo.lower(), []
    for cod, rx in REGOLE:
        if re.search(rx, resto):
            trovati.append(cod)
            resto = re.sub(rx, " ", resto)
    nota = ""
    avanzo = re.sub(NEUTRE, "", resto)
    if avanzo:
        nota = f"testo non coperto dalla regola: «{avanzo[:40]}»"
    return trovati or ["other"], nota


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--db", required=True)
    ap.add_argument("--release", default="2026-10-17")
    ap.add_argument("--riscrivi", action="store_true", help="riscrive anche se la tabella esiste (perde le revisioni)")
    a = ap.parse_args()
    dest = LAV / "proposta-ruoli.csv"
    if dest.exists() and not a.riscrivi:
        sys.exit(f"{dest.name} esiste: per non perdere le revisioni serve --riscrivi")
    raw = RAIZ / "rawdata/sec-edgar" / a.release
    db = json.load(open(a.db, encoding="utf-8"))
    per = {p: e["id"] for e in db["entities"] for p in ((e.get("sources") or {}).get("sec") or {}).get("person_ids", [])}
    quote = collections.Counter(r["target"] for r in db["relationships"] if r.get("type") == "ownership")
    aziende = {r["ticker"]: r for r in imp.leggi(raw / "aziende.csv")}
    t_az = {r["ticker"]: r["proposta_id"] for r in imp.leggi(LAV / "proposta-aziende.csv")}
    t_cl = collections.defaultdict(set)
    for r in imp.leggi(LAV / "proposta-classi.csv"):
        t_cl[r["ticker"]].add(r["id_proposto"])

    def scheda(t):
        c = sorted(t_cl.get(t, ()), key=lambda i: (-quote[i], i))
        return c[0] if c else t_az.get(t, "")

    note = {}

    def regola(ruolo, dett):
        cods, nota = codici(dett) if ruolo not in ("membro di comitato", "presidente di comitato") else (["committee_member"], "")
        if ruolo == "presidente di comitato":
            nota = "il presidente e un dettaglio del comitato (chair: true), non un codice a parte"
        implicito = ruolo == "consigliere" and "director" not in cods
        if implicito:
            cods = cods + ["director"]
        note[(ruolo, dett)] = nota
        return cods, implicito

    rels, usi, manc, lette = imp.costruisci_ruoli(raw, a.release, per, scheda,
                                                  lambda t: (aziende.get(t) or {}).get("quote_al") or None, regola)
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ruolo_nel_file", "dettaglio", "n_righe", "codici_proposti", "director_implicito", "nota", "revisione_nelson"])
        for (ru, dett), u in sorted(usi.items(), key=lambda kv: (kv[0][0], -kv[1]["n"], kv[0][1])):
            w.writerow([ru, dett, u["n"], " + ".join(u["codici"]), "si" if u["implicito"] else "", note.get((ru, dett), ""), ""])
    print(f"{lette} righe di ruolo, {len(usi)} diciture distinte, {len(rels)} relazioni persona-scheda; non risolte: {manc or 'nessuna'}")
    print(f"scritta {dest.relative_to(RAIZ)} (colonna revisione_nelson vuota: da compilare prima dell'import)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
