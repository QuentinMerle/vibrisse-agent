#!/bin/bash

# Vibrisse CLI Launcher - Swift & Robust Edition
# Usage: vibrisse [--no-ui] [--tui]

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Resolve root directory
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
ROOT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd "$ROOT_DIR"

# 0. UPDATE MECHANISM
if [[ "$1" == "update" ]]; then
    echo -e "${CYAN}--- 🔄 UPDATING VIBRISSE AGENT ---${NC}"
    
    echo -e "📦 Pulling latest changes from Git..."
    # On stash les changements locaux potentiels pour éviter les conflits
    git stash || true
    git pull origin main
    git stash pop || true
    
    echo -e "🐍 Updating Python dependencies..."
    if [ -d ".venv" ]; then
        source ".venv/bin/activate"
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo -e "${YELLOW}⚠️ Virtual environment not found. Skipping pip install.${NC}"
    fi
    
    echo -e "🎨 Rebuilding frontend assets..."
    if command -v npm &> /dev/null; then
        cd frontend && npm install && npm run build && cd ..
    else
        echo -e "${YELLOW}⚠️ npm not found. Using existing distribution folder.${NC}"
    fi
    
    echo -e "${GREEN}✅ Update complete! You can now launch Vibrisse.${NC}"
    exit 0
fi

# 1. PRE-FLIGHT CHECKS
echo -e "${CYAN}--- 🚀 VIBRISSE PRE-FLIGHT ---${NC}"

# Check Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: Ollama is not running.${NC}"
    echo -e "Local models will not work. Please start the Ollama application."
fi

# Check Port 8001
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}❌ Error: Port 8001 is already in use.${NC}"
    echo -e "Please close the application using port 8001 and try again."
    exit 1
fi

# Check Frontend Build (for safety)
if [ ! -d "frontend/dist" ]; then
    echo -e "${YELLOW}⚠️  Warning: frontend/dist not found.${NC}"
    echo -e "If you are a developer, run 'npm run build' in the frontend folder."
fi

# 2. ENVIRONMENT SETUP
# Activation du venv
if [ -d ".venv" ]; then
    source ".venv/bin/activate"
else
    echo -e "${RED}❌ Error: Virtual environment (.venv) not found.${NC}"
    echo -e "Please run the installer again: ./install.sh"
    exit 1
fi

# 3. LAUNCH
echo -e "${GREEN}✓ Everything looks good. Starting Vibrisse...${NC}"
echo "📂 Root : $ROOT_DIR"

# Arguments detection
ARGS="$*"
CMD_NAME=$(basename "$0")
if [[ "$CMD_NAME" == "vibrisse-tui" ]]; then
    ARGS="--tui $*"
fi

# Fonction de nettoyage
cleanup() {
    echo -e "\n${CYAN}--- 🛑 SHUTTING DOWN VIBRISSE ---${NC}"
    # On tue tous les processus fils (uvicorn, etc.)
    pkill -P $$ 2>/dev/null || true
    echo -e "${GREEN}--- ✅ DONE ---${NC}"
    exit 0
}

# On capture Ctrl+C
trap cleanup SIGINT SIGTERM

# UI Openings
if [[ "$ARGS" == *"--tui"* ]]; then
    (sleep 3 && python3 vibrisse_tui.py && cleanup) &
elif [[ "$ARGS" != *"--no-ui"* ]]; then
    (sleep 2 && echo -e "${CYAN}🌍 Opening Studio UI : http://localhost:8001${NC}" && open "http://localhost:8001") &
fi

# Lancement du Backend en PREMIER plan pour capter le signal directement
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
