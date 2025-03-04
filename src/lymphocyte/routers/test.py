"""
A set of routes for demonstration/debugging purposes, giving insight into the internals of the system.
"""

import logging
from typing import Any, Literal

import jinja2.sandbox
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from lymphocyte.actions.action_trigger_event import ActionTriggerEvent
from lymphocyte.events.bus import Event, EventBus, EventHandlerService
from lymphocyte.events.handlers.generic import GenericEventHandler
from lymphocyte.events.trigger import TriggerEvent
from lymphocyte.settings import Settings

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/evaluate_expression", tags=["test"])
@inject
def evaluate_expression(
    expression: str,
    context: dict[str, Any] = Depends(Provide["context"]),
) -> JSONResponse:
    """Evaluates arbitrary jinja templates for debugging purposes.

    Args:
        expression (str): Expression to be evaluated
        context (dict[str, Any], optional): Context variables in which the expression is evaluated. Defaults to Depends(Provide["context"]).

    Returns:
        JSONResponse: Evaluated response in JSON format
    """
    env = jinja2.sandbox.ImmutableSandboxedEnvironment(extensions=["jinja2.ext.debug"])
    result = env.compile_expression(expression)(context)
    return JSONResponse(content=jsonable_encoder(result))


@router.get("/event_handlers", tags=["test"])
@inject
async def list_event_handlers(
    event_handler_service: EventHandlerService = Depends(
        Provide["event_handler_service"]
    ),
) -> list[str]:
    """Returns the list of event handlers

    Args:
        event_handler_service (EventHandlerService, optional): Event handlers. Defaults to Depends( Provide["event_handler_service"] ).

    Returns:
        list[str]: list of event handlers names
    """
    return [handler.__repr__() for handler in event_handler_service.handlers]


@router.get("/activate_trigger", tags=["test"])
@inject
async def activate_trigger(
    name: str,
    event_bus: EventBus = Depends(Provide["event_bus"]),
) -> Literal[True]:
    """Manually put a named trigger on the event bus

    Args:
        name (str): Name of named trigger
        event_bus (EventBus, optional): Event bus. Defaults to Depends(Provide["event_bus"]).

    Returns:
        Literal[True]: Returns True after dispatching the trigger on the event bus.
    """
    await event_bus.dispatch_async(TriggerEvent(name))
    return True


@router.get("/activate_action", tags=["test"])
@inject
async def activate_action(
    name: str,
    event_bus: EventBus = Depends(Provide["event_bus"]),
) -> Literal[True]:
    """Manually put a named action on the event bus

    Args:
        name (str): Name of named action
        event_bus (EventBus, optional): Event bus. Defaults to Depends(Provide["event_bus"]).

    Returns:
        Literal[True]: Returns True after dispatching the action on the event bus.
    """
    await event_bus.dispatch_async(ActionTriggerEvent(name))
    return True


@router.get("/current_config", tags=["test"])
@inject
async def current_config(
    config: Settings = Depends(Provide["config"]),
) -> Settings:
    """Returns the current config of the environment.

    Args:
        config (Settings, optional): Current config in use. Defaults to Depends(Provide["config"]).

    Returns:
        Settings: Current config parameters
    """
    return config


@router.get("/current_tasks", tags=["test"])
@inject
async def current_tasks() -> list[str]:
    """Gets all current tasks running in the lymphocyte

    Returns:
        list[str]: Names of current tasks running.
    """
    import asyncio

    tasks = asyncio.all_tasks()
    return [task.get_name() for task in tasks]


@router.get("/all_events", tags=["test"])
async def test() -> HTMLResponse:
    return HTMLResponse(
        """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
        <div class="container">
        <h1>Events</h1>
        <ul id='all_events'>
        </ul>
        </div>
        <script>
            var url;
            if (window.location.protocol === "https:") {
                url = "wss:";
            } else {
                url = "ws:";
            }
            url += "//" + window.location.host + "/all_events"
            var ws = new WebSocket(url);
            console.log(ws);
            ws.onmessage = function(event) {
                console.log(event);
                var data = JSON.parse(event.data)
                var kind = data.kind
                var data = JSON.stringify(data.event, null, 2)

                var single_event = document.createElement('article')
                single_event.classList.add('message')
                single_event.classList.add('is-small')

                var header = document.createElement('div')
                header.classList.add('message-header')
                header.appendChild(document.createElement('em')).appendChild(document.createTextNode(new Date().toISOString()))
                header.appendChild(document.createTextNode(kind))
                single_event.appendChild(header)

                var body = document.createElement('div')
                body.classList.add('message-body')
                body.appendChild(document.createElement('pre')).appendChild(document.createTextNode(data))
                single_event.appendChild(body)

                document.getElementById('all_events').prepend(single_event)
            };
        </script>
    """
    )


@router.websocket("/all_events")
@inject
async def websocket_event_provider(
    websocket: WebSocket,
    event_handler_service: EventHandlerService = Depends(
        Provide["event_handler_service"]
    ),
) -> None:
    """Outputs all events from the event bus, for debugging purposes.

    Args:
        websocket (WebSocket): __
        event_handler_service (EventHandlerService, optional): __. Defaults to Depends( Provide["event_handler_service"] ).
    """
    await websocket.accept()

    handler = GenericEventHandler[Event](Event)

    event_handler_service.register(handler)
    try:
        async for event in handler:
            await websocket.send_json(
                {"kind": str(type(event)), "event": event.__dict__}
            )
    finally:
        event_handler_service.unregister(handler)
