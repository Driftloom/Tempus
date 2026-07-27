"""Layer classifier for memory items."""

from app.database.models.memory import MemoryLayer
from structlog import get_logger

logger = get_logger(__name__)


class LayerClassifier:
    """Classifier for determining memory layer."""
    
    def classify(self, content: str, source: str) -> MemoryLayer:
        """Classify content into a memory layer."""
        # Working memory: current session context, short-term
        if source in ["browser", "chrome_extension"]:
            return MemoryLayer.WORKING
        
        # Episodic memory: timestamped events
        if source in ["email", "calendar"]:
            return MemoryLayer.EPISODIC
        
        # Semantic memory: stable facts and preferences
        if self._is_semantic_content(content):
            return MemoryLayer.SEMANTIC
        
        # Procedural memory: learned patterns
        if self._is_procedural_content(content):
            return MemoryLayer.PROCEDURAL
        
        # Default to episodic
        return MemoryLayer.EPISODIC
    
    def _is_semantic_content(self, content: str) -> bool:
        """Check if content is semantic (stable facts)."""
        semantic_keywords = [
            "preference", "always", "never", "usually", "typically",
            "my", "i prefer", "i like", "i dislike", "important to me"
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in semantic_keywords)
    
    def _is_procedural_content(self, content: str) -> bool:
        """Check if content is procedural (learned patterns)."""
        procedural_keywords = [
            "how to", "process", "workflow", "routine", "habit",
            "usually do", "typically do", "my process"
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in procedural_keywords)
