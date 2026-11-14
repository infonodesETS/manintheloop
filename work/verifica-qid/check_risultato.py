#!/usr/bin/env python3
"""
check_risultato.py - controlla il risultato di un agente di ricerca sui QID rimessi (bozza provvisoria).

Verifica, senza fidarsi dell'agente:
  1. formato del file e campi obbligatori;
  2. la scheda esiste e ha ancora il QID dichiarato;
  3. l'etichetta Wikidata dichiarata e quella vera (API di Wikidata);
  4. ogni frase di prova si trova davvero nella pagina citata (Exa /contents, chiave in
     ~/.config/infonodes/exa.env, mai stampata);
  5. il verdetto e coerente con le prove.

Non scrive nel database ne altrove. Uso, dalla radice del repo:
    python3 -I work/verifica-qid/check_risultato.py work/verifica-qid/risultati/IN-0599.json [altri...]

Esito per file: PASS, NEEDS_HUMAN o FAIL (con i motivi). Codice di uscita: 0 se tutti PASS,
1 se almeno un NEEDS_HUMAN e nessun FAIL, 2 se almeno un FAIL.
"""
import json, os, re, sys, urllib.request

DB = "docs/data/database.json"
ENV = os.path.expanduser("~/.config/infonodes/exa.env")
VERDICTS = {"remove_qid", "keep_qid", "unclear"}
KINDS = {"primary", "secondary"}
REQUIRED = ["entity_id", "entity_name", "qid", "wikidata_label", "verdict", "verdict_reason",
            "identifiers", "evidence", "notes"]
QID_RE = re.compile(r"^Q\d+$")
MIN_PHRASE = 25  # caratteri: sotto, la frase non prova niente, salvo che sia un identificativo dichiarato


def norm(s):
    """Minuscolo, spazi ridotti, virgolette e apostrofi tipografici uniformati."""
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().casefold()


LEGAL = {"spa", "sl", "slu", "srl", "sa", "sas", "sasu", "bv", "nv", "gmbh", "ag", "ab", "oy", "oyj", "as", "asa",
         "plc", "ltd", "limited", "llc", "inc", "corp", "corporation", "co", "kft", "kg", "se", "sarl", "ltda"}


def norm_name(s):
    """Per confrontare nomi di societa: solo lettere e cifre, senza forma giuridica finale."""
    parole = re.sub(r"[^0-9a-z]+", " ", norm(s)).split()
    while parole and parole[-1] in LEGAL:
        parole.pop()
    return " ".join(parole)


def _is_identifier(phrase, identifiers):
    """Una frase breve e ammessa solo se e (parte di) un identificativo dichiarato, per esempio un KvK o un NIF."""
    p = norm(phrase)
    if len(p) < 5:
        return False
    for ident in identifiers:
        v = norm(str(ident.get("value", "")))
        if len(v) >= 5 and (p in v or v in p):
            return True
    return False


# --- accesso alla rete (sostituibili nei test) ---------------------------------

def get_wikidata_label(qid):
    url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=%s&props=labels&format=json" % qid)
    req = urllib.request.Request(url, headers={"User-Agent": "mitl-check-risultato/0.1 (verifica dati pubblici)"})
    r = json.load(urllib.request.urlopen(req, timeout=60))
    ent = r.get("entities", {}).get(qid, {})
    labels = ent.get("labels", {})
    if "en" in labels:
        return labels["en"]["value"]
    for v in labels.values():
        return v["value"]
    return ""


def _exa_key():
    with open(ENV, encoding="utf-8") as f:
        for riga in f:
            if riga.startswith("EXA_API_KEY"):
                return riga.split("=", 1)[1].strip()
    sys.exit("EXA_API_KEY non trovata in " + ENV)


def get_page_text(url):
    body = json.dumps({"urls": [url], "text": True}).encode()
    req = urllib.request.Request("https://api.exa.ai/contents", data=body, method="POST", headers={
        "x-api-key": _exa_key(), "content-type": "application/json", "user-agent": "mitl-check-risultato"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    res = r.get("results") or []
    return res[0].get("text", "") if res else ""


# --- controllo ------------------------------------------------------------------

def check(result, db_entities, label_fn=get_wikidata_label, text_fn=get_page_text):
    """Ritorna (esito, motivi). esito in PASS / NEEDS_HUMAN / FAIL."""
    fails, human = [], []

    # 1. formato
    if not isinstance(result, dict):
        return "FAIL", ["il file non e un oggetto JSON"]
    for k in REQUIRED:
        if k not in result:
            fails.append("campo mancante: " + k)
    if fails:
        return "FAIL", fails
    if result["verdict"] not in VERDICTS:
        fails.append("verdict non ammesso: %r" % result["verdict"])
    if not QID_RE.match(str(result["qid"])):
        fails.append("qid non valido: %r" % result["qid"])
    if not isinstance(result["evidence"], list) or not isinstance(result["identifiers"], list):
        fails.append("evidence e identifiers devono essere liste")
    if fails:
        return "FAIL", fails

    # 2. scheda e QID
    e = db_entities.get(result["entity_id"])
    if e is None:
        return "FAIL", ["scheda %s non trovata nel database" % result["entity_id"]]
    if e.get("wikidata_id") != result["qid"]:
        fails.append("la scheda ha wikidata_id %r, il risultato dice %r" % (e.get("wikidata_id"), result["qid"]))
    if norm(e["name"]) != norm(result["entity_name"]):
        fails.append("nome scheda %r diverso da entity_name %r" % (e["name"], result["entity_name"]))

    # 3. etichetta Wikidata vera
    try:
        true_label = label_fn(result["qid"])
    except Exception as ex:  # rete
        human.append("etichetta Wikidata non verificabile (%s)" % ex)
        true_label = None
    if true_label is not None and norm(true_label) != norm(result["wikidata_label"]):
        fails.append("etichetta Wikidata dichiarata %r, vera %r" % (result["wikidata_label"], true_label))

    # 4. frasi di prova nelle pagine
    verified = []
    for i, ev in enumerate(result["evidence"]):
        for k in ("claim", "url", "phrase", "source_kind"):
            if not ev.get(k):
                fails.append("evidence[%d]: campo mancante %s" % (i, k))
        if ev.get("source_kind") not in KINDS:
            fails.append("evidence[%d]: source_kind non ammesso %r" % (i, ev.get("source_kind")))
        if not ev.get("url") or not ev.get("phrase"):
            continue
        if len(norm(ev["phrase"])) < MIN_PHRASE and not _is_identifier(ev["phrase"], result["identifiers"]):
            fails.append("evidence[%d]: frase troppo corta (%d caratteri, minimo %d) e non e un identificativo dichiarato: %r"
                         % (i, len(norm(ev["phrase"])), MIN_PHRASE, ev["phrase"]))
            continue
        try:
            text = text_fn(ev["url"])
        except Exception as ex:
            fails.append("evidence[%d]: pagina non riaperta (%s): %s" % (i, ex, ev["url"]))
            continue
        if norm(ev["phrase"]) in norm(text):
            verified.append(ev)
        else:
            fails.append("evidence[%d]: frase non trovata nella pagina (%d caratteri letti; un PDF puo essere tronco): %s"
                         % (i, len(text), ev["url"]))

    # 5. coerenza del verdetto
    v = result["verdict"]
    same_name = norm_name(result["wikidata_label"]) == norm_name(e["name"]) and result["wikidata_label"] != ""
    if v == "remove_qid":
        if same_name:
            fails.append("remove_qid ma l'etichetta Wikidata coincide col nome della scheda")
        if not result["identifiers"] and not verified:
            fails.append("remove_qid senza identificativi ne frasi di prova verificate")
        elif not verified:
            human.append("remove_qid con identificativi ma nessuna frase di prova verificata")
        elif not any(ev.get("source_kind") == "primary" for ev in verified):
            human.append("remove_qid con sole prove secondarie (nessuna fonte primaria verificata): lo guarda una persona")
        if result["wikidata_label"] == "" and not verified:
            human.append("etichetta Wikidata vuota e nessuna prova verificata")
    elif v == "keep_qid":
        if not same_name:
            human.append("keep_qid ma l'etichetta Wikidata %r non coincide col nome %r: lo guarda una persona"
                         % (result["wikidata_label"], e["name"]))
        if not verified:
            fails.append("keep_qid senza nessuna frase di prova verificata")
    else:  # unclear
        human.append("verdetto unclear: lo guarda una persona")

    if fails:
        return "FAIL", fails + human
    if human:
        return "NEEDS_HUMAN", human
    return "PASS", ["etichetta, prove e verdetto coerenti (%d frasi verificate)" % len(verified)]


def main(argv):
    if not argv:
        sys.exit(__doc__)
    db = json.load(open(DB, encoding="utf-8"))
    ents = {x["id"]: x for x in db["entities"]}
    worst = 0
    for path in argv:
        try:
            result = json.load(open(path, encoding="utf-8"))
        except Exception as ex:
            esito, motivi = "FAIL", ["file non leggibile: %s" % ex]
        else:
            esito, motivi = check(result, ents)
        print("%s  %s" % (esito, path))
        for m in motivi:
            print("   - " + m)
        worst = max(worst, {"PASS": 0, "NEEDS_HUMAN": 1, "FAIL": 2}[esito])
    sys.exit(worst)


if __name__ == "__main__":
    main(sys.argv[1:])
