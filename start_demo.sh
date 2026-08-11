#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 was not found. Install it from https://www.python.org/downloads/ and run this script again."
  exit 1
fi

if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py setup_demo

echo ""
echo "ExpenseMate is starting at http://127.0.0.1:8000/"
echo "Admin:  irina@test.com / Password1234"
echo "Member: nicolas@test.com / Password1234"
echo "Press Control+C to stop the server."
echo ""
python manage.py runserver
