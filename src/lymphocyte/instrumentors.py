import asyncio
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

from fastapi import APIRouter, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from lymphocyte.background_tasks import BackgroundTask
from lymphocyte.routers import probes, prometheus, test, threat_level, webhooks

log = logging.getLogger(__name__)


class InstrumentFastAPI(Protocol):
    def instrument_app(self, app: FastAPI) -> None:
        ...


log = logging.getLogger(__name__)


@dataclass
class RegisterBackgroundTasks(InstrumentFastAPI):
    tasks: list[BackgroundTask] = field(default_factory=list)

    def instrument_app(self, app: FastAPI) -> None:
        @app.on_event("startup")
        async def startup_event() -> None:
            asyncio.gather(
                *[task.perform() for task in self.tasks], return_exceptions=True
            )


@dataclass
class RegisterRoutes(InstrumentFastAPI):
    routes: Iterable[APIRouter] = field(
        default_factory=lambda: [
            probes.router,
            webhooks.router,
            threat_level.router,
            test.router,
            prometheus.router,
        ]
    )

    def instrument_app(self, app: FastAPI) -> None:
        for router in self.routes:
            app.include_router(router=router)


@dataclass
class RegisterMiddlewares(InstrumentFastAPI):
    middlewares: Iterable[tuple[type, dict[Any, Any]]]

    def instrument_app(self, app: FastAPI) -> None:
        for middleware, options in self.middlewares:
            app.add_middleware(middleware, **options)


@dataclass
class RegisterPrometheus(InstrumentFastAPI):
    def instrument_app(self, app: FastAPI) -> None:
        instrumentator = Instrumentator().instrument(app)

        @app.on_event("startup")
        async def _startup() -> None:
            instrumentator.expose(app)
