"""Memory queries."""


from app.core.cqrs.base import Query


class GetMemoryQuery(Query):
    """Query to get a memory by ID."""
    memory_id: str
    user_id: str


class GetMemoriesByUserQuery(Query):
    """Query to get memories for a user."""
    user_id: str
    layer: str | None = None
    skip: int = 0
    limit: int = 100


class SearchMemoryQuery(Query):
    """Query to search memories."""
    user_id: str
    query: str
    layer: str | None = None
    limit: int = 10
