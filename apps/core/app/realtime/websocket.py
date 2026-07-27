"""WebSocket endpoint for real-time updates."""

from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.auth.dependencies import get_current_user
from structlog import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a WebSocket for a user."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info("WebSocket connected", user_id=user_id, connections=len(self.active_connections[user_id]))
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a WebSocket for a user."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Clean up empty user connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info("WebSocket disconnected", user_id=user_id)
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections for a user."""
        if user_id not in self.active_connections:
            logger.warning("No active connections for user", user_id=user_id)
            return
        
        disconnected = set()
        
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("Failed to send WebSocket message", error=str(e))
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users."""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("Failed to broadcast message", user_id=user_id, error=str(e))
                    self.disconnect(connection, user_id)


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: str = Depends(get_current_user)):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "CONNECTED",
            "payload": {
                "user_id": user_id,
                "message": "Connected to TEMPUS Core"
            }
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()
            
            # Handle client messages (ping, subscribe, etc.)
            if data.get("type") == "PING":
                await websocket.send_json({
                    "type": "PONG",
                    "payload": {"timestamp": data.get("timestamp")}
                })
            elif data.get("type") == "SUBSCRIBE":
                # Handle subscription to specific event types
                logger.info("Client subscription", user_id=user_id, events=data.get("events"))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info("WebSocket disconnected by client", user_id=user_id)
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        manager.disconnect(websocket, user_id)
