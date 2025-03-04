from unittest import mock

from httpx import AsyncClient

from lymphocyte.container import Container
from lymphocyte.events.bus import EventBus
from lymphocyte.events.handlers.webhook import WebhookEventHandler
from lymphocyte.events.trigger import TriggerEvent
from lymphocyte.events.webhook import WebhookEvent


async def test_webhook_dispatches_event(
    client: AsyncClient, container: Container
) -> None:
    event_bus = mock.Mock(EventBus)

    with container.event_bus.override(event_bus):
        response = await client.get("/webhook/asdf")

    assert response.json() == "ok"

    assert event_bus.dispatch_async.called
    arg = event_bus.dispatch_async.call_args[0][0]
    assert isinstance(arg, WebhookEvent)
    assert arg.name == "asdf"


async def test_webhook_event_handler() -> None:
    handler = WebhookEventHandler("trigger_name", "exact_matching_string")

    assert handler.name == "trigger_name"

    assert await handler.handle(WebhookEvent("not_matching_string")) == []

    res = list(await handler.handle(WebhookEvent("exact_matching_string")))
    assert len(res) == 1
    assert isinstance(res[0], TriggerEvent)
    assert res[0].name == "trigger_name"
