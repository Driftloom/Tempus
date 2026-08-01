"""TEMPUS Core FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from structlog import get_logger

from app.api.health import router as health_router
from app.api.v1.endpoints.router import api_router
from app.middleware.rate_limit import rate_limiter
from app.realtime.websocket import websocket_endpoint

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting TEMPUS Core")
    yield
    logger.info("Shutting down TEMPUS Core")


app = FastAPI(
    title="TEMPUS Core",
    description="Enterprise-grade personal intelligence layer",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware - configured via environment variables
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
    # Development fallback
    allowed_origins = ["http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1", tags=["api"])

# Include WebSocket endpoint
app.add_websocket_route("/ws", websocket_endpoint)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "TEMPUS Core",
        "version": "0.1.0",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
