@echo off
title GitHub - Biztonsagos Feltoltes
color 0B
cd /d C:\Telegram\csoport1_bot

echo ============================================================
echo   GitHub Frissites (Minden valtozas mentese)
echo ============================================================

set /p KOMMENT="Mi valtozott? (Leiras): "

if "%KOMMENT%"=="" (
    echo HIBA: Kerlek adj meg egy rovid leirast!
    pause
    exit
)

echo [+] Valtozasok osszegyujtese...
git add -A

echo [+] Helyi mentes elkeszitese...
git commit -m "%KOMMENT%"

echo [+] Szinkronizalas a GitHub-bal (Pull)...
git pull origin master --no-rebase --allow-unrelated-histories

echo [+] Vegleges feltoltes (Push)...
git push origin master

echo.
echo ============================================================
echo   KESZ! Minden frissitve a GitHubon.
echo ============================================================
pause