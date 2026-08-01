"""Celery tasks for memory processing."""

import structlog
from celery import shared_task

from app.database.session import AsyncSessionLocal
from app.memory.service import MemoryService

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3)
def consolidate_memory(self, user_id: str):
    """Consolidate memory items for a user."""
    logger.info("Consolidating memory", user_id=user_id)

    try:
        async def _consolidate():
            async with AsyncSessionLocal() as db:
                memory_service = MemoryService(db)
                await memory_service.consolidate(user_id)

        import asyncio
        asyncio.run(_consolidate())
        logger.info("Memory consolidated", user_id=user_id)
        return {"status": "success", "user_id": user_id}

    except Exception as e:
        logger.error("Memory consolidation failed", user_id=user_id, error=str(e))
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def generate_embeddings(memory_id: str):
    """Generate embeddings for a memory item."""
    logger.info("Generating embeddings", memory_id=memory_id)

    try:
        async def _generate():
            async with AsyncSessionLocal() as db:
                memory_service = MemoryService(db)
                await memory_service.generate_embeddings(memory_id)

        import asyncio
        asyncio.run(_generate())
        logger.info("Embeddings generated", memory_id=memory_id)
        return {"status": "success", "memory_id": memory_id}

    except Exception as e:
        logger.error("Embedding generation failed", memory_id=memory_id, error=str(e))
        raise


@shared_task
def prune_old_memory(user_id: str):
    """Prune old memory items based on retention policy."""
    logger.info("Pruning old memory", user_id=user_id)

    try:
        async def _prune():
            async with AsyncSessionLocal() as db:
                memory_service = MemoryService(db)
                await memory_service.prune_old(user_id)

        import asyncio
        asyncio.run(_prune())
        logger.info("Old memory pruned", user_id=user_id)
        return {"status": "success", "user_id": user_id}

    except Exception as e:
        logger.error("Memory pruning failed", user_id=user_id, error=str(e))
        raise


@shared_task
def update_memory_importance(user_id: str):
    """Update importance scores for memory items."""
    logger.info("Updating memory importance", user_id=user_id)

    try:
        async def _update():
            async with AsyncSessionLocal() as db:
                memory_service = MemoryService(db)
                await memory_service.update_importance_scores(user_id)

        import asyncio
        asyncio.run(_update())
        logger.info("Memory importance updated", user_id=user_id)
        return {"status": "success", "user_id": user_id}

    except Exception as e:
        logger.error("Memory importance update failed", user_id=user_id, error=str(e))
        raise
