@echo off
title Shree Shyam Cricket Academy - AI Suite Pro
cd /d "%~dp0"

echo ============================================
echo   Shree Shyam Cricket Academy - AI Suite Pro
echo ============================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found on this computer.
    echo Please install Python first: https://python.org
    echo Be sure to tick the "Add Python to PATH" checkbox during installation.
    echo.
    pause
    exit /b
)

echo [1/3] Checking/installing required libraries...
python -m pip install --quiet --disable-pip-version-check -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install libraries. Please check your internet connection.
    pause
    exit /b
)

echo [2/3] Libraries are ready.
echo [3/3] Starting the app... The browser will open automatically.
echo.
echo (Do not close this window while using the app)
echo.

python -m streamlit run app.py

pause
