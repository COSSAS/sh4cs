from dataclasses import dataclass, field

from lymphocyte.events.bus import Event


@dataclass
class ThreatLevelChangedEvent(Event):
    """Event communicating another's threat-level change

    Args:
        Event (Event): Base Event class
    """

    current: float
    identifier: str
    host: str


@dataclass
class OwnThreatLevelChangedEvent(ThreatLevelChangedEvent):
    """Event communicating own threat-level change

    Args:
        Event (Event): Base Event class
    """

    current: float
    identifier: str = field(init=False, default="self")
    host: str = field(init=False, default="localhost")
