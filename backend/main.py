"""
Court Automation Suite - Backend Application
FastAPI application for court case tracking, cause list monitoring, and analytics.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from utils.database import init_db, close_db
from utils.cache import init_cache, close_cache
from utils.security import RateLimitMiddleware, SecurityHeadersMiddleware
from api.routes.court_scraper import router as scraper_router
from api.routes.causelist import router as causelist_router
from api.routes.analytics import router as analytics_router
from api.routes.auth import router as auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    logger.info("🚀 Starting Court Automation Suite...")
    await init_db()
    await init_cache()
    logger.info("✅ Database and cache initialized")
    yield
    logger.info("🛑 Shutting down Court Automation Suite...")
    await close_db()
    await close_cache()
    logger.info("✅ Connections closed")


app = FastAPI(
    title="Court Automation Suite API",
    description="API for Indian court case tracking, cause list monitoring, and legal analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://court-automation.example.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(scraper_router, prefix="/api/v1/scraper", tags=["Court Scraper"])
app.include_router(causelist_router, prefix="/api/v1/causelist", tags=["Cause List"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "running",
        "service": "Court Automation Suite API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    from utils.database import get_db
    from utils.cache import get_cache

    db_status = "connected" if get_db() is not None else "disconnected"
    cache_status = "connected" if get_cache() is not None else "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "cache": cache_status,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # nosec B104 — dev runner only
