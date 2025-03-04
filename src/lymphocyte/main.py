import logging
import logging.config
import os

from lymphocyte.main_utils import create_container, create_settings

log = logging.getLogger(__name__)

if log_config_file := os.getenv("LYMPHOCYTE_LOG_CONFIG"):
    logging.config.fileConfig(log_config_file)

settings = create_settings(os.getenv("LYMPHOCYTE_CONFIG"))
container = create_container(settings=settings)
app = container.fastapi_app()

if log.isEnabledFor(logging.DEBUG):
    from pprint import pformat

    log.debug("All routes:\n%s", pformat(app.routes))
    log.debug(
        "All event handlers:\n%s",
        pformat(container.event_handler_service().handlers),
    )
