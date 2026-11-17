#!/usr/bin/env python3
"""
check_b5.py - controlla il risultato di un agente di ricerca per B5 (ruoli A e B), bozza provvisoria.

Verifica, senza fidarsi dell'agente:
  1. formato: stesso lotto dell'input, un caso per ogni caso dell'input, nessun caso in piu;
  2. le schede citate esistono nel database, sono attive e hanno il nome dichiarato;
  3. ogni frase di prova si trova davvero nella pagina citata (Exa /contents, chiave in
     ~/.config/infonodes/exa.env, mai stampata);
  4. il verdetto e coerente con le prove (una prova che nomina l'emittente SEC E la scheda).

Non scrive nel database ne altrove. Uso, dalla radice del repo:
    python3 -I work/b5-release1/agenti/check_b5.py work/b5-release1/agenti/risultati/A1.json [...]
Il file di input e work/b5-release1/agenti/input/<lotto>.json (stesso nome).
Esito per file: PASS, NEEDS_HUMAN o FAIL. Uscita: 0 tutti PASS, 1 almeno un NEEDS_HUMAN senza FAIL, 2 almeno un FAIL.
"""
import json, os, pathlib, re, sys, urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[3]
DB = RAIZ / "docs/data/database.json"
INPUT = RAIZ / "work/b5-release1/agenti/input"
ENV = os.path.expanduser("~/.config/infonodes/exa.env")
KINDS = {"primary", "secondary"}
VERDETTI = {"A": {"same_entity", "no_card", "unclear"},
            "B": {"same_entity", "different_entity", "related_group", "unclear"}}
MIN_PHRASE = 25
LEGAL = {"inc", "llc", "lp", "ltd", "limited", "plc", "corp", "corporation", "co", "company", "the", "sa", "nv",
         "ag", "llp", "pty", "holdings", "group", "se", "spa", "oyj", "ab", "as"}


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().casefold()


def norm_name(s):
    parole = re.sub(r"[^0-9a-z]+", " ", norm(s)).split()
    return " ".join(w for w in parole if w not in LEGAL)


def _exa_key():
    with open(ENV, encoding="utf-8") as f:
        for riga in f:
            if riga.startswith("EXA_API_KEY"):
                return riga.split("=", 1)[1].strip()
    sys.exit("EXA_API_KEY non trovata in " + ENV)


def get_page_text(url):
    body = json.dumps({"urls": [url], "text": True}).encode()
    req = urllib.request.Request("https://api.exa.ai/contents", data=body, method="POST", headers={
        "x-api-key": _exa_key(), "content-type": "application/json", "user-agent": "mitl-check-b5"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    res = r.get("results") or []
    return res[0].get("text", "") if res else ""


def attiva(e):
    return e is not None and not any(h.get("action") == "entity_retired" for h in e.get("history", []))


def domini(e):
    out = set()
    for k in ("sources",):
        s = e.get(k, {})
        for u in ((s.get("infonodes") or {}).get("website"), (s.get("wikidata") or {}).get("official_website"),
                  (s.get("crunchbase") or {}).get("website")):
            if u:
                d = re.sub(r"^https?://(www\.)?", "", u.strip().lower()).split("/")[0]
                if d:
                    out.add(d)
    return out


def isin_di(e):
    return ((e.get("sources", {}).get("wikidata") or {}).get("isin") or "").strip()


def check(result, inp, ents, text_fn=get_page_text):
    fails, human = [], []
    if not isinstance(result, dict) or "cases" not in result or "batch" not in result:
        return "FAIL", ["file non conforme: servono 'batch' e 'cases'"]
    ruolo = inp["role"]
    if result["batch"] != inp["batch"]:
        fails.append("lotto %r diverso dall'input %r" % (result["batch"], inp["batch"]))
    chiave = "ticker" if ruolo == "A" else "entita_id"
    attesi = {c[chiave] for c in inp["cases"]}
    dati = {}
    for c in result["cases"]:
        k = c.get(chiave)
        if k in dati:
            fails.append("caso duplicato: %s" % k)
        dati[k] = c
    for k in sorted(attesi - set(dati)):
        fails.append("caso mancante: %s" % k)
    for k in sorted(set(dati) - attesi):
        fails.append("caso non richiesto: %s" % k)
    inp_by = {c[chiave]: c for c in inp["cases"]}
    cache = {}

    def testo(url):
        if url not in cache:
            cache[url] = text_fn(url)
        return cache[url]

    riep = []
    for k in sorted(attesi & set(dati)):
        c, ic = dati[k], inp_by[k]
        esito_caso = []
        v = c.get("verdict")
        if v not in VERDETTI[ruolo]:
            fails.append("%s: verdict non ammesso %r" % (k, v))
            continue
        if not isinstance(c.get("evidence"), list) or not isinstance(c.get("notes", ""), str):
            fails.append("%s: evidence deve essere una lista e notes una stringa" % k)
            continue
        card = None
        if v == "same_entity" or (ruolo == "B" and c.get("db_id")):
            i = c.get("db_id")
            card = ents.get(i)
            if not i or not attiva(card):
                fails.append("%s: db_id %r non esiste o e ritirata" % (k, i))
                continue
            if norm(card["name"]) != norm(c.get("db_name", "")):
                fails.append("%s: db_name %r diverso dal nome in database %r" % (k, c.get("db_name"), card["name"]))
            if ruolo == "B" and i not in {x["id"] for x in ic["candidate_cards"]}:
                human.append("%s: db_id %s non e tra le schede candidate dell'input" % (k, i))
        verificate = []
        for n, ev in enumerate(c["evidence"]):
            mancanti = [f for f in ("claim", "url", "phrase", "source_kind") if not ev.get(f)]
            if mancanti:
                fails.append("%s: evidence[%d] campi mancanti %s" % (k, n, mancanti))
                continue
            if ev["source_kind"] not in KINDS:
                fails.append("%s: evidence[%d] source_kind non ammesso" % (k, n))
                continue
            if len(norm(ev["phrase"])) < MIN_PHRASE:
                fails.append("%s: evidence[%d] frase troppo corta (minimo %d caratteri)" % (k, n, MIN_PHRASE))
                continue
            try:
                t = testo(ev["url"])
            except Exception as ex:
                fails.append("%s: evidence[%d] pagina non riaperta (%s)" % (k, n, ex))
                continue
            if norm(ev["phrase"]) in norm(t):
                verificate.append(ev)
            else:
                fails.append("%s: evidence[%d] frase non trovata nella pagina (%d caratteri letti)" % (k, n, len(t)))
        frasi = " ".join(norm(e["phrase"]) for e in verificate)
        nome_sec = norm_name(ic["sec_name"])
        # una prova deve nominare l'emittente SEC: nome, CIK senza zeri o ticker
        cik = (ic.get("cik") or "").lstrip("0")
        nomina_sec = bool(nome_sec and nome_sec in norm_name(frasi)) or bool(cik and re.search(r"\b%s\b" % cik, frasi)) \
            or (ruolo == "A" and bool(re.search(r"\b%s\b" % re.escape(ic["ticker"].casefold()), frasi)))
        if ruolo == "B":
            for alt in [a.strip() for a in (ic.get("other_spellings") or "").split(";") if a.strip()]:
                nomina_sec = nomina_sec or norm_name(alt) in norm_name(frasi)
        nomina_scheda = False
        if card is not None:
            attr = {norm_name(card["name"])} | {d for d in domini(card)}
            if isin_di(card):
                attr.add(norm(isin_di(card)))
            nomina_scheda = any(a and a in (norm_name(frasi) + " " + frasi) for a in attr)
        if v == "same_entity":
            if not verificate:
                fails.append("%s: same_entity senza nessuna frase di prova verificata" % k)
            else:
                if not nomina_sec:
                    human.append("%s: nessuna frase verificata nomina l'emittente SEC (nome, CIK o ticker)" % k)
                if not nomina_scheda:
                    human.append("%s: nessuna frase verificata nomina la scheda (nome, sito o ISIN)" % k)
                if not any(e["source_kind"] == "primary" for e in verificate):
                    human.append("%s: same_entity con sole prove secondarie" % k)
        elif v in ("different_entity", "related_group"):
            if not verificate:
                fails.append("%s: %s senza nessuna frase di prova verificata" % (k, v))
            elif not any(e["source_kind"] == "primary" for e in verificate):
                human.append("%s: %s con sole prove secondarie" % (k, v))
            human.append("%s: verdetto %s, lo conferma una persona (S6: un nodo per depositante)" % (k, v)) if v == "related_group" else None
        else:
            human.append("%s: verdetto %s, lo guarda una persona" % (k, v))
        riep.append("%s=%s%s" % (k, v, ("→" + c["db_id"]) if c.get("db_id") else ""))
    if fails:
        return "FAIL", fails + human
    if human:
        return "NEEDS_HUMAN", human + ["riepilogo: " + ", ".join(riep)]
    return "PASS", ["tutti i casi coerenti: " + ", ".join(riep)]


def main(argv):
    if not argv:
        sys.exit(__doc__)
    ents = {e["id"]: e for e in json.load(open(DB, encoding="utf-8"))["entities"]}
    peggio = 0
    for path in argv:
        p = pathlib.Path(path)
        try:
            result = json.load(open(p, encoding="utf-8"))
            inp = json.load(open(INPUT / p.name, encoding="utf-8"))
        except Exception as ex:
            esito, motivi = "FAIL", ["file non leggibile: %s" % ex]
        else:
            esito, motivi = check(result, inp, ents)
        print("%-12s %s" % (esito, path))
        for m in motivi:
            print("   -", m)
        peggio = max(peggio, {"PASS": 0, "NEEDS_HUMAN": 1, "FAIL": 2}[esito])
    sys.exit(peggio)


if __name__ == "__main__":
    main(sys.argv[1:])
