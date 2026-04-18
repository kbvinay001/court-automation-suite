@echo off
REM ============================================================================
REM Court Automation Suite - Stop All Services
REM ============================================================================
REM This batch file stops all running Docker containers and services
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo   COURT AUTOMATION SUITE - SHUTDOWN
echo ============================================================================
echo.

echo [1/2] Stopping Docker containers...

REM Stop MongoDB
docker ps | find "court-mongo" >nul
if not errorlevel 1 (
    echo   Stopping MongoDB...
    docker stop court-mongo >nul 2>&1
    echo   ✓ MongoDB stopped
)

REM Stop Redis
docker ps | find "court-redis" >nul
if not errorlevel 1 (
    echo   Stopping Redis...
    docker stop court-redis >nul 2>&1
    echo   ✓ Redis stopped
)

echo.
echo [2/2] Cleaning up processes...
echo   Closing terminal windows...
echo.

REM Kill any node processes (Next.js)
taskkill /F /IM node.exe >nul 2>&1

REM Kill any Python processes (FastAPI)
taskkill /F /IM python.exe >nul 2>&1

echo.
echo ============================================================================
echo   ✓ ALL SERVICES STOPPED
echo ============================================================================
echo.
echo   Optional commands:
echo   - Remove containers: docker rm court-mongo court-redis
echo   - View container logs: docker logs court-mongo
echo                         docker logs court-redis
echo.
pause
