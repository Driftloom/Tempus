"""Natural language parser for task creation."""

from datetime import datetime, timedelta
from typing import Optional, Dict
from dateutil import parser as date_parser
from structlog import get_logger

logger = get_logger(__name__)


class NLParser:
    """Parser for natural language task input."""
    
    def __init__(self):
        """Initialize NL parser."""
        self.date_keywords = {
            "today": 0,
            "tomorrow": 1,
            "next week": 7,
            "next month": 30
        }
    
    def parse(self, input_text: str) -> Dict:
        """Parse natural language input into structured task data."""
        logger.info("Parsing NL input", input=input_text)
        
        result = {
            "title": input_text,
            "description": None,
            "due_at": None,
            "estimated_minutes": None,
            "tags": []
        }
        
        # Extract due date
        due_at = self._extract_due_date(input_text)
        if due_at:
            result["due_at"] = due_at
            # Remove date from title
            result["title"] = self._remove_date_from_title(input_text, due_at)
        
        # Extract time estimate
        estimated_minutes = self._extract_time_estimate(input_text)
        if estimated_minutes:
            result["estimated_minutes"] = estimated_minutes
        
        # Extract tags
        tags = self._extract_tags(input_text)
        if tags:
            result["tags"] = tags
        
        logger.info("NL parsing complete", result=result)
        return result
    
    def _extract_due_date(self, text: str) -> Optional[datetime]:
        """Extract due date from text."""
        text_lower = text.lower()
        
        # Check for keyword-based dates
        for keyword, days in self.date_keywords.items():
            if keyword in text_lower:
                return datetime.utcnow() + timedelta(days=days)
        
        # Try dateutil parser for specific dates
        try:
            # Look for date patterns
            words = text.split()
            for i, word in enumerate(words):
                try:
                    parsed_date = date_parser.parse(word, fuzzy=True)
                    # Only use if it's in the future
                    if parsed_date > datetime.utcnow():
                        return parsed_date
                except:
                    continue
        except Exception as e:
            logger.debug("Date parsing failed", error=str(e))
        
        return None
    
    def _remove_date_from_title(self, title: str, due_at: datetime) -> str:
        """Remove date references from title."""
        # Simple removal - in production would use more sophisticated NLP
        date_str = due_at.strftime("%B %d").lower()
        if date_str in title.lower():
            title = title.replace(date_str, "").strip()
        
        # Clean up common date keywords
        for keyword in ["by", "due", "on", "at"]:
            if keyword in title.lower():
                title = title.replace(keyword, "").strip()
        
        return title
    
    def _extract_time_estimate(self, text: str) -> Optional[int]:
        """Extract time estimate from text."""
        text_lower = text.lower()
        
        # Look for patterns like "30 min", "2 hours", "1h"
        import re
        
        # Minutes pattern
        min_match = re.search(r'(\d+)\s*(min|minute|m)', text_lower)
        if min_match:
            return int(min_match.group(1))
        
        # Hours pattern
        hour_match = re.search(r'(\d+)\s*(hour|h)', text_lower)
        if hour_match:
            return int(hour_match.group(1)) * 60
        
        return None
    
    def _extract_tags(self, text: str) -> list:
        """Extract tags from text (hashtags or keywords)."""
        tags = []
        
        # Hashtags
        import re
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags)
        
        # Common tag keywords
        tag_keywords = ["urgent", "important", "work", "personal", "review"]
        text_lower = text.lower()
        for keyword in tag_keywords:
            if keyword in text_lower:
                tags.append(keyword)
        
        return tags
