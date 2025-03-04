from typing import Any

import fastapi

# pylint: disable-next=no-name-in-module
from dependency_injector.containers import DynamicContainer
from httpx import AsyncClient

from lymphocyte.container import Container
from lymphocyte.settings import Settings


async def test_settings_initialize(settings: Any) -> None:
    assert isinstance(settings, Settings)


async def test_container_initialize(container: Any) -> None:
    assert isinstance(container, Container) or isinstance(container, DynamicContainer)


async def test_app_initialize(app: Any) -> None:
    assert isinstance(app, fastapi.FastAPI)


async def test_client_initialize(client: Any) -> None:
    assert isinstance(client, AsyncClient)


async def test_test_client_initialize(test_client: Any) -> None:
    assert isinstance(test_client, fastapi.testclient.TestClient)
