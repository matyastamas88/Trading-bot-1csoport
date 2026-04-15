@echo off
title 1. Csoport Bot - FIX SL
cd C:\Bot\Csoport1_bot

:: Leállítja a futó bot folyamatot
taskkill /FI "WINDOWTITLE eq 1. Csoport Bot - FIX SL" /F >nul 2>&1

:: Várunk hogy teljesen leálljon és a session fájl felszabaduljon
timeout /t 15 /nobreak >nul

:: Újraindítja a botot (ugyanebben az ablakban)
python main1.py
