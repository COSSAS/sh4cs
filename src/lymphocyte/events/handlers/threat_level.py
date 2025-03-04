import logging
from collections.abc import Iterable
from dataclasses import dataclass, field

from prometheus_client import Gauge

from lymphocyte.events.bus import Event, EventHandler
from lymphocyte.events.threat_level import (
    OwnThreatLevelChangedEvent,
    ThreatLevelChangedEvent,
)
from lymphocyte.events.trigger import TriggerEvent

log = logging.getLogger(__name__)


@dataclass
class ThreatLevelChangedHandler(EventHandler):
    """EventHandler for threat-level changes.

    Args:
        EventHandler (EventHandler): Base EventHandler class

    Returns:
        TriggerEvent: TriggerEvent of base class Event with named trigger.
    """

    name: str
    identifier: str
    host: str | None = field(default=None)

    async def handle(self, event: Event) -> Iterable[Event]:
        """Handles a ThreatLevelChangedEvent.

        Args:
            event (Event): An event from the event bus

        Returns:
            Iterable[Event]: Trigger event when: the received event was a ThreatLevelChangedEvent, when the handler and event identifiers match, and when the event's and handler's hosts are not the same.
            []: Returns an empty list when the above does not hold.
        """
        if not isinstance(event, ThreatLevelChangedEvent):
            return []

        if self.identifier != event.identifier:
            return []
        if self.host and self.host != event.host:
            return []

        return [TriggerEvent(self.name)]


@dataclass
class PrometheusThreatLevelChangedHandler(EventHandler):
    """EventHandler for Prometheus threat-level changes. Sets threat-level metric with the Prometheus threat-level

    Args:
        EventHandler (EventHandler): Base EventHandler class

    Returns:
        list: Returns empty list after setting the threat-level metric.
    """

    threat_level_metric: Gauge

    async def handle(self, event: Event) -> Iterable[Event]:
        """Handles an OwnThreatLevelChangedEvent. Sets the threat level metric after receiving the corresponding event.

        Args:
            event (Event): An event from the event bus.

        Returns:
            Iterable[Event]: Returns an empty list. No new events are passed on the event bus by this event handler.
        """
        if not isinstance(event, OwnThreatLevelChangedEvent):
            return []

        self.threat_level_metric.set(event.current)
        return []
