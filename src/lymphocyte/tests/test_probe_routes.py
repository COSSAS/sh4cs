import datetime
from unittest import mock

from freezegun import freeze_time
from httpx import AsyncClient

from lymphocyte.container import Container
from lymphocyte.events.bus import EventBus
from lymphocyte.managers.ttl import TTLManager
from lymphocyte.services.probe_service import ProbeService
from lymphocyte.settings import IncomingProbeSettings


async def test_liveness_probe_succeeds(
    client: AsyncClient, container: Container
) -> None:
    probe_service = mock.Mock(spec=ProbeService)
    probe_service.probe_liveness.return_value = True, None

    with container.probe_service.override(probe_service):
        response = await client.get("/livenessProbe")

    assert response.status_code == 200

    assert probe_service.probe_liveness.called


async def test_liveness_probe_fails(client: AsyncClient, container: Container) -> None:
    probe_service = mock.Mock(spec=ProbeService)
    unique_str = "some unique value"
    probe_service.probe_liveness.return_value = False, unique_str

    with container.probe_service.override(probe_service):
        response = await client.get("/livenessProbe")

    assert response.status_code != 200
    assert unique_str.encode() in response.content

    assert probe_service.probe_liveness.called


async def test_probe_fails_after_timedelta(
    client: AsyncClient, container: Container
) -> None:
    ttl = datetime.timedelta(minutes=5)

    event_bus = mock.Mock(EventBus)

    with freeze_time("2020-01-14 12:00:01") as frozen_datetime:
        with container.ttl_manager.override(
            TTLManager(event_bus=event_bus, base_ttl=ttl)
        ), container.config.incoming_probes.override(
            IncomingProbeSettings().model_dump()
        ):
            assert (await client.get("/livenessProbe")).status_code == 200
            assert (await client.get("/readinessProbe")).status_code == 200
            assert (await client.get("/startupProbe")).status_code == 200

            # Something long enough for the TTL manager
            frozen_datetime.tick(delta=ttl + datetime.timedelta(seconds=1))

            assert (await client.get("/livenessProbe")).status_code == 500
            assert (await client.get("/readinessProbe")).status_code == 500

            # Resets after receiving a startup probe again
            assert (await client.get("/startupProbe")).status_code == 200

            assert (await client.get("/livenessProbe")).status_code == 200
            assert (await client.get("/readinessProbe")).status_code == 200


async def test_probe_expressions(client: AsyncClient, container: Container) -> None:
    for startup_expression in ["true", "false"]:
        for readiness_expression in ["true", "false"]:
            for liveness_expression in ["true", "false"]:
                with container.config.incoming_probes.override(
                    IncomingProbeSettings(
                        startup_expression=startup_expression,
                        readiness_expression=readiness_expression,
                        liveness_expression=liveness_expression,
                    ).model_dump()
                ):
                    assert (await client.get("/startupProbe")).status_code == (
                        200 if startup_expression == "true" else 500
                    )
                    assert (await client.get("/readinessProbe")).status_code == (
                        200 if readiness_expression == "true" else 500
                    )
                    assert (await client.get("/livenessProbe")).status_code == (
                        200 if liveness_expression == "true" else 500
                    )
