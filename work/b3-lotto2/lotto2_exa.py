#!/usr/bin/env python3
"""
lotto2_exa.py - B3 lotto 2: 7 coppie di possibili duplicati della tabella «Retired IDs» (sola lettura sul DB).
Domande descrittive e neutre a Exa /answer; salva risposta e fonti in CSV. Il verdetto lo scrive una persona.
Chiave in ~/.config/infonodes/exa.env, mai stampata. Uso (dalla radice): python3 work/b3-lotto2/lotto2_exa.py [--solo N]
"""
import csv, json, os, sys, urllib.request
OUT = "work/b3-lotto2/exa-2026-11-15.csv"
ENV = os.path.expanduser("~/.config/infonodes/exa.env")
TAIL = " Describe the legal form, registration numbers and parent company of each, and say whether they are the same legal entity, a renamed version, or related but separate companies. Cite at least two independent sources and prefer primary ones (company registry, official website, annual report, regulatory filing). If you find no primary source, say so."
CASI = [
 (1, ["IN-1014", "IN-1329"], "What are 'Saab Aktiebolag' (EU participant, PIC 999959615, Sweden) and 'Saab' (Saab AB, VAT SE556036079301, Swedish defence company)?" + TAIL),
 (2, ["IN-1118", "IN-1241"], "What are 'Tekever Uas' (EU participant, PIC 899397387, Portugal) and 'TEKEVER' (Portugal, NIF PT508345650, drone and defence technology company)?" + TAIL),
 (3, ["IN-0753", "IN-1298"], "What are 'Indra Sistemas' (EU participant, PIC 999959130, Spain) and 'Indra' (Spain, NIF ESA28599033, Madrid-listed technology and defence company)?" + TAIL),
 (4, ["IN-0035", "IN-1253"], "What are 'Arafura Rare Earths' (ASX-listed, Australia) and 'Arafura Resources' (ABN 22 080 933 455)? Has the company changed its name?" + TAIL),
 (5, ["IN-0401", "IN-1344"], "What are 'Vale do Rio Doce' (Companhia Vale do Rio Doce) and 'Vale' (Vale S.A., CNPJ 33.592.510/0001-54, Brazil)?" + TAIL),
 (6, ["IN-0287", "IN-1320"], "What are 'PLS' (ASX ticker PLS, Australia) and 'Pilbara Minerals' (ABN 44 675 885 515)? Has the company changed its name or ticker?" + TAIL),
 (7, ["IN-1335", "IN-1150"], "What are 'ThyssenKrupp Marine Systems' (VAT DE811124479, Germany) and 'TKMS' (EU participant, PIC 950773049, Germany, website tkmsgroup.com)? Is there a listed holding company TKMS and an operating company thyssenkrupp Marine Systems?" + TAIL),
]
def chiave():
    for r in open(ENV, encoding="utf-8"):
        if r.startswith("EXA_API_KEY="): return r.split("=", 1)[1].strip()
    sys.exit("chiave non trovata")
def chiedi(k, q):
    req = urllib.request.Request("https://api.exa.ai/answer", data=json.dumps({"query": q, "text": False}).encode(), method="POST",
        headers={"x-api-key": k, "content-type": "application/json", "user-agent": "mitl-b3-lotto2"})
    return json.load(urllib.request.urlopen(req, timeout=180))
solo = int(sys.argv[sys.argv.index("--solo")+1]) if "--solo" in sys.argv else None
k = chiave(); righe = []
for n, ids, q in CASI:
    if solo and n != solo: continue
    try:
        r = chiedi(k, q); a = (r.get("answer") or "").replace("\n", " "); f = " ".join(c.get("url", "") for c in r.get("citations", [])); e = ""
    except Exception as ex:
        a, f, e = "", "", type(ex).__name__ + " " + str(getattr(ex, "code", ""))
    righe.append({"caso": n, "ids": " ".join(ids), "domanda": q, "risposta_exa": a, "fonti_exa": f, "errore": e})
    print(n, ids, "errore:" + e if e else "ok, %d fonti" % len(f.split()))
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["caso", "ids", "domanda", "risposta_exa", "fonti_exa", "errore"]); w.writeheader(); w.writerows(righe)
