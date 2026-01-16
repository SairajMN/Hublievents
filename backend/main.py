"""
Main FastAPI application entry point for Hublievents Luxury Event Platform.
Production-grade backend with comprehensive security and API layer.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config import settings
from database import create_tables, get_db
from security.middleware import SecurityHeadersMiddleware, CSRFMiddleware
from routes import (
    auth_router,
    # users_router, designs_router,
    # enquiries_router, gallery_router,
    admin_router
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting Hublievents Backend API")

    # Create database tables on startup
    create_tables()

    logger.info("Database tables initialized")

    yield

    logger.info("Shutting down Hublievents Backend API")

# Initialize FastAPI app
app = FastAPI(
    title="Hublievents API",
    description="Production-grade backend for Luxury Event & Shamiyana Customization Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CSRF protection
app.add_middleware(CSRFMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-CSRF-Token",
        "X-Requested-With"
    ],
)

# Trusted hosts middleware (production only)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured logging."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return {
        "error": {
            "code": exc.status_code,
            "message": exc.detail,
            "type": "http_exception"
        }
    }

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions without leaking sensitive information."""
    logger.error(f"Unhandled exception: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return {
        "error": {
            "code": 500,
            "message": "Internal server error",
            "type": "server_error"
        }
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# API v1 routes
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# TODO: Uncomment when routes are implemented
# app.include_router(
#     users_router,
#     prefix="/api/v1/users",
#     tags=["Users"]
# )

# app.include_router(
#     designs_router,
#     prefix="/api/v1/designs",
#     tags=["Designs"]
# )

# app.include_router(
#     enquiries_router,
#     prefix="/api/v1/enquiries",
#     tags=["Enquiries"]
# )

# app.include_router(
#     gallery_router,
#     prefix="/api/v1/gallery",
#     tags=["Gallery"]
# )

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Administration"]
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Hublievents Luxury Event Platform API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.DEBUG else "Disabled in production"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True,
        server_header=False,  # Security: don't expose server info
        date_header=False     # Security: don't expose server time
    )
