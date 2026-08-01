"""Unit tests for MCP module."""

from unittest.mock import AsyncMock, patch

import pytest
from app.mcp.connector import MCPConnector
from app.mcp.protocol import MCPMessage, MCPMessageType

from app.mcp.host import MCPHost


@pytest.fixture
def mcp_host():
    """Create MCP host fixture."""
    return MCPHost()


@pytest.fixture
def mcp_connector():
    """Create MCP connector fixture."""
    return MCPConnector("test_connector")


@pytest.fixture
def mcp_message():
    """Create MCP message fixture."""
    return MCPMessage(
        type=MCPMessageType.REQUEST,
        id="msg1",
        method="test_method",
        params={"param1": "value1"}
    )


# MCP Host Tests
def test_mcp_host_initialization(mcp_host):
    """Test MCP host initialization."""
    assert mcp_host is not None
    assert len(mcp_host.connectors) == 0


def test_mcp_host_register_connector(mcp_host):
    """Test registering a connector."""
    connector = MCPConnector("test_connector")
    mcp_host.register_connector(connector)

    assert "test_connector" in mcp_host.connectors


def test_mcp_host_unregister_connector(mcp_host):
    """Test unregistering a connector."""
    connector = MCPConnector("test_connector")
    mcp_host.register_connector(connector)
    mcp_host.unregister_connector("test_connector")

    assert "test_connector" not in mcp_host.connectors


@pytest.mark.asyncio
async def test_mcp_host_handle_message(mcp_host, mcp_message):
    """Test handling MCP message."""
    with patch.object(mcp_host, '_route_message', new_callable=AsyncMock) as mock_route:
        mock_route.return_value = {"result": "success"}

        result = await mcp_host.handle_message(mcp_message)

        assert result is not None


# MCP Connector Tests
def test_mcp_connector_initialization(mcp_connector):
    """Test MCP connector initialization."""
    assert mcp_connector.name == "test_connector"


@pytest.mark.asyncio
async def test_mcp_connector_connect(mcp_connector):
    """Test connector connection."""
    with patch.object(mcp_connector, '_establish_connection', return_value=True):
        result = await mcp_connector.connect()

        assert result is True


@pytest.mark.asyncio
async def test_mcp_connector_disconnect(mcp_connector):
    """Test connector disconnection."""
    with patch.object(mcp_connector, '_close_connection', return_value=True):
        result = await mcp_connector.disconnect()

        assert result is True


@pytest.mark.asyncio
async def test_mcp_connector_send(mcp_connector):
    """Test sending message through connector."""
    message = MCPMessage(
        type=MCPMessageType.REQUEST,
        id="msg1",
        method="test_method",
        params={}
    )

    with patch.object(mcp_connector, '_send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"result": "success"}

        result = await mcp_connector.send(message)

        assert result is not None


@pytest.mark.asyncio
async def test_mcp_connector_receive(mcp_connector):
    """Test receiving message through connector."""
    with patch.object(mcp_connector, '_receive_message', new_callable=AsyncMock) as mock_receive:
        mock_receive.return_value = MCPMessage(
            type=MCPMessageType.RESPONSE,
            id="msg1",
            result={"data": "test"}
        )

        result = await mcp_connector.receive()

        assert result is not None


# MCP Protocol Tests
def test_mcp_message_initialization(mcp_message):
    """Test MCP message initialization."""
    assert mcp_message.type == MCPMessageType.REQUEST
    assert mcp_message.id == "msg1"
    assert mcp_message.method == "test_method"


def test_mcp_message_type_values():
    """Test MCP message type enum values."""
    assert MCPMessageType.REQUEST.value == "request"
    assert MCPMessageType.RESPONSE.value == "response"
    assert MCPMessageType.NOTIFICATION.value == "notification"


def test_mcp_message_to_dict(mcp_message):
    """Test converting message to dictionary."""
    message_dict = mcp_message.to_dict()

    assert "type" in message_dict
    assert "id" in message_dict
    assert "method" in message_dict


def test_mcp_message_from_dict():
    """Test creating message from dictionary."""
    message_dict = {
        "type": "request",
        "id": "msg1",
        "method": "test_method",
        "params": {"param1": "value1"}
    }

    message = MCPMessage.from_dict(message_dict)

    assert message.type == MCPMessageType.REQUEST
    assert message.method == "test_method"


def test_mcp_message_validation():
    """Test MCP message validation."""
    valid_message = MCPMessage(
        type=MCPMessageType.REQUEST,
        id="msg1",
        method="test_method",
        params={}
    )

    assert valid_message.validate() is True
