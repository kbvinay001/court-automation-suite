#!/usr/bin/env pwsh
# ============================================================
#  Court Automation Suite — Windows Startup Script
#  Run from: d:\court-automation-suite
#  Usage:   .\scripts\start-all.ps1
# ============================================================

$Root    = $PSScriptRoot | Split-Path -Parent
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Venv    = Join-Path $Root ".venv\Scripts\activate.ps1"
$Redis   = "C:\redis\redis-server.exe"
$RedisConf = "C:\redis\redis.windows.conf"
$RedisCli  = "C:\redis\redis-cli.exe"

Write-Host ""
Write-Host "   ⚖️  Court Automation Suite — Starting all services" -ForegroundColor Cyan
Write-Host "   ====================================================" -ForegroundColor Cyan

# ─── 1. Redis ────────────────────────────────────────────────
Write-Host ""
Write-Host "   [1/5] Redis..." -ForegroundColor Yellow
$redisPong = & $RedisCli ping 2>$null
if ($redisPong -eq "PONG") {
    Write-Host "         ✅ Redis already running" -ForegroundColor Green
} elseif (Test-Path $Redis) {
    Start-Process -FilePath $Redis -ArgumentList $RedisConf -WindowStyle Hidden
    Start-Sleep -Seconds 2
    $redisPong = & $RedisCli ping 2>$null
    if ($redisPong -eq "PONG") {
        Write-Host "         ✅ Redis started" -ForegroundColor Green
    } else {
        Write-Host "         ❌ Redis failed to start" -ForegroundColor Red
    }
} else {
    Write-Host "         ❌ Redis not found at C:\redis — run setup first" -ForegroundColor Red
}

# ─── 2. MongoDB ──────────────────────────────────────────────
Write-Host ""
Write-Host "   [2/5] MongoDB..." -ForegroundColor Yellow
$mongod = Get-Process mongod -ErrorAction SilentlyContinue
if ($mongod) {
    Write-Host "         ✅ MongoDB already running (PID $($mongod.Id))" -ForegroundColor Green
} else {
    Write-Host "         ⚠️  MongoDB not running. Start it manually or via mongod." -ForegroundColor DarkYellow
}

# ─── 3. Backend (FastAPI) ────────────────────────────────────
Write-Host ""
Write-Host "   [3/5] FastAPI backend on :8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Write-Host 'FastAPI Backend' -ForegroundColor Cyan; " +
    "cd '$Root'; & '$Venv'; cd '$Backend'; " +
    "uvicorn main:app --reload --port 8000"
) -WindowStyle Normal
Start-Sleep -Seconds 3
Write-Host "         ✅ Backend started in new window" -ForegroundColor Green

# ─── 4. Celery Worker ────────────────────────────────────────
Write-Host ""
Write-Host "   [4/5] Celery Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Write-Host 'Celery Worker' -ForegroundColor Magenta; " +
    "cd '$Root'; & '$Venv'; cd '$Backend'; " +
    "celery -A workers.celery_app worker --loglevel=info --concurrency=2 --pool=solo"
) -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "         ✅ Celery worker started in new window" -ForegroundColor Green

# ─── 5. Celery Beat ──────────────────────────────────────────
Write-Host ""
Write-Host "   [5/5] Celery Beat (scheduler)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Write-Host 'Celery Beat Scheduler' -ForegroundColor DarkMagenta; " +
    "cd '$Root'; & '$Venv'; cd '$Backend'; " +
    "celery -A workers.celery_app beat --loglevel=info"
) -WindowStyle Normal
Write-Host "         ✅ Celery beat started in new window" -ForegroundColor Green

# ─── 6. Frontend (Next.js) ───────────────────────────────────
Write-Host ""
$frontendChoice = Read-Host "   Start frontend dev server? (y/n)"
if ($frontendChoice -match "^[Yy]") {
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-Command",
        "Write-Host 'Next.js Frontend' -ForegroundColor Blue; " +
        "cd '$Frontend'; npm run dev"
    ) -WindowStyle Normal
    Write-Host "         ✅ Frontend started on :3000" -ForegroundColor Green
}

# ─── Health Check ─────────────────────────────────────────────
Write-Host ""
Write-Host "   Waiting 5s for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host ""
    Write-Host "   ✅ Health Check:" -ForegroundColor Green
    Write-Host "      Status:   $($health.status)" -ForegroundColor White
    Write-Host "      Database: $($health.database)" -ForegroundColor White
    Write-Host "      Cache:    $($health.cache)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Backend not yet ready — check the backend window" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "   ============================================" -ForegroundColor Cyan
Write-Host "   🌐 Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "   📡 API:       http://localhost:8000" -ForegroundColor White
Write-Host "   📚 API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "   ============================================" -ForegroundColor Cyan
Write-Host ""
