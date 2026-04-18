@echo off
REM ============================================================================
REM Court Automation Suite - Start Backend Only
REM ============================================================================
REM Starts only the FastAPI backend server
REM Assumes MongoDB and Redis are already running
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================================
echo   COURT AUTOMATION SUITE - BACKEND ONLY
echo ============================================================================
echo.

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python is not installed or not in PATH
    echo   Please install Python 3.13+ from https://www.python.org
    echo.
    pause
    exit /b 1
)
echo   ✓ Python is installed

REM Check if requirements are installed
echo [2/3] Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo   Installing dependencies...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo   ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo   ✓ All dependencies are installed

REM Optional Docker check (non-blocking warning)
echo [3/3] Checking MongoDB and Redis...
docker ps 2>nul | find "court-mongo" >nul
if errorlevel 1 (
    echo   ⚠ MongoDB NOT running (optional, backend may work without it)
) else (
    echo   ✓ MongoDB is running
)

docker ps 2>nul | find "court-redis" >nul
if errorlevel 1 (
    echo   ⚠ Redis NOT running (optional, caching will be disabled)
) else (
    echo   ✓ Redis is running
)

echo.
echo Starting FastAPI Backend...
echo   Listening on: http://localhost:8000
echo   Docs:         http://localhost:8000/docs
echo   ReDoc:        http://localhost:8000/redoc
echo.
echo Press CTRL+C to stop
echo.

REM Run from root directory (important for module imports)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
