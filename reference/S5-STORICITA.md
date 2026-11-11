# S5 — storicità delle quote (decisione B1)

**Decisione S5 (Nelson, 2026-11-11): opzione (c), attuale più storia dentro la relazione.** Una relazione per (titolare, azienda, classe) con i valori correnti; i cambiamenti restano in `history[]` della relazione; niente cancellazioni. Una regola di questo file si cambia solo con una nuova decisione registrata nel log.

## Modello

- Chiave di unicità di `ownership`: `(source, target, type, classe)` (coerente con R2 di S3). Ogni relazione ha un `id` proprio.
- Campi di data e fonte: `filing_date` (ISO, data di deposito, se nota), `as_of` (ISO, data a cui si riferiscono le azioni), `as_of_origine` (`proxy` | `testo` | `deposito`), `release` (es. `2026-10-17`), `source_ref`.
- `current`: `true` finché la riga compare nell'ultima release importata.
- `history[]` della relazione (append-only): ogni voce con data, release, fonte, campo, valore vecchio, valore nuovo.

## `as_of` e `as_of_origine`

`as_of` si salva con quello che c'è, e `as_of_origine` dice quanto fidarsi:
- `proxy`: riga della tabella del proxy; `as_of` = `quote_al` di `aziende.csv` («la data a cui il proxy riferisce le quote», README della release). Data esatta del documento.
- `testo`: la data è scritta in prosa nella fonte («as of December 31, 2025») e viene estratta dal testo, con controllo a campione.
- `deposito`: solo la data di deposito del filing (13G/13D/13F); `as_of` = `filing_date`, approssimato (la data vera delle azioni sta dentro il filing, di solito il 31 dicembre dell'anno prima). Si può raffinare in seguito leggendo i filing, senza perdere nulla.

## Regole di re-import (B5 e release successive)

1. Prima di applicare, lo script stampa un **report dei cambiamenti**: righe nuove, cambiate, scomparse. La prima volta lo guarda una persona.
2. Riga con la stessa chiave e valori diversi: si aggiornano i valori correnti e si aggiunge una voce a `history[]` con valore vecchio, nuovo e fonte. Il valore vecchio non si perde.
3. Riga **scomparsa** in una release successiva: la relazione **non si cancella**. Si marca `current: false` con una voce in `history[]` e si elenca nel report come «da controllare». La scomparsa non significa che la quota sia finita: l'estrazione cambia fra due passate (su 20 aziende estratte due volte, 17 identiche, README di Andrea) e i depositi congiunti possono cambiare nome.
4. Riga con la stessa chiave e stessi valori: nessuna modifica (re-run sicuro, seconda esecuzione = 0 modifiche).
5. Valgono le regole di S3 (R1-R6) e S4 (soglia, riconciliazione, `rawdata` immutabili).

## Fuori da S5

- `role` (ruoli): campi `current`, `start_date`, `end_date` proposti da Andrea nella bozza; si decidono con S7 e la Release 2.
- Da verificare nel diff di B1: se `validate.py` controlla `history[]` delle relazioni (oggi solo 1 relazione su circa 3.500 ne ha una) e se il sito mostra o ignora `current: false`.

## Verifiche fatte (2026-11-11, sola lettura)

- La release 2026-10-17 è una sola fotografia: non esiste storico da conservare oggi.
- Su 571 righe: 333 con data ISO nella fonte (2011-2026: 108 nel 2024, 126 nel 2025, 96 nel 2026), 135 con fonte presente ma data in prosa o assente, 103 senza fonte (75 persone, 28 entità; `quote_al` dei proxy da 2025-08-28 a 2026-09-21).
- La chiave (azienda, titolare, classe) non è mai ripetuta nella release.
- Le relazioni del DB hanno oggi solo `created_at`.
