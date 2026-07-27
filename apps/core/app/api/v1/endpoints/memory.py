"""Memory API endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database.session import get_db
from app.memory.service import MemoryService
from app.database.models.memory import MemoryLayer, MemorySensitivity

router = APIRouter()


class MemoryIngest(BaseModel):
    """Memory ingestion schema."""
    content: str
    source: str = "user_direct"
    source_ref: str | None = None
    tags: List[str] | None = None


class MemoryQuery(BaseModel):
    """Memory query schema."""
    query: str
    layer: MemoryLayer | None = None
    sensitivity: MemorySensitivity | None = None
    limit: int = 10


class MemoryResponse(BaseModel):
    """Memory response schema."""
    id: str
    content: str
    layer: MemoryLayer
    sensitivity: MemorySensitivity
    importance_score: float
    created_at: str

    class Config:
        from_attributes = True


@router.post("/memory", response_model=MemoryResponse)
async def ingest_memory(
    memory_data: MemoryIngest,
    db: AsyncSession = Depends(get_db),
    user_id: str = "default-user"
):
    """Ingest content into memory."""
    memory_service = MemoryService(None, None, None, None)
    memory = await memory_service.ingest(
        db,
        user_id,
        memory_data.content,
        memory_data.source,
        memory_data.source_ref,
        memory_data.tags
    )
    return MemoryResponse.model_validate(memory)


@router.post("/memory/query", response_model=List[MemoryResponse])
async def query_memory(
    query_data: MemoryQuery,
    db: AsyncSession = Depends(get_db),
    user_id: str = "default-user"
):
    """Query memory for relevant information."""
    memory_service = MemoryService(None, None, None, None)
    results = await memory_service.query(
        db,
        user_id,
        query_data.query,
        query_data.layer,
        query_data.sensitivity,
        query_data.limit
    )
    return [MemoryResponse.model_validate(m) for m in results]


@router.delete("/memory/{memory_id}")
async def forget_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Forget a specific memory item."""
    memory_service = MemoryService(None, None, None, None)
    deleted = await memory_service.forget(db, memory_id)
    return {"deleted": deleted}
