#!/bin/sh
# Eseguito all'avvio di ogni sessione Claude Code (vedi .claude/settings.json).
# Allinea il repo con GitHub e riassume lo stato, così si riparte sempre
# sapendo dove eravamo rimasti — anche cambiando postazione.
# Volutamente senza dipendenze esterne (niente jq): deve funzionare su
# qualsiasi PC in cui si monti l'hard disk portatile. Solo git e strumenti
# POSIX (sh, awk).

echo "── Stato del repo all'avvio ──"
echo "Cartella: $(pwd)"
echo "Branch:   $(git rev-parse --abbrev-ref HEAD 2>&1)"
echo

git fetch --quiet 2>&1

# Upstream del branch corrente (vuoto se il branch non ha remoto o se HEAD
# è staccato). Serve a decidere se tentare il pull e se il branch si può
# dire allineato.
UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null)

# Il pull è --ff-only: se i due lati sono divergenti si ferma e lo segnala,
# invece di creare un merge a sorpresa all'avvio. Senza upstream non si
# tenta: git darebbe solo «no tracking information».
if [ -n "$UPSTREAM" ]; then
  if ! git pull --ff-only 2>&1; then
    echo "!! Pull non riuscito: branch divergente o lavoro locale non salvato."
    echo "   Da risolvere a mano prima di continuare."
  fi
else
  echo "Branch senza remoto, pull non tentato."
fi
echo

DIRTY=$(git status --porcelain)
if [ -n "$DIRTY" ]; then
  echo "!! FILE NON COMMITTATI (lavoro a metà della sessione precedente):"
  echo "$DIRTY"
else
  echo "Working tree pulito."
fi
echo

# Confronto del branch corrente con il suo upstream (dopo l'eventuale pull).
ALLINEATO=si
if [ -n "$UPSTREAM" ]; then
  UNPUSHED=$(git log '@{u}..HEAD' --oneline 2>/dev/null)
  if [ -n "$UNPUSHED" ]; then
    echo "!! COMMIT NON ANCORA SU GITHUB:"
    echo "$UNPUSHED"
    ALLINEATO=no
  fi
  # Se il pull non è riuscito il branch può restare indietro: va detto.
  BEHIND_UP=$(git rev-list --count 'HEAD..@{u}' 2>/dev/null)
  if [ -n "$BEHIND_UP" ] && [ "$BEHIND_UP" -gt 0 ]; then
    echo "!! Branch indietro di $BEHIND_UP commit rispetto a $UPSTREAM."
    ALLINEATO=no
  fi
else
  echo "Branch senza remoto: non confrontato con GitHub."
  ALLINEATO=no
fi

# main locale rispetto a origin/main, qualunque sia il branch corrente.
# Solo un avviso: main non viene aggiornato da qui.
if git rev-parse --verify --quiet refs/heads/main >/dev/null &&
   git rev-parse --verify --quiet refs/remotes/origin/main >/dev/null; then
  MAIN_BEHIND=$(git rev-list --count refs/heads/main..refs/remotes/origin/main)
  if [ "$MAIN_BEHIND" -gt 0 ]; then
    echo "!! main locale indietro di $MAIN_BEHIND commit rispetto a origin/main"
    echo "   Merge in origin/main che mancano a main:"
    git log --merges --oneline refs/heads/main..refs/remotes/origin/main
    ALLINEATO=no
  fi
fi

if [ "$ALLINEATO" = si ]; then
  echo "Tutto allineato con GitHub."
fi
echo

# Dove si riparte: il piano, tutte le righe in corso (◐) e la prima da fare (☐)
# della tabella «Stato di avanzamento» (scelta di Nelson, 2026-11-28: la sola
# prima riga non chiusa era spesso un task fermo da settimane).
# Campi: | Task | Descrizione | Stato | Data | Note |
PIANO_REL=reference/PIANO-RIORGANIZZAZIONE.md
RADICE=$(git rev-parse --show-toplevel 2>/dev/null)
PIANO="${RADICE:-.}/$PIANO_REL"
if [ -f "$PIANO" ]; then
  echo "Piano: $PIANO_REL"
  RIGHE=$(awk -F'|' '
    function riga() {
      for (i = 2; i <= 5; i++) { gsub(/^[ \t]+|[ \t]+$/, "", $i) }
      r = $2 " — " $3 " (" $4
      if ($5 != "") r = r ", " $5
      return r ")"
    }
    /^## Stato di avanzamento/ { dentro = 1; next }
    dentro && /^## / { exit }
    dentro && /^\|/ && $4 ~ /◐/ { print "  in corso: " riga(); next }
    dentro && /^\|/ && $4 ~ /☐/ && !da_fare { da_fare = 1; print "  primo da fare: " riga() }
  ' "$PIANO")
  if [ -n "$RIGHE" ]; then
    echo "Stato di avanzamento:"
    echo "$RIGHE"
  else
    echo "Nessuna riga ☐ o ◐ nella tabella «Stato di avanzamento»."
  fi
else
  echo "Piano non trovato ($PIANO_REL): nessun punto di ripartenza da mostrare."
fi
