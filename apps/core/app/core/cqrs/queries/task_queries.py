"""Task queries."""

from pydantic import Field
from app.core.cqrs.base import Query
from typing import Optional


class GetTaskQuery(Query):
    """Query to get a task by ID."""
    task_id: str
    user_id: str


class GetTasksByUserQuery(Query):
    """Query to get tasks for a user."""
    user_id: str
    status: Optional[str] = None
    priority: Optional[str] = None
    skip: int = 0
    limit: int = 100


class GetPendingTasksQuery(Query):
    """Query to get pending tasks for a user."""
    user_id: str
