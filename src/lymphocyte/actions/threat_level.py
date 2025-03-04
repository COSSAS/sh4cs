import logging
from dataclasses import dataclass, field

from lymphocyte.actions.action import Action
from lymphocyte.managers.threat_level import ThreatLevelManager

log = logging.getLogger(__name__)


@dataclass
class IncrementThreatLevelAction(Action):
    """Using the ThreatLevelManager, this Action increases the threat-level number of the pod by a specified amount. Default is 1.

    Args:
        Action (Action): Base Action class
    """

    threat_level_manager: ThreatLevelManager

    by: float = field(default=1)
    for_seconds: float | None = field(default=None)

    async def perform(self) -> None:
        """Performs the increment to the threat level."""
        await self.threat_level_manager.increment(self.by, self.for_seconds)


@dataclass
class ResetThreatLevelAction(Action):
    """Using the ThreatLevelManager, this Action resets the threat-level number of the pod.

    Args:
        Action (Action): Base Action class
    """

    threat_level_manager: ThreatLevelManager

    async def perform(self) -> None:
        """Performs the resetting of the threat level."""
        await self.threat_level_manager.reset()
