# https://prometheus.io/docs/alerting/latest/configuration/#webhook_config
import logging
from typing import Any, Literal

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from lymphocyte.managers.prometheus import PrometheusManager

log = logging.getLogger(__name__)

router = APIRouter()


class AlertmanagerAlert(BaseModel):
    """Class for Prometheus alert objects

    Args:
        BaseModel (Basemodel): Base class for Pydantic models.
    """

    model_config = ConfigDict(extra="ignore")

    status: Literal["resolved", "firing"]
    labels: dict[str, Any]


class AlertmanagerWebhook(BaseModel):
    """Class for Prometheus alert webhook objects

    Args:
        BaseModel (Basemodel): Base class for Pydantic models.
    """

    model_config = ConfigDict(extra="ignore")

    alerts: list[AlertmanagerAlert]
    commonLabels: dict[str, Any]


@router.post("/alertmanager_webhook")
@inject
async def alertmanager_webhook(
    payload: AlertmanagerWebhook,
    prometheus_manager: PrometheusManager = Depends(Provide["prometheus_manager"]),
) -> Literal[True]:
    """This manager parses the alert and passes the alert status to the Prometheus manager.

    Args:
        payload (AlertmanagerWebhook): Object containing alerts
        prometheus_manager (PrometheusManager, optional): Prometheus manager. Defaults to Depends(Provide["prometheus_manager"]).

    Raises:
        HTTPException: HTTP 400 Bad Request when an alert name is missing

    Returns:
        Literal[True]: Returns True after dealing with all alerts.
    """
    # import pprint
    # log.debug("Prometheus:\n%s", pprint.pformat(payload))

    for alert in payload.alerts:
        alert_labels = alert.labels | payload.commonLabels

        if "alertname" not in alert_labels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="alertname missing",
            )

        await prometheus_manager.set(
            alert_labels["alertname"], alert.status == "firing"
        )

    return True
