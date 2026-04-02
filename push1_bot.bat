@echo off
title GitHub Frissites Feltoltes
color 0A
echo.
echo ============================================================
echo   GitHub - Valtoztatások feltöltése
echo ============================================================
echo.

:: ITT JAVÍTSD KI AZ ÚTVONALAT:
cd /d C:\Telegram\csoport1_bot

echo Mi változott? (ez lesz a commit üzenet)
echo Pl: "SL javítás", "Új TP szint", "Config módosítás"
echo.
set /p KOMMENT="Leírás: "

if "%KOMMENT%"=="" (
    echo HIBA: Nem adtál meg leírást!
    pause
    exit /b 1
)

echo.
echo Feltöltés folyamatban...
git add .
git commit -m "%KOMMENT%"
git push

echo.
echo ============================================================
echo   Kész! A változtatások felkerültek GitHubra.
echo ============================================================
echo.
pause