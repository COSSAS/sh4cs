#!/usr/bin/env python3

import logging
import os
import time

import httpx
from rich.logging import RichHandler
from rich.progress import track

log = logging.getLogger(__name__)


FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log.setLevel(logging.DEBUG)

TESTAPP_BASEURL = os.getenv("TESTAPP_BASEURL", "http://localhost:8000")

with httpx.Client(base_url=TESTAPP_BASEURL) as testapp_client:
    try:
        for _ in track(range(20), description="Sending wrong login credentials"):
            testapp_client.post(
                "/token", data={"username": "unknown", "password": "wrong"}
            )
            time.sleep(0.1)

        for _ in track(range(20), description="Requesting nonexisting files"):
            testapp_client.get(
                "/download_file?file_name=nonexistent",
            )
            time.sleep(0.1)
    except:
        log.exception("Sending failed")
