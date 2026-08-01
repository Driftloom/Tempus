"""Task repository."""


from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.task import Task, TaskPriority, TaskStatus
from app.database.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task, dict, dict]):
    """Repository for Task model."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: str,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Task]:
        """Get tasks by user with optional filters."""
        query = select(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)

        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_pending_tasks(self, db: AsyncSession, user_id: str) -> list[Task]:
        """Get all pending tasks for a user."""
        result = await db.execute(
            select(Task)
            .where(and_(Task.user_id == user_id, Task.status == TaskStatus.PENDING))
            .order_by(Task.due_at.asc().nulls_last())
        )
        return result.scalars().all()
