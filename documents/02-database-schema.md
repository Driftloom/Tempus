# Part 02 — Database & Storage Schema

**Use with:** Claude Code / OpenCode / Codex. Requires Part 01 complete.

## Context
Core boots but has no data layer. This part builds the entire Postgres schema (structured + vector) and migration tooling that every later part (memory, tasks, connectors, auth) will build on. Get this right — schema churn later is expensive.

## Objective
A fully migrated Postgres database (with `pgvector`) plus a typed data-access layer in `apps/core`, covering users, tasks, time tracking, memory, connectors, skills, and audit logging.

## Requirements

### Functional
- ORM/migration tool: **SQLAlchemy 2.0 + SQLModel** (Pydantic-native models, so the same class doubles as the FastAPI request/response schema) with **Alembic** for migrations, using `pgvector`'s Python/SQLAlchemy integration (`pgvector-python`) for the embedding column — document the choice in `docs/decisions/adr-002-orm.md`
- Every table has `id (uuid)`, `created_at`, `updated_at`
- Seed script for local dev (one demo user, a few sample tasks)

### Non-functional
- All migrations are reversible (`up`/`down`)
- Foreign keys with explicit `ON DELETE` behavior (never silent cascades on user data — require explicit review)
- Sensitive columns (OAuth tokens, API keys) are stored encrypted at the application layer, never plaintext — schema should have `bytea` or `text` columns clearly named `*_encrypted`

## Schema (tables to create)

```sql
users (id, email, display_name, timezone, settings_json, created_at, updated_at)

tasks (id, user_id, title, description, status, priority, due_at, 
       estimated_minutes, actual_minutes, source, source_ref, tags[], 
       recurrence_rule, parent_task_id, created_at, updated_at)

time_blocks (id, user_id, task_id nullable, title, start_at, end_at, 
             type [focus|meeting|break|habit], created_at)

calendar_events (id, user_id, connector_id, external_id, title, 
                 start_at, end_at, attendees_json, raw_json, synced_at)

connectors (id, user_id, type [gmail|google_calendar|outlook|slack|github|notion],
            display_name, status [active|error|revoked], config_json, 
            last_sync_at, created_at)

connector_credentials (id, connector_id, access_token_encrypted, 
                        refresh_token_encrypted, expires_at, scopes[])

memory_items (id, user_id, layer [working|episodic|semantic|procedural],
              content, content_type, source, source_ref, importance_score,
              sensitivity [low|medium|high], tags[], embedding vector(1536),
              expires_at nullable, created_at, updated_at)

memory_edges (id, from_memory_id, to_memory_id, relation_type, weight, created_at)

skills_registry (id, name, version, manifest_json, enabled, permissions_json,
                  installed_at)

plugin_permissions (id, user_id, skill_id, permission [read_memory|write_memory|
                     read_tasks|write_tasks|read_connector|network], 
                     granted_at, revoked_at nullable)

notifications (id, user_id, type, title, body, status [pending|sent|dismissed|
               snoozed], scheduled_for, sent_at, related_task_id)

audit_log (id, user_id, actor [user|skill|connector|system], actor_id, 
           action, resource_type, resource_id, metadata_json, created_at)
```

## Deliverables
```
apps/core/app/database/
├── models/                  (one file per table, SQLModel classes — double as Pydantic schemas)
├── alembic/
│   ├── versions/            (generated migrations)
│   └── env.py
├── seed.py
├── session.py               (SQLAlchemy engine + session factory, async, exported singleton)
└── repositories/            (one repo class per domain: TasksRepository, 
                               MemoryRepository, ConnectorsRepository, etc.
                               — no raw queries outside this layer)
docs/decisions/adr-002-orm.md
infra/migrations/            (symlink or copy for docker-compose init)
```

## Step-by-step tasks
1. Add `pgvector` extension enablement in the first Alembic migration (`CREATE EXTENSION IF NOT EXISTS vector;`).
2. Define all schemas above as SQLModel classes, with proper types, enums (Python `Enum` + Postgres native enum or `str` check constraint), and array columns (`ARRAY(String)` or Postgres native arrays).
3. Generate (`alembic revision --autogenerate`) and apply the initial migration; verify against the dockerized Postgres from Part 01.
4. Build one Repository class per domain (async, using SQLAlchemy's async session) — every later part imports from here, never touches the SQLAlchemy session directly outside `database/`.
5. Write `seed.py`: one user, 5 sample tasks across statuses, 2 sample memory items (one per layer, semantic + episodic), run via `uv run python -m app.database.seed`.
6. Write a basic encryption helper (`crypto.py` using AES-256-GCM via the `cryptography` package, key from env) used by `ConnectorCredentialsRepository` for token storage — this becomes the standard for any future secret column.
7. Add a `docs/decisions/adr-002-orm.md` explaining the SQLModel/SQLAlchemy-over-alternatives call (notably: SQLModel classes double as FastAPI request/response schemas later, cutting out a translation layer).
8. Add DB reset script (`uv run python -m app.database.reset`) for local dev.

## Acceptance criteria
- [ ] `alembic upgrade head` runs clean against a fresh Postgres container
- [ ] `uv run python -m app.database.seed` populates demo data without error
- [ ] Every table has typed repository methods with at least create/read/update/delete
- [ ] `connector_credentials` tokens are never stored or logged in plaintext — verify with a test that inserts a token and asserts the raw DB row doesn't contain it
- [ ] `pgvector` similarity query works end-to-end (insert two embeddings, query nearest neighbor, get expected order)
- [ ] Migration is reversible: `alembic downgrade -1` then `alembic upgrade head` leaves the DB in the same state

## Out of scope
- Actual embedding generation (Part 03)
- API endpoints exposing this data (Part 08)
