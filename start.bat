@echo off
REM Ambient Dx Intelligence — Windows Start Script
REM Usage: start.bat [--cached]

echo.
echo =========================================
echo   Ambient Dx Intelligence
echo   MIT Grand Hack 2026
echo =========================================
echo.

REM Check .env
if not exist ".env" (
    echo ERROR: .env file not found. Copy .env.example to .env and add your API keys.
    exit /b 1
)

REM Setup backend
echo [1/2] Setting up backend...
cd backend
if not exist "venv" (
    echo   Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Start backend in background
echo   Starting FastAPI backend...
start "AmbientDx-Backend" cmd /c "cd /d %~dp0backend && venv\Scripts\activate.bat && python main.py %1"
cd ..

REM Wait for backend
echo   Waiting for backend to start...
timeout /t 3 /nobreak >nul

REM Setup frontend
echo [2/2] Setting up frontend...
cd frontend
if not exist "node_modules" (
    echo   Installing npm dependencies...
    call npm install
)

REM Start frontend
echo   Starting Vite dev server...
start "AmbientDx-Frontend" cmd /c "cd /d %~dp0frontend && npx vite --host"
cd ..

echo.
echo =========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo =========================================
echo.
echo Close the terminal windows to stop servers.
pause
