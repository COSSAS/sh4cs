import logging
from dataclasses import dataclass
from datetime import timedelta

from lymphocyte.actions.action import Action
from lymphocyte.managers.ttl import TTLManager

log = logging.getLogger(__name__)


@dataclass
class ScaleTTLAction(Action):
    """Action that multiplies the TTL by a given float.

    Args:
        Action (Action): Base Action class
    """

    ttl_manager: TTLManager

    by: float

    async def perform(self) -> None:
        await self.ttl_manager.scale(self.by)


@dataclass
class DecrementTTLAction(Action):
    """Action that decreases the TTL by a given number of seconds.

    Args:
        Action (Action): Base Action class
    """

    ttl_manager: TTLManager

    by_seconds: float

    async def perform(self) -> None:
        """Performs the decrement of the TTL"""
        await self.ttl_manager.decrement(timedelta(seconds=self.by_seconds))


@dataclass
class SetTTLAction(Action):
    """Action that Sets the TTL by a given number of seconds.

    Args:
        Action (Action): Base Action class
    """

    ttl_manager: TTLManager

    to_seconds: float

    async def perform(self) -> None:
        """Performs the setting of the TTL."""
        await self.ttl_manager.set(timedelta(seconds=self.to_seconds))


@dataclass
class RestartTTLAction(Action):
    """Action that restarts the TTL to its default value.

    Args:
        Action (Action): Base Action class
    """

    ttl_manager: TTLManager

    async def perform(self) -> None:
        """Performs the restarting of the TTL Manager."""
        await self.ttl_manager.restart()
