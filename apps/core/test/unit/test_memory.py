"""Unit tests for memory module."""

import pytest
from unittest.mock import AsyncMock
from app.memory.service import MemoryService
from app.memory.engine import MemoryEngine
from app.memory.models import MemoryItem, MemoryLayer


@pytest.fixture
def memory_service():
    """Create memory service fixture."""
    with patch('app.memory.service.memory_repository') as mock_repo:
        return MemoryService(mock_repo)


@pytest.fixture
def memory_engine():
    """Create memory engine fixture."""
    return MemoryEngine()


@pytest.fixture
def memory_item():
    """Create memory item fixture."""
    return MemoryItem(
        id="mem1",
        user_id="user123",
        content="Test memory content",
        layer=MemoryLayer.EPISODIC,
        importance_score=0.8
    )


# Memory Service Tests
@pytest.mark.asyncio
async def test_memory_service_create_memory(memory_service):
    """Test memory creation."""
    memory_data = {
        "content": "Test memory",
        "layer": MemoryLayer.EPISODIC,
        "importance_score": 0.8
    }
    
    with patch.object(memory_service.memory_repo, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"id": "mem1", **memory_data}
        
        result = await memory_service.create_memory("user123", memory_data)
        
        assert result["content"] == "Test memory"


@pytest.mark.asyncio
async def test_memory_service_get_memory(memory_service):
    """Test memory retrieval."""
    with patch.object(memory_service.memory_repo, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"id": "mem1", "content": "Test memory"}
        
        result = await memory_service.get_memory("mem1")
        
        assert result["id"] == "mem1"


@pytest.mark.asyncio
async def test_memory_service_search_memory(memory_service):
    """Test memory search."""
    with patch.object(memory_service.memory_repo, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [
            {"id": "mem1", "content": "Test memory 1"},
            {"id": "mem2", "content": "Test memory 2"},
        ]
        
        result = await memory_service.search_memory("user123", "test query")
        
        assert len(result) >= 1


@pytest.mark.asyncio
async def test_memory_service_update_memory(memory_service):
    """Test memory update."""
    update_data = {"content": "Updated memory"}
    
    with patch.object(memory_service.memory_repo, 'update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = {"id": "mem1", **update_data}
        
        result = await memory_service.update_memory("mem1", update_data)
        
        assert result["content"] == "Updated memory"


@pytest.mark.asyncio
async def test_memory_service_delete_memory(memory_service):
    """Test memory deletion."""
    with patch.object(memory_service.memory_repo, 'delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        
        result = await memory_service.delete_memory("mem1")
        
        assert result is True


# Memory Engine Tests
def test_memory_engine_initialization(memory_engine):
    """Test memory engine initialization."""
    assert memory_engine is not None


def test_memory_engine_store(memory_engine):
    """Test storing memory."""
    memory = MemoryItem(
        id="mem1",
        user_id="user123",
        content="Test memory",
        layer=MemoryLayer.WORKING
    )
    
    memory_engine.store(memory)
    
    assert "mem1" in memory_engine.working_memory


def test_memory_engine_retrieve(memory_engine):
    """Test retrieving memory."""
    memory = MemoryItem(
        id="mem1",
        user_id="user123",
        content="Test memory",
        layer=MemoryLayer.WORKING
    )
    memory_engine.store(memory)
    
    retrieved = memory_engine.retrieve("mem1")
    
    assert retrieved is not None
    assert retrieved.id == "mem1"


def test_memory_engine_search_semantic(memory_engine):
    """Test semantic memory search."""
    memory1 = MemoryItem(id="mem1", user_id="user123", content="Python programming", layer=MemoryLayer.SEMANTIC)
    memory2 = MemoryItem(id="mem2", user_id="user123", content="JavaScript coding", layer=MemoryLayer.SEMANTIC)
    
    memory_engine.store(memory1)
    memory_engine.store(memory2)
    
    results = memory_engine.search("programming")
    
    assert len(results) >= 1


def test_memory_engine_consolidate(memory_engine):
    """Test memory consolidation."""
    memory = MemoryItem(
        id="mem1",
        user_id="user123",
        content="Test memory",
        layer=MemoryLayer.WORKING,
        importance_score=0.9
    )
    memory_engine.store(memory)
    
    memory_engine.consolidate("mem1")
    
    # Memory should be moved from working to episodic
    assert "mem1" not in memory_engine.working_memory


# Memory Model Tests
def test_memory_item_initialization(memory_item):
    """Test memory item initialization."""
    assert memory_item.id == "mem1"
    assert memory_item.user_id == "user123"
    assert memory_item.layer == MemoryLayer.EPISODIC
    assert memory_item.importance_score == 0.8


def test_memory_layer_values():
    """Test memory layer enum values."""
    assert MemoryLayer.WORKING.value == "working"
    assert MemoryLayer.EPISODIC.value == "episodic"
    assert MemoryLayer.SEMANTIC.value == "semantic"
    assert MemoryLayer.PROCEDURAL.value == "procedural"


def test_memory_item_with_embedding():
    """Test memory item with embedding."""
    memory = MemoryItem(
        id="mem1",
        user_id="user123",
        content="Test memory",
        layer=MemoryLayer.EPISODIC,
        embedding=[0.1, 0.2, 0.3]
    )
    
    assert memory.embedding == [0.1, 0.2, 0.3]


def test_memory_item_with_provenance():
    """Test memory item with provenance."""
    memory = MemoryItem(
        id="mem1",
        user_id="user123",
        content="Test memory",
        layer=MemoryLayer.EPISODIC,
        provenance={"source": "email", "confidence": 0.9}
    )
    
    assert memory.provenance["source"] == "email"
