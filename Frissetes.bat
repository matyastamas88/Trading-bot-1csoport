@echo off
title Bot Frissites - GitHub Pull
color 0B
echo.
echo ============================================================
echo   Trading Bot - Frissites letoltese a GitHubrol
echo ============================================================
echo.

set BOT_DIR=C:\Bot\Csoport1_bot

if not exist "%BOT_DIR%\.git" (
    echo HIBA: Nem talalhato a bot mappa: %BOT_DIR%
    pause
    exit /b 1
)

echo Ellenorzes: Van-e uj verzio...
git -C "%BOT_DIR%" fetch origin >nul 2>&1

:: Ág meghatározása
for /f "tokens=*" %%i in ('git -C "%BOT_DIR%" symbolic-ref --short HEAD 2^>nul') do set BRANCH=%%i
if "%BRANCH%"=="" set BRANCH=master

echo Aktiv ag: %BRANCH%
echo.
echo Valtoztatasok listaja:
git -C "%BOT_DIR%" log HEAD..origin/%BRANCH% --oneline

echo.
set /p VALASZ="Szeretned letolteni a frissitest? (i/n): "

if /i "%VALASZ%"=="i" (
    echo.
    echo Frissites letoltese...
    git -C "%BOT_DIR%" pull origin %BRANCH%
    echo.
    echo ============================================================
    echo   KESZ! Inditsd ujra a botot!
    echo ============================================================
) else (
    echo Frissites megszakitva.
)

echo.
pause
