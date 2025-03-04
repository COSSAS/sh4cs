import logging
from collections.abc import Iterable
from dataclasses import dataclass

from lymphocyte.events.bus import Event, EventHandler
from lymphocyte.events.trigger import TriggerEvent
from lymphocyte.events.ttl import TTLChangedEvent, TTLRestartedEvent

log = logging.getLogger(__name__)


@dataclass
class TTLResetEventHandler(EventHandler):
    """EventHandler that handles a TTLRestartedEvent, and consequently returns a corresponding named trigger.

    Args:
        EventHandler (EventHandler): Base EventHandler class

    Returns:
        TriggerEvent: Named trigger.
    """

    name: str

    async def handle(self, event: Event) -> Iterable[Event]:
        if not isinstance(event, TTLRestartedEvent):
            return []

        return [TriggerEvent(self.name)]


@dataclass
class TTLChangedEventHandler(EventHandler):
    """EventHandler that handles a TTLChangedEvent, and consequently returns a corresponding named trigger.

    Args:
        EventHandler (EventHandler): Base EventHandler class

    Returns:
        TriggerEvent: Named trigger.
    """

    name: str

    async def handle(self, event: Event) -> Iterable[Event]:
        if not isinstance(event, TTLChangedEvent):
            return []

        return [TriggerEvent(self.name)]
