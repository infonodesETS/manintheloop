#!/usr/bin/env python3
"""
patch_remove_edf_duplicates.py - toglie da una scheda le relazioni `edf_participation` che sono copie di
relazioni di un'altra scheda (stesso progetto, stesso ruolo, stesso contributo UE). Nasce dal caso Airbus
Defence and Space (2026-11-19): edf_orgs.json puntava i 4 PIC a una sola scheda e l'import ne aveva copiato le
partecipazioni; dopo aver corretto edf_orgs.json ogni PIC ha la sua scheda e le copie restano su IN-0467.

Regole (si ferma con exit 2 se una non vale):
  - si toglie una relazione solo se un'ALTRA scheda attiva ha una relazione edf_participation verso lo stesso
    progetto con stesso ruolo e stesso eu_contribution (la copia non porta informazione che non sia altrove);
  - le relazioni da tenere si elencano con --keep EDF-NNNN (nessuna altra viene toccata);
  - niente va perso: le relazioni tolte sono copiate per intero nella voce di history della scheda
    (campo `relationships`, `old`) e riassunte in una voce di validation.
Dry-run di default.

Uso (dalla radice del repo):
    python3 scripts/patch_remove_edf_duplicates.py IN-0467 --keep EDF-0032 --why "motivo, in inglese" [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_remove_edf_duplicates.py"
TODAY = date.today().isoformat()


def retired(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("--keep", nargs="*", default=[], help="progetti EDF-NNNN da NON toccare")
    ap.add_argument("--why", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation).")
    db = json.load(open(a.db, encoding="utf-8"))
    by = {e["id"]: e for e in db["entities"]}
    if a.entity not in by:
        sys.exit("ERRORE: %s non esiste." % a.entity)
    if retired(by[a.entity]):
        sys.exit("ERRORE: %s e una scheda ritirata." % a.entity)
    rels = db["relationships"]
    mine = [r for r in rels if r["type"] == "edf_participation" and r["source"] == a.entity and r["target"] not in a.keep]
    for k in a.keep:
        if not any(r["type"] == "edf_participation" and r["source"] == a.entity and r["target"] == k for r in rels):
            sys.exit("ERRORE: --keep %s non e una partecipazione di %s." % (k, a.entity))
    remove, bad = [], []
    for r in mine:
        copy = [o for o in rels if o is not r and o["type"] == "edf_participation" and o["target"] == r["target"]
                and o["source"] != a.entity and o["source"] in by and not retired(by[o["source"]])
                and o.get("role") == r.get("role") and o.get("eu_contribution") == r.get("eu_contribution")]
        (remove if copy else bad).append((r, [o["source"] for o in copy]))
    print("%s patch_remove_edf_duplicates: %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.entity, by[a.entity]["name"]))
    for r, where in remove:
        print("  togli %s -> %s  %s %s  (copia su %s)" % (r["source"], r["target"], r.get("role"), r.get("eu_contribution"), ", ".join(where)))
    if bad:
        for r, _ in bad:
            print("STOP: %s -> %s %s %s non ha una copia identica su un'altra scheda attiva." % (r["source"], r["target"], r.get("role"), r.get("eu_contribution")))
        sys.exit(2)
    print("  tenute: %s | tolte: %d | relazioni %d -> %d" % (", ".join(a.keep) or "nessuna", len(remove), len(rels), len(rels) - len(remove)))
    if not remove:
        print("Nulla da fare.")
        return
    if not a.apply:
        print("DRY-RUN: nessuna modifica scritta.")
        return
    gone = {id(r) for r, _ in remove}
    db["relationships"] = [r for r in rels if id(r) not in gone]
    e = by[a.entity]
    e.setdefault("history", []).append({
        "date": TODAY, "source": "manual", "author": AUTHOR, "field": "relationships",
        "old": [r for r, _ in remove], "new": None,
        "description": "%d edf_participation relationships removed: each is an identical copy (same project, role and EU contribution) of a relationship on another active card. %s" % (len(remove), a.why)})
    e.setdefault("validation", []).append({
        "status": "relationships_removed",
        "description": "%d duplicate edf_participation relationships removed (full copies in history). Kept: %s. %s" % (len(remove), ", ".join(a.keep) or "none", a.why),
        "author": AUTHOR, "datestamp": TODAY})
    json.dump(db, open(a.db, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("Scritto %s. Ora: python3 scripts/validate.py" % a.db)


if __name__ == "__main__":
    main()
