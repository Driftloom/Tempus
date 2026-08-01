# TEMPUS System Architecture

## Overview

TEMPUS is an enterprise-grade Personal Intelligence Layer built on FastAPI with a four-layer memory architecture, multi-LLM provider support, and real-time WebSocket communication.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   Web    │  │ Extension│  │ Extension│  │  Mobile  │      │
│  │  App     │  │ (Chrome) │  │ (VS Code)│  │  App     │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Authentication│  │ Authorization│  │ Rate Limiting│  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ API Endpoints│  │ WebSocket    │  │ CORS Config  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Task Service │  │ Memory Engine│  │ Auth Service │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ LLM Manager  │  │ Notification │  │ Queue Manager │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ PostgreSQL   │  │    Redis     │  │   S3/Cloud   │         │
│  │  (Primary)   │  │  (Cache)     │  │  (Archive)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  Four-Layer Memory:                                             │
│  1. Working Memory (Redis) - Minutes                           │
│  2. Short-Term (PostgreSQL) - Days                             │
│  3. Long-Term (PostgreSQL + pgvector) - Years                   │
│  4. Archival (S3) - Indefinite                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   External Services                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Ollama  │  │ Anthropic│  │  OpenAI  │  │  Google  │      │
│  │  (Local) │  │  (Claude) │  │  (GPT-4) │  │  (Gmail) │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### API Gateway (FastAPI)
- **Authentication**: JWT-based with refresh tokens
- **Authorization**: RBAC with resource ownership checks
- **Rate Limiting**: Token bucket algorithm (60 req/min)
- **CORS**: Configurable allowed origins
- **WebSocket**: Real-time bidirectional communication

### Service Layer
- **Task Service**: Task CRUD, scheduling, NLP parsing
- **Memory Engine**: Four-layer memory management
- **Auth Service**: User management, credential validation
- **LLM Manager**: Multi-provider abstraction with fallback
- **Notification Service**: Real-time push notifications
- **Queue Manager**: Celery-based async task processing

### Data Layer
- **PostgreSQL**: Primary database with pgcrypto encryption
- **Redis**: Caching, sessions, rate limiting, working memory
- **S3/Cloud Storage**: Archival storage for historical data

### External Services
- **Ollama**: Local LLM inference (default)
- **Anthropic Claude**: High-quality LLM for complex tasks
- **OpenAI GPT-4**: Function calling capabilities
- **Google OAuth**: Gmail integration

## Data Flow

### Authentication Flow
```
1. User sends credentials to /auth/login
2. AuthService validates against database
3. JWT token generated and returned
4. Client includes token in Authorization header
5. get_current_user dependency validates token
6. Request proceeds with user context
```

### Task Creation Flow
```
1. Client POST /tasks with task data
2. Request validated and authenticated
3. TaskService creates task in database
4. NLP parser extracts metadata (due date, priority)
5. Priority scorer calculates task priority
6. Scheduler schedules task if needed
7. Notification sent via WebSocket
```

### Memory Storage Flow
```
1. User input received
2. Stored in Working Memory (Redis, TTL: 1 hour)
3. Relevance check: if important → Short-Term
4. Importance check: if valuable → Long-Term
5. Retention policy: if historical → Archival
6. Semantic search enabled on Long-Term layer
```

### LLM Query Flow
```
1. Service requests LLM completion
2. LLMManager selects provider (default: Ollama)
3. Request sent to provider
4. Response streamed via WebSocket
5. If provider fails → fallback to next provider
6. Result cached in Redis
```

## Security Architecture

### Authentication
- JWT tokens with HMAC-SHA256 signing
- Access tokens: 60-minute expiration
- Refresh tokens: 7-day expiration
- Token rotation on refresh
- Rate limiting on token generation

### Authorization
- Role-Based Access Control (RBAC)
- Resource ownership verification
- Endpoint-level permission checks
- User-scoped data isolation

### Data Security
- Database encryption at rest (pgcrypto)
- TLS/SSL for database connections
- Password hashing with bcrypt
- PII classification and protection
- Audit logging framework

## Scalability Architecture

### Horizontal Scaling
- Stateless API servers
- Redis Cluster for distributed caching
- PostgreSQL read replicas
- Load balancer with health checks

### Vertical Scaling
- Connection pooling (database, Redis)
- Async I/O throughout
- Efficient memory management
- Query optimization

### High Availability
- Database replication (planned)
- Redis clustering (planned)
- Graceful degradation
- Circuit breaker pattern

## Deployment Architecture

### Development
- Single Docker Compose stack
- Local PostgreSQL and Redis
- Ollama for LLM inference

### Production
- Kubernetes deployment
- Managed PostgreSQL (AWS RDS / GCP Cloud SQL)
- Redis Cluster (AWS ElastiCache / GCP Memorystore)
- S3 for archival storage
- CDN for static assets

## Monitoring & Observability

### Metrics
- Prometheus metrics collection
- Custom business metrics
- Performance monitoring
- Error rate tracking

### Logging
- Structured logging with structlog
- Log aggregation (ELK stack)
- Log retention policies
- Sensitive data masking

### Tracing
- Distributed tracing (planned)
- Request correlation IDs
- Performance profiling
- Bottleneck identification

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0 (async)
- **Cache**: Redis 7+
- **Queue**: Celery with Redis broker
- **ORM**: SQLAlchemy 2.0 with AsyncPG driver

### Frontend
- **Web**: React (planned)
- **Extensions**: Chrome Extension, VS Code Extension
- **Mobile**: React Native (planned)

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## Architecture Decision Records

Key architectural decisions are documented in ADRs:
- [ADR 001: Use SQLAlchemy Async with AsyncPG](./adr/001-use-sqlalchemy-async.md)
- [ADR 002: Use JWT for Authentication](./adr/002-jwt-authentication.md)
- [ADR 003: Four-Layer Memory Architecture](./adr/003-four-layer-memory.md)
- [ADR 004: Redis Caching Strategy](./adr/004-redis-caching-strategy.md)
- [ADR 005: LLM Provider Abstraction](./adr/005-llm-provider-abstraction.md)
- [ADR 006: WebSocket Real-Time Communication](./adr/006-websocket-realtime.md)
