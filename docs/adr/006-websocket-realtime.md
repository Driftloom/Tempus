# ADR 006: WebSocket Real-Time Communication

## Status
Accepted

## Context
TEMPUS requires real-time bidirectional communication for:
- Live task updates and notifications
- Real-time LLM streaming responses
- Collaborative features (future)
- Extension communication (Chrome, VS Code)

HTTP polling is inefficient and introduces latency. WebSockets provide persistent connections for real-time updates.

## Decision
Use WebSocket for real-time communication with a connection manager and Redis pub/sub for multi-server support.

### Architecture
```
Client (WebSocket)
    ↓
FastAPI WebSocket Endpoint
    ↓
Connection Manager (per server)
    ↓
Redis Pub/Sub (cross-server)
    ↓
Other Servers / Services
```

### Connection Management
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
```

### Redis Pub/Sub for Multi-Server
```python
async def redis_listener():
    pubsub = redis.pubsub()
    await pubsub.subscribe("notifications")
    
    async for message in pubsub.listen():
        data = json.loads(message["data"])
        await manager.send_personal_message(data["user_id"], data)
```

### Use Cases
1. **Task Updates**: Real-time task completion notifications
2. **LLM Streaming**: Stream LLM responses token-by-token
3. **Notifications**: Push notifications to connected clients
4. **Extension Sync**: Sync state across extension instances

### Rationale
1. **Real-Time**: Instant updates without polling
2. **Efficient**: Single persistent connection vs many HTTP requests
3. **Bidirectional**: Server can push to client
4. **Scalable**: Redis pub/sub enables multi-server support
5. **Standard**: Widely supported in browsers and extensions

### Connection Lifecycle
1. **Connect**: WebSocket upgrade with JWT authentication
2. **Heartbeat**: Ping/pong every 30 seconds
3. **Reconnect**: Automatic reconnection with exponential backoff
4. **Disconnect**: Graceful close on logout or timeout

### Alternatives Considered
- **HTTP Polling**: Inefficient, high latency
- **Server-Sent Events (SSE)**: Unidirectional only
- **WebRTC**: Overkill for text-based updates
- **GraphQL Subscriptions**: Complex setup, less mature

## Consequences
### Positive
- Real-time updates with low latency
- Efficient resource usage
- Scalable with Redis pub/sub
- Works across browsers and extensions

### Negative
- Additional infrastructure (Redis pub/sub)
- Connection state management complexity
- Need to handle reconnection logic
- Firewall/proxy compatibility issues

## Implementation
```python
from fastapi import WebSocket

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    # Authenticate
    token = await websocket.receive_text()
    decoded = jwt_handler.decode_token(token)
    
    # Connect
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages
    finally:
        await manager.disconnect(user_id)
```

## References
- FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
- WebSocket RFC: https://tools.ietf.org/html/rfc6455
