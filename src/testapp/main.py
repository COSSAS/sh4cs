from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()


instrumentator = Instrumentator(
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    inprogress_labels=True,
).instrument(app)


@app.on_event("startup")
async def _startup():
    instrumentator.expose(app)


import api
import auth
import probes

app.include_router(auth.router)
app.include_router(api.router)
app.include_router(probes.router)


from datetime import datetime, timedelta

rate_limiter_settings = {"enabled": False, "limit": timedelta(seconds=2)}


@app.get("/rate_limiter")
async def rate_limiter():
    return rate_limiter_settings["enabled"]


@app.get("/enable_rate_limiter")
async def enable_rate_limiter():
    rate_limiter_settings["enabled"] = True
    return rate_limiter_settings["enabled"]


@app.get("/disable_rate_limiter")
async def enable_rate_limiter():
    rate_limiter_settings["enabled"] = False
    return rate_limiter_settings["enabled"]


last_requests: dict[str, datetime] = {}


def should_limit(host: str, last_requests: dict[str, datetime]):
    return (
        rate_limiter_settings["enabled"]
        and host != "127.0.0.1"
        and host in last_requests
        and datetime.now() - last_requests[host] < rate_limiter_settings["limit"]
    )


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    if should_limit(request.client.host, last_requests):
        return JSONResponse({"detail": "Too many requests"}, status_code=429)
    last_requests[request.client.host] = datetime.now()
    return await call_next(request)
