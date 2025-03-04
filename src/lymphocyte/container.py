import asyncio
import itertools

from dependency_injector import containers, providers
from prometheus_client import Gauge

from lymphocyte.actions.debug import DebugAction
from lymphocyte.actions.kill import KillAction
from lymphocyte.actions.request import SendRestRequestAction
from lymphocyte.actions.threat_level import (
    IncrementThreatLevelAction,
    ResetThreatLevelAction,
)
from lymphocyte.actions.ttl import (
    DecrementTTLAction,
    RestartTTLAction,
    ScaleTTLAction,
    SetTTLAction,
)
from lymphocyte.container_utils import (
    create_app,
    create_background_tasks,
    create_event_handlers,
    create_instrumentors,
)
from lymphocyte.events.bus import Event, EventBus, EventHandlerService
from lymphocyte.events.handlers.prometheus import PrometheusAlertStatusChangedHandler
from lymphocyte.events.handlers.threat_level import (
    PrometheusThreatLevelChangedHandler,
    ThreatLevelChangedHandler,
)
from lymphocyte.events.handlers.tick import TickEventHandler
from lymphocyte.events.handlers.ttl import TTLChangedEventHandler, TTLResetEventHandler
from lymphocyte.events.handlers.webhook import WebhookEventHandler
from lymphocyte.managers.outgoing_probes import OutgoingProbesManager
from lymphocyte.managers.prometheus import PrometheusManager
from lymphocyte.managers.threat_level import (
    OtherThreatLevelsManager,
    ThreatLevelManager,
)
from lymphocyte.managers.ttl import TTLManager
from lymphocyte.rules.conditional_rule import ConditionalRule
from lymphocyte.services.probe_service import ProbeService


class Container(containers.DeclarativeContainer):
    __self__ = providers.Self()

    config = providers.Configuration(strict=True)
    wiring_config = containers.WiringConfiguration(packages=["lymphocyte.routers"])

    queue: providers.Object[asyncio.Queue[Event]] = providers.Object(asyncio.Queue())
    event_bus = providers.Factory(EventBus, queue=queue)

    threat_level_manager = providers.ThreadSafeSingleton(
        ThreatLevelManager, event_bus=event_bus, base_level=0
    )
    other_threat_levels_manager = providers.ThreadSafeSingleton(
        OtherThreatLevelsManager, event_bus=event_bus
    )
    ttl_manager = providers.ThreadSafeSingleton(
        TTLManager, event_bus=event_bus, base_ttl=config.ttl_manager.base_ttl_seconds
    )
    prometheus_manager = providers.ThreadSafeSingleton(
        PrometheusManager, event_bus=event_bus
    )
    outgoing_startup_probe_manager = providers.ThreadSafeSingleton(
        OutgoingProbesManager, event_bus=event_bus, name="startup", initial_status=False
    )
    outgoing_readiness_probe_manager = providers.ThreadSafeSingleton(
        OutgoingProbesManager,
        event_bus=event_bus,
        name="readiness",
        initial_status=False,
    )
    outgoing_liveness_probe_manager = providers.ThreadSafeSingleton(
        OutgoingProbesManager,
        event_bus=event_bus,
        name="liveness",
        initial_status=False,
    )

    context = providers.Dict(
        other_threat_levels_manager=other_threat_levels_manager,
        threat_level_manager=threat_level_manager,
        ttl_manager=ttl_manager,
        prometheus_manager=prometheus_manager,
        event_bus=event_bus,
        queue=queue,
        outgoing_startup_probe_manager=outgoing_startup_probe_manager,
        outgoing_readiness_probe_manager=outgoing_readiness_probe_manager,
        outgoing_liveness_probe_manager=outgoing_liveness_probe_manager,
    )
    probe_service = providers.Factory(
        ProbeService,
        ttl_manager=ttl_manager,
        startup_expression=config.incoming_probes.startup_expression,
        readiness_expression=config.incoming_probes.readiness_expression,
        liveness_expression=config.incoming_probes.liveness_expression,
        context=context,
    )

    factories = providers.Aggregate(
        triggers=providers.FactoryAggregate(
            tick_event=providers.Factory(TickEventHandler),
            ttl_reset=providers.Factory(TTLResetEventHandler),
            ttl_changed=providers.Factory(TTLChangedEventHandler),
            webhook=providers.Factory(WebhookEventHandler),
            threat_level=providers.Factory(ThreatLevelChangedHandler),
            prometheus_alert=providers.Factory(PrometheusAlertStatusChangedHandler),
        ),
        rules=providers.FactoryAggregate(
            conditional=providers.Factory(ConditionalRule, context=context)
        ),
        actions=providers.FactoryAggregate(
            debug=providers.Factory(DebugAction, context=context),
            kill=providers.Factory(KillAction),
            send_rest_request=providers.Factory(SendRestRequestAction),
            increment_threat_level=providers.Factory(
                IncrementThreatLevelAction, threat_level_manager=threat_level_manager
            ),
            reset_threat_level=providers.Factory(
                ResetThreatLevelAction, threat_level_manager=threat_level_manager
            ),
            scale_TTL=providers.Factory(ScaleTTLAction, ttl_manager=ttl_manager),
            decrement_TTL=providers.Factory(
                DecrementTTLAction, ttl_manager=ttl_manager
            ),
            set_TTL=providers.Factory(SetTTLAction, ttl_manager=ttl_manager),
            restart_TTL=providers.Factory(RestartTTLAction, ttl_manager=ttl_manager),
        ),
    )

    rule_event_handlers = providers.Resource(
        create_event_handlers,
        config=providers.Dict(
            triggers=config.triggers,
            rules=config.rules,
            actions=config.actions,
        ),
        factories=factories,
    )

    metric_threat_level: providers.Object[Gauge] = providers.Object(
        Gauge("lymphocyte_threat_level", "Threat level of lymphocyte")
    )

    extra_event_handler_factories = providers.List(
        providers.Factory(PrometheusThreatLevelChangedHandler, metric_threat_level)
    )

    event_handler_service = providers.ThreadSafeSingleton(
        EventHandlerService,
        handlers=providers.Factory(
            list,
            providers.Factory(
                itertools.chain, rule_event_handlers, extra_event_handler_factories
            ),
        ),
    )

    background_tasks = providers.Resource(create_background_tasks, __self__, config)
    instrumentors = providers.Resource(
        create_instrumentors, background_tasks=background_tasks
    )
    fastapi_app = providers.Resource(
        create_app,
        instrumentors=instrumentors,
    )
