@echo off
title Bot Frissites - GitHub Pull
color 0B
echo.
echo ============================================================
echo   Trading Bot - Frissites letoltese a GitHubrol
echo ============================================================
echo.

cd /d %~dp0

:: Frissítjük a távoli infókat
echo Kapcsolat ellenorzese...
git fetch --all

:: Megpróbáljuk kitalálni, mi az alapértelmezett ág (main vagy master)
git rev-parse --verify origin/main >nul 2>&1
if %errorlevel% equ 0 (set BRANCH=main) else (set BRANCH=master)

echo.
echo Ellenorzes az '%BRANCH%' agon...
echo.

echo Valtoztatasok listaja:
git log HEAD..origin/%BRANCH% --oneline

echo.
set /p VALASZ="Szeretned letolteni a frissitest? (i/n): "

if /i "%VALASZ%"=="i" (
    echo.
    echo Frissites folyamatban...
    git reset --hard origin/%BRANCH%
    echo.
    echo ============================================================
    echo   KESZ! A frissites sikeres volt.
    echo ============================================================
) else (
    echo.
    echo Frissites megszakitva.
)

echo.
pause