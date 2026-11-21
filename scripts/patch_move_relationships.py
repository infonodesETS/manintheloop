#!/usr/bin/env python3
"""
patch_move_relationships.py - sposta alcune relazioni `investment` da una scheda a un'altra (cambia il target),
quando il profilo Crunchbase da cui nascono e passato dalla prima scheda alla seconda (patch_clear_crunchbase.py
+ patch_set_crunchbase.py). Le relazioni restano le stesse (stessi campi, stessa data di creazione): cambia solo
il target. Niente viene cancellato: ogni relazione spostata riceve una voce di history con il vecchio target, e
le due schede ricevono una voce di history e una di validation. Dry-run di default.

Controlli: solo tipo `investment` (i tipi nuovi ownership/role/parte_di hanno regole proprie, S5); le due schede
esistono e non sono ritirate; ogni relazione richiesta esiste (source -> DA, tipo investment); nessuna uguale
esiste gia su A (si ferma, exit 2), salvo --merge-duplicates.

--merge-duplicates (2026-11-21, caso Helsing IN-0724 -> IN-0723): se su A c'e gia la stessa relazione (stesso
source, tipo investment), quella di DA viene tolta e conservata intera nella history di DA (voce
`relationships_removed`, campo old) piu una validation `relationships_removed`; alla relazione di A si aggiungono
solo le chiavi di `details` che le mancano (mai sovrascritte: valori in conflitto fermano lo script, exit 2), con
una voce nella history della relazione.

Uso (dalla radice del repo):
    python3 scripts/patch_move_relationships.py DA A IV-0001 [IV-0002 ...] --why "motivo, in inglese" [--merge-duplicates] [--history-letta --apply]
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
    ap.add_argument("--merge-duplicates", action="store_true",
                    help="se A ha gia la stessa relazione investment: togli quella di DA (copia intera nella history di DA) "
                         "e aggiungi alla relazione di A solo le chiavi di details che le mancano (voce di history sulla relazione)")
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
    moves, merges = [], []
    for s in a.sources:
        found = [r for r in rels if r["source"] == s and r["target"] == a.from_entity and r["type"] == "investment"]
        if len(found) != 1:
            sys.exit("ERRORE: attesa 1 relazione investment %s -> %s, trovate %d." % (s, a.from_entity, len(found)))
        on_to = [r for r in rels if r["source"] == s and r["target"] == a.to_entity and r["type"] == "investment"]
        if on_to:
            if not a.merge_duplicates or len(on_to) != 1:
                print("STOP: esiste gia una relazione investment %s -> %s." % (s, a.to_entity))
                sys.exit(2)
            dup, keep = found[0], on_to[0]
            add = {k: v for k, v in (dup.get("details") or {}).items() if k not in (keep.get("details") or {})}
            clash = {k: (v, keep["details"][k]) for k, v in (dup.get("details") or {}).items()
                     if k in (keep.get("details") or {}) and keep["details"][k] != v}
            if clash:
                print("STOP: details in conflitto per %s: %s" % (s, clash))
                sys.exit(2)
            merges.append((dup, keep, add))
            continue
        moves.append(found[0])
    print("%s patch_move_relationships: %s (%s) -> %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.from_entity,
          by[a.from_entity]["name"], a.to_entity, by[a.to_entity]["name"]))
    for r in moves:
        print("  investment %s (%s) -> %s: %s" % (r["source"], by[r["source"]]["name"], a.to_entity,
              {k: v for k, v in r.items() if k not in ("source", "target", "type")}))
    for dup, keep, add in merges:
        print("  copia %s -> %s tolta (resta %s -> %s, source_ref %s); details aggiunti: %s; copia: %s" % (
            dup["source"], a.from_entity, keep["source"], a.to_entity, keep.get("source_ref"), add or "nessuno",
            {k: v for k, v in dup.items() if k not in ("source", "target", "type")}))
    print("  relazioni totali prima/dopo: %d / %d" % (len(rels), len(rels) - len(merges)))
    print("  motivo: %s" % a.why)
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    ids = [r["source"] for r in moves]
    gone = {id(d) for d, _, _ in merges}
    if merges:
        db["relationships"] = [r for r in rels if id(r) not in gone]
        for dup, keep, add in merges:
            if add:
                keep.setdefault("details", {}).update(add)
            keep.setdefault("history", []).append({"date": TODAY, "author": AUTHOR,
                "description": "Duplicate %s -> %s (source_ref %s, created_at %s) removed; details added from it: %s. %s" % (
                    dup["source"], a.from_entity, dup.get("source_ref"), dup.get("created_at"),
                    json.dumps(add, ensure_ascii=False) if add else "none", a.why)})
        by[a.from_entity].setdefault("history", []).append({"date": TODAY, "source": "manual", "author": AUTHOR,
            "action": "relationships_removed", "field": "relationships", "old": [d for d, _, _ in merges], "new": None,
            "other_entity": a.to_entity,
            "description": "%d investment relationship(s) removed: each duplicates a relationship already on %s (same source, type investment); full copies in old, details not on %s copied there. %s" % (
                len(merges), a.to_entity, a.to_entity, a.why)})
        by[a.from_entity].setdefault("validation", []).append({"status": "relationships_removed",
            "description": "Duplicate investment relationships removed (full copies in history): %s; kept on %s. %s" % (
                ", ".join(d["source"] for d, _, _ in merges), a.to_entity, a.why), "author": AUTHOR, "datestamp": TODAY})
    for r in moves:
        r["target"] = a.to_entity
        r.setdefault("history", []).append({"date": TODAY, "author": AUTHOR,
            "description": "Target moved: %s -> %s. %s" % (a.from_entity, a.to_entity, a.why)})
    for eid, act, other in (((a.from_entity, "relationships_moved_out", a.to_entity),
                             (a.to_entity, "relationships_moved_in", a.from_entity)) if ids else ()):
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
