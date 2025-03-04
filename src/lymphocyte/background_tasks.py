import asyncio
import itertools
import json
import logging
import socket
from dataclasses import dataclass
from typing import NoReturn, Protocol

import httpx
import websockets
import websockets.uri

from lymphocyte.events.bus import Event, EventBus, EventHandlerService
from lymphocyte.events.tick import TickEvent
from lymphocyte.managers.outgoing_probes import OutgoingProbesManager
from lymphocyte.managers.threat_level import OtherThreatLevelsManager
from lymphocyte.settings import SingleOutgoingProbeSettings

log = logging.getLogger(__name__)


class BackgroundTask(Protocol):
    """Base class for background tasks.

    Args:
        Protocol (Protocol): Protocol class for base classes.
    """

    async def perform(self) -> NoReturn | None:
        ...


@dataclass
class EventConsumerTask(BackgroundTask):
    """Background task which reads events from the given event bus and passes them to the given event handler.

    Args:
        BackgroundTask (BackgroundTask): __
    """

    from_queue: asyncio.Queue[Event]
    event_handler_service: EventHandlerService
    to_queue: EventBus

    async def perform(self) -> None:
        while True:
            try:
                event = await self.from_queue.get()
                async for new_event in self.event_handler_service.handle(event):
                    log.debug("Dispatched new event %s", new_event)
                    await self.to_queue.dispatch_async(new_event)
                self.from_queue.task_done()
            except asyncio.exceptions.CancelledError:
                raise
            except Exception:  # Log all others # pylint: disable=broad-exception-caught
                log.exception("Error during consuming")


@dataclass
class TickTriggerTask(BackgroundTask):
    """Class for tick triggers. Places a Tick Event on the bus every second.

    Args:
        BackgroundTask (BackgroundTask): Base class for background tasks.
    """

    event_bus: EventBus

    async def perform(self) -> None:
        for counter in itertools.count(1):
            await asyncio.sleep(1)
            await self.event_bus.dispatch_async(TickEvent(counter=counter))


@dataclass
class ThreatLevelMonitorTask(BackgroundTask):
    """Monitors the threat level of other lymphos.

    Args:
        BackgroundTask (BackgroundTask): Base class for background tasks.
    """

    identifier: str
    uri: str
    other_threat_levels_manager: OtherThreatLevelsManager

    async def perform(self) -> None:
        hostname = websockets.uri.parse_uri(self.uri).host

        tasks: dict[str, asyncio.Task[None]] = {}
        first = True
        while True:
            try:
                if not first:
                    await asyncio.sleep(5)
                else:
                    first = False

                try:
                    _, _, hosts = socket.gethostbyname_ex(hostname)
                except socket.gaierror:
                    hosts = []

                for host, task in tasks.items():
                    if host not in hosts:
                        log.debug(
                            "Stopping task for host %s: %s", host, task.get_name()
                        )
                        task.cancel()

                # Remove tasks that are done from the task dict
                tasks = {host: task for host, task in tasks.items() if not task.done()}

                for host in hosts:
                    if host not in tasks:
                        log.debug("Starting %s", f"ws_conn-{self.identifier}-{host}")
                        tasks[host] = asyncio.create_task(
                            self.websocket_connection(
                                identifier=self.identifier,
                                uri=self.uri,
                                host=host,
                                other_threat_levels_manager=self.other_threat_levels_manager,
                            ),
                            name=f"ws_conn-{self.identifier}-{host}",
                        )
            except asyncio.exceptions.CancelledError:
                log.debug("Canceled connection manager")
                return
            except Exception:  # Log all others # pylint: disable=broad-exception-caught
                log.exception("Exception in websocket connection manager")
                continue

    async def websocket_connection(
        self,
        identifier: str,
        uri: str,
        host: str,
        other_threat_levels_manager: OtherThreatLevelsManager,
    ) -> None:
        for exp in range(5):
            try:
                log.debug("Connecting to %s with uri %s", host, uri)

                async with websockets.connect(
                    uri=uri,
                    host=host,
                ) as websocket:
                    log.debug("Connected to %s", websocket)
                    try:
                        while True:
                            response_raw = await websocket.recv()
                            log.debug("Received message: %s", response_raw)

                            response = json.loads(response_raw)

                            if not isinstance(response, dict):
                                log.warning("Not a dict, ignoring")
                                continue
                            if "threat_level" not in response:
                                log.warning("threat_level not in dict, ignoring")
                                continue
                            if not isinstance(
                                response["threat_level"], float
                            ) and not isinstance(response["threat_level"], int):
                                log.warning("threat_level not a float or int, ignoring")
                                continue
                            log.debug(
                                "Setting %s threat level %s",
                                host,
                                response["threat_level"],
                            )
                            await other_threat_levels_manager.set(
                                identifier=identifier,
                                host=host,
                                level=response["threat_level"],
                            )
                    except asyncio.exceptions.CancelledError:
                        raise
                    except:
                        log.warning("Exception while receiving")
                        raise
            except OSError as e:
                log.debug("Connection failed: %s", e.strerror)
            except websockets.ConnectionClosed:
                log.debug("Connection closed")
            except asyncio.exceptions.CancelledError:
                log.debug("Canceled")
                return
            except Exception:  # Log all others # pylint: disable=broad-exception-caught
                log.exception("Failed connecting")

            log.debug("Sleeping %d seconds", 2**exp)
            await asyncio.sleep(2**exp)


@dataclass
class ProbeTask(BackgroundTask):
    """Class for outgoing probe tasks, getting the status of other applications.

    Args:
        BackgroundTask (_type_): _description_
    """

    settings: SingleOutgoingProbeSettings
    probe_manager: OutgoingProbesManager
    dependent_probe_manager: OutgoingProbesManager | None = None

    async def perform(self) -> None:
        try:
            while True:
                while (
                    self.dependent_probe_manager is not None
                    and not self.dependent_probe_manager.status()
                ):
                    await asyncio.sleep(0.5)

                await asyncio.sleep(self.settings.initial_delay_seconds)

                while True:
                    try:
                        async with httpx.AsyncClient(
                            base_url=f"http://localhost:{self.settings.port}/"
                        ) as client:
                            res = await client.get(self.settings.path)
                            self.probe_manager.set(res.status_code < 400)

                        await asyncio.sleep(self.settings.period_seconds)
                    except asyncio.exceptions.CancelledError:
                        raise
                    except httpx.HTTPError:
                        self.probe_manager.set(False)
                        continue
        except asyncio.exceptions.CancelledError:
            raise
        except Exception:  # Log all others # pylint: disable=broad-exception-caught
            log.exception("Exception in outgoing probes manager")
