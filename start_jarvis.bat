@echo off
TITLE FRIDAY Autonomous AI Assistant
COLOR 0A

echo ===================================================
echo             F R I D A Y   V 5 . 0
echo       Autonomous Desktop AI Assistant
echo ===================================================
echo.

set PYTHON_EXE=venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo [1/3] Starting FRIDAY FastAPI Backend Server...
start "FRIDAY Backend" cmd /k "cd /d %~dp0 && %PYTHON_EXE% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Starting FRIDAY Futuristic HUD Frontend...
start "FRIDAY Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo [3/3] Waiting for servers to initialize...
timeout /t 4 >nul

echo [SYSTEM] Opening FRIDAY HUD Interface...
start http://localhost:5173

echo.
echo ===================================================
echo  FRIDAY is now running!
echo  Backend:  http://127.0.0.1:8000
echo  API Docs: http://127.0.0.1:8000/docs
echo  Frontend: http://localhost:5173
echo ===================================================
echo.
pause
