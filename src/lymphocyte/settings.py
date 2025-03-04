import datetime

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RulesSettings(BaseSettings):
    triggers: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    condition: str | None = Field(default=None)


class TriggerSetting(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    kind: str
    name: str


class ActionSetting(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    kind: str
    name: str


class RuleSetting(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    kind: str = Field(default="conditional")
    # name: str


class NeighborSetting(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    identifier: str
    threat_level_websocket_url: str


class IncomingProbeSettings(BaseSettings):
    startup_expression: str = Field(default="true")
    readiness_expression: str = Field(default="ttl_manager.fraction_passed() < 0.75")
    liveness_expression: str = Field(default="ttl_manager.fraction_passed() < 1")


class SingleOutgoingProbeSettings(BaseSettings):
    path: str
    port: int
    initial_delay_seconds: int
    period_seconds: int


class OutgoingProbeSettings(BaseSettings):
    startup: SingleOutgoingProbeSettings | None = Field(default=None)
    readiness: SingleOutgoingProbeSettings | None = Field(default=None)
    liveness: SingleOutgoingProbeSettings | None = Field(default=None)


class TTLManagerSettings(BaseSettings):
    base_ttl_seconds: datetime.timedelta = Field(
        default=datetime.timedelta(seconds=600)
    )


class Settings(BaseSettings):
    triggers: list[TriggerSetting] = Field(default_factory=list)
    actions: list[ActionSetting] = Field(default_factory=list)
    rules: list[RuleSetting] = Field(default_factory=list)

    neighbors: list[NeighborSetting] = Field(default_factory=list)

    incoming_probes: IncomingProbeSettings = Field(
        default_factory=IncomingProbeSettings
    )
    outgoing_probes: OutgoingProbeSettings = Field(
        default_factory=OutgoingProbeSettings
    )

    ttl_manager: TTLManagerSettings = Field(default_factory=TTLManagerSettings)
