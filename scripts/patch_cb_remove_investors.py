#!/usr/bin/env python3
"""
patch_cb_remove_investors.py - toglie uno o piu nomi da sources.crunchbase.top_investors di UNA entita (per
esempio persone fisiche per cui non si vuole creare una scheda IV- con import_investors_crunchbase.py), senza
perdere il valore: la lista di prima resta nella voce di history (campo old). Dry-run di default.

Scrive: history {field: "sources.crunchbase.top_investors", old: lista, new: lista senza i nomi, ...} e una
validation `crunchbase_field_edited`. Non tocca altri campi, altre entita, relazioni.

Uso (dalla radice del repo):
    python3 scripts/patch_cb_remove_investors.py ID "Nome" ["Nome" ...] --why "motivo, in inglese" [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_cb_remove_investors.py"
TODAY = date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("names", nargs="+")
    ap.add_argument("--why", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation).")
    db = json.load(open(a.db, encoding="utf-8"))
    e = next((x for x in db["entities"] if x["id"] == a.entity), None)
    if not e:
        sys.exit("ERRORE: %s non esiste." % a.entity)
    if any(h.get("action") == "entity_retired" for h in e.get("history", [])):
        sys.exit("ERRORE: %s e una scheda ritirata." % a.entity)
    cb = (e.get("sources") or {}).get("crunchbase")
    if not isinstance(cb, dict) or not isinstance(cb.get("top_investors"), list):
        sys.exit("ERRORE: %s non ha sources.crunchbase.top_investors." % a.entity)
    old = list(cb["top_investors"])
    absent = [n for n in a.names if n not in old]
    if absent:
        sys.exit("ERRORE: nomi non presenti in top_investors: %s" % absent)
    new = [n for n in old if n not in a.names]
    print("%s patch_cb_remove_investors: %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.entity, e["name"]))
    print("  top_investors: %d -> %d" % (len(old), len(new)))
    print("  tolti: %s" % a.names)
    print("  restano: %s" % new)
    print("  motivo: %s" % a.why)
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    cb["top_investors"] = new
    e.setdefault("history", []).append({"date": TODAY, "source": "manual", "author": AUTHOR,
                                        "field": "sources.crunchbase.top_investors", "old": old, "new": new,
                                        "description": a.why})
    e.setdefault("validation", []).append({"status": "crunchbase_field_edited", "field": "top_investors",
                                           "removed": a.names, "description": a.why, "author": AUTHOR,
                                           "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


main()
