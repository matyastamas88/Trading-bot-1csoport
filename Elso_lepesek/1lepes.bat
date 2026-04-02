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

:: 2. FRISSÍTÉS GITHUBRÓL
echo [+] Frissitesek letoltese a GitHubrol...
git fetch origin main >nul 2>&1
git reset --hard origin/main

:: 3. FÜGGŐSÉGEK TELEPÍTÉSE
echo [+] Szukseges modulok ellenorzese...
pip install -r requirements.txt --quiet

:: 4. INDÍTÁS
echo.
echo ============================================================
echo   Minden kesz! A bot indul...
echo ============================================================
python main1.py
pause