#!/bin/bash
# Ambient Dx Intelligence — Start Script
# Usage: ./start.sh [--cached] [--iris]

set -e

BACKEND_FLAGS=""
if [ "$1" = "--cached" ]; then
    BACKEND_FLAGS="--cached"
    echo "Running in CACHED mode (pre-computed LLM responses)"
elif [ "$1" = "--iris" ]; then
    BACKEND_FLAGS="--iris"
    echo "Running in IRIS mode (InterSystems IRIS retrieval backend)"
    if ! docker ps | grep -q iris; then
        echo "  Starting IRIS container..."
        docker compose up -d
        echo "  Waiting for IRIS to initialize..."
        sleep 10
    fi
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
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "  Using active conda env: $CONDA_DEFAULT_ENV"
elif [ -d "venv" ] || [ -d ".venv" ]; then
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || true
else
    echo "  Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
python main.py $BACKEND_FLAGS &
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
if [ "$BACKEND_FLAGS" = "--iris" ]; then
echo "  IRIS Mgmt: http://localhost:52773  (demo/demo)"
fi
echo "========================================="
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
