"""Stream processor for event streaming."""

from collections.abc import AsyncGenerator, Callable
from typing import Any

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


class StreamProcessor:
    """Process streams of events or data."""

    def __init__(self, batch_size: int = 100, timeout: int = 30):
        """Initialize stream processor."""
        self.batch_size = batch_size
        self.timeout = timeout

    async def process_stream(
        self,
        stream: AsyncGenerator[Any, None],
        processor: Callable[[Any], Any],
        on_error: Callable[[Exception], None] = None
    ) -> list[Any]:
        """Process a stream of items."""
        results = []
        batch = []

        try:
            async for item in stream:
                batch.append(item)

                if len(batch) >= self.batch_size:
                    batch_results = await self._process_batch(batch, processor, on_error)
                    results.extend(batch_results)
                    batch = []

            # Process remaining items
            if batch:
                batch_results = await self._process_batch(batch, processor, on_error)
                results.extend(batch_results)

            return results

        except Exception as e:
            logger.error("Stream processing failed", error=str(e))
            if on_error:
                on_error(e)
            raise

    async def _process_batch(
        self,
        batch: list[Any],
        processor: Callable[[Any], Any],
        on_error: Callable[[Exception], None] = None
    ) -> list[Any]:
        """Process a batch of items."""
        results = []

        for item in batch:
            try:
                result = await processor(item)
                results.append(result)
            except Exception as e:
                logger.error("Item processing failed", item=item, error=str(e))
                if on_error:
                    on_error(e)
                results.append(None)

        return results

    async def stream_from_queue(
        self,
        queue_name: str,
        processor: Callable[[Any], Any]
    ) -> AsyncGenerator[Any, None]:
        """Stream items from a queue."""
        with celery_app.connection_or_acquire() as conn:
            with conn.channel() as channel:
                queue = channel.queue_declare(queue_name, durable=True)

                while True:
                    method, properties, body = channel.basic_get(queue_name)

                    if method is None:
                        # No more messages
                        break

                    try:
                        result = await processor(body)
                        channel.basic_ack(method.delivery_tag)
                        yield result
                    except Exception as e:
                        logger.error("Queue item processing failed", error=str(e))
                        channel.basic_nack(method.delivery_tag, requeue=True)
                        yield None


class EventStream:
    """Event stream for real-time processing."""

    def __init__(self):
        """Initialize event stream."""
        self._subscribers: list[Callable] = []

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to event stream."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from event stream."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    async def publish(self, event: Any) -> None:
        """Publish event to all subscribers."""
        for callback in self._subscribers:
            try:
                await callback(event)
            except Exception as e:
                logger.error("Event subscriber failed", error=str(e))


# Global event stream
event_stream = EventStream()
