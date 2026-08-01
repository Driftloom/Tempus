# TEMPUS API Documentation

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.tempus.ai/api/v1
```

## Authentication

All API endpoints (except login) require JWT authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

### Login
Authenticate and receive a JWT token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

**Response (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### Get Current User
Get information about the authenticated user.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

## Tasks

### Create Task
Create a new task.

**Endpoint:** `POST /tasks`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "due_date": "2026-02-01T18:00:00Z",
  "priority": "high"
}
```

**Response (201 Created):**
```json
{
  "id": "task-123",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "due_date": "2026-02-01T18:00:00Z",
  "priority": "high",
  "status": "pending",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-29T10:00:00Z"
}
```

### List Tasks
Get all tasks for the authenticated user.

**Endpoint:** `GET /tasks`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional): Filter by status (pending, in_progress, completed)
- `priority` (optional): Filter by priority (low, medium, high)

**Response (200 OK):**
```json
{
  "tasks": [
    {
      "id": "task-123",
      "title": "Complete project documentation",
      "status": "pending",
      "priority": "high"
    }
  ],
  "total": 1
}
```

### Get Task
Get a specific task by ID.

**Endpoint:** `GET /tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "task-123",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "due_date": "2026-02-01T18:00:00Z",
  "priority": "high",
  "status": "pending",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-29T10:00:00Z"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to access this task"
}
```

### Update Task
Update an existing task.

**Endpoint:** `PATCH /tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Updated task title",
  "status": "in_progress"
}
```

**Response (200 OK):**
```json
{
  "id": "task-123",
  "title": "Updated task title",
  "status": "in_progress",
  "priority": "high"
}
```

### Complete Task
Mark a task as completed.

**Endpoint:** `POST /tasks/{task_id}/complete`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "task-123",
  "title": "Complete project documentation",
  "status": "completed",
  "completed_at": "2026-01-29T12:00:00Z"
}
```

### Delete Task
Delete a task.

**Endpoint:** `DELETE /tasks/{task_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

## Memory

### Store Memory
Store information in the memory system.

**Endpoint:** `POST /memory`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "content": "User prefers dark mode and uses TypeScript",
  "layer": "short_term",
  "sensitivity": "low"
}
```

**Response (201 Created):**
```json
{
  "id": "mem-456",
  "content": "User prefers dark mode and uses TypeScript",
  "layer": "short_term",
  "created_at": "2026-01-29T10:00:00Z"
}
```

### Query Memory
Search stored memories.

**Endpoint:** `POST /memory/query`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "query": "What are the user's preferences?",
  "layers": ["short_term", "long_term"],
  "limit": 10
}
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "mem-456",
      "content": "User prefers dark mode and uses TypeScript",
      "relevance": 0.95
    }
  ]
}
```

### Get Memory
Get a specific memory by ID.

**Endpoint:** `GET /memory/{memory_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "mem-456",
  "content": "User prefers dark mode and uses TypeScript",
  "layer": "short_term",
  "sensitivity": "low",
  "created_at": "2026-01-29T10:00:00Z"
}
```

### Delete Memory
Delete a memory.

**Endpoint:** `DELETE /memory/{memory_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "Retry-After": "60"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- **Login Endpoint**: 60 requests per minute per IP
- **API Endpoints**: 100 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## WebSocket

### Connect
Connect to real-time updates.

**Endpoint:** `WS /ws/{user_id}`

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/user123');
ws.send(JSON.stringify({ token: 'your_jwt_token' }));
```

**Message Format:**
```json
{
  "type": "task_update",
  "data": {
    "task_id": "task-123",
    "status": "completed"
  }
}
```

## SDK Examples

### Python
```python
import httpx

async def create_task(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/tasks",
            json={"title": "New task"},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### JavaScript
```javascript
async function createTask(token) {
  const response = await fetch('http://localhost:8000/api/v1/tasks', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ title: 'New task' })
  });
  return response.json();
}
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New task"}'
```
