from dataclasses import dataclass

from lymphocyte.events.bus import Event


@dataclass
class ActionTriggerEvent(Event):
    name: str
