"""Pydantic schemas for image description requests and responses."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DetailLevel(StrEnum):
    """Supported description detail levels."""

    brief = "brief"
    standard = "standard"
    detailed = "detailed"


class ImageDescription(BaseModel):
    """Structured output produced by the AI model."""

    description: str = Field(..., description="日本語の画像説明")


class DescriptionResponse(BaseModel):
    """Successful API response for a generated description."""

    description: str
    detail: DetailLevel
    model: str
    request_id: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    openai_configured: bool

