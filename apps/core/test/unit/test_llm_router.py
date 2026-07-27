"""Unit tests for LLM router."""

import pytest
from unittest.mock import AsyncMock, patch
from app.llm.router import LLMRouter


@pytest.fixture
def llm_router():
    """Create LLM router fixture."""
    return LLMRouter()


@pytest.mark.asyncio
async def test_select_model_cost_optimized(llm_router):
    """Test cost-optimized model selection."""
    llm_router.routing_policy = "cost_optimized"
    
    model, provider = llm_router._select_cost_optimized()
    
    assert provider in ["ollama", "openai"]
    assert model is not None


@pytest.mark.asyncio
async def test_select_model_performance(llm_router):
    """Test performance model selection."""
    llm_router.routing_policy = "performance"
    
    model, provider = llm_router._select_performance()
    
    assert provider in ["anthropic", "openai"]
    assert model is not None


@pytest.mark.asyncio
async def test_select_model_latency(llm_router):
    """Test low-latency model selection."""
    llm_router.routing_policy = "latency"
    
    model, provider = llm_router._select_low_latency()
    
    assert provider in ["ollama", "anthropic"]
    assert model is not None


@pytest.mark.asyncio
async def test_get_available_models(llm_router):
    """Test getting available models."""
    models = llm_router.get_available_models()
    
    assert isinstance(models, list)
    assert len(models) > 0


@pytest.mark.asyncio
async def test_set_routing_policy(llm_router):
    """Test setting routing policy."""
    llm_router.set_routing_policy("performance")
    
    assert llm_router.routing_policy == "performance"


@pytest.mark.asyncio
@patch('app.llm.router.acompletion')
async def test_complete_success(mock_acompletion, llm_router):
    """Test successful LLM completion."""
    mock_acompletion.return_value = {
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"total_tokens": 100}
    }
    
    messages = [{"role": "user", "content": "Test"}]
    result = await llm_router.complete(messages)
    
    assert result is not None
    assert "choices" in result
    mock_acompletion.assert_called_once()
