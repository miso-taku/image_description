"""Unit and property-based tests for image validation (PBT-03, PBT-07)."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core.errors import (
    EmptyImageError,
    ImageTooLargeError,
    InvalidImageTypeError,
)
from app.services.image_validation import (
    JPEG,
    PNG,
    WEBP,
    detect_media_type,
    validate_image,
)
from tests.conftest import JPEG_BYTES, PNG_BYTES, WEBP_BYTES

MAX = 10 * 1024 * 1024


def test_valid_signatures_detected() -> None:
    assert detect_media_type(PNG_BYTES) == PNG
    assert detect_media_type(JPEG_BYTES) == JPEG
    assert detect_media_type(WEBP_BYTES) == WEBP


def test_validate_accepts_supported_images() -> None:
    result = validate_image("a.png", "image/png", PNG_BYTES, MAX)
    assert result.media_type == PNG
    assert result.size_bytes == len(PNG_BYTES)


def test_empty_image_rejected() -> None:
    with pytest.raises(EmptyImageError):
        validate_image("a.png", "image/png", b"", MAX)


def test_too_large_rejected() -> None:
    with pytest.raises(ImageTooLargeError):
        validate_image("a.png", "image/png", PNG_BYTES, max_bytes=4)


def test_unknown_signature_rejected() -> None:
    with pytest.raises(InvalidImageTypeError):
        validate_image("a.txt", "text/plain", b"not an image at all!!", MAX)


def test_declared_type_conflict_rejected() -> None:
    # PNG signature but the client claims JPEG.
    with pytest.raises(InvalidImageTypeError):
        validate_image("a.jpg", "image/jpeg", PNG_BYTES, MAX)


# --- Property-based tests ---

# Signature prefixes that must always be detected regardless of trailing bytes.
_PREFIXES = {
    PNG: b"\x89PNG\r\n\x1a\n",
    JPEG: b"\xff\xd8\xff",
    WEBP: b"RIFF____WEBP",  # placeholder; real bytes built in the test
}


@given(tail=st.binary(min_size=4, max_size=64))
def test_png_signature_invariant(tail: bytes) -> None:
    data = b"\x89PNG\r\n\x1a\n" + tail
    assert detect_media_type(data) == PNG
    validated = validate_image("x.png", "image/png", data, MAX)
    assert validated.media_type == PNG


@given(size=st.integers(min_value=1, max_value=10_000))
def test_size_over_limit_always_rejected(size: int) -> None:
    # A payload larger than the limit is always rejected, whatever its content.
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * size
    with pytest.raises(ImageTooLargeError):
        validate_image("x.png", "image/png", data, max_bytes=4)


@given(data=st.binary(min_size=12, max_size=64))
def test_non_image_binary_rejected(data: bytes) -> None:
    # Skip inputs that happen to be a real signature.
    if detect_media_type(data) is not None:
        return
    with pytest.raises(InvalidImageTypeError):
        validate_image(None, None, data, MAX)
