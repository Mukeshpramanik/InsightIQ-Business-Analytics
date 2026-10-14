#!/usr/bin/env bash
# Start InsightIQ FastAPI Backend Server
set -e
cd "$(dirname "$0")"

if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/venv
    backend/venv/bin/pip install -r backend/requirements.txt
fi

echo "Starting InsightIQ Backend on http://127.0.0.1:8000 ..."
PYTHONPATH=. backend/venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
