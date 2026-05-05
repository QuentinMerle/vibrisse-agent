#!/bin/bash

# Vibrisse CLI Launcher - Version Unifiée Robuste
# Usage: vibrisse [--no-ui]

# On résout le chemin réel du script (même s'il est appelé via un lien symbolique)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
ROOT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd "$ROOT_DIR"

# Détection automatique du mode via le nom de la commande (symlink)
CMD_NAME=$(basename "$0")
if [[ "$CMD_NAME" == "vibrisse-tui" ]]; then
    # On force le mode TUI si appelé via vibrisse-tui
    ARGS="--tui $*"
else
    ARGS="$*"
fi

# Chargement de l'environnement native
if [ -f .env.native ]; then
    export $(grep -v '^#' .env.native | xargs)
fi

# Activation du venv
if [ -d ".venv" ]; then
    source ".venv/bin/activate"
elif [ -d "$ROOT_DIR/.venv" ]; then
    source "$ROOT_DIR/.venv/bin/activate"
else
    echo "❌ Erreur: Environnement virtuel (.venv) non trouvé dans $ROOT_DIR"
    exit 1
fi

echo "--- 🚀 LANCEMENT DE VIBRISSE (Mode Unifié) ---"
echo "📂 Dossier : $ROOT_DIR"

# Lancement du Backend (qui sert aussi le Frontend)
"$ROOT_DIR/.venv/bin/python3" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    echo "--- 🛑 ARRÊT DE VIBRISSE ---"
    
    # On tue tout le groupe de processus (le signe moins devant le PID)
    # Cela permet de tuer uvicorn ET ses sous-processus (Ragas, etc.)
    if [ ! -z "$BACKEND_PID" ]; then
        kill -TERM -$BACKEND_PID 2>/dev/null
        # On attend un peu, si c'est toujours là, on force
        sleep 1
        kill -KILL -$BACKEND_PID 2>/dev/null
    fi
    
    echo "--- ✅ ARRÊT COMPLET ---"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Ouvertures selon le mode
if [[ "$ARGS" == *"--tui"* ]]; then
    sleep 3 # On attend que le backend soit prêt
    "$ROOT_DIR/.venv/bin/python3" vibrisse_tui.py
    cleanup
elif [[ "$ARGS" != *"--no-ui"* ]]; then
    sleep 2
    echo "🌍 Ouverture de l'interface Studio : http://localhost:8001"
    open "http://localhost:8001"
fi

wait $BACKEND_PID
