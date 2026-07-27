"""Security tests for authorization."""

import pytest
from httpx import AsyncClient
from app.main import app
from app.security.rbac import Role, Permission, RBACManager, ABACManager


@pytest.mark.asyncio
async def test_rbac_permission_check():
    """Test RBAC permission checking."""
    rbac_manager = RBACManager()
    
    # User should have user permissions
    assert rbac_manager.has_permission(Role.USER, Permission.USER_READ)
    
    # User should not have admin permissions
    assert not rbac_manager.has_permission(Role.USER, Permission.ADMIN_READ)
    
    # Admin should have admin permissions
    assert rbac_manager.has_permission(Role.ADMIN, Permission.ADMIN_READ)


@pytest.mark.asyncio
async def test_rbac_role_hierarchy():
    """Test RBAC role hierarchy."""
    rbac_manager = RBACManager()
    
    # Admin should have all user permissions
    user_permissions = rbac_manager.get_permissions_for_role(Role.USER)
    admin_permissions = rbac_manager.get_permissions_for_role(Role.ADMIN)
    
    assert user_permissions.issubset(admin_permissions)


@pytest.mark.asyncio
async def test_abac_attribute_check():
    """Test ABAC attribute-based access control."""
    abac_manager = ABACManager()
    
    # Owner can access their own resource
    assert abac_manager.check_access(
        Role.USER,
        Permission.TASK_READ,
        "user123",
        resource_id="task1",
        resource_owner_id="user123"
    )
    
    # Non-owner cannot access
    assert not abac_manager.check_access(
        Role.USER,
        Permission.TASK_READ,
        "user456",
        resource_id="task1",
        resource_owner_id="user123"
    )


@pytest.mark.asyncio
async def test_api_authorization():
    """Test API endpoint authorization."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Unauthorized request
        response = await client.get("/tasks")
        
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_admin_only_endpoint():
    """Test admin-only endpoint protection."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Regular user token
        response = await client.get(
            "/admin/users",
            headers={"Authorization": "Bearer user_token"}
        )
        
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_resource_ownership():
    """Test resource ownership enforcement."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # User trying to access another user's resource
        response = await client.get(
            "/tasks/task456",
            headers={"Authorization": "Bearer user123_token"}
        )
        
        assert response.status_code in [401, 403, 404]


@pytest.mark.asyncio
async def test_permission_inheritance():
    """Test permission inheritance."""
    rbac_manager = RBACManager()
    
    # Check if roles have expected permissions
    assert rbac_manager.has_any_permission(Role.USER, [
        Permission.USER_READ,
        Permission.TASK_READ
    ])
    
    assert rbac_manager.has_all_permissions(Role.ADMIN, [
        Permission.USER_READ,
        Permission.ADMIN_READ
    ])


@pytest.mark.asyncio
async def test_cross_user_access_prevention():
    """Test prevention of cross-user data access."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # User A trying to access User B's data
        response = await client.get(
            "/users/user456/tasks",
            headers={"Authorization": "Bearer user123_token"}
        )
        
        assert response.status_code in [401, 403]
