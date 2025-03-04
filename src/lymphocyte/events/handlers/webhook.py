import logging
from collections.abc import Iterable
from dataclasses import dataclass

from lymphocyte.events.bus import Event, EventHandler
from lymphocyte.events.trigger import TriggerEvent
from lymphocyte.events.webhook import WebhookEvent

log = logging.getLogger(__name__)


@dataclass
class WebhookEventHandler(EventHandler):
    """EventHandler that handles a WebhookEvent, and consequently returns a corresponding named trigger.

    Args:
        EventHandler (EventHandler): Base EventHandler class

    Returns:
        TriggerEvent: Named trigger.
    """

    name: str
    exact_match: str

    async def handle(self, event: Event) -> Iterable[Event]:
        if not isinstance(event, WebhookEvent):
            return []

        if not event.name == self.exact_match:
            return []
        return [TriggerEvent(self.name)]
