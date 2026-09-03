# Come si lavora a questo progetto

Il progetto si sviluppa da postazioni diverse (laptop, PC ufficio). Questo
documento serve a garantire che, cambiando macchina, si riparta sempre
esattamente da dove si era rimasti — **compreso il lavoro a metà**.

---

## La regola che conta

> **Esiste una sola cartella di lavoro: quella sull'hard disk portatile.**
>
> `D:\infonodes\CLAUDE\manintheloop`

L'hard disk viaggia con te, quindi viaggia anche tutto ciò che git non vede:
file modificati e non committati, branch a metà, prove non finite. Non c'è
niente da sincronizzare, perché non esiste una seconda copia da cui divergere.

Se ti accorgi che esiste un altro clone del repo su un disco fisso di una
qualsiasi postazione, **non lavorarci**: è la causa numero uno di lavoro perso.

### Perché è importante

L'11 agosto 2026 è successo esattamente questo. Il lavoro della settimana
precedente — la ristrutturazione in sezioni EU Funding / Investimenti globali —
era stato fatto su una copia diversa da quella in uso, e non era mai stato
committato. Non essendo committato non era su GitHub; non essendo su GitHub
era invisibile. È stato recuperato solo cercando a mano sul disco.

---

## GitHub: a cosa serve davvero

GitHub **non** è il modo con cui il lavoro si sposta fra le postazioni — a
quello ci pensa l'hard disk. GitHub è la rete di sicurezza: se il disco si
rompe, si perde o viene dimenticato da qualche parte, il progetto è comunque
salvo.

Da qui la regola: **a fine sessione si pusha sempre**, anche il lavoro
incompleto. Un commit `wip: sto lavorando ai selettori` è brutto ma innocuo;
un pomeriggio di lavoro solo sul disco no.

Il lavoro in corso sta su un branch dedicato (oggi `eu-funding`), **mai
direttamente su `main`**: `main` è ciò che il sito pubblica, e non deve mai
contenere pagine a metà.

---

## Inizio sessione

Non devi fare niente. All'apertura di Claude Code parte da solo
`.claude/session-status.sh`, che allinea il repo con GitHub e riassume:

- in quale cartella e su quale branch sei
- se ci sono file non committati (= lavoro lasciato a metà)
- se ci sono commit non ancora su GitHub

Se compare un `!!`, quello è il punto da cui riprendere.

## Fine sessione

Chiedi a Claude di **"salvare e pushare tutto"**. Il controllo è comunque
automatico all'avvio successivo: se qualcosa è rimasto indietro, lo vedrai
subito.

---

## Prima volta su una postazione nuova

Due cose da sistemare una sola volta per macchina.

**1. Git rifiuta il repo sul disco esterno.** Windows assegna a ogni utente un
identificativo diverso, quindi git vede il repo come "di qualcun altro" e si
blocca con `dubious ownership`. Si sblocca così:

```bash
git config --global --add safe.directory D:/infonodes/CLAUDE/manintheloop
```

**2. Controlla la lettera dell'unità.** Tutto qui dà per scontato che l'hard
disk si monti come `D:`. Se su quella postazione diventa `E:` o altro, il
comando qui sopra va adattato — e conviene riassegnare la lettera a `D:` da
Gestione disco di Windows, così resta tutto coerente.

---

## Numero di versione

Sotto il logo, in ogni pagina, compare la versione: oggi **`Prototype v.2026-b`**.

Lo schema è `Prototype v.ANNO-lettera`. A ogni nuova versione si passa alla
lettera successiva dell'alfabeto; l'anno cambia quando cambia l'anno solare e
si riparte da `a`. La versione online prima di questa era `v.1-20260715`, con
il vecchio schema a data.

Serve a distinguere a colpo d'occhio quale versione si sta guardando, quindi
**va cambiata prima di pubblicare**, non dopo.

La stringa è ripetuta in sei file: `index.html`, `networks.html`,
`key-figures.html`, `search.html`, `publications.html`, `about.html`. Chiedi a
Claude di aggiornarla e le cambia tutte in una volta.

---

## Server locale per vedere il sito

```bash
py -3 -m http.server 8001 --directory D:/infonodes/CLAUDE/manintheloop
```

Poi apri `http://localhost:8001`.

---

## Cosa NON è coperto da tutto questo

L'hard disk portatile resta un singolo punto di rottura per le cose che git
non traccia. Il push a fine sessione copre il codice; non copre file esclusi
dal repo (vedi `.gitignore`) né materiali di lavoro tenuti fuori dalla cartella.
