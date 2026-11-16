#!/usr/bin/env python3
"""
patch_clear_crunchbase.py - mette a null sources.crunchbase di UNA entita quando il blocco appartiene a un'altra
entita (profilo Crunchbase sbagliato), senza perdere il contenuto: l'INTERO blocco vecchio resta nel campo "old"
della voce di history (append-only, principio 2 di UPDATE_PROTOCOL). Dry-run di default.

Scrive: una voce di history {field: "sources.crunchbase", old: <blocco>, new: null, ...} e una voce di
validation `cb_wrong_entity` (stato gia in uso, 18 voci; porta l'URL del profilo tolto in `cb_url_removed`).
Non tocca altri campi, altre entita, relazioni. Non importa il profilo giusto.

Uso (dalla radice del repo):
    python3 scripts/patch_clear_crunchbase.py ID --why "motivo, in inglese" [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_clear_crunchbase.py"
TODAY = date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
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
    if not isinstance(cb, dict) or not cb:
        sys.exit("ERRORE: %s non ha sources.crunchbase." % a.entity)
    print("%s patch_clear_crunchbase: %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.entity, e["name"]))
    print("  profilo: %s" % cb.get("profile_url"))
    print("  blocco vecchio (finira in history.old): %d campi, descrizione %r, sede %r" % (
        len(cb), (cb.get("description") or "")[:90], cb.get("headquarters")))
    print("  motivo: %s" % a.why)
    print("  history/validation presenti: %d / %d" % (len(e.get("history", [])), len(e.get("validation", []))))
    for v in e.get("validation", []):
        print("    V %s | %s | %s" % (v.get("datestamp"), v.get("status"), str(v.get("description") or "")[:120]))
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    old = e["sources"]["crunchbase"]
    e["sources"]["crunchbase"] = None
    e.setdefault("history", []).append({"date": TODAY, "source": "manual", "author": AUTHOR,
                                        "field": "sources.crunchbase", "old": old, "new": None, "description": a.why})
    e.setdefault("validation", []).append({"status": "cb_wrong_entity", "cb_url_removed": old.get("profile_url"),
                                           "description": a.why, "author": AUTHOR, "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


if __name__ == "__main__":
    main()
