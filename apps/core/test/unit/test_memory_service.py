"""Unit tests for memory service."""

import pytest
from app.memory.service import MemoryService
from app.memory.classification.layer_classifier import LayerClassifier
from app.memory.classification.sensitivity_classifier import SensitivityClassifier
from app.memory.embedding.embedding_generator import EmbeddingGenerator


@pytest.fixture
def layer_classifier():
    """Fixture for layer classifier."""
    return LayerClassifier()


@pytest.fixture
def sensitivity_classifier():
    """Fixture for sensitivity classifier."""
    return SensitivityClassifier()


@pytest.fixture
def embedding_generator():
    """Fixture for embedding generator."""
    return EmbeddingGenerator()


@pytest.fixture
def memory_service(layer_classifier, sensitivity_classifier, embedding_generator):
    """Fixture for memory service."""
    return MemoryService(
        memory_repository=None,
        layer_classifier=layer_classifier,
        sensitivity_classifier=sensitivity_classifier,
        embedding_generator=embedding_generator
    )


class TestLayerClassifier:
    """Tests for layer classifier."""
    
    def test_classify_working_memory(self, layer_classifier):
        """Test classification of working memory."""
        layer = layer_classifier.classify("test", "browser")
        assert layer.value == "working"
    
    def test_classify_episodic_memory(self, layer_classifier):
        """Test classification of episodic memory."""
        layer = layer_classifier.classify("test", "email")
        assert layer.value == "episodic"
    
    def test_classify_semantic_memory(self, layer_classifier):
        """Test classification of semantic memory."""
        layer = layer_classifier.classify("I always prefer coffee in the morning", "manual")
        assert layer.value == "semantic"


class TestSensitivityClassifier:
    """Tests for sensitivity classifier."""
    
    def test_classify_high_sensitivity(self, sensitivity_classifier):
        """Test classification of high sensitivity."""
        sensitivity = sensitivity_classifier.classify("My password is secret123", "manual")
        assert sensitivity.value == "high"
    
    def test_classify_medium_sensitivity(self, sensitivity_classifier):
        """Test classification of medium sensitivity."""
        sensitivity = sensitivity_classifier.classify("Work project deadline", "manual")
        assert sensitivity.value == "medium"
    
    def test_classify_low_sensitivity(self, sensitivity_classifier):
        """Test classification of low sensitivity."""
        sensitivity = sensitivity_classifier.classify("Just a note", "manual")
        assert sensitivity.value == "low"


class TestEmbeddingGenerator:
    """Tests for embedding generator."""
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, embedding_generator):
        """Test embedding generation."""
        embedding = await embedding_generator.generate("test text")
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
