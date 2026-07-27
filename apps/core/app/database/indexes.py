"""Database indexes for performance optimization."""

from sqlalchemy import Index, text
from app.database.models.memory import MemoryItem, MemoryEdge
from app.database.models.task import Task
from app.database.models.user import User


# Memory indexes
memory_user_layer_index = Index(
    "idx_memory_user_layer",
    MemoryItem.user_id,
    MemoryItem.layer,
)

memory_user_importance_index = Index(
    "idx_memory_user_importance",
    MemoryItem.user_id,
    MemoryItem.importance_score.desc(),
)

memory_provenance_index = Index(
    "idx_memory_provenance",
    MemoryItem.provenance,
)

memory_ttl_index = Index(
    "idx_memory_ttl",
    MemoryItem.ttl_at,
)

memory_created_at_index = Index(
    "idx_memory_created_at",
    MemoryItem.created_at.desc(),
)

# Task indexes
task_user_status_index = Index(
    "idx_task_user_status",
    Task.user_id,
    Task.status,
)

task_user_priority_index = Index(
    "idx_task_user_priority",
    Task.user_id,
    Task.priority,
)

task_due_at_index = Index(
    "idx_task_due_at",
    Task.due_at,
)

task_user_due_index = Index(
    "idx_task_user_due",
    Task.user_id,
    Task.due_at,
)

# Memory edge indexes
edge_from_index = Index(
    "idx_edge_from",
    MemoryEdge.from_memory_id,
)

edge_to_index = Index(
    "idx_edge_to",
    MemoryEdge.to_memory_id,
)

edge_type_index = Index(
    "idx_edge_type",
    MemoryEdge.edge_type,
)

# Composite indexes for common queries
memory_user_layer_sensitivity_index = Index(
    "idx_memory_user_layer_sensitivity",
    MemoryItem.user_id,
    MemoryItem.layer,
    MemoryItem.sensitivity,
)

task_user_status_priority_index = Index(
    "idx_task_user_status_priority",
    Task.user_id,
    Task.status,
    Task.priority,
)

# GIN indexes for text search (if using PostgreSQL full-text search)
# These would be added if implementing full-text search
# memory_content_gin_index = Index(
#     "idx_memory_content_gin",
#     text("to_tsvector('english', content)"),
#     postgresql_using='gin',
# )

__all__ = [
    "memory_user_layer_index",
    "memory_user_importance_index",
    "memory_provenance_index",
    "memory_ttl_index",
    "memory_created_at_index",
    "task_user_status_index",
    "task_user_priority_index",
    "task_due_at_index",
    "task_user_due_index",
    "edge_from_index",
    "edge_to_index",
    "edge_type_index",
    "memory_user_layer_sensitivity_index",
    "task_user_status_priority_index",
]
