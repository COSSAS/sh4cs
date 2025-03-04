import logging
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# import time


log = logging.getLogger(__name__)


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # start_time = time.time()

        try:
            # log.debug(
            #     "request client=%s method=%s url=%s",
            #     request.client,
            #     request.method,
            #     request.url,
            # )
            response: Response = await call_next(request)
            if "/metrics" not in request.url.path:
                log.info(
                    "response client=%s method=%s status_code=%s content_type=%s url=%s",
                    request.client,
                    request.method,
                    response.status_code,
                    response.headers.get("content-type", None),
                    request.url,
                )
            return response
        except Exception as e:
            log.warning("failed %s", e)
            raise
        # finally:
        #     process_time = (time.time() - start_time) * 1000
        #     log.debug("completed_in=%.2fms", process_time)
