#!/usr/bin/env python3
"""Prove del controllo (senza rete): casi giusti passano, errori piantati falliscono (test del test).
Uso, dalla radice: python3 -I work/verifica-qid/test_check_risultato.py"""
import copy, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_risultato as C

ENT = {"IN-0599": {"id": "IN-0599", "name": "Damen Naval", "wikidata_id": "Q950580"},
       "IN-0865": {"id": "IN-0865", "name": "Mbda Italia", "wikidata_id": "Q131887361"}}
PAGES = {"u1": "Foo. De Onderneming Damen Naval B.V., geregistreerd bij de Kamer van Koophandel (KvK)\n onder nummer 89106253, is gevestigd.",
         "u2": "Damen Naval is the dedicated naval shipbuilding division of the Damen Shipyards Group."}
LABELS = {"Q950580": "Damen Group", "Q131887361": "MBDA Italia SpA"}
lab = lambda q: LABELS[q]
txt = lambda u: PAGES[u]

BASE = {"entity_id": "IN-0599", "entity_name": "Damen Naval", "qid": "Q950580", "wikidata_label": "Damen Group",
        "verdict": "remove_qid", "verdict_reason": "x", "identifiers": [{"type": "KvK", "value": "89106253", "source_url": "u1"}],
        "evidence": [{"claim": "c", "url": "u1", "phrase": "geregistreerd bij de Kamer van Koophandel (KvK) onder nummer 89106253", "source_kind": "secondary"},
                     {"claim": "c2", "url": "u2", "phrase": "dedicated naval shipbuilding division", "source_kind": "primary"}],
        "notes": ""}

def run(mut=None, ents=ENT):
    r = copy.deepcopy(BASE)
    if mut: mut(r)
    return C.check(r, ents, lab, txt)

def drop(k):
    return lambda r: r.pop(k)

CASI = [
 ("giusto: remove_qid con prove verificate", None, "PASS"),
 ("campo mancante (notes)", drop("notes"), "FAIL"),
 ("verdict non ammesso", lambda r: r.update(verdict="forse"), "FAIL"),
 ("QID diverso da quello della scheda", lambda r: r.update(qid="Q131887361", wikidata_label="MBDA Italia SpA"), "FAIL"),
 ("etichetta Wikidata inventata", lambda r: r.update(wikidata_label="Damen Naval B.V."), "FAIL"),
 ("frase non presente nella pagina", lambda r: r["evidence"][0].update(phrase="questa frase non esiste"), "FAIL"),
 ("source_kind non ammesso", lambda r: r["evidence"][1].update(source_kind="wikipedia"), "FAIL"),
 ("remove_qid ma l'etichetta e il nome della scheda", lambda r: r.update(wikidata_label="Damen Naval"), "FAIL"),
 ("remove_qid senza identificativi ne prove", lambda r: r.update(identifiers=[], evidence=[]), "FAIL"),
 ("remove_qid con identificativi ma senza frasi verificate", lambda r: r.update(evidence=[]), "NEEDS_HUMAN"),
 ("unclear va a una persona", lambda r: r.update(verdict="unclear"), "NEEDS_HUMAN"),
 ("nome scheda sbagliato", lambda r: r.update(entity_name="Altra"), "FAIL"),
 ("scheda inesistente", lambda r: r.update(entity_id="IN-9999"), "FAIL"),
 ("keep_qid con nome diverso dall'etichetta: persona", lambda r: r.update(verdict="keep_qid"), "NEEDS_HUMAN"),
 ("frase troppo corta e non identificativo", lambda r: r["evidence"][1].update(phrase="Damen Naval"), "FAIL"),
 ("frase corta ma e l'identificativo dichiarato", lambda r: (r["evidence"][0].update(phrase="89106253"),
        r["identifiers"][0].update(value="KvK 89106253")), "PASS"),
 ("remove_qid con sole prove secondarie", lambda r: r["evidence"][1].update(source_kind="secondary"), "NEEDS_HUMAN"),
 ("frase corta che non e un identificativo (5+ caratteri)", lambda r: r["evidence"][0].update(phrase="Foo. "), "FAIL"),
]
bad = 0
for nome, mut, atteso in CASI:
    esito, motivi = run(mut)
    ok = esito == atteso
    bad += not ok
    print("%s  %-55s atteso %-11s ottenuto %s" % ("ok " if ok else "ERR", nome, atteso, esito))
# keep_qid giusto (MBDA Italia: etichetta = nome, prova verificata)
r = copy.deepcopy(BASE); r.update(entity_id="IN-0865", entity_name="Mbda Italia", qid="Q131887361",
    wikidata_label="MBDA Italia SpA", verdict="keep_qid", identifiers=[])
esito, _ = C.check(r, ENT, lab, txt)
ok = esito == "PASS"; bad += not ok
print("%s  %-55s atteso %-11s ottenuto %s" % ("ok " if ok else "ERR", "giusto: keep_qid con etichetta uguale e prova", "PASS", esito))
# la rete che cade non e un PASS
def boom(u): raise RuntimeError("403")
esito, _ = C.check(copy.deepcopy(BASE), ENT, lab, boom)
ok = esito == "FAIL"; bad += not ok
print("%s  %-55s atteso %-11s ottenuto %s" % ("ok " if ok else "ERR", "pagina non riaperta (403)", "FAIL", esito))
print("\nERRORI NEI TEST: %d" % bad)
sys.exit(1 if bad else 0)
