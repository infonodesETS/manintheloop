#!/usr/bin/env python3
"""
add_validation.py - aggiunge UNA voce a validation[] di UNA entita, senza cambiare nessun altro campo.

Serve per registrare una revisione fatta da una persona (per esempio un field_conflict esaminato):
la voce e append-only e non tocca valori, history, relazioni, altre entita. Dry-run di default.

Stati ammessi (UPDATE_PROTOCOL.md, tabella degli stati): confirmed, bad_crunchbase_match.
Non scrive su schede ritirate (entity_retired).

Uso (dalla radice del repo):
    python3 scripts/add_validation.py ID --status confirmed --why "testo in inglese" [--history-letta --apply]
    opzioni: --author "..."  --db PERCORSO
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

TODAY = date.today().isoformat()
STATI = ("confirmed", "bad_crunchbase_match")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("--status", required=True, choices=STATI)
    ap.add_argument("--why", required=True, help="descrizione della voce (in inglese)")
    ap.add_argument("--author", default="nelsonmau (proposed by Claude, approved %s)" % TODAY)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    a = ap.parse_args()
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation, che il dry-run stampa).")
    db = json.load(open(a.db, encoding="utf-8"))
    e = next((x for x in db["entities"] if x["id"] == a.entity), None)
    if not e:
        sys.exit("ERRORE: %s non esiste." % a.entity)
    if any(h.get("action") == "entity_retired" for h in e.get("history", [])):
        sys.exit("ERRORE: %s e una scheda ritirata." % a.entity)
    print("\n  %s (%s): %d voci di history, %d di validation" % (e["id"], e.get("name"), len(e.get("history", [])), len(e.get("validation", []))))
    for v in e.get("validation", []):
        print("    V %s | %s | %s" % (v.get("datestamp"), v.get("status"), str(v.get("description") or v.get("note") or "")[:150]))
    voce = {"status": a.status, "description": a.why.strip(), "author": a.author, "datestamp": TODAY}
    print("\n%s: nuova voce di validation su %s" % ("APPLICA" if a.apply else "DRY-RUN", a.entity))
    print("  ", json.dumps(voce, ensure_ascii=False))
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    e.setdefault("validation", []).append(voce)
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as f:
        f.write(json.dumps(db, indent=2, ensure_ascii=False))
    print("\nScritto %s." % a.db)


if __name__ == "__main__":
    main()
