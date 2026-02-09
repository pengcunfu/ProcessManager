@echo off
cd /d "%~dp0"

fltmc >nul 2>&1
if %errorLevel% == 0 (
    python main.py
) else (
    powershell Start-Process "%~f0" -Verb RunAs
)
