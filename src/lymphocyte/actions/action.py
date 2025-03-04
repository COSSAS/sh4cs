import abc
import asyncio
from collections.abc import Iterable
from dataclasses import dataclass

from lymphocyte.actions.action_trigger_event import ActionTriggerEvent
from lymphocyte.events.bus import Event, EventHandler


@dataclass
class Action(EventHandler, abc.ABC):
    """Action parent class. Just like Events, Actions can be put on the eventbus.

    Args:
        EventHandler (EventHandler): Base EventHandler class
        abc (ABC):
    """

    name: str

    async def handle(self, event: Event) -> Iterable[Event]:
        if not isinstance(event, ActionTriggerEvent):
            return []

        if event.name != self.name:
            return []

        asyncio.create_task(self.perform())
        return []

    @abc.abstractmethod
    async def perform(self) -> None:
        """Abstract method for Action sub-classes"""
