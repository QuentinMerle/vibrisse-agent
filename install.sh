#!/bin/bash

# Vibrisse Agent - Swift Installer (Zero-Build Edition)
# Optimized for macOS (Apple Silicon & Intel)
# Enforces Python 3.12

set -e

# Colors
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${PURPLE}"
echo "    _   ___ _          _                "
echo "   | | / (_) |__  _ __(_)___ ___  ___   "
echo "   | |/ /| | '_ \| '__| / __/ __|/ _ \  "
echo "   |   / | | |_) | |  | \__ \__ \  __/  "
echo "   |_|   |_|_.__/|_|  |_|___/___/\___|  "
echo -e "   Vibrisse AI: Small models, Great tools.${NC}"
echo ""

# 1. System Check
echo -e "${CYAN}--- 🔍 System Check ---${NC}"

# Check OS
OS=$(uname)
if [ "$OS" != "Darwin" ]; then
    echo -e "${YELLOW}Warning: This installer is optimized for macOS. Other systems might require manual setup.${NC}"
fi

# Check Python 3.12
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [ "$PY_VER" == "3.12" ]; then
        PYTHON_CMD="python3"
    else
        echo -e "${RED}Error: Python 3.12 is required. Found version $PY_VER.${NC}"
        echo -e "Please install it using: ${CYAN}brew install python@3.12${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Python 3.12 is required but not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3.12 detected.${NC}"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Note: Ollama is not installed. You will need it for local models: https://ollama.com${NC}"
fi

# 2. Setup Directory
INSTALL_DIR="$HOME/.vibrisse"
echo -e "${CYAN}--- 📦 Setup Directory ($INSTALL_DIR) ---${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d ".git" ]; then
    echo "Cloning Vibrisse Agent repository..."
    git clone https://github.com/QuentinMerle/vibrisse-agent.git .
else
    echo "Existing installation found. Updating..."
    git pull
fi

# 3. Backend Setup (Python)
echo -e "${CYAN}--- 🐍 Backend Setup (Python) ---${NC}"
if [ ! -d ".venv" ]; then
    $PYTHON_CMD -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Environment Config (Interactive)
if [ ! -f ".env" ]; then
    echo -e "${CYAN}--- ⚙️ Initial Configuration (Optional) ---${NC}"
    cp .env.example .env
    
    echo -e "Vibrisse works out-of-the-box with Ollama, but you can add Cloud keys now."
    echo -e "(Press Enter to skip any of these)"
    
    # Portabilité sed (macOS vs Linux)
    SED_CMD="sed -i"
    if [ "$OS" == "Darwin" ]; then
        SED_CMD="sed -i ''"
    fi

    read -p "Enter your GROQ API Key: " groq_key
    if [ ! -z "$groq_key" ]; then
        eval $SED_CMD "s/GROQ_API_KEY=.*/GROQ_API_KEY=$groq_key/" .env 2>/dev/null || echo "GROQ_API_KEY=$groq_key" >> .env
    fi

    read -p "Enter your OPENROUTER API Key: " or_key
    if [ ! -z "$or_key" ]; then
        eval $SED_CMD "s/OPENROUTER_API_KEY=.*/OPENROUTER_API_KEY=$or_key/" .env 2>/dev/null || echo "OPENROUTER_API_KEY=$or_key" >> .env
    fi

    read -p "Enter your TAVILY API Key (Web Search): " tav_key
    if [ ! -z "$tav_key" ]; then
        eval $SED_CMD "s/TAVILY_API_KEY=.*/TAVILY_API_KEY=$tav_key/" .env 2>/dev/null || echo "TAVILY_API_KEY=$tav_key" >> .env
    fi
fi

# 5. Global Alias
echo -e "${CYAN}--- 🚀 Finalizing ---${NC}"
SHELL_RC="$HOME/.zshrc"
[ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"

if ! grep -q "alias vibrisse=" "$SHELL_RC"; then
    echo "Adding aliases to $SHELL_RC..."
    echo "alias vibrisse='cd $INSTALL_DIR && ./vibrisse-cli.sh'" >> "$SHELL_RC"
    echo "alias vibrisse-tui='cd $INSTALL_DIR && ./vibrisse-cli.sh --tui'" >> "$SHELL_RC"
    echo -e "${GREEN}Success! Aliases 'vibrisse' and 'vibrisse-tui' added.${NC}"
else
    echo -e "${GREEN}Vibrisse aliases already present.${NC}"
fi

echo ""
echo -e "${PURPLE}Installation complete! Restart your terminal and type:${NC}"
echo -e "  - ${CYAN}vibrisse${NC}         : Open the Web Studio"
echo -e "  - ${CYAN}vibrisse-tui${NC}     : Open the Control Center"
echo -e "  - ${CYAN}vibrisse update${NC}  : Update the agent to the latest version"
