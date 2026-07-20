"""Error response schema."""

from __future__ import annotations

from pydantic import BaseModel


class ErrorBody(BaseModel):
    """Details of an error."""

    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    """Standard error envelope returned to clients."""

    error: ErrorBody
