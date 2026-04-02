@echo off
title Bot Frissites - GitHub Pull
color 0B
echo.
echo ============================================================
echo   Trading Bot - Frissites letoltese a GitHubrol
echo ============================================================
echo.

:: Lepjunk be a bot mappajaba
cd /d %~dp0

echo Ellenorzes: Van-e uj verzio...
git fetch origin main

echo.
echo Valtoztatasok listaja:
git log HEAD..origin/main --oneline

echo.
set /p VALASZ="Szeretned letolteni a frissitest? (i/n): "

if /i "%VALASZ%"=="i" (
    echo.
    echo Frissites letoltese...
    git reset --hard origin/main
    echo.
    echo ============================================================
    echo   KESZ! A frissites sikeres volt.
    echo   Most mar ujra gyarthatod az .exe-t vagy indithatod a botot.
    echo ============================================================
) else (
    echo.
    echo Frissites megszakitva.
)

echo.
pause