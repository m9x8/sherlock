@echo off
title No shit Sherlock - Windows Installer ^& Launcher
:: Force shift to script's directory
cd /d "%~dp0"

echo ======================================================================
echo           NO SHIT SHERLOCK (WINDOWS AUTOMATISCHE INSTALLATIE)
echo ======================================================================
echo.

:: Detect Python executable
set "PYTHON_EXE="

:: 1. Try "python"
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
    goto :python_found
)

:: 2. Try "py"
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=py"
    goto :python_found
)

:: 3. Try "python3"
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python3"
    goto :python_found
)

:python_found
if "%PYTHON_EXE%"=="" (
    echo [!] Fout: Python is niet gedetecteerd op uw systeem.
    echo Installeer Python 3.9 of hoger en vink "Add Python to PATH" aan in het installatieprogramma.
    echo Download link: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [+] Python gedetecteerd via commando: %PYTHON_EXE%

:: Create local virtual environment if it does not exist
if exist .venv goto :venv_created

echo [+] Virtuele omgeving (.venv) aanmaken in de huidige map...
%PYTHON_EXE% -m venv .venv
if %errorlevel% neq 0 (
    echo [!] Fout: Kon geen virtuele omgeving aanmaken via '%PYTHON_EXE% -m venv .venv'.
    echo Probeer de installer handmatig uit te voeren als Administrator, of installeer 'venv' module.
    echo.
    pause
    exit /b 1
)

:venv_created
:: Verify virtual environment python exists
if not exist .venv\Scripts\python.exe (
    echo [!] Fout: De virtuele omgeving is aangemaakt, maar .venv\Scripts\python.exe is niet gevonden.
    echo Het lijkt erop dat de installatie is afgebroken of beschadigd.
    echo Verwijder de map '.venv' en start dit script opnieuw.
    echo.
    pause
    exit /b 1
)

echo [+] Virtuele omgeving met succes geverifieerd!

set "VENV_PYTHON=.venv\Scripts\python.exe"

echo [+] Updaten van pip in virtuele omgeving...
%VENV_PYTHON% -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [!] Waarschuwing: Updaten van pip is mislukt. We gaan door met de rest van de installatie...
)

echo [+] Project installeren (editable mode, met alle dependencies uit pyproject.toml)...
%VENV_PYTHON% -m pip install -e .
if %errorlevel% neq 0 (
    echo [!] Fout: Installatie van de lokale Sherlock-project module is mislukt.
    echo/ Controleer uw internetverbinding of proxyinstellingen.
    echo.
    pause
    exit /b 1
)

echo [+] Camoufox browser binaries ophalen...
%VENV_PYTHON% -m camoufox fetch
if %errorlevel% neq 0 (
    echo [!] Waarschuwing: Kon Camoufox browser binaries niet ophalen. Sommige stealth functies werken mogelijk niet.
    echo.
)

echo [+] Een snelkoppeling op uw Bureaublad aanmaken...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop = [Environment]::GetFolderPath('Desktop'); $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut(\"$desktop\No shit Sherlock.lnk\"); $Shortcut.TargetPath = '%~dp0run_gui.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,22'; $Shortcut.Save()" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Waarschuwing: Kon geen snelkoppeling op uw Bureaublad maken.
    echo Dit kan liggen aan uw PowerShell restricties of groepsbeleid.
    echo U kunt de applicatie nog steeds handmatig starten met 'run_gui.bat'.
) else (
    echo [+] Bureaubladsnelkoppeling succesvol aangemaakt!
)

echo.
echo ======================================================================
echo [+] Installatie succesvol voltooid!
echo [+] Er is een snelkoppeling genaamd 'No shit Sherlock' op uw Bureaublad geplaatst.
echo [+] De No shit Sherlock GUI wordt nu opgestart...
echo ======================================================================
echo.

%VENV_PYTHON% -m sherlock_project --gui
if %errorlevel% neq 0 (
    echo [!] Fout: Er is een fout opgetreden tijdens het opstarten van de GUI.
    echo Zie de foutmeldingen hierboven voor details.
    echo.
    pause
)
