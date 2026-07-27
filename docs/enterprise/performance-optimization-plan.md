# Performance Optimization Plan

## Executive Summary

This document outlines the performance optimization strategy for TEMPUS to achieve sub-100ms API response times, handle 10,000+ concurrent users, and ensure efficient resource utilization.

## Current Performance Baseline

### Measured Metrics (Estimated)
- API response time: 200-500ms (p95)
- Database query time: 50-150ms (p95)
- Memory usage: 512MB per worker
- CPU usage: 30-50% under load
- Concurrent connections: 500 max

### Target Metrics
- API response time: <100ms (p95)
- Database query time: <50ms (p95)
- Memory usage: <256MB per worker
- CPU usage: <30% under load
- Concurrent connections: 10,000+

## Database Optimization

### Indexing Strategy

**Current State:**
- Basic indexes on foreign keys
- No composite indexes
- No partial indexes
- No covering indexes

**Recommended Indexes:**

```sql
-- Tasks table
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_due_at ON tasks(due_at) WHERE status = 'pending';
CREATE INDEX idx_tasks_priority_created ON tasks(priority, created_at DESC);

-- Memory table
CREATE INDEX idx_memory_user_layer ON memory_items(user_id, layer);
CREATE INDEX idx_memory_importance ON memory_items(importance_score DESC) WHERE layer = 'semantic';
CREATE INDEX idx_memory_provenance ON memory_items(provenance);

-- Agent runs table
CREATE INDEX idx_agent_runs_user_status ON agent_runs(user_id, status);
CREATE INDEX idx_agent_runs_created ON agent_runs(created_at DESC);

-- Notifications table
CREATE INDEX idx_notifications_user_scheduled ON notifications(user_id, scheduled_for) WHERE status = 'pending';
```

### Query Optimization

**Slow Query Identification:**
1. Enable query logging in PostgreSQL
2. Use pg_stat_statements to track slow queries
3. Set log_min_duration_statement = 100ms
4. Analyze EXPLAIN ANALYZE outputs

**Optimization Techniques:**
1. Use `select()` with specific columns instead of `*`
2. Implement pagination with cursor-based pagination
3. Add query result caching
4. Use `joinedload()` for eager loading
5. Implement batch operations for bulk inserts/updates

### Connection Pooling

**Current Configuration:**
```python
engine = create_async_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10
)
```

**Optimized Configuration:**
```python
engine = create_async_engine(
    settings.database_url,
    pool_size=20,           # Base pool size
    max_overflow=40,        # Max additional connections
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False
)
```

## Caching Strategy

### Redis Caching Layers

**1. Response Caching**
- Cache API responses for GET requests
- TTL: 5-15 minutes based on endpoint
- Invalidation: Write-through cache

**2. Query Result Caching**
- Cache frequently accessed database queries
- TTL: 1-5 minutes
- Invalidation: Time-based + event-based

**3. Session Caching**
- Cache user sessions in Redis
- TTL: 30 minutes
- Invalidation: On logout

**4. Semantic Cache**
- Cache LLM responses by semantic similarity
- TTL: 1 hour
- Invalidation: Manual

### Cache Implementation

```python
from app.core.cache import CacheManager

cache = CacheManager(redis_url=settings.redis_url)

# Response caching
@cache.cache_response(ttl=300)
async def get_tasks(user_id: str):
    return await task_service.get_user_tasks(user_id)

# Query caching
@cache.cache_query(ttl=60)
async def search_memory(query: str, user_id: str):
    return await memory_service.search(query, user_id)
```

## Async Optimization

### Async/Await Verification

**Current Issues:**
- Some synchronous I/O operations
- Blocking calls in async functions
- No async context managers for database

**Optimizations:**

1. **Replace synchronous I/O with async:**
```python
# Before
with open(file_path, 'r') as f:
    content = f.read()

# After
async with aiofiles.open(file_path, 'r') as f:
    content = await f.read()
```

2. **Use async context managers:**
```python
async with get_db() as db:
    result = await db.execute(query)
```

3. **Parallelize independent operations:**
```python
# Before
task1 = await service1.operation()
task2 = await service2.operation()

# After
task1, task2 = await asyncio.gather(
    service1.operation(),
    service2.operation()
)
```

### Background Tasks

**Use Celery for:**
- Email processing
- Large file operations
- Batch imports/exports
- Scheduled jobs

**Use asyncio.create_task for:**
- Non-blocking operations
- Fire-and-forget tasks
- Concurrent I/O

## Memory Optimization

### Memory Profiling

**Tools:**
- `memory_profiler` for function-level profiling
- `tracemalloc` for memory allocation tracking
- `objgraph` for object graph analysis

**Optimization Techniques:**
1. Use generators instead of lists for large datasets
2. Implement pagination to limit memory usage
3. Clear references to large objects
4. Use `__slots__` for frequently instantiated classes

### Embedding Optimization

**Current Issue:**
- Storing 1536-dimensional vectors in memory
- No vector quantization
- No dimensionality reduction

**Optimizations:**
1. Implement vector quantization (PQ)
2. Use dimensionality reduction (PCA)
3. Store vectors in pgvector (already configured)
4. Implement vector streaming for large batches

## API Optimization

### Response Compression

**Implementation:**
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Pagination

**Cursor-based pagination:**
```python
async def get_tasks_paginated(user_id: str, cursor: str = None, limit: int = 50):
    query = select(Task).where(Task.user_id == user_id)
    
    if cursor:
        query = query.where(Task.id > cursor)
    
    query = query.order_by(Task.id).limit(limit)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    next_cursor = tasks[-1].id if tasks else None
    
    return {"items": tasks, "next_cursor": next_cursor}
```

### Batch Operations

**Bulk insert:**
```python
async def bulk_create_tasks(db: AsyncSession, tasks: List[TaskCreate]):
    task_objects = [Task(**task.dict()) for task in tasks]
    db.add_all(task_objects)
    await db.commit()
```

## Monitoring and Profiling

### Performance Monitoring

**Metrics to Track:**
1. API response time (p50, p95, p99)
2. Database query time (p50, p95, p99)
3. Cache hit rate
4. Memory usage per worker
5. CPU usage per worker
6. Connection pool utilization

**Tools:**
- Prometheus for metrics collection
- Grafana for visualization
- APM (Application Performance Monitoring) - Datadog/New Relic

### Profiling Tools

**Python Profiling:**
- `cProfile` for function-level profiling
- `py-spy` for production profiling
- `line_profiler` for line-level profiling

**Database Profiling:**
- `pg_stat_statements` for query performance
- `EXPLAIN ANALYZE` for query optimization
- `pgBadger` for log analysis

## Load Testing Strategy

### Tools
- Locust for load testing
- k6 for performance testing
- JMeter for complex scenarios

### Test Scenarios

**1. Read-Heavy Load:**
- 80% GET requests
- 20% POST requests
- Target: 10,000 RPS

**2. Write-Heavy Load:**
- 30% GET requests
- 70% POST requests
- Target: 1,000 RPS

**3. Mixed Load:**
- 50% GET requests
- 30% POST requests
- 20% WebSocket connections
- Target: 5,000 RPS

### Performance Targets

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| API Response Time (p95) | <100ms | 200-500ms | 100-400ms |
| Database Query Time (p95) | <50ms | 50-150ms | 0-100ms |
| Cache Hit Rate | >80% | 0% | 80% |
| Concurrent Users | 10,000 | 500 | 9,500 |
| Memory per Worker | <256MB | 512MB | 256MB |

## Implementation Timeline

### Week 1: Database Optimization
- Add recommended indexes
- Optimize slow queries
- Configure connection pooling
- Implement query result caching

### Week 2: Caching Layer
- Implement Redis caching
- Add cache invalidation
- Implement semantic cache
- Monitor cache hit rate

### Week 3: Async Optimization
- Verify all I/O is async
- Implement parallel operations
- Add background tasks
- Profile and optimize

### Week 4: API Optimization
- Add response compression
- Implement pagination
- Add batch operations
- Load testing and tuning

## Conclusion

This performance optimization plan addresses database, caching, async, and API performance to achieve Fortune 500 production standards. Implementation should be phased with continuous monitoring to measure improvements.

**Total Estimated Effort:** 120-160 hours
**Timeline:** 4 weeks for full implementation
