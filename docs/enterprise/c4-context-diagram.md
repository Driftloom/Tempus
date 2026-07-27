# C4 Context Diagram - TEMPUS

## System Context

```
                    ┌─────────────────────────────────────┐
                    │           TEMPUS System              │
                    │                                     │
                    │  Personal Intelligence Layer         │
                    └─────────────────────────────────────┘
                              │         │         │
                              │         │         │
         ┌────────────────────┼─────────┼─────────┼────────────────────┐
         │                    │         │         │                    │
         │                    │         │         │                    │
┌────────┴────────┐   ┌───────┴─────┐ ┌─┴─────────┴──┐   ┌───────────┴─────────┐
│   Chrome User    │   │ VS Code User│ │  Web User     │   │   Admin User       │
│                  │   │             │ │               │   │                     │
│ - Side Panel     │   │ - Status Bar│ │ - Dashboard   │   │ - System Config     │
│ - Quick Capture  │   │ - Commands  │ │ - Full UI     │   │ - User Management   │
│ - Page Context   │   │ - TODO Lens │ │ - Analytics   │   │ - Audit Review      │
└─────────────────┘   └─────────────┘ └───────────────┘   └─────────────────────┘
```

## Context Description

### TEMPUS System
**Purpose**: Enterprise-grade personal intelligence layer

**Responsibilities**:
- Continuous task and time management
- Intelligent email processing and triage
- Four-layer persistent memory system
- Governed multi-agent automation
- Connector and skill extensibility

### Chrome User
**Type**: Primary User

**Description**: Technical professional who works primarily in a browser

**Key Interactions**:
- Side panel for task management and quick capture
- Page context saving to memory
- Omnibox for quick task entry
- Native notifications

**Benefits**:
- Seamless browser integration
- Context-aware task creation
- Real-time task updates

### VS Code User
**Type**: Primary User

**Description**: Developer who works primarily in code editors

**Key Interactions**:
- Status bar time tracking
- Command palette actions
- TODO-to-task conversion
- Webview dashboard

**Benefits**:
- IDE-native time tracking
- Code context awareness
- Seamless workflow integration

### Web User
**Type**: Secondary User

**Description**: User who prefers full web interface or needs advanced features

**Key Interactions**:
- Full dashboard interface
- Advanced analytics and reporting
- System configuration
- Team management (if multi-user)

**Benefits**:
- Complete feature access
- Advanced analytics
- Administrative functions

### Admin User
**Type**: Administrative User

**Description**: System administrator for enterprise deployments

**Key Interactions**:
- System configuration
- User management
- Audit log review
- Compliance monitoring

**Benefits**:
- Centralized administration
- Compliance oversight
- Security monitoring

## External Dependencies

```
                    ┌─────────────────────────────────────┐
                    │           TEMPUS System              │
                    └─────────────────────────────────────┘
                              │         │         │
         ┌────────────────────┼─────────┼─────────┼────────────────────┐
         │                    │         │         │                    │
┌────────┴────────┐   ┌───────┴─────┐ ┌─┴─────────┴──┐   ┌───────────┴─────────┐
│   Gmail API     │   │  Ollama     │ │ Anthropic API│   │   PostgreSQL       │
│                  │   │             │ │               │   │                     │
│ - Email Sync     │   │ - Local LLM │ │ - Cloud LLM   │   │ - Primary Data     │
│ - OAuth2         │   │ - Privacy   │ │ - Complex    │   │ - Vector Search    │
└─────────────────┘   └─────────────┘ │   Reasoning   │   └─────────────────────┘
                                         └───────────────┘
```

## External Dependency Description

### Gmail API
**Type**: External Service

**Purpose**: Email synchronization and processing

**Protocol**: OAuth2 + REST API

**Data Flow**:
- TEMPUS authenticates via OAuth2
- Fetches new messages periodically
- Processes content locally
- Stores extracted data in TEMPUS

**Privacy Considerations**:
- Content processed locally (high sensitivity)
- Only metadata sent to cloud if necessary
- Tokens encrypted at rest

### Ollama
**Type**: Local Service

**Purpose**: Local LLM inference for private data

**Protocol**: HTTP API

**Data Flow**:
- TEMPUS sends sensitive content locally
- Ollama processes without external calls
- Results returned to TEMPUS

**Privacy Considerations**:
- All processing stays on-premises
- No data leaves the machine
- Used for high-sensitivity content

### Anthropic API
**Type**: Cloud Service

**Purpose**: Cloud LLM inference for complex reasoning

**Protocol**: HTTPS API

**Data Flow**:
- TEMPUS sends low-sensitivity content
- Anthropic processes and returns results
- Results cached to reduce costs

**Privacy Considerations**:
- Only low-sensitivity data sent
- Content redacted (PII) before sending
- Cost tracking and budget enforcement

### PostgreSQL
**Type**: Data Store

**Purpose**: Primary data storage with vector search

**Protocol**: TCP (PostgreSQL wire protocol)

**Data Flow**:
- All persistent data stored here
- Vector search via pgvector
- Encrypted credentials stored

**Privacy Considerations**:
- Encrypted at rest (AES-256)
- Access controlled via RBAC
- Regular backups for disaster recovery

## Data Flow Overview

### Email Processing Flow
```
Gmail API → TEMPUS Email Intelligence → Local Classification → 
Task Creation → Memory Ingest → User Notification
```

### Task Creation Flow
```
User Input (Chrome/VS Code) → NL Parser → Task Engine → 
Memory Ingest → Notification → Calendar Integration
```

### Agent Execution Flow
```
User Goal → Agent Runtime → Loop Engine → Router → 
Tool Execution (via MCP Host) → Guardrails Check → 
Result → Memory Ingest → User Notification
```

### Memory Retrieval Flow
```
User Query → Memory Engine → Vector Search → 
Hybrid Ranking → Context Assembly → Response Generation
```

## Security Boundaries

### Trust Boundaries
1. **User Machine**: Trusted boundary for local processing
2. **TEMPUS Core**: Trusted boundary for data processing
3. **Cloud APIs**: Untrusted boundary for external services
4. **External Connectors**: Untrusted boundary for third-party data

### Data Classification
- **High Sensitivity**: Health, financial, personal data → Local only
- **Medium Sensitivity**: Work-related, professional data → Local default
- **Low Sensitivity**: General knowledge, public data → Cloud allowed

### Compliance Boundaries
- **GDPR**: EU data residency requirements
- **SOC 2**: Access control and audit requirements
- **ISO 27001**: Information security standards

## Integration Points

### MCP Connectors
TEMPUS supports MCP connectors for:
- Gmail (email)
- Google Calendar (scheduling)
- Outlook (email and calendar)
- Slack (communication)
- GitHub (development)
- Notion (knowledge management)

### Webhooks
TEMPUS provides webhooks for:
- Task completion events
- Memory consolidation events
- Agent completion events
- Notification events

### API Access
TEMPUS provides REST API for:
- Task management
- Memory query and ingest
- Connector management
- Skill management
- Agent execution
- Notification management

## Deployment Contexts

### Local Deployment
```
Single Machine:
- TEMPUS Core
- PostgreSQL + pgvector
- Redis
- Ollama
- Celery Worker
```

### Enterprise Deployment
```
Kubernetes Cluster:
- TEMPUS Core (multiple replicas)
- PostgreSQL + pgvector (HA)
- Redis Cluster
- Ollama (or local model deployment)
- Celery Workers (horizontal scaling)
- Load Balancer
- Monitoring Stack
```

### Cloud Deployment
```
Cloud Provider (AWS/GCP/Azure):
- Managed PostgreSQL (RDS/Cloud SQL)
- Managed Redis (ElastiCache/ Memorystore)
- Container Service (EKS/GKE/ACS)
- Load Balancer (ALB/Cloud LB)
- Monitoring (CloudWatch/Stackdriver)
```

## Conclusion

The TEMPUS context diagram shows a system designed for privacy-first, local-first deployment with optional cloud integration for complex reasoning. The system serves multiple user types through different interfaces while maintaining consistent security and privacy boundaries. External dependencies are carefully chosen to support the hybrid local/cloud architecture while maintaining data sovereignty.
