# TEMPUS Monitoring & Observability Strategy

## Overview

TEMPUS implements comprehensive monitoring and observability across all system components to ensure reliability, performance, and security. This strategy covers logging, metrics, tracing, alerting, and incident response.

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TEMPUS System                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     Application Layer                       │  │
│  │                                                           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  │
│  │  │ Struct   │ │ Metrics  │ │ Tracing  │ │ Health   │      │  │
│  │  │ Logging  │ │          │ │          │ │ Checks   │      │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │  │
│  └───────┼────────────┼────────────┼────────────┼────────────┘  │
│          │            │            │            │               │
└──────────┼────────────┼────────────┼────────────┼───────────────┘
           │            │            │            │
           │            │            │            │
┌──────────┼────────────┼────────────┼────────────┼───────────────┐
│          │            │            │            │               │
│  ┌───────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌──┴────────────┐  │
│  │   Loki      │ │Prometheus│ │  Jaeger  │ │ AlertManager │  │
│  │ (Logs)      │ │(Metrics) │ │(Tracing) │ │  (Alerting)  │  │
│  └─────────────┘ └──────────┘ └──────────┘ └───────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Grafana Dashboard                     │  │
│  │                                                           │  │
│  │  - System Metrics (CPU, Memory, Disk, Network)            │  │
│  │  - Application Metrics (Requests, Latency, Errors)       │  │
│  │  - Business Metrics (Tasks, Memory Items, Agent Runs)    │  │
│  │  - Security Metrics (Auth Failures, Guardrail Triggers)   │  │
│  │  - Log Aggregation and Search                             │  │
│  │  - Trace Visualization                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Structured Logging

### Logging Strategy

**Format**: Structured JSON logs with consistent fields

**Log Levels**:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors requiring immediate attention

**Standard Fields**:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `request_id`: Correlation ID for request tracing
- `user_id`: User ID (if applicable)
- `module`: Module/component name
- `action`: Action being performed
- `message`: Human-readable message
- `error`: Error details (if applicable)
- `context`: Additional context data

### Implementation

**Library**: `structlog` with JSON renderer

**Configuration**:
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

**Request Correlation**:
```python
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id', default=None)

# Middleware to set request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### Log Aggregation

**Development**: Console output with color formatting

**Production**: Loki for log aggregation and search

**Configuration**:
- Log retention: 30 days
- Log indexing: Full-text search
- Log parsing: Automatic JSON parsing
- Log alerts: Error rate thresholds

### Audit Logging

**Separate Audit Trail**: Immutable audit logs for security and compliance

**Audit Events**:
- User authentication (success/failure)
- Permission changes (grant/revoke)
- Data access (sensitive data)
- Autonomous actions (agent executions)
- Configuration changes
- Data deletion

**Audit Log Format**:
```json
{
  "timestamp": "2024-07-15T10:00:00Z",
  "audit_id": "uuid",
  "user_id": "uuid",
  "actor": "user",
  "actor_id": "uuid",
  "action": "task.create",
  "resource_type": "task",
  "resource_id": "uuid",
  "metadata": {
    "task_title": "Complete project proposal",
    "source": "email"
  },
  "ip_address": "192.168.1.1",
  "user_agent": "Chrome Extension/1.0.0"
}
```

## Metrics

### Metrics Strategy

**Format**: Prometheus exposition format

**Metric Types**:
- **Counter**: Monotonically increasing values (request counts, error counts)
- **Gauge**: Values that can go up or down (queue depth, memory usage)
- **Histogram**: Distribution of values (request latency)
- **Summary**: Summary of values (quantiles)

### Key Metrics

#### System Metrics
- `tempus_system_cpu_usage_percent`: CPU usage
- `tempus_system_memory_usage_bytes`: Memory usage
- `tempus_system_disk_usage_bytes`: Disk usage
- `tempus_system_network_bytes_sent`: Network bytes sent
- `tempus_system_network_bytes_received`: Network bytes received

#### API Metrics
- `tempus_api_requests_total`: Total API requests (by endpoint, method, status)
- `tempus_api_request_duration_seconds`: API request latency (histogram)
- `tempus_api_errors_total`: Total API errors (by endpoint, error type)
- `tempus_api_active_connections`: Active API connections

#### Business Metrics
- `tempus_tasks_created_total`: Tasks created (by source, priority)
- `tempus_tasks_completed_total`: Tasks completed (by time period)
- `tempus_memory_items_stored_total`: Memory items stored (by layer, sensitivity)
- `tempus_memory_queries_total`: Memory queries (by layer, filters)
- `tempus_agent_runs_total`: Agent runs (by agent type, status)
- `tempus_agent_steps_total`: Agent steps (by step type, status)

#### Router Metrics
- `tempus_router_requests_total`: Router requests (by provider, sensitivity)
- `tempus_router_cache_hits_total`: Cache hits (by cache type)
- `tempus_router_cache_misses_total`: Cache misses (by cache type)
- `tempus_router_cost_usd_total`: Total cost (by provider, template)
- `tempus_router_latency_seconds`: Router latency (histogram)

#### Security Metrics
- `tempus_auth_failures_total`: Authentication failures (by method)
- `tempus_permission_denials_total`: Permission denials (by permission)
- `tempus_guardrail_blocks_total`: Guardrail blocks (by rule)
- `tempus_guardrail_escalations_total`: Guardrail escalations (by type)

#### Connector Metrics
- `tempus_connector_syncs_total`: Connector syncs (by connector type, status)
- `tempus_connector_errors_total`: Connector errors (by connector type, error)
- `tempus_connector_latency_seconds`: Connector latency (histogram)

### Implementation

**Library**: `prometheus-fastapi-instrumentator` + custom metrics

**Configuration**:
```python
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_group_untemplated=True,
    should_instrument_requests_inprogress=True,
    should_instrument_requests_handler=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="tempus_api_requests_inprogress",
    inprogress_labels=True,
)

instrumentator.instrument(app).expose(app, endpoint="/metrics")
```

**Custom Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge

task_created_counter = Counter(
    'tempus_tasks_created_total',
    'Total tasks created',
    ['source', 'priority']
)

memory_query_histogram = Histogram(
    'tempus_memory_query_duration_seconds',
    'Memory query latency',
    ['layer', 'filters']
)

agent_run_gauge = Gauge(
    'tempus_agent_runs_active',
    'Active agent runs',
    ['agent_type']
)
```

### Metrics Collection

**Scrape Interval**: 15 seconds

**Retention**: 15 days for raw data, 90 days for aggregated data

**Storage**: Prometheus with long-term storage (Thanos or VictoriaMetrics for enterprise)

## Distributed Tracing

### Tracing Strategy

**Format**: OpenTelemetry

**Trace Propagation**: W3C Trace Context

**Sampling**: 10% for production, 100% for development

### Key Spans

#### API Spans
- `HTTP GET /api/v1/tasks`: Task list request
- `HTTP POST /api/v1/tasks`: Task creation request
- `HTTP POST /api/v1/memory/ingest`: Memory ingest request

#### Service Spans
- `memory_service.ingest`: Memory ingest operation
- `memory_service.query`: Memory query operation
- `task_service.create`: Task creation operation
- `router_service.route`: Router operation

#### External Spans
- `llm.call`: LLM API call (with provider and model)
- `connector.sync`: Connector sync operation
- `database.query`: Database query

#### Agent Spans
- `agent.run`: Complete agent run
- `agent.step.plan`: Plan step
- `agent.step.act`: Act step
- `agent.step.observe`: Observe step
- `agent.step.reflect`: Reflect step

### Implementation

**Library**: `opentelemetry-instrumentation-fastapi` + manual instrumentation

**Configuration**:
```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger import JaegerExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
```

**Manual Instrumentation**:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("memory_service.ingest")
async def ingest_memory(content: str, source: str):
    with tracer.start_as_current_span("classification"):
        layer = classify_layer(content)
    with tracer.start_as_current_span("embedding"):
        embedding = generate_embedding(content)
    # ... rest of implementation
```

### Trace Storage

**Development**: Jaeger local instance

**Production**: Jaeger or cloud tracing (AWS X-Ray, Google Cloud Trace)

**Retention**: 7 days for development, 30 days for production

## Health Checks

### Health Check Endpoints

#### Liveness Probe
**Endpoint**: `/health/live`

**Purpose**: Is the application running?

**Checks**:
- Application process is running
- Basic dependencies are accessible

**Response**:
```json
{
  "status": "alive",
  "timestamp": "2024-07-15T10:00:00Z"
}
```

#### Readiness Probe
**Endpoint**: `/health/ready`

**Purpose**: Is the application ready to serve traffic?

**Checks**:
- Database connection
- Redis connection
- Router service
- MCP host

**Response**:
```json
{
  "status": "ready",
  "timestamp": "2024-07-15T10:00:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "router": "healthy",
    "mcp_host": "healthy"
  }
}
```

#### Startup Probe
**Endpoint**: `/health/startup`

**Purpose**: Has the application finished starting up?

**Checks**:
- All migrations applied
- All services initialized
- Connectors loaded

**Response**:
```json
{
  "status": "started",
  "timestamp": "2024-07-15T10:00:00Z",
  "startup_time_seconds": 15.5
}
```

## Alerting

### Alert Strategy

**Severity Levels**:
- **Critical**: Immediate action required (service down, data breach)
- **High**: Action required within 15 minutes (degraded performance, security incident)
- **Warning**: Monitor closely (elevated error rates, resource pressure)
- **Info**: Informational (scheduled maintenance, capacity planning)

### Alert Rules

#### Critical Alerts
- **Service Down**: Any service unavailable for > 1 minute
- **Data Breach**: Unauthorized data access detected
- **Security Incident**: Guardrail escalation rate > 10% of actions
- **Database Down**: Database unavailable for > 30 seconds

#### High Alerts
- **High Error Rate**: API error rate > 5% for 5 minutes
- **High Latency**: API latency p95 > 2s for 5 minutes
- **Resource Exhaustion**: CPU > 90% for 10 minutes, Memory > 90% for 5 minutes
- **Queue Depth**: Celery queue depth > 1000 for 10 minutes

#### Warning Alerts
- **Elevated Error Rate**: API error rate > 1% for 10 minutes
- **Elevated Latency**: API latency p95 > 1s for 10 minutes
- **Resource Pressure**: CPU > 70% for 15 minutes, Memory > 70% for 15 minutes
- **Disk Space**: Disk usage > 80%

#### Info Alerts
- **Scheduled Maintenance**: Upcoming maintenance windows
- **Capacity Planning**: Resource usage trending upward
- **Version Updates**: New versions available

### Alert Channels

**Critical/High**:
- PagerDuty (on-call rotation)
- Slack (#alerts-critical)
- Email (on-call team)

**Warning**:
- Slack (#alerts-warning)
- Email (engineering team)

**Info**:
- Slack (#alerts-info)
- Email (all team)

### Alert Configuration

**Tool**: AlertManager (part of Prometheus)

**Example Alert**:
```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(tempus_api_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: high
          service: api
        annotations:
          summary: "High API error rate"
          description: "API error rate is {{ $value }} for the last 5 minutes"
```

## Dashboards

### Grafana Dashboards

#### System Overview
- CPU, memory, disk, network usage
- Service health status
- Request rate and latency
- Error rate

#### Monitoring Overview
- System metrics
- Application metrics
- Business metrics
- Security metrics

#### API Performance
- Request rate (by endpoint)
- Latency percentiles (by endpoint)
- Error rate (by endpoint)
- Active connections

#### Business Metrics
- Tasks created/completed
- Memory items stored/queried
- Agent runs and success rate
- Connector sync status

#### Security Overview
- Authentication failures
- Permission denials
- Guardrail triggers
- Audit log events

#### Router Performance
- Request rate (by provider)
- Cache hit/miss rate
- Cost tracking
- Latency by provider

## Incident Response

### Incident Severity Levels

**SEV1 - Critical**:
- Service completely down
- Data breach or security incident
- Significant data loss
- Impact: All users affected

**SEV2 - High**:
- Major functionality degraded
- Security incident (contained)
- Performance severely degraded
- Impact: Most users affected

**SEV3 - Medium**:
- Minor functionality degraded
- Performance degraded
- Single component failure
- Impact: Some users affected

**SEV4 - Low**:
- Minor issue
- No user impact
- Documentation or configuration issue

### Incident Response Process

1. **Detection**: Alert triggers or user report
2. **Triage**: Assess severity and impact
3. **Declaration**: Declare incident and notify team
4. **Investigation**: Identify root cause
5. **Mitigation**: Implement temporary fix
6. **Resolution**: Implement permanent fix
7. **Recovery**: Verify full recovery
8. **Post-Mortem**: Document and learn

### Escalation Matrix

**SEV1**:
- Immediate: Page on-call engineer
- 15 minutes: Page engineering manager
- 30 minutes: Page CTO
- 1 hour: Executive team notification

**SEV2**:
- Immediate: Slack alert to on-call engineer
- 15 minutes: Page on-call if no response
- 30 minutes: Page engineering manager

**SEV3**:
- Immediate: Slack alert to engineering team
- 5 minutes: Assign owner
- 1 hour: Status update

**SEV4**:
- Immediate: Create issue in backlog
- Next business day: Review and prioritize

### Runbooks

**Service Down**:
1. Check health endpoints
2. Check service logs
3. Check resource usage
4. Restart affected services
5. Escalate if unresolved

**High Latency**:
1. Check API metrics
2. Check database performance
3. Check external service latency
4. Check queue depth
5. Scale resources if needed

**Database Issues**:
1. Check database connectivity
2. Check database logs
3. Check query performance
4. Check replication status
5. Failover if needed

**Security Incident**:
1. Identify scope and impact
2. Contain the incident
3. Preserve evidence
4. Notify security team
5. Communicate with stakeholders

## Performance Monitoring

### Performance Targets

**API Latency**:
- p50: < 100ms
- p95: < 200ms
- p99: < 500ms

**Memory Query Latency**:
- p50: < 150ms
- p95: < 300ms
- p99: < 600ms

**Agent Step Latency**:
- p50: < 2s
- p95: < 5s
- p99: < 10s

**Connector Sync Latency**:
- p50: < 10s
- p95: < 30s
- p99: < 60s

### Performance Budgets

**API Latency Budget**: 200ms p95

**Breakdown**:
- Authentication: 20ms
- Authorization: 10ms
- Business Logic: 100ms
- Database Query: 50ms
- Response Serialization: 20ms

### Performance Testing

**Load Testing**: Regular load testing with k6 or Gatling

**Stress Testing**: Monthly stress testing to identify breaking points

**Capacity Planning**: Quarterly capacity planning based on metrics

## Conclusion

TEMPUS implements comprehensive monitoring and observability across all system components. The combination of structured logging, metrics, distributed tracing, health checks, and alerting provides complete visibility into system health, performance, and security.

Regular review and updating of monitoring configurations ensures the observability strategy remains effective as the system evolves.
