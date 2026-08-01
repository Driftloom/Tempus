"""Unit tests for realtime module."""

from unittest.mock import AsyncMock

import pytest

from app.realtime.websocket import WebSocketConnection, WebSocketManager


@pytest.fixture
def websocket_manager():
    """Create WebSocket manager fixture."""
    return WebSocketManager()


@pytest.fixture
def websocket_connection():
    """Create WebSocket connection fixture."""
    return WebSocketConnection(
        connection_id="conn1",
        user_id="user123",
        websocket=AsyncMock()
    )


# WebSocket Manager Tests
def test_websocket_manager_initialization(websocket_manager):
    """Test WebSocket manager initialization."""
    assert websocket_manager is not None
    assert len(websocket_manager.connections) == 0


def test_websocket_manager_add_connection(websocket_manager, websocket_connection):
    """Test adding a connection."""
    websocket_manager.add_connection(websocket_connection)

    assert "conn1" in websocket_manager.connections


def test_websocket_manager_remove_connection(websocket_manager, websocket_connection):
    """Test removing a connection."""
    websocket_manager.add_connection(websocket_connection)
    websocket_manager.remove_connection("conn1")

    assert "conn1" not in websocket_manager.connections


def test_websocket_manager_get_connection(websocket_manager, websocket_connection):
    """Test getting a connection."""
    websocket_manager.add_connection(websocket_connection)

    connection = websocket_manager.get_connection("conn1")

    assert connection is not None
    assert connection.connection_id == "conn1"


def test_websocket_manager_get_user_connections(websocket_manager):
    """Test getting user connections for a specific user."""
    conn1 = WebSocketConnection("conn1", "user123", AsyncMock())
    conn2 = WebSocketConnection("conn2", "user123", AsyncMock())

    websocket_manager.add_connection(conn1)
    websocket_manager.add_connection(conn2)

    connections = websocket_manager.get_user_connections("user123")

    assert len(connections) == 2


@pytest.mark.asyncio
async def test_websocket_manager_broadcast(websocket_manager, websocket_connection):
    """Test broadcasting message to all connections."""
    websocket_manager.add_connection(websocket_connection)

    message = {"type": "notification", "data": "test"}
    await websocket_manager.broadcast(message)

    websocket_connection.websocket.send_json.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_manager_send_to_user(websocket_manager):
    """Test sending message to specific user."""
    conn1 = WebSocketConnection("conn1", "user123", AsyncMock())
    websocket_manager.add_connection(conn1)

    message = {"type": "notification", "data": "test"}
    await websocket_manager.send_to_user("user123", message)

    conn1.websocket.send_json.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_manager_send_to_connection(websocket_manager, websocket_connection):
    """Test sending message to specific connection."""
    websocket_manager.add_connection(websocket_connection)

    message = {"type": "notification", "data": "test"}
    await websocket_manager.send_to_connection("conn1", message)

    websocket_connection.websocket.send_json.assert_called_once()


# WebSocket Connection Tests
def test_websocket_connection_initialization(websocket_connection):
    """Test WebSocket connection initialization."""
    assert websocket_connection.connection_id == "conn1"
    assert websocket_connection.user_id == "user123"


def test_websocket_connection_is_active(websocket_connection):
    """Test checking if connection is active."""
    websocket_connection.active = True

    assert websocket_connection.is_active() is True


def test_websocket_connection_set_inactive(websocket_connection):
    """Test setting connection as inactive."""
    websocket_connection.set_inactive()

    assert websocket_connection.active is False


def test_websocket_connection_last_activity(websocket_connection):
    """Test last activity timestamp."""
    from datetime import datetime

    websocket_connection.update_activity()

    assert websocket_connection.last_activity is not None
    assert isinstance(websocket_connection.last_activity, datetime)


def test_websocket_connection_is_expired(websocket_connection):
    """Test checking if connection is expired."""
    from datetime import datetime, timedelta

    # Set last activity to 1 hour ago
    websocket_connection.last_activity = datetime.utcnow() - timedelta(hours=1)

    # Connection should be expired if timeout is less than 1 hour
    assert websocket_connection.is_expired(timeout_minutes=30) is True
