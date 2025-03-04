import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import jinja2
import jinja2.sandbox

from lymphocyte.actions.action_trigger_event import ActionTriggerEvent
from lymphocyte.events.bus import Event, EventHandler
from lymphocyte.events.trigger import TriggerEvent

log = logging.getLogger(__name__)


@dataclass
class ConditionalRule(EventHandler):
    """Class for conditional rules.

    Args:
        EventHandler (EventHandler): Bass class EventHandler.

    Returns:
        ActionTriggerEvent: When a conditional rule holds
        []: In every other case
    """

    triggers: list[str]
    actions: list[str]
    condition: str | None = field(default=None)

    context: dict[str, Any] = field(default_factory=dict)
    environment: jinja2.Environment = field(
        default_factory=jinja2.sandbox.ImmutableSandboxedEnvironment
    )

    async def check_condition(self) -> bool:
        if not self.condition:
            return True
        return bool(self.environment.compile_expression(self.condition)(self.context))

    async def handle(self, event: Event) -> Iterable[Event]:
        if not isinstance(event, TriggerEvent):
            return []

        if event.name not in self.triggers:
            return []

        if not await self.check_condition():
            log.debug("Condition '%s' does not hold", self.condition)
            return []

        log.debug("Condition '%s' holds", self.condition)
        return [ActionTriggerEvent(action_name) for action_name in self.actions]
