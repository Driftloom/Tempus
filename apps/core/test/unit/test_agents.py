"""Unit tests for agents module."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.runtime.agent_base import AgentBase, AgentStatus
from app.agents.loop.loop_engine import LoopEngine
from app.agents.orchestration.supervisor import Supervisor


@pytest.fixture
def mock_agent():
    """Create mock agent fixture."""
    agent = MagicMock(spec=AgentBase)
    agent.agent_id = "test_agent_1"
    agent.user_id = "user_123"
    agent.goal = "Test goal"
    agent.status = AgentStatus.IDLE
    return agent


@pytest.fixture
def loop_engine():
    """Create loop engine fixture."""
    with patch('app.agents.loop.loop_engine.AgentStateStore') as mock_store:
        return LoopEngine(mock_store)


@pytest.fixture
def supervisor():
    """Create supervisor fixture."""
    return Supervisor()


# Agent Base Tests
def test_agent_initialization():
    """Test agent initialization."""
    agent = AgentBase(agent_id="test_1", user_id="user_123", goal="Test goal")
    
    assert agent.agent_id == "test_1"
    assert agent.user_id == "user_123"
    assert agent.goal == "Test goal"
    assert agent.status == AgentStatus.IDLE


def test_agent_status_transitions():
    """Test agent status transitions."""
    agent = AgentBase(agent_id="test_1", user_id="user_123", goal="Test goal")
    
    assert agent.status == AgentStatus.IDLE
    agent.status = AgentStatus.PLANNING
    assert agent.status == AgentStatus.PLANNING
    agent.status = AgentStatus.ACTING
    assert agent.status == AgentStatus.ACTING
    agent.status = AgentStatus.COMPLETED
    assert agent.status == AgentStatus.COMPLETED


def test_agent_get_state():
    """Test agent state retrieval."""
    agent = AgentBase(agent_id="test_1", user_id="user_123", goal="Test goal")
    state = agent.get_state()
    
    assert state["agent_id"] == "test_1"
    assert state["user_id"] == "user_123"
    assert state["goal"] == "Test goal"
    assert "status" in state


# Loop Engine Tests
@pytest.mark.asyncio
async def test_loop_engine_start_agent(loop_engine, mock_agent):
    """Test starting an agent."""
    with patch.object(loop_engine.state_store, 'save', new_callable=AsyncMock):
        with patch.object(mock_agent, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"result": "success"}
            
            result = await loop_engine.start_agent(mock_agent)
            
            assert result is not None
            mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_loop_engine_pause_agent(loop_engine, mock_agent):
    """Test pausing an agent."""
    with patch.object(loop_engine.state_store, 'save', new_callable=AsyncMock):
        await loop_engine.pause_agent(mock_agent.agent_id)
        
        assert mock_agent.agent_id not in loop_engine.active_agents


@pytest.mark.asyncio
async def test_loop_engine_resume_agent(loop_engine, mock_agent):
    """Test resuming an agent."""
    with patch.object(loop_engine.state_store, 'save', new_callable=AsyncMock):
        await loop_engine.resume_agent(mock_agent.agent_id)
        
        # Should not raise exception
        assert True


@pytest.mark.asyncio
async def test_loop_engine_cancel_agent(loop_engine, mock_agent):
    """Test canceling an agent."""
    with patch.object(loop_engine.state_store, 'save', new_callable=AsyncMock):
        await loop_engine.cancel_agent(mock_agent.agent_id)
        
        assert mock_agent.agent_id not in loop_engine.active_agents


def test_loop_engine_get_status(loop_engine):
    """Test getting agent status."""
    status = loop_engine.get_status("test_agent_id")
    
    assert status is not None


# Supervisor Tests
def test_supervisor_initialization(supervisor):
    """Test supervisor initialization."""
    assert supervisor is not None
    assert len(supervisor.registered_agents) == 0


def test_supervisor_register_agent(supervisor):
    """Test registering an agent type."""
    supervisor.register_agent("test_agent", AgentBase)
    
    assert "test_agent" in supervisor.registered_agents


@pytest.mark.asyncio
async def test_supervisor_orchestrate_sequential(supervisor):
    """Test sequential orchestration."""
    supervisor.register_agent("test_agent", AgentBase)
    
    with patch.object(supervisor, '_create_agent', return_value=MagicMock()):
        with patch.object(supervisor, '_execute_agents', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = [{"result": "success"}]
            
            result = await supervisor.orchestrate(
                "user_123",
                "Test goal",
                ["test_agent"],
                mode="sequential"
            )
            
            assert result is not None


@pytest.mark.asyncio
async def test_supervisor_orchestrate_concurrent(supervisor):
    """Test concurrent orchestration."""
    supervisor.register_agent("test_agent", AgentBase)
    
    with patch.object(supervisor, '_create_agent', return_value=MagicMock()):
        with patch.object(supervisor, '_execute_agents', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = [{"result": "success"}]
            
            result = await supervisor.orchestrate(
                "user_123",
                "Test goal",
                ["test_agent"],
                mode="concurrent"
            )
            
            assert result is not None


def test_supervisor_list_agent_types(supervisor):
    """Test listing agent types."""
    supervisor.register_agent("agent1", AgentBase)
    supervisor.register_agent("agent2", AgentBase)
    
    agent_types = supervisor.list_agent_types()
    
    assert "agent1" in agent_types
    assert "agent2" in agent_types
