"""Unit tests for queue module."""


import pytest

from app.queue.circuit_breaker import CircuitBreaker, CircuitBreakerState, circuit_breaker_decorator
from app.queue.retry import RetryManager, RetryPolicy, retry_decorator
from app.queue.stream import EventStream, StreamProcessor


@pytest.fixture
def stream_processor():
    """Create stream processor fixture."""
    return StreamProcessor()


@pytest.fixture
def event_stream():
    """Create event stream fixture."""
    return EventStream()


@pytest.fixture
def retry_manager():
    """Create retry manager fixture."""
    return RetryManager()


@pytest.fixture
def circuit_breaker():
    """Create circuit breaker fixture."""
    return CircuitBreaker(name="test", failure_threshold=3, recovery_timeout=60)


# Stream Processor Tests
@pytest.mark.asyncio
async def test_stream_processor_batch(stream_processor):
    """Test batch processing."""
    async def process_item(item):
        return item * 2

    items = [1, 2, 3, 4, 5]
    results = await stream_processor.process_batch(items, process_item, batch_size=2)

    assert results == [2, 4, 6, 8, 10]


@pytest.mark.asyncio
async def test_stream_processor_with_error(stream_processor):
    """Test stream processor with error handling."""
    async def process_item(item):
        if item == 3:
            raise ValueError("Test error")
        return item * 2

    items = [1, 2, 3, 4, 5]
    results = await stream_processor.process_batch(items, process_item, batch_size=2)

    assert results == [2, 4, None, 8, 10]


# Event Stream Tests
@pytest.mark.asyncio
async def test_event_stream_publish(event_stream):
    """Test event publishing."""
    await event_stream.publish("test_event", {"data": "test"})

    assert len(event_stream.events) == 1
    assert event_stream.events[0]["type"] == "test_event"


@pytest.mark.asyncio
async def test_event_stream_subscribe(event_stream):
    """Test event subscription."""
    received_events = []

    async def handler(event):
        received_events.append(event)

    event_stream.subscribe("test_event", handler)
    await event_stream.publish("test_event", {"data": "test"})

    assert len(received_events) == 1


# Retry Manager Tests
@pytest.mark.asyncio
async def test_retry_success(retry_manager):
    """Test retry on success."""
    call_count = 0

    async def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Test error")
        return "success"

    result = await retry_manager.retry(failing_function, max_attempts=3)

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_exhausted(retry_manager):
    """Test retry exhaustion."""
    async def always_failing():
        raise ValueError("Always fails")

    with pytest.raises(ValueError):
        await retry_manager.retry(always_failing, max_attempts=3)


def test_retry_policy():
    """Test retry policy."""
    policy = RetryPolicy(max_attempts=5, base_delay=1.0, max_delay=10.0)

    assert policy.max_attempts == 5
    assert policy.base_delay == 1.0
    assert policy.max_delay == 10.0


@pytest.mark.asyncio
async def test_retry_decorator():
    """Test retry decorator."""
    call_count = 0

    @retry_decorator(max_attempts=3, base_delay=0.01)
    async def test_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Test error")
        return "success"

    result = await test_function()

    assert result == "success"
    assert call_count == 2


# Circuit Breaker Tests
def test_circuit_breaker_initial_state(circuit_breaker):
    """Test initial circuit breaker state."""
    assert circuit_breaker.state == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_circuit_breaker_success(circuit_breaker):
    """Test circuit breaker on success."""
    async def success_function():
        return "success"

    result = await circuit_breaker.call(success_function)

    assert result == "success"
    assert circuit_breaker.state == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_circuit_breaker_failure(circuit_breaker):
    """Test circuit breaker on failure."""
    async def failing_function():
        raise ValueError("Test error")

    # Trigger failures to open circuit
    for _ in range(3):
        try:
            await circuit_breaker.call(failing_function)
        except ValueError:
            pass

    assert circuit_breaker.state == CircuitBreakerState.OPEN


@pytest.mark.asyncio
async def test_circuit_breaker_open_blocks_calls(circuit_breaker):
    """Test circuit breaker blocks calls when open."""
    async def failing_function():
        raise ValueError("Test error")

    # Open the circuit
    for _ in range(3):
        try:
            await circuit_breaker.call(failing_function)
        except ValueError:
            pass

    # Try to call when open - should raise circuit breaker error
    with pytest.raises(ValueError):
        await circuit_breaker.call(failing_function)


@pytest.mark.asyncio
async def test_circuit_breaker_decorator():
    """Test circuit breaker decorator."""
    cb = CircuitBreaker(name="test_decorator", failure_threshold=2)

    @circuit_breaker_decorator(cb)
    async def test_function():
        raise ValueError("Test error")

    # Trigger failures
    for _ in range(2):
        try:
            await test_function()
        except ValueError:
            pass

    assert cb.state == CircuitBreakerState.OPEN
