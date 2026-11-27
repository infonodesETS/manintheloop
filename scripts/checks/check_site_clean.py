#!/usr/bin/env python3
"""
Controllo F5.2: in docs/ ci sono solo i file del sito.

GitHub Pages pubblica tutto ciò che sta in docs/: un file di lavoro finito lì
per sbaglio (note, CSV, copie del database, file nascosti) andrebbe online.
Questo controllo elenca i file di docs/ che non sono nell'elenco ammesso:

  - in docs/:          CNAME e le pagine del sito (PAGINE);
  - in docs/data/:     solo i JSON di DATI;
  - in docs/web/:      solo file .js e .css;
  - in docs/reports/:  solo file .html.

Ogni altra cartella o file è un errore. Per pubblicare un file nuovo si
aggiunge qui, nella stessa PR: è una scelta da fare apposta.

Uso (dalla radice del repo):  python3 scripts/checks/check_site_clean.py [cartella]
Esce con 1 se trova file non ammessi, e li elenca.
"""
import os
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAGINE = {"CNAME", "index.html", "search.html", "networks.html", "key-figures.html",
          "publications.html", "about.html"}
DATI = {"database.json", "edf_orgs.json", "edf_calls.json", "mitl-index.json", "glossary.json",
        "glossary_terms.json", "about_why.json", "publications.json", "last_update.json",
        "defence_criteria.json"}
ESTENSIONI = {"web": (".js", ".css"), "reports": (".html",)}


def ammesso(rel):
    parti = rel.split("/")
    if any(p.startswith(".") for p in parti):
        return False                      # file e cartelle nascosti (.DS_Store, .git…)
    if len(parti) == 1:
        return parti[0] in PAGINE
    cima = parti[0]
    if cima == "data":
        return len(parti) == 2 and parti[1] in DATI
    if cima in ESTENSIONI:
        return parti[-1].endswith(ESTENSIONI[cima])
    return False


def main():
    sito = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(RADICE, "docs")
    tutti, fuori = 0, []
    for cartella, _, file in os.walk(sito):
        for f in file:
            rel = os.path.relpath(os.path.join(cartella, f), sito).replace(os.sep, "/")
            tutti += 1
            if not ammesso(rel):
                fuori.append(rel)
    print(f"File in {os.path.relpath(sito, RADICE)}/: {tutti}")
    if fuori:
        print(f"FILE NON AMMESSI: {len(fuori)} (andrebbero online con GitHub Pages)")
        for r in sorted(fuori):
            print(f"  ✗ {r}")
        sys.exit(1)
    print("CONTROLLO CARTELLA DEL SITO SUPERATO: solo file del sito")


if __name__ == "__main__":
    main()
