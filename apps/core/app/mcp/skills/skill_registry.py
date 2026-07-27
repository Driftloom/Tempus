"""Skill registry for MCP skills."""

from typing import Dict, List
from structlog import get_logger

logger = get_logger(__name__)


class SkillRegistry:
    """Registry for available MCP skills."""
    
    def __init__(self):
        """Initialize skill registry."""
        self.skills = {}  # skill_id -> manifest
    
    def register(self, skill_id: str, manifest: Dict) -> bool:
        """Register a skill in the registry."""
        logger.info("Registering skill in registry", skill_id=skill_id)
        
        # Validate manifest
        if not self._validate_manifest(manifest):
            logger.error("Invalid skill manifest", skill_id=skill_id)
            return False
        
        self.skills[skill_id] = manifest
        logger.info("Skill registered", skill_id=skill_id)
        return True
    
    def get(self, skill_id: str) -> Optional[Dict]:
        """Get skill manifest."""
        return self.skills.get(skill_id)
    
    def list_all(self) -> List[Dict]:
        """List all registered skills."""
        return list(self.skills.values())
    
    def list_by_category(self, category: str) -> List[Dict]:
        """List skills by category."""
        return [
            skill for skill in self.skills.values()
            if skill.get("category") == category
        ]
    
    def _validate_manifest(self, manifest: Dict) -> bool:
        """Validate skill manifest."""
        required_fields = [
            "name",
            "version",
            "description",
            "category",
            "permissions",
            "parameters"
        ]
        return all(field in manifest for field in required_fields)
