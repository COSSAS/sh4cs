from collections.abc import AsyncGenerator, Generator, Iterable

import fastapi
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from lymphocyte.background_tasks import BackgroundTask
from lymphocyte.container import Container
from lymphocyte.container_utils import (
    create_app,
    create_background_tasks,
    create_instrumentors,
)
from lymphocyte.instrumentors import InstrumentFastAPI
from lymphocyte.main_utils import create_container
from lymphocyte.settings import Settings


@pytest.fixture(name="settings")
def fixture_settings() -> Settings:
    return Settings()


@pytest.fixture(name="container")
def fixture_container(settings: Settings) -> Generator[Container, None, None]:
    container = create_container(settings)
    yield container
    container.unwire()


@pytest.fixture(name="instrumentors")
def fixture_instrumentors(container: Container) -> Iterable[InstrumentFastAPI]:
    return create_instrumentors(container.background_tasks())


@pytest.fixture(name="background_tasks")
def fixture_background_tasks(container: Container) -> Iterable[BackgroundTask]:
    return create_background_tasks(container, container.config())


@pytest.fixture(name="app")
def fixture_app(
    instrumentors: Iterable[InstrumentFastAPI],
) -> Generator[fastapi.FastAPI, None, None]:
    app = create_app(instrumentors)
    yield app


@pytest.fixture(name="client")
async def fixture_client(
    app: fastapi.FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_client(app: fastapi.FastAPI) -> TestClient:
    return TestClient(app=app)
