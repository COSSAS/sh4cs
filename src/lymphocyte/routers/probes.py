from typing import Literal

import fastapi
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from lymphocyte.services.probe_service import ProbeService

router = APIRouter()


@router.get("/livenessProbe")
@inject
async def liveness_probe(
    probe_service: ProbeService = Depends(Provide["probe_service"]),
) -> Literal[True]:
    """The liveness probe returns true if the lympho is still alive.

    Args:
        probe_service (ProbeService, optional). Defaults to Depends(Provide["probe_service"]).

    Raises:
        HTTPException: Raises HTTP 500 Internal Server Error if there is no positive response from the probe.

    Returns:
        Literal[True]: Returns True if alive.
    """
    ok, err = await probe_service.probe_liveness()
    if ok:
        return True
    else:
        raise HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


@router.get("/startupProbe")
@inject
async def startup_probe(
    probe_service: ProbeService = Depends(Provide["probe_service"]),
) -> Literal[True]:
    """The liveness probe returns true if the subject application is starting up OR has started up.

    Args:
        probe_service (ProbeService, optional). Defaults to Depends(Provide["probe_service"]).

    Raises:
        HTTPException: Raises HTTP 500 Internal Server Error if there is no positive response from the probe.

    Returns:
        Literal[True]: Returns True if starting up OR has started up.
    """

    ok, err = await probe_service.probe_startup()
    if ok:
        return True
    else:
        raise HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )


@router.get("/readinessProbe")
@inject
async def readiness_probe(
    probe_service: ProbeService = Depends(Provide["probe_service"]),
) -> Literal[True]:
    """The liveness probe returns true if the subject application is ready.

    Args:
        probe_service (ProbeService, optional). Defaults to Depends(Provide["probe_service"]).

    Raises:
        HTTPException: Raises HTTP 500 Internal Server Error if there is no positive response from the probe.

    Returns:
        Literal[True]: Returns True if ready.
    """
    ok, err = await probe_service.probe_readiness()
    if ok:
        return True
    else:
        raise HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
