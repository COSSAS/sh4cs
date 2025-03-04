from datetime import datetime, timedelta

from lymphocyte.events.bus import EventBus
from lymphocyte.events.ttl import TTLChangedEvent, TTLRestartedEvent


class TTLManager:
    """Manager storing and setting the Time To Live of the application.

    Returns:
        float: Fraction passed of total TTL
    """

    event_bus: EventBus

    start_time: datetime
    base_ttl: timedelta
    current_ttl: timedelta

    def __init__(self, event_bus: EventBus, base_ttl: timedelta) -> None:
        """Construct a TTLManager object.

        Args:
            event_bus (EventBus): The event bus.
            base_ttl (timedelta): The default TTL.
        """
        self.event_bus = event_bus
        self.base_ttl = base_ttl
        self.current_ttl = base_ttl
        self.start_time = datetime.now()

    async def reset(self) -> None:
        """Reset the TTL of the application to its default, then restart() the TTL."""
        self.current_ttl = self.base_ttl
        await self.restart()

    async def restart(self) -> None:
        """Restart the TTL of the application. This changes the start time, but does not change the TTL."""
        self.start_time = datetime.now()
        await self.event_bus.dispatch_async(TTLRestartedEvent())

    def fraction_passed(self) -> float:
        """Expresses the time passed in a fraction.

        Returns:
            float: Fraction of total TTL that has passed.
        """
        return (datetime.now() - self.start_time) / self.current_ttl

    async def scale(self, fraction: float) -> None:
        """Scale the time to live by a float.

        Args:
            fraction (float): Value to scale the TTL by
        """
        if self.current_ttl * fraction <= timedelta():
            return
        self.current_ttl *= fraction
        await self.event_bus.dispatch_async(TTLChangedEvent())

    async def decrement(self, by: timedelta) -> None:
        """Decrease the TTL by an absolute value

        Args:
            by (timedelta): Value to decrease the TTL by
        """
        if self.current_ttl - by <= timedelta():
            return
        self.current_ttl -= by
        await self.event_bus.dispatch_async(TTLChangedEvent())

    async def set(self, goal: timedelta) -> None:
        """Set the TTL to a given value.

        Args:
            goal (timedelta): _description_
        """
        if goal <= timedelta():
            return
        self.current_ttl = goal
        await self.event_bus.dispatch_async(TTLChangedEvent())
