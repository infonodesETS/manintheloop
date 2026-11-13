#!/usr/bin/env python3
"""
patch_clear_infonodes.py - mette a null alcuni campi di sources.infonodes di UN'entita quando descrivono
un'altra entita (per esempio la casa madre), senza perdere il valore: il vecchio valore resta nella voce di
history (campo "old"). Dry-run di default.

Per ogni campo: history (append-only) {field: "sources.infonodes.<campo>", old: valore, new: null, ...} e
una sola validation `infonodes_field_removed` con l'elenco e il motivo. Non tocca altri campi, altre entita,
relazioni.

Uso (dalla radice del repo):
    python3 scripts/patch_clear_infonodes.py ID campo [campo ...] --why "motivo" [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_clear_infonodes.py"
TODAY = date.today().isoformat()
ALLOWED = {"wikipedia_url", "main_focus", "tax_id", "website", "sector", "country"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("fields", nargs="+")
    ap.add_argument("--why", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    bad = [f for f in a.fields if f not in ALLOWED]
    if bad:
        sys.exit("ERRORE: campi non ammessi %s (ammessi: %s)" % (bad, sorted(ALLOWED)))
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation).")
    db = json.load(open(a.db, encoding="utf-8"))
    e = next((x for x in db["entities"] if x["id"] == a.entity), None)
    if not e:
        sys.exit("ERRORE: %s non esiste." % a.entity)
    if any(h.get("action") == "entity_retired" for h in e.get("history", [])):
        sys.exit("ERRORE: %s e una lapide." % a.entity)
    inf = (e.get("sources") or {}).get("infonodes")
    if not isinstance(inf, dict):
        sys.exit("ERRORE: %s non ha sources.infonodes." % a.entity)
    todo = [(f, inf.get(f)) for f in a.fields if inf.get(f) is not None]
    print("%s patch_clear_infonodes: %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.entity, e["name"]))
    for f in a.fields:
        print("  sources.infonodes.%s: %r -> null%s" % (f, inf.get(f), "" if inf.get(f) is not None else " (gia vuoto: salto)"))
    print("  motivo: %s" % a.why)
    if not todo:
        sys.exit("Nulla da fare.")
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    for f, old in todo:
        inf[f] = None
        e.setdefault("history", []).append({"date": TODAY, "source": "manual", "author": AUTHOR,
                                            "field": "sources.infonodes." + f, "old": old, "new": None,
                                            "description": a.why})
    e.setdefault("validation", []).append({"status": "infonodes_field_removed",
                                           "fields_removed": [f for f, _ in todo], "description": a.why,
                                           "author": AUTHOR, "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


main()
