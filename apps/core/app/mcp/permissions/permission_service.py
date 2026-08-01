"""Permission service for MCP skills."""


from structlog import get_logger

logger = get_logger(__name__)


class PermissionService:
    """Service for managing skill permissions."""

    def __init__(self):
        """Initialize permission service."""
        self.permissions = {}  # user_id -> {skill_id -> granted}

    async def request_permission(
        self,
        user_id: str,
        skill_id: str,
        skill_manifest: dict
    ) -> bool:
        """Request permission for skill execution."""
        logger.info("Permission requested", user_id=user_id, skill_id=skill_id)

        # Get required permissions from manifest
        required_permissions = skill_manifest.get("permissions", [])

        # Check if already granted
        if self._is_granted(user_id, skill_id):
            return True

        # In production, would prompt user for approval
        # For now, auto-grant for development
        await self._grant_permission(user_id, skill_id, required_permissions)

        return True

    async def revoke_permission(self, user_id: str, skill_id: str) -> bool:
        """Revoke permission for skill."""
        if user_id in self.permissions and skill_id in self.permissions[user_id]:
            del self.permissions[user_id][skill_id]
            logger.info("Permission revoked", user_id=user_id, skill_id=skill_id)
            return True
        return False

    async def check_permission(self, user_id: str, skill_id: str) -> bool:
        """Check if user has permission for skill."""
        return self._is_granted(user_id, skill_id)

    async def list_permissions(self, user_id: str) -> list[str]:
        """List all granted permissions for user."""
        return list(self.permissions.get(user_id, {}).keys())

    def _is_granted(self, user_id: str, skill_id: str) -> bool:
        """Check if permission is granted."""
        return (
            user_id in self.permissions and
            skill_id in self.permissions[user_id]
        )

    async def _grant_permission(
        self,
        user_id: str,
        skill_id: str,
        permissions: list[str]
    ) -> None:
        """Grant permission to user."""
        if user_id not in self.permissions:
            self.permissions[user_id] = {}

        self.permissions[user_id][skill_id] = permissions
        logger.info("Permission granted", user_id=user_id, skill_id=skill_id)
