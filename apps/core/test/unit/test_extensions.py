"""Unit tests for extensions module."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.extensions.sdk import TEMPUSClient, BaseExtension
from app.extensions.plugin import PluginManager, PluginValidator
from app.extensions.webhooks import WebhookHandler, WebhookValidator


@pytest.fixture
def tempus_client():
    """Create TEMPUS client fixture."""
    return TEMPUSClient(base_url="http://localhost:8000", api_key="test_key")


@pytest.fixture
def plugin_manager():
    """Create plugin manager fixture."""
    return PluginManager()


@pytest.fixture
def plugin_validator():
    """Create plugin validator fixture."""
    return PluginValidator()


@pytest.fixture
def webhook_handler():
    """Create webhook handler fixture."""
    return WebhookHandler()


@pytest.fixture
def webhook_validator():
    """Create webhook validator fixture."""
    return WebhookValidator()


# TEMPUS Client Tests
def test_tempus_client_initialization(tempus_client):
    """Test TEMPUS client initialization."""
    assert tempus_client.base_url == "http://localhost:8000"
    assert tempus_client.api_key == "test_key"


@pytest.mark.asyncio
async def test_tempus_client_create_task(tempus_client):
    """Test task creation via client."""
    with patch.object(tempus_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"id": "task1", "title": "Test Task"}
        
        result = await tempus_client.create_task({"title": "Test Task"})
        
        assert result["id"] == "task1"
        mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_tempus_client_get_memory(tempus_client):
    """Test memory retrieval via client."""
    with patch.object(tempus_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"id": "mem1", "content": "Test memory"}
        
        result = await tempus_client.get_memory("mem1")
        
        assert result["id"] == "mem1"
        mock_request.assert_called_once()


# Base Extension Tests
def test_base_extension_initialization():
    """Test base extension initialization."""
    extension = BaseExtension(name="test_extension", version="1.0.0")
    
    assert extension.name == "test_extension"
    assert extension.version == "1.0.0"


@pytest.mark.asyncio
async def test_base_extension_on_load():
    """Test extension on_load lifecycle."""
    extension = BaseExtension(name="test_extension", version="1.0.0")
    
    await extension.on_load()
    
    # Should not raise exception
    assert True


@pytest.mark.asyncio
async def test_base_extension_on_unload():
    """Test extension on_unload lifecycle."""
    extension = BaseExtension(name="test_extension", version="1.0.0")
    
    await extension.on_unload()
    
    # Should not raise exception
    assert True


# Plugin Manager Tests
def test_plugin_manager_initialization(plugin_manager):
    """Test plugin manager initialization."""
    assert plugin_manager is not None
    assert len(plugin_manager.loaded_plugins) == 0


@pytest.mark.asyncio
async def test_plugin_manager_load_plugin(plugin_manager):
    """Test plugin loading."""
    plugin = BaseExtension(name="test_plugin", version="1.0.0")
    
    with patch.object(plugin, 'on_load', new_callable=AsyncMock):
        await plugin_manager.load_plugin(plugin)
    
    assert "test_plugin" in plugin_manager.loaded_plugins


@pytest.mark.asyncio
async def test_plugin_manager_unload_plugin(plugin_manager):
    """Test plugin unloading."""
    plugin = BaseExtension(name="test_plugin", version="1.0.0")
    
    with patch.object(plugin, 'on_load', new_callable=AsyncMock):
        with patch.object(plugin, 'on_unload', new_callable=AsyncMock):
            await plugin_manager.load_plugin(plugin)
            await plugin_manager.unload_plugin("test_plugin")
    
    assert "test_plugin" not in plugin_manager.loaded_plugins


# Plugin Validator Tests
def test_plugin_validator_validate_metadata(plugin_validator):
    """Test plugin metadata validation."""
    metadata = {
        "name": "test_plugin",
        "version": "1.0.0",
        "description": "Test plugin",
        "author": "Test Author",
    }
    
    result = plugin_validator.validate_metadata(metadata)
    
    assert result is True


def test_plugin_validator_validate_invalid_metadata(plugin_validator):
    """Test invalid plugin metadata validation."""
    metadata = {
        "name": "",  # Invalid empty name
        "version": "1.0.0",
    }
    
    result = plugin_validator.validate_metadata(metadata)
    
    assert result is False


def test_plugin_validator_validate_permissions(plugin_validator):
    """Test plugin permissions validation."""
    permissions = ["read:tasks", "write:tasks"]
    
    result = plugin_validator.validate_permissions(permissions)
    
    assert result is True


def test_plugin_validator_validate_invalid_permissions(plugin_validator):
    """Test invalid plugin permissions validation."""
    permissions = ["admin:delete_all"]  # Invalid permission
    
    result = plugin_validator.validate_permissions(permissions)
    
    assert result is False


# Webhook Handler Tests
def test_webhook_handler_register(webhook_handler):
    """Test webhook registration."""
    async def handler(event):
        return {"status": "ok"}
    
    webhook_handler.register("test_event", handler)
    
    assert "test_event" in webhook_handler.handlers


@pytest.mark.asyncio
async def test_webhook_handler_broadcast(webhook_handler):
    """Test webhook broadcasting."""
    received_events = []
    
    async def handler(event):
        received_events.append(event)
    
    webhook_handler.register("test_event", handler)
    await webhook_handler.broadcast("test_event", {"data": "test"})
    
    assert len(received_events) == 1


# Webhook Validator Tests
def test_webhook_validator_validate_payload(webhook_validator):
    """Test webhook payload validation."""
    payload = {
        "event_type": "task.created",
        "data": {"task_id": "123"},
        "timestamp": "2024-01-01T00:00:00Z",
    }
    
    result = webhook_validator.validate_payload(payload)
    
    assert result is True


def test_webhook_validator_validate_invalid_payload(webhook_validator):
    """Test invalid webhook payload validation."""
    payload = {
        "event_type": "",  # Invalid empty event type
        "data": {},
    }
    
    result = webhook_validator.validate_payload(payload)
    
    assert result is False


def test_webhook_validator_validate_url(webhook_validator):
    """Test webhook URL validation."""
    url = "https://example.com/webhook"
    
    result = webhook_validator.validate_url(url)
    
    assert result is True


def test_webhook_validator_validate_invalid_url(webhook_validator):
    """Test invalid webhook URL validation."""
    url = "not-a-url"
    
    result = webhook_validator.validate_url(url)
    
    assert result is False
