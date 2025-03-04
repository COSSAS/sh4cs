from dataclasses import dataclass

from lymphocyte.events.bus import Event


@dataclass
class TTLChangedEvent(Event):
    """Event communicating a threat-level change.

    Args:
        Event (Event): Base Event class
    """


@dataclass
class TTLRestartedEvent(Event):
    """Event communicating a threat-level reset.

    Args:
        Event (Event): Base Event class
    """
