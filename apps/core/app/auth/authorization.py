"""Authorization utilities for RBAC and resource ownership checks."""

from enum import Enum
from typing import Callable
from functools import wraps

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

logger = get_logger(__name__)


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """Permissions for resource access."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


def require_role(required_role: UserRole):
    """Decorator to require specific user role.
    
    Args:
        required_role: Minimum required role
        
    Usage:
        @require_role(UserRole.ADMIN)
        async def admin_endpoint():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs (injected by FastAPI dependency)
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # In a full implementation, would check user's role from database
            # For now, assume all authenticated users have USER role
            # Admin role check would require role field in User model
            
            if required_role == UserRole.ADMIN:
                logger.warning("Admin access attempted but not implemented", user_id=current_user)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin role not implemented yet"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_resource_ownership(user_id: str, resource_user_id: str) -> bool:
    """Check if user owns a resource.
    
    Args:
        user_id: Current user ID
        resource_user_id: Resource owner's user ID
        
    Returns:
        True if user owns resource, False otherwise
    """
    return user_id == resource_user_id


def require_ownership(resource_user_id_getter: Callable):
    """Decorator to require resource ownership.
    
    Args:
        resource_user_id_getter: Function that extracts resource owner ID from args/kwargs
        
    Usage:
        @require_ownership(lambda kwargs: kwargs['task'].user_id)
        async def update_task(task_id: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            resource_user_id = resource_user_id_getter(kwargs)
            
            if not check_resource_ownership(current_user, resource_user_id):
                logger.warning(
                    "Ownership check failed",
                    current_user=current_user,
                    resource_owner=resource_user_id
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this resource"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def verify_user_owns_resource(
    db: AsyncSession,
    user_id: str,
    resource_type: str,
    resource_id: str
) -> bool:
    """Verify user owns a specific resource in database.
    
    Args:
        db: Database session
        user_id: Current user ID
        resource_type: Type of resource (task, memory, etc.)
        resource_id: Resource ID
        
    Returns:
        True if user owns resource, False otherwise
    """
    # This would query the database to verify ownership
    # For now, return True as placeholder
    # In full implementation:
    # - For tasks: SELECT user_id FROM tasks WHERE id = resource_id
    # - For memory: SELECT user_id FROM memory_items WHERE id = resource_id
    # - Compare with current user_id
    
    logger.info(
        "Ownership verification",
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id
    )
    
    return True  # Placeholder - implement actual database check
