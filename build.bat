@echo off
title Building UniFlash Tool Executable
echo ========================================================
echo  UniFlash Tool v1.0 — PyInstaller Standalone Compiler
echo  Developed by Tejas Jadhav (@vik4sx)
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking dependencies...
python -m pip install customtkinter Pillow pyinstaller --quiet

echo [2/3] Compiling standalone UniFlashTool.exe (this may take 1-2 minutes)...
pyinstaller --noconfirm --clean --onefile --windowed ^
            --icon="assets/icons/app.ico" ^
            --add-data "tools;tools" ^
            --add-data "assets;assets" ^
            --add-data "config;config" ^
            --add-data "brands;brands" ^
            --add-data "core;core" ^
            --add-data "ui;ui" ^
            --collect-all customtkinter ^
            --collect-all PIL ^
            --name "UniFlashTool" ^
            main.py

echo.
if exist "dist\UniFlashTool.exe" (
    echo ========================================================
    echo  BUILD SUCCESSFUL!
    echo  Standalone EXE ready at: dist\UniFlashTool.exe
    echo ========================================================
) else (
    echo [ERROR] Build failed. Check terminal output above.
)
pause
