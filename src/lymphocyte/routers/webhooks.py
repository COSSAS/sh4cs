from typing import Literal

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from lymphocyte.events.bus import EventBus
from lymphocyte.events.webhook import WebhookEvent

# from lymphocyte.managers.webhook_manager import WebhookTriggers

router = APIRouter()


@router.get("/webhook/{name}")
@router.post("/webhook/{name}")
@inject
async def webhook(
    name: str, event_bus: EventBus = Depends(Provide["event_bus"])
) -> Literal["ok"]:
    """Dispatches a manual webhook event onto the eventbus

    Returns:
        str: returns "ok" after dispatching.
    """
    await event_bus.dispatch_async(WebhookEvent(name))
    return "ok"
