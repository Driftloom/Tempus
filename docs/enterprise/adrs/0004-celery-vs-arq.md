# ADR-004: Celery vs arq for Job Queue

## Status

Accepted

## Context

TEMPUS requires a background job queue for:
- Email synchronization
- Notification delivery
- Memory consolidation
- Agent background tasks
- Scheduled jobs

We need to choose between Celery and arq for the job queue implementation.

## Decision

We chose Celery over arq for the job queue implementation.

## Rationale

### Celery Advantages

**1. Maturity and Stability**
- Celery has been in development since 2009
- Large community and extensive documentation
- Proven in production at scale (Instagram, Pinterest, etc.)
- Long-term support and stability

**2. Feature Rich**
- Task scheduling (Celery Beat)
- Task chains and chords
- Retry logic with exponential backoff
- Rate limiting
- Task result storage
- Monitoring and observability

**3. Broker Support**
- Redis (our choice)
- RabbitMQ
- SQS
- Multiple brokers for redundancy

**4. Monitoring**
- Flower for real-time monitoring
- Prometheus metrics
- Task tracking and inspection
- Error tracking and alerting

**5. Integration**
- FastAPI integration
- SQLAlchemy integration
- Django integration (if needed)
- Extensive ecosystem

### arq Considered

**Pros**
- Async-first design
- Modern Python (async/await)
- Simpler API
- Built on Redis

**Cons**
- Smaller community
- Less mature
- Fewer features
- Less monitoring support

### Why Not arq

While arq is modern and async-first, Celery's maturity, feature set, and monitoring capabilities make it the better choice for an enterprise-grade system. Celery's async support via Celery 5.0+ is sufficient for our needs.

## Consequences

### Positive

- **Maturity**: Proven in production at scale
- **Features**: Rich feature set for complex workflows
- **Monitoring**: Excellent monitoring and observability
- **Integration**: Well-integrated with our stack
- **Support**: Large community and documentation

### Negative

- **Complexity**: Celery has a learning curve
- **Overhead**: More overhead than simpler solutions
- **Configuration**: Complex configuration for advanced features

## Mitigation Strategies

- **Learning Curve**: Comprehensive documentation and training
- **Overhead**: Use only needed features
- **Configuration**: Standardized configuration templates
- **Monitoring**: Flower for easy monitoring

## References

- Celery Documentation: https://docs.celeryproject.org/
- Flower Documentation: https://flower.readthedocs.io/
- arq Documentation: https://arq-docs.helpmanual.io/
