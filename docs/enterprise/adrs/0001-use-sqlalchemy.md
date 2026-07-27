# ADR-001: Choice of SQLAlchemy over Other ORMs

## Status

Accepted

## Context

TEMPUS requires a database ORM for Python with the following requirements:
- Async/await support for scalability
- Support for PostgreSQL with pgvector extension
- Mature ecosystem and community support
- Migration support
- Type safety and IDE support

## Decision

We chose SQLAlchemy 2.0 with async support over other ORMs (Django ORM, Tortoise ORM, Pony ORM, SQLModel).

## Rationale

### SQLAlchemy Advantages

**1. Mature and Stable**
- SQLAlchemy has been in development since 2006
- Large community and extensive documentation
- Proven in production at scale (Fortune 500 companies)
- Regular updates and long-term support

**2. Async Support**
- SQLAlchemy 2.0 has first-class async support
- AsyncSession for async database operations
- Compatible with asyncpg driver for PostgreSQL
- Full async query execution

**3. pgvector Support**
- Native support for PostgreSQL extensions
- pgvector extension for vector similarity search
- Custom types for vector columns
- Efficient vector operations

**4. Flexibility**
- Supports both ORM and Core (SQL expression language)
- Can use ORM for high-level operations
- Can use Core for performance-critical queries
- Fine-grained control over SQL generation

**5. Migration Support**
- Alembic for database migrations
- Automatic migration generation
- Version control for schema changes
- Rollback support

**6. Type Safety**
- Type hints throughout
- Mypy plugin for type checking
- IDE autocomplete support
- Compile-time type validation

### Alternatives Considered

**Django ORM**
- Pros: Batteries included, admin interface
- Cons: Tied to Django framework, less flexible, limited async support

**Tortoise ORM**
- Pros: Async-first, similar to Django ORM
- Cons: Smaller community, less mature, limited pgvector support

**Pony ORM**
- Pros: Simple API, automatic query optimization
- Cons: Limited async support, smaller community

**SQLModel**
- Pros: Pydantic integration, type safety
- Cons: Based on SQLAlchemy 1.4, less mature, limited async support

## Consequences

### Positive

- **Scalability**: Async support enables high concurrency
- **Performance**: Efficient query execution with asyncpg
- **Vector Search**: pgvector support for semantic search
- **Type Safety**: Type hints and mypy support
- **Migrations**: Alembic for schema management
- **Flexibility**: Can use ORM or Core as needed

### Negative

- **Complexity**: SQLAlchemy has a learning curve
- **Boilerplate**: More verbose than simpler ORMs
- **Overhead**: ORM layer adds some overhead (mitigated with Core for critical paths)

## Mitigation Strategies

- **Learning Curve**: Comprehensive documentation and training
- **Boilerplate**: Use repository pattern to reduce repetition
- **Performance**: Use Core for performance-critical queries
- **Type Safety**: Enforce mypy in CI/CD

## References

- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Alembic Documentation: https://alembic.sqlalchemy.org/
- pgvector Documentation: https://github.com/pgvector/pgvector
