"""Command definitions."""

from app.core.cqrs.commands.memory_commands import (
    ConsolidateMemoryCommand,
    CreateMemoryCommand,
    DeleteMemoryCommand,
    UpdateMemoryCommand,
)
from app.core.cqrs.commands.task_commands import (
    CompleteTaskCommand,
    CreateTaskCommand,
    DeleteTaskCommand,
    UpdateTaskCommand,
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
