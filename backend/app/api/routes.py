"""API routes for image description and health checks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from app.core.config import Settings, get_settings
from app.core.errors import InvalidDetailError
from app.schemas.description import (
    DescriptionResponse,
    DetailLevel,
    HealthResponse,
)
from app.services.description_service import DescriptionService
from app.services.image_validation import validate_image

router = APIRouter()


def get_description_service(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> DescriptionService:
    """Provide a shared DescriptionService stored on the app state."""
    service: DescriptionService | None = getattr(request.app.state, "description_service", None)
    if service is None:
        service = DescriptionService(settings)
        request.app.state.description_service = service
    return service


@router.get("/health", response_model=HealthResponse, tags=["meta"])
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return application health without making any paid API call."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        openai_configured=settings.openai_configured,
    )


@router.post(
    "/api/v1/descriptions",
    response_model=DescriptionResponse,
    tags=["descriptions"],
)
async def create_description(
    request: Request,
    image: UploadFile = File(...),
    detail: str = Form(...),
    settings: Settings = Depends(get_settings),
    service: DescriptionService = Depends(get_description_service),
) -> DescriptionResponse:
    """Validate an uploaded image and return a Japanese description."""
    request_id: str = getattr(request.state, "request_id", "")

    try:
        detail_level = DetailLevel(detail)
    except ValueError as exc:
        raise InvalidDetailError() from exc

    data = await image.read()
    validated = validate_image(
        image.filename,
        image.content_type,
        data,
        settings.max_image_bytes,
    )

    result = await service.describe_image(validated, detail_level, request_id)

    return DescriptionResponse(
        description=result.description,
        detail=detail_level,
        model=settings.openai_model,
        request_id=request_id,
    )
