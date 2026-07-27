# TEMPUS Architecture Overview

## System Purpose

TEMPUS is an enterprise-grade personal intelligence layer that provides continuous task management, intelligent email processing, persistent layered memory, and governed multi-agent automation through a secure, self-hosted platform.

## Architectural Principles

### 1. Privacy-First Design
- **Hybrid Routing**: Sensitive data processed locally, complex reasoning in cloud
- **Data Sovereignty**: User data never leaves premises without explicit consent
- **Encryption**: All sensitive data encrypted at rest and in transit
- **Audit Trail**: Complete audit logging for all data access and actions

### 2. Governed Autonomy
- **Permission Model**: Fine-grained permissions for all capabilities
- **Guardrails**: Multi-layer security checks before any autonomous action
- **Human-in-the-Loop**: Escalation for irreversible or high-impact actions
- **Policy Engine**: Declarative rules for acceptable behavior

### 3. Extensibility
- **Standard Protocols**: MCP for connectors/skills, OpenAPI for integrations
- **Plugin Architecture**: Connector and skill marketplace
- **Open Source**: Transparent, community-extensible
- **No Lock-in**: Self-hosted, standard protocols, portable data

### 4. Reliability
- **Resilience**: Graceful degradation, automatic recovery
- **Observability**: Complete logging, metrics, and tracing
- **Testing**: Comprehensive test coverage with regression gating
- **Disaster Recovery**: Backup, restore, and business continuity

## High-Level Architecture

TEMPUS follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Layer                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐│
│  │ Chrome Extension │  │ VS Code Extension│  │  Web Dashboard  ││
│  └──────────────────┘  └──────────────────┘  └────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              ↕ REST/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  FastAPI + OpenAPI + Rate Limiting + CORS + Auth           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                   Service Layer                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐│
│  │ Memory   │ │  Task    │ │ Router   │ │ Agent    │ │ MCP   ││
│  │ Service  │ │ Service  │ │ Service  │ │ Runtime  │ │ Host  ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────┘│
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Email    │ │ Notify   │ │ Guard    │ │ Evals    │          │
│  │ Intel    │ │ Service  │ │ Rails    │ │ Framework│          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                   Data Layer                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL + pgvector (Structured + Vector Data)          │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Redis (Caching + Job Queue)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│              External Integrations                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Ollama  │ │ Anthropic│ │  Gmail   │ │ Calendar │          │
│  │ (Local)  │ │  Claude  │ │          │ │          │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Core Components

#### 1. Memory Engine (OBSESSION)
**Purpose**: Four-layer persistent memory system

**Layers**:
- **Working Memory**: Current session context (TTL: minutes-hours)
- **Episodic Memory**: Timestamped events (decays if unreferenced)
- **Semantic Memory**: Stable facts and preferences (persistent)
- **Procedural Memory**: Learned patterns (reinforced by repetition)

**Key Features**:
- Automatic classification and embedding
- Hybrid retrieval (vector + recency + importance)
- Consolidation and decay jobs
- Right-to-forget API

#### 2. Task & Time Engine
**Purpose**: Natural language task parsing and time management

**Key Features**:
- NL task capture with date parsing
- Recurring tasks via RRULE
- Time tracking with Pomodoro support
- Priority scoring with memory integration
- Daily planning with agent assistance

#### 3. Hybrid LLM Router
**Purpose**: Intelligent routing between local and cloud models

**Routing Policy**:
- High sensitivity → Local only
- Medium sensitivity → Local default, cloud with justification
- Low sensitivity + high complexity → Cloud preferred
- Low sensitivity + low complexity → Local preferred

**Key Features**:
- Provider abstraction via LiteLLM
- Response caching (exact match + semantic)
- Cost tracking and budget enforcement
- Prompt template registry

#### 4. MCP Host
**Purpose**: Extensibility framework for connectors and skills

**Extension Types**:
- **Connectors**: External data sources (Gmail, Calendar, Slack)
- **Skills**: Deterministic capabilities (classify, extract)
- **Plugins**: UI extensions (Chrome, VS Code)

**Key Features**:
- Standard MCP protocol
- Permission model with runtime checks
- Subprocess isolation for skills
- Audit logging for all actions

#### 5. Agent Runtime
**Purpose**: Plan-act-observe-reflect loop for open-ended goals

**Loop Steps**:
1. **Plan**: Decide next action via Router
2. **Act**: Execute tool through Guardrails
3. **Observe**: Capture result to working memory
4. **Reflect**: Assess goal completion
5. **Improve**: Loop with updated state

**Key Features**:
- Budget enforcement (steps, time, cost)
- Persistent state for resumption
- Cancellation support
- Streaming progress updates

#### 6. Multi-Agent Orchestration
**Purpose**: Supervisor for delegating to specialized subagents

**Default Subagents**:
- **Email Agent**: Multi-step email reasoning
- **Planning Agent**: Complex scheduling negotiation
- **Memory Curator Agent**: Memory review and consolidation
- **Research Agent**: Open-ended research tasks

**Key Features**:
- Config-driven agent registry
- Context isolation between agents
- Result merging and conflict resolution
- Federation-ready architecture

#### 7. Guardrails Layer
**Purpose**: Security and safety checks for autonomous actions

**Guardrail Types**:
- **Input Validation**: Schema validation before processing
- **PII Protection**: Redaction before cloud calls
- **Injection Defense**: Provenance tagging and policy enforcement
- **Tool Authorization**: Runtime permission checks
- **Policy Engine**: Declarative rule enforcement
- **Output Filtering**: Final check before surfacing results

**Key Features**:
- Provenance tagging (user_direct, internal_memory, external_untrusted)
- Human-in-the-loop escalation
- Comprehensive audit logging
- False-positive minimization

#### 8. Evals Framework
**Purpose**: Automated measurement of system quality

**Eval Types**:
- **Memory Classification**: Layer and sensitivity accuracy
- **Task Parsing**: NL to structured task accuracy
- **Agent Success**: Goal completion via LLM-as-judge
- **Guardrail Effectiveness**: Catch rate and false-positive rate

**Key Features**:
- Golden datasets with version control
- Automated regression gating in CI
- LLM-as-judge with pinned models
- Feedback ingestion from user corrections

### Supporting Components

#### 9. Email Intelligence
**Purpose**: Automatic email triage and action extraction

**Key Features**:
- Gmail and Outlook connectors
- Category classification (action-required, FYI, newsletter)
- Entity extraction (deadlines, action items, meetings)
- Automatic task creation
- Daily digest generation

#### 10. Notification System
**Purpose**: Proactive alerting and reminder delivery

**Key Features**:
- Celery-based job scheduling
- Escalation with backoff
- Snooze and quiet hours
- Multi-surface delivery (Chrome, VS Code)
- Missed job recovery

#### 11. Core API
**Purpose**: REST and WebSocket API surface

**Key Features**:
- Device-based authentication with JWT
- OAuth2 flows for connectors
- Rate limiting per consumer
- CORS locked to extension origins
- Generated TypeScript client

#### 12. Observability
**Purpose**: Complete system visibility

**Key Features**:
- Structured logging with request correlation
- Prometheus metrics endpoint
- OpenTelemetry distributed tracing
- Audit log completeness
- Performance monitoring

## Data Architecture

### Primary Data Store: PostgreSQL + pgvector

**Schema Overview**:
- **Users**: User accounts and settings
- **Tasks**: Structured tasks with metadata
- **Time Blocks**: Calendar-like time blocking
- **Calendar Events**: External calendar sync
- **Connectors**: External service connections
- **Connector Credentials**: Encrypted tokens
- **Memory Items**: Four-layer memory with embeddings
- **Memory Edges**: Memory relationships
- **Skills Registry**: Installed skills and permissions
- **Plugin Permissions**: User-granted permissions
- **Notifications**: Scheduled and delivered notifications
- **Audit Log**: Complete action audit trail
- **Agent Runs**: Agent execution state
- **Agent Run Steps**: Detailed step traces

### Secondary Data Store: Redis

**Usage**:
- Response caching (exact match)
- Job queue (Celery)
- Session storage
- Rate limiting counters
- Temporary state

### Vector Storage: pgvector

**Usage**:
- Memory item embeddings (1536-dimensional)
- Semantic similarity search
- IVFFlat or HNSW indexing
- Hybrid ranking with metadata

## Security Architecture

### Defense in Depth

**Layer 1: Network**
- TLS 1.3 for all communications
- CORS locked to known origins
- Rate limiting per consumer

**Layer 2: Authentication**
- Device-based authentication
- JWT short-lived tokens
- OAuth2 for external services
- Secure token storage

**Layer 3: Authorization**
- RBAC with role-based permissions
- ABAC with attribute-based policies
- Runtime permission checks
- Least privilege principle

**Layer 4: Data Protection**
- Encryption at rest (AES-256-GCM)
- Encryption in transit (TLS 1.3)
- PII redaction before cloud calls
- Sensitive data routing policies

**Layer 5: Application Security**
- Input validation on all endpoints
- Output encoding and sanitization
- SQL injection prevention (ORM)
- XSS protection (CSP, encoding)

**Layer 6: Agent Security**
- Provenance tagging for all content
- Injection defense and policy enforcement
- Tool authorization at runtime
- Human-in-the-loop escalation
- Comprehensive audit logging

### Compliance Mapping

**GDPR**:
- Right to be forgotten (forget API)
- Data portability (export functionality)
- Consent management (permission model)
- Data minimization (sensitivity routing)

**SOC 2**:
- Access controls (RBAC/ABAC)
- Audit logging (complete audit trail)
- Change management (CI/CD with approvals)
- Incident response (runbooks and monitoring)

**ISO 27001**:
- Information security policies
- Risk management (threat model)
- Business continuity (disaster recovery)
- Compliance monitoring (continuous audits)

## Deployment Architecture

### Local-First Deployment

**Components**:
- TEMPUS Core (FastAPI application)
- PostgreSQL with pgvector
- Redis
- Ollama (local LLM)
- Celery worker

**Deployment**:
- Docker Compose for local development
- Systemd service for production
- Optional VPS deployment for remote access

### Enterprise Deployment

**Components**:
- Kubernetes cluster
- PostgreSQL with pgvector (HA)
- Redis Cluster
- Ollama or local model deployment
- Horizontal pod autoscaling
- Load balancing (NGINX/HAProxy)

**Infrastructure**:
- Terraform for infrastructure as code
- Helm charts for Kubernetes deployment
- Monitoring stack (Prometheus, Grafana, Loki)
- Log aggregation (Loki or ELK)

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 + SQLModel
- **Migrations**: Alembic
- **Task Queue**: Celery
- **LLM Gateway**: LiteLLM

### Frontend
- **Language**: TypeScript
- **Framework**: React (Vite)
- **Build Tool**: Turborepo
- **Package Manager**: pnpm

### Extensions
- **Chrome**: Manifest V3, React
- **VS Code**: Extension API, React webview

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes (enterprise)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, OpenTelemetry
- **Logging**: Structured logging (JSON)

### Development
- **Python Tooling**: uv, ruff, mypy, pytest
- **TypeScript Tooling**: ESLint, Prettier, Vitest
- **Quality**: Pre-commit hooks, commitlint

## Integration Architecture

### MCP Protocol
TEMPUS uses the Model Context Protocol for all extensibility:

**Connectors**: External data sources exposed as MCP servers
**Skills**: Capabilities exposed as MCP tools
**Host**: TEMPUS Core acts as MCP client

### OpenAPI Specification
All REST APIs are documented via OpenAPI 3.0:
- Auto-generated from FastAPI
- TypeScript client generated via openapi-typescript
- Versioned API contracts

### WebSocket API
Real-time events for:
- Task updates
- New notifications
- Connector status changes
- Agent progress updates

## Performance Characteristics

### Targets
- **API Latency**: p95 < 200ms
- **Memory Query**: p95 < 300ms
- **Agent Loop**: < 5s per step
- **Email Sync**: < 30s for 100 messages

### Scalability
- **Single User**: 10,000+ memory items, 1,000+ tasks
- **Team Deployment**: 100+ users per instance
- **Enterprise**: Horizontal scaling via Kubernetes

### Reliability
- **Uptime**: 99.9% for self-hosted
- **Data Loss**: RPO < 1 hour, RTO < 4 hours
- **Recovery**: Automated backup and restore

## Conclusion

TEMPUS architecture is designed for enterprise-grade reliability, security, and extensibility while maintaining privacy-first principles and local-first deployment options. The layered architecture, governed autonomy, and standard protocols provide a solid foundation for both personal productivity and organizational intelligence.
