#!/usr/bin/env bash
# SmartFarm AI — one-command launcher (macOS / Linux)
set -e

cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
  echo "[1/3] Creating virtual environment..."
  python3 -m venv venv
fi

echo "[2/3] Activating virtual environment..."
source venv/bin/activate

echo "[3/3] Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "============================================"
echo " Open your browser at: http://127.0.0.1:5000"
echo " Press Ctrl+C to stop the server."
echo "============================================"
echo ""

python app.py
