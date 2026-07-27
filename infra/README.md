# TEMPUS Infrastructure

This directory contains infrastructure configuration and deployment files.

## Contents
- `docker-compose.yml` - Local development environment with Postgres, Redis, Ollama
- `docker/` - Dockerfiles for various services
- `kubernetes/` - Kubernetes manifests for production deployment
- `terraform/` - Infrastructure as code for cloud deployment
- `migrations/` - Database migration scripts (managed by Alembic in apps/core/)

## Local Development
Start the full stack:
```bash
docker-compose up -d
```

This will start:
- Postgres with pgvector extension
- Redis for caching and job queue
- Ollama for local LLM inference
- TEMPUS Core API
