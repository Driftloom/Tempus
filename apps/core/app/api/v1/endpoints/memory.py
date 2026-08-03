"""Memory API endpoints."""


from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.memory import MemoryLayer, MemorySensitivity
from app.database.session import get_db
from app.memory.service import MemoryService
from app.memory.classification.sensitivity_classifier import SensitivityClassifier
from app.memory.classification.layer_classifier import LayerClassifier
from app.auth.dependencies import get_current_user

router = APIRouter()


def get_memory_service() -> MemoryService:
    """Dependency injection for MemoryService."""
    return MemoryService(
        memory_engine=None,  # TODO: Add MemoryEngine when implemented
        sensitivity_classifier=SensitivityClassifier(),
        layer_classifier=LayerClassifier(),
        embedding_service=None  # TODO: Add embedding service
    )


class MemoryIngest(BaseModel):
    """Memory ingestion schema."""
    content: str
    source: str = "user_direct"
    source_ref: str | None = None
    tags: list[str] | None = None


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
    current_user: str = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    memory = await memory_service.ingest(
        db,
        current_user,
        memory_data.content,
        memory_data.source,
        memory_data.source_ref,
        memory_data.tags
    )
    return MemoryResponse.model_validate(memory)


@router.post("/memory/query", response_model=list[MemoryResponse])
async def query_memory(
    query_data: MemoryQuery,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    memory_service: MemoryService = Depends(get_memory_service)
):
    results = await memory_service.query(
        db,
        current_user,
        query_data.query,
        query_data.layer,
        query_data.sensitivity,
        query_data.limit
    )
    return [MemoryResponse.model_validate(m) for m in results]


@router.delete("/memory/{memory_id}")
async def forget_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
    memory_service: MemoryService = Depends(get_memory_service)
):
    deleted = await memory_service.forget(db, memory_id)
    return {"deleted": deleted}
