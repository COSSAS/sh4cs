from unittest import mock

from lymphocyte.events.bus import EventBus
from lymphocyte.events.threat_level import ThreatLevelChangedEvent
from lymphocyte.managers.threat_level import OtherThreatLevelsManager


async def test_other_threat_levels_manager_initializes() -> None:
    event_bus = mock.Mock(EventBus)

    manager = OtherThreatLevelsManager(event_bus)
    assert manager.get() == []


async def test_other_threat_levels_manager_dispatches_event() -> None:
    event_bus = mock.Mock(EventBus)

    manager = OtherThreatLevelsManager(event_bus)

    await manager.set("some_identifier", "some_host", 123)

    assert event_bus.dispatch_async.called
    arg = event_bus.dispatch_async.call_args[0][0]
    assert isinstance(arg, ThreatLevelChangedEvent)
    assert arg.identifier == "some_identifier"
    assert arg.host == "some_host"
    assert arg.current == 123
