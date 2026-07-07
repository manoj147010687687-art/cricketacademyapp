#!/bin/bash
cd "$(dirname "$0")"

echo "============================================"
echo "  Shree Shyam Cricket Academy - AI Suite Pro"
echo "============================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found. Please install it from: https://python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[1/3] Checking/installing required libraries..."
python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt

echo "[2/3] Libraries are ready."
echo "[3/3] Starting the app... The browser will open automatically."
echo ""

python3 -m streamlit run app.py

read -p "Press Enter to exit..."
