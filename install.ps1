# Vibrisse Agent - Windows Installer
# Optimized for Windows 10/11
# Enforces Python 3.12

$ErrorActionPreference = "Stop"

# Colors
$PURPLE = "`e[0;35m"
$CYAN = "`e[0;36m"
$GREEN = "`e[0;32m"
$YELLOW = "`e[0;33m"
$RED = "`e[0;31m"
$NC = "`e[0m"

Write-Host "${PURPLE}"
Write-Host "    _   ___ _          _                "
Write-Host "   | | / (_) |__  _ __(_)___ ___  ___   "
Write-Host "   | |/ /| | '_ \| '__| / __/ __|/ _ \  "
Write-Host "   |   / | | |_) | |  | \__ \__ \  __/  "
Write-Host "   |_|   |_|_.__/|_|  |_|___/___/\___|  "
Write-Host "   Vibrisse AI: Small models, Great tools.${NC}"
Write-Host ""

# 1. System Check
Write-Host "${CYAN}--- 🔍 System Check ---${NC}"

# Check Python 3.12
$python312 = Get-Command python3.12 -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue

if ($python312) {
    $PYTHON_CMD = "python3.12"
} elseif ($python) {
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ($version -eq "3.12") {
        $PYTHON_CMD = "python"
    } else {
        Write-Host "${RED}Error: Python 3.12 is required. Found version $version.${NC}"
        Write-Host "Please install it from https://www.python.org/downloads/"
        exit 1
    }
} else {
    Write-Host "${RED}Error: Python 3.12 is required but not found.${NC}"
    exit 1
}
Write-Host "${GREEN}✓ Python 3.12 detected.${NC}"

# Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "${RED}Error: Git is required but not found.${NC}"
    exit 1
}

# 2. Setup Directory
$INSTALL_DIR = Join-Path $HOME ".vibrisse"
Write-Host "${CYAN}--- 📦 Setup Directory ($INSTALL_DIR) ---${NC}"
if (-not (Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Force -Path $INSTALL_DIR
}
Set-Location $INSTALL_DIR

if (-not (Test-Path ".git")) {
    Write-Host "Cloning Vibrisse Agent repository..."
    git clone https://github.com/QuentinMerle/vibrisse-agent.git .
} else {
    Write-Host "Existing installation found. Updating..."
    git pull
}

# 3. Backend Setup (Python)
Write-Host "${CYAN}--- 🐍 Backend Setup (Python) ---${NC}"
if (-not (Test-Path ".venv")) {
    Invoke-Expression "$PYTHON_CMD -m venv .venv"
}
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Environment Config
if (-not (Test-Path ".env")) {
    Write-Host "${CYAN}--- ⚙️ Initial Configuration (Optional) ---${NC}"
    Copy-Item ".env.example" ".env"
    
    Write-Host "Vibrisse works out-of-the-box with Ollama, but you can add Cloud keys now."
    $groq_key = Read-Host "Enter your GROQ API Key (Enter to skip)"
    if ($groq_key) {
        (Get-Content .env) -replace 'GROQ_API_KEY=.*', "GROQ_API_KEY=$groq_key" | Set-Content .env
    }

    $or_key = Read-Host "Enter your OPENROUTER API Key (Enter to skip)"
    if ($or_key) {
        (Get-Content .env) -replace 'OPENROUTER_API_KEY=.*', "OPENROUTER_API_KEY=$or_key" | Set-Content .env
    }

    $tav_key = Read-Host "Enter your TAVILY API Key (Enter to skip)"
    if ($tav_key) {
        (Get-Content .env) -replace 'TAVILY_API_KEY=.*', "TAVILY_API_KEY=$tav_key" | Set-Content .env
    }
}

# 5. Finalizing
Write-Host ""
Write-Host "${PURPLE}Installation complete!${NC}"
Write-Host "To launch Vibrisse, run:"
Write-Host "  ${CYAN}.\vibrisse.bat${NC}"
Write-Host ""
pause
