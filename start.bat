@echo off
echo =========================================
echo  FraudLens AI - Starting All Services
echo =========================================
echo.

REM ── Start FastAPI Backend ──
echo [1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...
start "FraudLens-Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM ── Wait a moment for backend to init ──
timeout /t 3 /nobreak > nul

REM ── Start Vite Frontend ──
echo [2/2] Starting React frontend on http://127.0.0.1:5173 ...
start "FraudLens-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo =========================================
echo  Both services are starting!
echo  Frontend : http://127.0.0.1:5173
echo  Backend  : http://127.0.0.1:8000
echo  API Docs : http://127.0.0.1:8000/docs
echo =========================================
echo.
echo Press any key once done to close this window...
pause > nul
