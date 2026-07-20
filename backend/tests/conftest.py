"""Shared test fixtures. The OpenAI API is never called in tests."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.main import create_app
from app.schemas.description import DetailLevel, ImageDescription
from app.services.image_validation import ValidatedImage

# Minimal valid file signatures (padded to at least 12 bytes).
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
JPEG_BYTES = b"\xff\xd8\xff" + b"\x00" * 9
WEBP_BYTES = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP"


@dataclass
class FakeResult:
    output: ImageDescription


class FakeAgent:
    """Stand-in for a PydanticAI agent used in tests."""

    def __init__(
        self,
        output: ImageDescription | None = None,
        exc: Exception | None = None,
    ) -> None:
        self._output = output or ImageDescription(description="これはテスト用の説明です。")
        self._exc = exc
        self.calls: list[object] = []

    async def run(self, prompt: object) -> FakeResult:
        self.calls.append(prompt)
        if self._exc is not None:
            raise self._exc
        return FakeResult(output=self._output)


class FakeDescriptionService:
    """Fake service injected into the API in tests."""

    def __init__(
        self,
        output: ImageDescription | None = None,
        exc: Exception | None = None,
    ) -> None:
        self._output = output or ImageDescription(description="これはテスト用の説明です。")
        self._exc = exc
        self.received: list[tuple[ValidatedImage, DetailLevel, str]] = []

    async def describe_image(
        self,
        image: ValidatedImage,
        detail: DetailLevel,
        request_id: str,
    ) -> ImageDescription:
        self.received.append((image, detail, request_id))
        if self._exc is not None:
            raise self._exc
        return self._output


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        openai_api_key="test-key",
        openai_model="gpt-4.1-mini",
        openai_timeout_seconds=5.0,
        rate_limit_requests=1000,
    )


@pytest.fixture
def make_client(
    test_settings: Settings,
) -> Iterator[Callable[[FakeDescriptionService | None], TestClient]]:
    created: list[TestClient] = []

    def _make(service: FakeDescriptionService | None = None) -> TestClient:
        app = create_app()
        app.dependency_overrides[get_settings] = lambda: test_settings
        app.state.description_service = service or FakeDescriptionService()
        client = TestClient(app, raise_server_exceptions=False)
        created.append(client)
        return client

    yield _make
    for client in created:
        client.close()


__all__ = [
    "AppError",
    "FakeAgent",
    "FakeDescriptionService",
    "FakeResult",
    "JPEG_BYTES",
    "PNG_BYTES",
    "WEBP_BYTES",
]
