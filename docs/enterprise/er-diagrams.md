# Entity-Relationship Diagrams - TEMPUS

## Overview

This document provides entity-relationship (ER) diagrams for the TEMPUS database schema, illustrating the relationships between tables and their key attributes.

## Database Overview

**Database**: PostgreSQL 15+ with pgvector extension  
**Schema**: tempus  
**Character Set**: UTF-8  
**Collation**: en_US.UTF-8

## Core ER Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TEMPUS Database Schema                               │
│                                                                                   │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐            │
│  │    users     │         │    tasks     │         │ memory_items │            │
│  │              │         │              │         │              │            │
│  │ PK id        │◄────────│ FK user_id   │◄────────│ FK user_id   │            │
│  │    email     │         │    title     │         │    content   │            │
│  │    name      │         │    status    │         │    layer     │            │
│  │    settings  │         │    priority  │         │  embedding   │            │
│  │    created_at│         │    due_at    │         │ importance  │            │
│  │    updated_at│         │  created_at  │         │ provenance  │            │
│  └──────────────┘         │  updated_at  │         │  created_at  │            │
│                           └──────────────┘         │  updated_at  │            │
│                                                      └──────────────┘            │
│                                                                                   │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐            │
│  │ agent_runs   │         │ agent_steps  │         │ memory_edges │            │
│  │              │         │              │         │              │            │
│  │ PK id        │◄────────│ FK run_id    │         │ PK id        │            │
│  │ FK user_id   │         │    step_num  │         │ FK source_id │◄───────────┐
│  │    goal      │         │    action    │         │ FK target_id │◄───────────┤
│  │    status    │         │    result    │         │    weight    │            │
│  │  created_at  │         │  created_at  │         │  created_at  │            │
│  │  updated_at  │         └──────────────┘         └──────────────┘            │
│  └──────────────┘                                                              │
│                                                                                  │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐            │
│  │ connectors   │         │ notifications│         │    skills    │            │
│  │              │         │              │         │              │            │
│  │ PK id        │         │ PK id        │         │ PK id        │            │
│  │ FK user_id   │         │ FK user_id   │         │ FK user_id   │            │
│  │    type      │         │    title     │         │    name      │            │
│  │    status    │         │    body      │         │    code      │            │
│  │    tokens    │         │    status    │         │ permissions  │            │
│  │  created_at  │         │scheduled_for │         │  created_at  │            │
│  │  updated_at  │         │  created_at  │         │  updated_at  │            │
│  └──────────────┘         └──────────────┘         └──────────────┘            │
│                                                                                   │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐            │
│  │    devices   │         │ time_blocks  │         │  evals       │            │
│  │              │         │              │         │              │            │
│  │ PK id        │         │ PK id        │         │ PK id        │            │
│  │ FK user_id   │         │ FK task_id   │         │ FK user_id   │            │
│  │    name      │         │    start_at  │         │    name      │            │
│  │    type      │         │    end_at    │         │    dataset_id│            │
│  │    token     │         │    duration  │         │    status    │            │
│  │  created_at  │         │  created_at  │         │    result    │            │
│  │  updated_at  │         └──────────────┘         │  created_at  │            │
│  └──────────────┘                                  └──────────────┘            │
│                                                                                   │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐            │
│  │  eval_samples│         │  eval_results│         │    configs   │            │
│  │              │         │              │         │              │            │
│  │ PK id        │         │ PK id        │         │ PK key       │            │
│  │ FK eval_id   │◄────────│ FK sample_id │         │    value     │            │
│  │    input     │         │    output    │         │    type      │            │
│  │    expected  │         │    actual    │         │  created_at  │            │
│  │  created_at  │         │    score     │         │  updated_at  │            │
│  └──────────────┘         │  created_at  │         └──────────────┘            │
│                           └──────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Table Details

### users

**Purpose**: Store user account information and settings

**Columns**:
- `id` (UUID, PK): Unique user identifier
- `email` (VARCHAR(255), UNIQUE): User email address
- `name` (VARCHAR(255)): User display name
- `settings` (JSONB): User preferences and settings
- `created_at` (TIMESTAMP): Account creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_users_email` on `email`
- `idx_users_created_at` on `created_at`

**Relationships**:
- One-to-many with `tasks` (user_id)
- One-to-many with `memory_items` (user_id)
- One-to-many with `agent_runs` (user_id)
- One-to-many with `connectors` (user_id)
- One-to-many with `notifications` (user_id)
- One-to-many with `skills` (user_id)
- One-to-many with `devices` (user_id)
- One-to-many with `evals` (user_id)

### tasks

**Purpose**: Store task information and metadata

**Columns**:
- `id` (UUID, PK): Unique task identifier
- `user_id` (UUID, FK): Reference to users table
- `title` (VARCHAR(500)): Task title
- `description` (TEXT): Task description (optional)
- `status` (VARCHAR(50)): Task status (pending, in_progress, completed, cancelled)
- `priority` (VARCHAR(20)): Task priority (low, medium, high, urgent)
- `due_at` (TIMESTAMP): Task due date (optional)
- `completed_at` (TIMESTAMP): Task completion timestamp
- `snoozed_until` (TIMESTAMP): Snooze end time (optional)
- `source` (VARCHAR(50)): Task source (manual, email, agent, etc.)
- `recurrence_rule` (JSONB): Recurrence rule for recurring tasks
- `created_at` (TIMESTAMP): Task creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_tasks_user_id` on `user_id`
- `idx_tasks_status` on `status`
- `idx_tasks_due_at` on `due_at`
- `idx_tasks_user_status` on `(user_id, status)`
- `idx_tasks_priority_created` on `(priority, created_at DESC)`

**Relationships**:
- Many-to-one with `users` (user_id)
- One-to-many with `time_blocks` (task_id)

### memory_items

**Purpose**: Store memory items with embeddings for semantic search

**Columns**:
- `id` (UUID, PK): Unique memory identifier
- `user_id` (UUID, FK): Reference to users table
- `content` (TEXT): Memory content
- `layer` (VARCHAR(20)): Memory layer (working, short_term, semantic, long_term)
- `embedding` (VECTOR(1536)): Vector embedding for semantic search (pgvector)
- `importance_score` (FLOAT): Importance score (0.0-1.0)
- `provenance` (VARCHAR(50)): Memory source (browser, email, agent, etc.)
- `consolidated` (BOOLEAN): Whether memory has been consolidated
- `access_count` (INTEGER): Number of times accessed
- `last_accessed_at` (TIMESTAMP): Last access timestamp
- `created_at` (TIMESTAMP): Memory creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_memory_user_id` on `user_id`
- `idx_memory_layer` on `layer`
- `idx_memory_user_layer` on `(user_id, layer)`
- `idx_memory_importance` on `importance_score DESC` WHERE layer = 'semantic'
- `idx_memory_provenance` on `provenance`
- `idx_memory_embedding` on `embedding` (ivfflat, lists=100)

**Relationships**:
- Many-to-one with `users` (user_id)
- One-to-many with `memory_edges` as source (source_id)
- One-to-many with `memory_edges` as target (target_id)

### memory_edges

**Purpose**: Store relationships between memory items

**Columns**:
- `id` (UUID, PK): Unique edge identifier
- `source_id` (UUID, FK): Reference to memory_items (source)
- `target_id` (UUID, FK): Reference to memory_items (target)
- `weight` (FLOAT): Edge weight (0.0-1.0)
- `type` (VARCHAR(50)): Edge type (semantic, temporal, causal)
- `created_at` (TIMESTAMP): Edge creation timestamp

**Indexes**:
- `idx_memory_edges_source` on `source_id`
- `idx_memory_edges_target` on `target_id`
- `idx_memory_edges_weight` on `weight`

**Relationships**:
- Many-to-one with `memory_items` as source (source_id)
- Many-to-one with `memory_items` as target (target_id)

### agent_runs

**Purpose**: Store agent execution runs and state

**Columns**:
- `id` (UUID, PK): Unique agent run identifier
- `user_id` (UUID, FK): Reference to users table
- `agent_type` (VARCHAR(50)): Agent type (researcher, planner, executor)
- `goal` (TEXT): Agent goal
- `status` (VARCHAR(20)): Agent status (planning, acting, observing, reflecting, completed, failed, cancelled)
- `state` (JSONB): Agent state (for resumption)
- `step_count` (INTEGER): Number of steps executed
- `max_steps` (INTEGER): Maximum steps allowed
- `cost_used` (FLOAT): Cost incurred in USD
- `max_cost` (FLOAT): Maximum cost allowed
- `started_at` (TIMESTAMP): Agent start timestamp
- `completed_at` (TIMESTAMP): Agent completion timestamp
- `created_at` (TIMESTAMP): Agent run creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_agent_runs_user_id` on `user_id`
- `idx_agent_runs_status` on `status`
- `idx_agent_runs_user_status` on `(user_id, status)`
- `idx_agent_runs_created` on `created_at DESC`

**Relationships**:
- Many-to-one with `users` (user_id)
- One-to-many with `agent_steps` (run_id)

### agent_steps

**Purpose**: Store individual agent execution steps

**Columns**:
- `id` (UUID, PK): Unique step identifier
- `run_id` (UUID, FK): Reference to agent_runs
- `step_num` (INTEGER): Step number in sequence
- `phase` (VARCHAR(20)): Phase (plan, act, observe, reflect)
- `action` (JSONB): Action taken
- `result` (JSONB): Result of action
- `observation` (TEXT): Observation made
- `reflection` (TEXT): Reflection made
- `duration_ms` (INTEGER): Step duration in milliseconds
- `created_at` (TIMESTAMP): Step creation timestamp

**Indexes**:
- `idx_agent_steps_run_id` on `run_id`
- `idx_agent_steps_step_num` on `step_num`

**Relationships**:
- Many-to-one with `agent_runs` (run_id)

### connectors

**Purpose**: Store external connector configurations and tokens

**Columns**:
- `id` (UUID, PK): Unique connector identifier
- `user_id` (UUID, FK): Reference to users table
- `type` (VARCHAR(50)): Connector type (gmail, outlook, exchange, github)
- `status` (VARCHAR(20)): Connector status (disconnected, connecting, connected, error)
- `tokens` (JSONB): OAuth tokens (encrypted)
- `config` (JSONB): Connector configuration
- `last_sync_at` (TIMESTAMP): Last successful sync timestamp
- `error_message` (TEXT): Last error message (if any)
- `created_at` (TIMESTAMP): Connector creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_connectors_user_id` on `user_id`
- `idx_connectors_type` on `type`
- `idx_connectors_status` on `status`

**Relationships**:
- Many-to-one with `users` (user_id)

### notifications

**Purpose**: Store notification schedules and delivery status

**Columns**:
- `id` (UUID, PK): Unique notification identifier
- `user_id` (UUID, FK): Reference to users table
- `title` (VARCHAR(500)): Notification title
- `body` (TEXT): Notification body
- `status` (VARCHAR(20)): Notification status (pending, scheduled, delivered, acknowledged, failed)
- `scheduled_for` (TIMESTAMP): Scheduled delivery time
- `delivered_at` (TIMESTAMP): Actual delivery timestamp
- `acknowledged_at` (TIMESTAMP): Acknowledgment timestamp
- `escalation_level` (INTEGER): Current escalation level (0-5)
- `escalation_count` (INTEGER): Number of escalations
- `delivery_channel` (VARCHAR(50)): Delivery channel (websocket, email, push)
- `created_at` (TIMESTAMP): Notification creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_notifications_user_id` on `user_id`
- `idx_notifications_status` on `status`
- `idx_notifications_scheduled` on `scheduled_for` WHERE status = 'pending'
- `idx_notifications_user_scheduled` on `(user_id, scheduled_for)` WHERE status = 'pending'

**Relationships**:
- Many-to-one with `users` (user_id)

### skills

**Purpose**: Store custom skills and their permissions

**Columns**:
- `id` (UUID, PK): Unique skill identifier
- `user_id` (UUID, FK): Reference to users table
- `name` (VARCHAR(255)): Skill name
- `description` (TEXT): Skill description
- `code` (TEXT): Skill code (Python/JavaScript)
- `permissions` (JSONB): Required permissions
- `is_active` (BOOLEAN): Whether skill is active
- `execution_count` (INTEGER): Number of times executed
- `last_executed_at` (TIMESTAMP): Last execution timestamp
- `created_at` (TIMESTAMP): Skill creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_skills_user_id` on `user_id`
- `idx_skills_is_active` on `is_active`

**Relationships**:
- Many-to-one with `users` (user_id)

### devices

**Purpose**: Store user devices for authentication

**Columns**:
- `id` (UUID, PK): Unique device identifier
- `user_id` (UUID, FK): Reference to users table
- `name` (VARCHAR(255)): Device name
- `type` (VARCHAR(50)): Device type (chrome, vscode, mobile)
- `token` (VARCHAR(500)): Device authentication token
- `last_seen_at` (TIMESTAMP): Last activity timestamp
- `is_active` (BOOLEAN): Whether device is active
- `created_at` (TIMESTAMP): Device registration timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_devices_user_id` on `user_id`
- `idx_devices_token` on `token`
- `idx_devices_is_active` on `is_active`

**Relationships**:
- Many-to-one with `users` (user_id)

### time_blocks

**Purpose**: Store time blocks for task time tracking

**Columns**:
- `id` (UUID, PK): Unique time block identifier
- `task_id` (UUID, FK): Reference to tasks table
- `start_at` (TIMESTAMP): Time block start
- `end_at` (TIMESTAMP): Time block end
- `duration_seconds` (INTEGER): Duration in seconds
- `notes` (TEXT): Time block notes
- `created_at` (TIMESTAMP): Time block creation timestamp

**Indexes**:
- `idx_time_blocks_task_id` on `task_id`
- `idx_time_blocks_start_at` on `start_at`

**Relationships**:
- Many-to-one with `tasks` (task_id)

### evals

**Purpose**: Store evaluation runs for model testing

**Columns**:
- `id` (UUID, PK): Unique evaluation identifier
- `user_id` (UUID, FK): Reference to users table
- `name` (VARCHAR(255)): Evaluation name
- `dataset_id` (UUID, FK): Reference to eval_samples dataset
- `model` (VARCHAR(100)): Model being evaluated
- `status` (VARCHAR(20)): Evaluation status (pending, running, completed, failed)
- `overall_score` (FLOAT): Overall evaluation score
- `result` (JSONB): Detailed evaluation results
- `created_at` (TIMESTAMP): Evaluation creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_evals_user_id` on `user_id`
- `idx_evals_status` on `status`

**Relationships**:
- Many-to-one with `users` (user_id)
- One-to-many with `eval_samples` (eval_id)

### eval_samples

**Purpose**: Store evaluation dataset samples

**Columns**:
- `id` (UUID, PK): Unique sample identifier
- `eval_id` (UUID, FK): Reference to evals table
- `input` (TEXT): Sample input
- `expected` (TEXT): Expected output
- `metadata` (JSONB): Sample metadata
- `created_at` (TIMESTAMP): Sample creation timestamp

**Indexes**:
- `idx_eval_samples_eval_id` on `eval_id`

**Relationships**:
- Many-to-one with `evals` (eval_id)
- One-to-many with `eval_results` (sample_id)

### eval_results

**Purpose**: Store evaluation results for each sample

**Columns**:
- `id` (UUID, PK): Unique result identifier
- `sample_id` (UUID, FK): Reference to eval_samples table
- `output` (TEXT): Actual output
- `actual` (TEXT): Actual result
- `score` (FLOAT): Sample score
- `metrics` (JSONB): Detailed metrics
- `created_at` (TIMESTAMP): Result creation timestamp

**Indexes**:
- `idx_eval_results_sample_id` on `sample_id`

**Relationships**:
- Many-to-one with `eval_samples` (sample_id)

### configs

**Purpose**: Store system configuration

**Columns**:
- `key` (VARCHAR(255), PK): Configuration key
- `value` (JSONB): Configuration value
- `type` (VARCHAR(50)): Value type (string, number, boolean, json)
- `description` (TEXT): Configuration description
- `is_public` (BOOLEAN): Whether config is public
- `created_at` (TIMESTAMP): Configuration creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

**Indexes**:
- `idx_configs_is_public` on `is_public`

**Relationships**: None (standalone table)

## Key Relationships

### User-Centric Relationships
- **users → tasks**: One user has many tasks
- **users → memory_items**: One user has many memory items
- **users → agent_runs**: One user has many agent runs
- **users → connectors**: One user has many connectors
- **users → notifications**: One user has many notifications
- **users → skills**: One user has many skills
- **users → devices**: One user has many devices
- **users → evals**: One user has many evaluations

### Task-Centric Relationships
- **tasks → time_blocks**: One task has many time blocks

### Memory-Centric Relationships
- **memory_items → memory_edges**: One memory item can be source or target of many edges
- **memory_edges → memory_items**: Self-referential relationship for memory connections

### Agent-Centric Relationships
- **agent_runs → agent_steps**: One agent run has many steps

### Evaluation-Centric Relationships
- **evals → eval_samples**: One evaluation has many samples
- **eval_samples → eval_results**: One sample has many results

## Database Constraints

### Foreign Key Constraints
- All foreign key columns have ON DELETE CASCADE for automatic cleanup
- All foreign key columns have ON UPDATE CASCADE for automatic updates

### Unique Constraints
- `users.email` must be unique
- `devices.token` must be unique
- `configs.key` must be unique

### Check Constraints
- `tasks.status` must be one of: pending, in_progress, completed, cancelled
- `tasks.priority` must be one of: low, medium, high, urgent
- `memory_items.layer` must be one of: working, short_term, semantic, long_term
- `memory_items.importance_score` must be between 0.0 and 1.0
- `agent_runs.status` must be one of: planning, acting, observing, reflecting, completed, failed, cancelled
- `notifications.status` must be one of: pending, scheduled, delivered, acknowledged, failed
- `notifications.escalation_level` must be between 0 and 5

## Performance Considerations

### Indexing Strategy
- All foreign key columns are indexed
- Frequently queried columns are indexed
- Composite indexes for common query patterns
- Partial indexes for filtered queries
- Vector index for pgvector similarity search

### Partitioning Strategy
- Consider partitioning `memory_items` by `user_id` for large datasets
- Consider partitioning `agent_steps` by `run_id` for large agent runs
- Consider partitioning `notifications` by `scheduled_for` for time-based queries

### Query Optimization
- Use `EXPLAIN ANALYZE` to analyze query performance
- Monitor slow queries with `pg_stat_statements`
- Optimize JOIN operations with proper indexes
- Use connection pooling to reduce connection overhead

## Conclusion

The TEMPUS database schema is designed to support the core functionality of the system with proper normalization, indexing, and relationships. The schema supports:

1. **User Management**: Users, devices, authentication
2. **Task Management**: Tasks, time tracking, recurrence
3. **Memory System**: Four-layer memory with embeddings and edges
4. **Agent System**: Agent runs, steps, state persistence
5. **Connectors**: External service integrations
6. **Notifications**: Scheduled delivery with escalation
7. **Skills**: Custom skills with permissions
8. **Evaluations**: Model testing and evaluation framework
9. **Configuration**: System configuration management

The schema is optimized for performance with appropriate indexes and supports the vector similarity search capabilities required for the memory system.
