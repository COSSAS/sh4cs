from dataclasses import dataclass

from lymphocyte.events.bus import Event


@dataclass
class TickEvent(Event):
    """Tick Event sent every second.

    Args:
        Event (Event): Base Event class
    """

    counter: int
