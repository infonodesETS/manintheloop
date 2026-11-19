#!/usr/bin/env python3
"""
patch_rename_entity.py - cambia il nome di UNA scheda, con il nome vecchio conservato in history (come fa
merge_entities.py --rename: voce `field_corrected`, campo name, old_value/new_value) e una validation `confirmed`.
Dry-run di default. Non tocca altri campi, altre schede, relazioni, edf_orgs.json (che porta il nome EDF del PIC,
non il nome della scheda).

Uso (dalla radice del repo):
    python3 scripts/patch_rename_entity.py ID "Nuovo nome" --why "motivo, in inglese" [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_rename_entity.py"
TODAY = date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("name")
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
    new = a.name.strip()
    if not new or new == e["name"]:
        sys.exit("ERRORE: nome vuoto o uguale a quello attuale.")
    same = [x["id"] for x in db["entities"] if x["id"] != a.entity and x["name"].strip().lower() == new.lower()
            and not any(h.get("action") == "entity_retired" for h in x.get("history", []))]
    print("%s patch_rename_entity: %s  '%s' -> '%s'" % ("APPLICA" if a.apply else "DRY-RUN", a.entity, e["name"], new))
    print("  altre schede attive con lo stesso nome: %s" % (same or "nessuna"))
    print("  motivo: %s" % a.why)
    if same:
        sys.exit("ERRORE: esiste gia una scheda attiva con questo nome.")
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    old = e["name"]
    e["name"] = new
    e.setdefault("history", []).append({"date": TODAY, "action": "field_corrected", "field": "name", "old_value": old,
                                        "new_value": new, "author": AUTHOR, "note": a.why})
    e.setdefault("validation", []).append({"status": "confirmed", "description": "Name corrected: '%s' -> '%s'. %s" % (old, new, a.why),
                                           "author": AUTHOR, "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


main()
