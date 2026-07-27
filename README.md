# TEMPUS

Enterprise-grade personal intelligence layer that manages your time, tasks, and communications continuously through a governed multi-agent system.

## Overview

TEMPUS is an open-source, enterprise-grade personal intelligence layer that:
- Manages your time and tasks continuously (not a to-do list you have to update — it updates itself from context)
- Reads your inbox and pulls out what matters (deadlines, commitments, action items) without you triaging manually
- Remembers everything about you and your work in a structured, layered memory system
- Is extensible via a standard connector/plugin/skill protocol (MCP)
- Lives where you already work: Chrome extension and VS Code extension

## Architecture

TEMPUS follows a hybrid architecture with:
- **Four-layer memory engine** (Working, Episodic, Semantic, Procedural)
- **Hybrid LLM routing** (local Ollama for privacy, cloud Claude/GPT for complex reasoning)
- **Multi-agent system** with governed automation
- **MCP-based extensibility** for connectors and skills

## Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 8.0.0
- **Python** >= 3.11
- **uv** (Python package manager)
- **Docker** (for local development)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Tempus
```

### 2. Start Infrastructure

```bash
docker-compose up -d
```

This starts:
- PostgreSQL with pgvector
- Redis
- Ollama (local LLM)

### 3. Python Setup

```bash
cd apps/core
uv sync
```

### 4. TypeScript Setup

```bash
pnpm install
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 6. Start Development

```bash
# Start all services
make dev

# Or individually:
# Python backend
cd apps/core && uv run uvicorn app.main:app --reload

# TypeScript apps
pnpm turbo dev
```

## Project Structure

```
tempus/
├── apps/
│   ├── core/                 # FastAPI backend (Python)
│   ├── chrome-extension/     # Chrome extension (TypeScript)
│   └── vscode-extension/     # VS Code extension (TypeScript)
├── packages/
│   ├── types/                # Generated TypeScript types
│   ├── core-sdk/             # Typed API client
│   └── ui-kit/               # Shared React components
├── connectors/               # MCP connectors
├── skills/                   # MCP skills
├── evals/                    # Evaluation framework
├── infra/                    # Infrastructure configs
└── docs/                     # Documentation
```

## Development

### Python (Core)

```bash
cd apps/core
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
uv run mypy .
```

### TypeScript (Extensions & Packages)

```bash
pnpm dev          # Start all TS apps in dev mode
pnpm build        # Build all TS packages
pnpm lint         # Lint all TS packages
pnpm typecheck    # Type check all TS packages
pnpm test         # Run all TS tests
```

### Make Commands

```bash
make dev          # Start all services
make lint         # Lint Python and TypeScript
make test         # Test Python and TypeScript
make build        # Build Python and TypeScript
```

## Chrome Extension

### Load Unpacked Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `apps/chrome-extension/dist` directory

### Features

- Side panel for task management
- Quick capture for natural language task entry
- Memory search
- Page context saving
- Real-time notifications

## VS Code Extension

### Development Host

1. Press F5 in VS Code
2. Extension Development Host will open
3. Run commands via Command Palette (`Ctrl+Shift+P`)

### Commands

- `TEMPUS: Ping` - Test extension
- `TEMPUS: Start Timer` - Start time tracking
- `TEMPUS: Stop Timer` - Stop time tracking
- `TEMPUS: Quick Add Task` - Quick task creation
- `TEMPUS: Open Dashboard` - Open dashboard (coming soon)

## Documentation

### Enterprise Documentation
- [Executive Summary](docs/enterprise/executive-summary.md) - Product vision, business goals, strategy
- [Architecture Overview](docs/enterprise/architecture-overview.md) - System architecture and principles
- [API Documentation](docs/enterprise/api-documentation.md) - REST and WebSocket APIs
- [Security Documentation](docs/enterprise/threat-model.md) - Threat model and security architecture
- [Zero Trust Architecture](docs/enterprise/zero-trust-architecture.md) - Zero Trust implementation
- [Monitoring & Observability](docs/enterprise/monitoring-observability.md) - Monitoring, logging, tracing
- [Infrastructure](docs/enterprise/disaster-recovery.md) - DR, backup, capacity planning
- [AI Architecture](docs/enterprise/ai-architecture.md) - LLM routing, multi-agent system
- [Development](docs/enterprise/testing-strategy.md) - Testing, QA, release, versioning
- [Operations](docs/enterprise/operational-runbooks.md) - Runbooks, playbooks, ADRs

### Architecture Diagrams
- [C4 Context Diagram](docs/enterprise/c4-context-diagram.md)
- [C4 Container Diagram](docs/enterprise/c4-container-diagram.md)
- [C4 Component Diagram](docs/enterprise/c4-component-diagram.md)
- [C4 Deployment Diagram](docs/enterprise/c4-deployment-diagram.md)
- [ER Diagrams](docs/enterprise/er-diagrams.md)
- [Sequence Diagrams](docs/enterprise/sequence-diagrams.md)

### Operational Documentation
- [SLIs/SLOs/SLAs](docs/enterprise/sli-slo-sla.md) - Service level objectives
- [Risk Register](docs/enterprise/risk-register.md) - Risk management
- [Product Roadmap](docs/enterprise/product-roadmap.md) - Strategic roadmap
- [Capacity Planning](docs/enterprise/capacity-planning.md) - Capacity requirements
- [Migration Guide](docs/enterprise/migration-guide.md) - Upgrade procedures
- [Quality Audit](docs/enterprise/quality-audit.md) - Implementation quality assessment

## License

Apache-2.0

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
