"""Security-related middleware: request IDs and local rate limiting."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.errors import LocalRateLimitedError


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a server-generated request id to every request and response.

    The id is generated server-side and never taken from client input
    (SECURITY-03 correlation, avoids client-controlled log injection).
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """A lightweight in-memory sliding-window rate limiter per client IP.

    This is intended for local, single-process use only (SECURITY-11). It is
    not a substitute for a distributed rate limiter in production.
    """

    def __init__(self, app, *, max_requests: int, window_seconds: int) -> None:
        super().__init__(app)
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_key(self, request: Request) -> str:
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        if request.url.path.startswith("/api/"):
            key = self._client_key(request)
            now = time.monotonic()
            window_start = now - self._window_seconds
            hits = self._hits[key]
            while hits and hits[0] < window_start:
                hits.popleft()
            if len(hits) >= self._max_requests:
                error = LocalRateLimitedError()
                request_id = getattr(request.state, "request_id", None)
                return JSONResponse(
                    status_code=error.http_status,
                    content={
                        "error": {
                            "code": error.code,
                            "message": error.message,
                            "request_id": request_id,
                        }
                    },
                )
            hits.append(now)
        return await call_next(request)
