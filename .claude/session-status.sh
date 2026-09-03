#!/bin/sh
# Eseguito all'avvio di ogni sessione Claude Code (vedi .claude/settings.json).
# Allinea il repo con GitHub e riassume lo stato, così si riparte sempre
# sapendo dove eravamo rimasti — anche cambiando postazione.
# Volutamente senza dipendenze esterne (niente jq): deve funzionare su
# qualsiasi PC in cui si monti l'hard disk portatile.

echo "── Stato del repo all'avvio ──"
echo "Cartella: $(pwd)"
echo "Branch:   $(git rev-parse --abbrev-ref HEAD 2>&1)"
echo

git fetch --quiet 2>&1

# Il pull è --ff-only: se i due lati sono divergenti si ferma e lo segnala,
# invece di creare un merge a sorpresa all'avvio.
if ! git pull --ff-only 2>&1; then
  echo "!! Pull non riuscito: branch divergente o lavoro locale non salvato."
  echo "   Da risolvere a mano prima di continuare."
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

UNPUSHED=$(git log '@{u}..HEAD' --oneline 2>/dev/null)
if [ -n "$UNPUSHED" ]; then
  echo "!! COMMIT NON ANCORA SU GITHUB:"
  echo "$UNPUSHED"
else
  echo "Tutto allineato con GitHub."
fi
