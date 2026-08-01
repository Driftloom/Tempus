"""Task API endpoints."""


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.task import TaskPriority, TaskStatus
from app.database.session import get_db
from app.tasks.service import TaskService
from app.tasks.nlp.nl_parser import NLParser
from app.tasks.priority.priority_scorer import PriorityScorer
from app.tasks.scheduling.scheduler import Scheduler
from app.database.repositories.task_repository import TaskRepository
from app.auth.dependencies import get_current_user
from app.auth.authorization import verify_user_owns_resource

router = APIRouter()


def get_task_service() -> TaskService:
    """Dependency injection for TaskService."""
    return TaskService(
        task_repository=TaskRepository(),
        nl_parser=NLParser(),
        priority_scorer=PriorityScorer(),
        scheduler=Scheduler()
    )


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
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    task = await task_service.create_from_nl(
        db,
        current_user,
        task_data.input,
        task_data.source
    )
    return TaskResponse.model_validate(task)


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    tasks = await task_service.get_tasks(db, current_user, status, priority)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    task_repository: TaskRepository = Depends(lambda: TaskRepository())
):
    """Get a specific task."""
    # Verify ownership
    if not await verify_user_owns_resource(db, current_user, "task", task_id):
        raise HTTPException(status_code=403, detail="You do not have permission to view this task")
    
    task = await task_repository.get_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
    current_user: str = Depends(get_current_user)
):
    """Update a task."""
    # Verify ownership
    if not await verify_user_owns_resource(db, current_user, "task", task_id):
        raise HTTPException(status_code=403, detail="You do not have permission to modify this task")
    
    updates = task_data.model_dump(exclude_unset=True)
    task = await task_service.update_task(db, task_id, updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
    current_user: str = Depends(get_current_user)
):
    """Mark a task as completed."""
    # Verify ownership
    if not await verify_user_owns_resource(db, current_user, "task", task_id):
        raise HTTPException(status_code=403, detail="You do not have permission to modify this task")
    
    task = await task_service.complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)
