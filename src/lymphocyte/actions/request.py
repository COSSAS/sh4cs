import logging
from dataclasses import dataclass
from typing import Any

import httpx

from lymphocyte.actions.action import Action

log = logging.getLogger(__name__)


@dataclass
class SendRestRequestAction(Action):
    """Action that sends a HTTP REST request to a
    specified url with specified HTTP method, url query parameters, form data, json body and/or
    HTTP headers.

        Args:
            Action (Action): Base Action class
    """

    url: str
    method: str = "GET"
    params: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    json: Any = None
    headers: dict[str, Any] | None = None

    async def perform(self) -> None:
        """Perform the Rest Request Action."""
        async with httpx.AsyncClient() as client:
            await client.request(
                method=self.method,
                url=self.url,
                params=self.params,
                data=self.data,
                json=self.json,
                headers=self.headers,
            )
