import asyncio
import collections
import datetime

from lymphocyte.events.bus import EventBus
from lymphocyte.events.threat_level import (
    OwnThreatLevelChangedEvent,
    ThreatLevelChangedEvent,
)


class ThreatLevelManager:
    """Manager setting and storing the state of own threat-level.

    Returns:
        float: Current threat-level
    """

    _event_bus: EventBus

    _base_level: float
    _current_level: float

    def __init__(self, event_bus: EventBus, base_level: float) -> None:
        """Constructs a ThreatLevelManager object.

        Args:
            event_bus (EventBus): The event bus.
            base_level (float): Base threat level value.
        """
        self._event_bus = event_bus
        self._base_level = base_level
        self._current_level = base_level

    async def reset(self) -> None:
        """Resets the threat level to the base value."""
        self._current_level = self._base_level
        await self.notify_changed()

    async def _decrement_after_increment(
        self, amount: float, sleep_for_seconds: float
    ) -> None:
        """Decrease the threat level after n seconds to accomodate a temporary increment. Can be called by increment().

        Args:
            amount (float): Value to decrease the threat level by.
            sleep_for_seconds (float): Seconds to wait before decreasing the threat level back.
        """
        await asyncio.sleep(sleep_for_seconds)
        await self.increment(-amount, None)

    async def increment(self, amount: float, for_seconds: float | None = None) -> None:
        """Increase the threat level, possibly temporarily.

        Args:
            amount (float): Value to increase the threat level by
            for_seconds (float | None, optional): Amount of seconds of temporary increment. Defaults to None.
        """
        self._current_level += amount
        await self.notify_changed()

        if for_seconds:
            asyncio.get_event_loop().create_task(
                self._decrement_after_increment(amount, for_seconds)
            )

    async def notify_changed(self) -> None:
        """Dispatch an OwnThreatLevelChangedEvent onto the eventbus."""
        await self._event_bus.dispatch_async(OwnThreatLevelChangedEvent(self.current))

    @property
    def current(self) -> float:
        return self._current_level


ThreatLevelRecordIdentifiers = collections.namedtuple(
    "ThreatLevelRecordIdentifiers", ["identifier", "host"]
)
ThreatLevelRecordValues = collections.namedtuple(
    "ThreatLevelRecordValues", ["level", "last_update"]
)
ThreatLevelRecord = collections.namedtuple(
    "ThreatLevelRecord", ["identifier", "host", "level", "last_update"]
)


class OtherThreatLevelsManager:
    """Manager setting and storing the state of others' threat-levels.

    Returns:
        float: Current threat-level of others
    """

    _event_bus: EventBus

    _current_levels: dict[ThreatLevelRecordIdentifiers, ThreatLevelRecordValues]

    def __init__(self, event_bus: EventBus) -> None:
        """Constructs a OtherThreatLevelsManager object.

        Args:
            event_bus (EventBus): The event bus.
        """
        self._event_bus = event_bus
        self._current_levels = {}

    async def set(self, identifier: str, host: str, level: float) -> None:
        """Set the current threat level of another application, given identifier, host, and level.

        Args:
            identifier (str): Application identifier
            host (str): Hostname
            level (float): Value to set the threatlevel to.
        """
        self._current_levels[
            ThreatLevelRecordIdentifiers(identifier, host)
        ] = ThreatLevelRecordValues(level, datetime.datetime.now())
        await self.notify_changed(identifier=identifier, host=host, current=level)

    def get(
        self,
        identifier_match: str | None = None,
        host_match: str | None = None,
        value_gte: float | None = None,
        value_lte: float | None = None,
        after: datetime.datetime | None = None,
    ) -> list[ThreatLevelRecord]:
        """Get the threat level records of other applications, possibly given some identifier, host, value range, and minimum date.

        Args:
            identifier_match (str | None, optional): Identifier to match by. Defaults to None.
            host_match (str | None, optional): Host to match by. Defaults to None.
            value_gte (float | None, optional): Minimum threat level to match by. Defaults to None.
            value_lte (float | None, optional): Maximum threat level to match by. Defaults to None.
            after (datetime.datetime | None, optional): Minimum date to match by. Defaults to None.

        Returns:
            list[ThreatLevelRecord]: List of threat level records.
        """
        return [
            ThreatLevelRecord(identifier, host, value, last_update)
            for (identifier, host), (value, last_update) in self._current_levels.items()
            if (identifier_match is None or identifier == identifier_match)
            and (host_match is None or host == host_match)
            and (value_gte is None or value >= value_gte)
            and (value_lte is None or value <= value_lte)
            and (after is None or last_update > after)
        ]

    async def notify_changed(self, identifier: str, host: str, current: float) -> None:
        """Put a ThreatLevelChangedEvent on the event bus.

        Args:
            identifier (str): Identifier matching the application of the threat level change.
            host (str): host matching the application of the threat level change.
            current (float): Current threat level of the application.
        """
        await self._event_bus.dispatch_async(
            ThreatLevelChangedEvent(identifier=identifier, host=host, current=current)
        )
