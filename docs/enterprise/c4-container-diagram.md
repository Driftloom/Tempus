# C4 Container Diagram - TEMPUS

## Container Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TEMPUS System                                        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     Client Applications                                │  │
│  │                                                                       │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │  │
│  │  │ Chrome Extension │  │ VS Code Extension│  │  Web Dashboard   │    │  │
│  │  │                  │  │                  │  │                  │    │  │
│  │  │ - React + Vite   │  │ - Extension API  │  │ - React + Vite   │    │  │
│  │  │ - Manifest V3    │  │ - Webview        │  │ - Full UI        │    │  │
│  │  │ - Core SDK       │  │ - Core SDK       │  │ - Core SDK       │    │  │
│  │  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘    │  │
│  └───────────┼────────────────────┼────────────────────┼────────────────┘  │
│              │                    │                    │                    │
│              │ REST/WebSocket     │ REST/WebSocket     │ REST/WebSocket     │
│              │                    │                    │                    │
└──────────────┼────────────────────┼────────────────────┼────────────────────┘
               │                    │                    │
               └────────────────────┼────────────────────┘
                                    │
┌────────────────────────────────────┼──────────────────────────────────────────┐
│                                    │                                          │
│  ┌─────────────────────────────────┴───────────────────────────────────┐  │
│  │                     TEMPUS Core (FastAPI)                             │  │
│  │                                                                       │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │                    API Gateway Layer                           │  │  │
│  │  │                                                               │  │  │
│  │  │  - REST API (OpenAPI 3.0)                                     │  │  │
│  │  │  - WebSocket API                                              │  │  │
│  │  │  - Authentication (JWT + Device Auth)                        │  │  │
│  │  │  - Rate Limiting (slowapi)                                   │  │  │
│  │  │  - CORS (extension origins only)                              │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                   │                                  │  │
│  │  ┌─────────────────────────────────┴──────────────────────────────┐  │  │
│  │  │                     Service Layer                             │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │  │
│  │  │  │ Memory   │ │  Task    │ │ Router   │ │ Agent    │          │  │  │
│  │  │  │ Service  │ │ Service  │ │ Service  │ │ Runtime  │          │  │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │  │
│  │  │  │ Email    │ │ Notify   │ │ Guard    │ │ Evals    │          │  │  │
│  │  │  │ Intel    │ │ Service  │ │ Rails    │ │ Framework│          │  │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │  │  │
│  │  │  ┌──────────┐ ┌──────────┐                                     │  │  │
│  │  │  │ MCP Host │ │ Observ   │                                     │  │  │
│  │  │  │          │ │ ability  │                                     │  │  │
│  │  │  └──────────┘ └──────────┘                                     │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
┌───────────────────┴───┐ ┌────────┴────────┐ ┌─────┴────────────────┐
│   PostgreSQL          │ │     Redis       │ │   External Services   │
│                       │ │                │ │                       │
│ - pgvector            │ │ - Caching      │ │ - Ollama (Local)      │
│ - Structured Data     │ │ - Job Queue    │ │ - Anthropic (Cloud)   │
│ - Vector Search       │ │ - Sessions     │ │ - Gmail API           │
│ - Encrypted Creds     │ │ - Rate Limits  │ │ - Calendar API        │
└───────────────────────┘ └────────────────┘ └───────────────────────┘
```

## Container Descriptions

### Client Applications

#### Chrome Extension
**Type**: Browser Extension (Manifest V3)

**Technology**: React + Vite + TypeScript

**Responsibilities**:
- Side panel UI for task management
- Quick capture for natural language task entry
- Page context saving to memory
- Omnibox integration for quick task creation
- Native notification display
- WebSocket connection for real-time updates

**Key Features**:
- Content script for page context capture
- Background service worker for WebSocket
- Local storage for auth tokens
- Badge for pending task count

**Communication**: REST API + WebSocket to TEMPUS Core

#### VS Code Extension
**Type**: VS Code Extension

**Technology**: Extension API + React Webview + TypeScript

**Responsibilities**:
- Status bar time tracking display
- Command palette integration
- TODO-to-task conversion via CodeLens
- Webview dashboard for full UI
- Native notification display
- WebSocket connection for real-time updates

**Key Features**:
- CodeLens provider for TODO comments
- Secret storage for auth tokens
- Multi-window state synchronization
- Timer management

**Communication**: REST API + WebSocket to TEMPUS Core

#### Web Dashboard
**Type**: Web Application

**Technology**: React + Vite + TypeScript

**Responsibilities**:
- Full-featured web interface
- Administrative functions
- Advanced analytics and reporting
- Team management (if multi-user)
- System configuration

**Key Features**:
- Complete feature access
- Data visualization
- User management
- Audit log review

**Communication**: REST API + WebSocket to TEMPUS Core

### TEMPUS Core

#### API Gateway Layer
**Type**: FastAPI Application

**Responsibilities**:
- REST API endpoint handling
- WebSocket connection management
- Authentication and authorization
- Rate limiting
- CORS enforcement
- Request validation

**Key Components**:
- **REST API**: OpenAPI 3.0 specification
- **WebSocket API**: Real-time event streaming
- **Authentication**: JWT + Device-based auth
- **Rate Limiting**: Per-consumer limits via slowapi
- **CORS**: Locked to extension origins

**Security**:
- JWT token validation
- Device authentication
- OAuth2 flow for external services
- Input validation via Pydantic

#### Service Layer

##### Memory Service (OBSESSION)
**Type**: Python Service

**Responsibilities**:
- Four-layer memory management
- Content classification and embedding
- Memory consolidation and decay
- Hybrid retrieval (vector + metadata)
- Right-to-forget functionality

**Key Features**:
- Layer classifier (working/episodic/semantic/procedural)
- Sensitivity classifier (low/medium/high)
- Importance scoring
- Vector embedding generation
- Memory edge management
- Consolidation jobs

**Dependencies**: PostgreSQL + pgvector, Router Service

##### Task Service
**Type**: Python Service

**Responsibilities**:
- Natural language task parsing
- Task lifecycle management
- Time tracking
- Recurring task handling
- Priority scoring
- Daily planning assistance

**Key Features**:
- NL parser with date extraction
- RRULE for recurring tasks
- Pomodoro-style time tracking
- Memory-integrated priority scoring
- Calendar integration

**Dependencies**: Memory Service, Router Service

##### Router Service (Hybrid LLM Router)
**Type**: Python Service

**Responsibilities**:
- Hybrid local/cloud routing
- Provider abstraction via LiteLLM
- Response caching
- Cost tracking and budget enforcement
- Prompt template management

**Key Features**:
- Sensitivity-based routing policy
- Exact match and semantic caching
- Cost tracking per request
- Budget circuit breaker
- Template registry

**Dependencies**: Ollama (local), Anthropic (cloud), Redis (cache)

##### Agent Runtime
**Type**: Python Service

**Responsibilities**:
- Plan-act-observe-reflect loop execution
- Budget enforcement (steps, time, cost)
- State persistence and resumption
- Cancellation handling
- Progress streaming

**Key Features**:
- Generic loop engine
- Persistent state storage
- Budget tracking
- Cancellation support
- Step-by-step tracing

**Dependencies**: Router Service, MCP Host, Guardrails, Memory Service

##### Email Intelligence
**Type**: Python Service

**Responsibilities**:
- Email synchronization (Gmail, Outlook)
- Content classification and triage
- Entity extraction (deadlines, action items)
- Automatic task creation
- Daily digest generation

**Key Features**:
- Gmail and Outlook connectors
- Category classification
- Entity extraction
- Task auto-creation
- Digest generation

**Dependencies**: MCP Host, Task Service, Memory Service, Router Service

##### Notification Service
**Type**: Python Service

**Responsibilities**:
- Scheduled notification delivery
- Escalation with backoff
- Snooze and quiet hours
- Multi-surface delivery
- Missed job recovery

**Key Features**:
- Celery-based scheduling
- Escalation logic
- Quiet hours enforcement
- WebSocket delivery
- Startup recovery

**Dependencies**: Redis (Celery broker), WebSocket API

##### Guardrails
**Type**: Python Service

**Responsibilities**:
- Input validation
- PII redaction
- Injection defense
- Tool authorization
- Policy enforcement
- Output filtering

**Key Features**:
- Provenance tagging
- PII redaction via presidio
- Injection classification
- Runtime permission checks
- Declarative policy engine
- Human-in-the-loop escalation

**Dependencies**: Memory Service, Router Service

##### Evals Framework
**Type**: Python Service

**Responsibilities**:
- Golden dataset management
- Automated eval execution
- LLM-as-judge for subjective metrics
- Regression gating
- Feedback ingestion

**Key Features**:
- Dataset versioning
- Automated runners
- Pinned judge models
- CI integration
- Feedback collection

**Dependencies**: All services for evaluation

##### MCP Host
**Type**: Python Service

**Responsibilities**:
- Connector lifecycle management
- Skill execution with sandboxing
- Permission management
- Tool dispatch
- Audit logging

**Key Features**:
- MCP client connections
- Subprocess isolation
- Permission checks
- Tool authorization
- Audit trail

**Dependencies**: PostgreSQL, Redis

##### Observability
**Type**: Python Service

**Responsibilities**:
- Structured logging
- Metrics collection
- Distributed tracing
- Audit log completeness
- Performance monitoring

**Key Features**:
- Structured JSON logging
- Prometheus metrics
- OpenTelemetry tracing
- Request correlation
- Performance dashboards

**Dependencies**: Prometheus, Jaeger (tracing)

### Data Stores

#### PostgreSQL + pgvector
**Type**: Relational Database with Vector Search

**Responsibilities**:
- Primary data storage
- Structured data management
- Vector similarity search
- Encrypted credential storage
- Transaction management

**Key Features**:
- pgvector extension for embeddings
- ACID compliance
- Encryption at rest
- Backup and recovery
- High availability (enterprise)

**Data Stored**:
- Users and settings
- Tasks and time blocks
- Memory items with embeddings
- Connectors and credentials
- Agent runs and steps
- Audit logs

#### Redis
**Type**: In-Memory Data Store

**Responsibilities**:
- Response caching
- Job queue (Celery)
- Session storage
- Rate limiting counters
- Temporary state

**Key Features**:
- High-performance caching
- Pub/sub for real-time
- TTL-based expiration
- Persistence options
- Cluster support (enterprise)

### External Services

#### Ollama (Local)
**Type**: Local LLM Service

**Responsibilities**:
- Local model inference
- Privacy-preserving processing
- High-sensitivity content handling

**Key Features**:
- Local processing only
- No external calls
- Multiple model support
- HTTP API

**Used For**: High-sensitivity content processing

#### Anthropic API (Cloud)
**Type**: Cloud LLM Service

**Responsibilities**:
- Complex reasoning tasks
- Low-sensitivity content processing
- Advanced capabilities

**Key Features**:
- State-of-the-art models
- Prompt caching support
- Cost tracking
- Rate limiting

**Used For**: Low-sensitivity, high-complexity reasoning

#### Gmail API
**Type**: External Email Service

**Responsibilities**:
- Email synchronization
- OAuth2 authentication
- Message retrieval

**Key Features**:
- OAuth2 flow
- Webhook support
- Batch operations
- Label management

**Used For**: Email intelligence pipeline

#### Calendar API
**Type**: External Calendar Service

**Responsibilities**:
- Calendar synchronization
- Event management
- Free/busy information

**Key Features**:
- OAuth2 flow
- Event CRUD
- Recurring events
- Attendee management

**Used For**: Task scheduling and time blocking

## Data Flow Between Containers

### Email Processing Flow
```
Gmail API → Email Intelligence → Router (local) → 
Task Service → Memory Service → PostgreSQL
```

### Task Creation Flow
```
Chrome Extension → API Gateway → Task Service → 
Router (local/cloud) → Memory Service → PostgreSQL
```

### Agent Execution Flow
```
Web Dashboard → API Gateway → Agent Runtime → 
Router → MCP Host → External Service → 
Guardrails → Memory Service → PostgreSQL
```

### Memory Retrieval Flow
```
VS Code Extension → API Gateway → Memory Service → 
PostgreSQL (pgvector) → Router → Response
```

### Notification Flow
```
Celery Worker → Notification Service → 
WebSocket API → Chrome Extension → Native Notification
```

## Security Boundaries

### Container-Level Security
- **Client Apps**: Run in user-controlled environment
- **API Gateway**: Authentication and authorization boundary
- **Service Layer**: Internal trusted boundary
- **Data Stores**: Encrypted storage boundary
- **External Services**: Untrusted boundary

### Communication Security
- **TLS 1.3**: All external communications
- **Internal TLS**: Service-to-service in enterprise deployment
- **JWT**: API authentication
- **OAuth2**: External service authentication

### Data Security
- **Encryption at Rest**: PostgreSQL encryption
- **Encryption in Transit**: TLS for all communications
- **PII Redaction**: Before cloud calls
- **Sensitivity Routing**: Based on content classification

## Deployment Patterns

### Development Deployment
```
Single Machine:
- All services in Docker Compose
- Local PostgreSQL and Redis
- Local Ollama
- Hot reload for development
```

### Production Deployment
```
Kubernetes Cluster:
- TEMPUS Core: 3+ replicas with HPA
- PostgreSQL: Primary + replicas with pgvector
- Redis: Cluster mode
- Celery Workers: Horizontal scaling
- Load Balancer: NGINX or cloud LB
- Monitoring: Prometheus + Grafana
```

### Enterprise Deployment
```
Multi-Region:
- Regional clusters for data residency
- Global load balancing
- Disaster recovery with cross-region replication
- Compliance monitoring per region
- Centralized observability
```

## Scaling Considerations

### Horizontal Scaling
- **TEMPUS Core**: Stateless, can scale horizontally
- **Celery Workers**: Scale based on queue depth
- **PostgreSQL**: Read replicas for query scaling
- **Redis**: Cluster mode for horizontal scaling

### Vertical Scaling
- **PostgreSQL**: More CPU for vector search
- **Ollama**: GPU acceleration for local models
- **TEMPUS Core**: More memory for caching

### Caching Strategy
- **Response Cache**: Redis for LLM responses
- **Query Cache**: PostgreSQL query plan cache
- **Application Cache**: In-memory for frequently accessed data
- **CDN**: Static assets for web dashboard

## Monitoring and Observability

### Health Checks
- **TEMPUS Core**: `/health` endpoint
- **PostgreSQL**: Connection health
- **Redis**: Connection health
- **Celery Workers**: Heartbeat monitoring
- **External Services**: API health checks

### Metrics
- **Request Metrics**: Rate, latency, error rate
- **Business Metrics**: Tasks created, memory items stored, agent runs
- **System Metrics**: CPU, memory, disk, network
- **Custom Metrics**: Router decisions, cache hit rates, guardrail decisions

### Logging
- **Structured Logs**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging in enterprise
- **Audit Logs**: Separate immutable audit trail

### Tracing
- **Distributed Tracing**: OpenTelemetry across services
- **Span Context**: Request propagation
- **Trace Sampling**: Configurable sampling rate
- **Trace Storage**: Jaeger or cloud tracing

## Conclusion

The TEMPUS container diagram shows a well-architected system with clear separation of concerns, security boundaries, and scalability options. The modular design allows for independent scaling and deployment of components while maintaining the overall system integrity and performance.
