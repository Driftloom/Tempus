"""Performance tests for LLM operations."""

import pytest
import time
from unittest.mock import AsyncMock, patch
from app.llm.router import LLMRouter
from app.llm.prompt import PromptBuilder


@pytest.mark.asyncio
async def test_llm_router_selection_performance():
    """Test LLM router model selection performance."""
    with patch('app.llm.router.settings') as mock_settings:
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.openai_api_key = "test_key"
        
        router = LLMRouter()
        
        start_time = time.time()
        
        for _ in range(100):
            model, provider = router._select_cost_optimized()
        
        elapsed = time.time() - start_time
        
        print(f"Model selection time for 100 calls: {elapsed * 1000:.2f}ms")
        assert elapsed < 0.1  # Should be very fast


@pytest.mark.asyncio
async def test_prompt_builder_performance():
    """Test prompt builder performance."""
    builder = PromptBuilder()
    
    start_time = time.time()
    
    for i in range(100):
        builder.clear()
        builder.add_system_message("You are a helpful assistant.")
        builder.add_user_message(f"Test message {i}")
        builder.build()
    
    elapsed = time.time() - start_time
    
    print(f"Prompt building time for 100 messages: {elapsed * 1000:.2f}ms")
    assert elapsed < 0.5  # Should be fast


@pytest.mark.asyncio
async def test_prompt_optimizer_performance():
    """Test prompt optimizer performance."""
    from app.llm.prompt import PromptOptimizer
    
    optimizer = PromptOptimizer()
    
    long_prompt = "This is a test prompt " * 50
    
    start_time = time.time()
    
    for _ in range(50):
        optimizer.optimize_length(long_prompt, max_length=100)
    
    elapsed = time.time() - start_time
    
    print(f"Prompt optimization time for 50 calls: {elapsed * 1000:.2f}ms")
    assert elapsed < 0.5  # Should be fast


@pytest.mark.asyncio
async def test_multi_agent_orchestration_performance():
    """Test multi-agent orchestration performance."""
    from app.llm.multi_agent import MultiAgentOrchestrator, AgentRole
    
    with patch('app.llm.multi_agent.llm_router') as mock_router:
        mock_router.complete = AsyncMock(return_value={"choices": [{"message": {"content": "Response"}}]})
        
        orchestrator = MultiAgentOrchestrator(mock_router)
        
        agent = AgentRole(
            name="test_agent",
            description="Test agent",
            system_prompt="You are a test agent"
        )
        orchestrator.register_agent(agent)
        
        start_time = time.time()
        
        for _ in range(10):
            await orchestrator.execute_agent("test_agent", "Test task")
        
        elapsed = time.time() - start_time
    
    print(f"Agent execution time for 10 calls: {elapsed * 1000:.2f}ms")
    assert elapsed < 5.0  # Should complete in reasonable time


@pytest.mark.asyncio
async def test_concurrent_llm_requests():
    """Test concurrent LLM requests."""
    import asyncio
    
    with patch('app.llm.router.settings') as mock_settings:
        mock_settings.anthropic_api_key = "test_key"
        
        router = LLMRouter()
        
        async def make_request():
            with patch.object(router, '_call_provider', new_callable=AsyncMock) as mock_call:
                mock_call.return_value = {"choices": [{"message": {"content": "Response"}}]}
                return await router.complete([{"role": "user", "content": "Test"}])
        
        start_time = time.time()
        
        # Make 20 concurrent requests
        await asyncio.gather(*[make_request() for _ in range(20)])
        
        elapsed = time.time() - start_time
    
    print(f"20 concurrent LLM requests time: {elapsed * 1000:.2f}ms")
    assert elapsed < 2.0  # Should complete quickly
