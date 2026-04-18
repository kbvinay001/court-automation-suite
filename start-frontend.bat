@echo off
REM ============================================================================
REM Court Automation Suite - Start Frontend Only
REM ============================================================================
REM Starts only the Next.js frontend server
REM Assumes Backend is already running on http://localhost:8000
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================================
echo   COURT AUTOMATION SUITE - FRONTEND ONLY
echo ============================================================================
echo.

REM Check Node.js
echo [1/3] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Node.js is not installed or not in PATH
    echo   Please install Node.js 20+ from https://nodejs.org
    echo.
    pause
    exit /b 1
)
echo   ✓ Node.js is installed

REM Check if dependencies are installed
echo [2/3] Checking dependencies...
if not exist "frontend\node_modules" (
    echo   node_modules not found, installing...
    cd frontend
    call npm install -q --legacy-peer-deps
    cd ..
    if errorlevel 1 (
        echo   ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo   ✓ All dependencies are installed

REM Check Backend
echo [3/3] Checking Backend...
timeout /t 1 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Backend is not responding (http://localhost:8000)
    echo   Make sure backend is running with: start-backend.bat
    echo.
) else (
    echo   ✓ Backend is running
)

echo.
echo Starting Next.js Frontend...
echo   Opening:      http://localhost:3000
echo.
echo Press CTRL+C to stop
echo.

cd frontend
call npm run dev
