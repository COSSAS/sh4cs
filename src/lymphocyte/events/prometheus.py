from dataclasses import dataclass

from lymphocyte.events.bus import Event


@dataclass
class PrometheusAlertStatusChangedEvent(Event):
    """Event from Prometheus whenever a alert status has changed.

    Args:
        Event (Event): Base Event class
    """

    alertname: str
    is_firing: bool
