"""Unit tests for event system functionality."""

import pytest
from app.core.events.base import Event, EventHandler
from app.core.events.base import EventBus


class TestEvent(Event):
    """Test event."""
    
    def __init__(self, data: str):
        self.data = data


class TestEventHandler(EventHandler[TestEvent]):
    """Test event handler."""
    
    def __init__(self):
        self.handled_events = []
    
    async def handle(self, event: TestEvent) -> None:
        """Handle test event."""
        self.handled_events.append(event)


@pytest.mark.asyncio
async def test_event_bus_publish():
    """Test event bus publishing."""
    bus = EventBus()
    handler = TestEventHandler()
    
    bus.subscribe(TestEvent, handler)
    
    event = TestEvent("test_data")
    await bus.publish(event)
    
    assert len(handler.handled_events) == 1
    assert handler.handled_events[0].data == "test_data"


@pytest.mark.asyncio
async def test_event_bus_multiple_handlers():
    """Test event bus with multiple handlers."""
    bus = EventBus()
    handler1 = TestEventHandler()
    handler2 = TestEventHandler()
    
    bus.subscribe(TestEvent, handler1)
    bus.subscribe(TestEvent, handler2)
    
    event = TestEvent("test_data")
    await bus.publish(event)
    
    assert len(handler1.handled_events) == 1
    assert len(handler2.handled_events) == 1


@pytest.mark.asyncio
async def test_event_bus_unsubscribe():
    """Test event bus unsubscribe."""
    bus = EventBus()
    handler = TestEventHandler()
    
    bus.subscribe(TestEvent, handler)
    bus.unsubscribe(TestEvent, handler)
    
    event = TestEvent("test_data")
    await bus.publish(event)
    
    assert len(handler.handled_events) == 0
