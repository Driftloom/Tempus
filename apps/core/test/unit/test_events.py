"""Unit tests for event system functionality."""

import pytest
from app.core.events.base import Event
from app.core.events.base import EventBus


class TestEvent(Event):
    """Test event."""
    data: str


def test_event_bus_initialization():
    """Test event bus initialization."""
    bus = EventBus()
    assert bus._handlers == {}


def test_event_bus_subscribe():
    """Test event bus subscription."""
    bus = EventBus()

    async def handler(evt: TestEvent) -> None:
        pass

    bus.subscribe(TestEvent, handler)
    assert "TestEvent" in bus._handlers
    assert len(bus._handlers["TestEvent"]) == 1


def test_event_bus_subscribe_multiple():
    """Test event bus multiple subscriptions."""
    bus = EventBus()

    async def h1(evt: TestEvent) -> None:
        pass

    async def h2(evt: TestEvent) -> None:
        pass

    bus.subscribe(TestEvent, h1)
    bus.subscribe(TestEvent, h2)
    assert "TestEvent" in bus._handlers
    assert len(bus._handlers["TestEvent"]) == 2


def test_event_bus_unsubscribe():
    """Test event bus unsubscription."""
    bus = EventBus()

    async def handler(evt: TestEvent) -> None:
        pass

    bus.subscribe(TestEvent, handler)
    bus.unsubscribe(TestEvent, handler)
    assert len(bus._handlers["TestEvent"]) == 0
