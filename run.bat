@echo off
title UniFlash Tool Launcher
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo An error occurred while launching. Press any key to exit.
    pause
)
