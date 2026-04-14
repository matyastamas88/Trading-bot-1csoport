@echo off
title 1. Csoport Bot - Újraindítás
echo [%date% %time%] Bot újraindítása...

:: Leállítja a futó bot folyamatot
taskkill /FI "WINDOWTITLE eq 1. Csoport Bot - FIX SL" /F >nul 2>&1
timeout /t 3 /nobreak >nul

:: Újraindítja a botot
cd C:\Bot\Csoport1_bot
start "1. Csoport Bot - FIX SL" python main1.py

echo [%date% %time%] Bot újraindítva.
