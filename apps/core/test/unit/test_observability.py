"""Unit tests for observability module."""


import pytest

from app.observability.logging import get_logger
from app.observability.metrics import MetricsCollector
from app.observability.tracing import Tracer


@pytest.fixture
def logger():
    """Create logger fixture."""
    return get_logger("test")


@pytest.fixture
def metrics_collector():
    """Create metrics collector fixture."""
    return MetricsCollector()


@pytest.fixture
def tracer():
    """Create tracer fixture."""
    return Tracer("test_service")


# Logger Tests
def test_logger_info(logger):
    """Test logger info."""
    logger.info("Test message", key="value")

    # Should not raise any exception
    assert True


def test_logger_error(logger):
    """Test logger error."""
    logger.error("Test error", error_code=500)

    # Should not raise any exception
    assert True


def test_logger_warning(logger):
    """Test logger warning."""
    logger.warning("Test warning", warning_type="test")

    # Should not raise any exception
    assert True


# Metrics Collector Tests
def test_metrics_increment(metrics_collector):
    """Test metrics increment."""
    metrics_collector.increment("test_counter")

    assert metrics_collector.get_counter("test_counter") == 1


def test_metrics_increment_multiple(metrics_collector):
    """Test metrics increment multiple times."""
    for _ in range(5):
        metrics_collector.increment("test_counter")

    assert metrics_collector.get_counter("test_counter") == 5


def test_metrics_timing(metrics_collector):
    """Test metrics timing."""
    import time

    with metrics_collector.time("test_duration"):
        time.sleep(0.01)

    duration = metrics_collector.get_timing("test_duration")
    assert duration >= 0.01


def test_metrics_gauge(metrics_collector):
    """Test metrics gauge."""
    metrics_collector.set_gauge("test_gauge", 42)

    assert metrics_collector.get_gauge("test_gauge") == 42


def test_metrics_histogram(metrics_collector):
    """Test metrics histogram."""
    metrics_collector.record_histogram("test_histogram", 10)
    metrics_collector.record_histogram("test_histogram", 20)
    metrics_collector.record_histogram("test_histogram", 30)

    histogram = metrics_collector.get_histogram("test_histogram")
    assert len(histogram) == 3
    assert 10 in histogram


# Tracer Tests
def test_tracer_create_span(tracer):
    """Test span creation."""
    with tracer.trace("test_operation") as span:
        span.set_tag("key", "value")

    # Should not raise any exception
    assert True


def test_tracer_span_context(tracer):
    """Test span context."""
    with tracer.trace("test_operation") as span:
        span.set_tag("user_id", "123")
        span.set_tag("operation", "test")

    # Should not raise any exception
    assert True


def test_tracer_error_handling(tracer):
    """Test tracer error handling."""
    try:
        with tracer.trace("test_operation") as span:
            span.record_error(ValueError("Test error"))
            raise ValueError("Test error")
    except ValueError:
        pass

    # Should not raise any exception
    assert True
