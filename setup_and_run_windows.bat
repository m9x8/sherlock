@echo off
title Sherlock OSINT Suite - Windows Installer ^& Launcher
echo ======================================================================
echo           SHERLOCK OSINT SUITE (WINDOWS AUTOMATISCHE INSTALLATIE)
echo ======================================================================
echo.

:: Check for Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Fout: Python is niet gedetecteerd op uw systeem.
    echo Installeer Python 3.9 of hoger en vink "Add Python to PATH" aan in het installatieprogramma.
    echo Download link: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [+] Python gedetecteerd!

:: Create local virtual environment if it does not exist
if not exist .venv (
    echo [+] Virtuele omgeving (.venv) aanmaken...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [!] Kon geen virtuele omgeving aanmaken. We proberen direct te installeren...
    )
)

:: Activate the environment
if exist .venv\Scripts\activate.bat (
    echo [+] Virtuele omgeving activeren...
    call .venv\Scripts\activate.bat
)

echo [+] Updaten van pip...
python -m pip install --upgrade pip --quiet

echo [+] Installeren van alle benodigde pakketten...
python -m pip install customtkinter phonenumbers python-docx reportlab certifi colorama requests pandas openpyxl tomli requests-futures stem --quiet

:: Also install local project in editable mode
echo [+] Sherlock-pakket installeren...
python -m pip install -e . --quiet

echo [+] Een snelkoppeling op uw Bureaublad aanmaken...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop = [Environment]::GetFolderPath('Desktop'); $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut(\"$desktop\Sherlock OSINT Suite.lnk\"); $Shortcut.TargetPath = '%~dp0run_gui.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,22'; $Shortcut.Save()"

echo.
echo ======================================================================
echo [+] Installatie succesvol voltooid!
echo [+] Er is een snelkoppeling genaamd 'Sherlock OSINT Suite' op uw Bureaublad geplaatst.
echo [+] De Sherlock GUI wordt nu opgestart...
echo ======================================================================
echo.

python -m sherlock_project --gui

pause
