@echo off
title Sherlock OSINT Suite - Windows Installer & Launcher
echo ======================================================================
echo           SHERLOCK PROFESSIONAL OSINT SUITE (WINDOWS BATCH)
echo ======================================================================
echo.

:: Check for Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Fout: Python is niet gedetecteerd op uw systeem.
    echo Please install Python 3.9 or higher and check "Add to PATH" in the installer.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [+] Python gedetecteerd!
echo [+] Systeem controleren op Pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Fout: Pip is niet gedetecteerd of is niet goed geconfigureerd.
    echo Probeer python te installeren met "pip" geselecteerd.
    pause
    exit /b 1
)

echo [+] Installeren/Updaten van benodigde pakketten...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --quiet
python -m pip install customtkinter phonenumbers python-docx reportlab certifi colorama requests pandas openpyxl tomli --quiet

echo.
echo ======================================================================
echo [+] Alles is ingesteld! De Sherlock GUI wordt nu opgestart...
echo ======================================================================
echo.

python -m sherlock_project

pause
