from typing import Any

import jinja2
import jinja2.sandbox

from lymphocyte.managers.ttl import TTLManager


class ProbeService:
    """Probe base class to probe liveness, readiness, and startup."""

    def __init__(
        self,
        ttl_manager: TTLManager,
        startup_expression: str,
        readiness_expression: str,
        liveness_expression: str,
        context: dict[str, Any],
        environment: jinja2.Environment = jinja2.sandbox.ImmutableSandboxedEnvironment(
            extensions=["jinja2.ext.debug"]
        ),
    ) -> None:
        """Constructs a ProbeService object

        Args:
            ttl_manager (TTLManager): Time To Live manager of the lymphocyte regarding the subject application
            startup_expression (str): String expressing startup
            readiness_expression (str): String expressing readiness
            liveness_expression (str): String expressing liveness
            context (dict[str, Any]): Context variables
            environment (jinja2.Environment, optional): Environment. Defaults to jinja2.sandbox.ImmutableSandboxedEnvironment( extensions=["jinja2.ext.debug"] ).
        """
        self.ttl_manager = ttl_manager
        self.startup_expression = startup_expression
        self.readiness_expression = readiness_expression
        self.liveness_expression = liveness_expression
        self.context = context
        self.environment = environment

    def check_condition(self, condition: str) -> tuple[bool, str | None]:
        """Check if a condition hold in the environment given the context variables

        Args:
            condition (str): Condition to check

        Returns:
            tuple[bool, str | None]: Returns bool regarding correctness, accompanied by either None when true, or the condition when false.
        """
        if bool(self.environment.compile_expression(condition)(self.context)):
            return True, None

        return False, condition + " does not hold"

    async def probe_liveness(self) -> tuple[bool, str | None]:
        """Check the liveness of the subject application

        Returns:
            tuple[bool, str | None]: Returns bool regarding correctness, accompanied by either None when true, or the condition when false.
        """
        return self.check_condition(self.liveness_expression)

    async def probe_readiness(self) -> tuple[bool, str | None]:
        """Check the readiness of the subject application

        Returns:
            tuple[bool, str | None]: Returns bool regarding correctness, accompanied by either None when true, or the condition when false.
        """
        return self.check_condition(self.readiness_expression)

    async def probe_startup(self) -> tuple[bool, str | None]:
        """Reset the TTL Manager. THen, check the startup of the subject application

        Returns:
            tuple[bool, str | None]: Returns bool regarding correctness, accompanied by either None when true, or the condition when false.
        """
        await self.ttl_manager.reset()
        return self.check_condition(self.startup_expression)
