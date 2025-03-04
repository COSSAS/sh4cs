from collections.abc import Iterable
from typing import TypeVar

from dependency_injector import containers, providers
from fastapi import FastAPI

from lymphocyte.background_tasks import (
    BackgroundTask,
    EventConsumerTask,
    ProbeTask,
    ThreatLevelMonitorTask,
    TickTriggerTask,
)
from lymphocyte.instrumentors import (
    InstrumentFastAPI,
    RegisterBackgroundTasks,
    RegisterMiddlewares,
    RegisterPrometheus,
    RegisterRoutes,
)
from lymphocyte.settings import SingleOutgoingProbeSettings

T = TypeVar("T")


def create_event_handlers(
    factories: providers.Aggregate[T],
    config: dict[str, list[dict[str, str]]],
) -> list[T]:
    result: list[T] = []
    for config_key, config_itms in config.items():
        itm: dict[str, str]
        for itm in config_itms:
            try:
                itm_copy = itm.copy()
                result.append(factories(config_key, itm_copy.pop("kind"), **itm_copy))
            except:
                print(config_key, itm)
                raise
    return result


def create_background_tasks(
    container: containers.Container,
    config: providers.Configuration,
) -> list[BackgroundTask]:
    tasks: list[BackgroundTask] = []

    tasks += [
        EventConsumerTask(
            from_queue=container.queue(),
            event_handler_service=container.event_handler_service(),
            to_queue=container.event_bus(),
        )
    ]

    tasks += [TickTriggerTask(event_bus=container.event_bus())]

    tasks += [
        ThreatLevelMonitorTask(
            identifier=neighbor["identifier"],
            uri=neighbor["threat_level_websocket_url"],
            other_threat_levels_manager=container.other_threat_levels_manager(),
        )
        for neighbor in container.config()["neighbors"]
    ]

    if config["outgoing_probes"]["startup"]:
        tasks += [
            ProbeTask(
                settings=SingleOutgoingProbeSettings.model_validate(
                    config["outgoing_probes"]["startup"]
                ),
                probe_manager=container.outgoing_startup_probe_manager(),
                dependent_probe_manager=None,
            )
        ]
    if config["outgoing_probes"]["readiness"]:
        dependent_probe_manager = None
        if config["outgoing_probes"]["startup"]:
            dependent_probe_manager = container.outgoing_startup_probe_manager()
        tasks += [
            ProbeTask(
                SingleOutgoingProbeSettings.model_validate(
                    config["outgoing_probes"]["readiness"]
                ),
                probe_manager=container.outgoing_readiness_probe_manager(),
                dependent_probe_manager=dependent_probe_manager,
            )
        ]
    if config["outgoing_probes"]["liveness"]:
        dependent_probe_manager = None
        if config["outgoing_probes"]["startup"]:
            dependent_probe_manager = container.outgoing_startup_probe_manager()
        tasks += [
            ProbeTask(
                SingleOutgoingProbeSettings.model_validate(
                    config["outgoing_probes"]["liveness"]
                ),
                probe_manager=container.outgoing_liveness_probe_manager(),
                dependent_probe_manager=dependent_probe_manager,
            )
        ]

    return tasks


def create_instrumentors(
    background_tasks: list[BackgroundTask],
) -> Iterable[InstrumentFastAPI]:
    instrumentors: list[InstrumentFastAPI] = []

    instrumentors += [RegisterBackgroundTasks(background_tasks)]
    instrumentors += [RegisterRoutes()]
    instrumentors += [RegisterMiddlewares([])]
    instrumentors += [RegisterPrometheus()]

    return instrumentors


def create_app(
    # container: Container,
    instrumentors: Iterable[InstrumentFastAPI],
) -> FastAPI:
    app = FastAPI()
    # app.container = container

    for instrumentor in instrumentors:
        instrumentor.instrument_app(app)

    return app
