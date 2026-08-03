"""Unit tests for CQRS bus functionality."""

import pytest
from app.core.cqrs.bus import CommandBus, QueryBus
from app.core.cqrs.base import Command, Query


class TestCommand(Command):
    """Test command."""
    pass


class TestQuery(Query):
    """Test query."""
    pass


async def command_handler_func(command: TestCommand) -> None:
    """Test command handler function."""
    pass


async def query_handler_func(query: TestQuery) -> str:
    """Test query handler function."""
    return "test_result"


@pytest.mark.asyncio
async def test_command_bus_register_and_dispatch():
    """Test command bus registration and dispatch."""
    bus = CommandBus()

    bus.register(TestCommand, command_handler_func)

    command = TestCommand()
    await bus.dispatch(command)

    # Verify handler was registered
    assert TestCommand in bus._handlers


@pytest.mark.asyncio
async def test_query_bus_register_and_dispatch():
    """Test query bus registration and dispatch."""
    bus = QueryBus()

    bus.register(TestQuery, query_handler_func)

    query = TestQuery()
    result = await bus.dispatch(query)

    assert result == "test_result"
    assert TestQuery in bus._handlers


def test_command_bus_duplicate_handler():
    """Test that duplicate handler registration overwrites."""
    bus = CommandBus()

    bus.register(TestCommand, command_handler_func)
    # Registering again should overwrite, not raise error
    bus.register(TestCommand, command_handler_func)

    assert TestCommand in bus._handlers


def test_query_bus_duplicate_handler():
    """Test that duplicate handler registration overwrites."""
    bus = QueryBus()

    bus.register(TestQuery, query_handler_func)
    # Registering again should overwrite, not raise error
    bus.register(TestQuery, query_handler_func)

    assert TestQuery in bus._handlers
