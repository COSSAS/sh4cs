import asyncio
import logging
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from lymphocyte.events.bus import Event, EventHandler

log = logging.getLogger(__name__)

T = TypeVar("T", bound=Event)


@dataclass
class GenericEventHandler(EventHandler, Generic[T]):
    """Non-specific EventHandler to listen to events and put events on the event bus.

    Args:
        EventHandler (EventHandler): Base EventHandler class
        Generic (Event): Static Event type.

    Returns:
        List: The asynchronous handle function returns an empty list, as long as there is no event to put on the bus.

    Yields:
        Event: Yields an event from the bus that it is subscribed to.
    """

    handles: type[T]

    queue: asyncio.Queue[T] = field(default_factory=asyncio.Queue)

    async def handle(self, event: Event) -> Iterable[Event]:
        if isinstance(event, self.handles):
            await self.queue.put(event)
        return []

    async def subscribe(self) -> AsyncIterator[T]:
        while True:
            yield await self.queue.get()

    __aiter__ = subscribe
