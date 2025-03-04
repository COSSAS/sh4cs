import logging

import pytoml  # type: ignore
import yaml

from lymphocyte.container import Container
from lymphocyte.settings import Settings

log = logging.getLogger(__name__)


def create_settings(file_path: str | None = None, file_type: str = "yaml") -> Settings:
    if not file_path:
        return Settings()

    if file_type == "yaml":
        with open(file_path, "rb") as f:
            return Settings.model_validate(yaml.safe_load(f))

    if file_type == "toml":
        with open(file_path, "rb") as f:
            return Settings.model_validate(pytoml.load(f))
    return Settings()


def create_container(settings: Settings) -> Container:
    container = Container()
    container.config.from_dict(settings.model_dump())

    container.init_resources()

    return container
