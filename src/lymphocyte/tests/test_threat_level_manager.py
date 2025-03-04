import asyncio
from unittest import mock

import pytest

from lymphocyte.events.bus import EventBus
from lymphocyte.managers.threat_level import ThreatLevelManager

levels = [
    (0, 1),
    (123, 1),
    (-123, 1),
    (0, -1),
    (123, -1),
    (-123, -1),
]


@pytest.mark.parametrize("base_level,_", levels)
async def test_threat_level_manager_initializes(base_level: float, _: float) -> None:
    event_bus = mock.Mock(EventBus)

    manager = ThreatLevelManager(event_bus, base_level=base_level)
    assert manager.current == base_level


@pytest.mark.parametrize("base_level,increment_by", levels)
async def test_threat_level_manager_increments(
    base_level: float, increment_by: float
) -> None:
    event_bus = mock.Mock(EventBus)

    manager = ThreatLevelManager(event_bus, base_level=base_level)

    await manager.increment(increment_by)

    assert manager.current == base_level + increment_by


@pytest.mark.parametrize("base_level,increment_by", levels)
async def test_threat_level_manager_increments_for_duration(
    base_level: float, increment_by: float
) -> None:
    event_bus = mock.Mock(EventBus)

    manager = ThreatLevelManager(event_bus, base_level=base_level)

    increment_for_duration = 0.1

    await manager.increment(increment_by, increment_for_duration)
    assert manager.current == base_level + increment_by

    await asyncio.sleep(increment_for_duration + 0.1)
    assert manager.current == base_level
