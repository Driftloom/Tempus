# Observability Plan

## Executive Summary

This document outlines the observability strategy for TEMPUS using OpenTelemetry, structured logging, metrics, and distributed tracing to achieve production-grade monitoring and debugging capabilities.

## Observability Stack

### Technology Stack
- **Logging**: structlog with JSON output
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry + Jaeger
- **APM**: OpenTelemetry instrumentation
- **Log Aggregation**: Loki (optional) or ELK
- **Alerting**: Prometheus Alertmanager

## Logging Strategy

### Structured Logging

**Current State:**
- Using structlog (good)
- JSON format configured
- Log levels: INFO, WARNING, ERROR

**Enhancements:**

1. **Add Contextual Logging:**
```python
logger.info("Task created", 
    task_id=task.id, 
    user_id=task.user_id, 
    priority=task.priority,
    source="api"
)
```

2. **Add Request ID Tracking:**
```python
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    with structlog.contextvars.bind_contextvars(request_id=request_id):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

3. **Add User Context:**
```python
with structlog.contextvars.bind_contextvars(user_id=user_id):
    logger.info("User action performed")
```

### Log Levels

**Usage Guidelines:**
- **DEBUG**: Detailed diagnostic information
- **INFO**: Normal operational events
- **WARNING**: Unexpected but recoverable events
- **ERROR**: Error conditions requiring attention
- **CRITICAL**: Critical system failures

### Log Sampling

**Implementation:**
```python
# Sample 10% of DEBUG logs in production
if settings.tempus_env == "production":
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ]
    )
```

## Metrics Strategy

### Prometheus Metrics

**Key Metrics to Track:**

1. **API Metrics:**
```python
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

2. **Custom Metrics:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Request counter
task_requests_total = Counter(
    'task_requests_total',
    'Total task requests',
    ['method', 'endpoint', 'status']
)

# Request latency histogram
task_request_duration = Histogram(
    'task_request_duration_seconds',
    'Task request duration',
    ['endpoint']
)

# Active users gauge
active_users = Gauge(
    'active_users',
    'Number of active users'
)
```

3. **Business Metrics:**
```python
# Tasks created
tasks_created_total = Counter(
    'tasks_created_total',
    'Total tasks created',
    ['priority', 'source']
)

# Memory items ingested
memory_items_ingested_total = Counter(
    'memory_items_ingested_total',
    'Total memory items ingested',
    ['layer', 'provenance']
)

# Agent runs completed
agent_runs_completed_total = Counter(
    'agent_runs_completed_total',
    'Total agent runs completed',
    ['status', 'agent_type']
)
```

### Metric Naming Convention

**Format:** `metric_name{label_name="label_value"}`

**Examples:**
- `http_requests_total{method="GET",endpoint="/api/v1/tasks",status="200"}`
- `task_creation_duration_seconds{priority="high"}`
- `memory_query_duration_seconds{layer="semantic"}`

## Tracing Strategy

### OpenTelemetry Tracing

**Configuration:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configure tracing
provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)

# Instrument FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)
```

### Span Naming

**Best Practices:**
- Use operation names, not endpoint names
- Include resource identifiers
- Keep names short and descriptive

**Examples:**
- `POST /api/v1/tasks` → `task.create`
- `GET /api/v1/tasks/{id}` → `task.get`
- `memory.query` → `memory.search`

### Span Attributes

**Key Attributes to Add:**
```python
span.set_attribute("user.id", user_id)
span.set_attribute("task.id", task_id)
span.set_attribute("task.priority", task.priority)
span.set_attribute("http.method", request.method)
span.set_attribute("http.url", str(request.url))
```

### Distributed Tracing

**Context Propagation:**
```python
from opentelemetry.propagate import inject

headers = {}
inject(headers)

# Pass headers to external services
response = await httpx.post(
    external_url,
    headers=headers
)
```

## Alerting Strategy

### Alert Rules

**Critical Alerts:**
1. **API Error Rate > 5%**
```yaml
- alert: HighAPIErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High API error rate detected"
```

2. **API Latency p95 > 500ms**
```yaml
- alert: HighAPILatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
  for: 5m
  annotations:
    summary: "API latency above threshold"
```

3. **Database Connection Pool Exhaustion**
```yaml
- alert: DatabaseConnectionPoolExhaustion
  expr: pg_stat_activity_count / pg_settings_max_connections > 0.9
  for: 2m
  annotations:
    summary: "Database connection pool nearly exhausted"
```

**Warning Alerts:**
1. **Memory Usage > 80%**
2. **CPU Usage > 70%**
3. **Disk Usage > 80%**
4. **Cache Hit Rate < 50%**

### Alert Channels

**Channels:**
- Slack for critical alerts
- Email for warning alerts
- PagerDuty for critical incidents

## Dashboard Strategy

### Grafana Dashboards

**Key Dashboards:**

1. **API Dashboard:**
   - Request rate
   - Error rate
   - Latency (p50, p95, p99)
   - Status code distribution

2. **Database Dashboard:**
   - Connection pool usage
   - Query performance
   - Slow queries
   - Transaction rate

3. **Business Dashboard:**
   - Tasks created per hour
   - Memory items ingested per hour
   - Agent runs completed
   - Active users

4. **System Dashboard:**
   - CPU usage
   - Memory usage
   - Disk usage
   - Network I/O

## Implementation Timeline

### Week 1: Logging Enhancement
- Add contextual logging
- Implement request ID tracking
- Add user context binding
- Configure log sampling

### Week 2: Metrics Implementation
- Add Prometheus instrumentation
- Implement custom metrics
- Configure metric exporters
- Set up Grafana dashboards

### Week 3: Tracing Implementation
- Configure OpenTelemetry
- Instrument FastAPI
- Add span attributes
- Set up Jaeger

### Week 4: Alerting and Dashboards
- Configure alert rules
- Set up alert channels
- Create Grafana dashboards
- Test alerting pipeline

## Conclusion

This observability plan provides comprehensive monitoring, logging, metrics, and tracing capabilities for TEMPUS. Implementation will enable production-grade observability for debugging, performance optimization, and incident response.

**Total Estimated Effort:** 80-120 hours
**Timeline:** 4 weeks for full implementation
