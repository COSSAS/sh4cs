#!/usr/bin/env python3

import logging
import os
import time

import httpx
from rich.logging import RichHandler

log = logging.getLogger(__name__)


FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log.setLevel(logging.DEBUG)

REGENERATION_DEMO_BASEURL = os.getenv(
    "REGENERATION_DEMO_BASEURL", "http://localhost:8002"
)

with httpx.Client(base_url=REGENERATION_DEMO_BASEURL) as regeneration_demo_client:
    try:
        log.info("Setting readiness check to False")
        regeneration_demo_client.post(
            "/probe/ready/unset",
        )
        time.sleep(20)

        log.info("Setting readiness check to True")
        regeneration_demo_client.post(
            "/probe/ready/set",
        )
        time.sleep(20)

        log.info("Setting health check to False")
        regeneration_demo_client.post(
            "/probe/health/unset",
        )

    except:
        log.exception("Sending failed")
