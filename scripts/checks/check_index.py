#!/usr/bin/env python3
"""
Controllo F5.4: l'indice del chatbot MARLA (docs/data/mitl-index.json) è
coerente con il database (docs/data/database.json).

L'indice lo scrive scripts/build_chat_index.py. Questo controllo non lo importa:
un controllo che riusa il codice controllato non ne scoprirebbe gli errori.
Ricostruisce da sé le regole che gli servono:
  - una scheda è ritirata se la sua `history` ha un'azione `entity_retired`;
  - i soggetti sono le schede attive con id che non comincia per `EDF-`,
    i progetti quelle con id `EDF-`;
  - una relazione è attiva se né `source` né `target` sono ritirati;
  - url: <sito>/search.html?organization=<id> per i soggetti,
         <sito>/networks.html?selected=<id> per i progetti.

Due livelli, per una regola decisa nel piano: l'indice si rigenera solo con una
decisione separata e avvisando chi usa MARLA, quindi una PR di dati non deve
diventare rossa solo perché l'indice è indietro.

ERRORI (exit 1): l'indice è rotto.
  - JSON non valido (database o indice);
  - chiavi mancanti tra generato, fonte, visibilita, sito, soggetti, progetti,
    relazioni;
  - `sito` diverso da https://infonodesets.github.io/manintheloop (è l'URL che
    usa MARLA);
  - id di soggetto o progetto assente dal database (gli id sono permanenti:
    succede solo per errore); id doppi; un EDF- tra i soggetti o un non-EDF- tra i progetti;
  - relazione con `da` o `a` che non sono tra soggetti e progetti dell'indice;
  - `tipo` di relazione non ammesso (lo stesso elenco di scripts/validate.py,
    letto dal suo testo senza importarlo);
  - `url` diverso dalla forma qui sopra.

AVVISI (exit 0, anche come righe `::warning::` per GitHub Actions): l'indice è
solo vecchio.
  - schede ritirate ancora nell'indice: MARLA rimanda a schede che il sito non
    mostra più (decisione di Nelson, 2026-11-28: una PR che unisce due schede
    non deve diventare rossa solo per questo; prima era un errore);
  - soggetti, progetti o relazioni attive del database che mancano nell'indice;
  - relazioni dell'indice che non ci sono più nel database (confronto per
    (da, a, tipo), contando le ripetizioni);
  - `generato` più vecchio di `_updated` del database.
Per ogni caso: il conteggio e i primi 10.

Uso (dalla radice del repo):
  python3 scripts/checks/check_index.py [database.json] [mitl-index.json]
"""
import ast
import json
import os
import sys
from collections import Counter

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE = os.path.join(RADICE, "docs", "data", "database.json")
INDICE = os.path.join(RADICE, "docs", "data", "mitl-index.json")
VALIDATE = os.path.join(RADICE, "scripts", "validate.py")

SITO = "https://infonodesets.github.io/manintheloop"
CHIAVI = ("generato", "fonte", "visibilita", "sito", "soggetti", "progetti", "relazioni")
PRIMI = 10          # quanti esempi negli avvisi
MAX_ERRORI = 20     # quanti errori per tipo si stampano (il conteggio è sempre intero)


def tipi_ammessi():
    """VALID_REL_TYPES letto dal testo di validate.py, senza importarlo
    (validate.py legge sys.argv e fa lavoro all'import)."""
    albero = ast.parse(open(VALIDATE, encoding="utf-8").read(), VALIDATE)
    for nodo in albero.body:
        if isinstance(nodo, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "VALID_REL_TYPES" for t in nodo.targets):
            return set(ast.literal_eval(nodo.value))
    raise ValueError("VALID_REL_TYPES non trovato in scripts/validate.py")


def carica(percorso, nome):
    try:
        with open(percorso, encoding="utf-8") as f:
            return json.load(f), None
    except (OSError, UnicodeDecodeError, ValueError) as e:
        return None, f"{nome} ({percorso}): JSON non valido o illeggibile: {e}"


def main():
    p_db = sys.argv[1] if len(sys.argv) > 1 else DATABASE
    p_ix = sys.argv[2] if len(sys.argv) > 2 else INDICE

    errori = {}       # tipo di errore -> elenco di righe
    avvisi = []       # (testo riassuntivo, primi esempi, indice da rigenerare?)
    ritirati_ix = []  # id dell'indice che nel database sono schede ritirate

    def errore(tipo, testo):
        errori.setdefault(tipo, []).append(testo)

    db, e1 = carica(p_db, "database")
    ix, e2 = carica(p_ix, "indice")
    for e in (e1, e2):
        if e:
            errore("JSON non valido", e)
    if not isinstance(ix, dict) and not e2:
        errore("JSON non valido", "indice: non è un oggetto JSON")
        ix = None
    if not isinstance(db, dict) and not e1:
        errore("JSON non valido", "database: non è un oggetto JSON")
        db = None
    if db is None or ix is None:
        return fine(errori, avvisi, None)

    try:
        ammessi = tipi_ammessi()
    except (OSError, SyntaxError, ValueError) as e:
        errore("tipi di relazione", f"non riesco a leggere l'elenco da scripts/validate.py: {e}")
        ammessi = None

    # ── database: schede attive e relazioni attive ───────────────────────────
    entita = db.get("entities") or []
    tutte = {e.get("id") for e in entita}
    ritirate = {
        e.get("id") for e in entita
        if any(h.get("action") == "entity_retired" for h in (e.get("history") or []))
    }
    attivi = [e.get("id") for e in entita if e.get("id") not in ritirate]
    db_soggetti = [i for i in attivi if not str(i).startswith("EDF-")]
    db_progetti = [i for i in attivi if str(i).startswith("EDF-")]
    db_rel = Counter(
        (r.get("source"), r.get("target"), r.get("type"))
        for r in (db.get("relationships") or [])
        if r.get("source") not in ritirate and r.get("target") not in ritirate
    )

    # ── indice: struttura ────────────────────────────────────────────────────
    for k in CHIAVI:
        if k not in ix:
            errore("chiavi mancanti", f"manca la chiave `{k}`")
    if "sito" in ix and ix["sito"] != SITO:
        errore("sito", f"`sito` è {ix['sito']!r}, deve essere {SITO!r} (è l'URL che usa MARLA)")

    def elenco(k):
        v = ix.get(k, [])
        if not isinstance(v, list):
            errore("chiavi mancanti", f"`{k}` non è un elenco")
            return []
        return v

    ix_soggetti, ix_progetti, ix_rel = elenco("soggetti"), elenco("progetti"), elenco("relazioni")

    # ── indice: soggetti e progetti ──────────────────────────────────────────
    visti = Counter()
    for chiave, voci, edf, forma in (
            ("soggetti", ix_soggetti, False, SITO + "/search.html?organization=%s"),
            ("progetti", ix_progetti, True, SITO + "/networks.html?selected=%s")):
        for n, v in enumerate(voci):
            if not isinstance(v, dict) or "id" not in v:
                errore("voci senza id", f"{chiave}[{n}]: voce senza `id`")
                continue
            i = v["id"]
            visti[i] += 1
            if i not in tutte:
                errore("id assenti dal database", f"{chiave}: {i}")
            elif i in ritirate:
                ritirati_ix.append(i)
            if str(i).startswith("EDF-") != edf:
                errore("id nella lista sbagliata",
                       f"{chiave}: {i}" + (" non è un EDF-" if edf else " è un EDF-"))
            atteso = forma % i
            if v.get("url") != atteso:
                errore("url sbagliati", f"{chiave}: {i}: url {v.get('url')!r}, atteso {atteso!r}")
    for i, c in visti.items():
        if c > 1:
            errore("id doppi", f"{i} compare {c} volte tra soggetti e progetti")

    # ── indice: relazioni ────────────────────────────────────────────────────
    nell_indice = set(visti)
    ix_rel_c = Counter()
    for n, r in enumerate(ix_rel):
        if not isinstance(r, dict):
            errore("relazioni malformate", f"relazioni[{n}]: non è un oggetto")
            continue
        da, a, tipo = r.get("da"), r.get("a"), r.get("tipo")
        ix_rel_c[(da, a, tipo)] += 1
        for lato, i in (("da", da), ("a", a)):
            if i not in nell_indice:
                motivo = " (scheda ritirata)" if i in ritirate else ""
                errore("relazioni verso id fuori dall'indice",
                       f"relazioni[{n}] {da} -> {a} ({tipo}): `{lato}` {i!r} non è tra soggetti e progetti{motivo}")
        if ammessi is not None and tipo not in ammessi:
            errore("tipi di relazione non ammessi",
                   f"relazioni[{n}] {da} -> {a}: tipo {tipo!r} (ammessi: {', '.join(sorted(ammessi))})")

    # ── avvisi: indice indietro rispetto al database ─────────────────────────
    def avvisa(testo, voci):
        voci = list(voci)
        if voci:
            avvisi.append((f"{testo}: {len(voci)}", voci[:PRIMI], True))

    avvisa("schede ritirate ancora nell'indice (MARLA rimanda a schede che il sito "
           "non mostra più)", ritirati_ix)
    avvisa("soggetti attivi del database che mancano nell'indice",
           [i for i in db_soggetti if i not in nell_indice])
    avvisa("progetti attivi del database che mancano nell'indice",
           [i for i in db_progetti if i not in nell_indice])

    def righe_rel(diff):
        out = []
        for (da, a, tipo), c in sorted(diff.items(), key=lambda x: tuple(map(str, x[0]))):
            out.extend([f"{da} -> {a} ({tipo})"] * c)
        return out

    avvisa("relazioni attive del database che mancano nell'indice", righe_rel(db_rel - ix_rel_c))
    avvisa("relazioni dell'indice che non ci sono più nel database", righe_rel(ix_rel_c - db_rel))

    generato, aggiornato = ix.get("generato"), db.get("_updated")
    if aggiornato is None:
        avvisi.append(("il database non ha `_updated`: non posso dire se l'indice è più vecchio", [], False))
    elif isinstance(generato, str) and isinstance(aggiornato, str) and generato < aggiornato:
        avvisi.append((f"indice generato il {generato}, database aggiornato il {aggiornato}: "
                       f"l'indice è più vecchio del database", [], True))

    conteggi = (f"Indice: {len(ix_soggetti)} soggetti, {len(ix_progetti)} progetti, "
                f"{len(ix_rel)} relazioni. Database: {len(attivi)} entità attive "
                f"({len(db_soggetti)} soggetti, {len(db_progetti)} progetti; {len(ritirate)} ritirate), "
                f"{sum(db_rel.values())} relazioni attive.")
    return fine(errori, avvisi, conteggi)


def fine(errori, avvisi, conteggi):
    if conteggi:
        print(conteggi)
    for testo, voci, _ in avvisi:
        dettaglio = (" (primi %d: %s)" % (len(voci), "; ".join(voci))) if voci else ""
        print(f"::warning::Indice MARLA: {testo}{dettaglio}")
        print(f"  AVVISO: {testo}")
        for v in voci:
            print(f"    - {v}")
    if errori:
        n = sum(len(v) for v in errori.values())
        print(f"ERRORI: {n}")
        for tipo, righe in errori.items():
            print(f"  {tipo}: {len(righe)}")
            for r in righe[:MAX_ERRORI]:
                print(f"    ✗ {r}")
            if len(righe) > MAX_ERRORI:
                print(f"    … e altri {len(righe) - MAX_ERRORI}")
        print("CONTROLLO INDICE FALLITO")
        sys.exit(1)
    if avvisi:
        nota = (" (l'indice è da rigenerare, con una decisione separata e avvisando chi usa MARLA)"
                if any(vecchio for _, _, vecchio in avvisi) else "")
        print(f"CONTROLLO INDICE SUPERATO con {len(avvisi)} avvisi{nota}")
    else:
        print("CONTROLLO INDICE SUPERATO")


if __name__ == "__main__":
    main()
