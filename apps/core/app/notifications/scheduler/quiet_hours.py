"""Quiet hours logic for notifications."""

from datetime import datetime, time, timedelta
from typing import Optional
from structlog import get_logger

logger = get_logger(__name__)


class QuietHours:
    """Manager for quiet hours configuration."""
    
    def __init__(self):
        """Initialize quiet hours manager."""
        self.default_start = time(22, 0)  # 10 PM
        self.default_end = time(8, 0)  # 8 AM
    
    def is_quiet_hours(
        self,
        user_id: str,
        current_time: Optional[datetime] = None
    ) -> bool:
        """Check if current time is within quiet hours for user."""
        if current_time is None:
            current_time = datetime.utcnow()
        
        # In production, would fetch user's quiet hours from database
        # For now, use default
        start = self.default_start
        end = self.default_end
        
        current_time_only = current_time.time()
        
        # Check if current time is within quiet hours
        if start < end:
            # Same day range (e.g., 10 PM to 8 AM next day)
            return start <= current_time_only or current_time_only < end
        else:
            # Overnight range (e.g., 10 PM to 8 AM)
            return start <= current_time_only or current_time_only < end
    
    def get_next_allowed_time(
        self,
        user_id: str,
        current_time: Optional[datetime] = None
    ) -> datetime:
        """Get next time outside quiet hours."""
        if current_time is None:
            current_time = datetime.utcnow()
        
        if not self.is_quiet_hours(user_id, current_time):
            return current_time
        
        # Calculate next allowed time
        end = self.default_end
        
        # If quiet hours end today
        if end > current_time.time():
            return current_time.replace(
                hour=end.hour,
                minute=end.minute,
                second=0,
                microsecond=0
            )
        else:
            # Quiet hours end tomorrow
            return (current_time + timedelta(days=1)).replace(
                hour=end.hour,
                minute=end.minute,
                second=0,
                microsecond=0
            )
