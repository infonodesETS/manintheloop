#!/usr/bin/env python3
"""
sync_site_data.py — Tiene allineata la copia di edf_calls.json servita dal sito.

Il file sorgente è rawdata/edf_calls.json (dato grezzo, aggiornato con
merge_edf_calls.py). Il sito, servito dalla cartella docs/, ne usa una copia in
docs/data/edf_calls.json. Questo script verifica o rigenera la copia.

Uso (dalla radice del repo o da qualsiasi cartella):
    python3 scripts/sync_site_data.py --check    # esce con 0 se le copie sono identiche, 1 altrimenti
    python3 scripts/sync_site_data.py --write    # copia rawdata/edf_calls.json -> docs/data/edf_calls.json

Senza opzioni equivale a --check. Non modifica nient'altro.
"""
import hashlib
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPPIE = [
    (os.path.join(BASE, "rawdata", "edf_calls.json"),
     os.path.join(BASE, "docs", "data", "edf_calls.json")),
]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    args = set(sys.argv[1:])
    if args - {"--check", "--write"} or {"--check", "--write"} <= args:
        print(__doc__)
        return 2
    scrivi = "--write" in args
    diverse = 0
    for src, dst in COPPIE:
        rel_src, rel_dst = os.path.relpath(src, BASE), os.path.relpath(dst, BASE)
        if not os.path.exists(src):
            print(f"ERRORE: manca la sorgente {rel_src}")
            return 2
        uguali = os.path.exists(dst) and sha(src) == sha(dst)
        if uguali:
            print(f"OK        {rel_dst} è identico a {rel_src}")
            continue
        if scrivi:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"COPIATO   {rel_src} -> {rel_dst}")
        else:
            print(f"DIVERSO   {rel_dst} non coincide con {rel_src} (usa --write)")
            diverse += 1
    return 1 if diverse else 0


if __name__ == "__main__":
    sys.exit(main())
