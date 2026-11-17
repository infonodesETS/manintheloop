# Dry-run import SEC, release 2026-10-17 (nessuna scrittura nel database)

Righe nel file: 571
- importabile: 546
- scartata: 25
Riconciliazione: 571 = 571 -> OK
Attese da S4: 546 importate (somma importabili + bloccate + gia nel DB) e 25 scartate; trovate: 546 e 25
Chiavi duplicate tra le relazioni da creare: 0
Entita nuove (ID provvisori): PER 57, IV 93
Relazioni `ownership` da creare: 546 (da REL-0001)

## Righe bloccate (motivi)

## Date da controllare a mano (piu di due date nella fonte): 3
- riga 87 CHTR Liberty Broadband Corporation: «Schedule 13D/A dated May 16, 2025, filed May 19, 2025, e Form 4 dal 12 giugno 2025 al 14 gennaio 2026» -> filing 2025-05-19, as_of 2025-05-19
- riga 385 NWS Independent Franchise Partners: «Schedule 13G/A depositato il 13 agosto 2026 (Class A, dati al 30 giugno 2026); Schedule 13G/A depositato il 13» -> filing 2026-08-13, as_of 2026-06-30
- riga 386 NWS Independent Franchise Partners: «Schedule 13G/A depositato il 13 agosto 2026 (Class A, dati al 30 giugno 2026); Schedule 13G/A depositato il 13» -> filing 2026-08-13, as_of 2026-06-30

## Righe senza as_of: 4
- 2026-10-17/detentori-oltre-5.csv#155
- 2026-10-17/detentori-oltre-5.csv#156
- 2026-10-17/detentori-oltre-5.csv#157
- 2026-10-17/detentori-oltre-5.csv#158

## Origine di as_of: None=4, deposito=350, proxy=94, testo=98
