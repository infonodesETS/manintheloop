#!/usr/bin/env python3
"""
check_docs.py - controllo in sola lettura: i documenti di progetto sono in pari con le PR fuse?

Confronta le PR fuse in main (git log --merges --first-parent, "Merge pull request #N") con i
numeri di PR citati in:
  - reference/PIANO-RIORGANIZZAZIONE.md  (registro e tabella di avanzamento)
  - reference/LOG-RIORGANIZZAZIONE.md    (diario)
  - STATUS.md                            (solo informativo: per regola cita poche PR; si stampa
                                           solo l'ultima citata e quante ne mancano)
e segnala le PR fuse mai citate (l'arretrato). Non scrive nulla, non usa la rete.

Limite noto: la PR che contiene l'aggiornamento dei documenti non puo citare il proprio numero
(non esiste ancora): dopo il merge risultera l'ultima PR non citata; si cita nella PR successiva.

Uso (dalla radice del repo):
    python3 scripts/check_docs.py [--base origin/main]
Exit code: 0 piano e log in pari; 1 arretrato nel piano o nel log (STATUS.md e solo avviso).
Da lanciare a inizio e a fine sessione (piano, par. 0.5).
"""
import argparse, re, subprocess, sys

FILES = {
    "piano": "reference/PIANO-RIORGANIZZAZIONE.md",
    "log": "reference/LOG-RIORGANIZZAZIONE.md",
    "STATUS": "STATUS.md",
}


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"errore git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def merged_prs(base):
    out = git("log", "--merges", "--first-parent", "--format=%h %ad %s", "--date=short", base)
    prs = {}
    for line in out.splitlines():
        m = re.match(r"(\w+) (\S+) Merge pull request #(\d+) from (\S+)", line)
        if m:
            prs[int(m.group(3))] = (m.group(1), m.group(2), m.group(4))
    return prs


def cited(path):
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        sys.exit(f"file mancante: {path}")
    nums = {int(n) for n in re.findall(r"#(\d{2,4})\b", text)}
    # intervalli come "#48-#51" o "#43-46": tutte le PR comprese sono citate
    for a, b in re.findall(r"#(\d{2,4})\s*[-\u2013]\s*#?(\d{2,4})\b", text):
        if 0 < int(b) - int(a) < 40:
            nums.update(range(int(a), int(b) + 1))
    return nums


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    base = ap.parse_args().base

    prs = merged_prs(base)
    if not prs:
        sys.exit("nessuna PR fusa trovata")
    last = max(prs)
    print(f"Base {base}: {len(prs)} PR fuse, ultima #{last} ({prs[last][0]}, {prs[last][1]})")

    # PR di cui i documenti parlano: si guardano solo quelle dopo la #27 (prima del piano)
    relevant = {n for n in prs if n >= 28}
    fail = False
    for key, path in FILES.items():
        c = cited(path)
        missing = sorted(relevant - c)
        top = max((n for n in c if n in prs), default=None)
        print(f"\n{key} ({path}): ultima PR citata #{top}; PR fuse non citate: {len(missing)}")
        for n in (missing if key != "STATUS" else []):
            h, d, br = prs[n]
            print(f"  #{n}  {h}  {d}  {br}")
        if missing and key != "STATUS":
            fail = True

    st = git("status", "--short").strip()
    if st:
        print("\nAvviso: working tree non pulito:\n" + st)
    ahead = git("log", "--oneline", f"{base}..HEAD").strip()
    if ahead:
        print(f"\nAvviso: commit locali non in {base}:\n{ahead}")

    print("\nESITO:", "ARRETRATO nei documenti" if fail else "piano e log in pari")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
