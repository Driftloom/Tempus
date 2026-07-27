# TEMPUS API Documentation

## Overview

TEMPUS exposes a comprehensive REST API and WebSocket API for client applications. All APIs are documented via OpenAPI 3.0 specification and auto-generated from FastAPI route definitions.

## API Architecture

### REST API
- **Protocol**: HTTPS (TLS 1.3)
- **Format**: JSON
- **Authentication**: JWT tokens + Device authentication
- **Rate Limiting**: Per-consumer limits via slowapi
- **CORS**: Locked to extension origins only

### WebSocket API
- **Protocol**: WSS (Secure WebSocket)
- **Authentication**: JWT token in connection URL
- **Purpose**: Real-time event streaming
- **Events**: Task updates, notifications, connector status, agent progress

## API Endpoints

### Authentication

#### POST /api/v1/auth/device/register
Register a new device and receive authentication tokens.

**Request**:
```json
{
  "device_name": "Chrome Extension",
  "device_type": "chrome_extension"
}
```

**Response**:
```json
{
  "device_id": "uuid",
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "expires_in": 3600
}
```

#### POST /api/v1/auth/refresh
Refresh an expired access token.

**Request**:
```json
{
  "refresh_token": "refresh_token"
}
```

**Response**:
```json
{
  "access_token": "new_jwt_token",
  "expires_in": 3600
}
```

### Tasks

#### GET /api/v1/tasks
List all tasks for the authenticated user.

**Query Parameters**:
- `status`: Filter by status (pending, in_progress, completed, cancelled)
- `priority`: Filter by priority (low, medium, high, urgent)
- `due_before`: Filter by due date
- `limit`: Maximum number of results (default: 50)
- `offset`: Pagination offset

**Response**:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Complete project proposal",
      "description": "Write and submit the Q3 project proposal",
      "status": "pending",
      "priority": "high",
      "due_at": "2024-07-20T17:00:00Z",
      "estimated_minutes": 120,
      "actual_minutes": 0,
      "source": "email",
      "source_ref": "gmail_message_id",
      "tags": ["work", "q3"],
      "created_at": "2024-07-15T10:00:00Z",
      "updated_at": "2024-07-15T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### POST /api/v1/tasks
Create a new task from natural language.

**Request**:
```json
{
  "input": "Finish the SafeVixAI README by tomorrow 9am",
  "source": "chrome_extension",
  "source_ref": "optional_reference"
}
```

**Response**:
```json
{
  "task": {
    "id": "uuid",
    "title": "Finish the SafeVixAI README",
    "description": null,
    "status": "pending",
    "priority": "medium",
    "due_at": "2024-07-16T09:00:00Z",
    "estimated_minutes": null,
    "actual_minutes": 0,
    "source": "chrome_extension",
    "source_ref": null,
    "tags": [],
    "created_at": "2024-07-15T10:00:00Z",
    "updated_at": "2024-07-15T10:00:00Z"
  },
  "parse_confidence": 0.95,
  "ambiguous_fields": []
}
```

#### GET /api/v1/tasks/{task_id}
Get a specific task by ID.

**Response**: Same as task object in list response.

#### PUT /api/v1/tasks/{task_id}
Update a task.

**Request**:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "high",
  "due_at": "2024-07-20T17:00:00Z",
  "estimated_minutes": 180,
  "tags": ["work", "urgent"]
}
```

**Response**: Updated task object.

#### POST /api/v1/tasks/{task_id}/complete
Mark a task as completed.

**Response**: Updated task object with status "completed".

#### POST /api/v1/tasks/{task_id}/start-time
Start time tracking for a task.

**Response**:
```json
{
  "timer_id": "uuid",
  "started_at": "2024-07-15T10:00:00Z"
}
```

#### POST /api/v1/tasks/{task_id}/stop-time
Stop time tracking for a task.

**Response**:
```json
{
  "timer_id": "uuid",
  "stopped_at": "2024-07-15T11:30:00Z",
  "duration_minutes": 90
}
```

#### POST /api/v1/tasks/plan-day
Generate a proposed daily schedule.

**Request**:
```json
{
  "date": "2024-07-16",
  "include_calendar": true
}
```

**Response**:
```json
{
  "proposal": {
    "date": "2024-07-16",
    "time_blocks": [
      {
        "id": "uuid",
        "title": "Deep Work: Project Proposal",
        "start_at": "2024-07-16T09:00:00Z",
        "end_at": "2024-07-16T12:00:00Z",
        "type": "focus",
        "task_ids": ["task_uuid"]
      }
    ],
    "conflicts": [],
    "uncheduled_tasks": ["task_uuid"]
  }
}
```

### Memory

#### POST /api/v1/memory/ingest
Ingest content into memory.

**Request**:
```json
{
  "content": "User prefers deep work blocks in the morning",
  "content_type": "text",
  "source": "user_direct",
  "source_ref": null
}
```

**Response**:
```json
{
  "memory_id": "uuid",
  "layer": "semantic",
  "sensitivity": "low",
  "importance_score": 0.8,
  "created_at": "2024-07-15T10:00:00Z"
}
```

#### POST /api/v1/memory/query
Query memory for relevant information.

**Request**:
```json
{
  "query": "internship deadline",
  "filters": {
    "layer": null,
    "sensitivity": null,
    "tags": [],
    "date_range": null
  },
  "limit": 10
}
```

**Response**:
```json
{
  "results": [
    {
      "id": "uuid",
      "content": "Applying to Microsoft SWE internship, deadline July 31",
      "layer": "semantic",
      "sensitivity": "medium",
      "importance_score": 0.9,
      "similarity": 0.85,
      "tags": ["career", "internship"],
      "created_at": "2024-07-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### DELETE /api/v1/memory/{memory_id}
Forget a specific memory item.

**Response**: 204 No Content

#### POST /api/v1/memory/forget-by-filter
Forget memories matching filters.

**Request**:
```json
{
  "filters": {
    "layer": "episodic",
    "sensitivity": "low",
    "tags": ["test"],
    "date_range": {
      "before": "2024-07-01T00:00:00Z"
    }
  }
}
```

**Response**:
```json
{
  "deleted_count": 5
}
```

### Connectors

#### GET /api/v1/connectors
List all connectors.

**Response**:
```json
{
  "connectors": [
    {
      "id": "uuid",
      "type": "gmail",
      "display_name": "Gmail",
      "status": "active",
      "last_sync_at": "2024-07-15T09:00:00Z",
      "created_at": "2024-07-01T10:00:00Z"
    }
  ]
}
```

#### POST /api/v1/connectors/{connector_type}/oauth/initiate
Initiate OAuth flow for a connector.

**Request**:
```json
{
  "redirect_uri": "chrome-extension://extension_id/oauth/callback"
}
```

**Response**:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random_state"
}
```

#### POST /api/v1/connectors/{connector_type}/oauth/callback
Complete OAuth flow.

**Request**:
```json
{
  "code": "authorization_code",
  "state": "random_state"
}
```

**Response**:
```json
{
  "connector_id": "uuid",
  "status": "active"
}
```

#### DELETE /api/v1/connectors/{connector_id}
Disconnect a connector.

**Response**: 204 No Content

#### POST /api/v1/connectors/{connector_id}/sync
Trigger manual sync for a connector.

**Response**:
```json
{
  "sync_id": "uuid",
  "status": "started"
}
```

### Skills

#### GET /api/v1/skills
List all installed skills.

**Response**:
```json
{
  "skills": [
    {
      "id": "uuid",
      "name": "plan-my-day",
      "version": "1.0.0",
      "description": "Generate daily plan from tasks and calendar",
      "enabled": true,
      "installed_at": "2024-07-01T10:00:00Z"
    }
  ]
}
```

#### POST /api/v1/skills/install
Install a skill from local path or git URL.

**Request**:
```json
{
  "source": "git",
  "url": "https://github.com/example/tempus-skill-plan-my-day.git",
  "version": "1.0.0"
}
```

**Response**:
```json
{
  "skill_id": "uuid",
  "status": "installed",
  "permissions_required": ["read_tasks", "read_memory"]
}
```

#### POST /api/v1/skills/{skill_id}/enable
Enable a skill.

**Response**: Updated skill object.

#### POST /api/v1/skills/{skill_id}/disable
Disable a skill.

**Response**: Updated skill object.

#### DELETE /api/v1/skills/{skill_id}
Uninstall a skill.

**Response**: 204 No Content

#### POST /api/v1/skills/{skill_id}/permissions/grant
Grant permissions to a skill.

**Request**:
```json
{
  "permissions": ["read_tasks", "write_tasks"]
}
```

**Response**: 204 No Content

#### POST /api/v1/skills/{skill_id}/permissions/revoke
Revoke permissions from a skill.

**Request**:
```json
{
  "permissions": ["write_tasks"]
}
```

**Response**: 204 No Content

### Notifications

#### GET /api/v1/notifications
List all notifications.

**Query Parameters**:
- `status`: Filter by status (pending, sent, dismissed, snoozed)
- `type`: Filter by type
- `limit`: Maximum number of results (default: 50)

**Response**:
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "task_due",
      "title": "Task due soon",
      "body": "Complete project proposal is due in 1 hour",
      "status": "pending",
      "scheduled_for": "2024-07-15T16:00:00Z",
      "sent_at": null,
      "related_task_id": "task_uuid"
    }
  ],
  "total": 1
}
```

#### POST /api/v1/notifications/{notification_id}/dismiss
Dismiss a notification.

**Response**: Updated notification object.

#### POST /api/v1/notifications/{notification_id}/snooze
Snooze a notification.

**Request**:
```json
{
  "duration_minutes": 30,
  "until": null
}
```

**Response**: Updated notification object.

### Agents

#### POST /api/v1/agents/runs
Start a new agent run.

**Request**:
```json
{
  "agent_type": "planning_agent",
  "goal": "Plan my day for tomorrow considering my current tasks and calendar",
  "context_refs": [],
  "budget": {
    "max_steps": 10,
    "max_duration_seconds": 300,
    "max_cost_usd": 0.50
  }
}
```

**Response**:
```json
{
  "run_id": "uuid",
  "status": "running",
  "started_at": "2024-07-15T10:00:00Z"
}
```

#### GET /api/v1/agents/runs/{run_id}
Get agent run status and steps.

**Response**:
```json
{
  "run": {
    "id": "uuid",
    "agent_type": "planning_agent",
    "goal": "Plan my day for tomorrow...",
    "status": "completed",
    "current_step_index": 5,
    "budget": {
      "max_steps": 10,
      "max_duration_seconds": 300,
      "max_cost_usd": 0.50
    },
    "cost_used_usd": 0.15,
    "started_at": "2024-07-15T10:00:00Z",
    "completed_at": "2024-07-15T10:02:30Z",
    "result_summary": "Successfully planned day with 5 focus blocks",
    "error_reason": null
  },
  "steps": [
    {
      "id": "uuid",
      "step_index": 0,
      "step_type": "plan",
      "content": "Decided to query calendar events for tomorrow",
      "tool_called": null,
      "tool_result": null,
      "cost_usd": 0.01,
      "created_at": "2024-07-15T10:00:00Z"
    }
  ]
}
```

#### POST /api/v1/agents/runs/{run_id}/cancel
Cancel an in-progress agent run.

**Response**: Updated run object with status "cancelled".

### Health & Monitoring

#### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-07-15T10:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "router": "healthy",
    "mcp_host": "healthy"
  }
}
```

#### GET /metrics
Prometheus metrics endpoint.

**Response**: Prometheus-format metrics (text/plain)

## WebSocket API

### Connection
Connect to: `wss://api.tempus.local/ws/v1/events?token=jwt_token`

### Events

#### task.updated
Emitted when a task is created, updated, or completed.

```json
{
  "event_type": "task.updated",
  "data": {
    "task_id": "uuid",
    "change_type": "completed",
    "timestamp": "2024-07-15T10:00:00Z"
  }
}
```

#### notification.created
Emitted when a new notification is created.

```json
{
  "event_type": "notification.created",
  "data": {
    "notification_id": "uuid",
    "type": "task_due",
    "title": "Task due soon",
    "body": "Complete project proposal is due in 1 hour",
    "timestamp": "2024-07-15T10:00:00Z"
  }
}
```

#### connector.status_changed
Emitted when a connector status changes.

```json
{
  "event_type": "connector.status_changed",
  "data": {
    "connector_id": "uuid",
    "connector_type": "gmail",
    "old_status": "active",
    "new_status": "error",
    "error_reason": "OAuth token expired",
    "timestamp": "2024-07-15T10:00:00Z"
  }
}
```

#### agent.step_completed
Emitted when an agent completes a step.

```json
{
  "event_type": "agent.step_completed",
  "data": {
    "run_id": "uuid",
    "step_index": 3,
    "step_type": "act",
    "content": "Called calendar tool to get events",
    "timestamp": "2024-07-15T10:00:00Z"
  }
}
```

#### agent.completed
Emitted when an agent run completes.

```json
{
  "event_type": "agent.completed",
  "data": {
    "run_id": "uuid",
    "status": "completed",
    "result_summary": "Successfully planned day with 5 focus blocks",
    "cost_used_usd": 0.15,
    "timestamp": "2024-07-15T10:02:30Z"
  }
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "due_at",
      "reason": "Invalid date format"
    },
    "request_id": "uuid"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request data
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict (e.g., duplicate)
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INTERNAL_ERROR`: Internal server error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

## Rate Limiting

Rate limits are enforced per consumer (device) and per endpoint type:

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| Task CRUD | 100 requests | 1 minute |
| Memory Query | 50 requests | 1 minute |
| Agent Execution | 5 requests | 1 minute |
| Other | 200 requests | 1 minute |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Authentication

### Device Authentication
1. Register device to get device ID and tokens
2. Include access token in Authorization header: `Bearer jwt_token`
3. Refresh token before expiration
4. Tokens are stored securely in client (chrome.storage.local, SecretStorage)

### OAuth2 Flow
1. Initiate OAuth flow with redirect URI
2. User authorizes with external service
3. Receive callback with authorization code
4. Exchange code for access/refresh tokens
5. Tokens are encrypted and stored in database

## Versioning

API versioning is done via URL path: `/api/v1/`. Breaking changes will result in a new version (`/api/v2/`). Non-breaking changes may be added to the current version.

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:
- Development: `http://localhost:8000/openapi.json`
- Production: `https://api.tempus.local/openapi.json`

Interactive API documentation (Swagger UI) is available at:
- Development: `http://localhost:8000/docs`
- Production: `https://api.tempus.local/docs`

## TypeScript Client Generation

The TypeScript client is generated from the OpenAPI specification using `openapi-typescript`:

```bash
# Generate types
pnpm --filter types generate

# Client imports from generated types
import { components } from '@tempus/types';
```

The generated client ensures type safety between the API and client applications.
