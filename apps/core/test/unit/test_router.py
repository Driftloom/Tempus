"""Unit tests for router module."""

import pytest
from unittest.mock import AsyncMock, patch
from app.router.service import RouterService
from app.router.routing_policy import RoutingPolicy
from app.router.gateway.llm_gateway import LLMGateway
from app.router.economics.cost_tracker import CostTracker


@pytest.fixture
def router_service():
    """Create router service fixture."""
    with patch('app.router.service.llm_router') as mock_router:
        return RouterService(mock_router)


@pytest.fixture
def routing_policy():
    """Create routing policy fixture."""
    return RoutingPolicy()


@pytest.fixture
def llm_gateway():
    """Create LLM gateway fixture."""
    return LLMGateway()


@pytest.fixture
def cost_tracker():
    """Create cost tracker fixture."""
    return CostTracker()


# Router Service Tests
@pytest.mark.asyncio
async def test_router_service_route_request(router_service):
    """Test routing a request."""
    request = {
        "messages": [{"role": "user", "content": "Test"}],
        "policy": "cost_optimized"
    }
    
    with patch.object(router_service.llm_router, 'complete', new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = {"choices": [{"message": {"content": "Response"}}]}
        
        result = await router_service.route(request)
        
        assert result is not None


@pytest.mark.asyncio
async def test_router_service_select_provider(router_service):
    """Test provider selection."""
    with patch.object(router_service, '_select_provider', return_value="anthropic"):
        provider = await router_service.select_provider("cost_optimized")
        
        assert provider == "anthropic"


@pytest.mark.asyncio
async def test_router_service_fallback(router_service):
    """Test fallback mechanism."""
    with patch.object(router_service.llm_router, 'complete', new_callable=AsyncMock) as mock_complete:
        mock_complete.side_effect = [Exception("Error"), {"choices": [{"message": {"content": "Response"}}]}]
        
        request = {"messages": [{"role": "user", "content": "Test"}]}
        result = await router_service.route_with_fallback(request)
        
        assert result is not None


# Routing Policy Tests
def test_routing_policy_cost_optimized(routing_policy):
    """Test cost-optimized routing policy."""
    policy = routing_policy.get_policy("cost_optimized")
    
    assert policy["primary_provider"] == "ollama"
    assert policy["fallback_providers"] == ["openai"]


def test_routing_policy_performance(routing_policy):
    """Test performance routing policy."""
    policy = routing_policy.get_policy("performance")
    
    assert policy["primary_provider"] == "anthropic"
    assert policy["fallback_providers"] == ["openai"]


def test_routing_policy_latency(routing_policy):
    """Test low-latency routing policy."""
    policy = routing_policy.get_policy("latency")
    
    assert policy["primary_provider"] == "ollama"
    assert policy["fallback_providers"] == ["anthropic"]


def test_routing_policy_custom(routing_policy):
    """Test custom routing policy."""
    custom_policy = {
        "primary_provider": "openai",
        "fallback_providers": ["anthropic"],
        "weights": {"openai": 0.7, "anthropic": 0.3}
    }
    
    routing_policy.add_policy("custom", custom_policy)
    policy = routing_policy.get_policy("custom")
    
    assert policy["primary_provider"] == "openai"


# LLM Gateway Tests
@pytest.mark.asyncio
async def test_llm_gateway_forward_request(llm_gateway):
    """Test forwarding request through gateway."""
    request = {
        "provider": "anthropic",
        "messages": [{"role": "user", "content": "Test"}]
    }
    
    with patch.object(llm_gateway, '_call_provider', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = {"choices": [{"message": {"content": "Response"}}]}
        
        result = await llm_gateway.forward(request)
        
        assert result is not None


@pytest.mark.asyncio
async def test_llm_gateway_with_caching(llm_gateway):
    """Test gateway with caching enabled."""
    request = {
        "provider": "anthropic",
        "messages": [{"role": "user", "content": "Test"}],
        "use_cache": True
    }
    
    with patch.object(llm_gateway, '_check_cache', return_value=None):
        with patch.object(llm_gateway, '_call_provider', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"choices": [{"message": {"content": "Response"}}]}
            
            result = await llm_gateway.forward(request)
            
            assert result is not None


@pytest.mark.asyncio
async def test_llm_gateway_rate_limiting(llm_gateway):
    """Test gateway rate limiting."""
    request = {
        "provider": "anthropic",
        "messages": [{"role": "user", "content": "Test"}]
    }
    
    with patch.object(llm_gateway, '_check_rate_limit', return_value=True):
        with patch.object(llm_gateway, '_call_provider', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"choices": [{"message": {"content": "Response"}}]}
            
            result = await llm_gateway.forward(request)
            
            assert result is not None


# Cost Tracker Tests
def test_cost_tracker_initialization(cost_tracker):
    """Test cost tracker initialization."""
    assert cost_tracker is not None


def test_cost_tracker_track_request(cost_tracker):
    """Test tracking request cost."""
    cost_tracker.track_request(
        provider="anthropic",
        model="claude-3-opus",
        tokens_input=100,
        tokens_output=50
    )
    
    assert len(cost_tracker.costs) > 0


def test_cost_tracker_get_total_cost(cost_tracker):
    """Test getting total cost."""
    cost_tracker.track_request(
        provider="anthropic",
        model="claude-3-opus",
        tokens_input=100,
        tokens_output=50
    )
    
    total_cost = cost_tracker.get_total_cost()
    
    assert total_cost >= 0


def test_cost_tracker_get_cost_by_provider(cost_tracker):
    """Test getting cost by provider."""
    cost_tracker.track_request(
        provider="anthropic",
        model="claude-3-opus",
        tokens_input=100,
        tokens_output=50
    )
    
    cost_tracker.track_request(
        provider="openai",
        model="gpt-4",
        tokens_input=50,
        tokens_output=25
    )
    
    anthropic_cost = cost_tracker.get_cost_by_provider("anthropic")
    openai_cost = cost_tracker.get_cost_by_provider("openai")
    
    assert anthropic_cost >= 0
    assert openai_cost >= 0


def test_cost_tracker_reset(cost_tracker):
    """Test resetting cost tracker."""
    cost_tracker.track_request(
        provider="anthropic",
        model="claude-3-opus",
        tokens_input=100,
        tokens_output=50
    )
    
    cost_tracker.reset()
    
    assert len(cost_tracker.costs) == 0
