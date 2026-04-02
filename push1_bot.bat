@echo off
set /p msg="Leiras a valtoztatashoz: "
git add -A
git commit -m "%msg%"
:: Előbb megpróbáljuk behúzni a változásokat, hogy ne legyen hiba
git pull origin main --rebase
:: Utána küldjük fel
git push origin main
echo.
echo ========================================
echo   Kesz! Minden frissitve a GitHubon.
echo ========================================
pause