"""Integration tests for MCP connectors."""

import pytest
from app.mcp.host import MCPHost
from app.mcp.connector import MCPConnector


@pytest.mark.asyncio
async def test_mcp_host_with_connector():
    """Test MCP host with registered connector."""
    host = MCPHost()
    connector = MCPConnector("test_connector")
    
    host.register_connector(connector)
    
    assert "test_connector" in host.connectors


@pytest.mark.asyncio
async def test_mcp_connector_lifecycle():
    """Test MCP connector connection lifecycle."""
    connector = MCPConnector("test_connector")
    
    with patch.object(connector, '_establish_connection', return_value=True):
        connected = await connector.connect()
        assert connected is True
    
    with patch.object(connector, '_close_connection', return_value=True):
        disconnected = await connector.disconnect()
        assert disconnected is True


@pytest.mark.asyncio
async def test_mcp_message_roundtrip():
    """Test MCP message roundtrip through connector."""
    connector = MCPConnector("test_connector")
    
    from app.mcp.protocol import MCPMessage, MCPMessageType
    
    request = MCPMessage(
        type=MCPMessageType.REQUEST,
        id="msg1",
        method="test_method",
        params={"param1": "value1"}
    )
    
    with patch.object(connector, '_send_message', new_callable=AsyncMock) as mock_send:
        with patch.object(connector, '_receive_message', new_callable=AsyncMock) as mock_receive:
            mock_send.return_value = {"id": "msg1", "result": "success"}
            mock_receive.return_value = MCPMessage(
                type=MCPMessageType.RESPONSE,
                id="msg1",
                result={"data": "test"}
            )
            
            await connector.send(request)
            response = await connector.receive()
            
            assert response is not None
            assert response.id == "msg1"


@pytest.mark.asyncio
async def test_mcp_host_message_routing():
    """Test MCP host message routing to connector."""
    host = MCPHost()
    connector = MCPConnector("test_connector")
    host.register_connector(connector)
    
    from app.mcp.protocol import MCPMessage, MCPMessageType
    
    message = MCPMessage(
        type=MCPMessageType.REQUEST,
        id="msg1",
        method="test_method",
        params={"connector": "test_connector"}
    )
    
    with patch.object(host, '_route_message', new_callable=AsyncMock) as mock_route:
        mock_route.return_value = {"result": "success"}
        
        result = await host.handle_message(message)
        
        assert result is not None


@pytest.mark.asyncio
async def test_mcp_connector_error_handling():
    """Test MCP connector error handling."""
    connector = MCPConnector("test_connector")
    
    with patch.object(connector, '_establish_connection', side_effect=Exception("Connection failed")):
        try:
            await connector.connect()
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "Connection failed"


@pytest.mark.asyncio
async def test_mcp_multiple_connectors():
    """Test MCP host with multiple connectors."""
    host = MCPHost()
    
    connector1 = MCPConnector("connector1")
    connector2 = MCPConnector("connector2")
    connector3 = MCPConnector("connector3")
    
    host.register_connector(connector1)
    host.register_connector(connector2)
    host.register_connector(connector3)
    
    assert len(host.connectors) == 3
    assert "connector1" in host.connectors
    assert "connector2" in host.connectors
    assert "connector3" in host.connectors
