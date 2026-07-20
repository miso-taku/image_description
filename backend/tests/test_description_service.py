"""Tests for the description service error mapping and orchestration.

No real OpenAI calls are made; a fake agent stands in for PydanticAI.
"""

from __future__ import annotations

import asyncio

import pytest

from app.core.config import Settings
from app.core.errors import (
    ConfigurationError,
    UpstreamAuthenticationError,
    UpstreamError,
    UpstreamRateLimitedError,
    UpstreamTimeoutError,
)
from app.schemas.description import DetailLevel, ImageDescription
from app.services.description_service import DescriptionService, build_prompt
from app.services.image_validation import ValidatedImage
from tests.conftest import PNG_BYTES, FakeAgent


def _image() -> ValidatedImage:
    return ValidatedImage(data=PNG_BYTES, media_type="image/png", size_bytes=len(PNG_BYTES))


def _settings(**kwargs: object) -> Settings:
    base: dict[str, object] = {"openai_api_key": "test-key", "openai_timeout_seconds": 5.0}
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_build_prompt_varies_by_detail() -> None:
    prompts = {level: build_prompt(level) for level in DetailLevel}
    assert len({*prompts.values()}) == len(DetailLevel)


async def test_describe_image_success() -> None:
    agent = FakeAgent(output=ImageDescription(description="猫がいます。"))
    service = DescriptionService(_settings(), agent=agent)  # type: ignore[arg-type]
    result = await service.describe_image(_image(), DetailLevel.standard, "req-1")
    assert result.description == "猫がいます。"
    assert len(agent.calls) == 1


async def test_describe_image_requires_configuration() -> None:
    agent = FakeAgent()
    service = DescriptionService(_settings(openai_api_key=""), agent=agent)  # type: ignore[arg-type]
    with pytest.raises(ConfigurationError):
        await service.describe_image(_image(), DetailLevel.brief, "req-2")


async def test_describe_image_timeout() -> None:
    class SlowAgent:
        async def run(self, prompt: object) -> object:
            await asyncio.sleep(1)
            raise AssertionError("should have timed out")

    service = DescriptionService(
        _settings(openai_timeout_seconds=0.01),
        agent=SlowAgent(),  # type: ignore[arg-type]
    )
    with pytest.raises(UpstreamTimeoutError):
        await service.describe_image(_image(), DetailLevel.brief, "req-3")


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (type("AuthenticationError", (Exception,), {})(), UpstreamAuthenticationError),
        (type("RateLimitError", (Exception,), {})(), UpstreamRateLimitedError),
        (type("APITimeoutError", (Exception,), {})(), UpstreamTimeoutError),
        (type("APIError", (Exception,), {})(), UpstreamError),
    ],
)
async def test_describe_image_maps_provider_errors(exc: Exception, expected: type) -> None:
    agent = FakeAgent(exc=exc)
    service = DescriptionService(_settings(), agent=agent)  # type: ignore[arg-type]
    with pytest.raises(expected):
        await service.describe_image(_image(), DetailLevel.brief, "req-4")
