"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str


@router.get("/live", response_model=HealthResponse)
async def liveness():
    """Liveness probe."""
    from datetime import datetime

    return HealthResponse(
        status="alive",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness():
    """Readiness probe."""
    from datetime import datetime

    return HealthResponse(
        status="ready",
        timestamp=datetime.utcnow().isoformat(),
    )
