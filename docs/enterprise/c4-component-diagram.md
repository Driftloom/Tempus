# C4 Component Diagram - TEMPUS

## Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TEMPUS Core (Single Application)                        │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         API Gateway Layer                                  │  │
│  │                                                                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ REST API     │  │ WebSocket    │  │ Auth         │  │ Rate Limiter │  │  │
│  │  │ Controller   │  │ Controller   │  │ Middleware   │  │ Middleware   │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │  │
│  └─────────┼────────────────┼────────────────┼────────────────┼───────────────┘  │
│            │                │                │                │                  │
│  ┌─────────┼────────────────┼────────────────┼────────────────┼───────────────┐  │
│  │         │                │                │                │                  │  │
│  │  ┌──────┴────────────────┴────────────────┴────────────────┴──────────┐  │  │
│  │  │                     Service Layer                              │  │  │
│  │  │                                                                │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │  │
│  │  │  │ Memory   │ │  Task    │ │ Router   │ │ Agent    │          │  │  │
│  │  │  │ Service  │ │ Service  │ │ Service  │ │ Runtime  │          │  │  │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │  │  │
│  │  │       │            │            │            │                   │  │  │
│  │  │  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐          │  │  │
│  │  │  │ Email    │ │ Notify   │ │ Guard    │ │ Evals    │          │  │  │
│  │  │  │ Intel    │ │ Service  │ │ Rails    │ │ Framework│          │  │  │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │  │  │
│  │  │       │            │            │            │                   │  │  │
│  │  │  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐          │  │  │
│  │  │  │ MCP Host │ │ Observ   │ │ Multi-   │ │ Loop     │          │  │  │
│  │  │  │          │ │ ability  │ │ Agent    │ │ Engine   │          │  │  │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │  │  │
│  │  └───────┼────────────┼────────────┼────────────┼──────────────────┘  │  │
│  └──────────┼────────────┼────────────┼────────────┼───────────────────────┘  │
│             │            │            │            │                          │
│  ┌──────────┼────────────┼────────────┼────────────┼───────────────────────┐  │
│  │          │            │            │            │                          │  │
│  │  ┌───────┴────────────┴────────────┴────────────┴──────────────────┐  │  │
│  │  │                   Repository Layer                            │  │  │
│  │  │                                                                │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │  │
│  │  │  │ Memory   │ │  Task    │ │ Agent    │ │ User     │          │  │  │
│  │  │  │ Repo     │ │ Repo     │ │ Repo     │ │ Repo     │          │  │  │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │  │  │
│  │  │       │            │            │            │                   │  │  │
│  │  │  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐          │  │  │
│  │  │  │ Connector│ │ Notify   │ │ Skill    │ │ Config   │          │  │  │
│  │  │  │ Repo     │ │ Repo     │ │ Repo     │ │ Repo     │          │  │  │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │  │  │
│  │  └───────┼────────────┼────────────┼────────────┼──────────────────┘  │  │
│  └──────────┼────────────┼────────────┼────────────┼───────────────────────┘  │
│             │            │            │            │                          │
│  ┌──────────┼────────────┼────────────┼────────────┼───────────────────────┐  │
│  │          │            │            │            │                          │  │
│  │  ┌───────┴────────────┴────────────┴────────────┴──────────────────┐  │  │
│  │  │                   Data Access Layer                            │  │  │
│  │  │                                                                │  │  │
│  │  │  ┌────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │              SQLAlchemy ORM + AsyncSession              │  │  │  │
│  │  │  └────────────────────────────────────────────────────────┘  │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### API Gateway Layer

#### REST API Controller
**Type**: FastAPI Router

**Responsibilities**:
- HTTP request handling
- Request validation via Pydantic
- Response serialization
- Error handling and HTTP status codes
- OpenAPI documentation generation

**Key Endpoints**:
- `/api/v1/tasks` - Task management
- `/api/v1/memory` - Memory operations
- `/api/v1/agents` - Agent operations
- `/api/v1/connectors` - Connector management
- `/api/v1/notifications` - Notification management

**Dependencies**: Service Layer

#### WebSocket Controller
**Type**: FastAPI WebSocket

**Responsibilities**:
- WebSocket connection management
- Real-time event streaming
- Connection authentication
- Message routing to clients
- Connection lifecycle management

**Event Types**:
- Task events (created, completed, snoozed)
- Memory events (ingested, consolidated)
- Agent events (started, completed, failed)
- Notification events (scheduled, delivered)

**Dependencies**: Service Layer, Notification Service

#### Auth Middleware
**Type**: FastAPI Middleware

**Responsibilities**:
- JWT token validation
- Device authentication
- OAuth2 token handling
- User context extraction
- Permission verification

**Authentication Methods**:
- JWT access tokens
- Device-based authentication
- OAuth2 for external services

**Dependencies**: User Repository, Configuration

#### Rate Limiter Middleware
**Type**: FastAPI Middleware

**Responsibilities**:
- Request rate limiting
- Per-user rate limits
- Per-endpoint rate limits
- Redis-backed rate limiting
- Rate limit violation handling

**Rate Limits**:
- General: 100 requests/minute
- Task creation: 20 requests/minute
- Memory query: 50 requests/minute
- Agent execution: 10 requests/minute

**Dependencies**: Redis

### Service Layer

#### Memory Service (OBSESSION)
**Type**: Python Service

**Responsibilities**:
- Four-layer memory management
- Content classification and embedding
- Memory consolidation and decay
- Hybrid retrieval (vector + metadata)
- Right-to-forget functionality

**Key Methods**:
- `ingest_memory(content, source, user_id)` - Ingest new memory
- `query_memory(query, filters, user_id)` - Query memory
- `consolidate_memory(user_id)` - Consolidate memories
- `delete_memory(memory_id, user_id)` - Delete memory
- `get_related_memory(memory_id, user_id)` - Get related memories

**Dependencies**: Memory Repository, Router Service, PostgreSQL, Redis

#### Task Service
**Type**: Python Service

**Responsibilities**:
- Natural language task parsing
- Task lifecycle management
- Time tracking
- Recurring task handling
- Priority scoring
- Daily planning assistance

**Key Methods**:
- `create_task(input, source, user_id)` - Create task from NL
- `update_task(task_id, updates, user_id)` - Update task
- `complete_task(task_id, user_id)` - Complete task
- `snooze_task(task_id, duration, user_id)` - Snooze task
- `get_tasks(filters, user_id)` - Get tasks
- `generate_daily_plan(user_id)` - Generate daily plan

**Dependencies**: Task Repository, Router Service, Memory Service, Calendar Service

#### Router Service (Hybrid LLM Router)
**Type**: Python Service

**Responsibilities**:
- Hybrid local/cloud routing
- Provider abstraction via LiteLLM
- Response caching
- Cost tracking and budget enforcement
- Prompt template management

**Key Methods**:
- `route_request(prompt, sensitivity, user_id)` - Route to appropriate provider
- `get_response(prompt, provider, model)` - Get LLM response
- `cache_response(key, response)` - Cache response
- `track_cost(request_id, cost)` - Track cost
- `enforce_budget(user_id)` - Enforce budget limits

**Dependencies**: LiteLLM, Ollama, Anthropic API, OpenAI API, Redis

#### Agent Runtime
**Type**: Python Service

**Responsibilities**:
- Plan-act-observe-reflect loop execution
- Budget enforcement (steps, time, cost)
- State persistence and resumption
- Cancellation handling
- Progress streaming

**Key Methods**:
- `execute_agent(goal, user_id)` - Execute agent
- `pause_agent(agent_id)` - Pause agent
- `resume_agent(agent_id)` - Resume agent
- `cancel_agent(agent_id)` - Cancel agent
- `get_agent_status(agent_id)` - Get agent status

**Dependencies**: Router Service, MCP Host, Guardrails, Memory Service, Loop Engine

#### Email Intelligence
**Type**: Python Service

**Responsibilities**:
- Email synchronization (Gmail, Outlook)
- Content classification and triage
- Entity extraction (deadlines, action items)
- Automatic task creation
- Daily digest generation

**Key Methods**:
- `sync_emails(connector_id, user_id)` - Sync emails
- `classify_email(email)` - Classify email
- `extract_entities(email)` - Extract entities
- `create_tasks_from_email(email, user_id)` - Create tasks
- `generate_daily_digest(user_id)` - Generate digest

**Dependencies**: MCP Host, Task Service, Memory Service, Router Service

#### Notification Service
**Type**: Python Service

**Responsibilities**:
- Scheduled notification delivery
- Escalation with backoff
- Snooze and quiet hours
- Multi-surface delivery
- Missed job recovery

**Key Methods**:
- `schedule_notification(notification)` - Schedule notification
- `deliver_notification(notification)` - Deliver notification
- `escalate_notification(notification)` - Escalate notification
- `snooze_notification(notification, duration)` - Snooze notification
- `recover_missed_jobs()` - Recover missed jobs

**Dependencies**: Redis (Celery broker), WebSocket API, Notification Repository

#### Guardrails
**Type**: Python Service

**Responsibilities**:
- Input validation
- PII redaction
- Injection defense
- Tool authorization
- Policy enforcement
- Output filtering

**Key Methods**:
- `validate_input(input_text, context)` - Validate input
- `redact_pii(text)` - Redact PII
- `detect_injection(text)` - Detect injection
- `authorize_tool(tool, permissions)` - Authorize tool
- `filter_output(output, context)` - Filter output

**Dependencies**: Memory Service, Router Service, PII Redactor

#### Evals Framework
**Type**: Python Service

**Responsibilities**:
- Golden dataset management
- Automated eval execution
- LLM-as-judge for subjective metrics
- Regression gating
- Feedback ingestion

**Key Methods**:
- `run_eval(dataset_id, model)` - Run evaluation
- `create_dataset(name, samples)` - Create dataset
- `llm_judge(prompt, response, criteria)` - LLM-as-judge
- `check_regression(eval_result)` - Check regression
- `ingest_feedback(eval_id, feedback)` - Ingest feedback

**Dependencies**: All services for evaluation

#### MCP Host
**Type**: Python Service

**Responsibilities**:
- Connector lifecycle management
- Skill execution with sandboxing
- Permission management
- Tool dispatch
- Audit logging

**Key Methods**:
- `register_connector(connector)` - Register connector
- `execute_skill(skill_id, input, permissions)` - Execute skill
- `check_permission(skill_id, permission)` - Check permission
- `dispatch_tool(tool, input)` - Dispatch tool
- `audit_log(action, context)` - Audit log action

**Dependencies**: PostgreSQL, Redis, Skill Repository, Connector Repository

#### Observability
**Type**: Python Service

**Responsibilities**:
- Structured logging
- Metrics collection
- Distributed tracing
- Audit log completeness
- Performance monitoring

**Key Methods**:
- `log_event(event, context)` - Log event
- `record_metric(name, value, labels)` - Record metric
- `start_span(operation)` - Start span
- `audit_action(action, context)` - Audit action
- `measure_performance(operation, duration)` - Measure performance

**Dependencies**: Prometheus, Jaeger (tracing), Loki (logs)

#### Multi-Agent Orchestration
**Type**: Python Service

**Responsibilities**:
- Agent registration and management
- Concurrent/sequential orchestration
- Result merging
- Cancellation coordination
- Agent type discovery

**Key Methods**:
- `register_agent(agent_type, agent_class)` - Register agent
- `orchestrate(user_id, goal, agent_types)` - Orchestrate agents
- `merge_results(results)` - Merge results
- `cancel_all(agent_ids)` - Cancel all agents
- `list_agent_types()` - List agent types

**Dependencies**: Agent Runtime, Loop Engine

#### Loop Engine
**Type**: Python Service

**Responsibilities**:
- Agent execution lifecycle
- Start, pause, resume, cancel operations
- Active agent tracking
- State persistence
- Progress streaming

**Key Methods**:
- `start_agent(agent)` - Start agent
- `pause_agent(agent_id)` - Pause agent
- `resume_agent(agent_id)` - Resume agent
- `cancel_agent(agent_id)` - Cancel agent
- `get_status(agent_id)` - Get status

**Dependencies**: Agent State Store, Agent Runtime

### Repository Layer

#### Memory Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- Memory CRUD operations
- Vector search queries
- Memory edge management
- Memory consolidation queries

**Key Methods**:
- `create(memory)` - Create memory
- `get(memory_id)` - Get memory
- `query(query_vector, filters)` - Query memory
- `update(memory_id, updates)` - Update memory
- `delete(memory_id)` - Delete memory

**Dependencies**: PostgreSQL (pgvector)

#### Task Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- Task CRUD operations
- Task filtering and sorting
- Recurring task queries
- Time block queries

**Key Methods**:
- `create(task)` - Create task
- `get(task_id)` - Get task
- `list(filters)` - List tasks
- `update(task_id, updates)` - Update task
- `delete(task_id)` - Delete task

**Dependencies**: PostgreSQL

#### Agent Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- Agent run CRUD operations
- Agent step tracking
- Agent state persistence
- Agent history queries

**Key Methods**:
- `create_run(agent_run)` - Create agent run
- `get_run(run_id)` - Get agent run
- `create_step(step)` - Create agent step
- `update_state(run_id, state)` - Update agent state
- `get_history(user_id)` - Get agent history

**Dependencies**: PostgreSQL

#### User Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- User CRUD operations
- User settings management
- Device management
- User preferences

**Key Methods**:
- `create(user)` - Create user
- `get(user_id)` - Get user
- `update(user_id, updates)` - Update user
- `add_device(user_id, device)` - Add device
- `get_settings(user_id)` - Get settings

**Dependencies**: PostgreSQL

#### Connector Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- Connector CRUD operations
- OAuth token management
- Connector status tracking
- Connector configuration

**Key Methods**:
- `create(connector)` - Create connector
- `get(connector_id)` - Get connector
- `update_status(connector_id, status)` - Update status
- `store_token(connector_id, token)` - Store token
- `get_token(connector_id)` - Get token

**Dependencies**: PostgreSQL

#### Notification Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- Notification CRUD operations
- Scheduled notification queries
- Notification history
- Delivery tracking

**Key Methods**:
- `create(notification)` - Create notification
- `get(notification_id)` - Get notification
- `list_scheduled(user_id)` - List scheduled
- `update_status(notification_id, status)` - Update status
- `get_history(user_id)` - Get history

**Dependencies**: PostgreSQL

#### Skill Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- Skill CRUD operations
- Skill permission management
- Skill metadata
- Skill execution history

**Key Methods**:
- `create(skill)` - Create skill
- `get(skill_id)` - Get skill
- `update_permissions(skill_id, permissions)` - Update permissions
- `get_permissions(skill_id)` - Get permissions
- `log_execution(skill_id, result)` - Log execution

**Dependencies**: PostgreSQL

#### Config Repository
**Type**: SQLAlchemy Repository

**Responsibilities**:
- Configuration CRUD operations
- System settings
- Feature flags
- Configuration versioning

**Key Methods**:
- `get(key)` - Get config value
- `set(key, value)` - Set config value
- `get_all()` - Get all config
- `version_config()` - Version config
- `rollback_version(version)` - Rollback version

**Dependencies**: PostgreSQL

### Data Access Layer

#### SQLAlchemy ORM + AsyncSession
**Type**: ORM Framework

**Responsibilities**:
- Database connection management
- Query generation and execution
- Transaction management
- Model mapping
- Async database operations

**Key Features**:
- Async/await support
- Connection pooling
- Transaction management
- Query optimization
- Model validation

**Dependencies**: PostgreSQL driver (asyncpg)

## Data Flow Between Components

### Task Creation Flow
```
REST API Controller → Task Service → Router Service → Memory Service → Task Repository → PostgreSQL
```

### Memory Query Flow
```
REST API Controller → Memory Service → Memory Repository → PostgreSQL (pgvector) → Router Service
```

### Agent Execution Flow
```
REST API Controller → Agent Runtime → Loop Engine → Router Service → MCP Host → Guardrails → Memory Service
```

### Email Processing Flow
```
Celery Worker → Email Intelligence → MCP Host → Router Service → Task Service → Memory Service
```

### Notification Delivery Flow
```
Celery Worker → Notification Service → WebSocket Controller → Client Application
```

## Technology Stack

### API Layer
- **Framework**: FastAPI 0.100+
- **Validation**: Pydantic v2
- **Authentication**: python-jose (JWT), Authlib (OAuth2)
- **Rate Limiting**: slowapi
- **WebSocket**: FastAPI WebSocket

### Service Layer
- **LLM**: LiteLLM, Anthropic SDK, OpenAI SDK
- **Email**: Gmail API, Microsoft Graph API
- **Task Queue**: Celery + Redis
- **Guardrails**: presidio (PII), custom validators
- **Observability**: structlog, prometheus-client, opentelemetry

### Repository Layer
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15+ with pgvector
- **Caching**: Redis 7+
- **Migrations**: Alembic

### Data Access Layer
- **Driver**: asyncpg (PostgreSQL)
- **Connection Pooling**: SQLAlchemy pool
- **Transactions**: SQLAlchemy async transactions

## Security Boundaries

### Component-Level Security
- **API Gateway**: Authentication and authorization boundary
- **Service Layer**: Internal trusted boundary
- **Repository Layer**: Data access boundary
- **Data Access Layer**: Database connection boundary

### Communication Security
- **Internal**: All service-to-service communication trusted
- **External**: TLS 1.3 for all external communications
- **Database**: Encrypted connections to PostgreSQL
- **Redis**: Encrypted connections to Redis

## Scaling Considerations

### Horizontal Scaling
- **API Gateway**: Stateless, can scale horizontally
- **Service Layer**: Stateful services need careful scaling
- **Repository Layer**: Database connection pooling
- **Data Access Layer**: Connection pool management

### Vertical Scaling
- **API Gateway**: More CPU for request processing
- **Service Layer**: More memory for caching
- **Repository Layer**: More CPU for query processing
- **Data Access Layer**: More connections for higher throughput

### Caching Strategy
- **Service Layer**: Response caching in Redis
- **Repository Layer**: Query result caching
- **Data Access Layer**: Connection pool caching

## Monitoring Points

### API Gateway Metrics
- Request rate (by endpoint)
- Request latency (p50, p95, p99)
- Error rate (by endpoint)
- Authentication failures
- Rate limit violations

### Service Layer Metrics
- Service execution time
- Service error rate
- Cache hit rate
- External service latency
- Budget utilization

### Repository Layer Metrics
- Query execution time
- Query error rate
- Connection pool utilization
- Transaction duration
- Cache hit rate

### Data Access Layer Metrics
- Connection pool size
- Connection wait time
- Query execution time
- Transaction count
- Deadlock count

## Conclusion

The TEMPUS component diagram shows a well-structured application with clear separation of concerns across four layers: API Gateway, Service, Repository, and Data Access. The modular design allows for independent development, testing, and scaling of components while maintaining overall system integrity and performance.

Key architectural strengths:
1. Clear layer separation with well-defined boundaries
2. Service-oriented architecture with reusable services
3. Repository pattern for data access abstraction
4. Async/await throughout for scalability
5. Comprehensive observability across all layers
6. Security boundaries at each layer
