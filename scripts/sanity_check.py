import sys
import os
import subprocess
import requests
import sqlite3
from pathlib import Path

def check_python():
    print(f"🐍 Python Version: {sys.version.split()[0]}", end=" ")
    if sys.version_info >= (3, 12):
        print("✅")
    else:
        print("❌ (Requires 3.12+)")

def check_ollama():
    print("🦙 Ollama Status:", end=" ")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Running")
        else:
            print("⚠️ Running but error response")
    except:
        print("❌ Not Running")

def check_ripgrep():
    print("🔍 Ripgrep (rg):", end=" ")
    try:
        subprocess.run(["rg", "--version"], capture_output=True, check=True)
        print("✅ Installed")
    except:
        print("❌ Not Found (Recommended for surgical RAG)")

def check_vibrisse_data():
    print("📁 Vibrisse Storage:", end=" ")
    vibrisse_dir = Path.home() / ".vibrisse"
    try:
        vibrisse_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ {vibrisse_dir}")
    except:
        print("❌ Permission Error")

if __name__ == "__main__":
    print("\n--- 🐱 VIBRISSE SANITY CHECK ---")
    check_python()
    check_ollama()
    check_ripgrep()
    check_vibrisse_data()
    print("--------------------------------\n")
