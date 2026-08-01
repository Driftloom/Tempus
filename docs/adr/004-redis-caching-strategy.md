# ADR 004: Redis Caching Strategy

## Status
Accepted

## Context
TEMPUS requires high-performance caching for multiple use cases: session storage, rate limiting, working memory, and task queue management. A unified caching strategy is needed to optimize performance while maintaining consistency.

## Decision
Use Redis as the primary caching layer with a multi-tiered approach:
1. **Session Storage** - JWT token blacklist, user sessions
2. **Rate Limiting** - Token bucket algorithm counters
3. **Working Memory** - Short-term conversation context
4. **Task Queue** - Celery broker for async tasks
5. **Cache Layer** - Frequently accessed database queries

### Rationale
1. **Performance**: In-memory storage with sub-millisecond access
2. **Persistence**: Optional disk persistence for durability
3. **Data Structures**: Rich data types (hashes, lists, sets, sorted sets)
4. **Atomic Operations**: Built-in support for atomic operations
5. **Pub/Sub**: Native support for real-time messaging
6. **Maturity**: Battle-tested, extensive ecosystem

### Configuration
```python
# Session Storage (TTL: 24 hours)
redis.setex(f"session:{user_id}", 86400, session_data)

# Rate Limiting (TTL: 60 seconds)
redis.incr(f"ratelimit:{user_id}")
redis.expire(f"ratelimit:{user_id}", 60)

# Working Memory (TTL: 1 hour)
redis.setex(f"working:{user_id}", 3600, context_data)

# Task Queue (No TTL - managed by Celery)
redis.lpush("tasks:queue", task_data)
```

### Redis Cluster Strategy
- **Development**: Single Redis instance
- **Production**: Redis Cluster with 3 masters + 3 replicas
- **Failover**: Automatic replica promotion
- **Sharding**: Hash slot-based sharding

### Alternatives Considered
- **Memcached**: No persistence, limited data structures
- **In-Memory Python Dict**: No persistence, no distributed support
- **Database Caching**: Slower, adds load to database

## Consequences
### Positive
- Sub-millisecond cache access
- Rich data structure support
- Built-in pub/sub for real-time features
- Optional persistence for durability
- Horizontal scaling with Redis Cluster

### Negative
- Additional infrastructure component
- Memory-intensive (requires monitoring)
- Network latency in distributed setups
- Requires backup strategy

## Implementation
```python
import redis.asyncio as redis

class RedisManager:
    def __init__(self, url: str):
        self.client = redis.from_url(url, decode_responses=True)
    
    async def cache_get(self, key: str) -> str | None:
        return await self.client.get(key)
    
    async def cache_set(self, key: str, value: str, ttl: int = 3600):
        await self.client.setex(key, ttl, value)
```

## References
- Redis Documentation: https://redis.io/docs/
- Redis Cluster: https://redis.io/docs/manual/scaling/
