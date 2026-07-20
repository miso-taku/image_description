"""Pure image validation logic (SECURITY-05).

Validation checks the declared content type, the real file signature (magic
bytes), size bounds, and non-emptiness before any external API call.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.errors import (
    EmptyImageError,
    ImageTooLargeError,
    InvalidImageTypeError,
)

# Supported media types.
JPEG = "image/jpeg"
PNG = "image/png"
WEBP = "image/webp"

ALLOWED_MEDIA_TYPES: frozenset[str] = frozenset({JPEG, PNG, WEBP})


@dataclass(frozen=True)
class ValidatedImage:
    """An image that has passed validation. Held in memory only."""

    data: bytes
    media_type: str
    size_bytes: int


def detect_media_type(data: bytes) -> str | None:
    """Detect the media type from the leading file signature bytes.

    Returns one of the allowed media types, or None if unrecognized.
    """
    if len(data) < 12:
        return None
    if data[:3] == b"\xff\xd8\xff":
        return JPEG
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return PNG
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return WEBP
    return None


def validate_image(
    filename: str | None,
    content_type: str | None,
    data: bytes,
    max_bytes: int,
) -> ValidatedImage:
    """Validate an uploaded image and return a ValidatedImage.

    Raises an AppError subclass on any validation failure.
    """
    size = len(data)
    if size == 0:
        raise EmptyImageError()
    if size > max_bytes:
        raise ImageTooLargeError()

    detected = detect_media_type(data)
    if detected is None or detected not in ALLOWED_MEDIA_TYPES:
        raise InvalidImageTypeError()

    # If the client declared a content type, it must not contradict the
    # detected signature. Missing/generic content types fall back to detection.
    declared = (content_type or "").split(";")[0].strip().lower()
    if declared and declared in ALLOWED_MEDIA_TYPES and declared != detected:
        raise InvalidImageTypeError()

    return ValidatedImage(data=data, media_type=detected, size_bytes=size)
