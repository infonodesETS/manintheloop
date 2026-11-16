#!/usr/bin/env python3
"""
check_parte_di_branch.py - controllo, in sola lettura, di un branch che aggiunge legami `parte_di`.

Gemello di check_b3_branch.py (che conosce solo le unioni e le pulizie di B3 e segnala come errore
qualunque altra modifica). Confronta docs/data/database.json del working tree con quello di un
riferimento git (default origin/main) e verifica che il branch abbia fatto SOLO quello che fa
scripts/add_parte_di.py:
  1. stesse entita (nessuna aggiunta, nessuna tolta);
  2. tutte le relazioni di prima sono invariate e nello stesso ordine; le nuove sono solo `parte_di`,
     con id REL-NNNN consecutivi dal massimo di prima + 1 (REL-0001 se non ne esistono);
  3. ogni entita cambiata e la FIGLIA di una relazione nuova, e cambia solo `validation`: aggiunte in coda
     (la validation di prima e prefisso), con status `confirmed`, una per ogni relazione nuova di quella figlia;
     history e ogni altro campo identici;
  4. gli estremi delle relazioni nuove non sono schede ritirate;
  5. nessun cambio nei top-level a parte `_updated`.
I cicli e le regole sui campi li controlla scripts/validate.py (da lanciare prima).
Exit 0 se tutto ok, 1 altrimenti. Non scrive nulla.

Uso (dalla radice): python3 -I scripts/check_parte_di_branch.py [--base origin/main]
"""
import argparse, json, re, subprocess, sys
from collections import Counter

DB = "docs/data/database.json"
REL_ID_RE = re.compile(r"^REL-(\d{4,})$")


def git_json(ref, path):
    out = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True, check=True).stdout
    return json.loads(out.decode("utf-8"))


def retired(e):
    return any(h.get("action") == "entity_retired" for h in e.get("history", []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--db", default=DB, help="database da controllare (per le prove su copie)")
    a = ap.parse_args()
    old = git_json(a.base, DB)
    new = json.load(open(a.db, encoding="utf-8"))
    errs = []
    E0 = {e["id"]: e for e in old["entities"]}
    E1 = {e["id"]: e for e in new["entities"]}
    if set(E0) != set(E1) or len(old["entities"]) != len(new["entities"]):
        errs.append("entita aggiunte: %s, rimosse: %s" % (sorted(set(E1) - set(E0)), sorted(set(E0) - set(E1))))

    r0, r1 = old["relationships"], new["relationships"]
    if len(r1) < len(r0) or r1[:len(r0)] != r0:
        errs.append("le relazioni di prima non sono invariate e nello stesso ordine")
    added = r1[len(r0):]
    nums = [int(m.group(1)) for r in r0 if (m := REL_ID_RE.match(str(r.get("id", ""))))]
    nxt = (max(nums) + 1) if nums else 1
    for i, r in enumerate(added):
        if r.get("type") != "parte_di":
            errs.append("relazione nuova non parte_di: %s -> %s (%s)" % (r.get("source"), r.get("target"), r.get("type")))
        want = "REL-%04d" % (nxt + i)
        if r.get("id") != want:
            errs.append("id della relazione nuova %s -> %s: atteso %s, trovato %s" % (r.get("source"), r.get("target"), want, r.get("id")))
        for end in ("source", "target"):
            e = E1.get(r.get(end))
            if e is None:
                errs.append("relazione %s: %s %s non esiste" % (r.get("id"), end, r.get(end)))
            elif retired(e):
                errs.append("relazione %s: %s %s e una scheda ritirata" % (r.get("id"), end, r.get(end)))
    figlie = Counter(r.get("source") for r in added)

    changed = sorted(i for i in E1 if i in E0 and E1[i] != E0[i])
    for i in changed:
        if i not in figlie:
            errs.append("%s e cambiata ma non e la figlia di una relazione nuova" % i)
            continue
        o, n = E0[i], E1[i]
        if {k: v for k, v in o.items() if k != "validation"} != {k: v for k, v in n.items() if k != "validation"}:
            errs.append("%s: cambia qualcosa oltre a validation (history e altri campi devono restare identici)" % i)
        vo, vn = o.get("validation", []), n.get("validation", [])
        if vn[:len(vo)] != vo:
            errs.append("%s: la validation di prima non e prefisso di quella di ora (append-only violato)" % i)
        nuove = vn[len(vo):]
        if len(nuove) != figlie[i] or any(v.get("status") != "confirmed" for v in nuove):
            errs.append("%s: attese %d voci di validation `confirmed` nuove, trovate %d (%s)" % (
                i, figlie[i], len(nuove), sorted({v.get("status") for v in nuove})))
    for i in figlie:
        if i in E0 and i not in changed:
            errs.append("%s e figlia di una relazione nuova ma la sua validation non e cambiata" % i)

    top0 = {k: v for k, v in old.items() if k not in ("entities", "relationships", "_updated")}
    top1 = {k: v for k, v in new.items() if k not in ("entities", "relationships", "_updated")}
    if top0 != top1:
        errs.append("cambiano campi di primo livello oltre a _updated")

    print("Base: %s | entita %d -> %d | relazioni %d -> %d (nuove parte_di: %d) | entita cambiate: %d"
          % (a.base, len(E0), len(E1), len(r0), len(r1), len(added), len(changed)))
    for r in added:
        print("  %s %s -> %s forma=%s current=%s diretta=%s as_of=%s fino_al=%s" % (
            r.get("id"), r.get("source"), r.get("target"), r.get("forma"), r.get("current"), r.get("diretta"), r.get("as_of"), r.get("fino_al")))
    if errs:
        print("\nERRORI (%d):" % len(errs))
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("\nCONTROLLO PARTE_DI SUPERATO")


main()
