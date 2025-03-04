from dataclasses import dataclass

from lymphocyte.events.bus import Event


@dataclass
class TriggerEvent(Event):
    """Event communicating a named trigger

    Args:
        Event (Event): Base Event class
    """

    name: str
