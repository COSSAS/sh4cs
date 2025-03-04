import asyncio
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from lymphocyte.events.bus import EventHandlerService
from lymphocyte.events.handlers.generic import GenericEventHandler
from lymphocyte.events.threat_level import OwnThreatLevelChangedEvent
from lymphocyte.managers.threat_level import ThreatLevelManager

router = APIRouter()

log = logging.getLogger(__name__)


@router.get("/threat_level")
@inject
async def threat_level(
    threat_level_manager: ThreatLevelManager = Depends(Provide["threat_level_manager"]),
) -> float:
    """Get the current threat level through the manager.

    Args:
        threat_level_manager (ThreatLevelManager, optional): Threat level manager of the lympho. Defaults to Depends(Provide["threat_level_manager"]).

    Returns:
        float: Current threat level
    """
    log.info(threat_level_manager)

    return threat_level_manager.current


@router.websocket("/threat_level")
@inject
async def websocket_threat_level_provider(
    websocket: WebSocket,
    threat_level_manager: ThreatLevelManager = Depends(Provide["threat_level_manager"]),
    event_handler_service: EventHandlerService = Depends(
        Provide["event_handler_service"]
    ),
) -> None:
    """Websocket endpoint which outputs its own threat level when it changes.

    Args:
        websocket (WebSocket): __
        threat_level_manager (ThreatLevelManager, optional): __. Defaults to Depends(Provide["threat_level_manager"]).
        event_handler_service (EventHandlerService, optional): __. Defaults to Depends( Provide["event_handler_service"] ).
    """
    await websocket.accept()

    log.debug("Accepted, headers: %s", websocket.headers)

    handler = GenericEventHandler[OwnThreatLevelChangedEvent](
        OwnThreatLevelChangedEvent
    )

    event_handler_service.register(handler)
    try:
        await websocket.send_json({"threat_level": threat_level_manager.current})

        async for event in handler:
            await websocket.send_json({"threat_level": event.current})
    except WebSocketDisconnect:
        log.debug("Websocket disconnected")
    except asyncio.exceptions.CancelledError:
        pass
    except:  # Log all others # pylint: disable=bare-except
        log.exception("Error with websocket")
    finally:
        event_handler_service.unregister(handler)
