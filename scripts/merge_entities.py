#!/usr/bin/env python3
"""
merge_entities.py - unisce un'entita duplicata (perdente) in una canonica (vincitore), senza perdere dati.

Sostituisce dedup_entities.py --merge per i casi di B3 (regole R6 di reference/S3-CLASSI-AZIONI.md).
Differenze rispetto a dedup_entities.py:
  - il perdente NON viene cancellato: diventa una LAPIDE (history 'entity_retired' + validation 'retired',
    con 'canonical' = vincitore), il suo contenuto originale resta intatto;
  - ogni dato del perdente che non puo entrare nel vincitore (blocchi crunchbase/edf/wikidata diversi,
    campi infonodes diversi, relazioni doppie) viene conservato in 'preserved' nella voce di history del vincitore;
  - due relazioni 'uguali' per (source, target, type, classe, role_code) con contenuto diverso FERMANO l'operazione;
  - i blocchi iShares si deduplicano per (ETF, ticker, file) e non solo per ticker;
  - docs/data/edf_orgs.json viene aggiornato (db_id del perdente -> vincitore).

Per default e un DRY-RUN: non scrive nulla. Per applicare serve --apply e --why.

Uso (dalla radice del repo):
    python3 scripts/merge_entities.py WINNER LOSER --why "motivo"            # dry-run
    python3 scripts/merge_entities.py WINNER LOSER --why "motivo" --apply    # scrive
    opzioni: --db PERCORSO  --edf-orgs PERCORSO   (per lavorare su copie)

Dopo --apply: python3 scripts/validate.py [file]
"""
import argparse, copy, json, sys
from datetime import date

AUTHOR = "merge_entities.py"
TODAY = date.today().isoformat()
IGNORE_REL_KEYS = {"history", "created_at", "id"}


def is_retired(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def rel_key(r):
    return (r.get("source"), r.get("target"), r.get("type"), r.get("classe"), r.get("role_code"))


def rel_payload(r):
    return {k: v for k, v in r.items() if k not in IGNORE_REL_KEYS and k not in ("source", "target")}


def ishares_id(x):
    return (x.get("etf_ticker"), x.get("stock_ticker"), x.get("source_file"))


def merge_block(w_src, l_src, key, preserved, absorbed):
    lb = l_src.get(key)
    if not lb:
        return
    wb = w_src.get(key)
    if not wb:
        w_src[key] = copy.deepcopy(lb)
        absorbed.append("sources.%s copiato dal perdente" % key)
    elif wb != lb:
        preserved["sources." + key] = copy.deepcopy(lb)
        absorbed.append("sources.%s: blocco del perdente diverso, conservato in history" % key)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("winner")
    ap.add_argument("loser")
    ap.add_argument("--why", default="")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--rename", default="", help="nuovo nome del vincitore (la correzione e tracciata in history)")
    ap.add_argument("--history-letta", action="store_true",
                    help="conferma che la history di entrambe le entita e stata letta (obbligatoria con --apply)")
    ap.add_argument("--db", default="docs/data/database.json")
    ap.add_argument("--edf-orgs", default="docs/data/edf_orgs.json")
    a = ap.parse_args()

    if a.apply and not a.why.strip():
        sys.exit("ERRORE: con --apply serve --why con il motivo dell'unione (richiesto da UPDATE_PROTOCOL).")
    if a.apply and not a.history_letta:
        sys.exit("ERRORE: con --apply serve --history-letta: leggere prima la history di entrambe le entita (dry-run la stampa).")
    if a.winner == a.loser:
        sys.exit("ERRORE: vincitore e perdente coincidono.")

    db = json.load(open(a.db, encoding="utf-8"))
    ents = {e["id"]: e for e in db["entities"]}
    for i in (a.winner, a.loser):
        if i not in ents:
            sys.exit("ERRORE: %s non esiste." % i)
        if is_retired(ents[i]):
            sys.exit("ERRORE: %s e gia una lapide (entity_retired): nulla da fare." % i)
    w, l = ents[a.winner], ents[a.loser]

    wq, lq = w.get("wikidata_id"), l.get("wikidata_id")
    if wq and lq and wq != lq:
        sys.exit("ERRORE: wikidata_id diversi (%s contro %s): non sono lo stesso soggetto." % (wq, lq))

    absorbed, preserved, kept_rels = [], {}, []
    if not wq and lq:
        w["wikidata_id"] = lq
        absorbed.append("wikidata_id %s adottato dal perdente (il vincitore non ne aveva)" % lq)

    # --- sources ---
    w_src = w.setdefault("sources", {})
    l_src = l.get("sources") or {}
    new_is = [x for x in (l_src.get("ishares") or []) if ishares_id(x) not in {ishares_id(y) for y in (w_src.get("ishares") or [])}]
    if new_is:
        w_src["ishares"] = (w_src.get("ishares") or []) + copy.deepcopy(new_is)
        absorbed.append("sources.ishares: +%d voci (%s)" % (len(new_is), ", ".join("%s/%s" % (x.get("etf_ticker"), x.get("stock_ticker")) for x in new_is)))
    for key in l_src:
        if key in ("ishares", "infonodes"):
            continue
        wb, lb = w_src.get(key), l_src.get(key)
        # blocco EDF dello stesso PIC: e lo stesso dato aggiornato in momenti diversi, vince il piu recente
        if key == "edf" and wb and lb and wb != lb and wb.get("pic") == lb.get("pic") \
                and (lb.get("extracted_at") or "") > (wb.get("extracted_at") or ""):
            preserved["sources.edf (versione precedente del vincitore)"] = copy.deepcopy(wb)
            w_src["edf"] = copy.deepcopy(lb)
            absorbed.append("sources.edf: tenuto il blocco piu recente del perdente (%s contro %s), il precedente conservato in history"
                            % (lb.get("extracted_at"), wb.get("extracted_at")))
            continue
        if key == "crunchbase" and wb and lb and wb.get("profile_url") != lb.get("profile_url"):
            absorbed.append("ATTENZIONE crunchbase: profili diversi (%s contro %s): tenuto quello del vincitore, l'altro conservato in history; DA DECIDERE a mano"
                            % (wb.get("profile_url"), lb.get("profile_url")))
        merge_block(w_src, l_src, key, preserved, absorbed)
    if l_src.get("infonodes"):
        wi = w_src.setdefault("infonodes", {})
        diff = {}
        for k, v in l_src["infonodes"].items():
            if v is None:
                continue
            if wi.get(k) is None:
                wi[k] = copy.deepcopy(v)
                absorbed.append("sources.infonodes.%s copiato dal perdente" % k)
            elif wi[k] != v:
                diff[k] = v
        if diff:
            preserved["sources.infonodes"] = diff
            absorbed.append("sources.infonodes: %d campi diversi conservati in history (%s)" % (len(diff), ", ".join(diff)))

    rename_entry = None
    if a.rename.strip() and a.rename.strip() != w.get("name"):
        rename_entry = {"date": TODAY, "action": "field_corrected", "field": "name", "old_value": w.get("name"),
                        "new_value": a.rename.strip(), "author": AUTHOR,
                        "note": "Nome aggiornato in occasione dell'unione con %s (%s)." % (a.loser, l.get("name"))}
        absorbed.append("nome del vincitore: '%s' -> '%s'" % (w.get("name"), a.rename.strip()))

    # --- roles ---
    roles = sorted(set(w.get("roles") or []) | set(l.get("roles") or []))
    if roles != sorted(w.get("roles") or []):
        w["roles"] = roles
        absorbed.append("roles -> %s" % roles)

    # --- relazioni ---
    rels = db["relationships"]
    w_rels = {}
    for r in rels:
        if a.winner in (r["source"], r["target"]):
            w_rels.setdefault(rel_key(r), []).append(r)
    redirected, dropped, conflicts = [], [], []
    for r in rels:
        if a.loser not in (r["source"], r["target"]):
            continue
        new = dict(r)
        if new["source"] == a.loser:
            new["source"] = a.winner
        if new["target"] == a.loser:
            new["target"] = a.winner
        if new["source"] == new["target"]:
            conflicts.append("relazione %s -> %s diventerebbe un anello su se stessa" % (r["source"], r["target"]))
            continue
        twins = w_rels.get(rel_key(new), [])
        if twins:
            if any(rel_payload(t) == rel_payload(new) for t in twins):
                dropped.append(r)
            else:
                conflicts.append("relazione doppia %s -> %s (%s) con contenuto diverso: %s contro %s" % (
                    new["source"], new["target"], new["type"], rel_payload(twins[0]), rel_payload(new)))
        else:
            redirected.append(r)
    if conflicts:
        print("OPERAZIONE FERMATA, conflitti da risolvere a mano:")
        for c in conflicts:
            print("  -", c)
        sys.exit(2)
    if dropped:
        preserved["relationships_dropped"] = copy.deepcopy(dropped)
        absorbed.append("relazioni: %d identiche a quelle del vincitore, tolte e conservate in history" % len(dropped))
    if redirected:
        absorbed.append("relazioni: %d spostate sul vincitore" % len(redirected))

    # --- history e validation del vincitore ---
    why = a.why.strip() or "(motivo non indicato: dry-run)"
    w_hist_add = [dict(h, from_entity=a.loser) for h in (l.get("history") or [])]
    w_statuses = {v.get("status") for v in (w.get("validation") or [])}
    w_val_add = [dict(v, from_entity=a.loser) for v in (l.get("validation") or []) if v.get("status") not in w_statuses]
    decision = {
        "date": TODAY, "action": "dedup_decision", "author": AUTHOR, "field": "entity",
        "old": None, "new": "merged from %s" % a.loser,
        "note": "Unita %s (%s) in questa entita. Motivo: %s" % (a.loser, l.get("name"), why),
        "absorbed": absorbed, "loser_name": l.get("name"),
    }
    if preserved:
        decision["preserved"] = preserved

    # --- edf_orgs ---
    eo, eo_hits = None, []
    try:
        eo = json.load(open(a.edf_orgs, encoding="utf-8"))
        eo_hits = [pic for pic, o in eo["orgs"].items() if o.get("db_id") == a.loser]
    except FileNotFoundError:
        pass

    # --- lettura della history (passo obbligatorio del processo, richiesta di Nelson 2026-11-12) ---
    SEGNALI = {"qid_removed", "cb_wrong_entity", "accepted_duplicate", "share_class_variant", "retired",
               "qid_nulled_duplicate", "duplicate_wikidata_id", "field_conflict", "merged_from"}
    for ent in (w, l):
        print("\n  HISTORY di %s (%s): %d voci di history, %d di validation" % (ent["id"], ent.get("name"), len(ent.get("history", [])), len(ent.get("validation", []))))
        for h in ent.get("history", []):
            print("    H %s | %s | %s | %s" % (h.get("date") or h.get("datestamp"), h.get("author") or h.get("script"),
                                                 h.get("field") or h.get("action"), str(h.get("description") or h.get("note") or "")[:150]))
        for v in ent.get("validation", []):
            flag = "  <-- SEGNALE" if v.get("status") in SEGNALI else ""
            print("    V %s | %s | %s%s" % (v.get("datestamp"), v.get("status"), str(v.get("description") or v.get("note") or "")[:120], flag))
    print()

    # --- rapporto ---
    print("%s %s: %s (%s)  <-  %s (%s)" % ("APPLICA" if a.apply else "DRY-RUN", "unione", a.winner, w.get("name"), a.loser, l.get("name")))
    print("  motivo: %s" % why)
    for x in absorbed or ["nulla da assorbire"]:
        print("  -", x)
    print("  history del perdente copiate sul vincitore: %d | validation: %d" % (len(w_hist_add), len(w_val_add)))
    print("  edf_orgs.json: %d PIC da riassegnare %s" % (len(eo_hits), eo_hits))
    print("  il perdente resta nel database come LAPIDE (canonical = %s)" % a.winner)
    if not a.apply:
        print("\nDRY-RUN: nessuna modifica scritta.")
        return

    # --- applicazione ---
    for r in dropped:
        rels.remove(r)
    for r in redirected:
        if r["source"] == a.loser:
            r["source"] = a.winner
        if r["target"] == a.loser:
            r["target"] = a.winner
        r.setdefault("history", []).append({"date": TODAY, "author": AUTHOR,
                                            "description": "Entity reference redirected: %s -> %s (merge)" % (a.loser, a.winner)})
    w.setdefault("history", []).extend(w_hist_add)
    if rename_entry:
        w["name"] = rename_entry["new_value"]
        w["history"].append(rename_entry)
    w["history"].append(decision)
    w.setdefault("validation", []).extend(w_val_add)
    w["validation"].append({"status": "merged_from", "description": "Entita %s (%s) unita in questa il %s e lasciata come lapide." % (a.loser, l.get("name"), TODAY),
                            "author": AUTHOR, "datestamp": TODAY})
    note = "Duplicato di %s (%s). Unita il %s: relazioni e dati spostati sul vincitore, contenuto originale conservato qui. Motivo: %s" % (a.winner, w.get("name"), TODAY, why)
    l.setdefault("history", []).append({"action": "entity_retired", "note": note, "canonical": a.winner, "author": AUTHOR, "datestamp": TODAY})
    l.setdefault("validation", []).append({"status": "retired", "description": note, "canonical": a.winner, "author": AUTHOR, "datestamp": TODAY})
    db["_updated"] = TODAY
    with open(a.db, "w", encoding="utf-8") as f:
        f.write(json.dumps(db, indent=2, ensure_ascii=False))
    if eo and eo_hits:
        for pic in eo_hits:
            eo["orgs"][pic]["db_id"] = a.winner
        with open(a.edf_orgs, "w", encoding="utf-8") as f:
            f.write(json.dumps(eo, indent=2, ensure_ascii=False))
    left = [r for r in db["relationships"] if a.loser in (r["source"], r["target"])]
    print("\nScritto %s. Relazioni ancora legate al perdente: %d." % (a.db, len(left)))
    print("Ora: python3 scripts/validate.py %s" % (a.db if a.db != "docs/data/database.json" else ""))


main()
