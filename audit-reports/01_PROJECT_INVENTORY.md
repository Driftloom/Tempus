# Project Inventory

## Project Variables

```text
PROJECT_NAME: TEMPUS
PROJECT_LOCATION: c:\PROJECTS\PIOS\ClonU\Driftloom\Tempus
PROJECT_TYPE: WEB / API / AI / DATA
TARGET_USERS: Enterprise users, developers, knowledge workers
TARGET_ENVIRONMENT: LOCAL / DEVELOPMENT / STAGING / PRODUCTION
EXPECTED_SCALE: Unknown (requires capacity planning review)
DEPLOYMENT_PLATFORM: DOCKER / KUBERNETES
COMPLIANCE_REQUIREMENTS: UNKNOWN (requires legal review)
AUDIT_MODE: AUDIT_ONLY
RISK_TOLERANCE: MEDIUM
```

## Assumptions

- Project is in early development stage (version 0.1.0)
- Target environment includes local development and production deployment
- Compliance requirements not explicitly defined - requires legal review
- Expected scale not defined - requires capacity planning
- Risk tolerance set to MEDIUM based on enterprise-grade claims

## Technology Stack Inventory

| Area           | Technology | Version | Evidence | Status | Risk |
| -------------- | ---------- | ------: | -------- | ------ | ---- |
| **Frontend**   |            |         |          |        |      |
| Chrome Extension | React | ^18.2.0 | apps/chrome-extension/package.json | Active | Low |
| Chrome Extension | TypeScript | ^5.2.0 | apps/chrome-extension/package.json | Active | Low |
| Chrome Extension | Vite | ^5.0.0 | apps/chrome-extension/package.json | Active | Low |
| VS Code Extension | TypeScript | ^5.2.0 | apps/vscode-extension/package.json | Active | Low |
| VS Code Extension | VS Code API | ^1.85.0 | apps/vscode-extension/package.json | Active | Low |
| Shared UI Kit | React | ^18.2.0 | packages/ui-kit/package.json | Active | Low |
| **Backend**    |            |         |          |        |      |
| Core API | FastAPI | >=0.104.0 | apps/core/pyproject.toml | Active | Low |
| Core API | Python | >=3.11 | apps/core/pyproject.toml | Active | Low |
| Core API | Uvicorn | >=0.24.0 | apps/core/pyproject.toml | Active | Low |
| **Database**   |            |         |          |        |      |
| Primary | PostgreSQL | 16 | deploy/docker-compose.yml | Active | Low |
| Vector Extension | pgvector | 0.2.3 | apps/core/pyproject.toml | Active | Low |
| ORM | SQLModel | >=0.0.14 | apps/core/pyproject.toml | Active | Low |
| ORM | SQLAlchemy | >=2.0.23 | apps/core/pyproject.toml | Active | Low |
| Migrations | Alembic | >=1.12.1 | apps/core/pyproject.toml | Active | Low |
| Driver | asyncpg | >=0.29.0 | apps/core/pyproject.toml | Active | Low |
| **Cache**      |            |         |          |        |      |
| Cache | Redis | 7-alpine | deploy/docker-compose.yml | Active | Low |
| Client | redis | >=5.0.0 | apps/core/pyproject.toml | Active | Low |
| **Queue**      |            |         |          |        |      |
| Task Queue | Celery | >=5.3.4 | apps/core/pyproject.toml | Active | Low |
| **Authentication** |            |         |          |        |      |
| JWT | python-jose | >=3.3.0 | apps/core/pyproject.toml | Active | Low |
| Password Hashing | passlib | >=1.7.4 | apps/core/pyproject.toml | Active | Low |
| OAuth2 | authlib | >=1.2.1 | apps/core/pyproject.toml | Active | Low |
| **AI/ML**      |            |         |          |        |      |
| LLM Router | litellm | >=1.0.0 | apps/core/pyproject.toml | Active | Medium |
| Local LLM | Ollama | Latest | deploy/docker-compose.yml | Active | Medium |
| Cloud LLM | Anthropic API | - | .env.example | Configured | Medium |
| Cloud LLM | OpenAI API | - | .env.example | Configured | Medium |
| PII Detection | presidio | >=2.2.0 | apps/core/pyproject.toml | Active | Low |
| **Infrastructure** |            |         |          |        |      |
| Container | Docker | - | deploy/docker-compose.yml | Active | Low |
| Orchestration | Kubernetes | - | deploy/k8s/ | Active | Low |
| Monitoring | Prometheus | Latest | deploy/docker-compose.yml | Active | Low |
| Dashboards | Grafana | Latest | deploy/docker-compose.yml | Active | Low |
| **Testing**    |            |         |          |        |      |
| Python Tests | pytest | >=7.4.0 | apps/core/pyproject.toml | Active | Low |
| Python Linting | ruff | >=0.1.0 | apps/core/pyproject.toml | Active | Low |
| Python Type Check | mypy | >=1.6.0 | apps/core/pyproject.toml | Active | Low |
| TS Linting | eslint | ^8.50.0 | package.json | Active | Low |
| TS Type Check | tsc | ^5.2.0 | package.json | Active | Low |
| **Build Tools** |            |         |          |        |      |
| Package Manager | pnpm | >=8.0.0 | package.json | Active | Low |
| Python Package Manager | uv | - | README.md | Active | Low |
| Monorepo | Turbo | ^1.10.0 | package.json | Active | Low |
| **Observability** |            |         |          |        |      |
| Logging | structlog | >=23.2.0 | apps/core/pyproject.toml | Active | Low |
| Metrics | Prometheus Instrumentator | >=7.0.0 | apps/core/pyproject.toml | Active | Low |
| Tracing | OpenTelemetry | >=1.21.0 | apps/core/pyproject.toml | Active | Low |
| Tracing Exporter | Jaeger | >=1.21.0 | apps/core/pyproject.toml | Active | Low |

## Application Structure

### Monorepo Layout

```
tempus/
├── apps/
│   ├── core/                 # FastAPI backend (Python)
│   │   ├── app/
│   │   │   ├── agents/       # Multi-agent system
│   │   │   ├── api/          # REST API endpoints
│   │   │   ├── auth/         # Authentication & authorization
│   │   │   ├── cache/        # Redis caching
│   │   │   ├── core/         # Core business logic
│   │   │   ├── database/     # Database models & sessions
│   │   │   ├── email/        # Email processing
│   │   │   ├── evals/        # Evaluation framework
│   │   │   ├── extensions/   # Extension management
│   │   │   ├── guardrails/   # AI guardrails
│   │   │   ├── llm/          # LLM routing & management
│   │   │   ├── mcp/          # MCP connector framework
│   │   │   ├── memory/       # Four-layer memory engine
│   │   │   ├── notifications/ # Notification system
│   │   │   ├── observability/ # Logging, metrics, tracing
│   │   │   ├── queue/        # Celery task queue
│   │   │   ├── realtime/     # WebSocket support
│   │   │   ├── router/       # API routing
│   │   │   ├── security/     # Security utilities
│   │   │   ├── tasks/        # Task management
│   │   │   └── workers/      # Background workers
│   │   ├── test/             # Test suite (43 test files)
│   │   │   ├── unit/         # 24 unit tests
│   │   │   ├── integration/  # 9 integration tests
│   │   │   ├── performance/  # 5 performance tests
│   │   │   ├── security/     # 5 security tests
│   │   │   └── e2e/          # 2 end-to-end tests
│   │   └── alembic/          # Database migrations
│   ├── chrome-extension/     # Chrome extension (TypeScript/React)
│   │   ├── src/
│   │   └── manifest.json
│   └── vscode-extension/     # VS Code extension (TypeScript)
│       ├── src/
│       └── webview-ui/
├── packages/
│   ├── types/                # Shared TypeScript types
│   ├── core-sdk/             # Typed API client
│   └── ui-kit/               # Shared React components
├── connectors/               # MCP connectors
├── skills/                   # MCP skills
├── evals/                    # Evaluation framework
├── infra/                    # Infrastructure configs
├── deploy/                   # Deployment configurations
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── Dockerfile.celery
│   ├── k8s/                  # Kubernetes manifests
│   └── prometheus.yml
├── docs/                     # Documentation (39 files)
│   └── enterprise/           # Enterprise documentation
├── documents/                # Architecture documents
└── .github/workflows/        # CI/CD workflows
    ├── ci.yml
    └── release.yml
```

## Entry Points

### Backend
- **API Server**: `apps/core/app/main.py` - FastAPI application entry point
- **Celery Worker**: `apps/core/app/workers/celery_app.py` - Background task processing
- **Celery Beat**: Scheduled task management

### Frontend
- **Chrome Extension**: `apps/chrome-extension/src/` - Chrome extension entry point
- **VS Code Extension**: `apps/vscode-extension/src/extension.ts` - VS Code extension entry point

## Major Modules

### Core Business Logic
- **Memory Engine**: Four-layer memory system (Working, Episodic, Semantic, Procedural)
- **Multi-Agent System**: Governed AI agent orchestration
- **LLM Router**: Hybrid routing between local Ollama and cloud providers
- **Task Management**: Time tracking and task automation
- **Email Processing**: Inbox triage and commitment extraction

### Infrastructure
- **Authentication**: JWT-based auth with OAuth2 integration (Google, Outlook)
- **Authorization**: Role-based access control
- **Queue System**: Celery for async task processing
- **Caching**: Redis for performance optimization
- **Observability**: Structured logging, Prometheus metrics, OpenTelemetry tracing

### Extensions
- **MCP Framework**: Model Context Protocol for extensibility
- **Chrome Extension**: Browser integration
- **VS Code Extension**: IDE integration

## Service Boundaries

### Internal Services
- Core API (FastAPI)
- Celery Worker
- Celery Beat Scheduler

### External Dependencies
- PostgreSQL (database)
- Redis (cache & queue broker)
- Ollama (local LLM)
- Anthropic API (cloud LLM)
- OpenAI API (cloud LLM)
- Google OAuth2
- Microsoft OAuth2

## Data Flow

1. **User Input** → Chrome/VS Code Extension → Core API
2. **API Processing** → Business Logic → Memory Engine
3. **LLM Requests** → LLM Router → Ollama/Cloud LLMs
4. **Async Tasks** → Celery Queue → Celery Worker
5. **Persistence** → Database (PostgreSQL + pgvector)
6. **Caching** → Redis
7. **Observability** → Prometheus/Grafana/Jaeger

## Authentication Flow

1. User initiates OAuth2 login (Google/Outlook)
2. Extension redirects to Core API OAuth endpoint
3. Core API exchanges code for tokens
4. Core API generates JWT session token
5. JWT returned to extension
6. Extension stores token securely
7. Subsequent requests include JWT in Authorization header
8. Core API validates JWT on each request

## Deployment Flow

### Local Development
1. Start Docker services (PostgreSQL, Redis, Ollama)
2. Install Python dependencies with `uv sync`
3. Install TypeScript dependencies with `pnpm install`
4. Configure environment variables
5. Start Core API: `uv run uvicorn app.main:app --reload`
6. Start TypeScript apps: `pnpm turbo dev`

### Production (Docker)
1. Build Docker images
2. Deploy with `docker-compose up -d`
3. Services: PostgreSQL, Redis, API, Celery Worker, Celery Beat, Prometheus, Grafana

### Production (Kubernetes)
1. Deploy manifests in `deploy/k8s/`
2. Configure secrets and configmaps
3. Apply to cluster

## External Integrations

- **Google OAuth2**: User authentication
- **Microsoft OAuth2**: User authentication
- **Anthropic API**: Cloud LLM provider
- **OpenAI API**: Cloud LLM provider
- **Ollama**: Local LLM provider
- **Email Providers**: Gmail, Outlook (via OAuth2)

## Critical Business Operations

1. **User Authentication**: OAuth2 login, JWT session management
2. **Task Creation**: Natural language task entry
3. **Memory Storage**: Four-layer memory persistence
4. **LLM Inference**: AI reasoning and decision making
5. **Email Processing**: Inbox triage and extraction
6. **Time Tracking**: Timer start/stop
7. **Notification Delivery**: Real-time alerts

## Single Points of Failure

- **PostgreSQL**: Primary database (no replication configured)
- **Redis**: Single cache/queue instance (no clustering)
- **Ollama**: Local LLM (no fallback configured)
- **Core API**: Single API instance (no horizontal scaling configured)

## Unsupported or Abandoned Components

- None identified (project is in active development)

## Known Limitations

- No database replication configured
- No Redis clustering
- No horizontal scaling configuration
- No disaster recovery procedures documented
- No backup automation configured
- No rate limiting implementation verified
- No API versioning strategy documented

## Documentation Coverage

### Available Documentation (39 files)
- Executive summary
- Architecture overview
- API documentation
- Security/threat model
- Zero Trust architecture
- Monitoring & observability
- Disaster recovery
- AI architecture
- Testing strategy
- Operational runbooks
- C4 diagrams (context, container, component, deployment)
- ER diagrams
- Sequence diagrams
- SLIs/SLOs/SLAs
- Risk register
- Product roadmap
- Capacity planning
- Migration guide
- Quality audit
- ADRs (Architecture Decision Records)

### Documentation Status
- Comprehensive enterprise documentation exists
- Most architectural areas documented
- Implementation verification required
- Documentation accuracy needs validation against code
