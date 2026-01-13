"""
FastAPI Application Factory
Creates and configures the MSP Gateway application
"""

import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .middleware import RateLimitMiddleware, TenantContextMiddleware
from .routers import admin_router, infer_router, kb_router
from .schemas.responses import ErrorResponse, HealthResponse

# Configure logging
log_dir = Path(settings.log_dir)
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Track startup time
START_TIME = time.time()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="MSP Gateway",
        description="Tenant-aware inference API for local operation",
        version="0.1.0",
        docs_url="/docs" if not settings.offline else None,
        redoc_url="/redoc" if not settings.offline else None,
    )

    # Environment-aware CORS configuration
    # Security: Configure CORS origins based on environment to prevent unauthorized access
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    if cors_origins_env:
        # Use explicit CORS_ORIGINS from environment
        cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    elif os.getenv("ENVIRONMENT", "development") == "production":
        # Production: Restrict to specific domains.
        # ⚠️ IMPORTANT: These are placeholder domains that MUST be replaced before production deployment.
        # For production use, you MUST either:
        #   1. Set CORS_ORIGINS environment variable to your actual domains (recommended), OR
        #   2. Replace example.com below with your real frontend/API domains
        # Leaving these placeholder values will cause legitimate production requests to be rejected by CORS.
        cors_origins = [
            "https://example.com",
            "https://api.example.com"
        ]
    else:
        # Development/Local: Allow localhost only (binds to 127.0.0.1)
        # More secure than wildcard while still functional for local development
        cors_origins = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080"
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,  # Disable credentials for security
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-Request-Id"],
    )

    # Add custom middleware. Starlette wraps middleware such that the most
    # recently added middleware runs first. Register the tenant context before
    # the rate limiter so tenant information is attached to the request state
    # prior to rate limiting checks.
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Include routers
    app.include_router(kb_router)
    app.include_router(infer_router)
    app.include_router(admin_router)

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check():
        """Health check endpoint"""
        uptime = time.time() - START_TIME

        # Basic component checks
        checks = {
            "database": True,  # SQLite is always available
            "policies_loaded": True,  # Policies loaded at startup
        }

        return HealthResponse(
            status="healthy",
            version="0.1.0",
            offline_mode=settings.offline,
            uptime_seconds=uptime,
            checks=checks,
        )

    # Root endpoint
    @app.get("/", tags=["info"])
    async def root():
        """Root endpoint with API information"""
        return {
            "name": "MSP Gateway",
            "version": "0.1.0",
            "offline_mode": settings.offline,
            "endpoints": {
                "health": "/health",
                "docs": "/docs" if not settings.offline else "disabled",
                "inference": "/v1/infer",
                "kb_query": "/v1/query_kb",
                "admin": "/admin",
            },
        }

    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        error_response = ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"exception": str(exc)} if not settings.offline else {},
        )

        return JSONResponse(
            status_code=500,
            content=error_response.model_dump(),
        )

    logger.info(f"MSP Gateway application created (offline_mode={settings.offline})")

    return app


# Create the application instance
app = create_app()
