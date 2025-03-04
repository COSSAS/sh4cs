from unittest import mock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from lymphocyte.container import Container
from lymphocyte.events.bus import EventHandlerService
from lymphocyte.events.threat_level import OwnThreatLevelChangedEvent
from lymphocyte.managers.threat_level import ThreatLevelManager


async def test_threat_level_exposed(client: AsyncClient, container: Container) -> None:
    threat_level_manager = mock.Mock(ThreatLevelManager)
    threat_level_manager.current = 1234

    with container.threat_level_manager.override(threat_level_manager):
        response = await client.get("/threat_level")

    assert response.status_code == 200
    assert float(response.text) == 1234


@pytest.mark.skip(reason="websockets hang during testing")
async def test_threat_level_exposed_by_websocket(
    test_client: TestClient, container: Container
) -> None:
    event_handler_service = mock.Mock(EventHandlerService)
    event_handler_service.register = lambda handler: handler.handle(
        OwnThreatLevelChangedEvent(123)
    )

    threat_level_manager = mock.Mock(ThreatLevelManager)
    threat_level_manager.current = 1234

    with container.threat_level_manager.override(
        threat_level_manager
    ), container.event_handler_service.override(event_handler_service):
        with test_client.websocket_connect("/threat_level") as ws:
            data = ws.receive_json()
            assert data == {"threat_level": threat_level_manager.current}

            data = ws.receive_json()
            assert data == {"threat_level": 123}
