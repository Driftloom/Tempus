# ADR-002: Hybrid LLM Routing Strategy

## Status

Accepted

## Context

TEMPUS requires LLM integration for natural language processing with the following requirements:
- Support for multiple LLM providers (local and cloud)
- Cost control and budget enforcement
- Privacy and data protection for sensitive data
- Quality control for critical tasks
- Latency requirements for real-time interactions

## Decision

We chose a hybrid routing strategy that intelligently routes requests to the most appropriate LLM provider (local Ollama or cloud providers like Anthropic/OpenAI) based on sensitivity, complexity, budget, latency, and quality requirements.

## Rationale

### Hybrid Routing Advantages

**1. Privacy Protection**
- Sensitive data (PII, financial, health) routed to local providers
- Data never leaves user's environment for sensitive requests
- Compliance with privacy regulations (GDPR, HIPAA)

**2. Cost Optimization**
- Budget enforcement per user
- Cost estimation before routing
- Cheaper providers for simple tasks
- Premium providers for complex tasks

**3. Quality Control**
- High-capability models for complex reasoning
- Fast models for simple tasks
- Quality requirements drive provider selection
- A/B testing for quality optimization

**4. Latency Optimization**
- Local providers for real-time interactions
- Fast cloud providers for low-latency requirements
- Async processing for non-critical tasks

**5. Redundancy**
- Multiple providers for failover
- Local provider fallback when cloud unavailable
- Provider health monitoring

### Routing Factors

**Sensitivity Analysis**
- PII detection via presidio
- Sensitive data detection
- High sensitivity → Local provider

**Complexity Analysis**
- Token count estimation
- Reasoning requirements
- High complexity → High-capability provider

**Budget Analysis**
- User budget checking
- Cost estimation
- Budget constraints → Cheaper provider

**Latency Requirements**
- Real-time vs async
- Latency thresholds
- Real-time → Fast provider

**Quality Requirements**
- Accuracy vs speed trade-off
- Critical tasks → High-quality provider

### Alternatives Considered

**Cloud-Only**
- Pros: Simple, high quality
- Cons: Privacy concerns, high cost, no offline

**Local-Only**
- Pros: Privacy, low cost, offline
- Cons: Limited quality, resource intensive

**Manual Selection**
- Pros: User control
- Cons: Poor UX, suboptimal decisions

## Consequences

### Positive

- **Privacy**: Sensitive data stays local
- **Cost**: Budget enforcement and optimization
- **Quality**: Appropriate provider for each task
- **Latency**: Optimized for real-time needs
- **Flexibility**: Easy to add new providers

### Negative

- **Complexity**: Routing logic adds complexity
- **Overhead**: Routing decision latency
- **Maintenance**: Provider integration maintenance

## Mitigation Strategies

- **Complexity**: Well-documented routing algorithm
- **Overhead**: Cache routing decisions
- **Maintenance**: LiteLLM for provider abstraction
- **Monitoring**: Track routing decisions and outcomes

## References

- LiteLLM Documentation: https://docs.litellm.ai/
- Ollama Documentation: https://ollama.ai/
- Anthropic API: https://docs.anthropic.com/
- OpenAI API: https://platform.openai.com/docs
