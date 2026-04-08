@echo off
setlocal enabledelayedexpansion
title Trading Bot - Automata Indito
color 0B

echo ============================================================
echo   Trading Bot - Rendszerellenorzes es Inditas
echo ============================================================

:: 1. PYTHON ELLENŐRZÉSE
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python nem talalhato. Telepites...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' -OutFile 'python_installer.exe'"
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del python_installer.exe
    echo [+] Python telepitve! Kerlek inditsd ujra ezt a fajlt.
    pause
    exit
)

:: Bot mappa (1 szinttel feljebb mint ez a bat fajl)
set BOT_DIR=%~dp0..

:: 2. FRISSÍTÉS GITHUBRÓL
echo [+] Frissitesek letoltese a GitHubrol...
git -C "%BOT_DIR%" fetch origin main >nul 2>&1
git -C "%BOT_DIR%" pull origin main
echo [+] Frissites kesz!

:: 3. FÜGGŐSÉGEK TELEPÍTÉSE
echo [+] Szukseges modulok ellenorzese...
cd /d "%BOT_DIR%"
pip install telethon python-telegram-bot MetaTrader5 python-dotenv --quiet

:: 4. INDÍTÁS
echo.
echo ============================================================
echo   Minden kesz! A bot indul...
echo ============================================================
cd /d "%BOT_DIR%"
python main1.py
pause