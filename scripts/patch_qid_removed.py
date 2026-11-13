#!/usr/bin/env python3
"""
patch_qid_removed.py - toglie a un'entita un wikidata_id che appartiene a un'altra entita
(casa madre, filiale sorella, QID propagato per errore). Procedura `qid_removed` di
reference/UPDATE_PROTOCOL.md (tabella "Subsidiary or division with parent's QID" e sezione
"For qid_removed actions").

Cosa fa (solo sull'entita indicata):
  - wikidata_id -> null;
  - history (append-only): voce con field "wikidata_id", old = QID tolto, new = null, e nella
    descrizione: QID e sua etichetta Wikidata, perche l'entita lo aveva, cosa e davvero l'entita,
    se potrebbe esistere un QID corretto;
  - validation: voce `qid_removed` con wikidata_id_removed.
Con --clear-wikidata-block sposta anche il blocco sources.wikidata (dati della casa madre) nella voce
di history (campo "old"), cosi non si perde nulla, e lo mette a null. Senza l'opzione il blocco resta
com'e (come nei 51 casi di QID annullato del 2026-04-23).

Mette anche l'entita nel file dei candidati QID (work/qid_candidates.json) con status "rejected" e il QID
tolto, cosi search_missing_qids.py non lo ripropone e --apply non lo riapplica (rischio visto il 2026-06-18
su IN-0366). Se l'entita e gia nel file, la voce diventa "rejected" con il motivo (nulla viene cancellato:
lo stato precedente e riportato nel campo reason).

Dry-run di default. Per scrivere servono --apply e --history-letta.
Non tocca altre entita, relazioni, edf_orgs.json.

Uso (dalla radice del repo):
    python3 scripts/patch_qid_removed.py ID QID --label "etichetta Wikidata" --is "cosa e davvero" \\
        --why "perche aveva il QID" [--new-qid-note "..."] [--clear-wikidata-block]
    aggiungere --history-letta --apply per scrivere
Dopo: python3 scripts/validate.py
"""
import argparse, json, sys
from datetime import date

AUTHOR = "patch_qid_removed.py"
TODAY = date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entity")
    ap.add_argument("qid")
    ap.add_argument("--label", required=True, help="etichetta Wikidata del QID tolto")
    ap.add_argument("--is", dest="what", required=True, help="cosa e davvero l'entita (es. controllata, filiale)")
    ap.add_argument("--why", required=True, help="perche l'entita aveva quel QID")
    ap.add_argument("--new-qid-note", default="Un QID corretto potrebbe non esistere: da cercare con la pipeline QID.",
                    help="se puo esistere un QID corretto")
    ap.add_argument("--clear-wikidata-block", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--history-letta", action="store_true")
    ap.add_argument("--db", default="docs/data/database.json")
    ap.add_argument("--candidates", default="work/qid_candidates.json")
    a = ap.parse_args()

    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta (leggere prima history e validation).")
    db = json.load(open(a.db, encoding="utf-8"))
    ents = {e["id"]: e for e in db["entities"]}
    if a.entity not in ents:
        sys.exit("ERRORE: %s non esiste." % a.entity)
    e = ents[a.entity]
    if any(h.get("action") == "entity_retired" for h in e.get("history", [])):
        sys.exit("ERRORE: %s e una lapide." % a.entity)
    if e.get("wikidata_id") != a.qid:
        sys.exit("ERRORE: %s ha wikidata_id %r, non %s." % (a.entity, e.get("wikidata_id"), a.qid))
    others = [(x["id"], x["name"]) for x in db["entities"] if x.get("wikidata_id") == a.qid and x["id"] != a.entity]

    old_block = (e.get("sources") or {}).get("wikidata")
    desc = ("QID %s tolto: nella Wikidata e '%s'. Perche lo aveva: %s. L'entita e: %s. %s"
            % (a.qid, a.label, a.why, a.what, a.new_qid_note))
    h = {"date": TODAY, "source": "manual", "author": AUTHOR, "field": "wikidata_id",
         "old": a.qid, "new": None, "description": desc}
    if a.clear_wikidata_block and old_block:
        h["old_sources_wikidata"] = old_block
    v = {"status": "qid_removed", "wikidata_id_removed": a.qid, "wikidata_label": a.label,
         "description": desc, "author": AUTHOR, "datestamp": TODAY}

    print("%s %s: %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", "qid_removed", a.entity, e["name"]))
    print("  wikidata_id: %s -> null" % a.qid)
    print("  altre entita con lo stesso QID (restano): %s" % (others or "nessuna"))
    print("  sources.wikidata: %s" % ("spostato nella history e messo a null" if (a.clear_wikidata_block and old_block)
                                      else "lasciato com'e (%s)" % (("label " + old_block.get("label", "?")) if old_block else "assente")))
    cands = json.load(open(a.candidates, encoding="utf-8"))
    prev = next((c for c in cands["candidates"] if c["entity_id"] == a.entity), None)
    why_rej = "QID %s tolto con qid_removed il %s (%s): non riproporre ne applicare." % (a.qid, TODAY, a.what)
    if prev:
        why_rej += " Stato precedente: %s (%s, qid %s)." % (prev.get("status"), prev.get("reason"), prev.get("qid"))
    print("  %s: %s come rejected" % (a.candidates, "voce esistente aggiornata" if prev else "voce nuova"))
    print("  history: +1 voce (field wikidata_id) | validation: +1 voce (qid_removed)")
    print("  testo della voce: %s" % desc)
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return
    e["wikidata_id"] = None
    if a.clear_wikidata_block and old_block:
        e["sources"]["wikidata"] = None
    e.setdefault("history", []).append(h)
    e.setdefault("validation", []).append(v)
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as f:
        f.write(json.dumps(db, indent=2, ensure_ascii=False))
    entry = {"entity_id": a.entity, "entity_name": e["name"], "search_name": e["name"], "status": "rejected",
             "reason": why_rej, "qid": a.qid, "label": a.label, "description": None}
    if prev:
        prev.update({"status": "rejected", "reason": why_rej})
    else:
        cands["candidates"].append(entry)
        cands["_total"] = len(cands["candidates"])
    with open(a.candidates, "w", encoding="utf-8") as f:
        json.dump(cands, f, ensure_ascii=False, indent=2)
    print("\nScritto %s. Ora: python3 scripts/validate.py" % a.db)


main()
