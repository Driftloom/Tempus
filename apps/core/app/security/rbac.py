"""Role-Based Access Control (RBAC)."""

from enum import Enum

import structlog
from fastapi import HTTPException, status

logger = structlog.get_logger(__name__)


class Permission(str, Enum):
    """Permission enumeration."""
    # User permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # Task permissions
    TASK_READ = "task:read"
    TASK_WRITE = "task:write"
    TASK_DELETE = "task:delete"
    TASK_COMPLETE = "task:complete"

    # Memory permissions
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    MEMORY_DELETE = "memory:delete"

    # Connector permissions
    CONNECTOR_READ = "connector:read"
    CONNECTOR_WRITE = "connector:write"
    CONNECTOR_DELETE = "connector:delete"

    # Notification permissions
    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_WRITE = "notification:write"

    # Admin permissions
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_DELETE = "admin:delete"
    ADMIN_USER_MANAGE = "admin:user:manage"


class Role(str, Enum):
    """Role enumeration."""
    USER = "user"
    PREMIUM_USER = "premium_user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, set[Permission]] = {
    Role.USER: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.TASK_READ,
        Permission.TASK_WRITE,
        Permission.TASK_COMPLETE,
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.CONNECTOR_READ,
        Permission.CONNECTOR_WRITE,
        Permission.NOTIFICATION_READ,
        Permission.NOTIFICATION_WRITE,
    },
    Role.PREMIUM_USER: {
        *ROLE_PERMISSIONS[Role.USER],
        Permission.MEMORY_DELETE,
        Permission.TASK_DELETE,
    },
    Role.ADMIN: {
        *ROLE_PERMISSIONS[Role.PREMIUM_USER],
        Permission.ADMIN_READ,
        Permission.ADMIN_WRITE,
        Permission.ADMIN_USER_MANAGE,
    },
    Role.SUPER_ADMIN: {
        *ROLE_PERMISSIONS[Role.ADMIN],
        Permission.ADMIN_DELETE,
    },
}


class RBACManager:
    """Manager for RBAC operations."""

    def __init__(self):
        """Initialize RBAC manager."""
        self.role_permissions = ROLE_PERMISSIONS

    def get_permissions_for_role(self, role: Role) -> set[Permission]:
        """Get permissions for a role."""
        return self.role_permissions.get(role, set())

    def has_permission(self, role: Role, permission: Permission) -> bool:
        """Check if role has permission."""
        permissions = self.get_permissions_for_role(role)
        return permission in permissions

    def has_any_permission(self, role: Role, permissions: list[Permission]) -> bool:
        """Check if role has any of the specified permissions."""
        role_permissions = self.get_permissions_for_role(role)
        return any(perm in role_permissions for perm in permissions)

    def has_all_permissions(self, role: Role, permissions: list[Permission]) -> bool:
        """Check if role has all of the specified permissions."""
        role_permissions = self.get_permissions_for_role(role)
        return all(perm in role_permissions for perm in permissions)

    def check_permission(self, role: Role, permission: Permission) -> None:
        """Check permission and raise exception if not authorized."""
        if not self.has_permission(role, permission):
            logger.warning("Permission denied", role=role.value, permission=permission.value)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required",
            )


class ABACManager:
    """Attribute-Based Access Control (ABAC) manager."""

    def __init__(self):
        """Initialize ABAC manager."""
        self.rbac_manager = RBACManager()

    def check_access(
        self,
        role: Role,
        permission: Permission,
        user_id: str,
        resource_id: str | None = None,
        resource_owner_id: str | None = None,
        context: Dict | None = None
    ) -> bool:
        """Check access based on attributes."""
        # First check RBAC
        if not self.rbac_manager.has_permission(role, permission):
            return False

        # Resource ownership check
        if resource_owner_id and resource_id:
            if user_id == resource_owner_id:
                return True
            # Admins can access any resource
            if role in [Role.ADMIN, Role.SUPER_ADMIN]:
                return True
            return False

        # Context-based checks
        if context:
            # Add custom attribute-based logic here
            pass

        return True

    def check_access_or_raise(
        self,
        role: Role,
        permission: Permission,
        user_id: str,
        resource_id: str | None = None,
        resource_owner_id: str | None = None,
        context: Dict | None = None
    ) -> None:
        """Check access and raise exception if not authorized."""
        if not self.check_access(role, permission, user_id, resource_id, resource_owner_id, context):
            logger.warning(
                "Access denied",
                role=role.value,
                permission=permission.value,
                user_id=user_id,
                resource_id=resource_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )


# Global instances
rbac_manager = RBACManager()
abac_manager = ABACManager()
