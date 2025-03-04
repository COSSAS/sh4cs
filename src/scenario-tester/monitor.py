#!/usr/bin/env python3

import logging
import os
import random
import time

import httpx
from rich.layout import Layout
from rich.live import Live
from rich.logging import RichHandler
from rich.table import Table

log = logging.getLogger(__name__)


FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARN, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log.setLevel(logging.DEBUG)


TESTAPP_LYMPHOCYTE_BASEURL = os.getenv(
    "TESTAPP_LYMPHOCYTE_BASEURL", "http://localhost:12345"
)
TESTAPP2_LYMPHOCYTE_BASEURL = os.getenv(
    "TESTAPP2_LYMPHOCYTE_BASEURL", "http://localhost:12346"
)
REGENERATION_DEMO_LYMPHOCYTE_BASEURL = os.getenv(
    "REGENERATION_DEMO_LYMPHOCYTE_BASEURL", "http://localhost:12347"
)


with httpx.Client(
    base_url=TESTAPP_LYMPHOCYTE_BASEURL
) as testapp_lymphocyte_client, httpx.Client(
    base_url=TESTAPP2_LYMPHOCYTE_BASEURL
) as testapp2_lymphocyte_client, httpx.Client(
    base_url=REGENERATION_DEMO_LYMPHOCYTE_BASEURL
) as regeneration_demo_lymphocyte_client:

    def generate_prom_table(table: Table, name: str, client: httpx.Client) -> Table:
        try:
            for alert_status in client.post(
                "/evaluate_expression",
                params={
                    "expression": """
                    prometheus_manager.get()
                    """
                },
            ).json():
                table.add_row(
                    name,
                    alert_status[0],
                    "[red]firing" if alert_status[1] else "[green]resolved",
                    alert_status[2],
                )
            return table
        except KeyboardInterrupt:
            raise
        except:
            table.add_row(name, "[italic][yellow]Connection error")
            return table

    def generate_threat_level_table() -> Table:
        table = Table()
        table.add_column("Deployment")
        table.add_column("Threat level")
        table.add_column("Start time")
        table.add_column("Current TTL")
        table.add_column("Fraction TTL passed")
        table.add_column("Readiness probe")
        table.add_column("Liveness probe")
        table.add_column("Other threat levels")

        name: str
        client: httpx.Client
        for name, client in [
            ("testapp", testapp_lymphocyte_client),
            ("testapp2", testapp2_lymphocyte_client),
            ("regeneration-demo", regeneration_demo_lymphocyte_client),
        ]:
            try:
                res = client.post(
                    "/evaluate_expression",
                    params={
                        "expression": """(
                            threat_level_manager.current,
                            ttl_manager.start_time,
                            ttl_manager.current_ttl,
                            ttl_manager.fraction_passed(),
                            other_threat_levels_manager.get(),
                            )"""
                    },
                ).json()
                readiness_status_code = client.get("/readinessProbe").status_code
                liveness_status_code = client.get("/livenessProbe").status_code

                table.add_row(
                    name,
                    str(res[0]),
                    str(res[1]),
                    str(res[2]),
                    "{:.4f}".format(res[3]),
                    ("[green]" if readiness_status_code < 400 else "[red]")
                    + str(readiness_status_code),
                    ("[green]" if liveness_status_code < 400 else "[red]")
                    + str(liveness_status_code),
                    str(res[4]),
                )
            except KeyboardInterrupt:
                raise
            except:
                table.add_row(name, "[italic][yellow]Connection error")
        return table

    def generate_layout() -> Layout:
        layout = Layout()

        prom_table = Table()
        prom_table.add_column("Deployment")
        prom_table.add_column("Lymphocyte alert name")
        prom_table.add_column("State")
        prom_table.add_column("Last update")

        layout.split_column(
            generate_prom_table(prom_table, "testapp", testapp_lymphocyte_client),
            generate_threat_level_table(),
        )
        return layout

    with Live(generate_layout(), refresh_per_second=5) as live:
        while True:
            time.sleep(0.2)
            live.update(generate_layout())
