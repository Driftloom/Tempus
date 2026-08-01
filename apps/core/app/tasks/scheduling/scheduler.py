"""Scheduler for daily planning."""

from datetime import datetime, timedelta

from structlog import get_logger

from app.database.models.task import Task

logger = get_logger(__name__)


class Scheduler:
    """Scheduler for generating daily schedules."""

    def __init__(self):
        """Initialize scheduler."""
        self.work_day_start = 9  # 9 AM
        self.work_day_end = 17  # 5 PM
        self.block_duration = 60  # 60 minutes
        self.break_duration = 15  # 15 minutes

    def generate_schedule(
        self,
        tasks: list[Task],
        date_str: str,
        include_calendar: bool = True
    ) -> dict:
        """Generate daily schedule from tasks."""
        logger.info("Generating schedule", date=date_str, task_count=len(tasks))

        # Parse date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Sort tasks by priority and due date
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (self._priority_score(t.priority), t.due_at or datetime.max)
        )

        # Generate time blocks
        time_blocks = []
        current_time = target_date.replace(hour=self.work_day_start, minute=0)

        for task in sorted_tasks:
            if current_time.hour >= self.work_day_end:
                break

            # Calculate block duration
            duration = task.estimated_minutes or 60
            duration = min(duration, self.block_duration)

            # Create time block
            end_time = current_time + timedelta(minutes=duration)

            time_blocks.append({
                "id": f"block-{task.id}",
                "title": task.title,
                "start_at": current_time.isoformat(),
                "end_at": end_time.isoformat(),
                "type": "focus",
                "task_id": task.id
            })

            # Add break
            current_time = end_time + timedelta(minutes=self.break_duration)

        # Identify conflicts (placeholder)
        conflicts = []

        # Identify unscheduled tasks
        unscheduled_tasks = [t.id for t in sorted_tasks[len(time_blocks):]]

        schedule = {
            "date": date_str,
            "time_blocks": time_blocks,
            "conflicts": conflicts,
            "unscheduled_tasks": unscheduled_tasks
        }

        logger.info("Schedule generated", blocks_count=len(time_blocks))
        return schedule

    def _priority_score(self, priority: str) -> int:
        """Convert priority to numeric score."""
        scores = {
            "urgent": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return scores.get(priority, 0)
