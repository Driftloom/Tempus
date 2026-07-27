"""Prometheus metrics configuration."""

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
from structlog import get_logger

logger = get_logger(__name__)

# Define metrics
request_count = Counter(
    "tempus_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "tempus_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)

llm_requests_total = Counter(
    "tempus_llm_requests_total",
    "Total LLM requests",
    ["provider", "model"]
)

llm_request_duration = Histogram(
    "tempus_llm_request_duration_seconds",
    "LLM request duration",
    ["provider", "model"]
)

llm_cost_total = Counter(
    "tempus_llm_cost_total",
    "Total LLM cost in USD",
    ["provider", "model"]
)

memory_items_total = Gauge(
    "tempus_memory_items_total",
    "Total memory items",
    ["layer", "sensitivity"]
)

tasks_total = Gauge(
    "tempus_tasks_total",
    "Total tasks",
    ["status", "priority"]
)


def setup_metrics(app):
    """Setup Prometheus metrics for FastAPI app."""
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
    logger.info("Prometheus metrics configured")
    return instrumentator
