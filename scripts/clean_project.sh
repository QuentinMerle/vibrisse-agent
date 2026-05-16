#!/bin/bash

# Vibrisse Agent - Project Cleanup Script
# Use this before committing or distributing the project to reduce size.

# Colors
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${PURPLE}🐱 Vibrisse Cleaner - Industrial Grade Polishing${NC}"
echo "------------------------------------------------"

# Function to calculate size
get_size() {
    du -sh "$1" 2>/dev/null | cut -f1
}

# 1. Remove Old Environments
echo -e "${CYAN}Cleaning legacy environments...${NC}"
if [ -d ".venv_old_311" ]; then
    SIZE=$(get_size ".venv_old_311")
    rm -rf .venv_old_311
    echo -e "${GREEN}✓ Removed .venv_old_311 ($SIZE)${NC}"
fi

# 2. Clean Python Cache
echo -e "${CYAN}Cleaning Python bytecode & cache...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.py[co]" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
echo -e "${GREEN}✓ Python cache cleared.${NC}"

# 3. Clean RAG Data (Optional - Keep for local dev, remove for distribution)
read -p "Do you want to clear RAG cache (chroma_db)? [y/N] " clean_rag
if [[ $clean_rag =~ ^[Yy]$ ]]; then
    if [ -d "app/data/chroma_db" ]; then
        SIZE=$(get_size "app/data/chroma_db")
        rm -rf app/data/chroma_db/*
        echo -e "${GREEN}✓ RAG cache cleared ($SIZE).${NC}"
    fi
fi

# 4. Clean Frontend Artifacts
echo -e "${CYAN}Cleaning frontend temporary files...${NC}"
if [ -d "frontend/node_modules/.cache" ]; then
    SIZE=$(get_size "frontend/node_modules/.cache")
    rm -rf frontend/node_modules/.cache
    echo -e "${GREEN}✓ Frontend cache cleared ($SIZE).${NC}"
fi

# 5. OS Garbage
echo -e "${CYAN}Removing OS specific files...${NC}"
find . -type f -name ".DS_Store" -delete
echo -e "${GREEN}✓ OS garbage removed.${NC}"

echo "------------------------------------------------"
echo -e "${PURPLE}Project is now lean and ready!${NC}"
echo -e "Current directory size: $(du -sh . | cut -f1)"
