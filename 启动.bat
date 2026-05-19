@echo off
chcp 65001 >nul 2>&1
title VideoForge Pro - AI Universal Video Downloader

echo.
echo ============================================================
echo   VideoForge Pro - AI Universal Video Downloader
echo   Starting All Services...
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo [OK] Python ready

echo.
echo [2/5] Installing dependencies (if needed)...
pip install -q fastapi uvicorn yt-dlp websockets pydantic browser-cookie3 >nul 2>&1
echo [OK] Dependencies ready

echo.
echo [3/5] Starting Backend Server (http://localhost:8976) ...
start "VideoForge-Backend" cmd /k "cd backend && python main.py"

echo.
echo [4/5] Waiting for Backend to be ready...
:wait_backend
timeout /t 1 /nobreak >nul
curl -s http://localhost:8976/api/health >nul 2>&1
if errorlevel 1 (
    echo     ... still waiting for backend ...
    goto wait_backend
)
echo [OK] Backend is online!

echo.
echo [5/5] Starting Frontend Server (http://localhost:5173) ...
start "VideoForge-Frontend" cmd /k "cd frontend && npx vite --port 5173 --host"

echo.
echo ============================================================
echo   ALL SERVICES STARTED!
echo ============================================================
echo.
echo   Frontend URL:  http://localhost:5173
echo   Backend URL:   http://localhost:8976
echo   API Docs:      http://localhost:8976/docs
echo.
echo   Opening browser now...
echo.

start http://localhost:5173

echo.
echo ============================================================
echo   Press any key to STOP all services and close this window
echo ============================================================
pause >nul

taskkill /f /fi "WINDOWTITLE eq VideoForge-Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq VideoForge-Frontend*" >nul 2>&1

echo [DONE] Services stopped. Goodbye!
timeout /t 2 >nul
