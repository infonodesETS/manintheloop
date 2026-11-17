#!/usr/bin/env python3
"""B5 Release 1, passo 2b: PROPOSTA della tabella ticker + classe -> scheda (S3 R3).

Sola lettura. Parte dalla mappatura descritta in reference/S3-CLASSI-AZIONI.md
(gruppi 1-4, scritta dall'AI il 2026-11-11 con righe «?» da confermare) e la
VERIFICA contro il database (scheda esistente? attiva? nome? ticker iShares?).
Dove la classe manca nel database la proposta e
«madre» (regola sulle classi del 2026-11-12: IN-0017/IN-0018 e IN-0282 sono ritirate) o «attaccare» a
la scheda esistente della stessa societa (la classe vive nel campo `classe`, S3 R2); l'alternativa «nuova entita»
(esempio A di S3) e una decisione di Nelson (D1): e una proposta, la decide una persona.
Scrive solo work/b5-release1/proposta-classi.csv.
Uso: python3 -I work/b5-release1/proponi_classi.py
"""
import csv, json, pathlib, collections

RAIZ = pathlib.Path(__file__).resolve().parents[2]
REL = RAIZ / "rawdata/sec-edgar/2026-10-17"
OUT = RAIZ / "work/b5-release1/proposta-classi.csv"

# ticker -> (gruppo S3, {chiave classe normalizzata: ("esistente", ID) | ("nuova", "") | ("madre", ID)})
# La chiave e la classe del filing in minuscolo senza «common stock/stock».
M = {
    # Gruppo 1: una sola scheda, basta il campo classe
    "ATRO": (1, {"*": ("esistente", "IN-1395")}),
    "RDW": (1, {"*": ("esistente", "IN-1408")}),
    "RKLB": (1, {"*": ("esistente", "IN-1365")}),
    "UAMY": (1, {"*": ("esistente", "IN-0396")}),
    "USAR": (1, {"*": ("esistente", "IN-0398")}),
    # Gruppo 2: una scheda per classe, gia presenti
    "FOX": (2, {"class a": ("esistente", "IN-0135"), "class b": ("esistente", "IN-0136")}),
    "NWS": (2, {"class a": ("esistente", "IN-0250"), "class b": ("esistente", "IN-0251")}),
    "HEI": (2, {"common": ("esistente", "IN-1378"), "class a": ("esistente", "IN-1372")}),
    # Gruppo 3: nel DB c'e una sola classe
    "APP": (3, {"class a": ("esistente", "IN-0034"), "class b": ("attaccare", "IN-0034")}),
    "CMCSA": (3, {"class a": ("esistente", "IN-0095"), "class b": ("attaccare", "IN-0095")}),
    "DDOG": (3, {"class a": ("esistente", "IN-0106"), "class b": ("attaccare", "IN-0106")}),
    "WDAY": (3, {"class a": ("esistente", "IN-0422"), "class b": ("attaccare", "IN-0422")}),
    "METC": (3, {"class a": ("esistente", "IN-0298"), "class b": ("attaccare", "IN-0298")}),
    "TTD": (3, {"class a": ("esistente", "IN-0388"), "class b": ("attaccare", "IN-0388")}),
    "SATS": (3, {"class a": ("esistente", "IN-0116"), "class b": ("attaccare", "IN-0116")}),
    "META": (3, {"class a": ("esistente", "IN-0228"), "class b": ("attaccare", "IN-0228")}),
    "DELL": (3, {"class c": ("esistente", "IN-0107"), "class a": ("attaccare", "IN-0107"), "class b": ("attaccare", "IN-0107")}),
    "LUNR": (3, {"class a": ("esistente", "IN-1397"), "class c": ("attaccare", "IN-1397")}),
    "MOG-A": (3, {"class a": ("esistente", "IN-1381"), "class b": ("attaccare", "IN-1381")}),
    "TKO": (3, {"class a": ("esistente", "IN-0382"), "class b": ("attaccare", "IN-0382")}),
    # Gruppo 4: madre e classi
    "GOOG": (4, {"class a": ("madre", "IN-1247"), "class b": ("madre", "IN-1247")}),
    "PLTR": (4, {"class a": ("madre", "IN-1318"), "class b": ("madre", "IN-1318"),
                 "class f": ("madre", "IN-1318")}),
}


def chiave(classe):
    s = classe.lower().strip()
    for suf in (" common stock", " stock", " preferred stock", " preferred"):
        if s.endswith(suf) and "preferred" not in suf:
            s = s[: -len(suf)]
    return s.strip()


def stato(e):
    if e is None:
        return "NON ESISTE"
    for h in e.get("history", []):
        if h.get("action") == "entity_retired":
            return "RITIRATA"
    v = [x.get("status") for x in e.get("validation", [])]
    extra = [s for s in ("share_class_variant", "accepted_duplicate") if s in v]
    return "attiva" + (" (" + ",".join(extra) + ")" if extra else "")


def main():
    db = json.load(open(RAIZ / "docs/data/database.json", encoding="utf-8"))
    per_id = {e["id"]: e for e in db["entities"]}
    det = list(csv.DictReader(open(REL / "detentori-oltre-5.csv", encoding="utf-8")))
    conta = collections.defaultdict(collections.Counter)
    for r in det:
        conta[r["ticker"]][r["classe"]] += 1
    righe, problemi = [], 0
    for t in sorted(M):
        gruppo, mappa = M[t]
        for classe, n in sorted(conta[t].items()):
            k = chiave(classe)
            az, i = mappa.get("*") or mappa.get(k) or mappa.get(k.replace("common", "").strip()) or ("", "")
            if not az:
                az = "NON MAPPATA"
                problemi += 1
            e = per_id.get(i) if i else None
            tk = sorted({(x.get("stock_ticker") or "").upper() for x in ((e or {}).get("sources", {}).get("ishares") or [])})
            esito = stato(e) if i else "-"
            note = []
            if i and esito.startswith(("NON", "RITIR")):
                note.append("PROBLEMA: scheda non utilizzabile")
                problemi += 1
            if i and az == "esistente" and t.upper() not in tk and tk:
                note.append(f"ticker iShares della scheda: {','.join(tk)} (non {t})")
            righe.append({
                "ticker": t, "classe_nel_filing": classe, "n_righe": n, "gruppo_S3": gruppo,
                "azione_proposta": az, "id_proposto": i,
                "nome_scheda": (e or {}).get("name", ""), "stato_scheda": esito,
                "qid_scheda": (e or {}).get("wikidata_id") or "",
                "nota_automatica": "; ".join(note),
                "revisione_nelson": "", "nota": "",
            })
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)
    c = collections.Counter(r["azione_proposta"] for r in righe)
    print(f"{len(righe)} righe (ticker+classe) su {len(M)} aziende; problemi: {problemi}")
    print(dict(c))
    print(f"scritto {OUT.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
