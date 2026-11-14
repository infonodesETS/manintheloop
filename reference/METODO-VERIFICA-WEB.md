# Metodo di verifica web con Exa

> **BOZZA PROVVISORIA, DA CONFERMARE DEFINITIVAMENTE (Nelson, 2026-11-14).** Scritta dopo due piccoli test (9 domande); **non è ancora stata applicata su casi reali** e non è una regola vincolante, salvo la regola già in `STATUS.md` («ricerche web sempre con Exa»). I test sono in [`work/verifica-web-test-2026-11-14.md`](../work/verifica-web-test-2026-11-14.md). Prima di renderla definitiva: provarla su casi veri (vedi «Da definire»), poi Nelson la conferma e si toglie questo avviso.

## A cosa serve

Nel controllo puntuale dei dati (duplicati, QID, codici fiscali, società controllate) serve trovare **più fonti** da cui verificare, non fidarsi di una sola. Exa (`/answer` per le domande, `/contents` per leggere le pagine) trova e riassume le fonti. **Exa è un modello che sintetizza il web: non è una fonte.** Il suo output è una proposta; la prova sta nelle fonti che cita, riaperte e lette.

## Passi

1. **Dire che decisione si prende.** Prima della domanda scrivere cosa si farà del dato a seconda della risposta (es. «togliere il QID di `IN-0599` se la scheda è una società a sé con una controllante»). La domanda deve servire a quella decisione, non alla sua forma giuridica in astratto.
2. **Formulare una domanda descrittiva e neutra**, non sì/no e senza dentro la propria ipotesi. Modello: «What is 'X'? Describe its legal form, registration details (company number, tax ID, registry) and parent company. Cite at least two independent sources and prefer primary ones (company registry, official website, annual report, regulatory filing). If you find no primary source, say so.» Una domanda sì/no con l'ipotesi dentro ha prodotto, nel test, una motivazione falsa (Damen Naval).
3. **Solo dati pubblici nella query**: nomi di società, codici, ticker. Mai dati interni del progetto, mai chiavi. Per le **persone** il metodo non è ancora definito (vedi «Da definire»).
4. **Raccogliere gli identificativi** che la risposta dà (numero d'impresa, NIF, SIREN, KvK, LEI, CIK, QID) con la fonte: sono la parte controllabile e quella che si riporta nei dati.
5. **Riaprire le fonti su cui si agisce** (`/contents`) e cercare nel testo la frase che dovrebbe provare l'affermazione. Una citazione non garantisce che la frase ci sia: nel test la pagina Damen citata non conteneva ciò che Exa le attribuiva. Fonte non riaperta = «non verificata».
6. **Classificare ogni affermazione:** *verificata* (frase letta in una fonte primaria), *proposta* (solo Exa o fonte secondaria), *non trovata* (assenza di prova, che **non** è prova di assenza: es. «nessun QID trovato»).
7. **Esito deciso e firmato da una persona**, con la formula già in uso: «Nelson (proposto da agente Claude, approvato il AAAA-MM-GG)». Exa e gli agenti propongono.
8. **Registrare**: nei dati, una `validation` con gli URL, la data e la frase di prova; nel log, la domanda, la risposta, cosa è stato riaperto e cosa no. Per le modifiche ai dati valgono le regole di `STATUS.md` (dry-run, history e validation lette, ok di Nelson).

## Fonti: gerarchia

- **Primarie:** registri ufficiali (BOE/BORME, RCS e INSEE, KvK, Bolagsverket, Companies House, SEC EDGAR, GLEIF), siti e bilanci della società, comunicati ufficiali.
- **Secondarie, da usare solo per trovare l'identificativo:** aggregatori di registri (`pappers.fr`, `companyinfo.nl`, `filings.es`, `verif.com`), LinkedIn, Crunchbase, stampa. L'identificativo trovato si controlla poi sul registro ufficiale quando si agisce.
- **API di dati strutturati** (Wikidata, GLEIF): si consultano direttamente, sono consultazioni di una fonte e non ricerche web. Ciò che se ne conclude (es. «questo QID è della casa madre») si verifica anche con Exa. *(Interpretazione dell'AI, da confermare.)*

## Limiti noti

- Exa può sbagliare anche con fonti dall'aspetto primario: Alcoa Warrick (pilota B3, domanda sì/no: «stabilimento» invece di società), Damen Naval (test, «divisione, non entità separata» contraddetto dal registro).
- I PDF letti con `/contents` possono arrivare tronchi (2.000-5.000 caratteri): una frase non trovata non prova che non ci sia.
- L'assenza di un risultato non è una prova (es. «nessun QID»).
- Campione dei test: 9 domande, 6 + 3, con ipotesi dell'AI nelle prime. **Non dimostra affidabilità.**
- Costo: una chiamata per domanda; nessun limite fissato. Tempo di riapertura delle fonti, che non si salta.

## Da definire prima di confermare

- Soglia delle fonti (due indipendenti, di cui una primaria): da provare su casi reali.
- Dove registrare le fonti nello schema (`validation` con quali campi) e se serve uno `status` dedicato.
- Persone fisiche (Release 2, dati personali): metodo e limiti, GDPR.
- Se tenere un registro delle risposte di Exa sbagliate (calibrazione) e dove.
- Quali verifiche vanno fatte con Exa e quali basta l'API (conferma dell'interpretazione sopra).
- Budget e frequenza: quali casi giustificano la verifica web (non tutti i 2.500 record).

## Riferimenti

- Chiave: `~/.config/infonodes/exa.env` (variabile `EXA_API_KEY`, permessi 600). **Mai nei file del repo, nei log, nei commit, nelle risposte.**
- Script d'esempio per `/answer`: `work/b3-pilota/pilota_exa.py` (non scrive nel DB). Per `/contents`: richiesta POST a `https://api.exa.ai/contents` con `{"urls": [...], "text": true}`.
- Pilota B3 e verdetti: `work/b3-pilota/pilota-exa-2026-11-12.csv`; metodo dei duplicati: [`B3-METODO.md`](B3-METODO.md).
