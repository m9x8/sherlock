@echo off
title Sherlock OSINT Suite Launcher
:: Force shift to script's directory
cd /d "%~dp0"

echo ======================================================================
echo                 SHERLOCK OSINT SUITE - GUI LAUNCHER
echo ======================================================================
echo.

:: Check if virtual environment exists
if exist .venv\Scripts\python.exe goto :venv_exists

echo [!] Fout: De virtuele omgeving (.venv) is niet gevonden of incompleet!
echo Dit betekent dat de installatie nog niet is uitgevoerd of is mislukt.
echo.
set /p "choice=[?] Wilt u de automatische Windows installatie NU starten? (J/N): "
if /i "%choice%"=="J" (
    echo.
    echo [+] Starten van setup_and_run_windows.bat...
    echo.
    call setup_and_run_windows.bat
    exit /b %errorlevel%
) else (
    echo.
    echo [!] Actie geannuleerd. Voer eerst 'setup_and_run_windows.bat' uit om de app te installeren.
    echo.
    pause
    exit /b 1
)

:venv_exists
echo [+] Virtuele omgeving gevonden!
echo [+] Opstarten van Sherlock OSINT Suite GUI...
echo.

.venv\Scripts\python.exe -m sherlock_project --gui
if %errorlevel% neq 0 (
    echo.
    echo [!] Fout: De GUI is onverwachts afgesloten met een foutcode (%errorlevel%).
    echo Dit kan liggen aan een missende library of een runtime-fout.
    echo Probeer eventueel 'setup_and_run_windows.bat' opnieuw te starten om alles te herstellen.
    echo.
    pause
    exit /b %errorlevel%
)
