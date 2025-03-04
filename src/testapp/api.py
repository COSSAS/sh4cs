import os
import socket
from typing import Annotated

import auth
import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

base_url = os.getenv("BASE_URL", "http://localhost:8000")


@router.get("/download_file")
async def download_file(
    file_name: str,
):
    """
    This function is vulnerable to path injection
    """

    path = "files/" + file_name

    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Not found")

    if not os.access(path, os.R_OK):
        raise HTTPException(status_code=500, detail="Not readable")

    return FileResponse(path)


@router.get("/whoami")
async def whoami(request: Request):
    return {
        "server_hostname": socket.gethostname(),
        "request_client": request.client,
        "request_method": request.method,
        "request_url": str(request.url),
        "request_headers": request.headers,
    }


@router.get("/remote")
async def remote(path: str = "/whoami"):
    try:
        async with httpx.AsyncClient(base_url=base_url) as client:
            response = await client.get(path)
            try:
                response_body = response.json()
            except:
                response_body = response.text
            return {
                "client_hostname": socket.gethostname(),
                "response_status_code": response.status_code,
                "response_headers": response.headers,
                "response": response_body,
            }
    except:
        return False


@router.get("/complicated_calculation")
async def calculation(
    amount: int,
    current_user: Annotated[auth.User, Depends(auth.get_current_active_user)],
):
    """
    This function has no bounds check on the amount
    """

    for x in range(amount):
        x**x

    return True
