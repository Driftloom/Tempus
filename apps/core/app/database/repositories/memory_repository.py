"""Memory repository."""


from pgvector.sqlalchemy import max_inner_product
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.memory import MemoryEdge, MemoryItem, MemoryLayer, MemorySensitivity
from app.database.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[MemoryItem, dict, dict]):
    """Repository for MemoryItem model."""

    async def query_by_similarity(
        self,
        db: AsyncSession,
        user_id: str,
        query_embedding: list[float],
        layer: MemoryLayer | None = None,
        sensitivity: MemorySensitivity | None = None,
        limit: int = 10
    ) -> list[MemoryItem]:
        """Query memory by vector similarity."""
        query = select(MemoryItem).where(MemoryItem.user_id == user_id)

        if layer:
            query = query.where(MemoryItem.layer == layer)
        if sensitivity:
            query = query.where(MemoryItem.sensitivity == sensitivity)

        # Add similarity ordering
        query = query.order_by(
            max_inner_product(MemoryItem.embedding, query_embedding).desc()
        ).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_layer(
        self,
        db: AsyncSession,
        user_id: str,
        layer: MemoryLayer,
        limit: int = 100
    ) -> list[MemoryItem]:
        """Get memory items by layer."""
        result = await db.execute(
            select(MemoryItem)
            .where(and_(MemoryItem.user_id == user_id, MemoryItem.layer == layer))
            .order_by(MemoryItem.importance_score.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def create_edge(
        self,
        db: AsyncSession,
        from_memory_id: str,
        to_memory_id: str,
        edge_type: str,
        strength: float = 1.0
    ) -> MemoryEdge:
        """Create a memory edge."""
        edge = MemoryEdge(
            from_memory_id=from_memory_id,
            to_memory_id=to_memory_id,
            edge_type=edge_type,
            strength=strength
        )
        db.add(edge)
        await db.commit()
        await db.refresh(edge)
        return edge
