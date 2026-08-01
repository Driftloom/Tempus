"""OpenTelemetry tracing configuration."""

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from structlog import get_logger

logger = get_logger(__name__)


def setup_tracing(app, engine):
    """Setup OpenTelemetry tracing."""
    # Create tracer provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument(engine=engine)

    logger.info("OpenTelemetry tracing configured")
