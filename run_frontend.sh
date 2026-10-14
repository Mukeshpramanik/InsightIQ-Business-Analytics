#!/usr/bin/env bash
# Start InsightIQ React Vite Frontend
set -e
cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting InsightIQ Frontend on http://localhost:5173 ..."
npm run dev
