"""Embedding generator for memory items."""


from structlog import get_logger

from app.core.config import settings

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generator for text embeddings using LLM providers."""

    def __init__(self):
        """Initialize embedding generator."""
        self.ollama_host = settings.ollama_host

    async def generate(self, text: str) -> list[float]:
        """Generate embedding for text."""
        logger.info("Generating embedding", text_length=len(text))

        # For now, use a simple mock embedding
        # In production, this would call Ollama or cloud LLM API
        embedding = self._mock_embedding(text)

        logger.info("Embedding generated", dimension=len(embedding))
        return embedding

    def _mock_embedding(self, text: str) -> list[float]:
        """Generate a mock embedding (placeholder)."""
        # This is a placeholder - in production, use actual embedding model
        # For now, generate a deterministic pseudo-random embedding based on text
        import hashlib

        # Create a deterministic seed from text
        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)

        # Generate 1536-dimensional embedding (OpenAI default)
        import random
        random.seed(seed)
        embedding = [random.uniform(-1, 1) for _ in range(1536)]

        # Normalize embedding
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding
