#!/usr/bin/env python3
"""
check_b3_branch.py - controllo UNICO, in sola lettura, delle unioni/pulizie di B3 su un branch.

Confronta docs/data/database.json del working tree con quello di un riferimento git (default origin/main)
e verifica che il branch abbia fatto SOLO quello che deve:
  1. nessuna entita aggiunta o rimossa (le lapidi restano nel database);
  2. ogni entita cambiata e o una lapide nuova, o un suo canonico, o una con qid_removed;
  3. per ogni entita cambiata, la history e la validation di prima sono un PREFISSO di quelle di ora (append-only);
  4. ogni lapide nuova: contenuto originale (nome, wikidata_id, sources) invariato; canonical esistente, attivo e non lapide;
  5. nessuna relazione punta a una lapide;
  6. relazioni tolte: ognuna ha una equivalente rimasta (stessi source/target/type dopo il reindirizzamento);
  7. nessun wikidata_id condiviso tra entita ATTIVE che non fosse gia condiviso prima;
  8. edf_orgs.json: nessun db_id punta a una lapide;
  9. conteggi: entita totali uguali, attive calano del numero di lapidi nuove, relazioni calano del numero di tolte.
Exit 0 se tutto ok, 1 altrimenti. Non scrive nulla.

Uso (dalla radice): python3 -I scripts/check_b3_branch.py [--base origin/main]
"""
import argparse, json, subprocess, sys
from collections import defaultdict

DB = "docs/data/database.json"
EO = "docs/data/edf_orgs.json"


def git_json(ref, path):
    out = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True, check=True).stdout
    return json.loads(out.decode("utf-8"))


def retired(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def canonical(e):
    for h in e.get("history", []):
        if h.get("action") == "entity_retired":
            return h.get("canonical")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--db", default=DB, help="database da controllare (per le prove su copie)")
    ap.add_argument("--edf-orgs", default=EO)
    a = ap.parse_args()
    old = git_json(a.base, DB)
    new = json.load(open(a.db, encoding="utf-8"))
    errs, notes = [], []
    E0 = {e["id"]: e for e in old["entities"]}
    E1 = {e["id"]: e for e in new["entities"]}

    if set(E0) != set(E1):
        errs.append("entita aggiunte: %s, rimosse: %s" % (sorted(set(E1) - set(E0)), sorted(set(E0) - set(E1))))
    new_ret = sorted(i for i in E1 if i in E0 and retired(E1[i]) and not retired(E0[i]))
    winners = sorted({canonical(E1[i]) for i in new_ret})
    qid_rem = sorted(i for i in E1 if i in E0 and any(v.get("status") == "qid_removed" for v in E1[i].get("validation", []))
                     and not any(v.get("status") == "qid_removed" for v in E0[i].get("validation", [])))
    expected = set(new_ret) | set(winners) | set(qid_rem)
    changed = sorted(i for i in E1 if i in E0 and E1[i] != E0[i])
    for i in changed:
        if i not in expected:
            errs.append("%s e cambiata ma non e lapide, canonico o qid_removed" % i)
    for i in expected:
        if i in E1 and i not in changed:
            errs.append("%s e attesa cambiata ma e identica a prima" % i)

    for i in changed:
        for k in ("history", "validation"):
            o, n = E0[i].get(k, []), E1[i].get(k, [])
            if n[:len(o)] != o:
                errs.append("%s: %s di prima non e prefisso di quella di ora (append-only violato)" % (i, k))

    for i in new_ret:
        o, n = E0[i], E1[i]
        for k in ("name", "wikidata_id", "sources", "type", "roles"):
            if o.get(k) != n.get(k):
                errs.append("lapide %s: campo %s modificato" % (i, k))
        c = canonical(n)
        if c not in E1:
            errs.append("lapide %s: canonical %s non esiste" % (i, c))
        elif retired(E1[c]):
            errs.append("lapide %s: canonical %s e a sua volta una lapide" % (i, c))
        elif c == i:
            errs.append("lapide %s punta a se stessa" % i)

    R = lambda r: (r["source"], r["target"], r["type"], r.get("classe"), r.get("role_code"))
    ret_all = {i for i, e in E1.items() if retired(e)}
    for r in new["relationships"]:
        for end in (r["source"], r["target"]):
            if end in ret_all:
                errs.append("relazione %s -> %s punta alla lapide %s" % (r["source"], r["target"], end))
    redirect = {i: canonical(E1[i]) for i in new_ret}
    mp = lambda x: redirect.get(x, x)
    keys_new = defaultdict(int)
    for r in new["relationships"]:
        keys_new[R(r)] += 1
    keys_old = defaultdict(int)
    for r in old["relationships"]:
        k = R(r)
        keys_old[(mp(k[0]), mp(k[1])) + k[2:]] += 1
    removed = 0
    for k, n0 in keys_old.items():
        n1 = keys_new.get(k, 0)
        if n1 == 0:
            errs.append("relazione sparita senza equivalente: %s" % (k,))
        if n1 < n0:
            removed += n0 - n1
    for k, n1 in keys_new.items():
        if keys_old.get(k, 0) == 0:
            errs.append("relazione nuova non prevista: %s" % (k,))
    if len(old["relationships"]) - len(new["relationships"]) != removed:
        errs.append("conteggio relazioni non torna: tolte %d, calo %d" % (removed, len(old["relationships"]) - len(new["relationships"])))

    def shared(E):
        g = defaultdict(list)
        for i, e in E.items():
            if e.get("wikidata_id") and not retired(e):
                g[e["wikidata_id"]].append(i)
        return {q: sorted(v) for q, v in g.items() if len(v) > 1}
    s0, s1 = shared(E0), shared(E1)
    for q, v in s1.items():
        if s0.get(q) != v and not (set(v) < set(s0.get(q, v))):
            errs.append("QID %s condiviso tra attive %s (non lo era prima)" % (q, v))
    notes.append("QID ancora condivisi tra entita attive: %d (prima: %d)" % (len(s1), len(s0)))

    eo = json.load(open(a.edf_orgs, encoding="utf-8"))
    for pic, o in eo["orgs"].items():
        if o.get("db_id") in ret_all:
            errs.append("edf_orgs PIC %s punta alla lapide %s" % (pic, o["db_id"]))

    act0 = sum(1 for e in E0.values() if not retired(e))
    act1 = sum(1 for e in E1.values() if not retired(e))
    if act0 - act1 != len(new_ret):
        errs.append("attive: %d -> %d, lapidi nuove %d" % (act0, act1, len(new_ret)))

    print("Base: %s | entita %d -> %d | attive %d -> %d | relazioni %d -> %d"
          % (a.base, len(E0), len(E1), act0, act1, len(old["relationships"]), len(new["relationships"])))
    print("Lapidi nuove (%d): %s" % (len(new_ret), ", ".join("%s->%s" % (i, redirect[i]) for i in new_ret)))
    print("Canonici (%d): %s | qid_removed (%d): %s" % (len(winners), ", ".join(winners), len(qid_rem), ", ".join(qid_rem)))
    print("Entita cambiate: %d (attese %d)" % (len(changed), len(expected)))
    for n in notes:
        print("Nota:", n)
    if errs:
        print("\nERRORI (%d):" % len(errs))
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("\nCONTROLLO B3 SUPERATO")


main()
