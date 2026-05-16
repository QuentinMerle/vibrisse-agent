@echo off
TITLE Vibrisse Agent - Windows Launcher

echo --- 🚀 VIBRISSE PRE-FLIGHT (Windows) ---

:: 1. Check Ollama
curl -s http://localhost:11434/api/tags > nul
if %errorlevel% neq 0 (
    echo [WARNING] Ollama is not running. Local models will not work.
)

:: 2. Check Virtual Environment
if not exist ".venv" (
    echo [ERROR] Virtual environment (.venv) not found.
    echo Please run the installer: powershell -ExecutionPolicy Bypass -File install.ps1
    pause
    exit /b 1
)

:: 3. Activation
call .venv\Scripts\activate

:: 4. Update check
if "%1"=="update" (
    echo --- 🔄 UPDATING VIBRISSE AGENT ---
    git stash
    git pull origin main
    git stash pop
    pip install -r requirements.txt
    cd frontend
    npm install && npm run build
    cd ..
    echo ✅ Update complete!
    pause
    exit /b 0
)

:: 5. Launch
echo --- ✅ STARTING VIBRISSE ---
start http://localhost:8001
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
