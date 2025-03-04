import asyncio
import logging
from collections.abc import AsyncIterable, Iterable
from dataclasses import dataclass
from typing import Protocol

log = logging.getLogger(__name__)


@dataclass
class Event:
    """Base Event class."""


class EventHandler(Protocol):
    """Base EventHandler protocol class for static type checking.

    Args:
        Protocol (Protocol): allows for static type checking.
    """

    async def handle(self, event: Event) -> Iterable[Event]:
        ...


class EventBus:
    """The tasks are synchronized using an event bus. The event bus is a FIFO
    queue on which events are dispatched."""

    _queue: asyncio.Queue[Event]

    def __init__(self, queue: asyncio.Queue[Event]) -> None:
        self._queue = queue

    async def dispatch_async(self, event: Event) -> None:
        """Dispatch events on the bus.

        Args:
            event (Event): An Event object.
        """
        await self._queue.put(event)


@dataclass
class EventHandlerService:
    """Event handlers can be registered to receive certain event
    types, after some event has dispatched. When multiple handlers are registered for the same
    event type, they all get passed the same event, in order of registration. Event handlers can put
    new events on the event bus.

        Yields:
            (Future) Event: An eventual new event.
    """

    handlers: list[EventHandler]

    def register(self, handler: EventHandler) -> None:
        """Set up a handler.

        Args:
            handler (EventHandler): Generic event handler.
        """
        log.debug("Regisering new handler: %s", handler)
        self.handlers.append(handler)

    def unregister(self, handler: EventHandler) -> None:
        """Unregister a handler.

        Args:
            handler (EventHandler): Generic event handler.
        """
        log.debug("Unregistering handler: %s", handler)
        self.handlers.remove(handler)

    async def handle(self, event: Event) -> AsyncIterable[Event]:
        for new_events in asyncio.as_completed(
            [handler.handle(event) for handler in self.handlers]
        ):
            for new_event in await new_events:
                yield new_event
