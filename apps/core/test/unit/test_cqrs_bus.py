"""Unit tests for CQRS bus functionality."""

import pytest
from app.core.cqrs.bus import CommandBus, QueryBus
from app.core.cqrs.base import Command, Query, CommandHandler, QueryHandler


class TestCommand(Command):
    """Test command."""
    pass


class TestQuery(Query):
    """Test query."""
    pass


class TestCommandHandler(CommandHandler[TestCommand]):
    """Test command handler."""
    
    async def handle(self, command: TestCommand) -> None:
        """Handle test command."""
        pass


class TestQueryHandler(QueryHandler[TestQuery, str]):
    """Test query handler."""
    
    async def handle(self, query: TestQuery) -> str:
        """Handle test query."""
        return "test_result"


@pytest.mark.asyncio
async def test_command_bus_register_and_dispatch():
    """Test command bus registration and dispatch."""
    bus = CommandBus()
    handler = TestCommandHandler()
    
    bus.register(TestCommand, handler)
    
    command = TestCommand()
    await bus.dispatch(command)
    
    # Verify handler was called (would need mock in real test)
    assert TestCommand in bus._handlers


@pytest.mark.asyncio
async def test_query_bus_register_and_dispatch():
    """Test query bus registration and dispatch."""
    bus = QueryBus()
    handler = TestQueryHandler()
    
    bus.register(TestQuery, handler)
    
    query = TestQuery()
    result = await bus.dispatch(query)
    
    assert result == "test_result"
    assert TestQuery in bus._handlers


def test_command_bus_duplicate_handler():
    """Test that duplicate handler registration raises error."""
    bus = CommandBus()
    handler1 = TestCommandHandler()
    handler2 = TestCommandHandler()
    
    bus.register(TestCommand, handler1)
    
    with pytest.raises(ValueError):
        bus.register(TestCommand, handler2)


def test_query_bus_duplicate_handler():
    """Test that duplicate handler registration raises error."""
    bus = QueryBus()
    handler1 = TestQueryHandler()
    handler2 = TestQueryHandler()
    
    bus.register(TestQuery, handler1)
    
    with pytest.raises(ValueError):
        bus.register(TestQuery, handler2)
