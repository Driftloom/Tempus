"""Performance tests for queue operations."""

import asyncio
import time

import pytest

from app.queue.retry import RetryManager
from app.queue.stream import StreamProcessor


@pytest.mark.asyncio
async def test_stream_processor_throughput():
    """Test stream processor throughput."""
    processor = StreamProcessor()

    async def process_item(item):
        return item * 2

    items = list(range(1000))

    start_time = time.time()
    results = await processor.process_batch(items, process_item, batch_size=100)
    elapsed = time.time() - start_time

    throughput = len(items) / elapsed
    print(f"Stream processor throughput: {throughput:.2f} items/second")
    assert throughput > 100  # Should process at least 100 items/second


@pytest.mark.asyncio
async def test_stream_processor_batch_sizes():
    """Test stream processor with different batch sizes."""
    processor = StreamProcessor()

    async def process_item(item):
        return item * 2

    items = list(range(500))

    batch_sizes = [10, 50, 100, 200]
    results = {}

    for batch_size in batch_sizes:
        start_time = time.time()
        await processor.process_batch(items, process_item, batch_size=batch_size)
        elapsed = time.time() - start_time
        results[batch_size] = elapsed
        print(f"Batch size {batch_size}: {elapsed * 1000:.2f}ms")

    # Larger batches should generally be faster
    assert results[200] < results[10]


@pytest.mark.asyncio
async def test_retry_performance():
    """Test retry mechanism performance."""
    retry_manager = RetryManager()

    call_count = 0

    async def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Test error")
        return "success"

    start_time = time.time()
    result = await retry_manager.retry(failing_function, max_attempts=5, base_delay=0.01)
    elapsed = time.time() - start_time

    print(f"Retry with 2 failures time: {elapsed * 1000:.2f}ms")
    assert result == "success"
    assert elapsed < 1.0  # Should complete quickly even with retries


@pytest.mark.asyncio
async def test_concurrent_stream_processing():
    """Test concurrent stream processing."""
    processor = StreamProcessor()

    async def process_item(item):
        await asyncio.sleep(0.001)  # Simulate work
        return item * 2

    items = list(range(100))

    start_time = time.time()
    results = await processor.process_batch(items, process_item, batch_size=10)
    elapsed = time.time() - start_time

    print(f"Concurrent processing time: {elapsed * 1000:.2f}ms")
    assert elapsed < 1.0  # Should complete in under 1 second


@pytest.mark.asyncio
async def test_circuit_breaker_performance():
    """Test circuit breaker performance."""
    from app.queue.circuit_breaker import CircuitBreaker

    circuit_breaker = CircuitBreaker(name="test", failure_threshold=3, recovery_timeout=60)

    async def fast_function():
        return "success"

    # Measure overhead of circuit breaker
    start_time = time.time()

    for _ in range(100):
        await circuit_breaker.call(fast_function)

    elapsed = time.time() - start_time

    print(f"Circuit breaker overhead for 100 calls: {elapsed * 1000:.2f}ms")
    assert elapsed < 0.5  # Should add minimal overhead
