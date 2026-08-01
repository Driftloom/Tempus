"""Memory service for OBSESSION memory engine."""


from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.database.models.memory import MemoryItem, MemoryLayer, MemorySensitivity
from app.database.repositories.memory_repository import MemoryRepository
from app.memory.classification.layer_classifier import LayerClassifier
from app.memory.classification.sensitivity_classifier import SensitivityClassifier
from app.memory.embedding.embedding_generator import EmbeddingGenerator

logger = get_logger(__name__)


class MemoryService:
    """Service for managing memory operations."""

    def __init__(
        self,
        memory_repository: MemoryRepository,
        layer_classifier: LayerClassifier,
        sensitivity_classifier: SensitivityClassifier,
        embedding_generator: EmbeddingGenerator
    ):
        """Initialize memory service."""
        self.memory_repository = memory_repository
        self.layer_classifier = layer_classifier
        self.sensitivity_classifier = sensitivity_classifier
        self.embedding_generator = embedding_generator

    async def ingest(
        self,
        db: AsyncSession,
        user_id: str,
        content: str,
        source: str = "user_direct",
        source_ref: str | None = None,
        tags: list[str] | None = None,
        provenance: str | None = None
    ) -> MemoryItem:
        """Ingest content into memory."""
        logger.info("Ingesting memory", user_id=user_id, source=source, provenance=provenance)

        # Classify layer and sensitivity
        layer = self.layer_classifier.classify(content, source)
        sensitivity = self.sensitivity_classifier.classify(content, source)

        # Generate embedding
        embedding = await self.embedding_generator.generate(content)

        # Calculate importance score
        importance_score = self._calculate_importance(content, layer, sensitivity)

        # Set TTL for working memory
        ttl_at = self._calculate_ttl(layer) if layer == MemoryLayer.WORKING else None

        # Determine provenance if not provided
        if not provenance:
            provenance = self._determine_provenance(source, source_ref)

        # Create memory item
        memory_data = {
            "user_id": user_id,
            "content": content,
            "layer": layer,
            "sensitivity": sensitivity,
            "importance_score": importance_score,
            "embedding": embedding,
            "source": source,
            "source_ref": source_ref,
            "provenance": provenance,
            "tags": tags,
            "ttl_at": ttl_at
        }

        memory = await self.memory_repository.create(db, memory_data)
        logger.info("Memory ingested", memory_id=memory.id, layer=layer, sensitivity=sensitivity)

        return memory

    async def query(
        self,
        db: AsyncSession,
        user_id: str,
        query: str,
        layer: MemoryLayer | None = None,
        sensitivity: MemorySensitivity | None = None,
        limit: int = 10
    ) -> list[MemoryItem]:
        """Query memory for relevant information."""
        logger.info("Querying memory", user_id=user_id, query=query)

        # Generate query embedding
        query_embedding = await self.embedding_generator.generate(query)

        # Query by similarity
        results = await self.memory_repository.query_by_similarity(
            db,
            user_id=user_id,
            query_embedding=query_embedding,
            layer=layer,
            sensitivity=sensitivity,
            limit=limit
        )

        logger.info("Memory query completed", results_count=len(results))
        return results

    async def forget(
        self,
        db: AsyncSession,
        memory_id: str
    ) -> bool:
        """Forget a specific memory item."""
        logger.info("Forgetting memory", memory_id=memory_id)

        deleted = await self.memory_repository.delete(db, memory_id)
        if deleted:
            logger.info("Memory forgotten", memory_id=memory_id)
        else:
            logger.warning("Memory not found for forgetting", memory_id=memory_id)

        return deleted is not None

    async def forget_by_filter(
        self,
        db: AsyncSession,
        user_id: str,
        layer: MemoryLayer | None = None,
        sensitivity: MemorySensitivity | None = None,
        tags: list[str] | None = None
    ) -> int:
        """Forget memories matching filters."""
        logger.info("Forgetting memories by filter", user_id=user_id, layer=layer)

        # Get memories matching filters
        memories = await self.memory_repository.get_by_layer(db, user_id, layer or MemoryLayer.WORKING)

        # Apply additional filters
        if sensitivity:
            memories = [m for m in memories if m.sensitivity == sensitivity]
        if tags:
            memories = [m for m in memories if any(tag in (m.tags or []) for tag in tags)]

        # Delete memories
        deleted_count = 0
        for memory in memories:
            if await self.memory_repository.delete(db, memory.id):
                deleted_count += 1

        logger.info("Memories forgotten", count=deleted_count)
        return deleted_count

    def _calculate_importance(
        self,
        content: str,
        layer: MemoryLayer,
        sensitivity: MemorySensitivity
    ) -> float:
        """Calculate importance score for memory."""
        # Base score
        score = 0.5

        # Layer adjustments
        if layer == MemoryLayer.SEMANTIC:
            score += 0.3
        elif layer == MemoryLayer.PROCEDURAL:
            score += 0.2
        elif layer == MemoryLayer.EPISODIC:
            score += 0.1

        # Sensitivity adjustments
        if sensitivity == MemorySensitivity.HIGH:
            score += 0.2
        elif sensitivity == MemorySensitivity.MEDIUM:
            score += 0.1

        # Content length (longer content often more important)
        if len(content) > 100:
            score += 0.1

        return min(score, 1.0)

    def _calculate_ttl(self, layer: MemoryLayer) -> str | None:
        """Calculate TTL for memory based on layer."""
        if layer == MemoryLayer.WORKING:
            # Working memory expires after 1 hour
            from datetime import datetime, timedelta
            return (datetime.utcnow() + timedelta(hours=1)).isoformat()
        return None

    def _determine_provenance(self, source: str, source_ref: str | None) -> str:
        """Determine provenance based on source and reference."""
        from app.database.models.memory import MemoryProvenance

        # Map sources to provenance
        source_provenance_map = {
            "email": MemoryProvenance.EXTERNAL_UNTRUSTED_EMAIL,
            "browser": MemoryProvenance.EXTERNAL_UNTRUSTED_WEB,
            "user_direct": MemoryProvenance.USER_DIRECT,
            "internal": MemoryProvenance.INTERNAL_MEMORY,
        }

        # Default to user_direct for unknown sources
        return source_provenance_map.get(source, MemoryProvenance.USER_DIRECT)
