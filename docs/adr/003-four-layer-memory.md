# ADR 003: Four-Layer Memory Architecture

## Status
Accepted

## Context
TEMPUS needs to store and retrieve user information across different time horizons and sensitivity levels. A single flat storage approach would not provide the necessary performance, privacy, and context management.

## Decision
Implement a four-layer memory architecture:
1. **Working Memory** - Short-term, high-speed, volatile (minutes to hours)
2. **Short-Term Memory** - Recent context, indexed (hours to days)
3. **Long-Term Memory** - Persistent knowledge, semantic search (days to years)
4. **Archival Memory** - Cold storage, rarely accessed (years)

### Layer Characteristics

| Layer | Storage | Retention | Access Speed | Use Case |
|-------|---------|----------|-------------|----------|
| Working | Redis | Minutes | <1ms | Current conversation context |
| Short-Term | PostgreSQL | Days | <10ms | Recent tasks, active projects |
| Long-Term | PostgreSQL + pgvector | Years | <100ms | Knowledge base, patterns |
| Archival | S3/Cloud Storage | Indefinite | <1s | Historical data, compliance |

### Rationale
1. **Performance**: Hot data in fast storage, cold data in cheap storage
2. **Privacy**: Sensitive data can be isolated to specific layers
3. **Cost Optimization**: Expensive storage only for frequently accessed data
4. **Context Management**: Natural separation of temporal relevance

### Data Flow
```
User Input → Working Memory → [Relevance Check] → Short-Term Memory
                                                   ↓
                                           [Importance Check] → Long-Term Memory
                                                                   ↓
                                                           [Retention Policy] → Archival
```

### Alternatives Considered
- **Single Storage Layer**: Would be inefficient, expensive, and slow
- **Two-Layer (Hot/Cold)**: Insufficient granularity for context management
- **Elasticsearch Only**: Expensive for all data, no native SQL capabilities

## Consequences
### Positive
- Optimal performance for each access pattern
- Cost-effective storage strategy
- Natural data lifecycle management
- Privacy controls per layer

### Negative
- Increased system complexity
- Data movement between layers requires careful orchestration
- Query complexity increases with cross-layer searches

## Implementation
```python
from app.memory.engine.memory_engine import MemoryEngine

memory_engine = MemoryEngine()

# Store in appropriate layer
await memory_engine.store(
    content=user_input,
    layer=determine_layer(content),
    sensitivity=classify_sensitivity(content)
)

# Query across layers
results = await memory_engine.query(
    query=user_query,
    layers=[MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM]
)
```

## References
- Cognitive Science: Working Memory Model
- Data Warehousing: Hot/Cold Data Patterns
