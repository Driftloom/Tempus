# ADR-003: Memory Provenance Tagging

## Status

Accepted

## Context

TEMPUS implements a four-layer memory system (working, short-term, semantic, long-term) that ingests data from multiple sources (browser, email, agent, manual). We need to track the origin and trustworthiness of memory items for security, privacy, and quality control.

## Decision

We chose to implement provenance tagging for all memory items, tracking the source, timestamp, and metadata for each memory to enable security filtering, privacy controls, and quality management.

## Rationale

### Provenance Tagging Advantages

**1. Security Control**
- Filter memories by source (e.g., exclude agent-generated from critical decisions)
- Trust levels based on source (manual > browser > agent > email)
- Audit trail for memory origin

**2. Privacy Protection**
- Right-to-forget by source (e.g., delete all email-derived memories)
- Source-based access control
- Compliance with privacy regulations

**3. Quality Management**
- Weight memory importance by source reliability
- Filter low-quality sources in queries
- Track memory quality over time

**4. Debugging**
- Trace memory origin for debugging
- Identify problematic sources
- Audit memory ingestion

### Provenance Tags

**Source Types**
- `manual`: User manually created
- `browser`: Browser extension captured
- `email`: Email connector extracted
- `agent`: Agent generated
- `api`: API created
- `import`: Bulk imported

**Metadata**
- Source identifier (e.g., connector ID, agent ID)
- Source timestamp
- Source confidence score
- Source trust level

### Alternatives Considered

**No Provenance**
- Pros: Simple, no overhead
- Cons: No security control, no privacy control, no quality management

**Simple Source Tag**
- Pros: Minimal overhead
- Cons: Limited metadata, no detailed tracking

**Full Provenance Graph**
- Pros: Complete tracking
- Cons: Complex, high overhead, overkill

## Consequences

### Positive

- **Security**: Source-based filtering and access control
- **Privacy**: Source-based deletion and compliance
- **Quality**: Source-based weighting and filtering
- **Debugging**: Trace memory origin
- **Audit**: Complete memory provenance

### Negative

- **Storage**: Additional metadata storage
- **Complexity**: Provenance tracking logic
- **Query**: Filter by provenance adds query complexity

## Mitigation Strategies

- **Storage**: Metadata stored as JSONB, efficient storage
- **Complexity**: Well-defined provenance schema
- **Query**: Indexes on provenance fields for efficient filtering
- **Maintenance**: Provenance validation and cleanup

## References

- Memory System Architecture: `docs/enterprise/ai-architecture.md`
- Security Documentation: `docs/enterprise/threat-model.md`
