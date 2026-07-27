# Changelog

All notable changes to TEMPUS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Database schema for agent runs and steps tracking
- Provenance tagging for memory items with security tracking
- OAuth2 flows for Gmail and Outlook connectors
- WebSocket endpoint for real-time updates
- Agent state persistence with database backing
- Enterprise-grade Gmail connector with Microsoft Graph API
- Enterprise-grade Outlook connector with Microsoft Graph API
- LiteLLM integration for unified LLM provider abstraction
- Celery scheduler for notification delivery
- Prompt injection defense with pattern-based detection
- PII redaction with Presidio integration
- Evaluation framework with golden datasets and LLM-as-judge
- Security headers middleware
- Rate limiting middleware
- RBAC foundation
- OpenTelemetry instrumentation
- Prometheus metrics
- Distributed tracing with Jaeger
- Comprehensive documentation plans
- Architecture review documentation
- Security hardening plan
- Performance optimization plan
- Testing strategy documentation
- DevOps automation plans
- Code quality standards

### Changed
- Enhanced LLM gateway with LiteLLM support
- Updated notification service with Celery integration
- Improved memory service with provenance tracking
- Enhanced guardrails with injection defense
- Updated dependencies for security and performance

### Fixed
- Database connection pooling configuration
- Async/await patterns throughout codebase
- Type hints coverage improvements

### Security
- Added provenance-based security policies
- Implemented PII redaction for untrusted sources
- Added prompt injection detection
- Enhanced OAuth2 security flows

## [0.1.0] - 2024-01-16

### Added
- Initial release of TEMPUS
- Task management system
- Memory system with vector embeddings
- AI agent runtime with plan-act-observe-reflect loop
- Multi-agent orchestration with supervisor
- Guardrails layer for input/output validation
- Email intelligence pipeline
- Hybrid LLM routing
- Chrome extension
- VS Code extension
- FastAPI backend with SQLAlchemy 2.0
- PostgreSQL with pgvector
- Redis for caching
- Celery for background tasks
- Structured logging with structlog
- OpenTelemetry instrumentation
- CI/CD pipelines with GitHub Actions

## Versioning

TEMPUS follows Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

## Release Process

1. Update version in `apps/core/pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions will build and publish release
