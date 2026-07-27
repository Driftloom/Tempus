"""Task service for task and time management."""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.task import Task, TaskStatus, TaskPriority
from app.database.models.time_block import TimeBlock
from app.database.repositories.task_repository import TaskRepository
from app.tasks.nlp.nl_parser import NLParser
from app.tasks.priority.priority_scorer import PriorityScorer
from app.tasks.scheduling.scheduler import Scheduler
from structlog import get_logger

logger = get_logger(__name__)


class TaskService:
    """Service for managing tasks and time."""
    
    def __init__(
        self,
        task_repository: TaskRepository,
        nl_parser: NLParser,
        priority_scorer: PriorityScorer,
        scheduler: Scheduler
    ):
        """Initialize task service."""
        self.task_repository = task_repository
        self.nl_parser = nl_parser
        self.priority_scorer = priority_scorer
        self.scheduler = scheduler
    
    async def create_from_nl(
        self,
        db: AsyncSession,
        user_id: str,
        input_text: str,
        source: str = "manual",
        source_ref: Optional[str] = None
    ) -> Task:
        """Create task from natural language input."""
        logger.info("Creating task from NL", user_id=user_id, input=input_text)
        
        # Parse natural language
        parsed = self.nl_parser.parse(input_text)
        
        # Calculate priority
        priority = self.priority_scorer.score(parsed)
        
        # Create task
        task_data = {
            "user_id": user_id,
            "title": parsed["title"],
            "description": parsed.get("description"),
            "status": TaskStatus.PENDING,
            "priority": priority,
            "due_at": parsed.get("due_at"),
            "estimated_minutes": parsed.get("estimated_minutes"),
            "source": source,
            "source_ref": source_ref,
            "tags": parsed.get("tags", [])
        }
        
        task = await self.task_repository.create(db, task_data)
        logger.info("Task created", task_id=task.id, title=task.title, priority=priority)
        
        return task
    
    async def get_tasks(
        self,
        db: AsyncSession,
        user_id: str,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """Get tasks for user with optional filters."""
        return await self.task_repository.get_by_user(db, user_id, status, priority)
    
    async def update_task(
        self,
        db: AsyncSession,
        task_id: str,
        updates: dict
    ) -> Optional[Task]:
        """Update task."""
        task = await self.task_repository.get(db, task_id)
        if task:
            updated = await self.task_repository.update(db, task, updates)
            logger.info("Task updated", task_id=task_id)
            return updated
        return None
    
    async def complete_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[Task]:
        """Mark task as completed."""
        task = await self.task_repository.get(db, task_id)
        if task:
            updates = {
                "status": TaskStatus.COMPLETED,
                "completed_at": datetime.utcnow()
            }
            updated = await self.task_repository.update(db, task, updates)
            logger.info("Task completed", task_id=task_id)
            return updated
        return None
    
    async def plan_day(
        self,
        db: AsyncSession,
        user_id: str,
        date: str,
        include_calendar: bool = True
    ) -> dict:
        """Generate daily schedule proposal."""
        logger.info("Planning day", user_id=user_id, date=date)
        
        # Get pending tasks
        pending_tasks = await self.task_repository.get_pending_tasks(db, user_id)
        
        # Generate schedule
        schedule = self.scheduler.generate_schedule(
            pending_tasks,
            date,
            include_calendar
        )
        
        logger.info("Day plan generated", task_count=len(pending_tasks))
        return schedule
    
    async def start_timer(
        self,
        db: AsyncSession,
        task_id: str
    ) -> dict:
        """Start time tracking for task."""
        logger.info("Starting timer", task_id=task_id)
        
        task = await self.task_repository.get(db, task_id)
        if not task:
            raise ValueError("Task not found")
        
        # Create time block
        time_block_data = {
            "user_id": task.user_id,
            "task_id": task.id,
            "title": task.title,
            "start_at": datetime.utcnow(),
            "end_at": None,
            "block_type": "focus"
        }
        
        # For now, return timer info (would create time block in full implementation)
        return {
            "timer_id": f"timer-{task_id}",
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat()
        }
    
    async def stop_timer(
        self,
        db: AsyncSession,
        task_id: str
    ) -> dict:
        """Stop time tracking for task."""
        logger.info("Stopping timer", task_id=task_id)
        
        task = await self.task_repository.get(db, task_id)
        if not task:
            raise ValueError("Task not found")
        
        # For now, return timer info (would update time block in full implementation)
        return {
            "timer_id": f"timer-{task_id}",
            "task_id": task_id,
            "stopped_at": datetime.utcnow().isoformat(),
            "duration_minutes": 30  # Placeholder
        }
