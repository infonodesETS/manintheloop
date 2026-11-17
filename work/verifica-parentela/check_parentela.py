#!/usr/bin/env python3
"""
check_parentela.py - controllo automatico dei risultati degli agenti (BOZZA, fuori dal repo, sola lettura).

Per ogni file JSON: struttura, id esistenti e attivi, e per ogni prova riapre la pagina (Exa /contents) e
cerca la frase (normalizzando spazi e maiuscole). Non si fida dell'agente. Non stampa la chiave Exa.

Uso: python3 check_parentela.py file.json [...]
Esito per file: PASS (verdetto confirmed con >=1 prova primary trovata e parent_card_matches yes),
NEEDS_HUMAN (altro), FAIL (struttura o id sbagliati, verdetto confirmed ma nessuna prova trovata).
"""
import json, os, re, sys, urllib.request, urllib.error

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "data", "database.json")
ENV = os.path.expanduser("~/.config/infonodes/exa.env")
KEYS = ["child_id", "parent_id", "verdict", "evidence", "parent_card_matches", "kind", "status"]


def key():
    for l in open(ENV):
        if l.startswith("EXA_API_KEY="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("chiave Exa non trovata")


def norm(s):
    s = (s or "").lower().replace(" ", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def contents(url, k):
    req = urllib.request.Request("https://api.exa.ai/contents", method="POST",
                                 data=json.dumps({"urls": [url], "text": True}).encode(),
                                 headers={"x-api-key": k, "Content-Type": "application/json", "User-Agent": "mitl-check/1.0"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=60))
        return (r.get("results") or [{}])[0].get("text", "") or ""
    except Exception as e:  # noqa
        return ""


def plain(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mitl-check/1.0"})
    try:
        return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    except Exception:
        return ""


def main():
    db = json.load(open(DB, encoding="utf-8"))
    E = {e["id"]: e for e in db["entities"]}
    retired = lambda e: any(h.get("action") == "entity_retired" for h in e.get("history", []))
    k = key()
    for path in sys.argv[1:]:
        print("\n==", os.path.basename(path))
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            print("FAIL: JSON non leggibile:", e); continue
        errs = [f"manca {x}" for x in KEYS if x not in d]
        for x in ("child_id", "parent_id"):
            e = E.get(d.get(x))
            if not e: errs.append(f"{x} {d.get(x)} non esiste")
            elif retired(e): errs.append(f"{x} {d.get(x)} e una scheda ritirata")
        found_primary = 0
        for i, ev in enumerate(d.get("evidence", [])):
            url, ph = ev.get("url", ""), ev.get("phrase", "")
            text = contents(url, k)
            src = "exa"
            if norm(ph) not in norm(text):
                text2 = plain(url)
                if norm(ph) in norm(text2): text, src = text2, "http"
            ok = norm(ph) in norm(text)
            print("  [%d] %-9s %-4s %s | %s" % (i, ev.get("source_kind"), "OK" if ok else "NO", src if ok else "-", url[:90]))
            if ok and ev.get("source_kind") == "primary": found_primary += 1
        v = d.get("verdict")
        if errs:
            esito = "FAIL"
        elif v == "confirmed" and found_primary >= 1 and d.get("parent_card_matches") == "yes":
            esito = "PASS"
        elif v == "confirmed":
            esito = "FAIL"; errs.append("verdetto confirmed ma nessuna prova primary ritrovata o scheda capogruppo non confermata")
        else:
            esito = "NEEDS_HUMAN"
        print("  verdetto agente: %s | kind=%s status=%s fine/inizio=%s | prove primary ritrovate: %d" % (v, d.get("kind"), d.get("status"), d.get("start_or_end_date"), found_primary))
        for m in errs: print("  -", m)
        print("  ESITO:", esito)


if __name__ == "__main__":
    main()
