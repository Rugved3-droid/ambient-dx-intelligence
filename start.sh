#!/bin/bash
# Ambient Dx Intelligence — Start Script
# Usage: ./start.sh [--cached]

set -e

CACHED_FLAG=""
if [ "$1" = "--cached" ]; then
    CACHED_FLAG="--cached"
    echo "Running in CACHED mode (pre-computed LLM responses)"
fi

echo ""
echo "========================================="
echo "  Ambient Dx Intelligence"
echo "  MIT Grand Hack 2026"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and add your API keys."
    exit 1
fi

# Start backend
echo "[1/2] Starting backend (FastAPI)..."
cd backend
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || true
fi
python main.py $CACHED_FLAG &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "  Waiting for backend..."
sleep 3

# Start frontend
echo "[2/2] Starting frontend (Vite + React)..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "  Installing npm dependencies..."
    npm install
fi
npx vite --host &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================="
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
