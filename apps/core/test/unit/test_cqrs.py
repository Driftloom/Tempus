"""Unit tests for CQRS pattern."""

import pytest
from app.core.cqrs.base import Command, Query, CommandHandler, QueryHandler
from app.core.cqrs.bus import CommandBus, QueryBus


class TestCommand(Command):
    """Test command."""
    data: str = "test"


class TestQuery(Query):
    """Test query."""
    query: str = "test"


class TestCommandHandler(CommandHandler[TestCommand, dict]):
    """Test command handler."""
    
    async def handle(self, command: TestCommand) -> dict:
        return {"processed": command.data}


class TestQueryHandler(QueryHandler[TestQuery, dict]):
    """Test query handler."""
    
    async def handle(self, query: TestQuery) -> dict:
        return {"result": query.query}


@pytest.fixture
def command_bus():
    """Create command bus fixture."""
    return CommandBus()


@pytest.fixture
def query_bus():
    """Create query bus fixture."""
    return QueryBus()


@pytest.mark.asyncio
async def test_command_bus_register(command_bus):
    """Test command bus registration."""
    handler = TestCommandHandler()
    command_bus.register(TestCommand, handler)
    
    assert TestCommand in command_bus._handlers


@pytest.mark.asyncio
async def test_command_bus_dispatch(command_bus):
    """Test command bus dispatch."""
    handler = TestCommandHandler()
    command_bus.register(TestCommand, handler)
    
    command = TestCommand()
    result = await command_bus.dispatch(command)
    
    assert result == {"processed": "test"}


@pytest.mark.asyncio
async def test_command_bus_no_handler(command_bus):
    """Test command bus with no handler."""
    command = TestCommand()
    
    with pytest.raises(ValueError, match="No handler registered"):
        await command_bus.dispatch(command)


@pytest.mark.asyncio
async def test_query_bus_register(query_bus):
    """Test query bus registration."""
    handler = TestQueryHandler()
    query_bus.register(TestQuery, handler)
    
    assert TestQuery in query_bus._handlers


@pytest.mark.asyncio
async def test_query_bus_dispatch(query_bus):
    """Test query bus dispatch."""
    handler = TestQueryHandler()
    query_bus.register(TestQuery, handler)
    
    query = TestQuery()
    result = await query_bus.dispatch(query)
    
    assert result == {"result": "test"}


@pytest.mark.asyncio
async def test_query_bus_no_handler(query_bus):
    """Test query bus with no handler."""
    query = TestQuery()
    
    with pytest.raises(ValueError, match="No handler registered"):
        await query_bus.dispatch(query)
