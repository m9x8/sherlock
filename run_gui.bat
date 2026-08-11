@echo off
title Sherlock OSINT Suite Launcher
cd /d "%~dp0"
echo Opstarten van Sherlock OSINT Suite GUI...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python -m sherlock_project --gui
