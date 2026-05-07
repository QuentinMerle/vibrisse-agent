#!/bin/bash

# Vibrisse Agent - One-Liner Installer
# Optimized for macOS (Apple Silicon & Intel)

set -e

# Colors
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
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

# 1. Hardware Check
echo -e "${CYAN}--- 🔍 System Check ---${NC}"
OS=$(uname)
if [ "$OS" != "Darwin" ]; then
    echo -e "${RED}Warning: This installer is optimized for macOS. Other systems might require manual setup.${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 is required. Please install it first.${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is required for the Studio UI. Please install it first.${NC}"
    exit 1
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

# 3. Backend Setup
echo -e "${CYAN}--- 🐍 Backend Setup (Python) ---${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Frontend Setup
echo -e "${CYAN}--- 🎨 Frontend Setup (React) ---${NC}"
cd frontend
npm install
cd ..

# 5. Environment Config
if [ ! -f ".env" ]; then
    echo -e "${CYAN}--- ⚙️ Initial Configuration ---${NC}"
    cp .env.example .env
    echo "Default configuration created. You can edit the .env file later."
fi

# 6. Global Alias
echo -e "${CYAN}--- 🚀 Finalizing ---${NC}"
SHELL_RC="$HOME/.zshrc"
if [ ! -f "$SHELL_RC" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if ! grep -q "alias vibrisse=" "$SHELL_RC"; then
    echo "Adding 'vibrisse' alias to $SHELL_RC..."
    echo "alias vibrisse='cd $INSTALL_DIR && ./vibrisse-cli.sh'" >> "$SHELL_RC"
    echo -e "${GREEN}Success! You can now start the agent using the 'vibrisse' command in a new terminal.${NC}"
else
    echo -e "${GREEN}Vibrisse is already in your PATH.${NC}"
fi

echo ""
echo -e "${PURPLE}Installation complete! Restart your terminal and type 'vibrisse' to begin.${NC}"
