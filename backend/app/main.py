"""FastAPI application entry point."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import configure_logging, get_logger, log_event
from app.core.security import RateLimitMiddleware, RequestIDMiddleware

logger = get_logger("app.main")


def create_app() -> FastAPI:
    """Application factory."""
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title="Image Description API",
        version=settings.app_version,
        description="画像を日本語で説明するAPI (FastAPI + PydanticAI + OpenAI)",
    )

    # Middleware order: rate limit runs after request id is assigned.
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        log_event(
            logger,
            logging.WARNING,
            "app_error",
            request_id=request_id,
            code=exc.code,
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Fail closed: never leak internal details to the client (SECURITY-09/15).
        request_id = getattr(request.state, "request_id", None)
        log_event(
            logger,
            logging.ERROR,
            "unhandled_error",
            request_id=request_id,
            error_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "予期しないエラーが発生しました。時間をおいて再試行してください。",
                    "request_id": request_id,
                }
            },
        )

    app.include_router(router)
    return app


app = create_app()
