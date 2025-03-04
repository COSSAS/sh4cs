from dataclasses import dataclass

from lymphocyte.events.bus import Event


@dataclass
class WebhookEvent(Event):
    """Event communicating a webhook event

    Args:
        Event (Event): Base Event class
    """

    name: str
