"""Task queries."""


from app.core.cqrs.base import Query


class GetTaskQuery(Query):
    """Query to get a task by ID."""
    task_id: str
    user_id: str


class GetTasksByUserQuery(Query):
    """Query to get tasks for a user."""
    user_id: str
    status: str | None = None
    priority: str | None = None
    skip: int = 0
    limit: int = 100


class GetPendingTasksQuery(Query):
    """Query to get pending tasks for a user."""
    user_id: str
