"""Priority scorer for tasks."""

from app.database.models.task import TaskPriority
from typing import Dict
from structlog import get_logger

logger = get_logger(__name__)


class PriorityScorer:
    """Scorer for task priority based on various factors."""
    
    def __init__(self):
        """Initialize priority scorer."""
        self.urgency_keywords = ["urgent", "asap", "immediately", "critical"]
        self.importance_keywords = ["important", "priority", "key", "major"]
    
    def score(self, parsed_task: Dict) -> TaskPriority:
        """Calculate priority score for task."""
        title = parsed_task.get("title", "").lower()
        tags = parsed_task.get("tags", [])
        
        score = 0
        
        # Check for urgency keywords
        for keyword in self.urgency_keywords:
            if keyword in title:
                score += 3
        
        # Check for importance keywords
        for keyword in self.importance_keywords:
            if keyword in title:
                score += 2
        
        # Check tags
        if "urgent" in tags:
            score += 3
        if "important" in tags:
            score += 2
        
        # Due date urgency
        due_at = parsed_task.get("due_at")
        if due_at:
            from datetime import datetime, timedelta
            time_until_due = due_at - datetime.utcnow()
            if time_until_due < timedelta(hours=24):
                score += 3
            elif time_until_due < timedelta(days=3):
                score += 2
            elif time_until_due < timedelta(days=7):
                score += 1
        
        # Map score to priority
        if score >= 5:
            return TaskPriority.URGENT
        elif score >= 3:
            return TaskPriority.HIGH
        elif score >= 1:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW
