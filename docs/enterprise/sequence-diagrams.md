# Sequence Diagrams - TEMPUS

## Overview

This document provides sequence diagrams for key workflows in the TEMPUS system, illustrating the interaction between components for critical operations.

## Workflow 1: Task Creation via Natural Language

### Actors
- **User**: End user creating a task
- **Chrome Extension**: Browser extension UI
- **REST API**: FastAPI REST endpoint
- **Task Service**: Task business logic
- **Router Service**: LLM routing service
- **Memory Service**: Memory management
- **Task Repository**: Database operations
- **PostgreSQL**: Database

### Sequence Diagram

```
User → Chrome Extension: Enter task in natural language
Chrome Extension → REST API: POST /api/v1/tasks
    {
        "input": "Finish the SafeVixAI README by tomorrow 9am",
        "source": "chrome-extension"
    }
REST API → Auth Middleware: Validate JWT token
Auth Middleware → REST API: Token valid, user_id extracted
REST API → Rate Limiter: Check rate limit
Rate Limiter → REST API: Rate limit OK
REST API → Task Service: create_task(input, source, user_id)
Task Service → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Router Service: Check sensitivity level
Router Service → Router Service: Select provider (local/cloud)
Router Service → Ollama/Anthropic: Send prompt for parsing
Ollama/Anthropic → Router Service: Return parsed task data
    {
        "title": "Finish the SafeVixAI README",
        "due_at": "2026-07-23T09:00:00Z",
        "priority": "medium"
    }
Router Service → Router Service: Cache response
Router Service → Router Service: Track cost
Router Service → Task Service: Return parsed task
Task Service → Task Repository: create(task)
Task Repository → PostgreSQL: INSERT INTO tasks
PostgreSQL → Task Repository: Return created task
Task Repository → Task Service: Return task object
Task Service → Memory Service: ingest_memory(content, source, user_id)
Memory Service → Memory Repository: create(memory)
Memory Repository → PostgreSQL: INSERT INTO memory_items
PostgreSQL → Memory Repository: Return created memory
Memory Repository → Memory Service: Return memory object
Memory Service → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Generate embedding
Ollama/Anthropic → Router Service: Return embedding vector
Router Service → Memory Service: Return embedding
Memory Service → Memory Repository: update(memory_id, embedding)
Memory Repository → PostgreSQL: UPDATE memory_items SET embedding = ...
PostgreSQL → Memory Repository: Return updated memory
Memory Repository → Memory Service: Return updated memory
Memory Service → Task Service: Memory ingested
Task Service → REST API: Return created task
REST API → Chrome Extension: HTTP 200 OK
    {
        "task": {
            "id": "task-123",
            "title": "Finish the SafeVixAI README",
            "due_at": "2026-07-23T09:00:00Z",
            "priority": "medium",
            "status": "pending"
        }
    }
Chrome Extension → User: Display created task
```

### Key Points
- Natural language parsing via LLM
- Automatic due date extraction
- Memory ingestion for context
- Embedding generation for semantic search
- Rate limiting and authentication

## Workflow 2: Memory Query and Retrieval

### Actors
- **User**: End user querying memory
- **Chrome Extension**: Browser extension UI
- **REST API**: FastAPI REST endpoint
- **Memory Service**: Memory business logic
- **Memory Repository**: Database operations
- **PostgreSQL**: Database with pgvector
- **Router Service**: LLM routing service

### Sequence Diagram

```
User → Chrome Extension: Enter memory query
Chrome Extension → REST API: GET /api/v1/memory?query=SafeVixAI README
REST API → Auth Middleware: Validate JWT token
Auth Middleware → REST API: Token valid, user_id extracted
REST API → Memory Service: query_memory(query, filters, user_id)
Memory Service → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Generate query embedding
Ollama/Anthropic → Router Service: Return embedding vector
Router Service → Memory Service: Return embedding
Memory Service → Memory Repository: query(embedding, filters, user_id)
Memory Repository → PostgreSQL: SELECT * FROM memory_items
    WHERE user_id = ? AND layer = 'semantic'
    ORDER BY embedding <=> query_embedding
    LIMIT 10
PostgreSQL → Memory Repository: Return matching memories
Memory Repository → Memory Edge Repository: query_edges(memory_ids)
Memory Edge Repository → PostgreSQL: SELECT * FROM memory_edges
    WHERE source_id IN (...)
PostgreSQL → Memory Edge Repository: Return edges
Memory Edge Repository → Memory Repository: Return edges
Memory Repository → Memory Service: Return memories with edges
Memory Service → Memory Service: Rank by relevance and importance
Memory Service → Memory Service: Apply provenance filtering
Memory Service → REST API: Return query results
REST API → Chrome Extension: HTTP 200 OK
    {
        "memories": [
            {
                "id": "mem-123",
                "content": "Working on SafeVixAI README",
                "layer": "semantic",
                "importance_score": 0.85,
                "provenance": "browser",
                "related_memories": ["mem-456"]
            }
        ]
    }
Chrome Extension → User: Display memory results
```

### Key Points
- Vector similarity search via pgvector
- Memory edge traversal for related memories
- Relevance ranking and importance scoring
- Provenance-based filtering
- Query embedding generation

## Workflow 3: Agent Execution (Plan-Act-Observe-Reflect)

### Actors
- **User**: End user starting agent
- **REST API**: FastAPI REST endpoint
- **Agent Runtime**: Agent execution engine
- **Loop Engine**: Agent lifecycle management
- **Router Service**: LLM routing service
- **MCP Host**: Connector and skill host
- **Memory Service**: Memory management
- **Guardrails**: Input/output validation
- **Agent State Store**: State persistence
- **PostgreSQL**: Database

### Sequence Diagram

```
User → REST API: POST /api/v1/agents/start
    {
        "goal": "Research and summarize SafeVixAI project",
        "agent_type": "researcher"
    }
REST API → Auth Middleware: Validate JWT token
Auth Middleware → REST API: Token valid, user_id extracted
REST API → Loop Engine: start_agent(agent)
Loop Engine → Agent Runtime: execute(goal, user_id)
Agent Runtime → Agent Runtime: Set status to PLANNING
Agent Runtime → Agent State Store: save(agent_id, state)
Agent State Store → PostgreSQL: INSERT INTO agent_runs
PostgreSQL → Agent State Store: Return agent_run_id
Agent State Store → Agent Runtime: Return agent_run_id
Agent Runtime → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Generate plan
Ollama/Anthropic → Router Service: Return plan
Router Service → Agent Runtime: Return plan
Agent Runtime → Guardrails: validate_input(plan, context)
Guardrails → Guardrails: Check for injection attempts
Guardrails → Guardrails: Redact PII
Guardrails → Agent Runtime: Validation passed
Agent Runtime → Agent Runtime: Set status to ACTING
Agent Runtime → Agent State Store: save(agent_id, state)
Agent Runtime → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Generate action
Ollama/Anthropic → Router Service: Return action
Router Service → Agent Runtime: Return action
Agent Runtime → Guardrails: authorize_tool(action.tool, permissions)
Guardrails → MCP Host: check_permission(skill_id, permission)
MCP Host → Guardrails: Permission granted
Guardrails → Agent Runtime: Authorization granted
Agent Runtime → MCP Host: execute_skill(skill_id, input, permissions)
MCP Host → MCP Host: Load skill
MCP Host → MCP Host: Execute in sandbox
MCP Host → Agent Runtime: Return skill result
Agent Runtime → Agent Runtime: Set status to OBSERVING
Agent Runtime → Agent State Store: save(agent_id, state)
Agent Runtime → Memory Service: ingest_memory(observation, source, user_id)
Memory Service → Memory Repository: create(memory)
Memory Repository → PostgreSQL: INSERT INTO memory_items
PostgreSQL → Memory Repository → Memory Service → Agent Runtime
Agent Runtime → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Generate reflection
Ollama/Anthropic → Router Service: Return reflection
Router Service → Agent Runtime: Return reflection
Agent Runtime → Agent Runtime: Check completion criteria
Agent Runtime → Agent Runtime: If not complete, continue loop
Agent Runtime → Agent Runtime: Set status to COMPLETED
Agent Runtime → Agent State Store: save(agent_id, state)
Agent Runtime → Loop Engine: Return result
Loop Engine → REST API: Return agent result
REST API → User: HTTP 200 OK
    {
        "agent_run_id": "agent-123",
        "status": "completed",
        "result": "SafeVixAI project summary..."
    }
```

### Key Points
- Plan-act-observe-reflect loop
- Budget enforcement (steps, time, cost)
- State persistence for resumption
- Guardrails validation at each step
- Skill execution with sandboxing
- Memory ingestion during execution

## Workflow 4: Email Processing and Task Extraction

### Actors
- **Celery Worker**: Background task processor
- **Email Intelligence**: Email processing service
- **MCP Host**: Connector host
- **Gmail Connector**: Gmail API connector
- **Router Service**: LLM routing service
- **Task Service**: Task management
- **Memory Service**: Memory management
- **PostgreSQL**: Database

### Sequence Diagram

```
Celery Worker → Email Intelligence: sync_emails(connector_id, user_id)
Email Intelligence → MCP Host: get_connector(connector_id)
MCP Host → Connector Repository: get(connector_id)
Connector Repository → PostgreSQL: SELECT * FROM connectors
PostgreSQL → Connector Repository → MCP Host → Email Intelligence
Email Intelligence → MCP Host: execute_skill("gmail_sync", input, permissions)
MCP Host → Gmail Connector: sync_emails()
Gmail Connector → Gmail API: GET /gmail/v1/users/me/messages
Gmail API → Gmail Connector: Return messages
Gmail Connector → Email Intelligence: Return emails
Email Intelligence → Email Intelligence: Classify each email
Email Intelligence → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Classify email
Ollama/Anthropic → Router Service: Return classification
Router Service → Email Intelligence: Return classification
Email Intelligence → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Extract entities
Ollama/Anthropic → Router Service: Return entities (deadlines, action items)
Router Service → Email Intelligence: Return entities
Email Intelligence → Task Service: create_task_from_email(email, user_id)
Task Service → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Parse task from email
Ollama/Anthropic → Router Service: Return parsed task
Router Service → Task Service: Return parsed task
Task Service → Task Repository: create(task)
Task Repository → PostgreSQL: INSERT INTO tasks
PostgreSQL → Task Repository → Task Service → Email Intelligence
Email Intelligence → Memory Service: ingest_memory(email_content, source, user_id)
Memory Service → Memory Repository: create(memory)
Memory Repository → PostgreSQL: INSERT INTO memory_items
PostgreSQL → Memory Repository → Memory Service → Email Intelligence
Email Intelligence → Celery Worker: Sync complete
Celery Worker → Notification Service: schedule_notification(digest, user_id)
Notification Service → Notification Repository: create(notification)
Notification Repository → PostgreSQL: INSERT INTO notifications
PostgreSQL → Notification Repository → Notification Service
Notification Service → Celery Worker: Notification scheduled
```

### Key Points
- Background email synchronization
- Email classification and triage
- Entity extraction (deadlines, action items)
- Automatic task creation
- Memory ingestion for context
- Daily digest notification

## Workflow 5: Notification Delivery with Escalation

### Actors
- **Celery Beat**: Scheduler
- **Celery Worker**: Background task processor
- **Notification Service**: Notification management
- **Notification Repository**: Database operations
- **WebSocket Controller**: Real-time messaging
- **Chrome Extension**: Browser extension
- **PostgreSQL**: Database
- **Redis**: Celery broker

### Sequence Diagram

```
Celery Beat → Celery Worker: Trigger notification task
Celery Worker → Notification Service: deliver_notification(notification_id)
Notification Service → Notification Repository: get(notification_id)
Notification Repository → PostgreSQL: SELECT * FROM notifications
PostgreSQL → Notification Repository → Notification Service
Notification Service → Notification Service: Check quiet hours
Notification Service → Notification Service: If quiet hours, snooze
Notification Service → Notification Repository: update(notification_id, status="snoozed")
Notification Repository → PostgreSQL: UPDATE notifications
PostgreSQL → Notification Repository → Notification Service
Notification Service → WebSocket Controller: send_notification(user_id, notification)
WebSocket Controller → WebSocket Controller: Get active connections
WebSocket Controller → Chrome Extension: WebSocket message
    {
        "type": "notification",
        "data": {
            "id": "notif-123",
            "title": "Task due in 1 hour",
            "body": "Finish the SafeVixAI README"
        }
    }
Chrome Extension → User: Display notification
Chrome Extension → WebSocket Controller: ACK notification
WebSocket Controller → Notification Service: mark_delivered(notification_id)
Notification Service → Notification Repository: update(notification_id, status="delivered")
Notification Repository → PostgreSQL: UPDATE notifications
PostgreSQL → Notification Repository → Notification Service
Notification Service → Celery Worker: Delivery complete
Celery Worker → Notification Service: check_escalation(notification_id)
Notification Service → Notification Service: If not acknowledged after 30m
Notification Service → Notification Service: escalate_notification(notification_id)
Notification Service → Notification Repository: update(notification_id, escalation_level=1)
Notification Repository → PostgreSQL: UPDATE notifications
PostgreSQL → Notification Repository → Notification Service
Notification Service → WebSocket Controller: send_escalation(user_id, notification)
WebSocket Controller → Chrome Extension: Escalation notification
```

### Key Points
- Scheduled notification delivery
- Quiet hours handling
- Real-time WebSocket delivery
- Acknowledgment tracking
- Escalation with backoff
- Delivery status tracking

## Workflow 6: OAuth2 Authentication for Connector

### Actors
- **User**: End user
- **Chrome Extension**: Browser extension
- **REST API**: FastAPI REST endpoint
- **MCP Host**: Connector host
- **Connector Repository**: Database operations
- **PostgreSQL**: Database
- **External OAuth Provider**: Gmail/Outlook OAuth

### Sequence Diagram

```
User → Chrome Extension: Connect Gmail account
Chrome Extension → REST API: POST /api/v1/connectors/gmail/oauth/authorize
REST API → Auth Middleware: Validate JWT token
Auth Middleware → REST API: Token valid, user_id extracted
REST API → MCP Host: initiate_oauth_flow(connector_type, user_id)
MCP Host → MCP Host: Generate OAuth state
MCP Host → Connector Repository: create(connector)
Connector Repository → PostgreSQL: INSERT INTO connectors
PostgreSQL → Connector Repository: Return connector_id
Connector Repository → MCP Host: Return connector_id
MCP Host → External OAuth Provider: Generate authorization URL
External OAuth Provider → MCP Host: Return authorization URL
MCP Host → REST API: Return authorization URL
REST API → Chrome Extension: HTTP 200 OK
    {
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
    }
Chrome Extension → User: Redirect to authorization URL
User → External OAuth Provider: Authorize application
External OAuth Provider → Chrome Extension: Redirect with code
Chrome Extension → REST API: POST /api/v1/connectors/gmail/oauth/callback
    {
        "code": "auth_code",
        "state": "oauth_state"
    }
REST API → MCP Host: exchange_code_for_token(code, state)
MCP Host → Connector Repository: get_by_state(state)
Connector Repository → PostgreSQL: SELECT * FROM connectors WHERE state = ?
PostgreSQL → Connector Repository → MCP Host
MCP Host → External OAuth Provider: Exchange code for token
External OAuth Provider → MCP Host: Return access token, refresh token
MCP Host → Connector Repository: store_token(connector_id, tokens)
Connector Repository → PostgreSQL: UPDATE connectors SET tokens = ...
PostgreSQL → Connector Repository → MCP Host
MCP Host → Connector Repository: update_status(connector_id, "connected")
Connector Repository → PostgreSQL: UPDATE connectors SET status = 'connected'
PostgreSQL → Connector Repository → MCP Host
MCP Host → REST API: Return connector status
REST API → Chrome Extension: HTTP 200 OK
    {
        "connector_id": "connector-123",
        "status": "connected"
    }
Chrome Extension → User: Display connected status
```

### Key Points
- OAuth2 authorization code flow
- State parameter for CSRF protection
- Token storage and refresh
- Connector status tracking
- Secure token handling

## Workflow 7: Real-time WebSocket Event Streaming

### Actors
- **Chrome Extension**: Browser extension
- **WebSocket Controller**: WebSocket handler
- **REST API**: FastAPI REST endpoint
- **Notification Service**: Notification management
- **Task Service**: Task management
- **Agent Runtime**: Agent execution
- **Redis**: Pub/Sub for events

### Sequence Diagram

```
Chrome Extension → WebSocket Controller: WebSocket connection
WebSocket Controller → Auth Middleware: Validate JWT token from query param
Auth Middleware → WebSocket Controller: Token valid, user_id extracted
WebSocket Controller → WebSocket Controller: Register connection
WebSocket Controller → Chrome Extension: Connection established

Task Service → Redis: Publish event
    {
        "type": "task.created",
        "user_id": "user-123",
        "data": {
            "task_id": "task-123",
            "title": "New task"
        }
    }
Redis → WebSocket Controller: Subscribe to user channel
WebSocket Controller → Chrome Extension: Send event
    {
        "type": "task.created",
        "data": {...}
    }

Agent Runtime → Redis: Publish event
    {
        "type": "agent.started",
        "user_id": "user-123",
        "data": {
            "agent_id": "agent-123",
            "goal": "Research task"
        }
    }
Redis → WebSocket Controller: Receive event
WebSocket Controller → Chrome Extension: Send event
    {
        "type": "agent.started",
        "data": {...}
    }

Notification Service → Redis: Publish event
    {
        "type": "notification.delivered",
        "user_id": "user-123",
        "data": {
            "notification_id": "notif-123",
            "title": "Task due"
        }
    }
Redis → WebSocket Controller: Receive event
WebSocket Controller → Chrome Extension: Send event
    {
        "type": "notification.delivered",
        "data": {...}
    }

Chrome Extension → WebSocket Controller: Disconnect
WebSocket Controller → WebSocket Controller: Unregister connection
WebSocket Controller → Chrome Extension: Connection closed
```

### Key Points
- Real-time event streaming via WebSocket
- Redis Pub/Sub for event distribution
- User-specific event filtering
- Connection lifecycle management
- Event type routing

## Workflow 8: Memory Consolidation

### Actors
- **Celery Beat**: Scheduler
- **Celery Worker**: Background task processor
- **Memory Service**: Memory management
- **Memory Repository**: Database operations
- **Router Service**: LLM routing service
- **PostgreSQL**: Database

### Sequence Diagram

```
Celery Beat → Celery Worker: Trigger memory consolidation task
Celery Worker → Memory Service: consolidate_memory(user_id)
Memory Service → Memory Repository: get_consolidation_candidates(user_id)
Memory Repository → PostgreSQL: SELECT * FROM memory_items
    WHERE user_id = ? AND layer = 'working'
    AND created_at < NOW() - INTERVAL '24 hours'
PostgreSQL → Memory Repository: Return candidate memories
Memory Repository → Memory Service: Return candidates
Memory Service → Router Service: route_request(prompt, sensitivity, user_id)
Router Service → Ollama/Anthropic: Consolidate memories
Ollama/Anthropic → Router Service: Return consolidated memory
Router Service → Memory Service: Return consolidated memory
Memory Service → Memory Repository: create(consolidated_memory)
Memory Repository → PostgreSQL: INSERT INTO memory_items (layer='semantic')
PostgreSQL → Memory Repository → Memory Service
Memory Service → Memory Repository: create_memory_edges(source_ids, target_id)
Memory Edge Repository → PostgreSQL: INSERT INTO memory_edges
PostgreSQL → Memory Edge Repository → Memory Service
Memory Service → Memory Repository: mark_consolidated(source_ids)
Memory Repository → PostgreSQL: UPDATE memory_items SET consolidated = true
PostgreSQL → Memory Repository → Memory Service
Memory Service → Celery Worker: Consolidation complete
```

### Key Points
- Scheduled memory consolidation
- Working to semantic layer promotion
- Memory edge creation for relationships
- Consolidation tracking
- Batch processing

## Conclusion

These sequence diagrams illustrate the key workflows in the TEMPUS system, showing how components interact to deliver core functionality. The diagrams cover:

1. **Task Creation**: Natural language parsing, memory ingestion, embedding generation
2. **Memory Query**: Vector search, edge traversal, relevance ranking
3. **Agent Execution**: Plan-act-observe-reflect loop, guardrails, state persistence
4. **Email Processing**: Background sync, classification, task extraction
5. **Notification Delivery**: Scheduling, escalation, real-time delivery
6. **OAuth2 Authentication**: Authorization flow, token management
7. **WebSocket Streaming**: Real-time events, connection management
8. **Memory Consolidation**: Scheduled consolidation, layer promotion

These workflows demonstrate the system's core capabilities and the interactions between services, repositories, and external systems.
