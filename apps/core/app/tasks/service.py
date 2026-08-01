"""Task service for task and time management."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.database.models.task import Task, TaskPriority, TaskStatus
from app.database.repositories.task_repository import TaskRepository
from app.tasks.nlp.nl_parser import NLParser
from app.tasks.priority.priority_scorer import PriorityScorer
from app.tasks.scheduling.scheduler import Scheduler

logger = get_logger(__name__)


class TaskService:
    """Service for managing tasks and time."""

    def __init__(
        self,
        task_repository: TaskRepository,
        nl_parser: NLParser,
        priority_scorer: PriorityScorer,
        scheduler: Scheduler
    ) -> None:
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
        source_ref: str | None = None
    ) -> Task:
        """Create task from natural language input.
        
        Args:
            db: Database session
            user_id: User ID creating the task
            input_text: Natural language task description
            source: Source of the task (manual, email, etc.)
            source_ref: Reference ID from source
            
        Returns:
            Created Task object
        """
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
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None
    ) -> list[Task]:
        """Get tasks for user with optional filters.
        
        Args:
            db: Database session
            user_id: User ID to get tasks for
            status: Optional status filter
            priority: Optional priority filter
            
        Returns:
            List of Task objects matching filters
        """
        return await self.task_repository.get_by_user(db, user_id, status, priority)

    async def update_task(
        self,
        db: AsyncSession,
        task_id: str,
        updates: dict
    ) -> Task | None:
        """Update task with provided fields.
        
        Args:
            db: Database session
            task_id: Task ID to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated Task object or None if not found
        """
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
    ) -> Task | None:
        """Mark task as completed.
        
        Args:
            db: Database session
            task_id: Task ID to complete
            
        Returns:
            Updated Task object or None if not found
        """
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
        """Generate daily schedule proposal.
        
        Args:
            db: Database session
            user_id: User ID to plan for
            date: Date to plan (YYYY-MM-DD format)
            include_calendar: Whether to include calendar events
            
        Returns:
            Dictionary with schedule proposal
        """
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
        """Start time tracking for task.
        
        Args:
            db: Database session
            task_id: Task ID to start timer for
            
        Returns:
            Dictionary with timer start information
            
        Raises:
            ValueError: If task not found
        """
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
        """Stop time tracking for task.
        
        Args:
            db: Database session
            task_id: Task ID to stop timer for
            
        Returns:
            Dictionary with timer stop information
            
        Raises:
            ValueError: If task not found
        """
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
