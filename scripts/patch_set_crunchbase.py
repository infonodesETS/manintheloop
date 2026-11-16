#!/usr/bin/env python3
"""
patch_set_crunchbase.py - scrive sources.crunchbase di UNA entita (che ora lo ha a null) da un file JSON con il
blocco preparato a mano. Usare dopo patch_clear_crunchbase.py. Dry-run di default.

Controlli: il blocco deve avere esattamente le chiavi dello schema (quelle di un blocco gia presente nel database);
sources.crunchbase deve essere null; la scheda non deve essere ritirata. Scrive una voce di history
{field: "sources.crunchbase", old: null, new: <blocco>} e una validation `crunchbase_enriched`.
Non tocca altri campi, altre entita, relazioni. NON lancia import_investors_crunchbase.py.

Uso (dalla radice del repo):
    python3 scripts/patch_set_crunchbase.py ID blocco.json --why "motivo, in inglese" [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_set_crunchbase.py"
TODAY = date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("block")
    ap.add_argument("--why", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation).")
    db = json.load(open(a.db, encoding="utf-8"))
    block = json.load(open(a.block, encoding="utf-8"))
    e = next((x for x in db["entities"] if x["id"] == a.entity), None)
    if not e:
        sys.exit("ERRORE: %s non esiste." % a.entity)
    if any(h.get("action") == "entity_retired" for h in e.get("history", [])):
        sys.exit("ERRORE: %s e una scheda ritirata." % a.entity)
    if (e.get("sources") or {}).get("crunchbase"):
        sys.exit("ERRORE: %s ha gia un blocco crunchbase (toglierlo prima con patch_clear_crunchbase.py)." % a.entity)
    ref = next(x["sources"]["crunchbase"] for x in db["entities"]
               if isinstance((x.get("sources") or {}).get("crunchbase"), dict) and x["sources"]["crunchbase"])
    miss, extra = set(ref) - set(block), set(block) - set(ref)
    if miss or extra:
        sys.exit("ERRORE: chiavi diverse dallo schema. mancanti %s, in piu %s" % (sorted(miss), sorted(extra)))
    print("%s patch_set_crunchbase: %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.entity, e["name"]))
    for k in ref:
        print("  %-26s %r" % (k, block[k] if len(str(block[k])) < 110 else str(block[k])[:107] + "..."))
    print("  motivo: %s" % a.why)
    print("  history/validation presenti: %d / %d" % (len(e.get("history", [])), len(e.get("validation", []))))
    for v in e.get("validation", []):
        print("    V %s | %s | %s" % (v.get("datestamp"), v.get("status"), str(v.get("description") or "")[:120]))
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    e.setdefault("sources", {})["crunchbase"] = block
    e.setdefault("history", []).append({"date": TODAY, "source": "manual", "author": AUTHOR,
                                        "field": "sources.crunchbase", "old": None, "new": block, "description": a.why})
    e.setdefault("validation", []).append({"status": "crunchbase_enriched", "cb_url": block.get("profile_url"),
                                           "description": a.why, "author": AUTHOR, "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


main()
