@echo off
set /p msg="Mi valtozott? "
:: A -A kapcsoló mindent eszrevesz: ujat, toroltet, modositottat
git add -A
git commit -m "%msg%"
git push origin main
echo.
echo =========================================
echo   Sikeresen feltoltve es szinkronizalva!
echo =========================================
pause