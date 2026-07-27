# Enterprise Architecture Review

## Executive Summary

This document provides a comprehensive review of the TEMPUS architecture against enterprise-grade patterns including Clean Architecture, Domain-Driven Design (DDD), SOLID principles, and Dependency Injection (DI). The review identifies strengths, gaps, and actionable recommendations for achieving Fortune 500 production readiness.

## Current Architecture Assessment

### Overall Architecture Grade: B+

**Strengths:**
- Clear separation of concerns with modular structure
- Async/await throughout for scalability
- Type hints and Pydantic for data validation
- Structured logging with structlog
- Database abstraction with SQLAlchemy 2.0
- Service layer pattern for business logic

**Gaps:**
- No formal dependency injection container
- Tight coupling between services and repositories
- Missing domain layer abstraction
- No aggregate roots or value objects (DDD)
- Limited use of interfaces/protocols
- No application service layer
- Direct database access in services

## Clean Architecture Analysis

### Layer Structure

**Current State:**
```
app/
├── api/          # Presentation layer (FastAPI endpoints)
├── agents/       # Domain logic (mixed with infrastructure)
├── database/     # Infrastructure (data access)
├── memory/       # Domain logic (mixed with infrastructure)
├── tasks/        # Domain logic (mixed with infrastructure)
└── router/       # Domain logic (mixed with infrastructure)
```

**Issues:**
1. **No clear domain layer** - Business logic is mixed with infrastructure concerns
2. **Services directly access database** - Violates dependency rule
3. **No use case/application layer** - API endpoints call services directly
4. **Entities are database models** - Anemic domain model

**Recommended Clean Architecture:**
```
app/
├── domain/                    # Core business logic (no dependencies)
│   ├── entities/            # Business entities (pure Python)
│   ├── value_objects/       # Value objects
│   ├── repositories/        # Repository interfaces (protocols)
│   ├── services/            # Domain services (interfaces)
│   └── events/              # Domain events
├── application/             # Use cases (orchestration)
│   ├── services/            # Application services
│   ├── dto/                # Data transfer objects
│   └── commands/           # Command/Query objects
├── infrastructure/          # External concerns
│   ├── database/           # SQLAlchemy implementations
│   ├── llm/                # LLM gateway implementations
│   ├── email/              # Email connector implementations
│   └── websocket/          # WebSocket implementations
└── presentation/           # API layer
    ├── api/                # FastAPI endpoints
    └── schemas/            # Pydantic schemas
```

### Dependency Rule Compliance

**Current Violations:**
- `MemoryService` directly imports `MemoryItem` (database model)
- `TaskService` directly imports `Task` (database model)
- Services create database sessions directly
- No repository interfaces defined

**Recommendations:**
1. Define repository interfaces in `domain/repositories/`
2. Implement repositories in `infrastructure/database/`
3. Create domain entities separate from database models
4. Use dependency injection to wire implementations

## Domain-Driven Design Analysis

### Bounded Contexts

**Current State:**
- No explicit bounded contexts defined
- All modules share same database schema
- No context mapping between domains

**Recommended Bounded Contexts:**
1. **Task Management Context** - Tasks, time blocks, scheduling
2. **Memory Context** - Memory items, embeddings, retrieval
3. **Agent Context** - Agent runs, orchestration, state
4. **Connector Context** - External integrations, OAuth
5. **Notification Context** - Notifications, scheduling, delivery

### Aggregates and Aggregate Roots

**Current State:**
- Database models serve as entities
- No aggregate roots defined
- No invariant enforcement
- No domain events

**Recommended Aggregates:**
- **Task Aggregate** (Root: Task) - Contains TimeBlocks, RecurrenceRules
- **Memory Aggregate** (Root: MemoryItem) - Contains MemoryEdges
- **AgentRun Aggregate** (Root: AgentRun) - Contains AgentRunSteps
- **User Aggregate** (Root: User) - Contains Preferences, Devices

### Value Objects

**Missing Value Objects:**
- TaskPriority (currently enum)
- MemorySensitivity (currently enum)
- ProvenanceTag (currently string)
- TimeInterval (for time blocks)
- EmbeddingVector (for memory)

**Recommendations:**
- Convert enums to value objects with behavior
- Implement value objects for domain concepts
- Ensure immutability and equality by value

### Domain Events

**Current State:**
- No domain events defined
- No event publishing mechanism
- No event sourcing

**Recommended Events:**
- `TaskCreated`, `TaskCompleted`, `TaskEscalated`
- `MemoryIngested`, `MemoryConsolidated`
- `AgentStarted`, `AgentCompleted`, `AgentFailed`
- `NotificationScheduled`, `NotificationDelivered`

## SOLID Principles Analysis

### Single Responsibility Principle (SRP)

**Violations:**
1. `MemoryService` handles ingestion, classification, embedding, retrieval
2. `RouterService` handles routing, caching, cost tracking
3. `NotificationService` handles creation, scheduling, delivery

**Recommendations:**
- Split `MemoryService` into `MemoryIngestionService`, `MemoryRetrievalService`, `MemoryClassificationService`
- Split `RouterService` into `RoutingPolicyService`, `CacheService`, `CostTrackingService`
- Split `NotificationService` into `NotificationCreationService`, `NotificationScheduler`, `NotificationDeliveryService`

### Open/Closed Principle (OCP)

**Violations:**
1. Hard-coded provider logic in `LLMGateway`
2. Fixed connector types in email service
3. No plugin system for skills/connectors

**Recommendations:**
- Use strategy pattern for LLM providers
- Implement plugin architecture for connectors
- Use factory pattern for creating connectors

### Liskov Substitution Principle (LSP)

**Current State:**
- No inheritance hierarchies to evaluate
- Limited use of interfaces/protocols

**Recommendations:**
- Define `Connector` protocol/interface
- Define `LLMProvider` protocol/interface
- Ensure all implementations are substitutable

### Interface Segregation Principle (ISP)

**Current State:**
- No interfaces defined
- Services expose all methods

**Recommendations:**
- Define focused interfaces for each capability
- Split large interfaces into smaller, specific ones
- Use protocols for type hints

### Dependency Inversion Principle (DIP)

**Violations:**
1. High-level services depend on low-level database models
2. Services depend on concrete implementations
3. No dependency injection

**Recommendations:**
- Define repository interfaces in domain layer
- Inject dependencies via constructor
- Use DI container (e.g., FastAPI Depends, dependency-injector)

## Dependency Injection Analysis

### Current State

**No formal DI container:**
- Services instantiated directly
- Configuration accessed via global `settings` object
- No interface-based injection

### Recommended DI Strategy

**Option 1: FastAPI Depends (Simple)**
```python
from fastapi import Depends

def get_memory_repository(db: AsyncSession = Depends(get_db)):
    return MemoryRepository(db)

def get_memory_service(repo: MemoryRepository = Depends(get_memory_repository)):
    return MemoryService(repo)
```

**Option 2: dependency-injector (Enterprise)**
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    db = providers.Singleton(create_db_session)
    
    memory_repository = providers.Factory(
        MemoryRepository,
        session=db
    )
    
    memory_service = providers.Factory(
        MemoryService,
        repository=memory_repository
    )
```

**Recommendation:** Start with FastAPI Depends, migrate to dependency-injector for complex scenarios.

## Architecture Decision Records (ADRs)

### Missing ADRs

**Recommended ADRs:**
1. **ADR-001: Choice of SQLAlchemy over ORM** - Document rationale
2. **ADR-002: Hybrid LLM routing strategy** - Document decision
3. **ADR-003: Memory provenance tagging** - Document security rationale
4. **ADR-004: Celery vs arq for job queue** - Document evaluation
5. **ADR-005: Monorepo structure** - Document trade-offs

## Recommendations by Priority

### High Priority (Immediate)

1. **Implement Repository Pattern**
   - Define repository interfaces in domain layer
   - Implement repositories in infrastructure layer
   - Update services to use interfaces
   - Estimated effort: 8-12 hours

2. **Add Dependency Injection**
   - Set up FastAPI Depends for services
   - Inject database sessions via DI
   - Remove global `settings` access
   - Estimated effort: 4-6 hours

3. **Define Domain Entities**
   - Create domain entities separate from DB models
   - Implement value objects
   - Add domain events
   - Estimated effort: 12-16 hours

### Medium Priority (Next Sprint)

4. **Implement Application Service Layer**
   - Create use case services
   - Move orchestration from API layer
   - Implement command/query objects
   - Estimated effort: 16-20 hours

5. **Add Bounded Contexts**
   - Define context boundaries
   - Implement context mapping
   - Separate databases per context (optional)
   - Estimated effort: 8-12 hours

6. **Implement Domain Events**
   - Define event types
   - Implement event bus
   - Add event handlers
   - Estimated effort: 12-16 hours

### Lower Priority (Future)

7. **Implement CQRS (Optional)**
   - Separate read/write models
   - Implement event sourcing
   - Estimated effort: 24-32 hours

8. **Add Plugin Architecture**
   - Define plugin interfaces
   - Implement plugin loader
   - Estimated effort: 16-20 hours

## Migration Strategy

### Phase 1: Repository Pattern (Week 1)
1. Define repository interfaces
2. Implement repositories
3. Update services to use interfaces
4. Add unit tests for repositories

### Phase 2: Dependency Injection (Week 2)
1. Set up DI container
2. Wire dependencies
3. Update API endpoints
4. Integration testing

### Phase 3: Domain Layer (Week 3-4)
1. Create domain entities
2. Implement value objects
3. Add domain events
4. Migrate business logic

### Phase 4: Application Layer (Week 5-6)
1. Create application services
2. Implement use cases
3. Update API layer
4. End-to-end testing

## Conclusion

The TEMPUS architecture has a solid foundation with good separation of concerns and modern Python practices. However, it lacks formal enterprise patterns like Clean Architecture, DDD, and DI. Implementing these patterns will significantly improve maintainability, testability, and scalability for Fortune 500 production use.

**Key Takeaways:**
- Current architecture is functional but not enterprise-grade
- Repository pattern and DI are highest priority improvements
- Domain layer separation will enable better testing and business logic isolation
- Gradual migration is recommended to avoid disruption

**Estimated Total Effort:** 80-120 hours for full architecture refactoring
