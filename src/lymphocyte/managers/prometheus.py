import datetime
from collections import namedtuple

from lymphocyte.events.bus import EventBus
from lymphocyte.events.prometheus import PrometheusAlertStatusChangedEvent

StatusRecordIdentifiers = namedtuple("StatusRecordIdentifiers", ["alertname"])
StatusRecordValues = namedtuple("StatusRecordValues", ["current_status", "last_change"])
StatusRecord = namedtuple(
    "StatusRecord", ["alertname", "current_status", "last_change"]
)


class PrometheusManager:
    """Manager storing the state of Prometheus alerts and records with the use of set and get methods.

    Returns:
        list: the get method returns statusrecords
    """

    _event_bus: EventBus

    _statuses: dict[StatusRecordIdentifiers, StatusRecordValues]

    def __init__(self, event_bus: EventBus) -> None:
        """Constructs an PrometheusManager object

        Args:
            event_bus (EventBus): The event bus.
        """
        self._event_bus = event_bus
        self._statuses = {}

    async def set(self, alertname: str, is_firing: bool) -> None:
        """Keeps track of the alert-manager's alerts' firing state, which get communicated via a webhook.

        Args:
            alertname (str): Prometheus status record identifier.
            is_firing (bool): Status of alert firing.
        """
        identifier = StatusRecordIdentifiers(alertname)

        if (
            identifier in self._statuses
            and self._statuses[identifier].current_status == is_firing
        ):
            return

        self._statuses[identifier] = StatusRecordValues(
            is_firing, datetime.datetime.now()
        )
        await self._event_bus.dispatch_async(
            PrometheusAlertStatusChangedEvent(identifier.alertname, is_firing)
        )

    def get(
        self,
        alertname_eq: str | None = None,
        status_eq: bool | None = None,
        last_change_after: datetime.datetime | None = None,
    ) -> list[StatusRecord]:
        """Get status records with optionally given alert name, status and last change date.

        Args:
            alertname_eq (str | None, optional): _description_. Defaults to None.
            status_eq (bool | None, optional): _description_. Defaults to None.
            last_change_after (datetime.datetime | None, optional): _description_. Defaults to None.

        Returns:
            list[StatusRecord]: _description_
        """
        return [
            StatusRecord(alertname, status, last_change)
            for (alertname,), (status, last_change) in self._statuses.items()
            if (alertname_eq is None or alertname_eq == alertname)
            and (status_eq is None or status == status_eq)
            and (last_change_after is None or last_change > last_change_after)
        ]
