import logging
from dataclasses import dataclass
from typing import Any

import jinja2
import jinja2.sandbox

from lymphocyte.actions.action import Action

log = logging.getLogger(__name__)


@dataclass(init=False)
class DebugAction(Action):
    """Debug Action that can be triggered. Gives the context of action.

    Args:
        Action (Action): Base action class
    """

    context: dict[str, Any]

    template: jinja2.Template

    def __init__(
        self,
        name: str,
        context: dict[str, Any],
        message: str,
        environment: jinja2.Environment = jinja2.sandbox.ImmutableSandboxedEnvironment(
            extensions=["jinja2.ext.debug"]
        ),
    ) -> None:
        """Constructs a DebugAction object.

        Args:
            name (str): Name of the action
            context (dict[str, Any]): Context variables.
            message (str): Template string passed to jinja. Jinja evaluates the template with the given context.
            environment (jinja2.Environment, optional): Current environment of the pod. Defaults to jinja2.sandbox.ImmutableSandboxedEnvironment( extensions=["jinja2.ext.debug"] ).
        """
        super().__init__(name)
        self.context = context
        self.template = environment.from_string(message)

    async def perform(self) -> None:
        """Perform the debugging action by logging."""
        if self.template.environment.is_async:  # type: ignore[attr-defined]
            log.debug(
                "%s",
                await self.template.render_async(self.context),
            )
        else:
            log.debug(
                "%s",
                self.template.render(self.context),
            )
