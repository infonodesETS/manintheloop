#!/usr/bin/env python3
"""
Controllo C7 / F5.3: nei file del repo non ci sono segreti né dati personali
di chi ci lavora.

Cerca, riga per riga, in tutti i file tracciati da git (salvo i *.min.js di
terze parti e i file binari):
  - percorsi personali: /home/<utente>/, /Users/<utente>/, C:\\Users\\
    (non dentro un indirizzo web: https://sito/home/pagina non conta);
  - chiavi private (BEGIN … PRIVATE KEY);
  - token in formati noti: GitHub (ghp_, gho_, github_pat_), Anthropic e
    OpenAI (sk-…), AWS (AKIA…), Exa (EXA_API_KEY=<valore>);
  - assegnazioni del tipo api_key / secret / token / password = "valore",
    con un valore lungo almeno 20 caratteri che mescola lettere e cifre;
  - email di provider personali (gmail, yahoo, hotmail, outlook, icloud,
    libero, proton, live): le email di società e istituzioni nei dati
    pubblici non contano.

Le regole sono strette apposta: il grep generico del piano (C7) dava solo
falsi positivi (indirizzi web con /home/, attributi data-token, script che
leggono la chiave da un file locale). Il controllo non stampa mai il valore
trovato per intero: solo file, riga, tipo e i primi caratteri.

Uso (dalla radice del repo):  python3 scripts/checks/check_secrets_paths.py [cartella]
Senza cartella: i file tracciati da git. Con una cartella: tutti i suoi file
(serve per le prove). Esce con 1 se trova qualcosa.
"""
import os
import re
import subprocess
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REGOLE = [
    # i nomi segnaposto (x, utente, user, nome) servono negli esempi dei documenti
    ("percorso personale", re.compile(
        r"(?<![\w.:/%-])(?:/home/(?!(?:x|utente|user|nome)/)[a-z_][a-z0-9_.-]*/"
        r"|/Users/(?!(?:x|utente|user|nome)/)[A-Za-z][\w.-]*/"
        r"|[A-Za-z]:\\{1,2}Users\\{1,2}(?!(?:x|utente|user|nome)\\)[A-Za-z])")),
    ("chiave privata", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |ENCRYPTED )?PRIVATE KEY-----")),
    ("token GitHub", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})")),
    ("chiave sk-", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}")),
    ("chiave AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("chiave Exa", re.compile(r"\bEXA_API_KEY\s*=\s*[\"']?[A-Za-z0-9-]{16,}")),
    ("segreto assegnato", re.compile(
        r"\b(?:api[_-]?key|secret|token|password|passwd)[\"']?\s*[:=]\s*[\"']"
        r"(?=[A-Za-z0-9_/+-]*[0-9])(?=[A-Za-z0-9_/+-]*[A-Za-z])[A-Za-z0-9_/+][A-Za-z0-9_/+-]{19,}[\"']", re.I)),
    ("email personale", re.compile(
        r"\b[A-Za-z0-9._%+-]+@(?:gmail|googlemail|yahoo|hotmail|outlook|icloud|libero|proton|protonmail|live)\.[a-z.]{2,}\b",
        re.I)),
]


def file_da_controllare(cartella):
    if cartella:
        for base, dirs, files in os.walk(cartella):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in files:
                yield os.path.join(base, f)
        return
    out = subprocess.run(["git", "-C", RADICE, "ls-files", "-z"], capture_output=True, check=True).stdout
    for rel in out.decode("utf-8").split("\0"):
        if rel:
            yield os.path.join(RADICE, rel)


def main():
    cartella = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else None
    base = cartella or RADICE
    letti, trovati = 0, []
    for p in file_da_controllare(cartella):
        if p.endswith(".min.js") or not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                righe = f.readlines()
        except (UnicodeDecodeError, OSError):
            continue                       # binari (immagini, pdf): non si controllano
        letti += 1
        for n, riga in enumerate(righe, 1):
            for nome, rx in REGOLE:
                m = rx.search(riga)
                if m:
                    trovati.append(f"{os.path.relpath(p, base)}:{n}: {nome} ({m.group(0)[:12]}…)")
    print(f"File di testo controllati: {letti}")
    if trovati:
        print(f"TROVATI: {len(trovati)} (segreti o dati personali da togliere prima del merge)")
        for t in trovati:
            print(f"  ✗ {t}")
        sys.exit(1)
    print("CONTROLLO SEGRETI E PERCORSI SUPERATO: nulla da segnalare")


if __name__ == "__main__":
    main()
