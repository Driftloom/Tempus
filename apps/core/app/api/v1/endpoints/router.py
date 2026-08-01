"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, memory, oauth, tasks

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
