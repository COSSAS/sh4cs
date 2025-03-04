import logging
from collections.abc import Iterable
from dataclasses import dataclass

from lymphocyte.events.bus import Event, EventHandler
from lymphocyte.events.prometheus import PrometheusAlertStatusChangedEvent
from lymphocyte.events.trigger import TriggerEvent

log = logging.getLogger(__name__)


@dataclass
class PrometheusAlertStatusChangedHandler(EventHandler):
    """If this EventHandler receives a PrometheusAlertStatusChangedEvent, it returns the

    Args:
        EventHandler (EventHandler): Base EventHandler class

    Returns:
        TriggerEvent: TriggerEvent of base class Event with named trigger.
    """

    name: str
    alertname: str

    async def handle(self, event: Event) -> Iterable[Event]:
        """Handles a PrometheusAlertStatusChangedEvent.

        Args:
            event (Event): An event from the bus.

        Returns:
            Iterable[Event]: Trigger event when the received event was a PrometheusAlertStatusChangedEvent and when event name corresponds with the handler's name.
            []: Returns an empty list when the above does not hold.
        """
        if not isinstance(event, PrometheusAlertStatusChangedEvent):
            return []

        if self.alertname != event.alertname:
            return []

        return [TriggerEvent(self.name)]
