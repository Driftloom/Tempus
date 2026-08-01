"""Memory consolidator for OBSESSION engine."""

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.database.models.memory import MemoryItem, MemoryLayer
from app.database.repositories.memory_repository import MemoryRepository

logger = get_logger(__name__)


class MemoryConsolidator:
    """Consolidator for memory items."""

    def __init__(self, memory_repository: MemoryRepository):
        """Initialize memory consolidator."""
        self.memory_repository = memory_repository

    async def consolidate_episodic_to_semantic(
        self,
        db: AsyncSession,
        user_id: str
    ) -> int:
        """Consolidate episodic memories into semantic memories."""
        logger.info("Starting episodic to semantic consolidation", user_id=user_id)

        # Get episodic memories that haven't been referenced recently
        episodic_memories = await self.memory_repository.get_by_layer(
            db, user_id, MemoryLayer.EPISODIC, limit=100
        )

        consolidated_count = 0

        for memory in episodic_memories:
            # Check if memory should be consolidated
            if self._should_consolidate(memory):
                # Create semantic memory from episodic
                semantic_data = {
                    "user_id": user_id,
                    "content": memory.content,
                    "layer": MemoryLayer.SEMANTIC,
                    "sensitivity": memory.sensitivity,
                    "importance_score": memory.importance_score * 0.8,  # Slightly lower importance
                    "embedding": memory.embedding,
                    "source": "consolidation",
                    "source_ref": memory.id,
                    "tags": memory.tags
                }

                await self.memory_repository.create(db, semantic_data)

                # Delete original episodic memory
                await self.memory_repository.delete(db, memory.id)

                consolidated_count += 1

        logger.info("Episodic to semantic consolidation completed", count=consolidated_count)
        return consolidated_count

    async def decay_working_memory(
        self,
        db: AsyncSession,
        user_id: str
    ) -> int:
        """Decay and remove expired working memory items."""
        logger.info("Starting working memory decay", user_id=user_id)

        from datetime import datetime

        # Get working memory items
        working_memories = await self.memory_repository.get_by_layer(
            db, user_id, MemoryLayer.WORKING, limit=100
        )

        decayed_count = 0
        now = datetime.utcnow()

        for memory in working_memories:
            # Check if TTL has expired
            if memory.ttl_at and datetime.fromisoformat(memory.ttl_at) < now:
                await self.memory_repository.delete(db, memory.id)
                decayed_count += 1

        logger.info("Working memory decay completed", count=decayed_count)
        return decayed_count

    def _should_consolidate(self, memory: MemoryItem) -> bool:
        """Determine if memory should be consolidated."""
        # Consolidate if:
        # - High importance
        # - Not recently referenced (would need reference tracking)
        # - Old enough (would need age tracking)

        # For now, use importance as the primary factor
        return memory.importance_score > 0.7
