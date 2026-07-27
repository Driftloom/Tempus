"""Task API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database.session import get_db
from app.tasks.service import TaskService
from app.database.models.task import TaskStatus, TaskPriority

router = APIRouter()


class TaskCreate(BaseModel):
    """Task creation schema."""
    input: str
    source: str = "manual"


class TaskUpdate(BaseModel):
    """Task update schema."""
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskResponse(BaseModel):
    """Task response schema."""
    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_at: str | None
    estimated_minutes: int | None
    created_at: str

    class Config:
        from_attributes = True


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = "default-user"  # Would come from auth
):
    """Create a new task from natural language input."""
    # In production, would inject TaskService via dependency
    task_service = TaskService(None, None, None, None)
    task = await task_service.create_from_nl(
        db,
        user_id,
        task_data.input,
        task_data.source
    )
    return TaskResponse.model_validate(task)


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    db: AsyncSession = Depends(get_db),
    user_id: str = "default-user"
):
    """List tasks with optional filters."""
    task_service = TaskService(None, None, None, None)
    tasks = await task_service.get_tasks(db, user_id, status, priority)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task."""
    # Implementation would fetch task by ID
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    task_service = TaskService(None, None, None, None)
    updates = task_data.model_dump(exclude_unset=True)
    task = await task_service.update_task(db, task_id, updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark a task as completed."""
    task_service = TaskService(None, None, None, None)
    task = await task_service.complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)
