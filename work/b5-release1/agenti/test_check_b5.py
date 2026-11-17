"""Test di check_b5.py con pagine finte (nessuna rete). Uso: python3 -I work/b5-release1/agenti/test_check_b5.py"""
import json, pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_b5 as C

ENTS = {e["id"]: e for e in json.load(open(C.DB, encoding="utf-8"))["entities"]}
INP = {"role": "A", "batch": "T1", "cases": [
    {"ticker": "FTNT", "sec_name": "Fortinet, Inc.", "cik": "0001262039", "sec_proxy_url": "x"},
    {"ticker": "GOOG", "sec_name": "Alphabet Inc.", "cik": "0001652044", "sec_proxy_url": "x"}]}
PAGE = "Fortinet, Inc. (CIK 0001262039) is a Delaware corporation; its website is fortinet.com and the company is also known as Fortinet."
FRASE = "Fortinet, Inc. (CIK 0001262039) is a Delaware corporation"


def caso(t, **kw):
    base = {"ticker": t, "db_id": "IN-0134", "db_name": ENTS["IN-0134"]["name"], "verdict": "same_entity", "notes": "",
            "evidence": [{"claim": "issuer", "url": "u1", "phrase": FRASE, "source_kind": "primary"}]}
    base.update(kw)
    return base


def run(cases, inp=INP):
    return C.check({"batch": "T1", "cases": cases}, inp, ENTS, text_fn=lambda u: PAGE)


class T(unittest.TestCase):
    def test_pass(self):
        e, m = run([caso("FTNT"), caso("GOOG", verdict="unclear", db_id=None, evidence=[])])
        self.assertEqual(e, "NEEDS_HUMAN", m)  # unclear -> persona
        e, m = C.check({"batch": "T1", "cases": [caso("FTNT")]}, {**INP, "cases": INP["cases"][:1]}, ENTS, text_fn=lambda u: PAGE)
        self.assertEqual(e, "PASS", m)

    def test_missing_case(self):
        e, m = run([caso("FTNT")])
        self.assertEqual(e, "FAIL"); self.assertTrue(any("mancante" in x for x in m))

    def test_extra_case(self):
        e, m = run([caso("FTNT"), caso("GOOG"), caso("ZZZ")])
        self.assertEqual(e, "FAIL")

    def test_phrase_not_in_page(self):
        c = caso("FTNT"); c["evidence"][0]["phrase"] = "Fortinet, Inc. is a Californian cooperative bank founded in 1901"
        e, m = C.check({"batch": "T1", "cases": [c]}, {**INP, "cases": INP["cases"][:1]}, ENTS, text_fn=lambda u: PAGE)
        self.assertEqual(e, "FAIL")

    def test_retired_card(self):
        e, m = C.check({"batch": "T1", "cases": [caso("FTNT", db_id="IN-0017", db_name="Alphabet Class A")]},
                       {**INP, "cases": INP["cases"][:1]}, ENTS, text_fn=lambda u: PAGE)
        self.assertEqual(e, "FAIL")

    def test_wrong_card_name(self):
        e, m = C.check({"batch": "T1", "cases": [caso("FTNT", db_name="Altro nome")]},
                       {**INP, "cases": INP["cases"][:1]}, ENTS, text_fn=lambda u: PAGE)
        self.assertEqual(e, "FAIL")

    def test_phrase_does_not_name_card(self):
        c = caso("FTNT"); c["evidence"][0]["phrase"] = "its website is fortinet.com and the company is also known"
        c["db_id"] = "IN-0270"; c["db_name"] = ENTS["IN-0270"]["name"]  # Nucor
        e, m = C.check({"batch": "T1", "cases": [c]}, {**INP, "cases": INP["cases"][:1]}, ENTS, text_fn=lambda u: PAGE)
        self.assertEqual(e, "NEEDS_HUMAN", m)  # la frase non nomina Nucor

    def test_wrong_batch(self):
        e, m = C.check({"batch": "X", "cases": []}, INP, ENTS, text_fn=lambda u: PAGE)
        self.assertEqual(e, "FAIL")


if __name__ == "__main__":
    unittest.main(verbosity=1)
