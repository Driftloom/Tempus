"""Command definitions."""

from app.core.cqrs.commands.task_commands import (
    CreateTaskCommand,
    UpdateTaskCommand,
    DeleteTaskCommand,
    CompleteTaskCommand,
)
from app.core.cqrs.commands.memory_commands import (
    CreateMemoryCommand,
    UpdateMemoryCommand,
    DeleteMemoryCommand,
    ConsolidateMemoryCommand,
)

__all__ = [
    "CreateTaskCommand",
    "UpdateTaskCommand",
    "DeleteTaskCommand",
    "CompleteTaskCommand",
    "CreateMemoryCommand",
    "UpdateMemoryCommand",
    "DeleteMemoryCommand",
    "ConsolidateMemoryCommand",
]
