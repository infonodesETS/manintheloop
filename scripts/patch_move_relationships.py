#!/usr/bin/env python3
"""
patch_move_relationships.py - sposta alcune relazioni `investment` da una scheda a un'altra (cambia il target),
quando il profilo Crunchbase da cui nascono e passato dalla prima scheda alla seconda (patch_clear_crunchbase.py
+ patch_set_crunchbase.py). Le relazioni restano le stesse (stessi campi, stessa data di creazione): cambia solo
il target. Niente viene cancellato: ogni relazione spostata riceve una voce di history con il vecchio target, e
le due schede ricevono una voce di history e una di validation. Dry-run di default.

Controlli: solo tipo `investment` (i tipi nuovi ownership/role/parte_di hanno regole proprie, S5); le due schede
esistono e non sono ritirate; ogni relazione richiesta esiste (source -> DA, tipo investment); nessuna uguale
esiste gia su A (si ferma, exit 2).

Uso (dalla radice del repo):
    python3 scripts/patch_move_relationships.py DA A IV-0001 [IV-0002 ...] --why "motivo, in inglese" [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_move_relationships.py"
TODAY = date.today().isoformat()


def retired(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("from_entity")
    ap.add_argument("to_entity")
    ap.add_argument("sources", nargs="+", help="ID dei nodi source delle relazioni da spostare")
    ap.add_argument("--why", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation).")
    db = json.load(open(a.db, encoding="utf-8"))
    by = {e["id"]: e for e in db["entities"]}
    for i in (a.from_entity, a.to_entity):
        if i not in by:
            sys.exit("ERRORE: %s non esiste." % i)
        if retired(by[i]):
            sys.exit("ERRORE: %s e una scheda ritirata." % i)
    if a.from_entity == a.to_entity:
        sys.exit("ERRORE: le due schede sono la stessa.")
    rels = db["relationships"]
    moves = []
    for s in a.sources:
        found = [r for r in rels if r["source"] == s and r["target"] == a.from_entity and r["type"] == "investment"]
        if len(found) != 1:
            sys.exit("ERRORE: attesa 1 relazione investment %s -> %s, trovate %d." % (s, a.from_entity, len(found)))
        if any(r["source"] == s and r["target"] == a.to_entity and r["type"] == "investment" for r in rels):
            print("STOP: esiste gia una relazione investment %s -> %s." % (s, a.to_entity))
            sys.exit(2)
        moves.append(found[0])
    print("%s patch_move_relationships: %s (%s) -> %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.from_entity,
          by[a.from_entity]["name"], a.to_entity, by[a.to_entity]["name"]))
    for r in moves:
        print("  investment %s (%s) -> %s: %s" % (r["source"], by[r["source"]]["name"], a.to_entity,
              {k: v for k, v in r.items() if k not in ("source", "target", "type")}))
    print("  relazioni totali prima/dopo: %d / %d (invariate)" % (len(rels), len(rels)))
    print("  motivo: %s" % a.why)
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    ids = [r["source"] for r in moves]
    for r in moves:
        r["target"] = a.to_entity
        r.setdefault("history", []).append({"date": TODAY, "author": AUTHOR,
            "description": "Target moved: %s -> %s. %s" % (a.from_entity, a.to_entity, a.why)})
    for eid, act, other in ((a.from_entity, "relationships_moved_out", a.to_entity),
                            (a.to_entity, "relationships_moved_in", a.from_entity)):
        e = by[eid]
        e.setdefault("history", []).append({"date": TODAY, "source": "manual", "author": AUTHOR, "action": act,
            "field": "relationships", "old": None, "new": None, "relationship_sources": ids, "other_entity": other,
            "description": "%d investment relationship(s) %s %s: %s" % (len(ids), "moved to" if act.endswith("out") else "moved from", other, a.why)})
        e.setdefault("validation", []).append({"status": "confirmed", "description": "Relationships moved (%s): %s. %s" % (act, ", ".join(ids), a.why),
            "author": AUTHOR, "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


main()
