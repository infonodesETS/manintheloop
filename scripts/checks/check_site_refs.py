#!/usr/bin/env python3
"""
Controllo C4 / F5.1: ogni file locale richiamato dal sito esiste in docs/.

Legge le pagine (docs/**/*.html) e i moduli JavaScript (docs/web/*.js, salvo i
*.min.js di terze parti) e ne estrae i riferimenti locali:
  - nelle pagine: src="…", href="…" e fetch('…') negli script dentro la pagina;
  - nei moduli: fetch('…') e import … from './…'.
Salta gli indirizzi esterni (http, https, //, mailto:, tel:, javascript:, data:),
le ancore (#…) e i riferimenti costruiti a runtime (con `${`), perché non si
possono risolvere leggendo il file.

Come si risolve un riferimento:
  - src, href e fetch in una pagina: rispetto alla cartella della pagina;
  - fetch in un modulo: rispetto a docs/, perché il browser lo risolve rispetto
    alla pagina che carica il modulo, e tutte le pagine che caricano moduli con
    fetch stanno in docs/ (verificato il 2026-11-27);
  - import in un modulo: rispetto alla cartella del modulo.
Querystring e frammento si tolgono; un riferimento a una cartella vuol dire la
sua index.html.

Uso (dalla radice del repo):  python3 scripts/checks/check_site_refs.py [cartella]
Esce con 1 se manca anche un solo file, e li elenca.
"""
import os
import re
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ATTR = re.compile(r"""\b(?:src|href)\s*=\s*(["'])(.*?)\1""", re.I | re.S)
FETCH = re.compile(r"""\bfetch\(\s*(["'])(.*?)\1""")
IMPORT = re.compile(r"""\bimport\b[^'"`;]*?(?:\bfrom\s*)?(["'])(\.{1,2}/[^"']+)\1""")
ESTERNO = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.I)


def locale(rif):
    """Il percorso da controllare, oppure None se il riferimento va saltato."""
    rif = rif.strip()
    if not rif or rif.startswith("#") or "${" in rif or ESTERNO.match(rif):
        return None
    return re.split(r"[?#]", rif, maxsplit=1)[0]


def esiste(base, percorso, sito):
    pieno = os.path.normpath(os.path.join(base, percorso))
    if not pieno.startswith(sito + os.sep) and pieno != sito:
        return False, "fuori da docs/"
    if os.path.isdir(pieno):
        pieno = os.path.join(pieno, "index.html")
    return os.path.isfile(pieno), None


def main():
    sito = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(RADICE, "docs")
    pagine, moduli = [], []
    for cartella, _, file in os.walk(sito):
        for f in file:
            p = os.path.join(cartella, f)
            if f.endswith(".html"):
                pagine.append(p)
            elif f.endswith(".js") and not f.endswith(".min.js"):
                moduli.append(p)

    controllati, mancanti = 0, []

    def controlla(origine, base, rif):
        nonlocal controllati
        percorso = locale(rif)
        if percorso is None:
            return
        if percorso == "":
            percorso = "."
        controllati += 1
        ok, motivo = esiste(base, percorso, sito)
        if not ok:
            mancanti.append(f"{os.path.relpath(origine, sito)}: {rif}" + (f" ({motivo})" if motivo else ""))

    for p in sorted(pagine):
        testo = open(p, encoding="utf-8").read()
        for rx in (ATTR, FETCH):
            for m in rx.finditer(testo):
                controlla(p, os.path.dirname(p), m.group(2))
    for p in sorted(moduli):
        testo = open(p, encoding="utf-8").read()
        for m in FETCH.finditer(testo):
            controlla(p, sito, m.group(2))
        for m in IMPORT.finditer(testo):
            controlla(p, os.path.dirname(p), m.group(2))

    print(f"Riferimenti locali controllati: {controllati} ({len(pagine)} pagine, {len(moduli)} moduli JavaScript)")
    if mancanti:
        print(f"MANCANTI: {len(mancanti)}")
        for m in mancanti:
            print(f"  ✗ {m}")
        sys.exit(1)
    print("CONTROLLO RIFERIMENTI SUPERATO: nessun file mancante")


if __name__ == "__main__":
    main()
