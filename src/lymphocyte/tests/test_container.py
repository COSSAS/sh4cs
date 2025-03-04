from typing import Any
from unittest import mock

import dependency_injector.errors
import pytest
from dependency_injector import providers

from lymphocyte.container import Container
from lymphocyte.container_utils import create_event_handlers
from lymphocyte.settings import Settings


def test_default_is_empty_list() -> None:
    container = Container()

    container.config.from_dict(Settings().model_dump())

    assert len(container.rule_event_handlers()) == 0


def test_create_event_handlers_empty() -> None:
    factories = mock.Mock(providers.Aggregate)
    config: dict[str, list[dict[str, str]]] = {}

    res: list[Any] = create_event_handlers(factories, config)
    assert len(res) == 0


def test_create_event_handlers_single_item_without_args() -> None:
    factories = mock.Mock(providers.Aggregate)
    factories.return_value = mock.sentinel
    config = {"config_item": [{"kind": "some_kind"}]}

    res: list[Any] = create_event_handlers(factories, config)
    assert len(res) == 1
    assert res[0] == factories.return_value

    assert factories.called
    assert factories.call_args.args == (
        "config_item",
        "some_kind",
    )
    assert factories.call_args.kwargs == {}


def test_create_event_handlers_single_item_with_args() -> None:
    factories = mock.Mock(providers.Aggregate)
    factories.return_value = mock.sentinel
    config = {"config_item": [{"kind": "some_kind", "extra_kwarg": "yes"}]}

    res: list[Any] = create_event_handlers(factories, config)
    assert len(res) == 1
    assert res[0] == factories.return_value

    assert factories.called
    assert factories.call_args.args == (
        "config_item",
        "some_kind",
    )
    assert factories.call_args.kwargs == {"extra_kwarg": "yes"}


factory_call_args_initialize = [
    ("triggers", "tick_event", {"name": "some_name"}),
    ("triggers", "tick_event", {"name": "some_name", "every_n_seconds": 1}),
    ("triggers", "ttl_reset", {"name": "some_name"}),
    ("triggers", "ttl_changed", {"name": "some_name"}),
    ("triggers", "webhook", {"name": "some_name", "exact_match": "exact_match"}),
    ("triggers", "threat_level", {"name": "some_name", "identifier": "identifier"}),
    (
        "triggers",
        "threat_level",
        {"name": "some_name", "identifier": "identifier", "host": "host"},
    ),
    ("triggers", "prometheus_alert", {"name": "some_name", "alertname": "alertname"}),
]


@pytest.mark.parametrize(
    "factory_kind,factory_name,factory_kwargs", factory_call_args_initialize
)
def test_factories_initialize(
    factory_kind: str, factory_name: str, factory_kwargs: dict[Any, Any]
) -> None:
    container = Container()

    container.config.from_dict(Settings().model_dump())

    container.factories(factory_kind, factory_name, **factory_kwargs)


factory_call_args_not_initializing: list[tuple[str, str, dict[Any, Any], type]] = [
    ("triggers", "unknown", {}, dependency_injector.errors.NoSuchProviderError),
    ("rules", "unknown", {}, dependency_injector.errors.NoSuchProviderError),
    ("actions", "unknown", {}, dependency_injector.errors.NoSuchProviderError),
    ("triggers", "tick_event", {}, TypeError),
]


@pytest.mark.parametrize(
    "factory_kind,factory_name,factory_kwargs,type_of_error",
    factory_call_args_not_initializing,
)
def test_factories_not_initializing(
    factory_kind: str,
    factory_name: str,
    factory_kwargs: dict[Any, Any],
    type_of_error: type,
) -> None:
    container = Container()

    container.config.from_dict(Settings().model_dump())

    with pytest.raises(type_of_error):
        container.factories(factory_kind, factory_name, **factory_kwargs)
