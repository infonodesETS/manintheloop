#!/usr/bin/env python3
"""
patch_set_infonodes.py - scrive un valore in un campo VUOTO di sources.infonodes di UN'entita, con fonte
primaria. Gemello di patch_clear_infonodes.py (che svuota). Dry-run di default.

Campi ammessi (per ora): tax_id. Il campo deve essere vuoto (null o assente): se ha gia un valore, prima lo si
svuota con patch_clear_infonodes.py (che conserva il vecchio valore nella history). Rifiuta se un'altra scheda
ATTIVA ha gia lo stesso valore (segno di duplicato o di scheda di gruppo: da guardare a mano, non da forzare).

Scrive: history (append-only) {field: "sources.infonodes.<campo>", old: null, new: valore, ...} e una sola
validation `infonodes_field_set` con la fonte. Non tocca altri campi, altre entita, relazioni.

La fonte (--source) e un riferimento primario: registro, deposito, GLEIF; non un aggregatore.

Uso (dalla radice del repo):
    python3 scripts/patch_set_infonodes.py ID tax_id VALORE --source "URL o riferimento" --why "text in English" \\
        [--history-letta --apply]
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_set_infonodes.py"
TODAY = date.today().isoformat()
ALLOWED = {"tax_id"}


def retired(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("field")
    ap.add_argument("value")
    ap.add_argument("--source", required=True, help="fonte primaria (URL o riferimento)")
    ap.add_argument("--why", required=True, help="motivo, in inglese")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    if a.field not in ALLOWED:
        sys.exit("ERRORE: campo non ammesso %r (ammessi: %s)" % (a.field, sorted(ALLOWED)))
    value = a.value.strip()
    if not value or not a.source.strip() or not a.why.strip():
        sys.exit("ERRORE: valore, --source e --why non possono essere vuoti.")
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation).")
    db = json.load(open(a.db, encoding="utf-8"))
    e = next((x for x in db["entities"] if x["id"] == a.entity), None)
    if not e:
        sys.exit("ERRORE: %s non esiste." % a.entity)
    if retired(e):
        sys.exit("ERRORE: %s e una scheda ritirata." % a.entity)
    inf = (e.get("sources") or {}).get("infonodes")
    if not isinstance(inf, dict):
        sys.exit("ERRORE: %s non ha sources.infonodes." % a.entity)
    if inf.get(a.field) is not None:
        sys.exit("ERRORE: %s.%s ha gia un valore (%r): svuotarlo prima con patch_clear_infonodes.py." % (a.entity, a.field, inf[a.field]))
    others = [x["id"] for x in db["entities"] if x["id"] != a.entity and not retired(x)
              and str(((x.get("sources") or {}).get("infonodes") or {}).get(a.field) or "").strip().lower() == value.lower()]
    if others:
        sys.exit("ERRORE: lo stesso %s e gia su schede attive %s: guardare a mano (duplicato o gruppo), non forzare." % (a.field, others))

    print("%s patch_set_infonodes: %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", a.entity, e["name"]))
    print("  sources.infonodes.%s: null -> %r" % (a.field, value))
    print("  fonte: %s" % a.source)
    print("  motivo: %s" % a.why)
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    inf[a.field] = value
    e.setdefault("history", []).append({"date": TODAY, "source": "manual", "author": AUTHOR,
                                        "field": "sources.infonodes." + a.field, "old": None, "new": value,
                                        "description": "%s Source: %s" % (a.why.strip(), a.source.strip())})
    e.setdefault("validation", []).append({"status": "infonodes_field_set", "fields_set": [a.field],
                                           "description": a.why.strip(), "source_ref": a.source.strip(),
                                           "author": AUTHOR, "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


main()
