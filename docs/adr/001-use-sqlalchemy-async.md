# ADR 001: Use SQLAlchemy Async with AsyncPG

## Status
Accepted

## Context
TEMPUS requires a high-performance, scalable database layer that can handle concurrent requests efficiently. The application is built on FastAPI, which is natively asynchronous, and needs a database driver that matches this architecture.

## Decision
Use SQLAlchemy 2.0 with AsyncPG driver for PostgreSQL database access.

### Rationale
1. **Async Support**: SQLAlchemy 2.0 provides first-class async support, matching FastAPI's async architecture
2. **Performance**: AsyncPG is the fastest PostgreSQL driver for Python, built on Cython
3. **Connection Pooling**: Built-in async connection pooling reduces connection overhead
4. **ORM Benefits**: SQLAlchemy provides powerful ORM capabilities while maintaining async performance
5. **Future-Proof**: SQLAlchemy 2.0 is the current stable release with long-term support

### Alternatives Considered
- **SQLAlchemy with Sync Driver**: Would block event loop, reducing performance
- **Tortoise ORM**: Less mature, smaller community
- **Databases (SQLAlchemy Core)**: Would lose ORM benefits
- **Raw AsyncPG**: Would require writing all SQL manually, losing ORM benefits

## Consequences
### Positive
- High performance with non-blocking database operations
- Leverages existing SQLAlchemy ecosystem and knowledge
- Type-safe queries with SQLAlchemy 2.0
- Easy migration path from sync to async

### Negative
- Slightly more complex than sync SQLAlchemy
- Requires async/await throughout database code
- Some third-party extensions may not support async

## Implementation
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=False
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

## References
- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/en/20/
- AsyncPG Documentation: https://www.magicstack.com/asyncpg/
