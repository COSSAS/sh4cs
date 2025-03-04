import logging
from collections.abc import Iterable
from dataclasses import dataclass, field

from lymphocyte.events.bus import Event, EventHandler
from lymphocyte.events.tick import TickEvent
from lymphocyte.events.trigger import TriggerEvent

log = logging.getLogger(__name__)


@dataclass
class TickEventHandler(EventHandler):
    """EventHandler listening for TickEvents and triggering a named trigger every n seconds.

    Args:
        EventHandler (EventHandler): Base Eventhandler class

    Returns:
        TriggerEvent: Named trigger
    """

    name: str
    every_n_seconds: int = field(default=1)

    async def handle(self, event: Event) -> Iterable[Event]:
        """Handles a TickEvent.

        Args:
            event (Event): An event from the event bus,

        Returns:
            Iterable[Event]: Trigger event when tick event aligns with the handlder's every_n_seconds value.
        """
        if not isinstance(event, TickEvent):
            return []
        if event.counter % self.every_n_seconds != 0:
            return []
        return [TriggerEvent(self.name)]
