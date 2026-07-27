"""Command and query bus for CQRS pattern."""

from typing import Type, Dict, Callable, Any
from app.core.cqrs.base import Command, Query, CommandHandler, QueryHandler
import structlog

logger = structlog.get_logger(__name__)


class CommandBus:
    """Command bus for dispatching commands to handlers."""

    def __init__(self):
        """Initialize command bus."""
        self._handlers: Dict[Type[Command], Callable] = {}

    def register(self, command_type: Type[Command], handler: Callable) -> None:
        """Register a command handler."""
        self._handlers[command_type] = handler
        logger.debug("Registered command handler", command=command_type.__name__)

    async def dispatch(self, command: Command) -> Any:
        """Dispatch a command to its handler."""
        command_type = type(command)
        if command_type not in self._handlers:
            raise ValueError(f"No handler registered for command: {command_type.__name__}")
        
        handler = self._handlers[command_type]
        logger.info("Dispatching command", command=command_type.__name__)
        result = await handler(command)
        logger.info("Command handled", command=command_type.__name__)
        return result


class QueryBus:
    """Query bus for dispatching queries to handlers."""

    def __init__(self):
        """Initialize query bus."""
        self._handlers: Dict[Type[Query], Callable] = {}

    def register(self, query_type: Type[Query], handler: Callable) -> None:
        """Register a query handler."""
        self._handlers[query_type] = handler
        logger.debug("Registered query handler", query=query_type.__name__)

    async def dispatch(self, query: Query) -> Any:
        """Dispatch a query to its handler."""
        query_type = type(query)
        if query_type not in self._handlers:
            raise ValueError(f"No handler registered for query: {query_type.__name__}")
        
        handler = self._handlers[query_type]
        logger.info("Dispatching query", query=query_type.__name__)
        result = await handler(query)
        logger.info("Query handled", query=query_type.__name__)
        return result


# Global bus instances
command_bus = CommandBus()
query_bus = QueryBus()
