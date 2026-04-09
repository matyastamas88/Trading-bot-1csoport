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
    echo Letoltes folyamatban... (1-2 perc)
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe' -OutFile '%TEMP%\python_installer.exe'}"
    if %errorlevel% neq 0 (
        echo HIBA: Python letoltes sikertelen! Ellenorizd az internetkapcsolatot.
        pause
        exit /b 1
    )
    start /wait "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%TEMP%\python_installer.exe"
    set "PATH=%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts"
    echo [+] Python sikeresen telepitve! Kerlek inditsd ujra ezt a fajlt.
    pause
    exit /b 0
)

:: Bot mappa (1 szinttel feljebb mint ez a bat fajl)
set BOT_DIR=%~dp0..

:: 2. FRISSÍTÉS GITHUBRÓL
echo [+] Frissitesek letoltese a GitHubrol...
git -C "%BOT_DIR%" fetch origin >nul 2>&1
git -C "%BOT_DIR%" pull origin master
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