@echo off
REM ============================================================================
REM  Court Automation Suite — One-Click Launcher
REM  Double-click this file to start everything and open the website.
REM ============================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================================
echo   COURT AUTOMATION SUITE — STARTING UP
echo ============================================================================
echo.

REM ── Step 0: Locate virtual-env Python ──────────────────────────────────────
set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
set "VENV_UV=%~dp0.venv\Scripts\uvicorn.exe"

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Python virtual environment not found at .venv\
    echo.
    echo   Please run the one-time setup first:
    echo     python -m venv .venv
    echo     .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo [OK] Python venv found

REM ── Step 1: Check Node / npm ───────────────────────────────────────────────
echo.
echo [1/5] Checking Node.js...
where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js / npm found

REM ── Step 2: Check / install frontend dependencies ─────────────────────────
echo.
echo [2/5] Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo   Installing frontend packages (first run only — takes ~1 min)...
    cd frontend
    call npm install --silent
    cd ..
)
echo [OK] Frontend dependencies ready

REM ── Step 3: Docker + MongoDB + Redis ──────────────────────────────────────
echo.
echo [3/5] Checking Docker ...
docker info >nul 2>&1
if errorlevel 1 (
    echo [WARN] Docker is not running — skipping MongoDB/Redis via Docker.
    echo        The backend will still start; it will use in-memory fallbacks.
    echo        To use real persistence, start Docker Desktop and re-run.
    echo.
    goto :START_SERVICES
)
echo [OK] Docker is running

REM MongoDB
docker ps --format "{{.Names}}" | findstr /x "court-mongo" >nul 2>&1
if errorlevel 1 (
    docker ps -a --format "{{.Names}}" | findstr /x "court-mongo" >nul 2>&1
    if errorlevel 1 (
        echo   Creating MongoDB container...
        docker run -d --name court-mongo -p 27017:27017 mongo:7 >nul 2>&1
    ) else (
        docker start court-mongo >nul 2>&1
    )
    echo [OK] MongoDB started on port 27017
) else (
    echo [OK] MongoDB already running
)

REM Redis
docker ps --format "{{.Names}}" | findstr /x "court-redis" >nul 2>&1
if errorlevel 1 (
    docker ps -a --format "{{.Names}}" | findstr /x "court-redis" >nul 2>&1
    if errorlevel 1 (
        echo   Creating Redis container...
        docker run -d --name court-redis -p 6379:6379 redis:7-alpine >nul 2>&1
    ) else (
        docker start court-redis >nul 2>&1
    )
    echo [OK] Redis started on port 6379
) else (
    echo [OK] Redis already running
)

REM Give containers 3 s to initialise
timeout /t 3 /nobreak >nul

:START_SERVICES
REM ── Step 4: Start Backend ──────────────────────────────────────────────────
echo.
echo [4/5] Starting FastAPI backend ...
start "Court Backend ^| http://localhost:8000" cmd /k ^
    "cd /d "%~dp0backend" && "%~dp0.venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

REM Give the backend 5 s to bind its port
timeout /t 5 /nobreak >nul

REM ── Step 5: Start Frontend ─────────────────────────────────────────────────
echo.
echo [5/5] Starting Next.js frontend ...
start "Court Frontend ^| http://localhost:3000" cmd /k ^
    "cd /d "%~dp0frontend" && npm run dev"

REM ── Wait for Next.js to compile then open browser ─────────────────────────
echo.
echo   Waiting for frontend compiler (up to 30 s) ...

set TRIES=0
:WAIT_FRONTEND
set /a TRIES+=1
timeout /t 2 /nobreak >nul
powershell -NoProfile -Command ^
    "try { $r = Invoke-WebRequest http://localhost:3000 -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto :OPEN_BROWSER
if %TRIES% lss 15 goto :WAIT_FRONTEND

echo   (Frontend not responding after 30 s — opening anyway)

:OPEN_BROWSER
start "" "http://localhost:3000"

echo.
echo ============================================================================
echo   ALL SERVICES STARTED
echo ============================================================================
echo.
echo   MongoDB  : localhost:27017  (Docker)
echo   Redis    : localhost:6379   (Docker)
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo   Frontend : http://localhost:3000  ^<-- browser opened
echo.
echo   Close the Backend / Frontend terminal windows to stop those services.
echo   Run  stop-all.bat  to stop Docker containers too.
echo ============================================================================
echo.
pause
