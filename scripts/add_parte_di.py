#!/usr/bin/env python3
"""
add_parte_di.py - aggiunge UNA relazione `parte_di` (figlia -> capogruppo legale) tra due schede gia presenti.

Dry-run di default. Non tocca altre schede, altre relazioni, history esistenti. Modello e regole:
reference/S6-GESTORI.md e reference/SCHEMA.md (sezione parte_di).

Scrive: la relazione (id REL-NNNN = massimo esistente + 1, mai riusato; il primo e REL-0001) e UNA voce
`validation` con status `confirmed` sulla scheda figlia (testo in inglese, da --why). `_updated` a oggi.

Controlli (exit 1 se falliscono): le due schede esistono, sono IV-/IN-, non sono ritirate, non sono la stessa;
il legame (figlia, capogruppo, parte_di) non esiste gia; con --current true serve --as-of (data della fonte
primaria piu recente) e nessun ciclo tra i legami correnti; --fino-al solo con --current false.

Autore: --author e obbligatorio e porta l'approvazione di chi decide, nella forma gia usata nel database:
"nelsonmau (proposed by Claude, approved AAAA-MM-GG)". Lo script non puo sapere se c'e stata: non la inventa.

Campi: forma (controllata | divisione | non_chiaro), current (true | false), diretta (si | no | nd:
si = capogruppo immediata; no = tra le due c'e una societa senza scheda; nd = non accertato), source_ref
(fonte primaria: URL o riferimento), as_of, fino_al. Le percentuali NON si scrivono qui (restano in `ownership`).

Il dry-run stampa history e validation di entrambe le schede: vanno lette prima di --apply
(--history-letta e obbligatorio con --apply).

Uso (dalla radice del repo):
    python3 scripts/add_parte_di.py FIGLIA CAPOGRUPPO --forma controllata --current true --diretta si \\
        --as-of 2024-02-15 --source-ref "https://..." --why "text in English" \\
        --author "nelsonmau (proposed by Claude, approved AAAA-MM-GG)" [--history-letta --apply]
Dopo: python3 scripts/validate.py && python3 -I scripts/check_parte_di_branch.py
"""
import argparse, json, re, sys
from datetime import date

TODAY = date.today().isoformat()
FORME = ("controllata", "divisione", "non_chiaro")
REL_ID_RE = re.compile(r"^REL-(\d{4,})$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def retired(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("figlia")
    ap.add_argument("capogruppo")
    ap.add_argument("--forma", required=True, choices=FORME)
    ap.add_argument("--current", required=True, choices=("true", "false"))
    ap.add_argument("--diretta", required=True, choices=("si", "no", "nd"))
    ap.add_argument("--source-ref", required=True)
    ap.add_argument("--why", required=True, help="testo della voce di validation (in inglese)")
    ap.add_argument("--author", required=True, help='chi ha approvato, es. "nelsonmau (proposed by Claude, approved AAAA-MM-GG)"')
    ap.add_argument("--as-of", default=None, help="data della fonte primaria piu recente (AAAA-MM-GG)")
    ap.add_argument("--fino-al", default=None, help="data di fine del legame (AAAA-MM-GG, solo con --current false)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation delle due schede, che il dry-run stampa).")
    for nm, val in (("--as-of", a.as_of), ("--fino-al", a.fino_al)):
        if val and not DATE_RE.match(val):
            sys.exit("ERRORE: %s deve essere AAAA-MM-GG." % nm)
    cur = a.current == "true"
    if cur and not a.as_of:
        sys.exit("ERRORE: con --current true serve --as-of (data della fonte primaria piu recente).")
    if a.fino_al and cur:
        sys.exit("ERRORE: --fino-al ha senso solo con --current false.")
    if not a.source_ref.strip() or not a.why.strip() or not a.author.strip():
        sys.exit("ERRORE: --source-ref, --why e --author non possono essere vuoti.")
    if "approved" not in a.author:
        sys.exit('ERRORE: --author deve riportare l\'approvazione, es. "nelsonmau (proposed by Claude, approved AAAA-MM-GG)".')

    db = json.load(open(a.db, encoding="utf-8"))
    E = {e["id"]: e for e in db["entities"]}
    errs = []
    for label, eid in (("figlia", a.figlia), ("capogruppo", a.capogruppo)):
        e = E.get(eid)
        if not e:
            errs.append("%s %s non esiste" % (label, eid)); continue
        if not re.match(r"^(IV|IN)-\d{4,}$", eid):
            errs.append("%s %s: servono schede IV-/IN-" % (label, eid))
        if retired(e):
            errs.append("%s %s e una scheda ritirata" % (label, eid))
    if a.figlia == a.capogruppo:
        errs.append("figlia e capogruppo coincidono")
    for r in db["relationships"]:
        if r["type"] == "parte_di" and r["source"] == a.figlia and r["target"] == a.capogruppo:
            errs.append("il legame esiste gia (%s): questo script non modifica legami esistenti" % r.get("id"))
    if cur and not errs:  # ciclo: dalla capogruppo si risale fino alla figlia?
        up = {}
        for r in db["relationships"]:
            if r["type"] == "parte_di" and r.get("current") is True:
                up.setdefault(r["source"], set()).add(r["target"])
        stack, seen = [a.capogruppo], set()
        while stack:
            x = stack.pop()
            if x == a.figlia:
                errs.append("il legame creerebbe un ciclo tra legami correnti"); break
            if x in seen:
                continue
            seen.add(x)
            stack.extend(up.get(x, ()))
    if errs:
        for m in errs:
            print("ERRORE:", m)
        sys.exit(1)

    for eid in (a.figlia, a.capogruppo):
        e = E[eid]
        print("\n  %s (%s): %d voci di history, %d di validation" % (eid, e.get("name"), len(e.get("history", [])), len(e.get("validation", []))))
        for h in e.get("history", []):
            print("    H %s | %s | %s | %s" % (h.get("date") or h.get("datestamp"), h.get("author") or h.get("script"),
                                                 h.get("field") or h.get("action"), str(h.get("description") or h.get("note") or "")[:140]))
        for v in e.get("validation", []):
            print("    V %s | %s | %s" % (v.get("datestamp"), v.get("status"), str(v.get("description") or v.get("note") or "")[:130]))
    nums = [int(m.group(1)) for r in db["relationships"] if (m := REL_ID_RE.match(str(r.get("id", ""))))]
    rid = "REL-%04d" % ((max(nums) + 1) if nums else 1)
    diretta = {"si": True, "no": False, "nd": None}[a.diretta]
    rel = {"id": rid, "type": "parte_di", "source": a.figlia, "target": a.capogruppo,
           "forma": a.forma, "current": cur, "diretta": diretta, "as_of": a.as_of, "fino_al": a.fino_al,
           "source_ref": a.source_ref.strip(), "created_at": TODAY, "history": []}
    voce = {"status": "confirmed", "description": a.why.strip(), "author": a.author.strip(), "datestamp": TODAY}
    print("\n%s: nuova relazione e nuova voce di validation su %s" % ("APPLICA" if a.apply else "DRY-RUN", a.figlia))
    print("  REL ", json.dumps(rel, ensure_ascii=False))
    print("  VAL ", json.dumps(voce, ensure_ascii=False))
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    db["relationships"].append(rel)
    E[a.figlia].setdefault("validation", []).append(voce)
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as f:
        f.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py && python3 -I scripts/check_parte_di_branch.py" % a.db)


if __name__ == "__main__":
    main()
