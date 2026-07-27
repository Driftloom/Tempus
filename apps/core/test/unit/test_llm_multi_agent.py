"""Unit tests for LLM multi-agent module."""

import pytest
from unittest.mock import AsyncMock, patch
from app.llm.multi_agent import AgentRole, MultiAgentOrchestrator, AgentWorkflow


@pytest.fixture
def orchestrator():
    """Create multi-agent orchestrator fixture."""
    with patch('app.llm.multi_agent.llm_router') as mock_router:
        return MultiAgentOrchestrator(mock_router)


# Agent Role Tests
def test_agent_role_initialization():
    """Test agent role initialization."""
    role = AgentRole(
        name="planner",
        description="Plans tasks",
        system_prompt="You are a planner",
    )
    
    assert role.name == "planner"
    assert role.description == "Plans tasks"
    assert role.system_prompt == "You are a planner"


def test_agent_role_with_capabilities():
    """Test agent role with capabilities."""
    role = AgentRole(
        name="researcher",
        description="Researches topics",
        system_prompt="You are a researcher",
        capabilities=["search", "analyze", "summarize"],
    )
    
    assert "search" in role.capabilities
    assert "analyze" in role.capabilities


# Multi-Agent Orchestrator Tests
@pytest.mark.asyncio
async def test_orchestrator_register_agent(orchestrator):
    """Test agent registration."""
    agent = AgentRole(
        name="test_agent",
        description="Test agent",
        system_prompt="You are a test agent",
    )
    
    orchestrator.register_agent(agent)
    
    assert "test_agent" in orchestrator.agents


@pytest.mark.asyncio
async def test_orchestrator_execute_agent(orchestrator):
    """Test single agent execution."""
    agent = AgentRole(
        name="test_agent",
        description="Test agent",
        system_prompt="You are a test agent",
    )
    
    orchestrator.register_agent(agent)
    
    with patch.object(orchestrator.llm_router, 'complete', new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = {"choices": [{"message": {"content": "Test response"}}]}
        
        result = await orchestrator.execute_agent("test_agent", "Test task")
        
        assert result is not None
        mock_complete.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_sequential_workflow(orchestrator):
    """Test sequential workflow execution."""
    agent1 = AgentRole(name="agent1", description="Agent 1", system_prompt="Agent 1")
    agent2 = AgentRole(name="agent2", description="Agent 2", system_prompt="Agent 2")
    
    orchestrator.register_agent(agent1)
    orchestrator.register_agent(agent2)
    
    with patch.object(orchestrator.llm_router, 'complete', new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = {"choices": [{"message": {"content": "Response"}}]}
        
        result = await orchestrator.execute_workflow(
            AgentWorkflow.SEQUENTIAL,
            ["agent1", "agent2"],
            "Test task"
        )
        
        assert result is not None


@pytest.mark.asyncio
async def test_orchestrator_hierarchical_workflow(orchestrator):
    """Test hierarchical workflow execution."""
    supervisor = AgentRole(name="supervisor", description="Supervisor", system_prompt="Supervisor")
    worker = AgentRole(name="worker", description="Worker", system_prompt="Worker")
    
    orchestrator.register_agent(supervisor)
    orchestrator.register_agent(worker)
    
    with patch.object(orchestrator.llm_router, 'complete', new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = {"choices": [{"message": {"content": "Response"}}]}
        
        result = await orchestrator.execute_workflow(
            AgentWorkflow.HIERARCHICAL,
            {"supervisor": "supervisor", "workers": ["worker"]},
            "Test task"
        )
        
        assert result is not None


@pytest.mark.asyncio
async def test_orchestrator_collaborative_workflow(orchestrator):
    """Test collaborative workflow execution."""
    agent1 = AgentRole(name="agent1", description="Agent 1", system_prompt="Agent 1")
    agent2 = AgentRole(name="agent2", description="Agent 2", system_prompt="Agent 2")
    
    orchestrator.register_agent(agent1)
    orchestrator.register_agent(agent2)
    
    with patch.object(orchestrator.llm_router, 'complete', new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = {"choices": [{"message": {"content": "Response"}}]}
        
        result = await orchestrator.execute_workflow(
            AgentWorkflow.COLLABORATIVE,
            ["agent1", "agent2"],
            "Test task"
        )
        
        assert result is not None


@pytest.mark.asyncio
async def test_orchestrator_agent_not_found(orchestrator):
    """Test orchestrator with non-existent agent."""
    with pytest.raises(ValueError):
        await orchestrator.execute_agent("non_existent_agent", "Test task")


# Agent Workflow Tests
def test_agent_workflow_values():
    """Test agent workflow enum values."""
    assert AgentWorkflow.SEQUENTIAL.value == "sequential"
    assert AgentWorkflow.HIERARCHICAL.value == "hierarchical"
    assert AgentWorkflow.COLLABORATIVE.value == "collaborative"
